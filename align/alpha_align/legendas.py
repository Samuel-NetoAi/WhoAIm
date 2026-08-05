"""Geração de legendas a partir do alinhamento.

Os limites abaixo são a convenção corrente de legendagem (a mesma que
Netflix/BBC publicam em linhas gerais) e existem por causa da leitura humana,
não por gosto: passar deles é o que faz o espectador perder a fala.

O texto vem sempre do roteiro; os tempos, do alinhamento. Uma legenda nunca
atravessa duas linhas do roteiro — cada fala é uma unidade de sentido.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil

from .alinhador import Alinhamento, PalavraAlinhada

MAX_CARACTERES_POR_LINHA = 42
MAX_LINHAS = 2
MAX_CARACTERES = MAX_CARACTERES_POR_LINHA * MAX_LINHAS
DURACAO_MINIMA = 1.0
DURACAO_MAXIMA = 7.0
CARACTERES_POR_SEGUNDO = 17.0


@dataclass
class Legenda:
    indice: int
    t0: float
    t1: float
    texto: str
    linha_roteiro: int
    confianca: float

    @property
    def linhas(self) -> list[str]:
        return quebrar_em_linhas(self.texto)


def quebrar_em_linhas(texto: str) -> list[str]:
    """Quebra em até 2 linhas equilibradas, sem partir palavra."""
    if len(texto) <= MAX_CARACTERES_POR_LINHA:
        return [texto]

    palavras = texto.split()
    melhor: tuple[int, list[str]] | None = None
    for corte in range(1, len(palavras)):
        primeira = " ".join(palavras[:corte])
        segunda = " ".join(palavras[corte:])
        if len(primeira) > MAX_CARACTERES_POR_LINHA:
            break
        if len(segunda) > MAX_CARACTERES_POR_LINHA:
            continue
        desequilibrio = abs(len(primeira) - len(segunda))
        if melhor is None or desequilibrio < melhor[0]:
            melhor = (desequilibrio, [primeira, segunda])

    return melhor[1] if melhor else [texto]


def _fatiar(palavras: list[PalavraAlinhada]) -> list[list[PalavraAlinhada]]:
    """Reparte uma fala em legendas de tamanho EQUILIBRADO.

    Encher cada legenda até o limite e jogar o resto na última produz órfã —
    aquela legenda de uma palavra só que pisca na tela. Em vez disso: descobre
    quantas legendas a fala exige (por texto e por tempo) e reparte o total
    igualmente entre elas.
    """
    if not palavras:
        return []

    origem = palavras[0].inicio
    comprimento = palavras[-1].fim - origem
    duracao = palavras[-1].t1 - palavras[0].t0

    quantidade = max(
        1,
        ceil(comprimento / MAX_CARACTERES),
        ceil(duracao / DURACAO_MAXIMA),
    )
    if quantidade == 1:
        return [palavras]

    alvo = comprimento / quantidade
    fatias: list[list[PalavraAlinhada]] = [[] for _ in range(quantidade)]
    for palavra in palavras:
        meio = (palavra.inicio + palavra.fim) / 2 - origem
        fatias[min(quantidade - 1, int(meio // alvo))].append(palavra)

    return [f for f in fatias if f]


def gerar(alinhamento: Alinhamento) -> list[Legenda]:
    legendas: list[Legenda] = []

    for trecho in alinhamento.linhas:
        do_trecho = [p for p in alinhamento.palavras if p.linha == trecho.indice]
        posicao = {id(p): i for i, p in enumerate(do_trecho)}

        for fatia in _fatiar(do_trecho):
            # O offset da palavra termina na última letra, então o ponto final
            # e a vírgula ficariam de fora. Estica até onde a próxima palavra
            # começa (ou até o fim da fala) para recuperar a pontuação.
            seguinte = posicao[id(fatia[-1])] + 1
            fim = (
                do_trecho[seguinte].inicio
                if seguinte < len(do_trecho)
                else len(trecho.texto)
            )
            ancoradas = sum(1 for p in fatia if p.ancora)
            legendas.append(
                Legenda(
                    indice=len(legendas) + 1,
                    t0=fatia[0].t0,
                    t1=fatia[-1].t1,
                    # Fatia a linha ORIGINAL: preserva vírgula, reticência,
                    # hífen e maiúscula exatamente como o roteiro escreveu.
                    texto=trecho.texto[fatia[0].inicio : fim].strip(),
                    linha_roteiro=trecho.indice,
                    confianca=round(ancoradas / len(fatia), 3),
                )
            )

    return _ajustar_duracoes(legendas, alinhamento.duracao_audio)


def _ajustar_duracoes(legendas: list[Legenda], duracao_audio: float) -> list[Legenda]:
    """Aplica piso e teto de duração sem deixar duas legendas se sobreporem."""
    for i, legenda in enumerate(legendas):
        limite = legendas[i + 1].t0 if i + 1 < len(legendas) else duracao_audio

        # Piso: legenda curta demais some da tela antes de ser lida. Estica no
        # silêncio seguinte, nunca por cima da próxima fala.
        minima = max(DURACAO_MINIMA, len(legenda.texto) / CARACTERES_POR_SEGUNDO)
        if legenda.t1 - legenda.t0 < minima:
            legenda.t1 = round(min(legenda.t0 + minima, limite), 3)

        # Teto: legenda parada 7s na tela é pausa longa da narração, não fala.
        if legenda.t1 - legenda.t0 > DURACAO_MAXIMA:
            legenda.t1 = round(legenda.t0 + DURACAO_MAXIMA, 3)

        if legenda.t1 <= legenda.t0:
            legenda.t1 = round(legenda.t0 + 0.2, 3)

    return legendas


def _timestamp_srt(segundos: float) -> str:
    total_ms = int(round(segundos * 1000))
    horas, resto = divmod(total_ms, 3_600_000)
    minutos, resto = divmod(resto, 60_000)
    segs, ms = divmod(resto, 1000)
    return f"{horas:02d}:{minutos:02d}:{segs:02d},{ms:03d}"


def para_srt(legendas: list[Legenda]) -> str:
    partes = []
    for legenda in legendas:
        tempo = f"{_timestamp_srt(legenda.t0)} --> {_timestamp_srt(legenda.t1)}"
        partes.append(f"{legenda.indice}\n{tempo}\n" + "\n".join(legenda.linhas))
    return "\n\n".join(partes) + "\n"


def para_vtt(legendas: list[Legenda]) -> str:
    corpo = para_srt(legendas).replace(",", ".")
    return "WEBVTT\n\n" + corpo
