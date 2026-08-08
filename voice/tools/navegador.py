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
# Os prints ficam fora do git: mostram a tela logada do Samuel.
PRINTS = BASE_DIR / "_prints"

REDES = {
    "youtube": ("YouTube", "https://studio.youtube.com/"),
    "instagram": ("Instagram", "https://www.instagram.com/"),
    "tiktok": ("TikTok", "https://www.tiktok.com/tiktokstudio/upload"),
    "x": ("X", "https://x.com/compose/post"),
    "twitter": ("X", "https://x.com/compose/post"),
}

# Onde cada rede começa o envio. Só abrimos a página certa; o resto é do
# usuário, por decisão de segurança (ver regra 2 no topo).
#
# O YouTube usa `youtube.com/upload`, e não a URL do Studio: ela redireciona
# para `.../channel/UC/content?d=ud` — o `UC` é resolvido pelo próprio
# YouTube para o canal de quem está logado, e o `?d=ud` já abre a caixa de
# envio. Verificado seguindo os redirecionamentos.
ENVIO = {
    "youtube": "https://www.youtube.com/upload",
    "instagram": "https://www.instagram.com/",
    "tiktok": "https://www.tiktok.com/tiktokstudio/upload",
    "x": "https://x.com/compose/post",
}

# Como chegar até o campo de arquivo em cada rede, em ordem de tentativa.
# Um `input[type=file]` só existe depois de a página montar o formulário, e
# no Instagram ele nem existe até clicar em "Criar". Antes disto o código
# tinha um laço sobre UMA tupla de um seletor só — que parecia robustez e
# não era.
#
# Isto vai quebrar quando as redes mudarem o layout: é a natureza de
# automação de navegador. O que dá para garantir é que a quebra seja DITA,
# com o print na tela, em vez de virar um "não achei onde anexar" mudo.
CAMINHO_ATE_O_ARQUIVO: dict[str, tuple[tuple[str, ...], ...]] = {
    # (botões a clicar antes, ...) — cada tupla é uma tentativa independente
    "youtube": (
        (),                                    # o ?d=ud já abre a caixa
        ("button:has-text('Selecionar arquivos')",),
        ("#select-files-button",),
    ),
    "instagram": (
        ("svg[aria-label='Nova publicação']",),
        ("svg[aria-label='New post']",),
        ("a:has-text('Criar')", "span:has-text('Publicação')"),
    ),
    "tiktok": (
        (),
        ("button:has-text('Selecionar vídeo')",),
        ("button:has-text('Select video')",),
    ),
    "x": (
        (),
        ("input[data-testid='fileInput']",),
    ),
}

_estado: dict = {"playwright": None, "contexto": None,
                 "navegador": "", "pagina": None}
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
# OPERA GX NÃO ENTRA NESTA LISTA, e o motivo é medido: ele até é lançado pelo
# Playwright (é Chromium 133), mas TODA navegação morre com ERR_ABORTED —
# testado com example.com, google.com e o Trends, e com as três correções
# conhecidas (desligar VPN/adblock, desligar extensões, --remote-allow-origins).
# É limitação do Opera com automação. O Samuel pode continuar usando o GX
# normalmente: a gravação de aula e a captura de tela não dependem de qual
# navegador é, só do que sai no som e do que está na tela.
# BRAVE PRIMEIRO, por escolha do Samuel — ele prefere Brave e Opera ao Chrome,
# e o Opera não serve. Testado: lança e navega em example.com, no upload do
# YouTube e no Trends.
#
# A ressalva que eu tinha (o Brave bloqueia rastreador por padrão, e isso pode
# esconder um botão em formulário de upload) continua de pé — é por isso que
# `preparar_postagem` tira print quando não acha o campo de arquivo. Se algum
# dia uma rede quebrar só no Brave, `"navegador": "chrome"` no config resolve
# sem mexer em código.
NAVEGADORES = (
    (r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe", "Brave"),
    (r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe", "Brave"),
    (r"C:\Program Files\Google\Chrome\Application\chrome.exe", "Chrome"),
    (r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe", "Chrome"),
    (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", "Edge"),
    (r"C:\Program Files\Microsoft\Edge\Application\msedge.exe", "Edge"),
)


def _preferido() -> str:
    """Qual navegador o Samuel escolheu no config, se escolheu algum."""
    try:
        import json

        cfg = json.loads((BASE_DIR / "config" / "api_keys.json")
                         .read_text(encoding="utf-8-sig"))
        return (cfg.get("navegador") or "").strip().lower()
    except Exception:  # noqa: BLE001
        return ""


def _executavel() -> tuple[str, str] | tuple[None, None]:
    """(caminho, nome) do navegador a usar."""
    preferido = _preferido()
    if preferido:
        # Caminho completo também vale, para quem instalou fora do padrão.
        if Path(preferido).exists():
            return preferido, Path(preferido).stem
        for caminho, nome in NAVEGADORES:
            if nome.lower() == preferido and Path(caminho).exists():
                return caminho, nome
    for caminho, nome in NAVEGADORES:
        if Path(caminho).exists():
            return caminho, nome
    return None, None


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
    executavel, nome = _executavel()
    if executavel:
        opcoes["executable_path"] = executavel
        # Sem isto o Brave abre o tour de boas-vindas na primeira vez e a
        # navegação chega numa aba que não é a nossa.
        opcoes["args"] = list(opcoes["args"]) + ["--no-first-run",
                                                 "--no-default-browser-check"]
    _estado["navegador"] = nome or "Chromium"
    contexto = pw.chromium.launch_persistent_context(**opcoes)
    _estado.update({"playwright": pw, "contexto": contexto})
    return contexto


def _nossa_pagina():
    """A aba que o OMEGA usa — guardada, não adivinhada.

    O Brave abre abas próprias (boas-vindas, nova aba), então `pages[0]` e
    `pages[-1]` deixam de ser a mesma coisa: o print saía de um `about:blank`
    enquanto a navegação acontecia noutra aba. Com o Chrome isso passava
    despercebido porque só havia uma.
    """
    contexto = _abrir_contexto()
    pagina = _estado.get("pagina")
    try:
        if pagina is not None and not pagina.is_closed():
            return pagina
    except Exception:  # noqa: BLE001 — página morta se comporta como ausente
        pass
    pagina = contexto.pages[0] if contexto.pages else contexto.new_page()
    _estado["pagina"] = pagina
    return pagina


def _ir_para(url: str):
    pagina = _nossa_pagina()
    pagina.goto(url, wait_until="domcontentloaded", timeout=60000)
    pagina.bring_to_front()
    return pagina


def abrir(nome_rede: str) -> str:
    """Abre a rede no navegador do OMEGA (já logado, se você já entrou)."""
    if not disponivel():
        return "O navegador não está instalado. Rode: pip install playwright"
    if _executavel()[0] is None:
        return ("Não achei Chrome, Brave nem Edge nesta máquina. O Opera GX "
                "não serve: ele abre mas não navega sob automação.")
    achado = _resolver_rede(nome_rede)
    if not achado:
        return f"Não conheço a rede {nome_rede}. Tenho YouTube, Instagram, TikTok e X."
    _, rotulo, url = achado
    try:
        with _trava:
            _ir_para(url)
        return (f"{rotulo} aberto no {_estado['navegador']}. Se pedir login, "
                "entre você mesmo — eu não uso senha.")
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


def preparar_postagem(rede: str, caminho_video: str, titulo: str = "",
                      ui=None) -> str:
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
            if _parece_tela_de_login(pagina):
                _mostrar(ui, pagina, f"{rotulo} — precisa de login")
                return (
                    f"O {rotulo} está pedindo login. Entre você mesmo na janela "
                    "que abri — eu não uso senha. Depois peça de novo."
                )
            anexado, onde_parou = _anexar(pagina, chave, video)
            _mostrar(ui, pagina, f"{rotulo} — {'anexado' if anexado else 'parei aqui'}")
    except Exception as e:  # noqa: BLE001
        return f"Falhou ao preparar no {rotulo}: {str(e)[:90]}"

    if anexado:
        return (
            f"{rotulo} aberto com {video.name} já anexado"
            + (f' e o título "{titulo}"' if titulo else "")
            + ". Revise e publique você — eu não aperto o botão de publicar."
        )
    # Dizer ONDE parou, e não só que não deu: é a diferença entre o Samuel
    # arrastar o arquivo em dez segundos e ele achar que o OMEGA quebrou.
    return (
        f"{rotulo} aberto, mas não cheguei ao campo de arquivo ({onde_parou}). "
        f"Arraste o {video.name} para a janela — está na pasta renders do "
        "projeto. Coloquei um print na tela para você ver onde parei."
    )


def _parece_tela_de_login(pagina) -> bool:
    """Detecta a parede de login antes de tentar anexar.

    Sem isto o OMEGA tentava anexar num formulário que não existe e
    respondia "não achei onde anexar" — verdade, mas inútil: o problema era
    outro, e a ação a tomar também.
    """
    try:
        url = (pagina.url or "").lower()
    except Exception:  # noqa: BLE001
        return False
    return any(m in url for m in (
        "accounts.google.com", "/login", "signin", "sign_in", "/auth"))


def _anexar(pagina, chave: str, video: Path) -> tuple[bool, str]:
    """Tenta cada caminho conhecido até o campo de arquivo.

    Devolve (conseguiu, descrição de onde parou).
    """
    ultimo = "nenhum caminho conhecido para esta rede"
    for passos in CAMINHO_ATE_O_ARQUIVO.get(chave, ((),)):
        try:
            for seletor in passos:
                pagina.click(seletor, timeout=6000)
                pagina.wait_for_timeout(800)
            campo = pagina.wait_for_selector(
                "input[type=file]", timeout=8000, state="attached")
            campo.set_input_files(str(video))
            # Anexar não é instantâneo: sem esperar, o print sai antes de a
            # página reagir e parece que não funcionou.
            pagina.wait_for_timeout(2500)
            return True, ""
        except Exception as e:  # noqa: BLE001 — caminho ausente é esperado
            ultimo = (f"parei em '{passos[0]}'" if passos
                      else f"não apareceu campo de arquivo: {str(e)[:50]}")
            continue
    return False, ultimo


def _mostrar(ui, pagina, titulo: str) -> None:
    """Print da janela do navegador dentro da tela do OMEGA.

    Pedido do Samuel: acompanhar sem ter que caçar a janela do Chrome. Também
    é o que torna uma falha diagnosticável — a mensagem diz onde parou, o
    print mostra o que havia lá.
    """
    if ui is None or not hasattr(ui, "show_image"):
        return
    try:
        PRINTS.mkdir(parents=True, exist_ok=True)
        alvo = PRINTS / "navegador.png"
        pagina.screenshot(path=str(alvo), full_page=False)
        ui.show_image(titulo, str(alvo))
    except Exception:  # noqa: BLE001 — print é conveniência, não pode derrubar
        pass


def ver(ui=None) -> str:
    """"O que você está vendo?" — print do navegador na tela do OMEGA."""
    with _trava:
        contexto = _estado["contexto"]
        if contexto is None or not contexto.pages:
            return "Não estou com nenhuma página aberta."
        # A NOSSA aba, não a última que o navegador abriu.
        pagina = _estado.get("pagina") or contexto.pages[0]
        try:
            endereco = pagina.url
        except Exception:  # noqa: BLE001
            return "A janela do navegador foi fechada."
        _mostrar(ui, pagina, "Navegador do OMEGA")
    curto = endereco.split("?")[0][:70]
    return f"Estou em {curto}. Coloquei o print na tela."


def fechar() -> str:
    with _trava:
        try:
            if _estado["contexto"]:
                _estado["contexto"].close()
            if _estado["playwright"]:
                _estado["playwright"].stop()
        except Exception:  # noqa: BLE001
            pass
        _estado.update({"playwright": None, "contexto": None, "pagina": None})
    return "Navegador fechado."
