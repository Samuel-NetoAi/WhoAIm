"""Detector de PALMAS no fluxo de áudio que já existe.

Serve para chamar o OMEGA de volta à tela quando ele está minimizado, sem
teclado e sem palavra de ativação. Bate palma duas vezes e ele aparece.

Por que DSP em vez de modelo: uma palma é acusticamente simples — um estouro
de banda larga com ataque quase instantâneo e decaimento em poucas centenas de
milissegundos. Reconhecer isso é aritmética sobre a energia do sinal. Um modelo
de wake word seria mais pesado, mais lento e não mais certeiro para esse caso.

Sem numpy de propósito: ele não está instalado no venv, e o `audioop`, que
faria isso na biblioteca padrão, foi removido no Python 3.13. Cada janela de
10 ms tem 160 amostras — somar quadrados em Python puro custa quase nada, e
`array` faz a desempacotagem em C.

O detector NÃO abre o app fechado: alguém precisa estar ouvindo o microfone
para escutar a palma, e esse alguém é o próprio OMEGA rodando. Ele traz de
volta o que está minimizado; não ressuscita o que não existe.
"""

from __future__ import annotations

from array import array
from dataclasses import dataclass

# Janela de análise. 10 ms é curto o bastante para o ataque de uma palma não
# se diluir na média e longo o bastante para a conta ser barata.
JANELA_MS = 10

# Quantas vezes acima do ruído de fundo a energia precisa saltar. Palma real
# passa MUITO disso (20–50x); o limiar baixo cobre microfone fraco e sala grande.
FATOR_DE_PICO = 8.0

# Piso absoluto: sem ele, o silêncio absoluto vira "fundo zero" e qualquer
# ruído mínimo parece um salto de mil vezes.
PISO_ABSOLUTO = 1500.0  # RMS em amostras int16 (escala -32768..32767)

# O que separa palma de voz alta: a palma DESABA. Passados ~120 ms ela já caiu
# para uma fração do pico; uma vogal gritada continua ali.
DECAIMENTO_MS = 120
QUEDA_MINIMA = 0.35  # precisa cair abaixo de 35% do pico

# Duas palmas humanas ficam nesta faixa. Abaixo é eco/repique da mesma palma;
# acima já não é um gesto, são dois eventos separados.
INTERVALO_MIN_S = 0.12
INTERVALO_MAX_S = 0.70

# Depois de reconhecer o gesto, ignora tudo por um tempo — senão o eco da
# segunda palma vira a primeira do gesto seguinte.
DESCANSO_S = 1.2

# O fundo acompanha a SALA, não os eventos: sobe e desce devagar, na escala de
# segundos. Com suavização rápida, a própria palma entrava na média e levantava
# o limiar acima de si mesma no instante em que tocava — o detector se cegava.
SUAVIZACAO_SUBIDA = 0.05
SUAVIZACAO_DESCIDA = 0.02


def _rms(amostras: array, inicio: int, fim: int) -> float:
    soma = 0
    for i in range(inicio, fim):
        v = amostras[i]
        soma += v * v
    n = fim - inicio
    return (soma / n) ** 0.5 if n else 0.0


@dataclass
class DetectorDePalmas:
    """Máquina de estados que consome blocos de áudio e avisa o gesto.

    `taxa` é a taxa de amostragem do fluxo (16 kHz no motor gratuito).
    `ao_detectar` é chamado quando duas palmas fecham o gesto.
    """

    taxa: int = 16000
    ao_detectar: object = None

    _fundo: float = 0.0
    _pico_pendente: float = 0.0
    _instante_pico: float = 0.0
    _aguardando_decaimento: bool = False
    # Começa muito no passado: a primeira palma não pode formar par com o nada.
    _ultima_palma: float = -999.0
    _mudo_ate: float = 0.0
    _relogio: float = 0.0

    @property
    def _amostras_por_janela(self) -> int:
        return max(1, int(self.taxa * JANELA_MS / 1000))

    def alimentar(self, dados: bytes) -> bool:
        """Consome um bloco PCM16 mono. Devolve True se o gesto fechou aqui."""
        amostras = array("h")
        amostras.frombytes(dados[: len(dados) - (len(dados) % 2)])

        largura = self._amostras_por_janela
        passo = JANELA_MS / 1000
        detectou = False

        for inicio in range(0, len(amostras) - largura + 1, largura):
            energia = _rms(amostras, inicio, inicio + largura)
            self._relogio += passo
            if self._processar(energia):
                detectou = True

        return detectou

    def _processar(self, energia: float) -> bool:
        agora = self._relogio

        # 1. Esperando confirmar o decaimento de um candidato.
        if self._aguardando_decaimento:
            if agora - self._instante_pico >= DECAIMENTO_MS / 1000:
                caiu = energia < self._pico_pendente * QUEDA_MINIMA
                self._aguardando_decaimento = False
                if caiu:
                    return self._registrar_palma(self._instante_pico)
            return False

        if agora < self._mudo_ate:
            self._atualizar_fundo(energia)
            return False

        limiar = max(self._fundo * FATOR_DE_PICO, PISO_ABSOLUTO)
        if energia > limiar:
            self._pico_pendente = energia
            self._instante_pico = agora
            self._aguardando_decaimento = True
            # NÃO alimenta o fundo com o próprio candidato — era isso que fazia
            # o limiar disparar junto com a palma e nunca ser ultrapassado.
            return False

        self._atualizar_fundo(energia)
        return False

    def _atualizar_fundo(self, energia: float) -> None:
        if self._fundo == 0.0:
            self._fundo = energia
            return
        alfa = SUAVIZACAO_SUBIDA if energia > self._fundo else SUAVIZACAO_DESCIDA
        self._fundo = (1 - alfa) * self._fundo + alfa * energia

    def _registrar_palma(self, instante: float) -> bool:
        intervalo = instante - self._ultima_palma
        self._ultima_palma = instante

        if INTERVALO_MIN_S <= intervalo <= INTERVALO_MAX_S:
            self._mudo_ate = self._relogio + DESCANSO_S
            self._ultima_palma = -999.0
            if callable(self.ao_detectar):
                try:
                    self.ao_detectar()
                except Exception:  # noqa: BLE001 — gesto nunca derruba o áudio
                    pass
            return True
        return False


def detector_para(taxa: int, ao_detectar) -> DetectorDePalmas:
    return DetectorDePalmas(taxa=taxa, ao_detectar=ao_detectar)


# ---------------------------------------------------------------------------
# Geração de áudio sintético — usada pelos testes, e útil para calibrar o
# limiar sem precisar bater palma na frente do microfone.


def _pcm(valores) -> bytes:
    limitados = array("h", (max(-32768, min(32767, int(v))) for v in valores))
    return limitados.tobytes()


def silencio(segundos: float, taxa: int = 16000, ruido: float = 200.0) -> bytes:
    """Silêncio com um chiado de fundo — microfone real nunca dá zero."""
    import random

    n = int(segundos * taxa)
    return _pcm(random.gauss(0, ruido) for _ in range(n))


def palma(taxa: int = 16000, amplitude: float = 20000.0, decaimento_s: float = 0.09) -> bytes:
    """Estouro de banda larga com ataque imediato e queda exponencial."""
    import math
    import random

    n = int(decaimento_s * taxa)
    return _pcm(
        random.gauss(0, amplitude) * math.exp(-4.0 * i / n) for i in range(n)
    )


def voz_alta(segundos: float, taxa: int = 16000, amplitude: float = 12000.0) -> bytes:
    """Som forte mas SUSTENTADO — o que não pode ser confundido com palma."""
    import math

    n = int(segundos * taxa)
    return _pcm(
        amplitude * math.sin(2 * math.pi * 180 * i / taxa) for i in range(n)
    )
