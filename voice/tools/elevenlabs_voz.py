"""Voz do OMEGA pela ElevenLabs, com queda automática para a voz do Windows.

Uso PRIVADO: só o Samuel escuta o OMEGA, então a camada gratuita serve (o
plano Free não dá licença comercial — a narração do canal sai de outra conta,
com plano pago).

Como os créditos são poucos (10k/mês ≈ 10 min de fala), este módulo:
  - fala pela ElevenLabs enquanto houver crédito;
  - cai para a voz Maria do Windows quando faltar, sem deixar o OMEGA mudo;
  - registra quanto já gastou, para o usuário poder acompanhar.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG = BASE_DIR / "config" / "api_keys.json"
# A API devolve MP3; o sounddevice só toca PCM. Em vez de mais uma dependência
# de decodificação, reaproveitamos o ffmpeg completo que já vive no Studio.
FFMPEG_STUDIO = BASE_DIR.parent / "studio" / "bin" / "ffmpeg.exe"

API = "https://api.elevenlabs.io/v1"
MODELO = "eleven_multilingual_v2"  # o que fala português decente

# Perfil JARVIS: masculina, britânica, grave, formal. Procuramos POR NOME na
# conta em vez de fixar um voice_id porque a ElevenLabs aposenta as vozes
# padrão (as atuais expiram em 31/12/2026) e um ID fixo viraria erro 404.
# A ordem é a preferência: a primeira que existir na conta vence.
PREFERENCIA = ("george", "daniel", "brian", "charlie", "callum", "adam", "antoni")

_estado = {"creditos_gastos": 0, "sem_credito": False, "voz_resolvida": None}



def _config() -> dict:
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}


def disponivel() -> bool:
    """Há chave configurada e ainda há crédito nesta sessão?"""
    if _estado["sem_credito"]:
        return False
    return bool((_config().get("elevenlabs_api_key") or "").strip())


def creditos_gastos() -> int:
    return _estado["creditos_gastos"]


def assinatura() -> str:
    """Frase com o saldo real da conta, para o comando 'creditos'."""
    chave = (_config().get("elevenlabs_api_key") or "").strip()
    if not chave:
        return "Sem chave da ElevenLabs configurada."
    try:
        r = requests.get(
            f"{API}/user/subscription",
            headers={"xi-api-key": chave},
            timeout=20,
        )
        if not r.ok:
            return f"A ElevenLabs recusou a consulta ({r.status_code})."
        d = r.json()
        usado = d.get("character_count", 0)
        limite = d.get("character_limit", 0)
        restante = max(0, limite - usado)
        plano = d.get("tier", "?")
        return (
            f"Plano {plano}: {restante} de {limite} créditos restantes "
            f"neste ciclo."
        )
    except requests.RequestException as e:
        return f"Não consegui consultar a ElevenLabs: {str(e)[:80]}"


def listar_vozes() -> list[dict]:
    """Vozes disponíveis na conta: [{id, nome, descricao}]."""
    chave = (_config().get("elevenlabs_api_key") or "").strip()
    if not chave:
        return []
    try:
        r = requests.get(f"{API}/voices", headers={"xi-api-key": chave}, timeout=30)
        if not r.ok:
            return []
        return [
            {
                "id": v.get("voice_id", ""),
                "nome": v.get("name", "?"),
                "descricao": (v.get("labels") or {}).get("description", ""),
                "sotaque": (v.get("labels") or {}).get("accent", ""),
                "genero": (v.get("labels") or {}).get("gender", ""),
            }
            for v in r.json().get("voices", [])
        ]
    except requests.RequestException:
        return []


def _vozes_a_tentar() -> list[str]:
    """Ordem de tentativa. `elevenlabs_voice_id` aceita um id ou uma lista.

    Uma voz da Voice Library só responde pela API depois de adicionada à
    conta; por isso há cadeia em vez de um id único — se a primeira der 404,
    a seguinte assume, e só então caímos para a voz do Windows.
    """
    # Uma voz que já funcionou nesta sessão não precisa ser redescoberta.
    if _estado["voz_resolvida"]:
        return [_estado["voz_resolvida"]]

    bruto = _config().get("elevenlabs_voice_id") or []
    if isinstance(bruto, str):
        bruto = [bruto]
    escolhidas = [v.strip() for v in bruto if isinstance(v, str) and v.strip()]
    if escolhidas:
        return escolhidas

    # Sem nada configurado: procura por NOME na conta (sobrevive à
    # aposentadoria das vozes padrão, que trocam de id).
    vozes = listar_vozes()
    if not vozes:
        return []
    por_nome = {v["nome"].strip().lower(): v["id"] for v in vozes}
    for preferida in PREFERENCIA:
        if preferida in por_nome:
            return [por_nome[preferida]]
    masculina = next((v for v in vozes if v["genero"].lower() == "male"), None)
    return [(masculina or vozes[0])["id"]]


def sintetizar(texto: str) -> Path | None:
    """Gera o áudio e devolve o caminho do MP3, ou None se não deu.

    None significa 'use a voz do Windows' — nunca levanta exceção, porque
    ficar mudo é pior que falar com voz robótica.
    """
    cfg = _config()
    chave = (cfg.get("elevenlabs_api_key") or "").strip()
    if not chave or _estado["sem_credito"]:
        return None

    audio = None
    for voz in _vozes_a_tentar():
        try:
            r = requests.post(
                f"{API}/text-to-speech/{voz}",
                headers={"xi-api-key": chave, "Content-Type": "application/json"},
                json={
                    "text": texto,
                    "model_id": cfg.get("elevenlabs_model") or MODELO,
                    "voice_settings": {"stability": 0.45, "similarity_boost": 0.8},
                },
                timeout=60,
            )
        except requests.RequestException:
            return None

        if r.status_code == 401:
            _estado["sem_credito"] = True  # chave inválida: não insistir
            return None
        if r.status_code == 429 or (
            r.status_code == 400 and b"quota" in r.content.lower()
        ):
            # Créditos acabaram: para de tentar até reiniciar o app.
            _estado["sem_credito"] = True
            return None
        if r.ok and r.content:
            _estado["voz_resolvida"] = voz  # fixa a que funcionou
            audio = r.content
            break
        # 404/422: voz inexistente ou não adicionada à conta — tenta a próxima.

    if audio is None:
        return None

    _estado["creditos_gastos"] += len(texto)

    tmp = Path(tempfile.gettempdir())
    mp3 = tmp / f"omega_voz_{os.getpid()}.mp3"
    wav = tmp / f"omega_voz_{os.getpid()}.wav"
    mp3.write_bytes(audio)

    ffmpeg = str(FFMPEG_STUDIO) if FFMPEG_STUDIO.exists() else shutil.which("ffmpeg")
    if not ffmpeg:
        return None
    try:
        subprocess.run(
            [ffmpeg, "-y", "-i", str(mp3), "-ar", "24000", "-ac", "1",
             "-f", "wav", str(wav)],
            capture_output=True,
            timeout=60,
        )
    except (subprocess.SubprocessError, OSError):
        return None
    return wav if wav.exists() and wav.stat().st_size > 0 else None
