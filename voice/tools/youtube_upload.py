"""Upload de vídeo pro YouTube via API oficial — sem navegador, sem senha.

Existe porque o `navegador.py` não serve pro YouTube: testado em 15/08/2026,
o Google bloqueia login de QUALQUER navegador sob controle de automação
("Esse navegador ou app pode não ser seguro") — o CDP do Playwright deixa
marca mesmo com o Samuel digitando a senha à mão, então aquele caminho está
permanentemente fechado para essa rede especificamente (Instagram/TikTok/X
continuam pelo navegador.py, sem esse bloqueio).

A saída é a API oficial do YouTube com OAuth2: o consentimento abre o
navegador PADRÃO do sistema (sem automação grudada — é por isso que o
Google não bloqueia), só na primeira vez; depois disso o token fica salvo e
o upload sobe direto pela API, sem simular nenhum clique.

DUAS REGRAS HERDADAS do navegador.py — continuam não se negociando aqui:
1. SENHA NUNCA PASSA POR AQUI. O consentimento acontece na tela REAL do
   Google, fora do nosso controle; só recebemos o token depois de aprovado.
2. NUNCA SOBE COMO PÚBLICO. Todo envio vai como "não listado"
   (privacyStatus="unlisted") — existe, tem link, mas só fica visível no
   canal/busca quando o Samuel revisar no Studio e trocar a visibilidade
   manualmente. Mesma régua do `preparar_postagem`, adaptada pra API: o
   OMEGA prepara, nunca aperta o botão final sozinho.

`youtube_client.json` (baixado do Google Cloud Console) e `token.json`
(gerado no primeiro uso) ficam em `config/`, fora do git — ver .gitignore.
"""

from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
CLIENT_SECRETS = CONFIG_DIR / "youtube_client.json"
TOKEN_FILE = CONFIG_DIR / "token.json"

# Só o escopo de upload — pedir leitura de analytics ou gestão de comentários
# junto ampliaria à toa o que um token vazado conseguiria fazer.
ESCOPOS = ["https://www.googleapis.com/auth/youtube.upload"]

CATEGORIA_PADRAO = "24"  # Entretenimento — dá para passar outra por vídeo


def disponivel() -> bool:
    try:
        import google_auth_oauthlib  # noqa: F401
        import googleapiclient  # noqa: F401

        return True
    except ImportError:
        return False


def _credenciais():
    """Token salvo e válido? Usa. Expirado? Renova. Nenhum dos dois? Pede
    consentimento uma vez, no navegador padrão do sistema (não no Chromium
    automatizado do navegador.py — ver o motivo no topo do arquivo).
    """
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), ESCOPOS)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    elif not creds or not creds.valid:
        if not CLIENT_SECRETS.exists():
            raise FileNotFoundError(
                f"Não achei {CLIENT_SECRETS.name} em {CONFIG_DIR}. Baixe as "
                "credenciais no Google Cloud Console antes (ID do cliente "
                "OAuth, tipo App para computador)."
            )
        fluxo = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS), ESCOPOS)
        creds = fluxo.run_local_server(port=0)

    TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    return creds


def enviar(caminho_video: str, titulo: str, descricao: str = "",
           tags: list[str] | None = None, categoria: str = CATEGORIA_PADRAO) -> str:
    """Sobe o vídeo como NÃO LISTADO. Devolve uma frase falável com o link.

    Upload resumível de propósito: um vídeo de mitologia com blocos Seedance
    pesa dezenas de MB, e uma queda de rede no meio não pode obrigar a
    recomeçar do zero.
    """
    if not disponivel():
        return ("Falta instalar as bibliotecas do YouTube. Rode: pip install "
                "google-auth-oauthlib google-api-python-client")

    video = Path(caminho_video)
    if not video.exists():
        return f"Não achei o vídeo {video.name}."
    if not titulo.strip():
        return "Preciso de um título para subir o vídeo."

    try:
        creds = _credenciais()
    except FileNotFoundError as e:
        return str(e)

    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload

    youtube = build("youtube", "v3", credentials=creds)
    corpo = {
        "snippet": {
            "title": titulo[:100],
            "description": descricao[:5000],
            "tags": tags or [],
            "categoryId": categoria,
        },
        "status": {
            "privacyStatus": "unlisted",
            "selfDeclaredMadeForKids": False,
        },
    }
    midia = MediaFileUpload(str(video), chunksize=-1, resumable=True, mimetype="video/*")
    pedido = youtube.videos().insert(part="snippet,status", body=corpo, media_body=midia)

    try:
        resposta = None
        while resposta is None:
            _status, resposta = pedido.next_chunk()
    except HttpError as e:
        return f"Falhou no upload: {str(e)[:150]}"

    video_id = resposta["id"]
    return (
        f'"{titulo}" subiu como NÃO LISTADO: https://youtu.be/{video_id} — '
        "revise no Studio e troque a visibilidade quando quiser publicar de verdade."
    )
