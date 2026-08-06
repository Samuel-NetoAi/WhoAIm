"""Apagar coisas do projeto por voz ou texto, com confirmação.

Duas travas, porque apagar por voz é o comando mais perigoso que o OMEGA
tem — um "apaga a Medusa" mal transcrito não pode destruir meses de trabalho:

1. NADA acontece sem uma segunda ordem explícita ("confirmar"). O primeiro
   comando só mostra o que seria apagado, com tamanho e contagem.
2. Nada é destruído de fato: vai para `_lixeira/<data>/` na raiz do projeto.
   Some da vista, continua recuperável até o usuário esvaziar.

Alvos aceitos (sempre DENTRO de C:\\Ai-Project — caminho fora disso é
recusado, mesmo que o modelo de voz peça):
  - "projeto <nome>"  -> a pasta inteira da criatura
  - "renders de <nome>" -> só os vídeos renderizados daquele projeto
"""

from __future__ import annotations

import shutil
import time
from datetime import datetime
from pathlib import Path

from .pipeline import AI_PROJECT_ROOT, _slugify
import unicodedata

LIXEIRA = AI_PROJECT_ROOT / "_lixeira"

# A confirmação expira: sem isto, um "confirmar" dito meia hora depois, em
# outro contexto, apagaria algo que o usuário nem lembra ter pedido.
VALIDADE_SEGUNDOS = 120

_pendente: dict = {}


def _tamanho(caminho: Path) -> tuple[int, int]:
    """(arquivos, bytes) de uma pasta ou arquivo."""
    if caminho.is_file():
        return 1, caminho.stat().st_size
    arquivos = [p for p in caminho.rglob("*") if p.is_file()]
    return len(arquivos), sum(p.stat().st_size for p in arquivos)


def _humano(bytes_: int) -> str:
    for unidade in ("B", "KB", "MB", "GB"):
        if bytes_ < 1024:
            return f"{bytes_:.0f} {unidade}"
        bytes_ /= 1024
    return f"{bytes_:.1f} TB"


def _normalizar(texto: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", texto.lower().strip())
        if unicodedata.category(c) != "Mn"
    ).replace(" ", "")


def _pasta_da_criatura(nome: str) -> Path | None:
    """Casa pelo NOME DA PASTA, nunca por apelido.

    Aqui NÃO se usa `mesma_criatura`: apelido serve para não pesquisar o
    mesmo ser duas vezes, mas em exclusão ele é perigoso — pedir "apaga o
    Pennywise" (pasta vazia) chegava a resolver para "IT A Coisa", que é
    onde estava a pesquisa de verdade.
    """
    raiz = AI_PROJECT_ROOT / "Criaturas"
    if not raiz.exists():
        return None
    alvo = _normalizar(nome)
    pastas = [p for p in raiz.iterdir() if p.is_dir()]

    for pasta in pastas:  # nome exato primeiro
        if _normalizar(pasta.name) == alvo:
            return pasta
    # Prefixo só serve se for de uma pasta só; senão é ambíguo demais para
    # uma operação destrutiva.
    parciais = [p for p in pastas if _normalizar(p.name).startswith(alvo)]
    return parciais[0] if len(parciais) == 1 else None


def _dentro_da_raiz(caminho: Path) -> bool:
    """Trava final: nunca tocar em nada fora de C:\\Ai-Project."""
    try:
        caminho.resolve().relative_to(AI_PROJECT_ROOT.resolve())
        return True
    except ValueError:
        return False


def preparar(alvo: str) -> str:
    """Primeiro passo: descreve o que seria apagado e guarda a pendência."""
    alvo = (alvo or "").strip()
    if not alvo:
        return "Apagar o quê, senhor? Diga 'apagar projeto <nome>'."

    baixo = alvo.lower()
    somente_renders = baixo.startswith(("renders", "render"))
    nome = alvo
    for prefixo in ("renders de ", "renders do ", "renders da ", "renders ",
                    "render de ", "projeto ", "a criatura ", "criatura "):
        if baixo.startswith(prefixo):
            nome = alvo[len(prefixo):].strip()
            break

    pasta = _pasta_da_criatura(nome)
    if not pasta:
        return f"Não achei projeto chamado {nome}."

    if somente_renders:
        caminho = pasta / f"{_slugify(pasta.name)}-video" / "renders"
        descricao = f"os renders de {pasta.name}"
    else:
        caminho = pasta
        descricao = f"o projeto {pasta.name} INTEIRO"

    if not caminho.exists():
        return f"Não existe {descricao} para apagar."
    if not _dentro_da_raiz(caminho):
        return "Recusado: esse caminho está fora da pasta de projetos."

    arquivos, bytes_ = _tamanho(caminho)
    _pendente.clear()
    _pendente.update({"caminho": caminho, "descricao": descricao, "em": time.monotonic()})

    if arquivos == 0:
        return (
            f"{descricao.capitalize()} está vazio. "
            "Diga 'confirmar' para remover a pasta."
        )
    return (
        f"Isso vai remover {descricao}: {arquivos} arquivo(s), {_humano(bytes_)}. "
        "Vai para a lixeira, dá para recuperar. Diga 'confirmar' para prosseguir "
        "ou 'cancelar' para desistir."
    )


def confirmar() -> str:
    """Segundo passo: move para a lixeira."""
    if not _pendente:
        return "Não há nada aguardando confirmação."
    if time.monotonic() - _pendente["em"] > VALIDADE_SEGUNDOS:
        alvo = _pendente["descricao"]
        _pendente.clear()
        return f"A confirmação para {alvo} expirou. Peça de novo, por segurança."

    caminho: Path = _pendente["caminho"]
    descricao: str = _pendente["descricao"]
    _pendente.clear()

    if not caminho.exists():
        return f"{descricao.capitalize()} já não existe."
    if not _dentro_da_raiz(caminho):
        return "Recusado: caminho fora da pasta de projetos."

    destino = LIXEIRA / datetime.now().strftime("%Y%m%d-%H%M%S") / caminho.name
    try:
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(caminho), str(destino))
    except Exception as e:  # noqa: BLE001 — vira frase falada
        return f"Não consegui mover para a lixeira: {str(e)[:100]}"

    return (
        f"Pronto. {descricao.capitalize()} foi para a lixeira, "
        f"em _lixeira, e pode ser recuperado de lá."
    )


def cancelar() -> str:
    if not _pendente:
        return "Não havia nada pendente."
    alvo = _pendente["descricao"]
    _pendente.clear()
    return f"Cancelado. {alvo.capitalize()} continua no lugar."


def ha_pendencia() -> bool:
    return bool(_pendente) and (
        time.monotonic() - _pendente["em"] <= VALIDADE_SEGUNDOS
    )
