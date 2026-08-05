"""Dispara as fases 0-2 do canal (pesquisa/roteiro/prompts) via Claude Code CLI.

O trabalho criativo pesado continua sendo do Claude (skills pesquisa-seres e
whoiam) — esta ferramenta só é a ponte por voz. Roda em thread própria porque
uma pesquisa completa leva minutos; o resultado cai em notes/ do projeto.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import threading
import unicodedata
from pathlib import Path

AI_PROJECT_ROOT = Path(r"C:\Ai-Project")


def _slugify(value: str) -> str:
    """Mesma regra do create-project.ts do Studio, para os caminhos baterem."""
    text = unicodedata.normalize("NFD", value.strip().lower())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def _project_dir(creature: str) -> Path:
    """Pasta que o Alpha Studio reconhece como projeto desta criatura.

    O Studio resolve notas em <root>\\Criaturas\\<Nome>\\<slug>-video\\notes,
    então a pesquisa precisa cair exatamente aí para aparecer na aba Notas.
    """
    return AI_PROJECT_ROOT / "Criaturas" / creature / f"{_slugify(creature)}-video"


def _ensure_project(creature: str) -> Path:
    project = _project_dir(creature)
    for sub in ("notes", "public/videos", "public/audio"):
        (project / sub).mkdir(parents=True, exist_ok=True)
    return project

# Estado do último pipeline disparado (um por vez é suficiente por voz).
_current: dict = {"running": False, "creature": None, "result": None}


def _run_claude(creature: str, phase: str) -> None:
    notes = _ensure_project(creature) / "notes"
    prompt = {
        "pesquisa": (
            f"Use a skill pesquisa-seres para montar o dossiê completo de {creature}. "
            f"Salve o dossiê final em {notes / 'dossie.md'}."
        ),
        "producao": (
            f"Use a skill whoiam para gerar o pacote de produção de {creature} "
            f"a partir do dossiê em {notes / 'dossie.md'}. "
            f"Salve o roteiro de narração em {notes / 'roteiro.md'} e todos os "
            f"prompts (model sheets, storyboards, Seedance) em {notes / 'prompts.md'}."
        ),
    }[phase]
    try:
        proc = subprocess.run(
            ["claude", "-p", prompt, "--permission-mode", "acceptEdits"],
            cwd=str(AI_PROJECT_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=1800,
            shell=True,
        )
        saida = (proc.stdout or "") + (proc.stderr or "")
        if proc.returncode == 0:
            onde = (
                "na aba Notas, em Dossiê"
                if phase == "pesquisa"
                else "na aba Notas, em Roteiro e Prompts"
            )
            _current["result"] = (
                f"Fase de {phase} de {creature} concluída. "
                f"O resultado está no projeto {creature} do Studio, {onde}."
            )
        elif "Not logged in" in saida or "/login" in saida:
            _current["result"] = (
                "O Claude Code está instalado mas não está logado. "
                "Abra um terminal, rode claude, e faça o login com sua conta. "
                "Depois disso essa função passa a funcionar."
            )
        else:
            _current["result"] = (
                f"Fase de {phase} de {creature} terminou com erro: {saida[-150:]}"
            )
    except subprocess.TimeoutExpired:
        _current["result"] = f"A fase de {phase} de {creature} passou de 30 minutos e foi interrompida."
    except Exception as e:  # noqa: BLE001 — vira frase falada, nunca crash
        _current["result"] = f"Falha ao rodar o Claude Code: {str(e)[:150]}"
    finally:
        _current["running"] = False


def pipeline_criatura(args: dict) -> str:
    action = (args.get("action") or "start").strip()

    if action == "status":
        if _current["running"]:
            return f"Ainda estou trabalhando na criatura {_current['creature']}."
        if _current["result"]:
            return _current["result"]
        return "Nenhum pipeline de criatura foi iniciado nesta sessão."

    creature = (args.get("creature") or "").strip()
    phase = (args.get("phase") or "pesquisa").strip()
    if not creature:
        return "Me diga o nome da criatura."
    if phase not in ("pesquisa", "producao"):
        return "A fase precisa ser pesquisa ou producao."

    if shutil.which("claude") is None:
        return (
            "O Claude Code CLI não está instalado neste computador, então não "
            "consigo disparar a pesquisa por voz ainda. Instale com: "
            "npm install -g @anthropic-ai/claude-code — depois disso essa "
            "função passa a funcionar."
        )

    if _current["running"]:
        return f"Já existe um pipeline rodando para {_current['creature']}. Pergunte o status."

    _current.update({"running": True, "creature": creature, "result": None})
    threading.Thread(target=_run_claude, args=(creature, phase), daemon=True).start()
    nome_fase = "pesquisa e dossiê" if phase == "pesquisa" else "roteiro e prompts"
    return (
        f"Iniciei a fase de {nome_fase} da criatura {creature} com o Claude. "
        "Isso leva alguns minutos; pergunte o status quando quiser."
    )
