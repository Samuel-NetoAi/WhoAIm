"""Alinhamento forçado roteiro ↔ narração para o pipeline do canal WhoIAm.

Entrada: o roteiro exato (Documento 1) + o áudio exato da narração.
Saída: o tempo real de cada palavra, linha e bloco — que alimenta, de uma vez,
os cortes do Studio, os cues de trilha, as transições e as legendas.
"""

from .alinhador import Alinhamento, PalavraASR, alinhar
from .roteiro import Roteiro, carregar

__all__ = ["Alinhamento", "PalavraASR", "Roteiro", "alinhar", "carregar"]
