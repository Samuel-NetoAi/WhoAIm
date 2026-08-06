"""Encontra o projeto certo a partir de um nome MAL FALADO.

O reconhecimento de voz não entrega o nome limpo: "IT A Coisa" chegou como
"e a coisas", "do piteco", "doente". Casar por igualdade exata condena o
usuário a digitar — e ele nem sempre está na frente do PC.

A busca vai do mais seguro ao mais tolerante e para no primeiro que decide:
  1. nome idêntico
  2. apelido conhecido (Pennywise = IT = A Coisa)
  3. palavra marcante em comum ("coisa" -> "IT A Coisa")
  4. semelhança sonora/ortográfica acima de um limiar

Ambiguidade nunca é resolvida no chute: se dois projetos empatam, quem
chamou recebe a lista para escolher.
"""

from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

from .pipeline import AI_PROJECT_ROOT
from .vocabulario import mesma_criatura

# Abaixo disto a semelhança é coincidência, não intenção.
LIMIAR = 0.62

# Palavras que aparecem em qualquer frase e não distinguem nada.
VAZIAS = {
    "o", "a", "os", "as", "de", "do", "da", "dos", "das", "e", "em", "no",
    "na", "um", "uma", "para", "pra", "com", "que", "meu", "minha", "the",
    "projeto", "criatura", "video", "sobre",
}


def _norm(texto: str) -> str:
    sem_acento = "".join(
        c for c in unicodedata.normalize("NFD", texto.lower())
        if unicodedata.category(c) != "Mn"
    )
    return re.sub(r"[^a-z0-9 ]+", " ", sem_acento).strip()


def _palavras_uteis(texto: str) -> set[str]:
    # Palavra de 1 letra não distingue nada e gera falso positivo.
    return {p for p in _norm(texto).split() if p not in VAZIAS and len(p) > 1}


def _semelhanca(a: str, b: str) -> float:
    return SequenceMatcher(None, _norm(a), _norm(b)).ratio()


def listar_pastas() -> list[Path]:
    raiz = AI_PROJECT_ROOT / "Criaturas"
    if not raiz.is_dir():
        return []
    return [p for p in raiz.iterdir() if p.is_dir() and not p.name.startswith("_")]


def resolver(nome: str) -> tuple[Path | None, list[str]]:
    """(pasta, candidatos). Pasta preenchida = decidiu; senão veja a lista."""
    nome = (nome or "").strip()
    pastas = listar_pastas()
    if not nome or not pastas:
        return None, [p.name for p in pastas]

    alvo = _norm(nome)

    # 1. idêntico
    for p in pastas:
        if _norm(p.name) == alvo:
            return p, []

    # 2. apelido conhecido
    for p in pastas:
        if mesma_criatura(nome, p.name):
            return p, []

    # 3. palavra marcante em comum — resolve "analisar e a coisas"
    faladas = _palavras_uteis(nome)
    if faladas:
        por_palavra = [p for p in pastas if _palavras_uteis(p.name) & faladas]
        if len(por_palavra) == 1:
            return por_palavra[0], []
        if len(por_palavra) > 1:
            return None, [p.name for p in por_palavra]

    # 4. semelhança geral, com margem para não decidir em empate técnico
    notas = sorted(
        ((_semelhanca(nome, p.name), p) for p in pastas),
        key=lambda x: x[0],
        reverse=True,
    )
    if notas and notas[0][0] >= LIMIAR:
        melhor, segunda = notas[0], (notas[1] if len(notas) > 1 else (0.0, None))
        if melhor[0] - segunda[0] >= 0.08:
            return melhor[1], []
        return None, [p.name for _, p in notas[:3] if p]

    return None, [p.name for p in pastas]


def frase_de_ajuda(nome: str, candidatos: list[str]) -> str:
    """O que dizer quando não deu para decidir.

    Distingue "está entre estes dois" de "não faço ideia": listar quinze
    projetos porque nenhum se parece com o que foi dito não ajuda ninguém.
    """
    total = len(listar_pastas())
    if not candidatos:
        return f"Não achei nenhum projeto parecido com {nome}."
    # Quando os "candidatos" são praticamente todos, não houve semelhança —
    # o reconhecimento errou feio e sugerir nomes ao acaso confunde.
    if len(candidatos) >= max(4, total - 1):
        return (
            f"Não entendi qual projeto é {nome}. "
            "Diga 'projetos' para ver a lista na tela."
        )
    if len(candidatos) == 1:
        return f"Não achei {nome}. Quis dizer {candidatos[0]}?"
    return "Qual deles, senhor: " + ", ".join(candidatos[:4]) + "?"
