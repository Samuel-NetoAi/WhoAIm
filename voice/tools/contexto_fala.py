"""Diz ao Whisper, ANTES de ouvir, quais palavras esperar.

Isto é o que a literatura chama de *contextual biasing*, e é como assistentes
de produção resolvem vocabulário próprio sem retreinar nada
(arXiv:2410.18363). Vinha faltando aqui: o OMEGA transcrevia às cegas e
depois tentava consertar o estrago com um dicionário de erros observados
(`vocabulario.py`). Consertar depois é sempre pior do que guiar antes — uma
vez que o decoder escolheu "haiti é coisa", a informação de que era "IT A
Coisa" já se perdeu.

Duas alavancas, que o faster-whisper aplica no mesmo lugar (o slot `sot_prev`):

- `hotwords`: a lista de palavras que provavelmente vão aparecer. Nomes das
  criaturas em produção, o nome do assistente e os verbos de comando.
- `initial_prompt`: uma frase de exemplo no registro certo, para o decoder
  partir do domínio (produção de vídeo em português) e não do português geral.

TETO DE TOKENS: o faster-whisper corta `hotwords` em `max_length // 2` tokens
*sem avisar*, e ainda divide esse espaço com o `initial_prompt`. Uma lista que
cresce sozinha com o número de pastas encostaria nesse teto e passaria a
truncar em silêncio — as últimas criaturas simplesmente deixariam de ser
enviadas, e ninguém descobriria. Por isso o orçamento aqui é explícito e o
excesso é registrado, não engolido.
"""

from __future__ import annotations

import re
import unicodedata

from .projetos import listar_pastas
from .vocabulario import APELIDOS, CORRECOES

# O orçamento real é `max_length // 2` = 224 tokens, dividido com o
# initial_prompt (~35). Sobra folga, mas não a gastamos toda: lista longa
# demais dilui o viés em vez de reforçá-lo — a literatura é explícita em que
# biasing por prompt degrada com listas grandes.
MAX_TOKENS_HOTWORDS = 150

# ~1 token a cada 3,5 caracteres em português. Estimativa suficiente para um
# teto de segurança — o custo de errar para menos é zero.
_CHARS_POR_TOKEN = 3.5

# O registro em que o Samuel realmente fala com o OMEGA. Não é enfeite: o
# Whisper decodifica condicionado a este texto, então uma frase no domínio
# certo puxa a transcrição para o vocabulário certo.
INITIAL_PROMPT = (
    "Ômega, me mostra a pesquisa da Medusa. Ômega, monta o vídeo do Cthulhu. "
    "Ômega, lê o roteiro e as cenas da criatura."
)

# Pastas dentro de Criaturas/ que NÃO são criaturas. Sem isto elas comem o
# orçamento e, pior, enviesam a transcrição para palavras de ferramenta:
# "skill" passa a ser uma hipótese provável em toda frase.
_NAO_SAO_CRIATURAS = {"skill", "remotionskill", "remotion skill", "_lixeira"}

# Palavras do comando que não podem ser confundidas, porque errar uma delas
# derruba a frase inteira. Ficam antes dos nomes de criatura na lista.
_TERMOS_FIXOS = (
    "Ômega",
    "pesquisa", "roteiro", "cenas", "vídeo", "corte",
    "montar", "analisar", "pesquisar", "produzir",
    "projetos", "progresso", "andamento",
    "ler", "narrar", "parar", "imagem", "postar", "apagar", "confirmar",
)

_cache: dict = {"chave": None, "hotwords": ""}


def _sem_acento(texto: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )


def _nome_falado(pasta: str) -> str:
    """'DragõesOcidentais' -> 'Dragões Ocidentais'.

    O nome da PASTA é colado e sem espaço; o Whisper nunca vai produzir isso.
    O que ajuda o decoder é a forma como a palavra é FALADA.
    """
    com_espaco = re.sub(r"(?<=[a-zà-ÿ])(?=[A-ZÀ-Ý])", " ", pasta)
    return " ".join(com_espaco.replace("_", " ").replace("-", " ").split())


def _termos() -> list[str]:
    """Vocabulário do momento, do mais crítico ao mais dispensável.

    A ordem importa porque a cauda é o que morre no corte.
    """
    vistos: set[str] = set()
    saida: list[str] = []

    def juntar(termo: str) -> None:
        termo = termo.strip()
        chave = _sem_acento(termo.lower())
        if termo and chave not in vistos:
            vistos.add(chave)
            saida.append(termo)

    for t in _TERMOS_FIXOS:
        juntar(t)

    # As criaturas em produção AGORA — é o vocabulário que muda, e a razão
    # desta lista ser montada em tempo de execução em vez de escrita à mão.
    for pasta in listar_pastas():
        if _sem_acento(pasta.name.lower()) in _NAO_SAO_CRIATURAS:
            continue
        juntar(_nome_falado(pasta.name))

    # Grafias corretas que já sabemos que ele erra. Só as formas certas: as
    # variantes erradas continuam em vocabulario.py, como rede de segurança.
    for correta in CORRECOES:
        juntar(correta)
    for grupo in APELIDOS:
        for a in grupo:
            juntar(a)

    return saida


def _custo(termo: str) -> float:
    # +2 pelo ", " que separa os termos na string final.
    return (len(termo) + 2) / _CHARS_POR_TOKEN


def _cortar_no_orcamento(termos: list[str]) -> tuple[list[str], list[str]]:
    """Devolve (cabem, sobraram). Nunca trunca em silêncio."""
    cabem: list[str] = []
    gasto = 0.0
    for i, termo in enumerate(termos):
        if gasto + _custo(termo) > MAX_TOKENS_HOTWORDS:
            return cabem, termos[i:]
        cabem.append(termo)
        gasto += _custo(termo)
    return cabem, []


def _chave_do_cache() -> tuple:
    """Muda quando as pastas mudam — só então vale remontar a lista."""
    try:
        return tuple(sorted(p.name for p in listar_pastas()))
    except Exception:  # noqa: BLE001 — disco fora do ar não pode matar a escuta
        return ()


def hotwords(forcar: bool = False) -> str:
    """A string de viés para passar ao `transcribe()`."""
    chave = _chave_do_cache()
    if not forcar and _cache["chave"] == chave:
        return _cache["hotwords"]

    cabem, sobraram = _cortar_no_orcamento(_termos())
    texto = ", ".join(cabem)
    _cache.update({"chave": chave, "hotwords": texto, "sobraram": sobraram})
    return texto


def diagnostico() -> str:
    """O que está sendo enviado ao Whisper — e o que ficou de fora."""
    texto = hotwords(forcar=True)
    sobraram = _cache.get("sobraram") or []
    linhas = [
        f"Viés de vocabulário: {len(texto.split(', '))} termos, "
        f"~{int(sum(_custo(t) for t in texto.split(', ')))} "
        f"de {MAX_TOKENS_HOTWORDS} tokens.",
        texto,
    ]
    if sobraram:
        linhas.append(
            f"FORA (estourou o teto): {', '.join(sobraram)} — "
            "suba MAX_TOKENS_HOTWORDS ou tire termos fixos."
        )
    return "\n".join(linhas)
