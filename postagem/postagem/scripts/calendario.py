#!/usr/bin/env python3
"""
Calendário de postagem do canal — gera os slots fixos e projeta a gaveta.

Existe porque data feita de cabeça erra em silêncio, e porque o número que
importa não é a lista de datas: é a semana em que a gaveta chega a zero com o
ritmo de produção real. Quebrar o padrão de frequência é o erro que o curso
repete em três aulas diferentes; este script mostra a quebra antes dela.

Uso:
  python3 calendario.py --inicio 2026-09-02 --dias qua,sab --hora 19:00 \
      --prontos 9 --producao-por-semana 2 --semanas 16

  # com os vídeos já nomeados, na ordem em que vão ao ar:
  python3 calendario.py --inicio 2026-09-02 --dias qua,sab --hora 19:00 \
      --prontos 9 --producao-por-semana 1.5 --fila "Dullahan,Baku,Wendigo"
"""

import argparse
from datetime import date, datetime, timedelta

DIAS = {
    "seg": 0, "ter": 1, "qua": 2, "qui": 3, "sex": 4, "sab": 5, "dom": 6,
    "segunda": 0, "terca": 1, "terça": 1, "quarta": 2, "quinta": 3,
    "sexta": 4, "sabado": 5, "sábado": 5, "domingo": 6,
}
NOME_DIA = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]


def parse_dias(txt):
    out = []
    for pedaco in txt.split(","):
        chave = pedaco.strip().lower()
        if chave not in DIAS:
            raise SystemExit(
                f"dia '{pedaco.strip()}' não reconhecido. "
                f"use: seg, ter, qua, qui, sex, sab, dom"
            )
        if DIAS[chave] not in out:
            out.append(DIAS[chave])
    return sorted(out)


def slots(inicio: date, dias_semana, semanas):
    """Todos os slots de postagem a partir de `inicio` (inclusive)."""
    fora = []
    # recua para a segunda-feira da semana de início, para varrer semana a semana
    cursor = inicio - timedelta(days=inicio.weekday())
    for semana in range(semanas + 1):
        for wd in dias_semana:
            d = cursor + timedelta(days=wd)
            if d >= inicio:
                fora.append((d, semana))
        cursor += timedelta(days=7)
    return fora


def main():
    p = argparse.ArgumentParser(description="Calendário de postagem e projeção de gaveta")
    p.add_argument("--inicio", required=True, help="data do primeiro vídeo (AAAA-MM-DD)")
    p.add_argument("--dias", required=True, help="dias fixos, ex: qua,sab")
    p.add_argument("--hora", default="19:00", help="horário fixo, ex: 19:00")
    p.add_argument("--prontos", type=int, default=0, help="vídeos já prontos na gaveta")
    p.add_argument("--producao-por-semana", type=float, default=0.0,
                   help="vídeos que você TERMINA por semana (o número honesto, não a meta)")
    p.add_argument("--semanas", type=int, default=16, help="horizonte da projeção")
    p.add_argument("--gaveta-minima", type=int, default=6,
                   help="abaixo disso o calendário alerta")
    p.add_argument("--fila", default="", help="criaturas na ordem, separadas por vírgula")
    args = p.parse_args()

    try:
        inicio = datetime.strptime(args.inicio, "%Y-%m-%d").date()
    except ValueError:
        raise SystemExit("--inicio precisa estar no formato AAAA-MM-DD")
    dias_semana = parse_dias(args.dias)
    fila = [c.strip() for c in args.fila.split(",") if c.strip()]

    por_semana = len(dias_semana)
    todos = slots(inicio, dias_semana, args.semanas)

    print(f"# Calendário de postagem")
    print(f"\nEstreia: {inicio.strftime('%d/%m/%Y')} ({NOME_DIA[inicio.weekday()]}) às {args.hora}")
    print(f"Dias fixos: {', '.join(NOME_DIA[d] for d in dias_semana)}  |  "
          f"{por_semana} vídeo(s)/semana")
    print(f"Gaveta na estreia: {args.prontos}  |  "
          f"produção real: {args.producao_por_semana:g}/semana")
    print(f"\nSaldo semanal: {args.producao_por_semana - por_semana:+g} vídeo(s)/semana\n")

    print("| # | Data | Dia | Hora | Vídeo | Gaveta depois |")
    print("|---:|---|---|---|---|---:|")

    gaveta = float(args.prontos)
    semana_atual = -1
    zera_em = None
    alerta_em = None

    for i, (d, semana) in enumerate(todos, start=1):
        if semana != semana_atual:
            if semana_atual >= 0:
                gaveta += args.producao_por_semana
            semana_atual = semana
        gaveta -= 1
        nome = fila[i - 1] if i - 1 < len(fila) else "— a definir —"
        marca = ""
        if gaveta < 0:
            marca = "  ⛔ SEM VÍDEO"
            if zera_em is None:
                zera_em = d
        elif gaveta < args.gaveta_minima:
            marca = "  ⚠️"
            if alerta_em is None:
                alerta_em = d
        print(f"| {i} | {d.strftime('%d/%m/%Y')} | {NOME_DIA[d.weekday()]} | "
              f"{args.hora} | {nome} | {gaveta:g}{marca} |")
        if gaveta < 0:
            break

    print()
    if zera_em:
        print(f"**A gaveta acaba em {zera_em.strftime('%d/%m/%Y')}.** Nessa data você não tem "
              f"vídeo para o slot — e reduzir a frequência é o erro que o curso repete em três "
              f"aulas (aula 10 [08:49]; aula 12 [02:20]; aula 13 [19:56]). Ou a produção sobe "
              f"para {por_semana}/semana antes disso, ou a estreia espera mais vídeos prontos.")
    elif alerta_em:
        print(f"**Atenção:** a gaveta cai abaixo de {args.gaveta_minima} em "
              f"{alerta_em.strftime('%d/%m/%Y')}. Ainda dá para corrigir sem quebrar o padrão.")
    else:
        print(f"Gaveta estável no horizonte de {args.semanas} semanas. "
              f"Se ela ficar em {args.gaveta_minima}+ por três semanas seguidas, é o gatilho "
              f"combinado para subir para {por_semana + 1}/semana — só para cima, nunca para baixo "
              f"(aula 10, [08:49]).")

    if args.producao_por_semana > por_semana:
        print(f"\nVocê produz mais do que publica (+{args.producao_por_semana - por_semana:g}"
              f"/semana). A gaveta cresce — é o cenário para considerar subir a frequência.")


if __name__ == "__main__":
    main()
