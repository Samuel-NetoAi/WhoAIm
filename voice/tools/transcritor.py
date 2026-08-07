"""Reconhecimento de fala do OMEGA com Whisper local (faster-whisper).

Substitui o Vosk, que errava demais em português: "Ômega" virava "amiga",
"IT A Coisa" virava "haiti é coisa" / "e tinha coice" / "e a colonizar".
Nenhuma camada de correção conserta transcrição desse nível — o motor tinha
que mudar.

Diferença estrutural: o Vosk é contínuo (entrega texto enquanto se fala) e o
Whisper é por trecho (precisa da frase inteira). Por isso aqui há um detector
de fala por energia: acumula áudio enquanto há voz e transcreve quando cai o
silêncio. É também o que permite ler frases longas sem cortar no meio.

Roda na GPU (RTX 3050) quando dá — ~0,05 s por frase contra ~1,6 s na CPU.
As DLLs de CUDA vêm dos pacotes pip da NVIDIA e precisam entrar no PATH
ANTES do ctranslate2 carregar, senão ele reclama de `cublas64_12.dll`.
"""

from __future__ import annotations

import os
import sys
import wave
from pathlib import Path

import numpy as np

TAXA = 16000  # o Whisper trabalha em 16 kHz

# --- silêncio e fala -------------------------------------------------------
# Calibrados para microfone de mesa em ambiente doméstico. Se ele começar a
# cortar no meio da frase, aumente SILENCIO_FIM; se disparar sozinho com
# ruído, suba LIMIAR_VOZ.
LIMIAR_VOZ = 380.0        # RMS acima disso conta como fala
SILENCIO_FIM = 0.8        # segundos de silêncio que encerram a frase
MINIMO_FALA = 0.35        # frases mais curtas que isso são ruído
MAXIMO_FALA = 25.0        # trava de segurança contra ruído contínuo

_modelo = {"obj": None, "dispositivo": None}


def _preparar_cuda() -> None:
    """Põe as DLLs da NVIDIA no caminho de busca do Windows."""
    base = Path(sys.prefix) / "Lib" / "site-packages" / "nvidia"
    dirs = [str(base / s / "bin") for s in ("cublas", "cudnn")
            if (base / s / "bin").exists()]
    if not dirs:
        return
    os.environ["PATH"] = os.pathsep.join(dirs) + os.pathsep + os.environ.get("PATH", "")
    for d in dirs:
        try:
            os.add_dll_directory(d)
        except OSError:
            pass


def carregar(tamanho: str = "small") -> tuple[object, str]:
    """Carrega o modelo uma vez. Devolve (modelo, 'cuda'|'cpu')."""
    if _modelo["obj"] is not None:
        return _modelo["obj"], _modelo["dispositivo"]

    _preparar_cuda()
    from faster_whisper import WhisperModel

    try:
        obj = WhisperModel(tamanho, device="cuda", compute_type="float16")
        # Carregar não basta: o ctranslate2 só procura o cuBLAS na primeira
        # inferência. Fazemos uma de mentira para descobrir agora, e não no
        # meio de um comando falado.
        obj.transcribe(np.zeros(TAXA // 2, dtype=np.float32), language="pt")
        dispositivo = "cuda"
    except Exception:  # noqa: BLE001 — sem GPU utilizável, a CPU resolve
        obj = WhisperModel(tamanho, device="cpu", compute_type="int8")
        dispositivo = "cpu"

    _modelo.update({"obj": obj, "dispositivo": dispositivo})
    return obj, dispositivo


def transcrever(audio_int16: bytes) -> str:
    """Transcreve um trecho de áudio PCM 16 bits mono a 16 kHz."""
    modelo, _ = carregar()
    amostras = np.frombuffer(audio_int16, dtype=np.int16).astype(np.float32) / 32768.0
    if amostras.size < TAXA * MINIMO_FALA:
        return ""
    segmentos, _info = modelo.transcribe(
        amostras,
        language="pt",
        beam_size=5,
        # O Whisper "alucina" frases prontas em trechos de silêncio; estes
        # dois freios cortam a maior parte disso.
        condition_on_previous_text=False,
        vad_filter=True,
    )
    return " ".join(s.text for s in segmentos).strip()


def energia(bloco: bytes) -> float:
    """RMS do bloco — é o que distingue fala de silêncio."""
    if not bloco:
        return 0.0
    amostras = np.frombuffer(bloco, dtype=np.int16).astype(np.float32)
    if amostras.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(amostras * amostras)))


class DetectorDeFala:
    """Junta blocos de áudio numa frase e avisa quando ela termina.

    Sem isto o Whisper receberia pedaços soltos (ele não é contínuo como o
    Vosk) e transcreveria metade de palavra.
    """

    def __init__(self, taxa: int = TAXA):
        self.taxa = taxa
        self._buffer = bytearray()
        self._falando = False
        self._silencio = 0.0
        self._duracao = 0.0

    def alimentar(self, bloco: bytes) -> bytes | None:
        """Devolve o áudio da frase quando ela acaba; senão None."""
        segundos = len(bloco) / 2 / self.taxa
        if energia(bloco) >= LIMIAR_VOZ:
            self._falando = True
            self._silencio = 0.0
            self._buffer.extend(bloco)
            self._duracao += segundos
        elif self._falando:
            # Guarda o silêncio curto: é a pausa natural entre palavras.
            self._buffer.extend(bloco)
            self._silencio += segundos
            self._duracao += segundos

        estourou = self._duracao >= MAXIMO_FALA
        if self._falando and (self._silencio >= SILENCIO_FIM or estourou):
            audio = bytes(self._buffer)
            self.limpar()
            util = len(audio) / 2 / self.taxa
            return audio if util >= MINIMO_FALA else None
        return None

    def limpar(self) -> None:
        self._buffer.clear()
        self._falando = False
        self._silencio = 0.0
        self._duracao = 0.0


def salvar_wav(audio_int16: bytes, caminho: Path, taxa: int = TAXA) -> None:
    """Grava um trecho — usado nos testes e para depurar transcrição ruim."""
    with wave.open(str(caminho), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(taxa)
        w.writeframes(audio_int16)
