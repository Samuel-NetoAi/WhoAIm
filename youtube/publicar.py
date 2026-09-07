"""Sobe vídeo no YouTube pela Data API v3 — com os limites reais escritos no código.

## O que esta peça assume, e por quê

**O vídeo nasce PRIVADO e isso não é bug.** Regra oficial do YouTube, publicada em
2020-07-28 e não revogada até 2026-09-01: todo vídeo enviado por `videos.insert` de
um projeto de API **não auditado** criado depois daquela data fica travado em privado.
Ver `D:\\Agentes\\_registros\\YOUTUBE.md`. Por isso o padrão aqui é `private` e por isso
`403 privacyError` é tratado como resposta esperada, não como falha do código.

**A cota não é o gargalo.** Desde 2026-06-01 o `videos.insert` tem balde próprio de
**100 chamadas/dia** a 1 unidade cada — não os 1.600 que quase todo guia ainda repete
(a própria página do Google se contradiz sobre isso). Publicamos 1-2 vídeos por mês.

**`containsSyntheticMedia` é obrigatório para este canal.** O campo existe desde
2024-10-30 para "cena realista que não aconteceu", que é literalmente o que o canal
produz. Não é opcional e não tem default silencioso aqui: quem chamar tem que dizer.

## O que NÃO passa por aqui

O segredo do cliente OAuth **nunca** entra por argumento, por variável de ambiente nem
por chat — lição registrada nesta casa: chave que passa pelo chat fica em texto puro no
transcript para sempre. Ele é lido de um arquivo que só o Samuel coloca no lugar.

O token de acesso é guardado com **DPAPI** (amarrado ao usuário do Windows), nunca em
texto puro.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SEGREDO_CLIENTE = AQUI / "client_secret.json"   # o Samuel põe. Nunca commitar.
TOKEN = AQUI / "token.dpapi"                     # cifrado por DPAPI. Nunca commitar.

# Escopo estreito de propósito: sobe o vídeo e nada mais. O escopo largo
# ("youtube") é o que permite thumbnail e playlist, e é mais difícil de passar
# na revisão do Google. Trocar só quando alguém precisar de verdade.
ESCOPO_SO_SUBIR = ["https://www.googleapis.com/auth/youtube.upload"]
ESCOPO_COMPLETO = ["https://www.googleapis.com/auth/youtube"]

# A API exige pedaço múltiplo de 256 KB no upload retomável. 4 MB é o
# compromisso entre número de requisições e quanto se perde ao reconectar.
PEDACO = 4 * 1024 * 1024

CATEGORIA_ENTRETENIMENTO = "24"


class FaltaConfigurar(RuntimeError):
    """Erro que EXPLICA o passo que falta, em vez de estourar um stack trace.

    Existe por lição desta casa: falha silenciosa é pior que falha ruidosa, e
    'não configurado' é um fato diferente de 'quebrou'.
    """


# ---------------------------------------------------------------- credenciais

def _dpapi_guardar(caminho: Path, texto: str) -> None:
    import win32crypt
    dados = win32crypt.CryptProtectData(texto.encode("utf-8"), "omega-youtube",
                                        None, None, None, 0)
    caminho.write_bytes(dados)


def _dpapi_ler(caminho: Path) -> str | None:
    if not caminho.exists():
        return None
    import win32crypt
    _, dados = win32crypt.CryptUnprotectData(caminho.read_bytes(),
                                             None, None, None, 0)
    return dados.decode("utf-8")


def credenciais(escopos: list[str] | None = None, *, interativo: bool = False):
    """Devolve credencial válida, renovando sozinha quando dá.

    `interativo=True` abre o navegador — só o comando `autorizar` faz isso.
    Qualquer outro caminho falha dizendo o que falta, em vez de abrir janela
    sozinho no meio de um pipeline.
    """
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials

    escopos = escopos or ESCOPO_SO_SUBIR
    bruto = _dpapi_ler(TOKEN)
    cred = Credentials.from_authorized_user_info(json.loads(bruto), escopos) if bruto else None

    if cred and cred.valid:
        return cred

    if cred and cred.expired and cred.refresh_token:
        cred.refresh(Request())          # renovação silenciosa, sem navegador
        _dpapi_guardar(TOKEN, cred.to_json())
        return cred

    if not interativo:
        raise FaltaConfigurar(
            "Sem autorização válida. Rode:  python youtube\\publicar.py autorizar\n"
            "Isso abre o navegador UMA vez e guarda o token cifrado por DPAPI."
        )

    if not SEGREDO_CLIENTE.exists():
        raise FaltaConfigurar(
            f"Falta o arquivo {SEGREDO_CLIENTE.name} em {AQUI}.\n"
            "Ele sai do Google Cloud Console (OAuth client ID, tipo 'Desktop app').\n"
            "Leia youtube\\LEIA-ME.md — são 6 passos, todos no navegador.\n"
            "NÃO cole o conteúdo dele no chat: baixe e salve direto na pasta."
        )

    from google_auth_oauthlib.flow import InstalledAppFlow
    fluxo = InstalledAppFlow.from_client_secrets_file(str(SEGREDO_CLIENTE), escopos)
    cred = fluxo.run_local_server(port=0)
    _dpapi_guardar(TOKEN, cred.to_json())
    return cred


def _servico(escopos: list[str] | None = None, *, interativo: bool = False):
    from googleapiclient.discovery import build
    return build("youtube", "v3", credentials=credenciais(escopos, interativo=interativo),
                 cache_discovery=False)


# --------------------------------------------------------------------- subir

@dataclass
class Video:
    arquivo: Path
    titulo: str
    descricao: str
    tags: list[str]
    # Sem default de propósito: o canal produz cena sintética realista, e quem
    # chamar tem que declarar isso conscientemente. Ver o cabeçalho.
    conteudo_sintetico: bool
    privacidade: str = "private"
    categoria: str = CATEGORIA_ENTRETENIMENTO
    idioma: str = "pt-BR"

    def corpo(self) -> dict:
        return {
            "snippet": {
                "title": self.titulo[:100],
                "description": self.descricao[:5000],
                "tags": self.tags,
                "categoryId": self.categoria,
                "defaultLanguage": self.idioma,
                "defaultAudioLanguage": self.idioma,
            },
            "status": {
                "privacyStatus": self.privacidade,
                "selfDeclaredMadeForKids": False,
                "containsSyntheticMedia": self.conteudo_sintetico,
            },
        }


def subir(v: Video, *, ao_progredir=None) -> dict:
    """Sobe pelo protocolo retomável e devolve o recurso do vídeo.

    Devolve dict com `id`, `url` e `privacidade_real` — esta última lida da
    RESPOSTA, não do que pedimos: se a auditoria não passou, o YouTube devolve
    `private` mesmo tendo sido pedido `public`, e sem isso a gente acharia que
    publicou.
    """
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload

    if not v.arquivo.exists():
        raise FaltaConfigurar(f"Arquivo não existe: {v.arquivo}")

    midia = MediaFileUpload(str(v.arquivo), chunksize=PEDACO, resumable=True,
                            mimetype="video/*")
    pedido = _servico().videos().insert(part="snippet,status", body=v.corpo(),
                                        media_body=midia)
    resposta = None
    while resposta is None:
        try:
            situacao, resposta = pedido.next_chunk()
            if situacao and ao_progredir:
                ao_progredir(int(situacao.progress() * 100))
        except HttpError as e:
            raise _traduzir(e) from e

    pedida, real = v.privacidade, resposta["status"]["privacyStatus"]
    return {
        "id": resposta["id"],
        "url": f"https://youtu.be/{resposta['id']}",
        "privacidade_pedida": pedida,
        "privacidade_real": real,
        # O aviso que evita a gente anunciar publicação que não aconteceu.
        "travado_pela_auditoria": real == "private" and pedida != "private",
    }


def _traduzir(e) -> Exception:
    """Traduz o erro da API para o que ele significa AQUI.

    A tabela vem do dossiê de 2026-09-07. Sem isso, `403` é indistinguível
    entre 'auditoria não passou', 'canal no limite' e 'cota do dia acabou' —
    e os três pedem reação diferente.
    """
    motivo = ""
    try:
        motivo = json.loads(e.content.decode())["error"]["errors"][0].get("reason", "")
    except Exception:  # noqa: BLE001
        pass
    mapa = {
        "privacyError": ("O projeto de API ainda NÃO passou pela auditoria de conformidade. "
                         "O vídeo só pode nascer privado. Ver _registros\\YOUTUBE.md §1."),
        "uploadLimitExceeded": ("O CANAL bateu o limite próprio de upload (separado da cota "
                                "da API). Esperar 15+ minutos e tentar de novo."),
        "quotaExceeded": ("Acabou a cota do dia (100 uploads). Ela zera à meia-noite do "
                          "Pacífico."),
        "forbidden": "Escopo insuficiente ou canal sem permissão para este upload.",
    }
    if motivo in mapa:
        return RuntimeError(f"[{motivo}] {mapa[motivo]}")
    return e


# ------------------------------------------------------------------ verificar

def verificar() -> dict:
    """Diz em que passo a configuração está, SEM subir nada e sem gastar cota.

    Cada linha é um fato diferente — 'não configurado', 'configurado e válido' e
    'quebrado' não podem parecer a mesma coisa.
    """
    situacao = {
        "client_secret.json": SEGREDO_CLIENTE.exists(),
        "token guardado": TOKEN.exists(),
        "autorizacao valida": False,
        "canal": None,
        "erro": None,
    }
    if not situacao["client_secret.json"]:
        situacao["erro"] = "falta o client_secret.json — ver LEIA-ME.md"
        return situacao
    try:
        r = _servico().channels().list(part="snippet,status", mine=True).execute()
        situacao["autorizacao valida"] = True
        itens = r.get("items") or []
        if itens:
            situacao["canal"] = itens[0]["snippet"]["title"]
    except FaltaConfigurar as e:
        situacao["erro"] = str(e)
    except Exception as e:  # noqa: BLE001
        situacao["erro"] = f"{type(e).__name__}: {e}"
    return situacao


# ------------------------------------------------------------------------ cli

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Publicar no YouTube (Omega)")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("autorizar", help="abre o navegador uma vez e guarda o token")
    sub.add_parser("verificar", help="diz em que passo a configuração está")

    s = sub.add_parser("subir", help="sobe um vídeo")
    s.add_argument("arquivo", type=Path)
    s.add_argument("--titulo", required=True)
    s.add_argument("--descricao", default="")
    s.add_argument("--tags", default="")
    s.add_argument("--privacidade", default="private",
                   choices=["private", "unlisted", "public"])
    s.add_argument("--sintetico", action="store_true",
                   help="OBRIGATÓRIO quando há cena gerada por IA (é o caso do canal)")
    s.add_argument("--nao-sintetico", action="store_true",
                   help="declara explicitamente que NÃO há mídia sintética")

    a = p.parse_args(argv)
    try:
        if a.cmd == "autorizar":
            credenciais(interativo=True)
            print("Autorizado. Token guardado cifrado por DPAPI.")
            return 0

        if a.cmd == "verificar":
            for k, v in verificar().items():
                print(f"  {k}: {v}")
            return 0

        if a.sintetico == a.nao_sintetico:
            print("ERRO: escolha --sintetico OU --nao-sintetico. O YouTube exige a "
                  "declaração desde 2024-10-30, e o canal produz cena sintética.",
                  file=sys.stderr)
            return 2

        r = subir(Video(
            arquivo=a.arquivo, titulo=a.titulo, descricao=a.descricao,
            tags=[t.strip() for t in a.tags.split(",") if t.strip()],
            conteudo_sintetico=a.sintetico, privacidade=a.privacidade,
        ), ao_progredir=lambda pct: print(f"  {pct}%", end="\r", flush=True))

        print(f"\nno ar: {r['url']}")
        print(f"privacidade pedida: {r['privacidade_pedida']} · real: {r['privacidade_real']}")
        if r["travado_pela_auditoria"]:
            print("\nATENÇÃO: o vídeo ficou PRIVADO apesar de você ter pedido outra coisa.\n"
                  "É a regra de auditoria do YouTube, não um erro. Ver _registros\\YOUTUBE.md")
        return 0

    except FaltaConfigurar as e:
        print(f"\n{e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
