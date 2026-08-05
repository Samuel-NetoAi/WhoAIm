#!/usr/bin/env python
"""Mede o ERRO DE SINCRONIA do alinhador, em segundos.

Não é teste de unidade: é o experimento que responde "a legenda vai ficar
torta?" com número em vez de opinião. Constrói uma narração sintética a partir
de um roteiro real (cujos tempos verdadeiros passamos a conhecer), simula um
ASR que reconhece só uma fração das palavras, alinha, e compara com a verdade.

    python testes/simular_precisao.py [caminho/do/roteiro.md]

Serve para decidir se vale trocar o Vosk por WhisperX: rode de novo com a taxa
de acerto do motor novo e compare o erro.
"""

from __future__ import annotations

import random
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from alpha_align.alinhador import PalavraASR, alinhar
from alpha_align.roteiro import carregar

# Narração do canal: ritmo lento e pausado (~2 palavras/s com respiros).
SEGUNDOS_POR_CARACTERE = 0.075
PAUSA_ENTRE_FALAS = 0.6
TAXA_ERRO_ASR = 0.15  # fração das palavras "reconhecidas" que saem trocadas


def narracao_sintetica(roteiro) -> tuple[list[tuple[str, float, float]], float]:
    """Verdade fundamental: cada palavra com o tempo em que foi 'dita'."""
    verdade: list[tuple[str, float, float]] = []
    relogio = 0.0
    for linha in roteiro.linhas:
        for token in linha.tokens:
            duracao = max(0.12, len(token.chave) * SEGUNDOS_POR_CARACTERE)
            verdade.append((token.chave, relogio, relogio + duracao))
            relogio += duracao + 0.05
        relogio += PAUSA_ENTRE_FALAS
    return verdade, relogio


def asr_simulado(verdade, taxa_acerto: float, semente: int) -> list[PalavraASR]:
    sorteio = random.Random(semente)
    saida: list[PalavraASR] = []
    for chave, t0, t1 in verdade:
        if sorteio.random() > taxa_acerto:
            continue
        # Parte do que o ASR "reconhece" vem errado — e não pode virar âncora.
        if sorteio.random() < TAXA_ERRO_ASR:
            chave = chave[::-1] + "x"
        # Vosk marca a fronteira da palavra com pequeno desvio.
        desvio = sorteio.uniform(-0.05, 0.05)
        saida.append(PalavraASR(chave, chave, round(t0 + desvio, 3), round(t1 + desvio, 3)))
    return saida


def medir(roteiro, taxa: float, semente: int) -> dict:
    verdade, duracao = narracao_sintetica(roteiro)
    resultado = alinhar(roteiro, asr_simulado(verdade, taxa, semente), duracao)
    erros = [
        abs(palavra.t0 - real_t0)
        for palavra, (_, real_t0, _) in zip(resultado.palavras, verdade)
    ]
    erros.sort()
    return {
        "confianca": resultado.confianca,
        "mediana": statistics.median(erros),
        "media": statistics.fmean(erros),
        "p95": erros[int(len(erros) * 0.95)],
        "pior": erros[-1],
    }


def main() -> None:
    caminho = sys.argv[1] if len(sys.argv) > 1 else None
    if not caminho:
        sys.exit("Uso: python testes/simular_precisao.py <roteiro.md>")

    roteiro = carregar(caminho)
    print(f"Roteiro: {len(roteiro.linhas)} falas, {len(roteiro.chaves)} palavras")
    print(f"\n{'ASR acerta':>10}  {'âncoras':>8}  {'erro mediano':>13}  {'médio':>7}  {'p95':>7}  {'pior':>7}")
    print("-" * 64)

    for taxa in (0.10, 0.25, 0.40, 0.60, 0.80, 0.95):
        # Média de várias sementes: uma amostra só engana.
        amostras = [medir(roteiro, taxa, semente) for semente in range(5)]
        media = lambda campo: statistics.fmean(a[campo] for a in amostras)  # noqa: E731
        print(
            f"{taxa:>9.0%}  {media('confianca'):>7.0%}  "
            f"{media('mediana'):>12.2f}s  {media('media'):>6.2f}s  "
            f"{media('p95'):>6.2f}s  {media('pior'):>6.2f}s"
        )

    print(
        "\nLeitura: o erro mediano é o que o espectador sente na legenda.\n"
        "Acima de ~0,5s a legenda começa a parecer fora de sincronia."
    )


if __name__ == "__main__":
    main()
