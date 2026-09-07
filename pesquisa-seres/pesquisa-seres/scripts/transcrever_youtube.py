#!/usr/bin/env python3
"""
Transcreve um vídeo do YouTube usando as legendas que o próprio YouTube gera.
Não baixa o vídeo — só puxa a legenda. Rápido e leve.

ONDE RODA: na sua máquina local ou no Claude Code (rede livre).
NÃO RODA no chat do Claude.ai — o container bloqueia youtube.com (403 host_not_allowed).

Dependência:  pip install youtube-transcript-api

Uso:
  python transcrever_youtube.py "<URL ou ID do vídeo>" --langs pt en
  python transcrever_youtube.py dQw4w9WgXcQ --langs pt en --out transcricao.txt
  python transcrever_youtube.py "<URL>" --timestamps
"""

import argparse
import re
import sys


def extrair_video_id(entrada: str) -> str:
    """Aceita URL completa (watch, youtu.be, shorts, embed) ou o ID puro."""
    padroes = [
        r"(?:v=|/videos/|embed/|youtu\.be/|/shorts/|/live/)([A-Za-z0-9_-]{11})",
        r"^([A-Za-z0-9_-]{11})$",
    ]
    for p in padroes:
        m = re.search(p, entrada)
        if m:
            return m.group(1)
    sys.exit(f"ERRO: não consegui extrair um ID de vídeo de: {entrada}")


def formatar_tempo(segundos: float) -> str:
    m, s = divmod(int(segundos), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def main() -> None:
    ap = argparse.ArgumentParser(description="Transcreve legendas de vídeo do YouTube.")
    ap.add_argument("video", help="URL ou ID do vídeo")
    ap.add_argument("--langs", nargs="+", default=["pt", "pt-BR", "en"],
                    help="Idiomas preferidos, em ordem (padrão: pt pt-BR en)")
    ap.add_argument("--out", help="Salvar em arquivo em vez de imprimir")
    ap.add_argument("--timestamps", action="store_true",
                    help="Incluir marcas de tempo (útil para localizar trecho)")
    args = ap.parse_args()

    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        from youtube_transcript_api._errors import (
            NoTranscriptFound, TranscriptsDisabled, VideoUnavailable,
        )
    except ImportError:
        sys.exit("ERRO: biblioteca ausente. Rode:  pip install youtube-transcript-api")

    video_id = extrair_video_id(args.video)
    api = YouTubeTranscriptApi()

    transcript = None
    try:
        # 1) Tenta os idiomas pedidos, na ordem.
        transcript = api.fetch(video_id, languages=args.langs)
    except NoTranscriptFound:
        # 2) Não há legenda nos idiomas pedidos: tenta traduzir uma existente.
        try:
            lista = api.list(video_id)
            for t in lista:
                if t.is_translatable:
                    alvo = args.langs[0].split("-")[0]
                    print(f"[aviso] Sem legenda em {args.langs}; traduzindo de "
                          f"'{t.language_code}' para '{alvo}'.", file=sys.stderr)
                    transcript = t.translate(alvo).fetch()
                    break
        except Exception:
            pass
    except (TranscriptsDisabled, VideoUnavailable) as e:
        sys.exit(f"SEM LEGENDA: {type(e).__name__} — este vídeo não tem transcrição "
                 f"automática disponível. Procure outro vídeo; não invente transcrição.")
    except Exception as e:
        sys.exit(f"ERRO de acesso ({type(e).__name__}): {str(e)[:200]}\n"
                 f"Se estiver rodando dentro do Claude.ai: youtube.com é bloqueado ali. "
                 f"Rode na sua máquina ou no Claude Code.")

    if transcript is None:
        sys.exit("SEM LEGENDA: nenhuma transcrição disponível nem traduzível para este "
                 "vídeo. Procure outro vídeo; não invente transcrição.")

    snippets = getattr(transcript, "snippets", transcript)
    linhas = []
    for s in snippets:
        texto = s.text.replace("\n", " ").strip()
        if not texto:
            continue
        if args.timestamps:
            linhas.append(f"[{formatar_tempo(s.start)}] {texto}")
        else:
            linhas.append(texto)

    resultado = ("\n" if args.timestamps else " ").join(linhas)
    cabecalho = f"# Transcrição — vídeo {video_id}\n# https://www.youtube.com/watch?v={video_id}\n\n"

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(cabecalho + resultado + "\n")
        print(f"Salvo em: {args.out} ({len(resultado)} caracteres)")
    else:
        print(cabecalho + resultado)


if __name__ == "__main__":
    main()
