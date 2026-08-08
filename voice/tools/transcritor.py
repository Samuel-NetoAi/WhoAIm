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

# Silero VAD (embutido no faster-whisper). O detector de energia lá embaixo
# resolve QUANDO a frase acabou; isto resolve o que dentro dela é voz. Sem
# ele, porta batendo e ventilador entram no decoder como se fossem fala e o
# Whisper "alucina" palavras em cima de ruído.
VAD = {
    "threshold": 0.5,
    "min_speech_duration_ms": 200,
    "min_silence_duration_ms": 300,
    "speech_pad_ms": 200,
}

# MEDIDO nesta máquina (RTX 3050 8 GB, com o desktop normal do Samuel rodando
# — overlay da NVIDIA e WebView já ocupavam 3,4 GB e 98% da GPU), 8 frases
# reais, mediana, com o viés de vocabulário ligado:
#
#   large-v3        int8_float16   3,32 s/frase   acertou os 8 nomes
#   large-v3-turbo  int8_float16   0,94 s/frase   errou Orphanim e Dullhan
#   large-v3        float16        inviável (>40 s) — não cabe junto do desktop
#
# Escolhido o large-v3: o turbo é 3,5x mais rápido, mas erra exatamente os
# nomes que motivaram este trabalho, e `projetos.resolver` só recupera parte
# deles ("Orfanin" -> Orphanim sim; "Dulliano" -> ambíguo, "Umboso" -> nada).
# Precisão foi a queixa; latência tem outra saída, que é o motor Live.
#
# Quem tiver GPU mais folgada ou preferir velocidade troca no config
# (`whisper_modelo`) sem editar código.
MODELO_PADRAO = "large-v3"

# int8 não é economia de VRAM aqui — é o que torna o modelo grande VIÁVEL.
# Em float16 ele briga por memória com o resto do desktop e o tempo por frase
# passa de 40 s. Ver os números acima.
QUANTIZACAO = "int8_float16"

_modelo = {"obj": None, "dispositivo": None, "nome": None}


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


def _modelo_configurado() -> str:
    """O modelo pedido no config, ou o padrão."""
    try:
        import json

        cfg = json.loads(
            (Path(__file__).resolve().parent.parent / "config" / "api_keys.json")
            .read_text(encoding="utf-8")
        )
        return (cfg.get("whisper_modelo") or MODELO_PADRAO).strip()
    except Exception:  # noqa: BLE001 — config ausente não pode impedir de ouvir
        return MODELO_PADRAO


def carregar(tamanho: str | None = None) -> tuple[object, str]:
    """Carrega o modelo uma vez. Devolve (modelo, 'cuda'|'cpu')."""
    tamanho = tamanho or _modelo_configurado()
    if _modelo["obj"] is not None:
        return _modelo["obj"], _modelo["dispositivo"]

    _preparar_cuda()
    from faster_whisper import WhisperModel

    try:
        obj = WhisperModel(tamanho, device="cuda", compute_type=QUANTIZACAO)
        # Carregar não basta: o ctranslate2 só procura o cuBLAS na primeira
        # inferência. Fazemos uma de mentira para descobrir agora, e não no
        # meio de um comando falado.
        obj.transcribe(np.zeros(TAXA // 2, dtype=np.float32), language="pt")
        dispositivo = "cuda"
    except Exception:  # noqa: BLE001 — sem GPU utilizável, a CPU resolve
        # Na CPU o modelo grande é inviável (dezenas de segundos por frase):
        # ali a escolha certa é o menor que ainda serve, não o mais preciso.
        tamanho = "small" if tamanho.startswith("large") else tamanho
        obj = WhisperModel(tamanho, device="cpu", compute_type="int8")
        dispositivo = "cpu"

    _modelo.update({"obj": obj, "dispositivo": dispositivo, "nome": tamanho})
    return obj, dispositivo


def nome_do_modelo() -> str:
    return _modelo.get("nome") or _modelo_configurado()


def transcrever(audio_int16: bytes, viesar: bool = True) -> str:
    """Transcreve um trecho de áudio PCM 16 bits mono a 16 kHz.

    `viesar=False` desliga o viés de vocabulário — serve para MEDIR o efeito
    dele, que é a única forma honesta de saber se ajudou.
    """
    modelo, _ = carregar()
    amostras = np.frombuffer(audio_int16, dtype=np.int16).astype(np.float32) / 32768.0
    if amostras.size < TAXA * MINIMO_FALA:
        return ""

    # Contextual biasing: dizer ao decoder o que esperar ANTES de ele decidir.
    # Ver tools/contexto_fala.py para o porquê de isto vir antes da correção
    # por dicionário, e não depois.
    hotwords = prompt = None
    if viesar:
        try:
            from . import contexto_fala

            hotwords = contexto_fala.hotwords() or None
            prompt = contexto_fala.INITIAL_PROMPT
        except Exception:  # noqa: BLE001 — sem viés é pior, mas surdo é pior ainda
            pass

    segmentos, _info = modelo.transcribe(
        amostras,
        language="pt",
        beam_size=5,
        hotwords=hotwords,
        initial_prompt=prompt,
        # O Whisper "alucina" frases prontas em trechos de silêncio; estes
        # dois freios cortam a maior parte disso.
        condition_on_previous_text=False,
        vad_filter=True,
        vad_parameters=VAD,
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
