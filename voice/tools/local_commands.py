"""Comandos de texto que rodam 100% local — sem OpenAI, sem internet.

Existem para que o Omega seja útil mesmo sem créditos na conta: ler o que as
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
from . import apagar as _apagar
from . import leitura as _leitura
from . import imagens as _imagens
from .projetos import frase_de_ajuda as _ajuda_projeto
from .projetos import resolver as _resolver_projeto

# Os nomes de comando são escolhidos para serem TRANSCRITOS bem, não para
# serem bonitos. Palavra estrangeira ("dossiê", "prompts", "short") sai
# deformada do reconhecimento — "dossiê" já virou "torcedor" e "doce e do
# lixo". A forma preferida é sempre a portuguesa comum; as estrangeiras
# continuam valendo para quem digita.
NOTE_ALIASES = {
    # dossiê -> diga "pesquisa"
    "pesquisa": "dossie",
    "pesquisas": "dossie",
    "dossie": "dossie",
    "dossier": "dossie",
    "dossiê": "dossie",
    # roteiro (palavra portuguesa, transcreve bem)
    "roteiro": "roteiro",
    "narracao": "roteiro",
    "narração": "roteiro",
    "texto": "roteiro",
    # prompts -> diga "cenas"
    "cenas": "prompts",
    "cena": "prompts",
    "imagens": "prompts",
    "prompts": "prompts",
    "prompt": "prompts",
}

AJUDA = """# Comandos (funcionam sem créditos)

> **Fale as palavras em NEGRITO.** Elas foram escolhidas por serem
> portuguesas e comuns — o reconhecimento de voz erra feio em palavra
> estrangeira ("dossiê" já virou *torcedor*). As formas em inglês continuam
> valendo quando você digita.

**Ver conteúdo**
- **`pesquisa <criatura>`** — exibe a pesquisa na tela *(= dossiê)*
- **`roteiro <criatura>`** — exibe o roteiro de narração
- **`cenas <criatura>`** — exibe as descrições de imagem *(= prompts)*
- **`video <criatura>`** — toca o último vídeo renderizado
- **`ler <criatura>`** — **lê a pesquisa em voz alta** (voz do Windows,
  para não gastar créditos da ElevenLabs); vale também "me lê o roteiro de X"
- **`parar`** — interrompe a leitura
- **`imagem <descrição>`** — gera uma imagem pela OpenAI e exibe
  *(precisa de saldo na conta OpenAI)*
- **`projetos`** — lista os projetos encontrados
- **`voltar`** — volta para o núcleo do OMEGA *(= hud)*
- **`diagnostico`** — o que esta máquina tem e o que falta

**Agir — edição**
- **`analisar <criatura>`** — monta o plano de edição
- **`montar <criatura>`** — renderiza o vídeo completo *(= renderizar)*
- **`corte <criatura>`** — renderiza a versão curta *(= short)*
- **`progresso`** — como estão os renders *(= status)*

**Agir — pesquisa e roteiro (dispara o Claude Code)**
- **`pesquisar <criatura>`** — produz a pesquisa (fase 0)
- **`produzir <criatura>`** — roteiro e cenas (fases 1–2)
- **`andamento`** — como vai a pesquisa em curso *(= pipeline)*

**Apagar** (sempre em dois passos, e vai para a lixeira)
- **`apagar projeto <criatura>`** → depois **`confirmar`** ou **`cancelar`**

> Repare na diferença: **`pesquisa X`** *lê* o que já existe;
> **`pesquisar X`** *produz* do zero (leva minutos).
"""


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFD", text.strip().lower())
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


def _slugify(value: str) -> str:
    text = _norm(value)
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def _pasta_da_criatura(creature: str) -> Path | None:
    """A pasta da criatura a partir de um nome possivelmente mal falado.

    Delega ao resolvedor tolerante: "e a coisas" e "it" chegam em
    "IT A Coisa". Continua devolvendo None (em vez de estourar) quando não
    dá para decidir — este módulo responde por frases faladas, e um
    traceback viraria silêncio na cara do usuário.
    """
    pasta, _ = _resolver_projeto(creature)
    return pasta


# Verbos que revelam intenção de OUVIR, não de ver. Vêm antes da
# palavra-chave na frase: "me lê a pesquisa da Medusa".
_VERBOS_DE_LEITURA = {"ler", "leia", "le", "lê", "leiame", "narrar", "narre",
                      "recitar", "recite", "ouvir", "escutar", "conta",
                      "conte", "fala", "fale"}


def _quer_ouvir(raw: str) -> bool:
    return any(_norm(p) in _VERBOS_DE_LEITURA for p in raw.split())


_VERBOS_DE_IMAGEM = {"imagem", "imagina", "desenha", "desenhar",
                     "ilustra", "ilustrar", "gerar-imagem"}


# Toda palavra-chave que inicia um comando com alvo. A ordem não importa:
# vence a que aparecer primeiro na frase.
_VERBOS_COM_ALVO = (
    _VERBOS_DE_LEITURA
    | _VERBOS_DE_IMAGEM
    | set(NOTE_ALIASES)
    | {"video", "vídeo", "assistir", "analisar", "analise", "analisa",
       "montar", "monta", "gerar", "gera", "renderizar", "renderiza", "render",
       "corte", "corta", "resumo", "short", "abrir", "abre",
       "apagar", "apaga", "deletar", "deleta", "remover", "remove",
       "pesquisar", "pesquise", "investigar", "investigue",
       "produzir", "produza", "roteirizar", "roteirize"}
)

# Preposições, artigos e substantivos genéricos que sobram grudados no alvo
# ("do it a coisa", "o video da medusa").
_LIXO_INICIAL = {"o", "a", "os", "as", "do", "da", "dos", "das", "de", "no",
                 "na", "em", "sobre", "para", "pra", "meu", "minha",
                 "video", "vídeo", "projeto", "arquivo", "pasta"}


def _extrair_verbo_e_alvo(raw: str) -> tuple[str, str] | None:
    """Acha a palavra-chave na frase e devolve (verbo, alvo).

    "me mostra a pesquisa do it a coisa" -> ("pesquisa", "it a coisa")
    Devolve None quando não há palavra-chave alguma — aí quem chama manda
    para o modelo de linguagem.
    """
    palavras = raw.split()

    def varrer(aceitas: set[str]) -> tuple[str, str] | None:
        for i, palavra in enumerate(palavras):
            verbo = _norm(palavra)
            if verbo not in aceitas:
                continue
            resto = palavras[i + 1:]
            # Tira artigos/preposições do começo do alvo, senão "do it a
            # coisa" e "it a coisa" viram buscas diferentes.
            while resto and _norm(resto[0]) in _LIXO_INICIAL:
                resto = resto[1:]
            alvo = " ".join(resto).strip()
            if alvo:
                return verbo, alvo
        return None

    # O QUE ele quer ver ganha de COMO ("abrir a pesquisa da Medusa" é pedido
    # de ver a pesquisa, não de abrir o navegador). Sem esta prioridade o
    # verbo genérico, por vir antes na frase, sequestrava o comando.
    return varrer(set(NOTE_ALIASES)) or varrer(_VERBOS_COM_ALVO)


def _read_note(creature: str, note: str) -> tuple[str, str] | str:
    """Devolve (titulo, conteudo) ou uma frase de erro."""
    pasta, candidatos = _resolver_projeto(creature)
    if pasta is None:
        # Melhor dizer quais existem do que só negar: o nome quase sempre
        # chegou deformado pelo reconhecimento de voz.
        return _ajuda_projeto(creature, candidatos)
    # Daqui em diante usa o nome REAL do projeto, não o que foi falado: se
    # "e a coisas" virou "IT A Coisa", o usuário precisa ver isso na tela
    # para confiar que abriu o certo.
    nome = pasta.name
    rotulos = {"dossie": "pesquisa", "roteiro": "roteiro", "prompts": "cenas"}
    caminho = pasta / f"{_slugify(nome)}-video" / "notes" / f"{note}.md"
    if caminho.exists():
        return (f"{rotulos[note]} — {nome}", caminho.read_text(encoding="utf-8"))
    return (
        f"Ainda não existe {rotulos[note]} para {nome}. "
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
    """Estado de cada peça de que o OMEGA depende, nesta máquina.

    Existe porque as duas máquinas do projeto têm capacidades diferentes e a
    falha silenciosa é o padrão: sem CLI, a pesquisa não roda; sem Studio, o
    render não roda; sem modelo Vosk, o microfone não roda. Melhor uma linha
    dizendo qual peça falta do que descobrir depois de esperar dez minutos.
    """
    from .pipeline import AI_PROJECT_ROOT as RAIZ_PIPELINE, _resolver_claude

    linhas: list[str] = ["# Diagnóstico do OMEGA", ""]
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

    if low in ("voltar", "inicio", "início", "tela", "hud", "rosto"):
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

    if low in ("progresso", "status", "situacao", "situação"):
        return studio_control({"action": "status"})

    # Confirmação de exclusão: vem antes de tudo para que um "confirmar" solto
    # nunca seja interpretado como outra coisa.
    if low in ("parar", "para", "chega", "silencio", "silêncio", "cala"):
        return _leitura.parar()

    if low in ("confirmar", "confirma", "confirmado", "pode apagar", "sim apaga"):
        return _apagar.confirmar()
    if low in ("cancelar", "cancela", "deixa", "esquece", "nao apaga", "não apaga"):
        return _apagar.cancelar()

    if low in ("andamento", "trabalho", "como esta", "como está", "pipeline"):
        return pipeline_criatura({"action": "status"})

    if low in ("diagnostico", "diagnóstico", "checar", "check"):
        titulo, doc, resumo = _diagnostico()
        ui.show_document(titulo, doc)
        return resumo

    # Comandos com argumento. Ninguém fala "pesquisa medusa" — fala "me
    # mostra a pesquisa da Medusa". Procuramos a palavra-chave em QUALQUER
    # posição e tomamos o resto como alvo; sem isso a frase inteira ia parar
    # no Gemini (que vive estourando a cota gratuita).
    achado = _extrair_verbo_e_alvo(raw)
    if achado is None:
        return None
    verbo, alvo = achado

    if verbo in _VERBOS_DE_LEITURA:
        # "lê a Medusa" sem dizer o quê: assume a pesquisa.
        resultado = _read_note(alvo, "dossie")
        if isinstance(resultado, str):
            return resultado
        titulo, conteudo = resultado
        ui.show_document(titulo, conteudo)
        return _leitura.ler(titulo, conteudo, ui)

    if verbo in NOTE_ALIASES:
        nota = NOTE_ALIASES[verbo]
        resultado = _read_note(alvo, nota)
        if isinstance(resultado, str):
            return resultado
        titulo, conteudo = resultado
        ui.show_document(titulo, conteudo)
        # "ler a pesquisa da Medusa" exibe E lê; "pesquisa da Medusa" só
        # exibe. A intenção de ouvir vem do verbo dito antes da palavra-chave.
        if _quer_ouvir(raw):
            return _leitura.ler(titulo, conteudo, ui)
        return f"{titulo} na tela."

    if verbo in _VERBOS_DE_IMAGEM:
        # "imagem da Medusa em pedra" -> gera e exibe. Se o texto
        # citar um projeto conhecido, a imagem é salva junto dele.
        pasta, _ = _resolver_projeto(alvo)
        return _imagens.gerar(alvo, pasta.name if pasta else None, ui)

    if verbo in ("video", "vídeo", "assistir"):
        caminho = _latest_render(alvo)
        if caminho is None:
            return f"Nenhum vídeo renderizado ainda para {alvo}."
        ui.show_video(f"vídeo — {alvo}", str(caminho))
        return f"Reproduzindo {caminho.name}."

    if verbo in ("analisar", "analise", "analisa"):
        return studio_control({"action": "analyze", "project": alvo})

    if verbo in ("montar", "monta", "gerar", "gera", "renderizar", "renderiza", "render"):
        return studio_control({"action": "render_full", "project": alvo})

    if verbo in ("corte", "corta", "resumo", "short"):
        return studio_control({"action": "render_short", "project": alvo})

    if verbo in ("abrir", "abre"):
        return studio_control({"action": "open", "project": alvo})

    if verbo in ("apagar", "apaga", "deletar", "deleta", "remover", "remove"):
        return _apagar.preparar(alvo)

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
