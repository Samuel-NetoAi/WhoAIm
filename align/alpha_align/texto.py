"""Normalização e tokenização de texto pt-BR.

Os dois lados do alinhamento (roteiro escrito e transcrição do ASR) precisam
ser normalizados EXATAMENTE da mesma forma, senão palavras iguais não casam.
Toda a regra de normalização vive aqui, num lugar só, por isso.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

# Números por extenso: o ASR devolve "quinze", o roteiro pode trazer "15".
# Cobre 0-20 e as dezenas, que é o que aparece em narração de mitologia
# ("três irmãs", "mil anos"). Fora disso, o token vira anti-âncora e o
# interpolador resolve — não vale a pena um conversor completo.
_NUMEROS = {
    "0": "zero", "1": "um", "2": "dois", "3": "tres", "4": "quatro",
    "5": "cinco", "6": "seis", "7": "sete", "8": "oito", "9": "nove",
    "10": "dez", "11": "onze", "12": "doze", "13": "treze", "14": "quatorze",
    "15": "quinze", "16": "dezesseis", "17": "dezessete", "18": "dezoito",
    "19": "dezenove", "20": "vinte", "30": "trinta", "40": "quarenta",
    "50": "cinquenta", "60": "sessenta", "70": "setenta", "80": "oitenta",
    "90": "noventa", "100": "cem", "1000": "mil",
}

# O que conta como palavra. O apóstrofo entra ("d'água" é uma palavra só); o
# hífen NÃO entra, porque o ASR devolve "chamam" e "nas" separados em
# "chamam-nas" — casar exige quebrar do mesmo jeito.
_PALAVRA = re.compile(r"[0-9A-Za-zÀ-ÿ]+(?:'[A-Za-zÀ-ÿ]+)*")


def remover_acentos(texto: str) -> str:
    decomposto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in decomposto if unicodedata.category(c) != "Mn")


def normalizar(palavra: str) -> str:
    """Devolve a forma comparável de uma palavra ('Dríades!' -> 'driades').

    Devolve string vazia quando o token não tem conteúdo comparável (só
    pontuação) — quem chama descarta esses.
    """
    chave = remover_acentos(palavra.strip().lower())
    chave = re.sub(r"[^a-z0-9']", "", chave)
    chave = chave.strip("'")
    return _NUMEROS.get(chave, chave)


@dataclass(frozen=True)
class Token:
    """Uma palavra do roteiro e sua posição exata na linha de origem.

    Guardar os offsets (em vez de só o texto) é o que permite reconstruir a
    legenda fatiando a linha ORIGINAL — com vírgulas, reticências, hífens e
    maiúsculas intactos. Recolar tokens com espaço perderia tudo isso.
    """

    texto: str
    chave: str
    inicio: int
    fim: int


def tokenizar(texto: str) -> list[Token]:
    return [
        Token(texto=m.group(), chave=chave, inicio=m.start(), fim=m.end())
        for m in _PALAVRA.finditer(texto)
        if (chave := normalizar(m.group()))
    ]
