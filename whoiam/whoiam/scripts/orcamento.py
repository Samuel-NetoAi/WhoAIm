#!/usr/bin/env python3
"""
Orçamento de créditos Higgsfield para um vídeo do canal WhoIAm.

Existe porque a conta de "quantos vídeos eu consigo fazer" foi feita de cabeça uma vez
e saiu errada por 3,6x (o preço observado de 75 créditos era Seedance 2.5 em 480p, não
o padrão do canal). Conta de dinheiro não se faz de cabeça.

Plano do canal: Higgsfield ULTRA, degrau de 9.000 créditos/mês (US$ 270/mês, anual)
=> US$ 0,03 por crédito. Use --saldo 9000.

Preços em CRÉDITOS POR SEGUNDO, medidos na API do Higgsfield em 19/08/2026 via get_cost.
Se algum mudar, remeça com get_cost e corrija a tabela AQUI — não no meio de uma conversa.

Uso:
  # um vídeo todo em Seedance 2.5 720p, 20 blocos de 30s
  python3 orcamento.py --blocos 20 --duracao 30 --modelo seedance25_720

  # orçamento misto: 6 blocos de ação em Seedance 2.5 720p + 14 simples em Cinema Studio std
  python3 orcamento.py --acao 6 --acao-duracao 30 --acao-modelo seedance25_720 \
                       --simples 14 --simples-duracao 12 --simples-modelo cinema_std

  # padrão do canal: 480p em tudo + ECU da revelação em 1080p nativo
  python3 orcamento.py --acao 19 --acao-duracao 30 --acao-modelo seedance25_480 \
                       --simples 1 --simples-duracao 10 --simples-modelo seedance25_1080 \
                       --saldo 9000

  # ENVELOPE: quanto posso gastar por vídeo para fechar 4/mês, e quanto de
  # retrabalho isso tolera (o modo mais útil — ver "envelope" abaixo)
  python3 orcamento.py --envelope --saldo 9000 --meta-videos 4 \
                       --duracao-video 480 --vitrine 30 --vitrine-modelo seedance25_1080

  # quantos vídeos de 10 min cabem no saldo, por modelo
  python3 orcamento.py --tabela --saldo 9000
"""

import argparse

# créditos por segundo — [MEDIDO] 19/08/2026
PRECOS = {
    "seedance25_1080": (9.0, "Seedance 2.5 · 1080p", 30),
    "seedance25_720": (6.5, "Seedance 2.5 · 720p", 30),
    "seedance25_480": (2.5, "Seedance 2.5 · 480p", 30),
    "seedance20_1080": (9.0, "Seedance 2.0 std · 1080p", 15),
    "seedance20_720": (4.5, "Seedance 2.0 std · 720p", 15),
    "seedance20mini_720": (2.5, "Seedance 2.0 Mini · 720p", 15),
    "cinema_pro": (2.0, "Cinema Studio Video · pro", 12),
    "cinema_std": (1.5, "Cinema Studio Video · std", 12),
}

RETRABALHO_PADRAO = 1.4  # orçado, não medido. Corrigir com o número real do canal.

# Imagens (model sheet, storyboard, clean plate, painel avulso, thumb) ficam FORA das contas
# abaixo de propósito: no padrão do canal (nano_banana_pro 2k, count 4) são ~2 créditos cada,
# ~50 créditos por vídeo inteiro, contra 1.900-3.900 do vídeo. É ruído. Ver
# references/higgsfield-cinema-studio.md secao 2.


def fmt(n: float) -> str:
    return f"{n:,.0f}".replace(",", ".")


def custo(blocos: int, duracao: int, modelo: str) -> tuple[float, str, int]:
    if modelo not in PRECOS:
        raise SystemExit(f"modelo desconhecido: {modelo}. Opções: {', '.join(PRECOS)}")
    cr_s, nome, teto = PRECOS[modelo]
    if duracao > teto:
        raise SystemExit(
            f"ERRO: {nome} aceita no máximo {teto}s por geração; você pediu {duracao}s.\n"
            f"       Reduza a duração do bloco ou troque de modelo."
        )
    return blocos * duracao * cr_s, nome, blocos * duracao


def linha(rotulo: str, blocos: int, duracao: int, modelo: str, retrab: float) -> float:
    total, nome, segundos = custo(blocos, duracao, modelo)
    print(f"  {rotulo}: {blocos} blocos × {duracao}s = {segundos}s  |  {nome}")
    print(f"      sem retrabalho: {fmt(total)} cr   |   com ×{retrab}: {fmt(total * retrab)} cr")
    return total


def main() -> None:
    ap = argparse.ArgumentParser(description="Orçamento de créditos Higgsfield por vídeo.")
    ap.add_argument("--blocos", type=int, help="Nº de blocos (modo simples, um modelo só)")
    ap.add_argument("--duracao", type=int, default=30, help="Duração de cada bloco em segundos")
    ap.add_argument("--modelo", default="seedance25_720", help=f"Um de: {', '.join(PRECOS)}")
    ap.add_argument("--acao", type=int, default=0, help="Nº de blocos classificados AÇÃO")
    ap.add_argument("--acao-duracao", type=int, default=30)
    ap.add_argument("--acao-modelo", default="seedance25_720")
    ap.add_argument("--simples", type=int, default=0, help="Nº de blocos classificados SIMPLES")
    ap.add_argument("--simples-duracao", type=int, default=12)
    ap.add_argument("--simples-modelo", default="cinema_std")
    ap.add_argument("--retrabalho", type=float, default=RETRABALHO_PADRAO)
    ap.add_argument("--saldo", type=float, help="Créditos disponíveis no mês (rode `balance`)")
    ap.add_argument("--tabela", action="store_true",
                    help="Mostra quantos vídeos de 10 min cabem no saldo, por modelo")
    ap.add_argument("--envelope", action="store_true",
                    help="Modo envelope: fixa o orçamento POR VÍDEO a partir da meta mensal")
    ap.add_argument("--meta-videos", type=float, default=4.0,
                    help="Vídeos por mês que o canal quer sustentar (padrão 4)")
    ap.add_argument("--duracao-video", type=int, default=480,
                    help="Duração-alvo do vídeo em segundos (padrão 480 = 8 min)")
    ap.add_argument("--vitrine", type=int, default=30,
                    help="Segundos do bloco-vitrine (ECU da criatura) em alta resolução")
    ap.add_argument("--vitrine-modelo", default="seedance25_1080")
    ap.add_argument("--base-modelo", default="seedance25_480",
                    help="Modelo/resolução do resto do vídeo")
    args = ap.parse_args()

    if args.envelope:
        saldo = args.saldo or 9000
        envelope = saldo / args.meta_videos
        base_crs = PRECOS[args.base_modelo][0]
        vit_crs, vit_nome, vit_teto = PRECOS[args.vitrine_modelo]
        if args.vitrine > vit_teto:
            raise SystemExit(f"ERRO: {vit_nome} aceita no máximo {vit_teto}s.")
        base_seg = args.duracao_video - args.vitrine
        custo_base = base_seg * base_crs + args.vitrine * vit_crs
        max_retrab = envelope / custo_base if custo_base else 0
        m, s = divmod(args.duracao_video, 60)
        print(f"\nENVELOPE POR VÍDEO — meta de {args.meta_videos:g} vídeos/mês em {fmt(saldo)} cr\n")
        print(f"  Envelope: {fmt(envelope)} créditos por vídeo (~US$ {envelope*0.03:,.0f})")
        print(f"  Vídeo de {m}m{s:02d}s = {base_seg}s em {PRECOS[args.base_modelo][1]}")
        print(f"                    + {args.vitrine}s de VITRINE em {vit_nome}")
        print(f"  Custo sem retrabalho: {fmt(custo_base)} cr")
        print(f"  ► RETRABALHO MÁXIMO TOLERADO: ×{max_retrab:.2f}"
              f"  ({(max_retrab-1)*100:.0f}% dos blocos podem ser regerados)")
        if max_retrab < 1.4:
            print("    ⚠ Abaixo do ×1,4 orçado. Encurtar o vídeo ou baixar a vitrine.")
        print("\n  A vitrine NÃO é o que decide: 1080p vs 720p nela muda ~75 cr (3% do vídeo).")
        print("  Quem decide é a DURAÇÃO do vídeo e o RETRABALHO REAL — meça e volte aqui.\n")
        return

    if args.tabela:
        saldo = args.saldo or 9000
        print(f"\nVÍDEOS DE 10 MIN (600s) QUE CABEM EM {fmt(saldo)} CRÉDITOS")
        print(f"(retrabalho ×{args.retrabalho})\n")
        print(f"  {'modelo':32} {'cr/vídeo':>10} {'c/ retrab':>11} {'vídeos/mês':>11}")
        print("  " + "-" * 68)
        for chave, (cr_s, nome, _teto) in PRECOS.items():
            por_video = 600 * cr_s
            com = por_video * args.retrabalho
            print(f"  {nome:32} {fmt(por_video):>10} {fmt(com):>11} {com and saldo / com:>11.2f}")
        print()
        return

    print("\nORÇAMENTO DO VÍDEO\n")
    total = 0.0
    segundos = 0
    if args.blocos:
        total += linha("único modelo", args.blocos, args.duracao, args.modelo, args.retrabalho)
        segundos += args.blocos * args.duracao
    if args.acao:
        total += linha("AÇÃO", args.acao, args.acao_duracao, args.acao_modelo, args.retrabalho)
        segundos += args.acao * args.acao_duracao
    if args.simples:
        total += linha("SIMPLES", args.simples, args.simples_duracao, args.simples_modelo,
                       args.retrabalho)
        segundos += args.simples * args.simples_duracao
    if not (args.blocos or args.acao or args.simples):
        raise SystemExit("Nada a orçar. Use --blocos, ou --acao/--simples, ou --tabela.")

    com_retrab = total * args.retrabalho
    USD_POR_CREDITO = 0.03  # Ultra 9.000/mês por US$ 270
    print(f"\n  DURAÇÃO DO VÍDEO: {segundos}s = {segundos // 60}m{segundos % 60:02d}s")
    print(f"  TOTAL sem retrabalho: {fmt(total)} cr")
    print(f"  TOTAL com retrabalho ×{args.retrabalho}: {fmt(com_retrab)} cr"
          f"  (~US$ {com_retrab * USD_POR_CREDITO:,.0f} por vídeo)")
    print("  (imagens de model sheet/storyboard: 1–2 cr cada — irrelevante no total)")

    if segundos < 480:
        print(f"\n  ⚠ {segundos // 60}m{segundos % 60:02d}s fica abaixo dos 8 min: perde o anúncio")
        print("    intermediário (regra da skill `postagem`, aula 13 [11:37]). Decisão do usuário,")
        print("    mas tem que aparecer no checkpoint.")

    if args.saldo:
        sobra = args.saldo - com_retrab
        print(f"\n  Saldo informado: {fmt(args.saldo)} cr")
        print(f"  Sobra depois deste vídeo: {fmt(sobra)} cr")
        if sobra < 0:
            print("  ⛔ NÃO CABE. Antes de gerar qualquer bloco, escolher uma saída:")
            print("     1) encurtar o vídeo (menos blocos)")
            print("     2) reclassificar blocos de AÇÃO para SIMPLES (modelo mais barato)")
            print("     3) baixar a resolução (o padrão do canal já é 480p + upscale na pós)")
            print("     4) comprar top-up de créditos")
        elif sobra < com_retrab * 0.15:
            print("  ⚠ Sobra menor que 15% do custo do vídeo: sem margem para regeração de emergência.")
        print(f"\n  Vídeos deste tamanho por mês com {fmt(args.saldo)} cr: {args.saldo / com_retrab:.2f}")
    print()


if __name__ == "__main__":
    main()
