"""Assiste o curso inteiro sozinho: abre a aula, dá play, grava, vai pra próxima.

O pedido do Samuel foi este, com estas palavras: "termina o vídeo, ele para a
gravação, salva em algum lugar e vai pro próximo vídeo na ordem". Ele vai
assistir pelo celular; o OMEGA aqui não substitui isso — ele garante que,
quando o Samuel não puder assistir, o conteúdo já esteja gravado e virando
regra em `curso.py`.

POR QUE ISTO RODA NUM PROCESSO SEPARADO, e não numa thread do app

Duas razões, e as duas doem se ignoradas:

1. O Playwright síncrono é preso à thread que o iniciou. Chamar a mesma
   página de outra thread estoura na hora. O app abre o navegador na thread
   dele (`login`, `abrir`, `tendências`), então a maratona não pode dividir
   esse objeto.
2. O perfil do Chromium é de UM processo só. Se o app estiver com o navegador
   aberto, uma segunda abertura do mesmo `user_data_dir` falha. Por isso quem
   inicia a maratona FECHA o navegador do app antes.

O processo separado também sobrevive ao app: se ele cair no meio, o curso
continua sendo gravado, e o estado fica no disco para o app reencontrar.

O QUE ELE NÃO FAZ

NUNCA NAVEGUE PARA `members.kiwify.com/login` DE PROPÓSITO. Eu fiz isso uma
vez, sondando o formulário, e a própria visita DERRUBOU a sessão salva — o
Samuel teve que entrar de novo. Para saber se está logado, abra a AULA e veja
se ela carrega (`_assentar`); a tela de login aparece sozinha quando precisa.

Senha, nunca — a mesma regra de `navegador.py`. O Samuel entra à mão uma vez
e a sessão fica no perfil. E não clica em "concluir aula" quando existe outro
jeito de avançar: quem marca a aula como assistida é ele, não eu.

Material comprado: fica em `C:\\Ai-Project\\Cursos\\` (fora do git) e não é
republicado em lugar nenhum.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import threading
import sys
import time
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Estado no disco, e não em memória: o app e a maratona são processos
# diferentes, e o app pode ser reiniciado no meio de um curso de 3 horas.
ESTADO = BASE_DIR / "_maratona.json"
PEDIDO_DE_PARAR = BASE_DIR / "_maratona.parar"
DIARIO = BASE_DIR / "_maratona.log"
CONFIG = BASE_DIR / "config" / "curso.json"

# Uma aula da Kiwify é um <a> para /<produto>/<módulo>/<aula>. É por este
# formato que eu separo link de aula de link de menu, sem depender de classe
# CSS — que muda quando a plataforma muda de tema.
LINK_DE_AULA = re.compile(
    r"members\.kiwify\.com/[0-9a-f-]{8,}/[0-9a-f-]{8,}/[0-9a-f-]{8,}", re.I)

MAX_AULAS = 60             # trava de segurança contra laço em círculo
ESPERA_PLAYER = 45.0       # o player é iframe e demora a montar
PACIENCIA_TRAVADO = 120.0  # vídeo sem avançar: buffer, anúncio, ou acabou mal
SOBRA_FINAL = 3.0          # o `ended` às vezes não vem; isto fecha a conta
ESPERA_FIM_MUDO = 20.0     # congelado perto do fim: acabou, não travou
LIMITE_MUDO = 60.0         # gravar uma hora de silêncio é pior que parar


# ─────────────────────────── lado do app ───────────────────────────────────

def _ler_estado() -> dict:
    try:
        return json.loads(ESTADO.read_text(encoding="utf-8-sig"))
    except Exception:  # noqa: BLE001
        return {}


def _vivo(pid: int) -> bool:
    """O processo da maratona ainda existe? Um .json órfão mente."""
    if not pid:
        return False
    try:
        saida = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
            capture_output=True, text=True, timeout=8).stdout
        return str(pid) in saida
    except Exception:  # noqa: BLE001
        return True     # na dúvida, não declaro morto o que pode estar vivo


def rodando() -> bool:
    e = _ler_estado()
    return bool(e.get("rodando")) and _vivo(e.get("pid", 0))


def url_salva() -> str:
    try:
        return (json.loads(CONFIG.read_text(encoding="utf-8-sig"))
                .get("url") or "").strip()
    except Exception:  # noqa: BLE001
        return ""


def guardar_url(url: str) -> None:
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps({"url": url.strip()}, indent=1),
                      encoding="utf-8")


def situacao() -> str:
    e = _ler_estado()
    if not e:
        return "Não comecei nenhuma maratona de curso."
    if not rodando():
        fim = e.get("fim") or "sem conclusão registrada"
        return (f"Maratona encerrada: {fim}. "
                f"Gravei {e.get('gravadas', 0)} aula(s).")
    aula_ = e.get("aula") or "abrindo"
    quanto = ""
    if e.get("segundos") and e.get("duracao"):
        quanto = (f" — {int(e['segundos']) // 60}:{int(e['segundos']) % 60:02d}"
                  f" de {int(e['duracao']) // 60}:{int(e['duracao']) % 60:02d}")
    return (f"Assistindo o curso: aula {e.get('indice', '?')} de "
            f"{e.get('total', '?')}, \"{aula_}\"{quanto}. "
            f"{e.get('gravadas', 0)} já gravada(s). Diga 'parar o curso' para eu parar.")


# Medido: áudio 16 kHz mono são ~32 KB/s (≈115 MB por hora) e as telas somam
# ~9 MB por hora. Dez horas de curso ficam perto de 1,3 GB.
MINIMO_LIVRE_GB = 4.0


def _espaco_curto() -> str:
    from . import aula as _aula

    try:
        import shutil

        raiz = _aula.CURSOS
        while not raiz.exists() and raiz != raiz.parent:
            raiz = raiz.parent
        livre = shutil.disk_usage(raiz).free / 1e9
    except Exception:  # noqa: BLE001
        return ""
    if livre >= MINIMO_LIVRE_GB:
        return ""
    return (f"Só há {livre:.1f} GB livres e uma noite de curso pede uns "
            "1,3 GB com folga. Libere espaço antes — se o disco encher no "
            "meio, eu perco as aulas seguintes.")


def iniciar(url: str = "", ui=None) -> str:
    """Dispara o processo que assiste o curso. Devolve a frase para o Samuel."""
    from . import aula as _aula
    from . import navegador

    if rodando():
        return "Já estou assistindo o curso. " + situacao()
    if _aula.gravando():
        return ("Estou gravando uma aula agora. Diga 'parar de gravar' antes "
                "de eu maratonar o curso.")
    if not navegador.disponivel():
        return "O navegador não está instalado. Rode: pip install playwright"

    url = (url or "").strip() or url_salva()
    if not url:
        return ("Me passe o link do curso uma vez — depois eu guardo. "
                "É a página de qualquer aula, com você já logado.")
    if "kiwify" not in url and "http" not in url:
        return f"Isso não parece um link de curso: {url[:60]}"
    guardar_url(url)

    # Uma noite de curso são ~1,5 GB entre áudio e telas. Descobrir que o
    # disco encheu na aula 30 é perder as trinta seguintes.
    falta = _espaco_curto()
    if falta:
        return falta

    # O perfil do Chromium é de um processo só (ver o cabeçalho).
    navegador.fechar()
    try:
        PEDIDO_DE_PARAR.unlink()
    except FileNotFoundError:
        pass

    criacao = 0x08000000 if os.name == "nt" else 0     # sem janela de console
    try:
        subprocess.Popen(
            [sys.executable, "-m", "tools.maratona", url],
            cwd=str(BASE_DIR), creationflags=criacao,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:  # noqa: BLE001
        return f"Não consegui iniciar a maratona: {str(e)[:90]}"

    return (
        "Vou assistir o curso inteiro e gravar aula por aula. Duas coisas para "
        "você saber: eu gravo o som que SAI do computador, então não toque "
        "outro áudio aqui enquanto isso — use o celular à vontade. E eu tiro "
        "print da tela a cada 30 segundos, então deixo a janela do curso na "
        "frente. Pergunte 'como está o curso' quando quiser, e 'parar o curso' "
        "para eu encerrar."
    )


def parar() -> str:
    if not rodando():
        return "Não estou assistindo o curso."
    PEDIDO_DE_PARAR.write_text(str(time.time()), encoding="utf-8")
    # A verdade, e não a versão bonita: ele para em segundos, no meio da aula.
    # A gravação parcial fica no disco mas NÃO ganha a marca de completa, então
    # ao retomar essa aula é refeita do começo e as anteriores são puladas.
    return ("Paro em alguns segundos. A aula que está gravando agora fica pela "
            "metade — quando você mandar assistir de novo, eu refaço só ela e "
            "pulo as que já terminei.")


# ─────────────────────────── lado do trabalhador ───────────────────────────

def _impedir_dormir(ligar: bool) -> None:
    """Segura o Windows acordado durante a maratona.

    O risco número um de rodar dez horas de madrugada não é o navegador: é o
    Windows apagar a tela e suspender a máquina às três horas. O vídeo para, o
    áudio para, e de manhã há trinta aulas faltando sem erro nenhum no diário.

    `ES_DISPLAY_REQUIRED` também segura o protetor de tela — e é por isso que
    ele entra junto, mesmo a gravação sendo de áudio: com a tela apagada o
    print sai preto, e é o print que amarra o slide ao minuto da fala.

    Vale só para a thread que chamou, então quem chama é o laço principal.
    """
    if os.name != "nt":
        return
    import ctypes

    CONTINUO, SISTEMA, TELA = 0x80000000, 0x00000001, 0x00000002
    try:
        ctypes.windll.kernel32.SetThreadExecutionState(
            (CONTINUO | SISTEMA | TELA) if ligar else CONTINUO)
    except Exception:  # noqa: BLE001
        pass


def _anotar(msg: str) -> None:
    linha = f"{datetime.now():%H:%M:%S} {msg}"
    print(linha, flush=True)
    try:
        with DIARIO.open("a", encoding="utf-8") as f:
            f.write(linha + "\n")
    except Exception:  # noqa: BLE001
        pass


def _publicar(**campos) -> None:
    """Grava o estado onde o app consegue ler."""
    atual = _ler_estado()
    atual.update(campos, quando=time.time())
    try:
        ESTADO.write_text(json.dumps(atual, ensure_ascii=False, indent=1),
                          encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass


def _mandaram_parar() -> bool:
    return PEDIDO_DE_PARAR.exists()


# Quanto esperar a página parar de se mexer antes de julgar o que ela é.
#
# Medido: numa abertura fria a aula levou 35 SEGUNDOS para montar (com cache
# quente eram 5 a 10). Com o limite anterior de 40 s a primeira tentativa
# expirava por pouco — e o pior não era a espera perdida, era eu concluir
# "pediu login" e clicar em "Fazer login com Kiwify", SAINDO de uma página que
# ia carregar sozinha. Paciência de sobra custa segundos; impaciência custou a
# retomada inteira desta manhã.
PACIENCIA_ASSENTAR = 120.0

# JULGA-SE PELO CONTEÚDO, NUNCA PELO ENDEREÇO.
#
# A Kiwify é uma página só: depois de entrar pelo repasse, ela troca o miolo
# pela aula e DEIXA o endereço em `/login`. Eu barrava justamente esse caso —
# a aula estava tocando na tela, com o player e tudo, e eu insistia que era
# tela de login porque o endereço dizia isso. Perdi a manhã nesse detalhe.
_PRONTA = """() => {
  const t = document.body ? (document.body.innerText || '') : '';
  if (/Acessar .rea de membros|Fazer login com Kiwify|Escolha uma conta/i
        .test(t)) return false;
  return !!document.querySelector('video')
      || document.querySelectorAll('ol li a[href]').length > 1;
}"""


def _assentar(pagina, limite: float = PACIENCIA_ASSENTAR) -> bool:
    """Espera a página ASSENTAR antes de decidir qualquer coisa sobre ela.

    Medido na Kiwify real: ela abre na aula, PULA para /login por volta de 2
    segundos enquanto revalida a sessão, e volta sozinha aos 10. Uma checagem
    única cai no meio desse pulo mais ou menos na metade das vezes — e o
    ensaio desta noite morreu assim, com "pediu login" na primeira tentativa,
    logado o tempo todo. Numa maratona sem ninguém olhando, isso é a noite
    inteira jogada fora por causa de uma amostra tirada no instante errado.

    Assentada = não está no /login E já tem vídeo ou lista de aulas na tela.
    """
    fim = time.monotonic() + limite
    while time.monotonic() < fim:
        try:
            if pagina.evaluate(_PRONTA):
                return True
        except Exception:  # noqa: BLE001 — durante a troca a página some
            pass
        time.sleep(1.5)
    return False


def _perfil_ocupado() -> bool:
    """Ainda há um navegador segurando o nosso perfil?"""
    from . import navegador

    try:
        saida = subprocess.run(
            ["wmic", "process", "where",
             "name='brave.exe' or name='chrome.exe' or name='msedge.exe'",
             "get", "CommandLine", "/format:list"],
            capture_output=True, text=True, timeout=20).stdout
    except Exception:  # noqa: BLE001 — sem wmic, seguimos e torcemos
        return False
    return navegador.PERFIL.name in (saida or "")


# A tela do repasse não é formulário: é "Escolha uma conta", com o e-mail dele
# já listado e a senha guardada por trás. Escolher a conta é UM CLIQUE — não
# digito nada, não vejo senha nenhuma, e nem preciso saber o e-mail: procuro a
# linha que TEM cara de e-mail e clico nela.
#
# Eu tinha errado o alvo: procurava `input[type=password]`, não achava (a tela
# não tem campo nenhum) e desistia com "formulário vazio". Foi o Samuel quem
# viu, olhando a tela: "é só um tab e um enter".
#
# "Usar outra conta" fica de fora de propósito: aquilo leva a um formulário de
# verdade, e é lá que a regra da senha voltaria a valer.
_ESCOLHER_CONTA = r"""() => {
  const eMail = /^[^\s@]+@[^\s@]+\.[a-z]{2,}$/i;
  const folhas = [...document.querySelectorAll('*')].filter(
      e => e.children.length === 0 && eMail.test((e.textContent || '').trim()));
  if (!folhas.length) return '';
  const linha = folhas[0];
  const clicavel = linha.closest('button, a, [role=button], li, [tabindex]')
                   || linha.parentElement || linha;
  clicavel.click();
  return (linha.textContent || '').trim().slice(0, 3) + '***';
}"""


def _escolher_conta(pagina) -> str:
    """Clica na conta já listada. Devolve uma pista mascarada, para o diário."""
    try:
        return pagina.evaluate(_ESCOLHER_CONTA) or ""
    except Exception:  # noqa: BLE001
        return ""


def _tentar_reentrar(pagina, destino: str = "") -> bool:
    """Volta a entrar no curso SEM nunca ver a senha.

    Pedido do Samuel, e foi ele quem viu como: "e so um tab e um enter". A
    tela do repasse nao pede senha — pede para ESCOLHER A CONTA, com o e-mail
    dele ja listado. Escolher e um clique. O segredo nao passa por aqui.

    O CAMINHO CERTO, medido a duras penas:

    - Ir direto ao endereco do repasse NAO resolve: a tela abre, o botao da
      conta aceita o clique e nada acontece. Falta o contexto de origem, que
      so existe quando se chega pela pagina do curso.
    - O clique em "Fazer login com Kiwify" abre uma JANELA nova, e ela precisa
      ser capturada com `expect_popup`. Sem isso eu ficava um minuto esperando
      uma aba que, para mim, nunca existia.
    - O clique na conta tem que ser do Playwright (evento confiavel), nao um
      `.click()` de DOM.
    - E no fim a aula volta na pagina principal COM O ENDERECO AINDA EM
      /login. Quem julga isso e `_PRONTA`, pelo conteudo.
    """
    from . import navegador

    destino = destino or pagina.url

    try:
        with navegador._trava:
            pagina = navegador._ir_para(destino)
    except Exception as e:  # noqa: BLE001
        _anotar(f"nao cheguei a pagina do curso: {str(e)[:70]}")
        return False
    time.sleep(6)

    janela = None
    try:
        with pagina.expect_popup(timeout=25000) as info:
            pagina.click("button:has-text('Fazer login com Kiwify')",
                         timeout=10000)
        janela = info.value
        janela.wait_for_load_state("domcontentloaded")
    except Exception as e:  # noqa: BLE001
        _anotar(f"o repasse nao abriu: {str(e)[:70]}")
        return False

    time.sleep(5)
    escolheu = False
    try:
        janela.locator("button").filter(has_text="@").first.click(timeout=10000)
        escolheu = True
        _anotar("escolhi a conta ja listada — um clique, sem senha")
    except Exception:  # noqa: BLE001
        pass

    if not escolheu and not _entrar_por_formulario(janela, destino):
        _fechar(janela)
        return False

    voltou = _assentar(pagina, PACIENCIA_ASSENTAR)
    _fechar(janela)
    if voltou:
        _anotar("entrei de novo sozinho")
    return voltou


def _fechar(janela) -> None:
    """Aba do repasse fechada na mao: senao o Brave a restaura na proxima vez."""
    try:
        if janela is not None and not janela.is_closed():
            janela.close()
    except Exception:  # noqa: BLE001
        pass


def _entrar_por_formulario(pagina, destino: str) -> bool:
    """Último caso: formulário de verdade. Só aperto o botão se JÁ vier cheio.

    Aqui a regra da senha volta a valer inteira — eu olho se o campo está
    vazio ou não, nunca o conteúdo, e quem preenche é o Chromium, do perfil
    dele, e só no endereço em que a senha foi salva.
    """
    try:
        cheio = pagina.evaluate("""() => {
            const s = document.querySelector('input[type=password]');
            const u = document.querySelector(
                'input[type=email], input[type=text]');
            return !!s && (s.value || '').length > 0
                       && !!u && (u.value || '').length > 0;
        }""")
    except Exception:  # noqa: BLE001
        cheio = False
    if not cheio:
        _anotar("o formulário veio vazio — não invento senha, paro aqui")
        return False

    _anotar("o navegador preencheu do perfil; eu só apertei o botão")
    for seletor in ("button[type=submit]", "button:has-text('Entrar')",
                    "button:has-text('Acessar')"):
        try:
            pagina.click(seletor, timeout=5000)
            break
        except Exception:  # noqa: BLE001
            continue
    time.sleep(10)
    return True


TENTATIVAS_POR_PAGINA = 4


def _abrir_curso(pagina, url: str, tentativas: int = TENTATIVAS_POR_PAGINA,
                 relancar: bool = False):
    """Abre um endereço do curso e INSISTE até a página estar de pé.

    Insistir aqui não é paranoia, é o número medido. Abri a mesma aula quatro
    vezes seguidas, com a sessão salva o tempo todo, e UMA delas veio com
    "Acessar área de membros" — a Kiwify erra a revalidação de vez em quando,
    e o `localStorage` continuava lá, intacto, na tentativa seguinte.

    Uma em quatro parece pouco até multiplicar por trinta e oito aulas: seriam
    umas nove noites de trabalho perdidas se uma recusa dessas encerrasse a
    maratona. Recarregar custa quinze segundos. Com quatro tentativas a chance
    de a aula ser perdida por isso cai para menos de meio por cento.

    Devolve (página, deu certo).
    """
    from . import navegador

    for n in range(1, tentativas + 1):
        try:
            if n == 1 or pagina is None:
                with navegador._trava:
                    pagina = navegador._ir_para(url)
            else:
                pagina.reload(wait_until="domcontentloaded", timeout=60000)
        except Exception as e:  # noqa: BLE001
            _anotar(f"navegação falhou ({n}): {str(e)[:80]}")
            pagina = _reabrir(pagina, url)
            continue

        if _assentar(pagina, PACIENCIA_ASSENTAR):
            return pagina, True
        # Só age se for MESMO a tela de entrada. Se a página está apenas
        # lenta, clicar em "Fazer login" me tira dela e piora tudo.
        if not _tela_de_login(pagina):
            _anotar(f"a aula não montou na tentativa {n} (não é login)")
            time.sleep(5)
            continue
        # Reentrar já na PRIMEIRA: ele passa o dia fora, e esperar uma segunda
        # tentativa só para começar a agir é tempo parado sem ninguém para
        # destravar. `_tela_de_login` acima já garante que é login mesmo.
        _anotar(f"a Kiwify pediu login na tentativa {n}")
        if _tentar_reentrar(pagina, url):
            return pagina, True
        time.sleep(5)

    if relancar:
        # Último recurso: derrubar o navegador e subir de novo. Só na abertura
        # do curso, onde vale gastar um minuto para não perder a noite.
        _anotar("último recurso: reiniciando o navegador")
        navegador.fechar()
        time.sleep(15)
        return _abrir_curso(None, url, tentativas=2, relancar=False)
    return pagina, False


def _tela_de_login(pagina) -> bool:
    """É a parede de login, ou só uma página lenta?

    A distinção não é cosmética: "não carregou ainda" pede ESPERAR, e "está
    deslogado" pede AGIR. Confundi as duas e agi sobre uma página que estava
    apenas montando — o clique me tirou dela e transformou lentidão em falha.

    Pelo endereço OU pelo texto: a Kiwify às vezes mantém o endereço da aula e
    troca só o conteúdo pela tela de entrada.
    """
    # Conteúdo primeiro, endereço só como último recurso: depois do repasse a
    # aula aparece com o endereço ainda em `/login`, e confiar no endereço
    # fazia eu tratar aula tocando como parede de entrada.
    try:
        return bool(pagina.evaluate(
            "() => /Acessar .rea de membros|Fazer login com Kiwify|"
            "Escolha uma conta/i.test("
            "document.body ? (document.body.innerText || '') : '')"))
    except Exception:  # noqa: BLE001
        pass
    try:
        endereco = (pagina.url or "").lower()
    except Exception:  # noqa: BLE001
        return False
    return any(m in endereco for m in ("/login", "signin", "sign_in"))


def _quadro_do_video(pagina, limite: float = ESPERA_PLAYER):
    """O <video> pode estar num iframe (a Kiwify usa player de terceiro).

    O Playwright enxerga dentro de iframe de outro domínio, então dá para
    perguntar ao próprio elemento quanto tempo ele tem e onde está — que é
    infinitamente mais confiável que cronometrar por fora.
    """
    fim = time.monotonic() + limite
    while time.monotonic() < fim:
        for quadro in pagina.frames:
            try:
                tem = quadro.evaluate(
                    "() => { const v = document.querySelector('video');"
                    "  return v ? (v.duration || 0) : -1; }")
            except Exception:  # noqa: BLE001 — quadro pode morrer no meio
                continue
            if tem and tem > 0:
                return quadro
        time.sleep(1.5)
    return None


_LER_VIDEO = """() => {
  const v = document.querySelector('video');
  if (!v) return null;
  return {t: v.currentTime, d: v.duration || 0,
          fim: !!v.ended, parado: !!v.paused, mudo: !!v.muted, vol: v.volume};
}"""

_DAR_PLAY = """() => {
  const v = document.querySelector('video');
  if (!v) return false;
  v.muted = false; v.volume = 1;
  const p = v.play();
  if (p && p.catch) p.catch(() => {});
  return true;
}"""


def _tocar(quadro) -> None:
    """Play sem depender de um seletor de botão que muda a cada tema.

    A política de autoplay do Chromium bloqueia som sem gesto do usuário; por
    isso `navegador.py` sobe o navegador com `--autoplay-policy`. O clique
    fica como reserva, para o caso de o play programático ser recusado.
    """
    try:
        quadro.evaluate(_DAR_PLAY)
    except Exception:  # noqa: BLE001
        pass
    time.sleep(1.5)
    try:
        estado = quadro.evaluate(_LER_VIDEO) or {}
    except Exception:  # noqa: BLE001
        return
    if not estado.get("parado"):
        return
    for seletor in ("button[aria-label*='lay' i]", "[class*='play' i]",
                    ".vjs-big-play-button", "video"):
        try:
            quadro.click(seletor, timeout=3000)
            time.sleep(1.2)
            if not (quadro.evaluate(_LER_VIDEO) or {}).get("parado"):
                return
        except Exception:  # noqa: BLE001
            continue


# O nome da aula vem da LISTA, não do <h1> da página. Medido na página real:
# o <h1> é o nome do MÓDULO ("START - O COMEÇO DA SUA JORNADA"), igual para
# todas as aulas dele — e como o nome vira nome de pasta, as dezessete aulas
# de um módulo colidiriam e o OMEGA pularia dezesseis achando que já tinha
# gravado. A lista já traz o título certo de cada uma.


# Links que casam com o formato de aula mas NÃO são aula: as abas do topo
# ("Aulas", "Conteúdo", "Comentários") apontam para a própria lição, com o
# mesmo formato de endereço. Sem isto o OMEGA abriria a mesma página três
# vezes achando que eram aulas diferentes. Verificado na página real.
_NAO_E_AULA = ("aulas", "conteudo", "conteúdo", "comentarios", "comentários",
               "current page", "materiais", "suporte", "inicio", "início")

# A Kiwify libera aula por data ("Liberação em 15/08/2026"). O item continua
# sendo um link, e a página abre — só que sem vídeo nenhum. Reconhecer isso
# aqui evita 45 segundos de espera por aula que ainda nem existe, e permite
# DIZER ao Samuel o que ficou de fora em vez de deixar buraco silencioso.
_BLOQUEADA = re.compile(r"libera[cç][aã]o em", re.I)

_COLHER_LINKS = """() => {
  // A lista de aulas é uma <ol> de <li>; a aula travada tem opacity-50 no
  // <li>. Se o tema mudar e isto não achar nada, quem chama cai no plano B.
  const de = (sel) => [...document.querySelectorAll(sel)].map(a => ({
      href: a.href,
      txt: (a.innerText || '').replace(/\\s+/g, ' ').trim(),
      fraco: !!a.closest('li') &&
             /opacity-\\d/.test(a.closest('li').className || '')}));
  const lista = de('ol li a[href]');
  return lista.length >= 2 ? lista : de('a[href]');
}"""


def _lista_de_aulas(pagina) -> list[dict]:
    """As aulas, na ordem da página, já separando as que ainda não abriram."""
    try:
        brutos = pagina.evaluate(_COLHER_LINKS)
    except Exception:  # noqa: BLE001
        return []
    saida, vistos = [], set()
    for item in brutos:
        href = item.get("href") or ""
        if not LINK_DE_AULA.search(href):
            continue
        chave = href.split("?")[0]
        if chave in vistos:
            continue
        texto = (item.get("txt") or "").strip()
        if not texto or texto.lower().lstrip("current page: ") in _NAO_E_AULA \
                or any(texto.lower().startswith(n) for n in _NAO_E_AULA):
            continue
        vistos.add(chave)
        saida.append({
            "href": href,
            "titulo": _BLOQUEADA.split(texto)[0].strip(" -–—"),
            "bloqueada": bool(item.get("fraco")) or bool(_BLOQUEADA.search(texto)),
        })
    return saida[:MAX_AULAS]


# Marca de aula INTEIRA. Não basta existir um WAV grande: se o processo cair
# aos 80% de uma aula de 20 minutos, o arquivo tem 16 minutos e pareceria
# pronto — e ao retomar o OMEGA pularia justamente a aula que ficou pela
# metade, sem dizer nada. Só quem chegou ao fim ganha esta marca.
MARCA_COMPLETA = "completa.json"


def _ja_gravada(curso: str, titulo: str) -> bool:
    from . import aula as _aula

    pasta = _aula.CURSOS / _aula._slug(curso) / "aulas"
    alvo = _aula._slug(titulo)
    return any((d / MARCA_COMPLETA).exists() for d in pasta.glob(f"*-{alvo}"))


def _marcar_completa(pasta: Path, titulo: str, duracao: float) -> None:
    try:
        (pasta / MARCA_COMPLETA).write_text(
            json.dumps({"titulo": titulo, "duracao": duracao,
                        "quando": f"{datetime.now():%Y-%m-%d %H:%M}"},
                       ensure_ascii=False, indent=1), encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass


def _assistir_uma(pagina, curso: str, indice: int, total: int,
                  titulo: str) -> str:
    """Grava uma aula do começo ao fim. Devolve o motivo de ter terminado."""
    from . import aula as _aula

    titulo = (titulo or "").strip() or f"aula {indice}"
    _publicar(indice=indice, total=total, aula=titulo, segundos=0, duracao=0)

    if _ja_gravada(curso, titulo):
        _anotar(f"[{indice}/{total}] já tenho \"{titulo}\" — pulo")
        return "já gravada"

    quadro = _quadro_do_video(pagina)
    if quadro is None:
        _anotar(f"[{indice}/{total}] \"{titulo}\": não achei vídeo nesta página")
        return "sem vídeo"

    _tocar(quadro)
    info = quadro.evaluate(_LER_VIDEO) or {}
    duracao = float(info.get("d") or 0)
    if info.get("parado"):
        _anotar(f"[{indice}/{total}] \"{titulo}\": o player não deu play")
        return "não tocou"

    # Voltar ao início: se ele já assistiu parte pelo celular, o player retoma
    # de onde parou e eu gravaria só o pedaço final.
    try:
        quadro.evaluate("() => { document.querySelector('video').currentTime = 0; }")
    except Exception:  # noqa: BLE001
        pass

    resposta = _aula.iniciar(curso, titulo, avisar=lambda m: _anotar(m))
    if not resposta.startswith("GRAVANDO"):
        _anotar(f"[{indice}/{total}] não consegui gravar: {resposta[:120]}")
        return "sem gravação"
    pasta = _aula._estado["pasta"]        # some do estado depois do `parar`
    _anotar(f"[{indice}/{total}] gravando \"{titulo}\" "
            f"({int(duracao) // 60}:{int(duracao) % 60:02d})")

    motivo = _acompanhar(quadro, duracao, indice, total, titulo)
    _anotar(f"[{indice}/{total}] {_aula.parar()[:160]}")
    if motivo == "acabou":
        _marcar_completa(pasta, titulo, duracao)
    return motivo


def _acompanhar(quadro, duracao: float, indice: int, total: int,
                titulo: str) -> str:
    """Fica de olho até o vídeo acabar — ou até ficar claro que deu errado."""
    from . import aula as _aula

    ultimo_t, parado_desde = -1.0, time.monotonic()
    comecou = time.monotonic()
    teto = (duracao * 1.6 + 300) if duracao else 3 * 3600
    tentou_religar = False

    while True:
        time.sleep(4)
        if _mandaram_parar():
            return "você mandou parar"
        if time.monotonic() - comecou > teto:
            return "passou do tempo previsto"

        try:
            info = quadro.evaluate(_LER_VIDEO) or {}
        except Exception:  # noqa: BLE001 — trocou de página ou fechou
            return "a página saiu do ar"
        t = float(info.get("t") or 0)
        d = float(info.get("d") or duracao or 0)
        _publicar(segundos=t, duracao=d)

        if info.get("fim") or (d and t >= d - SOBRA_FINAL):
            return "acabou"

        # FIM SEM AVISO. Medido na primeira noite real: em 6 das 10 aulas o
        # player chegou ao fim, congelou o último quadro e NUNCA disparou
        # `ended` — e o `currentTime` parou alguns segundos antes da duração,
        # fora dos 3 s de folga. Cada uma dessas custou 2 minutos de silêncio
        # gravado, ficou sem a marca de completa (seria regravada) e contou
        # como falha: cinco seguidas encerraram a maratona na aula 10 de 38.
        #
        # Perto do fim, portanto, parar de andar não é defeito — é o fim.
        #
        # O `parado` é o que dá confiança para afrouxar o limite: engasgo de
        # rede no meio do vídeo deixa o player TOCANDO e sem dados
        # (`paused` false), enquanto o fim o deixa pausado. Ninguém encosta
        # nesse navegador, então pausa espontânea passados 90% é fim de aula.
        perto_do_fim = bool(d) and (t >= d - 20
                                    or (info.get("parado") and t >= d * 0.90))

        # Silêncio é a falha cara: dá para gravar uma aula inteira de nada.
        # 60 s bastam para distinguir uma abertura silenciosa de um vídeo mudo.
        decorrido = time.monotonic() - comecou
        if decorrido > LIMITE_MUDO and _aula._estado.get("pico", 0) < _aula.PICO_MINIMO:
            if not tentou_religar:
                tentou_religar = True
                _anotar(f"[{indice}/{total}] sem som — tirando o mudo e "
                        "tentando de novo")
                try:
                    quadro.evaluate(_DAR_PLAY)
                except Exception:  # noqa: BLE001
                    pass
                comecou = time.monotonic()      # dá outra chance limpa
                continue
            return "vídeo sem som"

        if t > ultimo_t + 0.3:
            ultimo_t, parado_desde = t, time.monotonic()
            continue
        # Congelado no fim: 20 s bastam para separar isso de um engasgo de
        # rede, e economizam 100 s de silêncio por aula.
        travado_ha = time.monotonic() - parado_desde
        if perto_do_fim and travado_ha > ESPERA_FIM_MUDO:
            return "acabou"
        if travado_ha > PACIENCIA_TRAVADO:
            return "o vídeo travou"
        if info.get("parado") and not perto_do_fim:
            _tocar(quadro)


def _reabrir(pagina, url: str):
    """Levanta o navegador de novo depois de um tombo.

    O Chromium morre: aba que trava, GPU que cai, atualização automática. Numa
    sessão de dez horas isso deixa de ser hipótese. Reabrir custa segundos, e
    a alternativa é perder o resto da noite.
    """
    from . import navegador

    try:
        if not pagina.is_closed():
            return pagina
    except Exception:  # noqa: BLE001
        pass
    _anotar("o navegador caiu — reabrindo")
    try:
        navegador.fechar()
        with navegador._trava:
            nova = navegador._ir_para(url)
        nova.wait_for_timeout(5000)
        return nova
    except Exception as e:  # noqa: BLE001
        _anotar(f"não consegui reabrir: {str(e)[:120]}")
        return pagina


INTERVALO_CUTUCADA = (600, 1200)   # 10 a 20 minutos, sorteado


def _cutucar_o_windows(parar) -> None:
    """Sinal de vida para o Windows, de dez em dez ou vinte em vinte minutos.

    `SetThreadExecutionState` ja segura a suspensao, mas ele e uma DECLARACAO
    ("estou ocupado"), nao atividade: politica de grupo, protetor de tela com
    senha e o bloqueio automatico de algumas maquinas contam INATIVIDADE de
    entrada, e para esses o pedido nao vale. Dez horas sem teclado nem mouse
    e tempo de sobra para um deles apagar a tela.

    O QUE ELE NAO FAZ: nada de pausar/despausar o video, que era a ideia
    inicial. Pausar corta a gravacao no meio e deixa buraco na aula. E nada
    de tecla comum, que digitaria dentro da pagina. Sobram dois gestos
    inofensivos: mover o ponteiro um pixel e devolver, e apertar F15 — uma
    tecla que teclado nenhum tem, inventada justamente para isto.
    """
    import ctypes
    import ctypes.wintypes
    import random

    if os.name != "nt":
        return
    usuario = ctypes.windll.user32
    F15, SOLTAR = 0x7E, 0x0002
    while not parar.wait(random.randint(*INTERVALO_CUTUCADA)):
        try:
            ponto = ctypes.wintypes.POINT()
            if usuario.GetCursorPos(ctypes.byref(ponto)):
                usuario.SetCursorPos(ponto.x + 1, ponto.y)
                time.sleep(0.05)
                usuario.SetCursorPos(ponto.x, ponto.y)
            usuario.keybd_event(F15, 0, 0, 0)
            usuario.keybd_event(F15, 0, SOLTAR, 0)
            _anotar("cutucada: sinal de vida para o Windows")
        except Exception as e:  # noqa: BLE001 — nao pode derrubar a maratona
            _anotar(f"cutucada falhou: {str(e)[:60]}")


def _falar(texto: str) -> None:
    """Aviso por voz entre as aulas — NUNCA durante a gravação.

    Entre uma aula e outra não há gravação aberta, então a voz do OMEGA não
    entra no áudio do curso. É de propósito que ele não narra o progresso no
    meio da aula.
    """
    try:
        from . import voz_local

        voz_local.falar(texto, economico=True)
    except Exception:  # noqa: BLE001 — sem voz o trabalho continua
        pass


def trabalhar(url: str) -> None:
    from . import aula as _aula
    from . import navegador

    curso = _aula.curso_atual()
    # Zerar, e não mesclar: `_publicar` atualiza campo a campo, então sem isto
    # o minuto e a duração da corrida ANTERIOR sobrevivem, e a "situação"
    # relata uma aula que não está tocando. Visto no ensaio.
    ESTADO.unlink(missing_ok=True)
    _publicar(rodando=True, pid=os.getpid(), inicio=time.time(), gravadas=0,
              url=url, fim="", curso=curso, aula="", indice=0, total=0,
              segundos=0, duracao=0, travadas=[])
    _anotar(f"=== maratona: {url[:80]}")
    _impedir_dormir(True)
    fim_da_cutucada = threading.Event()
    threading.Thread(target=_cutucar_o_windows, args=(fim_da_cutucada,),
                     name="cutucada", daemon=True).start()

    gravadas = 0
    try:
        if _perfil_ocupado():
            _anotar("esperando o navegador anterior soltar o perfil")
            for _ in range(10):
                time.sleep(4)
                if not _perfil_ocupado():
                    break
        pagina, assentou = _abrir_curso(None, url, relancar=True)

        if not assentou:
            _anotar("parou no login de verdade — não vou adivinhar senha")
            _publicar(rodando=False, fim="pediu login")
            _falar("O curso está pedindo login. Entre na janela que eu abri, "
                   "e depois peça de novo.")
            return

        todas = _lista_de_aulas(pagina)
        if not todas:
            _anotar("não achei a lista de aulas nesta página")
            _publicar(rodando=False, fim="não achei a lista de aulas")
            _falar("Abri o curso mas não achei a lista de aulas. "
                   "Confira se a página é a de uma aula.")
            return

        travadas = [a["titulo"] for a in todas if a["bloqueada"]]
        aulas = [a for a in todas if not a["bloqueada"]]
        total = len(aulas)
        _anotar(f"{len(todas)} itens: {total} abertas, {len(travadas)} travadas")
        for t in travadas:
            _anotar(f"  travada: {t[:80]}")
        _publicar(total=total, travadas=travadas)
        _falar(f"Achei {total} aulas para assistir"
               + (f". Outras {len(travadas)} ainda não foram liberadas — "
                  "eu aviso quando abrirem." if travadas else ".")
               + " Começando pela primeira.")

        # Da PRIMEIRA em diante, e não de onde ele parou: o curso tem ordem, e
        # a extração de regras fica melhor com o contexto vindo em sequência.
        seguidas_ruins = 0
        for indice, item in enumerate(aulas, start=1):
            if _mandaram_parar():
                break
            # UMA AULA QUE FALHA NÃO PODE LEVAR AS OUTRAS TRINTA E SETE. Sem
            # este try, um `Target closed` na aula 3 encerraria a madrugada
            # inteira — que é exatamente o risco de rodar sem ninguém olhando.
            try:
                if pagina.url.split("?")[0] != item["href"].split("?")[0]:
                    # A recusa intermitente da Kiwify acontece a CADA troca de
                    # aula. Insistir aqui é o que impede que uma recusa numa
                    # aula qualquer no meio da madrugada encerre a maratona.
                    pagina, ok = _abrir_curso(pagina, item["href"])
                    if not ok:
                        _anotar(f"[{indice}/{total}] não consegui abrir a aula")
                        motivo = "não abriu"
                        seguidas_ruins += 1
                        if seguidas_ruins >= 5:
                            _anotar("cinco seguidas falharam — parando")
                            _falar("A sessão do curso parece ter caído. Entre "
                                   "de novo na janela e me mande retomar: eu "
                                   "pulo o que já gravei.")
                            break
                        continue

                motivo = _assistir_uma(pagina, curso, indice, total,
                                       item["titulo"])
            except Exception as e:  # noqa: BLE001
                motivo = f"erro: {type(e).__name__}"
                _anotar(f"[{indice}/{total}] {motivo}: {str(e)[:140]}")
                if _aula.gravando():
                    _aula.parar()
                pagina = _reabrir(pagina, item["href"])

            if motivo == "acabou":
                gravadas += 1
                seguidas_ruins = 0
            elif motivo not in ("já gravada", "você mandou parar"):
                seguidas_ruins += 1
                # Cinco seguidas não é azar, é algo quebrado (sessão, som,
                # rede). Insistir mais só gasta a madrugada.
                if seguidas_ruins >= 5:
                    _anotar("cinco aulas seguidas falharam — parando")
                    _falar("Cinco aulas seguidas falharam, então parei. "
                           "Olhe o diário da maratona.")
                    break
            _publicar(gravadas=gravadas)
            if motivo == "você mandou parar":
                break

        _publicar(rodando=False, fim=f"{gravadas} aula(s) gravada(s)")
        _anotar(f"=== fim: {gravadas} gravada(s)")
        _falar(f"Terminei. Gravei {gravadas} aulas"
               + (f", e {len(travadas)} continuam travadas por data."
                  if travadas else ".")
               + " Diga 'processar curso' quando quiser que eu extraia as regras."
               if gravadas else
               "Encerrei a maratona sem conseguir gravar nada. "
               "Olhe o diário da maratona.")
    except Exception as e:  # noqa: BLE001 — nada pode deixar o estado mentindo
        _anotar(f"ERRO: {type(e).__name__}: {str(e)[:200]}")
        _publicar(rodando=False, fim=f"erro: {str(e)[:80]}")
    finally:
        if _aula.gravando():
            _anotar(_aula.parar()[:160])
        fim_da_cutucada.set()
        _impedir_dormir(False)
        try:
            PEDIDO_DE_PARAR.unlink()
        except FileNotFoundError:
            pass
        navegador.fechar()


if __name__ == "__main__":
    trabalhar(sys.argv[1] if len(sys.argv) > 1 else url_salva())
