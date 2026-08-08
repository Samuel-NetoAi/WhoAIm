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
_parar = threading.Event()
# Contador, não booleano: a leitura de um documento e um aviso de render podem
# se sobrepor, e um `retomar()` cedo demais deixaria a voz do OMEGA entrar na
# gravação da aula.
_silenciado = 0


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


def _dispositivo_do_pc() -> tuple[int, int, int] | None:
    """(índice, taxa, canais) da entrada que ouve o que TOCA no PC.

    Procura a Mixagem estéreo pelo nome, em português e em inglês — o mesmo
    driver Realtek aparece com rótulo traduzido conforme o idioma do Windows.
    """
    for i, d in enumerate(sd.query_devices()):
        if d["max_input_channels"] <= 0:
            continue
        if _e_mixagem(d["name"]):
            return i, int(d["default_samplerate"]), min(2, d["max_input_channels"])
    return None


def _callback(indata, frames, tempo, status):
    if _silenciado:
        # A voz do OMEGA está saindo pelos alto-falantes. Descartar é melhor
        # que gravar: um trecho faltando na aula é recuperável ouvindo de
        # novo; a voz dele no meio contamina a extração de regras.
        return
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

    # Dito ANTES de gravar: descobrir no fim que era o dispositivo errado
    # custa a aula inteira.
    aviso_saida = _saida_incompativel()
    aviso_saida = (aviso_saida + " ") if aviso_saida else ""

    achado = _dispositivo_do_pc()
    if achado is None:
        return (
            "Não achei a Mixagem estéreo nesta máquina. Ative em: botão direito "
            "no ícone de som, Configurações de som, Mais opções, aba Gravação, "
            "botão direito na área vazia, Mostrar dispositivos desativados, "
            "e habilite a Mixagem estéreo."
        )
    indice, taxa, canais = achado

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
                    "taxa": taxa, "canais": canais, "curso": curso})
    _recentes.clear()
    _parar.clear()
    _wav = arquivo

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

    return (aviso_saida + f"Gravando {titulo}. Estou ouvindo o som do computador e tirando "
            "print da tela de meio em meio minuto. Pode perguntar 'o que ele "
            "acabou de dizer' quando quiser. Diga 'parar aula' no fim.")


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
    _estado.update({"gravando": False, "pasta": None, "titulo": ""})
    _recentes.clear()

    if duracao < 5:
        # Nada de útil: avisar em vez de deixar uma pasta vazia acumulando.
        return (f"Parei, mas só gravei {duracao:.0f} segundos de áudio. "
                "Confira se o som estava tocando pelos alto-falantes.")

    minutos = int(duracao // 60)
    return (f"Aula {titulo} gravada: {minutos} minuto(s) de áudio e {prints} "
            f"prints. Diga 'processar curso' quando quiser que eu transcreva e "
            f"tire as regras — leva mais ou menos {int(minutos / 1.7)} minutos.")


def situacao() -> str:
    if not _estado["gravando"]:
        return "Nenhuma aula sendo gravada."
    passados = int(time.monotonic() - _estado["inicio"])
    return (f"Gravando {_estado['titulo']} há {passados // 60}:{passados % 60:02d}, "
            f"{_estado['prints']} prints.")
