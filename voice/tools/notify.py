"""Canal de aviso ATIVO: as ferramentas falam sem serem perguntadas.

Antes, tudo aqui era "pergunte o status": a pesquisa rodava por dez minutos em
silêncio e o render também. Quem disparou não tinha como saber se ainda estava
andando, se tinha acabado ou se tinha morrido — e ficava perguntando.

As ferramentas rodam em threads e não conhecem a janela, então elas publicam
aqui e o `main.py` liga este canal na UI. Sem notificador registrado (testes,
modo headless) as mensagens são descartadas em silêncio, nunca quebram.
"""

from __future__ import annotations

import threading
from typing import Callable, Protocol


class Notificador(Protocol):
    def __call__(self, texto: str, *, falar: bool) -> None: ...


_notificador: Notificador | None = None
_trava = threading.Lock()


def definir_notificador(fn: Notificador | None) -> None:
    global _notificador
    with _trava:
        _notificador = fn


def notificar(texto: str, *, falar: bool = False) -> None:
    """Publica um aviso. `falar=True` só para marcos — começo, fim e erro.

    Batimento de progresso vai só para o log: ouvir "ainda pesquisando" a cada
    dois minutos cansa mais do que informa.
    """
    with _trava:
        fn = _notificador
    if fn is None:
        return
    try:
        fn(texto, falar=falar)
    except Exception:  # noqa: BLE001 — aviso nunca derruba a tarefa que avisa
        pass


def duracao_falada(segundos: float) -> str:
    """"3 minutos", "1 minuto e meio", "40 segundos" — para ler em voz alta."""
    if segundos < 90:
        return f"{int(segundos)} segundos"
    minutos = segundos / 60
    if minutos < 2:
        return "1 minuto e meio"
    return f"{int(round(minutos))} minutos"


def batimento(
    intervalo_segundos: float,
    mensagem: Callable[[float], str],
    ativo: Callable[[], bool],
) -> threading.Thread:
    """Avisa de tempos em tempos enquanto `ativo()` for verdadeiro.

    Existe para tarefas longas (pesquisa, render) darem sinal de vida. Roda em
    daemon: fechar a janela não fica preso esperando o batimento.
    """
    import time

    inicio = time.monotonic()

    # Dorme em fatias para reagir rápido ao fim da tarefa, mas nunca em fatias
    # maiores que um quarto do intervalo — senão um batimento curto passa
    # batido e a função só serve para os intervalos longos de produção.
    fatia = min(0.5, intervalo_segundos / 4)

    def laco() -> None:
        ultimo_aviso = inicio
        while ativo():
            time.sleep(fatia)
            agora = time.monotonic()
            if agora - ultimo_aviso < intervalo_segundos:
                continue
            if not ativo():
                return
            notificar(mensagem(agora - inicio))
            ultimo_aviso = agora

    t = threading.Thread(target=laco, daemon=True)
    t.start()
    return t
