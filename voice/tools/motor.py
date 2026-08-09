"""Quem decide qual motor de voz está no ar — e como trocar sem reiniciar.

POR QUE O PADRÃO MUDOU. O Live (voz em tempo real do Gemini) é o mais
agradável de usar, e por isso era o padrão. Só que ele cobra pelo ÁUDIO: uma
troca curta medida aqui deu 436 tokens, e ele consome enquanto ouve, não só
quando responde. Na camada gratuita isso estoura no meio da sessão — foi o
que aconteceu com o Samuel, e o sintoma na tela foi um `1008 policy
violation` seguido de "a cota gratuita do Gemini estourou".

O motor local gasta muito menos: manda texto, não áudio. Não é tão fluido,
mas a maior parte do uso dele são COMANDOS ("pesquisa da Medusa", "montar o
vídeo"), que nem precisam de conversa.

Então a inversão: o local é o padrão, e o Live sobe **sob demanda**, quando
ele pedir conversa. A cota passa a ser gasta onde tem valor.

Este módulo é só o árbitro. Os motores não se conhecem: cada um pergunta
`quer_trocar()` no próprio laço e sai quando é a vez do outro.
"""

from __future__ import annotations

import threading

_estado: dict = {"atual": "", "pedido": None}
_trava = threading.Lock()

NOMES = {
    "live": "voz em tempo real (Gemini Live)",
    "free": "motor local (Whisper + Gemini + voz do Windows)",
    "realtime": "OpenAI Realtime",
}


def definir_atual(nome: str) -> None:
    with _trava:
        _estado["atual"] = nome
        _estado["pedido"] = None


def atual() -> str:
    return _estado["atual"]


def pedir(nome: str) -> str:
    """Pede a troca. O motor em execução sai no próximo laço."""
    nome = (nome or "").strip().lower()
    if nome not in NOMES:
        return f"Não conheço o motor {nome}."
    if nome == _estado["atual"]:
        return f"Já estou no {NOMES[nome]}."
    with _trava:
        _estado["pedido"] = nome
    return f"Trocando para o {NOMES[nome]}. Um instante."


def quer_trocar() -> str | None:
    """O motor em execução chama isto para saber se deve sair."""
    return _estado["pedido"]


def consumir_pedido() -> str | None:
    with _trava:
        pedido, _estado["pedido"] = _estado["pedido"], None
    return pedido
