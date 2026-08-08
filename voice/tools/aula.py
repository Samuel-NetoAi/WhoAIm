"""Grava a aula que está tocando no PC, para o OMEGA assistir junto.

O Samuel comprou um curso sobre o algoritmo do YouTube. Os vídeos não têm
transcrição e rodam no navegador — não há arquivo para processar. Então a
captura tem que ser do que SAI pelos alto-falantes.

COMO, e por que não do jeito óbvio:

- Não gravamos a TELA para obter o áudio. O som do PC sai direto pela
  "Mixagem estéreo" (verificado nesta máquina: captura e transcreve certo).
  Gravar vídeo para extrair áudio e jogar o vídeo fora custaria disco e CPU
  por nada.
- Mas a tela IMPORTA num curso desses: é onde aparecem os títulos de exemplo,
  as thumbnails e os gráficos de analytics. Por isso prints periódicos —
  imagens, não vídeo. Medido: 0,05 s por print, ~9 MB por hora de aula.
- Não transcrevemos ao vivo. Medido: transcrição roda a 1,0x (large-v3) ou
  1,7x (turbo) o tempo real, então acompanhar uma aula em tempo real é
  impossível. Gravar é quase de graça; o processamento pesado vem depois
  (tools/curso.py). O que fica ao vivo é só um buffer curto, para responder
  "o que ele acabou de dizer?".

A ARMADILHA QUE ESTE MÓDULO TRATA: a Mixagem estéreo captura TUDO que sai
pelos alto-falantes — inclusive a voz do próprio OMEGA. Sem pausar a captura
enquanto ele fala, a transcrição da aula viria salpicada das respostas dele, e
a extração de regras trataria isso como conteúdo do curso. Ver `pausar()`.
"""

from __future__ import annotations

import re
import threading
import time
import unicodedata
import wave
from collections import deque
from datetime import datetime
from pathlib import Path

import numpy as np
import sounddevice as sd

from .pipeline import AI_PROJECT_ROOT
from .transcritor import TAXA, para_16k_mono

CURSOS = AI_PROJECT_ROOT / "Cursos"

# Quanto do passado recente fica em memória para o "o que ele acabou de
# dizer?". 90 s cobre um raciocínio inteiro do professor sem virar um bloco
# grande demais para transcrever depressa.
JANELA_RECENTE = 90.0

INTERVALO_PRINT = 30.0     # segundos entre prints automáticos
LARGURA_PRINT = 960        # metade de 1080p: legível e leve
QUALIDADE_PRINT = 70

_estado: dict = {
    "gravando": False,
    "pasta": None,
    "titulo": "",
    "inicio": 0.0,
    "pausas": 0.0,
    "prints": 0,
}
_trava = threading.Lock()
_recentes: deque = deque()
_wav: wave.Wave_write | None = None
_stream = None
# Um evento POR SESSÃO, não global. Com um só, parar e começar outra aula
# deixava a thread de leitura antiga viva: ela via o evento ser limpo pelo
# novo `iniciar()` e voltava a escrever — duas threads no mesmo arquivo, com
# taxas diferentes. Cada gravação carrega o próprio sinal de parada.
_parar = threading.Event()
# Contador, não booleano: a leitura de um documento e um aviso de render podem
# se sobrepor, e um `retomar()` cedo demais deixaria a voz do OMEGA entrar na
# gravação da aula.
_silenciado = 0


def _segundos_de_aula() -> float:
    return time.monotonic() - _estado.get("inicio", time.monotonic())


def _sem_acento(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto)
                   if unicodedata.category(c) != "Mn")


def _slug(texto: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", _sem_acento(texto).lower()).strip("-") or "aula"


# Qual curso está em andamento. Fica em disco para sobreviver ao fechamento do
# app: ninguém quer dizer o nome do curso antes de cada aula.
_MARCADOR = CURSOS / ".curso-atual"
CURSO_PADRAO = "algoritmo-youtube"


def curso_atual() -> str:
    try:
        return _MARCADOR.read_text(encoding="utf-8").strip() or CURSO_PADRAO
    except Exception:  # noqa: BLE001
        return CURSO_PADRAO


def definir_curso(nome: str) -> str:
    nome = (nome or "").strip()
    if not nome:
        return f"O curso atual é {curso_atual()}."
    try:
        CURSOS.mkdir(parents=True, exist_ok=True)
        _MARCADOR.write_text(_slug(nome), encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        return f"Não consegui gravar: {str(e)[:60]}"
    return f"Curso atual: {nome}. As próximas aulas vão para lá."


def gravando() -> bool:
    return _estado["gravando"]


def pausar() -> None:
    """Para de gravar enquanto o OMEGA fala. Chamado pelos dois motores."""
    global _silenciado
    with _trava:
        _silenciado += 1


def retomar() -> None:
    global _silenciado
    with _trava:
        _silenciado = max(0, _silenciado - 1)


def _saida_incompativel() -> str | None:
    """Avisa quando o som NÃO vai sair por onde a Mixagem escuta.

    A Mixagem estéreo pertence a UMA placa (aqui, a Realtek). Se o som estiver
    saindo pelo HDMI do monitor ou por um fone USB, ela grava silêncio — e o
    Samuel só descobriria depois de assistir a aula inteira. Verificado nesta
    máquina: a saída pela NVIDIA não é capturada.
    """
    try:
        apis = sd.query_hostapis()
        i = next(n for n, a in enumerate(apis) if "WASAPI" in a["name"])
        saida = sd.query_devices(apis[i].get("default_output_device"))["name"]
    except Exception:  # noqa: BLE001
        return None
    for i, d in enumerate(sd.query_devices()):
        if d["max_input_channels"] > 0 and _e_mixagem(d["name"]):
            # Mesma fabricante no nome = mesma placa. Grosseiro, mas é o que
            # dá para saber sem descer ao WASAPI de verdade, e pega o caso
            # real (Realtek x NVIDIA).
            marca = d["name"].split("(")[-1].split(")")[0].split()[0].lower()
            if marca and marca not in saida.lower():
                return (f"Atenção: o som está saindo por '{saida}', e eu só "
                        f"escuto a mixagem da {marca.capitalize()}. Mude a "
                        "saída de áudio antes, ou eu vou gravar silêncio.")
            return None
    return None


def _e_mixagem(nome: str) -> bool:
    n = nome.lower()
    return "mixagem" in n or "stereo mix" in n or "what u hear" in n


# CAPTURA POR WASAPI LOOPBACK, e não mais pela Mixagem estéreo.
#
# A Mixagem funcionava, mas é frágil de três jeitos que já bateram aqui:
#  - pode estar DESABILITADA no Windows (aconteceu entre uma sessão e outra);
#  - pertence a UMA placa, então fone USB ou HDMI do monitor não é capturado;
#  - aparece uma vez por API de áudio, e escolher a errada (WDM-KS) dava
#    "Invalid device [-9996]" sem explicação.
#
# O loopback do WASAPI (via PyAudioWPatch) não tem nenhum desses problemas:
# ele grampeia a SAÍDA PADRÃO, seja ela qual for, sem depender de dispositivo
# habilitado. Testado: capturou e transcreveu com a Mixagem desligada.
#
# A Mixagem fica como reserva para máquina sem o pacote instalado.
_APIS_BOAS = ("MME", "WASAPI", "DirectSound")


def _loopback():
    """(pyaudio, info) da saída padrão grampeada. None se não der."""
    try:
        import pyaudiowpatch as pa
    except ImportError:
        return None, None
    try:
        audio = pa.PyAudio()
        return audio, audio.get_default_wasapi_loopback()
    except Exception:  # noqa: BLE001
        try:
            audio.terminate()
        except Exception:  # noqa: BLE001
            pass
        return None, None


def _dispositivo_do_pc() -> tuple[int, int, int] | None:
    """RESERVA: a Mixagem estéreo, quando o loopback não estiver disponível."""
    apis = [a["name"] for a in sd.query_hostapis()]
    achados: list[tuple[int, int, int, str]] = []
    for i, d in enumerate(sd.query_devices()):
        if d["max_input_channels"] <= 0 or not _e_mixagem(d["name"]):
            continue
        achados.append((i, int(d["default_samplerate"]),
                        min(2, d["max_input_channels"]), apis[d["hostapi"]]))
    for preferida in _APIS_BOAS:
        for i, taxa, canais, api in achados:
            if preferida in api:
                return i, taxa, canais
    return None


def _so_existe_no_wdm() -> bool:
    """A Mixagem está desabilitada no Windows? (só aparece no nível do driver)"""
    apis = [a["name"] for a in sd.query_hostapis()]
    vistas = {apis[d["hostapi"]] for d in sd.query_devices()
              if d["max_input_channels"] > 0 and _e_mixagem(d["name"])}
    return bool(vistas) and all("WDM-KS" in v for v in vistas)


def _ler_do_loopback(audio, info, parar: threading.Event,
                     pronto: threading.Event) -> None:
    """Thread que lê o loopback em blocos e alimenta o mesmo caminho de sempre.

    Leitura bloqueante em vez de callback: o PyAudio em modo callback tem as
    mesmas armadilhas do sounddevice, e aqui não há requisito de latência —
    é gravação, não conversa.
    """
    import pyaudiowpatch as pa

    taxa, canais = int(info["defaultSampleRate"]), info["maxInputChannels"]
    _estado.update({"taxa": taxa, "canais": canais})
    try:
        fluxo = audio.open(format=pa.paInt16, channels=canais, rate=taxa,
                           input=True, input_device_index=info["index"],
                           frames_per_buffer=int(taxa * 0.5))
    except Exception:  # noqa: BLE001
        pronto.set()
        return
    pronto.set()
    try:
        while not parar.is_set():
            try:
                bruto = fluxo.read(int(taxa * 0.5), exception_on_overflow=False)
            except Exception:  # noqa: BLE001 — dispositivo trocado no meio
                break
            _callback(bruto, 0, None, None)
    finally:
        try:
            fluxo.stop_stream()
            fluxo.close()
        except Exception:  # noqa: BLE001
            pass
        try:
            audio.terminate()
        except Exception:  # noqa: BLE001
            pass


def _callback(indata, frames, tempo, status):
    # NADA MAIS É DESCARTADO. A primeira versão jogava fora o áudio enquanto o
    # OMEGA falava, para não sujar a transcrição — e o preço apareceu no uso
    # real: numa aula de 25 minutos sobraram 16. Metade das perguntas do
    # Samuel custou um pedaço da aula, e ele não tinha como saber.
    #
    # Agora grava sempre e ANOTA o intervalo em que o OMEGA falou. A limpeza
    # acontece na transcrição, por timestamp, onde ela é reversível — se a
    # marcação errar, o áudio continua lá para conferir.
    if _silenciado and not _estado.get("mudo_desde"):
        _estado["mudo_desde"] = _segundos_de_aula()
    elif not _silenciado and _estado.get("mudo_desde"):
        _estado.setdefault("mudos", []).append(
            (_estado["mudo_desde"], _segundos_de_aula()))
        _estado["mudo_desde"] = None

    amostras = np.frombuffer(bytes(indata), dtype=np.int16).astype(np.float32)
    pcm = para_16k_mono(amostras, _estado["taxa"], _estado["canais"])
    if _wav is not None:
        try:
            _wav.writeframes(pcm)
        except Exception:  # noqa: BLE001 — disco cheio não pode matar o áudio
            pass
    # Nível acumulado: é como se descobre, em segundos, que a gravação está
    # muda — som no dispositivo errado, aba sem áudio, autoplay bloqueado pelo
    # Chrome. Sem isto o silêncio só apareceria no fim da aula.
    if pcm:
        amostras16 = np.frombuffer(pcm, dtype=np.int16).astype(np.float32)
        if amostras16.size:
            _estado["pico"] = max(_estado.get("pico", 0),
                                  int(np.abs(amostras16).max()))
    _recentes.append(pcm)
    # deque com maxlen não serve: os blocos têm tamanhos diferentes, então o
    # limite tem que ser em SEGUNDOS, não em número de blocos.
    total = sum(len(b) for b in _recentes) / 2 / TAXA
    while total > JANELA_RECENTE and len(_recentes) > 1:
        total -= len(_recentes.popleft()) / 2 / TAXA


# Abaixo disto não há som nenhum saindo pelos alto-falantes.
PICO_MINIMO = 150


def _vigiar_silencio(avisar) -> None:
    """Avisa UMA vez se os primeiros segundos vieram mudos."""
    if _parar.wait(12) or not _estado["gravando"]:
        return
    if _estado.get("pico", 0) < PICO_MINIMO:
        avisar(
            "SYS: não estou ouvindo nada há 12 segundos. Confira se o vídeo "
            "está tocando e se o som sai pelos alto-falantes — sigo gravando."
        )


def _laco_de_prints(pasta: Path) -> None:
    from PIL import ImageGrab

    while not _parar.wait(INTERVALO_PRINT):
        if _silenciado:
            # Só o PRINT é pulado: a tela nessa hora costuma ser a janela do
            # OMEGA, não a aula. O áudio continua sendo gravado.
            continue
        try:
            segundos = int(time.monotonic() - _estado["inicio"])
            imagem = ImageGrab.grab()
            largura = LARGURA_PRINT
            altura = int(imagem.height * largura / imagem.width)
            imagem.convert("RGB").resize((largura, altura)).save(
                pasta / f"{segundos:05d}.jpg", quality=QUALIDADE_PRINT)
            _estado["prints"] += 1
        except Exception:  # noqa: BLE001 — print é apoio, não pode derrubar
            pass


def iniciar(curso: str, titulo: str, avisar=None) -> str:
    """Começa a gravar a aula que está tocando."""
    global _wav, _stream
    if _estado["gravando"]:
        return f"Já estou gravando {_estado['titulo']}. Diga 'parar aula' antes."

    audio, info = _loopback()
    reserva = None if audio else _dispositivo_do_pc()
    if audio is None and reserva is None:
        desligada = _so_existe_no_wdm()
        return (
            "Não consigo ouvir o som do computador. "
            + ("A Mixagem estéreo está DESABILITADA no Windows e o loopback "
               "não está disponível. " if desligada else "")
            + "Rode `pip install PyAudioWPatch` — com ele eu gravo direto da "
            "saída de áudio, sem depender de dispositivo habilitado."
        )

    pasta = (CURSOS / _slug(curso) / "aulas" /
             f"{datetime.now():%Y%m%d-%H%M}-{_slug(titulo)}")
    try:
        (pasta / "telas").mkdir(parents=True, exist_ok=True)
        arquivo = wave.open(str(pasta / "audio.wav"), "wb")
        arquivo.setnchannels(1)
        arquivo.setsampwidth(2)
        arquivo.setframerate(TAXA)
    except Exception as e:  # noqa: BLE001
        return f"Não consegui preparar a pasta da aula: {str(e)[:80]}"

    _estado.update({"gravando": True, "pasta": pasta, "titulo": titulo,
                    "inicio": time.monotonic(), "prints": 0, "pico": 0,
                    "curso": curso, "mudos": [], "mudo_desde": None,
                    "por_onde": ""})
    _recentes.clear()
    _parar.clear()
    sessao = threading.Event()
    _estado["parar_sessao"] = sessao
    _wav = arquivo

    if audio is not None:
        _estado["por_onde"] = info["name"].split("[")[0].strip()
        # "GRAVANDO" tem que significar que JÁ está gravando. Abrir o fluxo
        # leva um instante, e responder antes disso faz o Samuel dar play e
        # perder os primeiros segundos da aula.
        pronto = threading.Event()
        threading.Thread(target=_ler_do_loopback,
                         args=(audio, info, sessao, pronto),
                         name="loopback-aula", daemon=True).start()
        pronto.wait(timeout=3)
    else:
        indice, taxa, canais = reserva
        _estado.update({"taxa": taxa, "canais": canais,
                        "por_onde": "Mixagem estéreo"})
        try:
            _stream = sd.RawInputStream(
                samplerate=taxa, channels=canais, dtype="int16",
                device=indice, blocksize=int(taxa * 0.5), callback=_callback)
            _stream.start()
        except Exception as e:  # noqa: BLE001
            _wav.close()
            _wav = None
            _estado["gravando"] = False
            return f"Não consegui abrir a captura do som do PC: {str(e)[:80]}"

    threading.Thread(target=_laco_de_prints, args=(pasta / "telas",),
                     name="prints-aula", daemon=True).start()
    if avisar:
        threading.Thread(target=_vigiar_silencio, args=(avisar,),
                         name="silencio-aula", daemon=True).start()
        # Pulso de vida. O Samuel parou a aula duas vezes só para perguntar se
        # ainda estava gravando — não havia nada na tela dizendo que sim, e
        # cada pausa dessas custava conteúdo. Agora ele avisa sozinho.
        threading.Thread(target=_pulso, args=(avisar,),
                         name="pulso-aula", daemon=True).start()

    return (f"GRAVANDO: {titulo}. Ouvindo por {_estado['por_onde']} e tirando "
            "print a cada 30 segundos. Vou avisar de dois em dois minutos que "
            "continuo gravando. Pergunte 'o que ele acabou de dizer' quando "
            "quiser; para encerrar, 'parar aula'.")


# De dois em dois minutos. Curto o bastante para ele não duvidar, longo o
# bastante para não virar ruído numa aula de uma hora.
INTERVALO_PULSO = 120.0


def _pulso(avisar) -> None:
    while not _parar.wait(INTERVALO_PULSO):
        if not _estado["gravando"]:
            return
        s = int(_segundos_de_aula())
        avisar(f"SYS: ● gravando {_estado['titulo']} — {s // 60}:{s % 60:02d}, "
               f"{_estado['prints']} telas.")


def print_agora(rotulo: str = "") -> str:
    """Print sob comando — para quando algo importante aparece na tela."""
    if not _estado["gravando"]:
        return "Não estou gravando aula nenhuma, senhor."
    from PIL import ImageGrab

    try:
        segundos = int(time.monotonic() - _estado["inicio"])
        marca = f"{segundos:05d}-{_slug(rotulo)}" if rotulo else f"{segundos:05d}-pedido"
        imagem = ImageGrab.grab()
        largura = LARGURA_PRINT
        altura = int(imagem.height * largura / imagem.width)
        imagem.convert("RGB").resize((largura, altura)).save(
            _estado["pasta"] / "telas" / f"{marca}.jpg", quality=QUALIDADE_PRINT)
        _estado["prints"] += 1
    except Exception as e:  # noqa: BLE001
        return f"Não consegui tirar o print: {str(e)[:60]}"
    return f"Guardei a tela em {segundos // 60}:{segundos % 60:02d} da aula."


def trecho_recente() -> bytes:
    """Os últimos ~90 s de áudio da aula, para transcrever sob demanda."""
    return b"".join(_recentes)


def parar() -> str:
    """Encerra a gravação e deixa a aula pronta para processar."""
    global _wav, _stream
    if not _estado["gravando"]:
        return "Não estou gravando nada, senhor."

    _parar.set()
    sessao = _estado.get("parar_sessao")
    if sessao is not None:
        sessao.set()
    # Dar à thread de leitura tempo de sair do `read()` antes de fechar o wav:
    # sem isso ela pode escrever num arquivo já fechado.
    time.sleep(0.6)
    try:
        if _stream is not None:
            _stream.stop()
            _stream.close()
    except Exception:  # noqa: BLE001
        pass
    _stream = None

    duracao = 0.0
    try:
        if _wav is not None:
            duracao = _wav.getnframes() / TAXA
            _wav.close()
    except Exception:  # noqa: BLE001
        pass
    _wav = None

    pasta = _estado["pasta"]
    titulo, prints = _estado["titulo"], _estado["prints"]

    # Os intervalos em que o OMEGA falou vão para disco junto do áudio: é o
    # que permite a transcrição descartar a voz dele SEM descartar a aula.
    if _estado.get("mudo_desde"):
        _estado.setdefault("mudos", []).append(
            (_estado["mudo_desde"], _segundos_de_aula()))
    try:
        import json

        (pasta / "falas-do-omega.json").write_text(
            json.dumps([[round(a, 1), round(b, 1)]
                        for a, b in _estado.get("mudos", [])]),
            encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass

    _estado.update({"gravando": False, "pasta": None, "titulo": "",
                    "mudos": [], "mudo_desde": None})
    _recentes.clear()

    if duracao < 5:
        # Nada de útil: avisar em vez de deixar uma pasta vazia acumulando.
        return (f"PAREI. Mas só gravei {duracao:.0f} segundos de áudio — "
                "confira se o som estava saindo pelos alto-falantes.")

    minutos = int(duracao // 60)
    # A confirmação precisa ser INEQUÍVOCA. O Samuel mandou parar quatro vezes
    # porque a resposta nunca dizia, com todas as letras, que tinha parado —
    # e ele não tinha como saber se a aula seguia gravando.
    return (f"PAREI DE GRAVAR. Aula '{titulo}': {minutos} minuto(s) de áudio, "
            f"{prints} telas, salvo em {pasta.name}. "
            "Diga 'processar curso' quando quiser as regras — leva menos de um "
            "minuto por hora de aula.")


def situacao() -> str:
    if not _estado["gravando"]:
        return "NÃO estou gravando aula nenhuma agora."
    passados = int(_segundos_de_aula())
    return (f"SIM, ainda gravando '{_estado['titulo']}' — "
            f"{passados // 60}:{passados % 60:02d} de aula, "
            f"{_estado['prints']} telas, por {_estado.get('por_onde', 'áudio do PC')}.")
