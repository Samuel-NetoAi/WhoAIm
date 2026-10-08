#!/usr/bin/env python3
"""
Orçamento de créditos Higgsfield para um vídeo do canal WhoIAm.

Conta de dinheiro não se faz de cabeça: a primeira feita assim saiu errada por 3,6x.

Padrão do canal (2026-10-06): todo bloco é Seedance 2.5 via Cinema Studio 4.0,
30 s, 480p. Imagem é gerada no GPT e não entra na conta.

Preço medido na API do Higgsfield em 19/08/2026 (get_cost). Se mudar, remeça e
corrija a tabela AQUI.

Uso:
  # o vídeo padrão: 20 blocos de 30 s
  python orcamento.py --blocos 20 --saldo 9000

  # com 4 blocos de ação gerados em 4 takes (régua 4/4)
  python orcamento.py --blocos 20 --acao-4takes 4 --saldo 9000

  # quantos vídeos cabem no mês
  python orcamento.py --blocos 20 --saldo 9000 --meta-videos 4
"""

import argparse
import sys

# créditos por segundo, Seedance 2.5 — [MEDIDO] 19/08/2026
PRECO_480 = 2.5
PRECO_720 = 6.5  # só para comparar; o canal não gera em 720p
RETRABALHO_PADRAO = 1.4  # orçado, não medido. Corrigir com o número real do canal.


def fmt(n: float) -> str:
    return f"{n:,.0f}".replace(",", ".")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Orçamento de um vídeo WhoIAm")
    ap.add_argument("--blocos", type=int, default=20, help="Nº de blocos (partes do roteiro)")
    ap.add_argument("--duracao", type=int, default=30, help="Segundos por bloco")
    ap.add_argument("--acao-4takes", type=int, default=0,
                    help="Quantos blocos de ação serão gerados em 4 takes")
    ap.add_argument("--retrabalho", type=float, default=RETRABALHO_PADRAO,
                    help="Multiplicador de regeração dos blocos simples")
    ap.add_argument("--saldo", type=float, help="Créditos disponíveis no mês")
    ap.add_argument("--meta-videos", type=float, help="Quantos vídeos se quer por mês")
    a = ap.parse_args()

    por_bloco = a.duracao * PRECO_480
    simples = a.blocos - a.acao_4takes
    custo_simples = simples * por_bloco * a.retrabalho
    custo_acao = a.acao_4takes * por_bloco * 4
    total = custo_simples + custo_acao

    print(f"Bloco: {a.duracao}s × {PRECO_480} cr/s = {fmt(por_bloco)} créditos (480p)")
    print(f"Blocos simples: {simples} × {fmt(por_bloco)} × {a.retrabalho} retrabalho = {fmt(custo_simples)}")
    if a.acao_4takes:
        print(f"Blocos de ação em 4 takes: {a.acao_4takes} × {fmt(por_bloco)} × 4 = {fmt(custo_acao)}")
    print(f"TOTAL DO VÍDEO: {fmt(total)} créditos "
          f"({a.blocos * a.duracao / 60:.1f} min de vídeo)")
    print(f"  (a 720p seria {fmt(total * PRECO_720 / PRECO_480)} — por isso é sempre 480p)")

    if a.saldo:
        cabem = a.saldo / total
        print(f"Saldo {fmt(a.saldo)}: cabem {cabem:.2f} vídeos")
        if a.meta_videos:
            envelope = a.saldo / a.meta_videos
            folga = envelope - total
            estado = "CABE" if folga >= 0 else "NÃO CABE"
            print(f"Meta {a.meta_videos:g}/mês → envelope {fmt(envelope)} por vídeo: "
                  f"{estado} (folga {fmt(folga)})")


if __name__ == "__main__":
    main()
