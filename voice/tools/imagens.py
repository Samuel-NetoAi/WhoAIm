"""Geração de imagem pela API da OpenAI (gpt-image-1).

A conta do Samuel está SEM CRÉDITOS hoje (a API responde 429
`credit_balance_exhausted`), então isto só passa a funcionar quando houver
saldo. Foi construído mesmo assim porque a falha é limpa e informativa: em
vez de um erro cru, o OMEGA diz o que está faltando e o que fazer.

As imagens vão para a pasta do projeto (`<criatura>-video/public/imagens/`)
quando há criatura no pedido, senão para `Omega/imagens/`. Ficar junto do
projeto importa: é lá que o Studio e as skills procuram material.
"""

from __future__ import annotations

import base64
import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path

import requests

from .pipeline import AI_PROJECT_ROOT, _slugify
from .projetos import resolver as _resolver_projeto

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG = BASE_DIR / "config" / "api_keys.json"
PASTA_SOLTA = BASE_DIR.parent / "imagens"

API = "https://api.openai.com/v1/images/generations"
MODELO = "gpt-image-1"
TAMANHO = "1024x1024"


def _chave() -> str:
    try:
        return (
            json.loads(CONFIG.read_text(encoding="utf-8"))
            .get("openai_api_key", "")
            .strip()
        )
    except Exception:  # noqa: BLE001
        return ""


def _nome_de_arquivo(descricao: str) -> str:
    texto = unicodedata.normalize("NFD", descricao.lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = re.sub(r"[^a-z0-9]+", "-", texto).strip("-")[:40] or "imagem"
    return f"{texto}-{datetime.now().strftime('%H%M%S')}.png"


def _destino(descricao: str, criatura: str | None) -> Path:
    if criatura:
        pasta, _ = _resolver_projeto(criatura)
        if pasta is not None:
            destino = (
                pasta / f"{_slugify(pasta.name)}-video" / "public" / "imagens"
            )
            destino.mkdir(parents=True, exist_ok=True)
            return destino / _nome_de_arquivo(descricao)
    PASTA_SOLTA.mkdir(parents=True, exist_ok=True)
    return PASTA_SOLTA / _nome_de_arquivo(descricao)


def gerar(descricao: str, criatura: str | None = None, ui=None) -> str:
    """Gera uma imagem e a exibe. Devolve a frase a ser falada."""
    descricao = (descricao or "").strip()
    if not descricao:
        return "Descreva a imagem, senhor."

    chave = _chave()
    if not chave:
        return "Não há chave da OpenAI configurada para gerar imagens."

    try:
        r = requests.post(
            API,
            headers={"Authorization": f"Bearer {chave}",
                     "Content-Type": "application/json"},
            json={"model": MODELO, "prompt": descricao, "n": 1,
                  "size": TAMANHO},
            timeout=180,
        )
    except requests.RequestException as e:
        return f"Não consegui falar com a OpenAI: {str(e)[:90]}"

    if r.status_code in (401, 403):
        return "A OpenAI recusou a chave para gerar imagens."
    if r.status_code == 429:
        # Distingue falta de saldo de excesso de chamadas: a ação do usuário
        # é completamente diferente em cada caso.
        corpo = r.text.lower()
        if "credit" in corpo or "quota" in corpo or "billing" in corpo:
            return (
                "A conta da OpenAI está sem créditos, então não consigo gerar "
                "imagens ainda. Adicione saldo em platform.openai.com, na área "
                "de cobrança, e o comando passa a funcionar sozinho."
            )
        return "A OpenAI pediu para esperar um pouco (limite de chamadas)."
    if not r.ok:
        return f"A geração falhou ({r.status_code})."

    try:
        item = r.json()["data"][0]
    except (KeyError, IndexError, ValueError):
        return "A OpenAI respondeu num formato que não reconheci."

    destino = _destino(descricao, criatura)
    if item.get("b64_json"):
        destino.write_bytes(base64.b64decode(item["b64_json"]))
    elif item.get("url"):
        try:
            baixado = requests.get(item["url"], timeout=120)
            baixado.raise_for_status()
            destino.write_bytes(baixado.content)
        except requests.RequestException:
            return "A imagem foi gerada, mas não consegui baixá-la."
    else:
        return "A OpenAI não devolveu imagem."

    if ui is not None and hasattr(ui, "show_image"):
        ui.show_image(f"imagem — {descricao[:40]}", str(destino))

    onde = "no projeto" if criatura else "na pasta de imagens"
    return f"Imagem pronta e {onde}: {destino.name}. Está na tela."
