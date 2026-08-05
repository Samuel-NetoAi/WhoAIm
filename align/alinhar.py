#!/usr/bin/env python
"""CLI do alinhamento: narração + roteiro → tempos, cortes e legendas.

    python alinhar.py --audio narracao.mp3 --roteiro notes/roteiro.md

Saídas em `analysis/` (ou onde `--saida` apontar):

    asr.json          transcrição bruta do Vosk (cache — ver abaixo)
    alignment.json    palavras, linhas e blocos com tempo e confiança
    captions.json     legendas em formato consumível pelo Studio/Remotion
    captions.<id>.srt legendas prontas para subir no YouTube

O `asr.json` é gravado como CACHE de propósito: a transcrição é a parte lenta,
e o alinhamento é a parte que vamos ajustar várias vezes. Com `--usar-cache` o
alinhamento inteiro re-roda em menos de um segundo, sem tocar no áudio.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from dataclasses import asdict
from pathlib import Path

from alpha_align import alinhador, asr as asr_mod, legendas as legendas_mod, roteiro as roteiro_mod

CONFIANCA_BAIXA = 0.35


def _carregar_asr(args, saida: Path) -> tuple[list[alinhador.PalavraASR], float]:
    cache = saida / "asr.json"

    if args.usar_cache and cache.is_file():
        dados = json.loads(cache.read_text(encoding="utf-8"))
        palavras = [alinhador.PalavraASR(**p) for p in dados["palavras"]]
        print(f"ASR lido do cache ({len(palavras)} palavras) — {cache}")
        return palavras, float(dados["duracao"])

    if not args.audio:
        sys.exit("Sem --audio e sem cache de ASR. Passe um dos dois.")

    audio = Path(args.audio)
    duracao = asr_mod.duracao_segundos(audio)
    print(f"Áudio: {audio.name} — {duracao:.1f}s")

    with tempfile.TemporaryDirectory() as tmp:
        wav = asr_mod.converter_para_wav16k(audio, Path(tmp) / "narracao16k.wav")
        print("Transcrevendo com Vosk (só para marcar o tempo)...")
        palavras = asr_mod.transcrever(wav, args.modelo)

    print(f"ASR: {len(palavras)} palavras reconhecidas")
    cache.write_text(
        json.dumps(
            {"duracao": duracao, "palavras": [asdict(p) for p in palavras]},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return palavras, duracao


def _relatorio(resultado: alinhador.Alinhamento, clipe_segundos: float) -> None:
    print()
    grupos = len(resultado.blocos)
    declarados = sum(b.abrange for b in resultado.blocos)
    resumo_blocos = f"{grupos} grupos"
    if declarados != grupos:
        # Cabeçalho "[Blocos 2-3]" é um grupo de falas para dois clipes — sem
        # isso a conta de material do canal (1 clipe por bloco) não fecha.
        resumo_blocos += f" cobrindo {declarados} blocos declarados"
    print(f"Blocos: {resumo_blocos} (origem: {resultado.origem_blocos})")
    print(f"Confiança global: {resultado.confianca:.0%} das palavras ancoradas")
    print()
    print(f"{'#':>3}  {'início':>8}  {'dur':>7}  {'conf':>5}  {'vs clipe':>9}  texto")
    print("-" * 92)

    for bloco in resultado.blocos:
        sobra = bloco.duracao - clipe_segundos * bloco.abrange
        if abs(sobra) < 0.75:
            veredito = "ok"
        elif sobra > 0:
            veredito = f"+{sobra:.1f}s❄"  # narração maior que o clipe = congela
        else:
            veredito = f"{sobra:.1f}s✂"  # clipe sobra e será cortado
        alerta = " ⚠" if bloco.confianca < CONFIANCA_BAIXA else "  "
        resumo = bloco.texto[:44].replace("\n", " ")
        etiqueta = f"{bloco.indice + 1}" + (f"×{bloco.abrange}" if bloco.abrange > 1 else "")
        print(
            f"{etiqueta:>3}  {bloco.t0:>8.2f}  {bloco.duracao:>6.2f}s  "
            f"{bloco.confianca:>4.0%}{alerta}{veredito:>9}  {resumo}"
        )

    fracos = [b for b in resultado.blocos if b.confianca < CONFIANCA_BAIXA]
    print()
    if fracos:
        print(
            f"⚠ {len(fracos)} bloco(s) com pouca âncora: "
            + ", ".join(str(b.indice + 1) for b in fracos)
        )
        print("  Nesses o tempo é estimado, não medido — confira antes de publicar.")
    else:
        print("Nenhum bloco abaixo do limite de confiança.")
    print(f"❄ = falta clipe (congelamento)   ✂ = sobra clipe (será cortado)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Alinha o roteiro de narração com o áudio e gera cortes e legendas.",
    )
    parser.add_argument("--audio", help="narração (mp3/wav/m4a)")
    parser.add_argument("--roteiro", required=True, help="notes/roteiro.md")
    parser.add_argument("--saida", default="analysis", help="pasta de saída")
    parser.add_argument("--modelo", help="pasta do modelo Vosk pt-BR")
    parser.add_argument("--idioma", default="pt", help="código do idioma nas legendas")
    parser.add_argument(
        "--clipe-segundos",
        type=float,
        default=15.0,
        help="duração dos clipes gerados, para o relatório de sobra/falta (padrão 15)",
    )
    parser.add_argument(
        "--usar-cache",
        action="store_true",
        help="reaproveita asr.json e pula a transcrição (iteração rápida)",
    )
    args = parser.parse_args()

    saida = Path(args.saida)
    saida.mkdir(parents=True, exist_ok=True)

    texto_roteiro = roteiro_mod.carregar(args.roteiro)
    print(
        f"Roteiro: {len(texto_roteiro.blocos)} blocos, "
        f"{len(texto_roteiro.linhas)} falas, {len(texto_roteiro.chaves)} palavras"
    )

    palavras_asr, duracao = _carregar_asr(args, saida)
    resultado = alinhador.alinhar(texto_roteiro, palavras_asr, duracao)

    (saida / "alignment.json").write_text(
        json.dumps(
            {
                "version": 1,
                "duracaoAudio": resultado.duracao_audio,
                "confianca": resultado.confianca,
                "origemBlocos": resultado.origem_blocos,
                "cortes": resultado.cortes,
                "blocos": [asdict(b) for b in resultado.blocos],
                "linhas": [asdict(l) for l in resultado.linhas],
                "palavras": [asdict(p) for p in resultado.palavras],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    legendas = legendas_mod.gerar(resultado)
    (saida / f"captions.{args.idioma}.srt").write_text(
        legendas_mod.para_srt(legendas), encoding="utf-8"
    )
    (saida / "captions.json").write_text(
        json.dumps(
            {
                "version": 1,
                "idioma": args.idioma,
                "legendas": [asdict(c) for c in legendas],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    _relatorio(resultado, args.clipe_segundos)
    print(f"\nGravado em {saida.resolve()}  ({len(legendas)} legendas)")


if __name__ == "__main__":
    main()
