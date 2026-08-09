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
    return ("Encerro depois da aula que está gravando agora — cortar no meio "
            "deixaria uma gravação pela metade.")


# ─────────────────────────── lado do trabalhador ───────────────────────────

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


_TITULO = """() => {
  for (const s of ['h1', '[class*=lesson] h2', 'h2',
                   '[class*=titulo]', '[class*=title]']) {
    const e = document.querySelector(s);
    const t = e && (e.innerText || '').trim();
    if (t && t.length > 2 && t.length < 120) return t;
  }
  return (document.title || '').split('|')[0].trim();
}"""


def _lista_de_aulas(pagina) -> list[str]:
    """Os links das aulas, na ordem em que aparecem na página."""
    try:
        brutos = pagina.evaluate(
            "() => [...document.querySelectorAll('a[href]')].map(a => a.href)")
    except Exception:  # noqa: BLE001
        return []
    saida, vistos = [], set()
    for h in brutos:
        if not LINK_DE_AULA.search(h or ""):
            continue
        chave = h.split("?")[0]
        if chave in vistos:
            continue
        vistos.add(chave)
        saida.append(h)
    return saida[:MAX_AULAS]


def _proxima_pelo_botao(pagina) -> bool:
    """Reserva para quando a lista não é feita de links (SPA sem <a>).

    Preferimos os links: o botão de avançar às vezes é "concluir e avançar",
    e marcar a aula como assistida é decisão do Samuel, não minha.
    """
    for seletor in ("a:has-text('Próxima')", "button:has-text('Próxima')",
                    "a:has-text('Proxima')", "button:has-text('Avançar')",
                    "[class*=next]"):
        try:
            antes = pagina.url
            pagina.click(seletor, timeout=4000)
            pagina.wait_for_timeout(3000)
            if pagina.url != antes:
                return True
        except Exception:  # noqa: BLE001
            continue
    return False


def _ja_gravada(curso: str, titulo: str) -> bool:
    from . import aula as _aula

    pasta = _aula.CURSOS / _aula._slug(curso) / "aulas"
    alvo = _aula._slug(titulo)
    for d in pasta.glob(f"*-{alvo}"):
        wav = d / "audio.wav"
        if wav.exists() and wav.stat().st_size > 200_000:   # ~6 s de áudio
            return True
    return False


def _assistir_uma(pagina, curso: str, indice: int, total: int) -> str:
    """Grava uma aula do começo ao fim. Devolve o motivo de ter terminado."""
    from . import aula as _aula

    titulo = "aula"
    try:
        titulo = pagina.evaluate(_TITULO) or f"aula {indice}"
    except Exception:  # noqa: BLE001
        titulo = f"aula {indice}"
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
    _anotar(f"[{indice}/{total}] gravando \"{titulo}\" "
            f"({int(duracao) // 60}:{int(duracao) % 60:02d})")

    motivo = _acompanhar(quadro, duracao, indice, total, titulo)
    _anotar(f"[{indice}/{total}] {_aula.parar()[:160]}")
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
        if time.monotonic() - parado_desde > PACIENCIA_TRAVADO:
            return "o vídeo travou"
        if info.get("parado"):
            _tocar(quadro)


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
    _publicar(rodando=True, pid=os.getpid(), inicio=time.time(),
              gravadas=0, url=url, fim="", curso=curso)
    _anotar(f"=== maratona: {url[:80]}")

    gravadas = 0
    try:
        with navegador._trava:
            pagina = navegador._ir_para(url)
        pagina.wait_for_timeout(5000)

        if navegador._parece_tela_de_login(pagina):
            _publicar(rodando=False, fim="pediu login")
            _falar("O curso está pedindo login. Entre na janela que eu abri, "
                   "e depois peça de novo.")
            return

        aulas = _lista_de_aulas(pagina)
        if url.split("?")[0] not in [a.split("?")[0] for a in aulas]:
            aulas.insert(0, url)
        total = len(aulas) or 1
        _anotar(f"achei {len(aulas)} aula(s)")
        _publicar(total=total)
        _falar(f"Achei {total} aulas. Começando." if len(aulas) > 1
               else "Vou gravar esta aula e seguir pelas próximas.")

        indice = 0
        visitadas: set[str] = set()
        while indice < MAX_AULAS:
            if _mandaram_parar():
                break
            atual = pagina.url.split("?")[0]
            if atual in visitadas:
                _anotar("voltei numa aula que já vi — encerrando")
                break
            visitadas.add(atual)
            indice += 1

            motivo = _assistir_uma(pagina, curso, indice, max(total, indice))
            if motivo == "acabou":
                gravadas += 1
            _publicar(gravadas=gravadas)
            if motivo == "você mandou parar":
                break

            proxima = next((a for a in aulas
                            if a.split("?")[0] not in visitadas), "")
            if proxima:
                with navegador._trava:
                    pagina = navegador._ir_para(proxima)
                pagina.wait_for_timeout(4000)
            elif not _proxima_pelo_botao(pagina):
                _anotar("não há próxima aula — terminei")
                break

        _publicar(rodando=False, fim=f"{gravadas} aula(s) gravada(s)")
        _anotar(f"=== fim: {gravadas} gravada(s)")
        _falar(f"Terminei o curso. Gravei {gravadas} aulas. "
               "Diga 'processar curso' quando quiser que eu extraia as regras."
               if gravadas else
               "Encerrei a maratona sem conseguir gravar nada. "
               "Olhe o diário da maratona.")
    except Exception as e:  # noqa: BLE001 — nada pode deixar o estado mentindo
        _anotar(f"ERRO: {type(e).__name__}: {str(e)[:200]}")
        _publicar(rodando=False, fim=f"erro: {str(e)[:80]}")
    finally:
        if _aula.gravando():
            _anotar(_aula.parar()[:160])
        try:
            PEDIDO_DE_PARAR.unlink()
        except FileNotFoundError:
            pass
        navegador.fechar()


if __name__ == "__main__":
    trabalhar(sys.argv[1] if len(sys.argv) > 1 else url_salva())
