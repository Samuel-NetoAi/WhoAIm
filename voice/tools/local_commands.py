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

from .studio import _find_project, _get_projects, _ensure_studio, _studio_alive, STUDIO_URL
from .studio import studio_control
# A raiz vem do pipeline para haver UMA fonte de verdade: ela respeita
# AI_PROJECT_ROOT, e ter duas constantes divergindo fazia o leitor de notas
# procurar num caminho e a pesquisa gravar em outro.
from .pipeline import AI_PROJECT_ROOT, pipeline_criatura

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
- `diagnostico` — o que esta máquina tem e o que falta
- `projetos` — lista os projetos encontrados
- `dossie <criatura>` — exibe a pesquisa aqui na tela
- `roteiro <criatura>` — exibe o roteiro de narração
- `prompts <criatura>` — exibe os prompts (model sheets, storyboards, Seedance)
- `video <criatura>` — toca o último vídeo renderizado, aqui mesmo
- `hud` — volta para o rosto do Alpha

**Agir — edição**
- `analisar <criatura>` — analisa clipes + narração e monta o plano de edição
- `renderizar <criatura>` — renderiza o vídeo completo
- `short <criatura>` — renderiza o Short
- `status` — progresso dos renders em andamento

**Agir — pesquisa e roteiro (dispara o Claude Code)**
- `pesquisar <criatura>` — monta o dossiê com a skill `pesquisa-seres` (fase 0)
- `produzir <criatura>` — roteiro e prompts com a skill `whoiam` (fases 1–2)
- `pipeline` — andamento da pesquisa/produção em curso

> Repare: `dossie X` **lê** o que já existe; `pesquisar X` **produz**.
> Leva minutos e exige o Claude Code instalado e logado neste computador.

**Com créditos na OpenAI**, é só falar naturalmente — sem decorar comando.
"""


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFD", text.strip().lower())
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


def _slugify(value: str) -> str:
    text = _norm(value)
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def _pasta_da_criatura(creature: str) -> Path | None:
    """A pasta da criatura, tolerante à grafia digitada.

    Devolve None em vez de estourar quando a raiz não existe — este módulo
    responde por frases faladas, e um traceback vira silêncio na cara do
    usuário. Acontece de verdade quando a máquina não é a do Windows ou o
    AI_PROJECT_ROOT está errado.
    """
    criaturas = AI_PROJECT_ROOT / "Criaturas"
    exata = criaturas / creature
    if exata.is_dir():
        return exata
    if not criaturas.is_dir():
        return None
    for d in criaturas.iterdir():
        if d.is_dir() and _norm(d.name) == _norm(creature):
            return d
    return None


def _read_note(creature: str, note: str) -> tuple[str, str] | str:
    """Devolve (titulo, conteudo) ou uma frase de erro."""
    pasta = _pasta_da_criatura(creature)
    candidates = []
    if pasta is not None:
        candidates.append(pasta / f"{_slugify(pasta.name)}-video" / "notes" / f"{note}.md")
    for path in candidates:
        if path.exists():
            return (f"{note} — {creature}", path.read_text(encoding="utf-8"))
    rotulo = {"dossie": "dossiê", "roteiro": "roteiro", "prompts": "prompts"}[note]
    return (
        f"Ainda não existe {rotulo} para {creature}. "
        f"Peça a pesquisa primeiro (ou gere pelo Claude)."
    )


def _latest_render(creature: str) -> Path | None:
    base = _pasta_da_criatura(creature)
    if base is None:
        return None
    renders = base / f"{_slugify(base.name)}-video" / "renders"
    if not renders.exists():
        return None
    videos = sorted(
        renders.glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True
    )
    return videos[0] if videos else None


def _diagnostico() -> tuple[str, str, str]:
    """Estado de cada peça de que o ALPHA depende, nesta máquina.

    Existe porque as duas máquinas do projeto têm capacidades diferentes e a
    falha silenciosa é o padrão: sem CLI, a pesquisa não roda; sem Studio, o
    render não roda; sem modelo Vosk, o microfone não roda. Melhor uma linha
    dizendo qual peça falta do que descobrir depois de esperar dez minutos.
    """
    from .pipeline import AI_PROJECT_ROOT as RAIZ_PIPELINE, _resolver_claude

    linhas: list[str] = ["# Diagnóstico do ALPHA", ""]
    problemas = 0

    def item(rotulo: str, ok: bool, detalhe: str) -> None:
        nonlocal problemas
        if not ok:
            problemas += 1
        linhas.append(f"- {'✅' if ok else '❌'} **{rotulo}** — {detalhe}")

    item(
        "Pasta dos projetos",
        RAIZ_PIPELINE.is_dir(),
        f"`{RAIZ_PIPELINE}`" + ("" if RAIZ_PIPELINE.is_dir() else " (defina AI_PROJECT_ROOT)"),
    )

    claude = _resolver_claude()
    item(
        "Claude Code CLI",
        claude is not None,
        f"`{claude}`" if claude else "não encontrado — `npm install -g @anthropic-ai/claude-code`",
    )

    estudio_vivo = _studio_alive()
    item(
        "Alpha Studio",
        estudio_vivo,
        f"respondendo em {STUDIO_URL}" if estudio_vivo else f"offline em {STUDIO_URL}",
    )

    if estudio_vivo:
        try:
            projetos = _get_projects()
            item("Projetos", bool(projetos), f"{len(projetos)} encontrado(s)")
        except Exception as e:  # noqa: BLE001
            item("Projetos", False, f"erro ao listar: {str(e)[:60]}")

    modelo = Path(__file__).resolve().parent.parent / "models" / "pt-br"
    item(
        "Modelo de voz (Vosk pt-BR)",
        modelo.is_dir(),
        f"`{modelo}`" if modelo.is_dir() else "ausente — só comandos digitados",
    )

    catalogo = RAIZ_PIPELINE / "Trilhas" / "catalogo.json"
    if catalogo.exists():
        try:
            import json as _json

            dados = _json.loads(catalogo.read_text(encoding="utf-8"))
            faixas = dados if isinstance(dados, list) else dados.get("faixas", [])
            item("Biblioteca de trilha", bool(faixas), f"{len(faixas)} faixa(s)")
        except Exception:  # noqa: BLE001
            item("Biblioteca de trilha", False, "catalogo.json ilegível")
    else:
        item(
            "Biblioteca de trilha",
            False,
            "sem catálogo — rode `npm run trilhas` no studio",
        )

    linhas.append("")
    linhas.append(
        "Tudo pronto." if problemas == 0 else f"{problemas} peça(s) faltando."
    )
    resumo = (
        "Diagnóstico na tela: tudo pronto."
        if problemas == 0
        else f"Diagnóstico na tela: {problemas} peça(s) faltando."
    )
    return ("diagnóstico", "\n".join(linhas), resumo)


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

    if low in ("pipeline", "pesquisa?", "andamento"):
        return pipeline_criatura({"action": "status"})

    if low in ("diagnostico", "diagnóstico", "checar", "check"):
        titulo, doc, resumo = _diagnostico()
        ui.show_document(titulo, doc)
        return resumo

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

    # Verbo = AGIR, substantivo = LER. "dossie X" mostra a pesquisa que já
    # existe; "pesquisar X" dispara o Claude Code para produzi-la. Sem essa
    # separação, "pesquisa X" abria o arquivo e parecia que a pesquisa tinha
    # falhado, quando na verdade ela nunca tinha sido iniciada.
    if verbo in ("pesquisar", "pesquise", "investigar", "investigue"):
        return pipeline_criatura(
            {"action": "start", "creature": alvo, "phase": "pesquisa"}
        )

    if verbo in ("produzir", "produza", "roteirizar", "roteirize"):
        return pipeline_criatura(
            {"action": "start", "creature": alvo, "phase": "producao"}
        )

    return None
