"""Camada de reconhecimento de fala — só empresta o relógio ao alinhador.

Backend atual: **Vosk offline pt-BR**, escolhido porque já está instalado nas
duas máquinas (o motor gratuito do Alpha usa o mesmo modelo em
`voice/models/pt-br`) e roda sem internet, sem GPU e sem custo. A qualidade da
transcrição é medíocre — e isso é tolerável por desenho: o alinhador só usa as
palavras que o ASR acertou.

Trocar por WhisperX/MFA depois é trocar esta função: a saída é uma lista de
`PalavraASR` e nada mais do sistema sabe de onde ela veio.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import wave
from pathlib import Path

from .alinhador import PalavraASR

RAIZ_ALPHA = Path(__file__).resolve().parents[2]
MODELO_PADRAO = RAIZ_ALPHA / "voice" / "models" / "pt-br"

TAXA_AMOSTRAGEM = 16000  # exigência do modelo Vosk


def _candidatos_ffmpeg(binario: str) -> list[Path]:
    """Onde procurar ffmpeg/ffprobe, do mais provável ao mais improvável.

    O Studio já carrega binários completos para as duas plataformas, então não
    exigimos instalação no sistema: no Windows tem `studio/bin/ffmpeg.exe`, e o
    compositor do Remotion traz o seu próprio para cada SO.
    """
    sufixo = ".exe" if sys.platform == "win32" else ""
    modulos = RAIZ_ALPHA / "studio" / "node_modules" / "@remotion"
    candidatos = [RAIZ_ALPHA / "studio" / "bin" / f"{binario}{sufixo}"]
    if modulos.is_dir():
        candidatos += sorted(modulos.glob(f"compositor-*/{binario}{sufixo}"))
    return candidatos


def resolver_ffmpeg(binario: str = "ffmpeg") -> str:
    do_sistema = shutil.which(binario)
    if do_sistema:
        return do_sistema
    for candidato in _candidatos_ffmpeg(binario):
        if candidato.is_file():
            return str(candidato)
    raise RuntimeError(
        f"Não encontrei o {binario}. Instale no sistema ou rode `npm install` "
        f"em {RAIZ_ALPHA / 'studio'} (o Remotion traz o binário embutido)."
    )


def duracao_segundos(audio: str | Path) -> float:
    saida = subprocess.run(
        [
            resolver_ffmpeg("ffprobe"), "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(audio),
        ],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return float(saida)


def converter_para_wav16k(entrada: str | Path, saida: str | Path) -> Path:
    """A narração chega em mp3; o Vosk exige WAV PCM 16 kHz mono."""
    subprocess.run(
        [
            resolver_ffmpeg(), "-y", "-i", str(entrada),
            "-ar", str(TAXA_AMOSTRAGEM), "-ac", "1", "-c:a", "pcm_s16le",
            str(saida),
        ],
        capture_output=True, check=True,
    )
    return Path(saida)


def transcrever(
    wav16k: str | Path, modelo: str | Path | None = None
) -> list[PalavraASR]:
    try:
        from vosk import KaldiRecognizer, Model, SetLogLevel
    except ImportError as erro:  # noqa: TRY003 — mensagem acionável vale mais
        raise RuntimeError(
            "vosk não está instalado. Use o venv do Alpha "
            "(voice/.venv) ou rode: pip install vosk"
        ) from erro

    caminho_modelo = Path(modelo or os.environ.get("ALPHA_VOSK_MODEL") or MODELO_PADRAO)
    if not caminho_modelo.is_dir():
        raise RuntimeError(
            f"Modelo Vosk pt-BR não encontrado em {caminho_modelo}. "
            "Baixe o vosk-model-small-pt e aponte com --modelo ou ALPHA_VOSK_MODEL."
        )

    SetLogLevel(-1)
    with wave.open(str(wav16k), "rb") as wf:
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2:
            raise RuntimeError("O WAV precisa ser mono PCM 16 bits.")

        reconhecedor = KaldiRecognizer(Model(str(caminho_modelo)), wf.getframerate())
        reconhecedor.SetWords(True)

        brutas: list[dict] = []
        while True:
            pedaco = wf.readframes(4000)
            if not pedaco:
                break
            if reconhecedor.AcceptWaveform(pedaco):
                brutas += json.loads(reconhecedor.Result()).get("result", [])
        brutas += json.loads(reconhecedor.FinalResult()).get("result", [])

    from .texto import normalizar

    return [
        PalavraASR(
            palavra=p["word"],
            chave=normalizar(p["word"]),
            t0=float(p["start"]),
            t1=float(p["end"]),
            conf=float(p.get("conf", 1.0)),
        )
        for p in brutas
        if normalizar(p["word"])
    ]
