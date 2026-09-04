"""As seis fases de um vídeo do canal — a espinha que dá nome ao que já existe.

POR QUE ISTO EXISTE

O `AJUDA` do OMEGA tem quarenta entradas e ganha mais a cada sessão. O Samuel
disse, com estas palavras, que vai esquecer. O que ele pediu no lugar foi um
vocabulário único: *"vamos começar a fase 0"*.

Então este módulo NÃO FAZ O TRABALHO. Ele sabe qual é o trabalho, quem já o faz,
e onde cada criatura parou. Quem pesquisa continua sendo o `pipeline.py`; quem
renderiza continua sendo o `studio.py`; quem abre a rede continua sendo o
`navegador.py`. Aqui só existe a ordem das coisas e a memória do que já andou.

DUAS REGRAS DE HONESTIDADE

1. FASE SEM FERRAMENTA NÃO MENTE. Se `executor` é `None`, a fase entrega o que
   pode e fica em `aguardando você` — nunca em `pronta`. Atualizado em
   04/09/2026: das seis, CINCO já têm executor real. A fase 3 (vídeo) foi a
   última a cair — ficou parada de 21/08 a 04/09 não por falta de MCP, mas
   porque a edição que a destravava foi recusada pelo classificador do modo
   automático; a mudança esperou escrita em
   `PENDENTE-FASE3-destravar-video.md` até ser aplicada. A fase 4 (edição)
   tem executor desde 21/08/2026 (`_run_edicao` em pipeline.py, HTTP direto
   contra o Studio), testado de verdade. A fase 5 (publicação) é a ÚNICA que
   continua PERMANENTEMENTE sem executor, e por decisão de projeto, não por
   limitação: publicar é irreversível, então o botão fica sempre com o
   Samuel. Mesmo assim ela já escreve o pacote de SEO inteiro em segundo
   plano (ver `comecar()`, ramo `n == 5`) — e desde 03/09 o
   `local_commands._postar` sobe o arquivo pela API do YouTube quando ele
   pede, sempre como NÃO LISTADO: existe, tem link, e só vira público quando
   ele troca a visibilidade com a própria mão.
2. O ESTADO VIVE EM DISCO, na pasta do projeto que o Studio já lê. O app pode
   ser reiniciado no meio de uma produção de dias, e "em que pé estamos" tem
   que responder certo depois disso.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .pipeline import AI_PROJECT_ROOT, _project_dir

# Os estados que uma fase pode ter. `aguardando` é o que impede o OMEGA de
# dizer "pronto" sobre algo que depende do Samuel — é a diferença entre um
# painel útil e um painel que mente.
NAO_COMECOU = "não começou"
RODANDO = "rodando"
PRONTA = "pronta"
AGUARDANDO = "aguardando você"
FALHOU = "falhou"

# Cada fase: número, nome curto, o que entrega, e quem faz.
#
# `executor` é a fase equivalente no `pipeline.py` quando existe uma; None
# significa que o trabalho não é automatizável hoje e a fase só orienta.
FASES: tuple[dict, ...] = (
    {
        "n": 0, "nome": "Pesquisa", "chave": "pesquisa",
        "entrega": "o dossiê da criatura, com fontes e veredito por afirmação",
        "executor": "pesquisa",
        "precisa": "só do nome da criatura",
    },
    {
        "n": 1, "nome": "Model sheets", "chave": "model-sheets",
        "entrega": "o roteiro de narração e a cara de cada personagem",
        "executor": "model-sheets",
        "precisa": "do dossiê da fase 0",
        # Ele escolheu separar 1 e 2 justamente por isto.
        "para_aqui": ("aprovar a cara dos personagens antes dos storyboards — "
                      "errar o personagem depois de catorze blocos custa os catorze"),
    },
    {
        "n": 2, "nome": "Storyboards", "chave": "storyboards",
        "entrega": "os storyboards e os prompts de vídeo (Seedance)",
        "executor": "storyboards",
        "precisa": "dos model sheets aprovados na fase 1",
    },
    {
        "n": 3, "nome": "Vídeos", "chave": "videos",
        "entrega": "os clipes de cada cena",
        # Destravada em 04/09/2026 — ver KAIROGEN_FERRAMENTAS_VIDEO no
        # pipeline.py. O campo "falta" saiu junto: deixa de ser lido assim
        # que existe executor, e deixar lá era guardar uma frase que o OMEGA
        # nunca mais diria e que já não era verdade.
        "executor": "videos",
        "precisa": "dos prompts da fase 2",
    },
    {
        "n": 4, "nome": "Edição", "chave": "edicao",
        "entrega": "o vídeo montado, com narração e trilha",
        "executor": "edicao",
        "precisa": ("dos clipes da fase 3 E da narração pronta (ElevenLabs) "
                    "em public/audio — eu não gero narração sozinho"),
    },
    {
        "n": 5, "nome": "Publicação", "chave": "publicacao",
        "entrega": "o pacote de SEO e o vídeo no canal, como não listado",
        "executor": None,
        "precisa": "do vídeo montado da fase 4",
        # Atualizado em 04/09/2026: a frase antiga ("eu levo até o formulário
        # e PARO") descrevia o caminho do navegador, que continua valendo para
        # Instagram/TikTok/X. Para o YouTube o caminho mudou — o Google bloqueia
        # login em qualquer navegador automatizado, então virou API oficial, e
        # o vídeo sobe NÃO LISTADO. O que não mudou é o que importa: o OMEGA
        # nunca torna nada público sozinho.
        "falta": ("eu subo como NÃO LISTADO e paro aí. Tornar público é "
                  "irreversível, e esse botão é seu"),
    },
)

ARQUIVO = "fases.json"


def por_numero(n: int) -> dict | None:
    return next((f for f in FASES if f["n"] == n), None)


def _caminho(criatura: str) -> Path:
    return _project_dir(criatura) / "notes" / ARQUIVO


def ler(criatura: str) -> dict:
    try:
        return json.loads(_caminho(criatura).read_text(encoding="utf-8-sig"))
    except Exception:  # noqa: BLE001
        return {"criatura": criatura, "fases": {}}


def _gravar(criatura: str, dados: dict) -> None:
    alvo = _caminho(criatura)
    try:
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text(json.dumps(dados, ensure_ascii=False, indent=1),
                        encoding="utf-8")
    except Exception:  # noqa: BLE001 — anotar o estado não pode derrubar nada
        pass


def marcar(criatura: str, n: int, estado: str, nota: str = "") -> None:
    dados = ler(criatura)
    dados["criatura"] = criatura
    dados.setdefault("fases", {})[str(n)] = {
        "estado": estado, "nota": nota,
        "quando": f"{datetime.now():%Y-%m-%d %H:%M}",
    }
    _gravar(criatura, dados)


def estado_de(criatura: str, n: int) -> str:
    return (ler(criatura).get("fases", {}).get(str(n), {})
            .get("estado") or NAO_COMECOU)


def _entregou(criatura: str, n: int) -> bool:
    """Os arquivos da fase existem no disco?

    A verdade sobre o que foi feito está nos ARQUIVOS, não no meu registro: o
    Samuel pode ter gerado algo à mão, ou o app pode ter caído antes de anotar.
    """
    from .pipeline import _arquivos_da_fase

    fase = por_numero(n)
    if not fase or not fase["executor"]:
        return False
    arquivos = _arquivos_da_fase(criatura, fase["executor"])
    return bool(arquivos) and all(a.exists() for a in arquivos)


def proxima(criatura: str) -> int | None:
    """A primeira fase que ainda não terminou. None quando tudo acabou."""
    for fase in FASES:
        n = fase["n"]
        if estado_de(criatura, n) == PRONTA or _entregou(criatura, n):
            continue
        return n
    return None


def _linha(criatura: str, fase: dict) -> str:
    n = fase["n"]
    estado = estado_de(criatura, n)
    if estado != PRONTA and _entregou(criatura, n):
        estado = PRONTA          # o arquivo manda mais que o meu registro
    return f"fase {n} ({fase['nome']}): {estado}"


def situacao(criatura: str = "") -> str:
    """Onde estamos — de uma criatura, ou de todas as que existem."""
    criatura = (criatura or "").strip()
    if criatura:
        alvo = proxima(criatura)
        linhas = "; ".join(_linha(criatura, f) for f in FASES)
        if alvo is None:
            return f"{criatura}: as seis fases terminaram. {linhas}"
        fase = por_numero(alvo)
        return (f"{criatura} está na fase {alvo}, {fase['nome']} "
                f"({estado_de(criatura, alvo)}). {linhas}")

    raiz = AI_PROJECT_ROOT / "Criaturas"
    if not raiz.is_dir():
        return "Ainda não há criatura nenhuma em produção."
    partes = []
    for pasta in sorted(raiz.iterdir()):
        if not pasta.is_dir() or pasta.name.startswith((".", "_")):
            continue
        alvo = proxima(pasta.name)
        if alvo is None:
            partes.append(f"{pasta.name}: terminada")
        else:
            fase = por_numero(alvo)
            partes.append(f"{pasta.name}: fase {alvo}, {fase['nome']} "
                          f"({estado_de(pasta.name, alvo)})")
    if not partes:
        return "Ainda não há criatura nenhuma em produção."
    return "Em produção — " + "; ".join(partes) + "."


def em_andamento() -> list[str]:
    """Criaturas que já começaram e ainda não acabaram.

    Serve ao "pode seguir" sem nome: se só uma está no meio do caminho, não há
    ambiguidade e não faz sentido perguntar. Com duas, perguntar é obrigatório
    — seguir a errada custa uma pesquisa inteira.
    """
    raiz = AI_PROJECT_ROOT / "Criaturas"
    if not raiz.is_dir():
        return []
    vivas = []
    for pasta in sorted(raiz.iterdir()):
        if not pasta.is_dir() or pasta.name.startswith((".", "_")):
            continue
        alvo = proxima(pasta.name)
        if alvo is not None and alvo > 0:
            vivas.append(pasta.name)
    return vivas


def anunciar(criatura: str, terminou: int) -> str:
    """O que vem depois — dito por ele, para o Samuel não decorar comando.

    Esta é a peça que aposenta as quarenta entradas do AJUDA: terminada uma
    fase, ele mesmo diz qual é a próxima, o que ela faz e o que precisa. O
    Samuel só responde "pode seguir".
    """
    seguinte = por_numero(terminou + 1)
    if seguinte is None:
        return (f"Fase {terminou} concluída, e era a última. {criatura} está "
                "pronta para ir ao ar.")
    aviso = ""
    if not seguinte["executor"]:
        aviso = f" Aviso: {seguinte['falta']}."
    return (f"Fase {terminou} concluída. A próxima é a fase {seguinte['n']}, "
            f"{seguinte['nome']}: entrega {seguinte['entrega']}.{aviso} "
            "Diga 'pode seguir' quando quiser.")


def comecar(criatura: str, n: int, ui=None) -> str:
    """Dispara uma fase. Quem trabalha é o módulo de sempre."""
    criatura = (criatura or "").strip()
    if not criatura:
        return "Me diga de qual criatura, senhor."
    fase = por_numero(n)
    if fase is None:
        return f"Só existem as fases 0 a {FASES[-1]['n']}."

    anterior = por_numero(n - 1)
    if anterior and estado_de(criatura, n - 1) != PRONTA and \
            not _entregou(criatura, n - 1):
        return (f"A fase {n} precisa {fase['precisa']}, e a fase {n - 1} "
                f"({anterior['nome']}) ainda não terminou. Quer que eu comece "
                f"por ela?")

    if not fase["executor"]:
        marcar(criatura, n, AGUARDANDO, fase["falta"])
        resposta = (f"Fase {n}, {fase['nome']}: {fase['falta']}. "
                    f"O que ela entrega é {fase['entrega']}. "
                    "Deixei anotado que está esperando você.")
        if n == 5:
            # A publicação é a outra fase em que ele quis o curso agindo
            # sozinho — e é a que mais rende: título, descrição, tags e
            # thumbnail são decididos aqui, e é aqui que errar custa alcance.
            from . import curso as _curso

            material = _curso.orientar(
                ("titulo", "thumbnail", "descricao", "tags", "quando-postar"),
                sobre=criatura)
            if material:
                resposta += "\n\n" + material

            # DESTRAVADO EM 21/08/2026: além de mostrar as regras do curso,
            # dispara em segundo plano a escrita de verdade do pacote (título,
            # descrição, tags, thumbnail gerada) — skill `postagem`, fase
            # `seo` do pipeline. Continua PARANDO antes de publicar: a fase 5
            # em si nunca ganha `executor` (fica None ali em cima, de
            # propósito), e o Claude que escreve o pacote não tem NENHUMA
            # ferramenta de navegador/upload no allowedTools — só imagem.
            # "Publicar é seu" continua verdade, só o trabalho de PREPARAR
            # deixou de ser manual.
            from .pipeline import pipeline_criatura

            aviso_seo = pipeline_criatura(
                {"creature": criatura, "phase": "seo"})
            resposta += (
                f"\n\nTambém já iniciei o pacote de SEO e a thumbnail em "
                f"segundo plano: {aviso_seo}"
            )
        return resposta

    from .pipeline import pipeline_criatura

    marcar(criatura, n, RODANDO)
    resposta = pipeline_criatura({"creature": criatura,
                                  "phase": fase["executor"]})
    parada = f" Depois desta eu paro, para você {fase['para_aqui']}." \
        if fase.get("para_aqui") else ""
    return f"Fase {n}, {fase['nome']}. {resposta}{parada}"


def seguir(criatura: str, ui=None) -> str:
    """"pode seguir" — avança a partir de onde a criatura está."""
    alvo = proxima(criatura)
    if alvo is None:
        return f"{criatura} já passou pelas seis fases."
    return comecar(criatura, alvo, ui)
