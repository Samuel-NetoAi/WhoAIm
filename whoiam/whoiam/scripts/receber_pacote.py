#!/usr/bin/env python3
"""
Recebe o que a extensão baixou: renomeia, move para o destino certo e confere.

A extensão não tem acesso ao disco e não controla o nome do download. Ela só baixa, na ordem
do PACOTE.md. Este script lê a lista "ARQUIVOS ESPERADOS, NA ORDEM" do pacote, pega os arquivos
que chegaram em Downloads DEPOIS da criação do pacote, em ordem de chegada, e casa um a um.

Se a quantidade não bater, não move nada e mostra o que achou — conferir com o relatório da
extensão e rodar de novo com --pular (ex.: --pular 3 quando a imagem 3 foi recusada pelo filtro).

Uso:
  python receber_pacote.py --pacote "<pasta do bloco>\\_pacote_passo1\\PACOTE.md" --simular
  python receber_pacote.py --pacote "<...>\\PACOTE.md"
  python receber_pacote.py --pacote "<...>\\PACOTE.md" --pular 3
"""

import argparse
import datetime as dt
import re
import shutil
import sys
from pathlib import Path

IMAGEM = {".png", ".jpg", ".jpeg", ".webp"}
VIDEO = {".mp4", ".mov", ".webm"}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--pacote", required=True)
    ap.add_argument("--origem", default=str(Path.home() / "Downloads"))
    ap.add_argument("--pular", type=int, action="append", default=[],
                    help="número de item que não foi baixado (pode repetir)")
    ap.add_argument("--simular", action="store_true")
    a = ap.parse_args()

    texto = Path(a.pacote).read_text(encoding="utf-8")
    criado = dt.datetime.fromisoformat(re.search(r"^CRIADO EM:\s*(\S+)", texto, re.M).group(1))
    bloco = texto.split("## ARQUIVOS ESPERADOS, NA ORDEM", 1)[1]
    esperados = [(int(n), Path(c.strip())) for n, c in re.findall(r"^(\d+)\.\s*(C:\\.*)$", bloco, re.M)]
    esperados = [(n, c) for n, c in esperados if n not in a.pular]
    exts = VIDEO if all(c.suffix.lower() in VIDEO for _, c in esperados) else IMAGEM

    chegados = sorted((p for p in Path(a.origem).iterdir()
                       if p.is_file() and p.suffix.lower() in exts
                       and dt.datetime.fromtimestamp(p.stat().st_mtime) > criado),
                      key=lambda p: p.stat().st_mtime)

    print(f"Pacote criado em {criado:%d/%m %H:%M}. Esperados: {len(esperados)}. Chegaram depois: {len(chegados)}.")
    for p in chegados:
        print(f"   {dt.datetime.fromtimestamp(p.stat().st_mtime):%H:%M:%S}  {p.name}")
    if len(chegados) != len(esperados):
        print("\nQUANTIDADE NÃO BATE — nada foi movido. Conferir com o relatório da extensão "
              "(imagem recusada → --pular N; download a mais → apagar de Downloads) e rodar de novo.")
        sys.exit(1)

    for (n, destino), arq in zip(esperados, chegados):
        alvo = destino if arq.suffix.lower() == destino.suffix.lower() else destino.with_suffix(arq.suffix.lower())
        aviso = "" if alvo == destino else f"  (extensão {arq.suffix}, não {destino.suffix})"
        if alvo.exists():
            print(f"{n}. JÁ EXISTE, não sobrescrevi: {alvo}")
            continue
        if not a.simular:
            alvo.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(arq), alvo)
        print(f"{n}. {'moveria' if a.simular else 'OK'}: {arq.name} → {alvo}{aviso}")

    if not a.simular:
        faltam = [str(c) for n, c in esperados if not (c.exists() or any(c.with_suffix(e).exists() for e in IMAGEM | VIDEO))]
        print("\nConferência:", "todos os arquivos estão no destino." if not faltam else "FALTAM:\n- " + "\n- ".join(faltam))


if __name__ == "__main__":
    main()
