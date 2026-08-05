"""Comandos de texto que rodam 100% local — sem OpenAI, sem internet.

Existem para que o Alpha seja útil mesmo sem créditos na conta: ler o que as
skills geraram, listar projetos, abrir o vídeo renderizado, disparar render.
Tudo isso é arquivo local + a API do Studio em localhost, nada externo.

Quando há créditos, a voz continua sendo o caminho principal; estes comandos
ficam como atalho digitado. `handle()` devolve None quando não reconhece o
texto, e aí quem chama repassa para o modelo de voz.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from .studio import _find_project, _get_projects, _ensure_studio, STUDIO_URL
from .studio import studio_control

AI_PROJECT_ROOT = Path(r"C:\Ai-Project")

NOTE_ALIASES = {
    "dossie": "dossie",
    "dossier": "dossie",
    "pesquisa": "dossie",
    "roteiro": "roteiro",
    "narracao": "roteiro",
    "prompts": "prompts",
    "prompt": "prompts",
}

AJUDA = """# Comandos locais (funcionam sem créditos)

**Ver conteúdo**
- `projetos` — lista os projetos encontrados
- `dossie <criatura>` — exibe a pesquisa aqui na tela
- `roteiro <criatura>` — exibe o roteiro de narração
- `prompts <criatura>` — exibe os prompts (model sheets, storyboards, Seedance)
- `video <criatura>` — toca o último vídeo renderizado, aqui mesmo
- `hud` — volta para o rosto do Alpha

**Agir**
- `analisar <criatura>` — analisa clipes + narração e monta o plano de edição
- `renderizar <criatura>` — renderiza o vídeo completo
- `short <criatura>` — renderiza o Short
- `status` — progresso dos renders em andamento

**Com créditos na OpenAI**, é só falar naturalmente — sem decorar comando.
"""


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFD", text.strip().lower())
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


def _slugify(value: str) -> str:
    text = _norm(value)
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def _read_note(creature: str, note: str) -> tuple[str, str] | str:
    """Devolve (titulo, conteudo) ou uma frase de erro."""
    base = AI_PROJECT_ROOT / "Criaturas" / creature
    candidates = [base / f"{_slugify(creature)}-video" / "notes" / f"{note}.md"]
    # Se o usuário digitou o nome com grafia diferente da pasta, procura.
    if not base.exists():
        for d in (AI_PROJECT_ROOT / "Criaturas").iterdir():
            if _norm(d.name) == _norm(creature):
                candidates.insert(
                    0, d / f"{_slugify(d.name)}-video" / "notes" / f"{note}.md"
                )
                break
    for path in candidates:
        if path.exists():
            return (f"{note} — {creature}", path.read_text(encoding="utf-8"))
    rotulo = {"dossie": "dossiê", "roteiro": "roteiro", "prompts": "prompts"}[note]
    return (
        f"Ainda não existe {rotulo} para {creature}. "
        f"Peça a pesquisa primeiro (ou gere pelo Claude)."
    )


def _latest_render(creature: str) -> Path | None:
    base = AI_PROJECT_ROOT / "Criaturas" / creature
    if not base.exists():
        for d in (AI_PROJECT_ROOT / "Criaturas").iterdir():
            if _norm(d.name) == _norm(creature):
                base = d
                break
    renders = base / f"{_slugify(base.name)}-video" / "renders"
    if not renders.exists():
        return None
    videos = sorted(
        renders.glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True
    )
    return videos[0] if videos else None


def handle(text: str, ui) -> str | None:
    """Executa um comando local. Devolve a frase de resposta, ou None se o
    texto não for um comando local reconhecido."""
    raw = text.strip()
    low = _norm(raw)
    if not low:
        return None

    if low in ("ajuda", "help", "comandos", "?"):
        ui.show_document("ajuda", AJUDA)
        return "Comandos exibidos na tela."

    if low in ("hud", "voltar", "rosto"):
        ui.show_hud()
        return "De volta ao HUD."

    if low in ("projetos", "projetos?", "listar projetos", "lista de projetos"):
        err = _ensure_studio()
        if err:
            return err
        projetos = _get_projects()
        if not projetos:
            return "Nenhum projeto encontrado."
        linhas = [
            f"| {p['creatureName']} | {p['clipCount']} | "
            f"{'sim' if p['hasAudio'] else 'não'} | "
            f"{'sim' if p['hasEditPlan'] else 'não'} |"
            for p in projetos
        ]
        doc = (
            "# Projetos\n\n"
            "| Projeto | Clipes | Áudio | Plano |\n|---|---|---|---|\n"
            + "\n".join(linhas)
        )
        ui.show_document("projetos", doc)
        return f"{len(projetos)} projeto(s) na tela."

    if low == "status":
        return studio_control({"action": "status"})

    # Comandos com argumento: "<verbo> <criatura>"
    partes = raw.split(None, 1)
    if len(partes) < 2:
        return None
    verbo, alvo = _norm(partes[0]), partes[1].strip()

    if verbo in NOTE_ALIASES:
        nota = NOTE_ALIASES[verbo]
        resultado = _read_note(alvo, nota)
        if isinstance(resultado, str):
            return resultado
        titulo, conteudo = resultado
        ui.show_document(titulo, conteudo)
        return f"{titulo} na tela."

    if verbo in ("video", "vídeo", "assistir"):
        caminho = _latest_render(alvo)
        if caminho is None:
            return f"Nenhum vídeo renderizado ainda para {alvo}."
        ui.show_video(f"vídeo — {alvo}", str(caminho))
        return f"Reproduzindo {caminho.name}."

    if verbo in ("analisar", "analise", "analisa"):
        return studio_control({"action": "analyze", "project": alvo})

    if verbo in ("renderizar", "renderiza", "render"):
        return studio_control({"action": "render_full", "project": alvo})

    if verbo == "short":
        return studio_control({"action": "render_short", "project": alvo})

    if verbo in ("abrir", "abre"):
        return studio_control({"action": "open", "project": alvo})

    return None
