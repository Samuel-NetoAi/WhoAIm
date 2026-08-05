"""Dispara as fases 0-2 do canal (pesquisa/roteiro/prompts) via Claude Code CLI.

O trabalho criativo pesado continua sendo do Claude (skills pesquisa-seres e
whoiam) — esta ferramenta só é a ponte por voz. Roda em thread própria porque
uma pesquisa completa leva minutos; o resultado cai em notes/ do projeto.
"""

from __future__ import annotations

import os
import platform
import re
import shutil
import subprocess
import threading
import time
import unicodedata
from pathlib import Path

from .notify import batimento, duracao_falada, notificar

# Mesma variável que o Studio usa (lib/projects/constants.ts), para as duas
# metades do sistema concordarem sobre onde os projetos vivem. O padrão é a
# máquina principal; no Linux, exportar AI_PROJECT_ROOT.
AI_PROJECT_ROOT = Path(os.environ.get("AI_PROJECT_ROOT") or r"C:\Ai-Project")

E_WINDOWS = platform.system() == "Windows"

# Onde procurar o CLI, do mais provável ao menos. No Windows o npm instala um
# .CMD que só o PATH resolve; no Linux/macOS o instalador global costuma cair
# em ~/.local/bin.
def _resolver_claude() -> str | None:
    do_path = shutil.which("claude")
    if do_path:
        return do_path
    candidatos = [
        Path.home() / ".local" / "bin" / "claude",
        Path.home() / ".claude" / "local" / "claude",
        Path.home() / ".npm-global" / "bin" / "claude",
    ]
    if E_WINDOWS:
        appdata = os.environ.get("APPDATA")
        if appdata:
            candidatos.insert(0, Path(appdata) / "npm" / "claude.CMD")
    for c in candidatos:
        if c.exists():
            return str(c)
    return None


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


def _arquivos_da_fase(creature: str, phase: str) -> list[Path]:
    """O que cada fase promete gravar — usado para conferir se de fato gravou."""
    notes = _project_dir(creature) / "notes"
    if phase == "pesquisa":
        return [notes / "dossie.md"]
    return [notes / "roteiro.md", notes / "prompts.md"]


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
    executavel = _resolver_claude() or "claude"
    rotulo = "pesquisa" if phase == "pesquisa" else "roteiro e prompts"
    inicio = time.monotonic()

    # Sinal de vida: sem isto, uma pesquisa de dez minutos parece um travamento.
    batimento(
        120,
        lambda d: f"Ainda trabalhando na {rotulo} de {creature} — {duracao_falada(d)} até agora.",
        lambda: _current["running"],
    )

    try:
        proc = subprocess.run(
            [executavel, "-p", prompt, "--permission-mode", "acceptEdits"],
            cwd=str(AI_PROJECT_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=1800,
            # shell=True só no Windows, onde o npm instala um .CMD que precisa
            # do interpretador. No POSIX, shell=True com LISTA roda
            # `sh -c "claude"` e joga fora todos os argumentos seguintes — o
            # prompt sumiria e o Claude abriria em modo interativo, travando
            # até o timeout de 30 minutos.
            shell=E_WINDOWS,
        )
        saida = (proc.stdout or "") + (proc.stderr or "")
        levou = duracao_falada(time.monotonic() - inicio)

        if proc.returncode == 0:
            # Os arquivos são gravados DENTRO da pasta do projeto, que é de onde
            # o Studio lê — então "gravou" e "chegou no Studio" são a mesma
            # coisa. Dizer o arquivo por nome poupa procurar.
            arquivos = _arquivos_da_fase(creature, phase)
            escritos = [a for a in arquivos if a.exists()]
            onde = (
                "na aba Notas, em Dossiê"
                if phase == "pesquisa"
                else "na aba Notas, em Roteiro e Prompts"
            )
            if escritos:
                lista = ", ".join(a.name for a in escritos)
                _current["result"] = (
                    f"{rotulo.capitalize()} de {creature} concluída em {levou}. "
                    f"Gravei {lista} no projeto — já aparece no Studio, {onde}."
                )
            else:
                # Saiu com código 0 mas não escreveu nada: dizer "concluído"
                # aqui seria mentira, e é o tipo de mentira que só se descobre
                # abrindo a aba Notas e achando-a vazia.
                _current["result"] = (
                    f"O Claude terminou a {rotulo} de {creature} em {levou}, mas "
                    "não encontrei os arquivos esperados no projeto. "
                    "Confira a aba Notas antes de seguir."
                )
        elif "Not logged in" in saida or "/login" in saida:
            _current["result"] = (
                "O Claude Code está instalado mas não está logado. "
                "Abra um terminal, rode claude, e faça o login com sua conta. "
                "Depois disso essa função passa a funcionar."
            )
        else:
            _current["result"] = (
                f"A {rotulo} de {creature} terminou com erro: {saida[-150:]}"
            )
    except subprocess.TimeoutExpired:
        _current["result"] = (
            f"A {rotulo} de {creature} passou de 30 minutos e foi interrompida."
        )
    except Exception as e:  # noqa: BLE001 — vira frase falada, nunca crash
        _current["result"] = f"Falha ao rodar o Claude Code: {str(e)[:150]}"
    finally:
        _current["running"] = False
        # Marco: este é o aviso que o usuário está esperando, então fala.
        notificar(_current["result"], falar=True)


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

    if _resolver_claude() is None:
        return (
            "O Claude Code CLI não está instalado neste computador, então não "
            "consigo disparar a pesquisa ainda. Instale com: "
            "npm install -g @anthropic-ai/claude-code — depois disso essa "
            "função passa a funcionar. (O app de desktop do Claude não serve: "
            "o que a ferramenta chama é o comando de terminal.)"
        )

    if not AI_PROJECT_ROOT.is_dir():
        return (
            f"A pasta dos projetos não existe em {AI_PROJECT_ROOT}. "
            "Aponte a variável AI_PROJECT_ROOT para a pasta certa antes."
        )

    if _current["running"]:
        return f"Já existe um pipeline rodando para {_current['creature']}. Pergunte o status."

    _current.update({"running": True, "creature": creature, "result": None})
    threading.Thread(target=_run_claude, args=(creature, phase), daemon=True).start()
    nome_fase = "pesquisa e dossiê" if phase == "pesquisa" else "roteiro e prompts"
    return (
        f"Iniciei a fase de {nome_fase} da criatura {creature} com o Claude. "
        "Leva alguns minutos — vou avisando o andamento e falo quando terminar."
    )
