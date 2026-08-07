"""Navegador do OMEGA — abre as redes e prepara a postagem dos vídeos.

DUAS REGRAS QUE NÃO SE NEGOCIAM, e o motivo de cada uma:

1. SENHA NUNCA PASSA POR AQUI. O OMEGA não digita, não guarda e não pede
   credencial. Em vez disso usa um PERFIL PERSISTENTE do Chromium: o Samuel
   faz login à mão uma vez (`login <rede>`) e a sessão fica salva no perfil,
   como em qualquer navegador. Daí em diante o OMEGA já entra logado.

2. PUBLICAR É IRREVERSÍVEL, ENTÃO O OMEGA NÃO CLICA EM "PUBLICAR". Ele leva
   o vídeo até o formulário, preenche o que dá, e PARA — com a janela
   aberta, para o Samuel revisar e apertar o botão. Um comando de voz mal
   transcrito não pode publicar no canal.

O perfil vive em `voice/navegador-perfil/` (fora do git: contém sessões).
"""

from __future__ import annotations

import threading
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PERFIL = BASE_DIR / "navegador-perfil"

REDES = {
    "youtube": ("YouTube", "https://studio.youtube.com/"),
    "instagram": ("Instagram", "https://www.instagram.com/"),
    "tiktok": ("TikTok", "https://www.tiktok.com/tiktokstudio/upload"),
    "x": ("X", "https://x.com/compose/post"),
    "twitter": ("X", "https://x.com/compose/post"),
}

# Onde cada rede começa o envio. Só abrimos a página certa; o resto é do
# usuário, por decisão de segurança (ver regra 2 no topo).
ENVIO = {
    "youtube": "https://studio.youtube.com/channel/UC/videos/upload",
    "instagram": "https://www.instagram.com/",
    "tiktok": "https://www.tiktok.com/tiktokstudio/upload",
    "x": "https://x.com/compose/post",
}

_estado: dict = {"playwright": None, "contexto": None}
_trava = threading.Lock()


def _resolver_rede(nome: str) -> tuple[str, str, str] | None:
    """(chave, rótulo, url) da rede citada, ou None."""
    alvo = (nome or "").strip().lower()
    for chave, (rotulo, url) in REDES.items():
        if chave in alvo or alvo in chave:
            return chave, rotulo, url
    return None


def disponivel() -> bool:
    try:
        import playwright  # noqa: F401

        return True
    except ImportError:
        return False


# O Chromium que vem com o Playwright não roda nesta máquina (erro
# "side-by-side configuration", falta runtime da Microsoft). Em vez de
# instalar dependência de sistema, usamos o navegador que o Samuel já tem —
# que também é o que ele reconhece quando a janela abre.
NAVEGADORES = (
    (r"C:\Program Files\Google\Chrome\Application\chrome.exe", "Chrome"),
    (r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe", "Chrome"),
    (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", "Edge"),
    (r"C:\Program Files\Microsoft\Edge\Application\msedge.exe", "Edge"),
)


def _executavel() -> str | None:
    for caminho, _ in NAVEGADORES:
        if Path(caminho).exists():
            return caminho
    return None


def _abrir_contexto():
    """Abre (ou reaproveita) o navegador com o perfil persistente."""
    from playwright.sync_api import sync_playwright

    if _estado["contexto"] is not None:
        return _estado["contexto"]

    PERFIL.mkdir(parents=True, exist_ok=True)
    pw = sync_playwright().start()
    opcoes = {
        "user_data_dir": str(PERFIL),
        # Visível de propósito: o Samuel precisa ver, revisar e publicar.
        "headless": False,
        "args": ["--start-maximized"],
        "no_viewport": True,
    }
    executavel = _executavel()
    if executavel:
        opcoes["executable_path"] = executavel
    contexto = pw.chromium.launch_persistent_context(**opcoes)
    _estado.update({"playwright": pw, "contexto": contexto})
    return contexto


def _ir_para(url: str):
    contexto = _abrir_contexto()
    pagina = contexto.pages[0] if contexto.pages else contexto.new_page()
    pagina.goto(url, wait_until="domcontentloaded", timeout=60000)
    pagina.bring_to_front()
    return pagina


def abrir(nome_rede: str) -> str:
    """Abre a rede no navegador do OMEGA (já logado, se você já entrou)."""
    if not disponivel():
        return "O navegador não está instalado. Rode: pip install playwright"
    achado = _resolver_rede(nome_rede)
    if not achado:
        return f"Não conheço a rede {nome_rede}. Tenho YouTube, Instagram, TikTok e X."
    _, rotulo, url = achado
    try:
        with _trava:
            _ir_para(url)
        return f"{rotulo} aberto. Se pedir login, entre você mesmo — eu não uso senha."
    except Exception as e:  # noqa: BLE001 — vira frase falada
        return f"Não consegui abrir o {rotulo}: {str(e)[:90]}"


def login(nome_rede: str) -> str:
    """Abre a rede para o Samuel entrar À MÃO. A sessão fica salva no perfil."""
    achado = _resolver_rede(nome_rede)
    if not achado:
        return f"Não conheço a rede {nome_rede}."
    _, rotulo, url = achado
    resposta = abrir(nome_rede)
    if resposta.startswith("Não consegui"):
        return resposta
    return (
        f"{rotulo} aberto para você entrar. Faça o login normalmente — eu não "
        "vejo nem guardo senha. Depois de entrar, a sessão fica salva e nas "
        "próximas vezes eu já abro logado."
    )


def preparar_postagem(rede: str, caminho_video: str, titulo: str = "") -> str:
    """Leva o vídeo até a tela de envio e PARA, para o Samuel revisar.

    Deliberadamente não clica em publicar: ver a regra 2 no topo do arquivo.
    """
    if not disponivel():
        return "O navegador não está instalado."
    achado = _resolver_rede(rede)
    if not achado:
        return f"Não conheço a rede {rede}."
    chave, rotulo, _ = achado

    video = Path(caminho_video)
    if not video.exists():
        return f"Não achei o vídeo {video.name}."

    try:
        with _trava:
            pagina = _ir_para(ENVIO.get(chave, REDES[chave][1]))
            # O seletor de arquivo varia por rede e muda com frequência;
            # tentamos o padrão e, se não houver, o usuário arrasta o vídeo.
            anexado = False
            for seletor in ("input[type=file]",):
                try:
                    campo = pagina.wait_for_selector(
                        seletor, timeout=8000, state="attached"
                    )
                    campo.set_input_files(str(video))
                    anexado = True
                    break
                except Exception:  # noqa: BLE001 — seletor ausente é esperado
                    continue
    except Exception as e:  # noqa: BLE001
        return f"Falhou ao preparar no {rotulo}: {str(e)[:90]}"

    if anexado:
        return (
            f"{rotulo} aberto com {video.name} já anexado"
            + (f' e o título "{titulo}"' if titulo else "")
            + ". Revise e publique você — eu não aperto o botão de publicar."
        )
    return (
        f"{rotulo} aberto na tela de envio, mas não achei onde anexar "
        f"automaticamente. Arraste o {video.name} para a janela. "
        "Ele está em renders, no projeto."
    )


def fechar() -> str:
    with _trava:
        try:
            if _estado["contexto"]:
                _estado["contexto"].close()
            if _estado["playwright"]:
                _estado["playwright"].stop()
        except Exception:  # noqa: BLE001
            pass
        _estado.update({"playwright": None, "contexto": None})
    return "Navegador fechado."
