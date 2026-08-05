"""Leitura do roteiro de narração (Documento 1) em blocos e linhas.

Formatos reais encontrados nos roteiros do canal (ago/2026):

- **Dullahan** — cabeçalhos de bloco explícitos:
      **[Blocos 2-3 — origem, registro de lenda]**
      Contam que houve um povo que dançava...
- **Dríade** — sem cabeçalho nenhum, só parágrafos separados por linha em branco.

O parser aceita os dois e REGISTRA qual modo usou (`origem`), porque a
diferença muda o que "bloco" significa lá na frente — nada é inventado em
silêncio.

Convenção importante: tudo que vem antes do primeiro `---` é nota de produção
(cabeçalho do documento, avisos de estrutura) e NÃO é narrado. É a mesma regra
que o Documento 4 usa ao colar no ElevenLabs.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .texto import Token, tokenizar

# **[Bloco 4 — o padre]** / [Blocos 2-3 — origem] / ## Bloco 7
_CABECALHO = re.compile(
    r"^\s*(?:\*{1,2})?\s*(?:#{1,6}\s*)?\[?\s*Bloco?s?\s+"
    r"(?P<numeros>\d+(?:\s*[-–]\s*\d+)?)"
    r"(?P<rotulo>[^\]\n]*)\]?\s*(?:\*{1,2})?\s*$",
    re.IGNORECASE,
)


@dataclass
class Linha:
    """Uma fala do roteiro — a unidade natural de legenda e de corte."""

    indice: int
    bloco: int
    texto: str
    tokens: list[Token] = field(default_factory=list)


@dataclass
class Bloco:
    numero: int
    rotulo: str
    linhas: list[int] = field(default_factory=list)
    # Quantos blocos de produção este grupo cobre. `[Blocos 2-3]` é UM grupo de
    # falas que corresponde a DOIS clipes — sem esse número, a conta de clipes
    # não fecha com a do roteiro.
    abrange: int = 1


@dataclass
class Roteiro:
    blocos: list[Bloco]
    linhas: list[Linha]
    origem: str  # "cabecalhos" | "paragrafos"

    @property
    def chaves(self) -> list[str]:
        """Todas as palavras normalizadas, na ordem — o lado esquerdo do alinhamento."""
        return [token.chave for linha in self.linhas for token in linha.tokens]


def _corpo_narrado(texto: str) -> list[str]:
    """Descarta o preâmbulo de produção e devolve as linhas narradas."""
    linhas = texto.splitlines()
    try:
        # Tudo antes do primeiro separador horizontal é nota de produção.
        inicio = next(i for i, l in enumerate(linhas) if l.strip() in ("---", "***", "___")) + 1
    except StopIteration:
        # Sem separador: descarta só o título H1, se houver.
        inicio = 1 if linhas and linhas[0].lstrip().startswith("# ") else 0
    return linhas[inicio:]


def _numero_do_cabecalho(numeros: str) -> tuple[int, int]:
    """'2-3' -> (2, 2 blocos cobertos). '4' -> (4, 1)."""
    partes = [int(p.strip()) for p in re.split(r"[-–]", numeros)]
    primeiro = partes[0]
    ultimo = partes[-1]
    return primeiro, max(1, ultimo - primeiro + 1)


def carregar(caminho_ou_texto: str, *, e_texto: bool = False) -> Roteiro:
    texto = caminho_ou_texto if e_texto else open(
        caminho_ou_texto, encoding="utf-8"
    ).read()

    blocos: list[Bloco] = []
    linhas: list[Linha] = []
    bloco_atual: Bloco | None = None
    tem_cabecalho = False
    paragrafo_aberto = False

    for bruta in _corpo_narrado(texto):
        crua = bruta.strip()

        if not crua:
            paragrafo_aberto = False
            continue
        if crua in ("---", "***", "___"):
            continue

        cabecalho = _CABECALHO.match(crua)
        if cabecalho:
            tem_cabecalho = True
            numero, abrange = _numero_do_cabecalho(cabecalho.group("numeros"))
            bloco_atual = Bloco(
                numero=numero, rotulo=crua.strip("*[] "), abrange=abrange
            )
            blocos.append(bloco_atual)
            paragrafo_aberto = False
            continue

        # Comentário/nota solta que sobrou depois do preâmbulo.
        if crua.startswith("#") or crua.startswith(">"):
            continue

        tokens = tokenizar(crua)
        if not tokens:
            continue

        # Sem cabeçalhos, cada parágrafo (bloco de linhas coladas) vira um bloco.
        if bloco_atual is None or (not tem_cabecalho and not paragrafo_aberto):
            bloco_atual = Bloco(numero=len(blocos) + 1, rotulo="")
            blocos.append(bloco_atual)

        linha = Linha(
            indice=len(linhas), bloco=len(blocos) - 1, texto=crua, tokens=tokens
        )
        linhas.append(linha)
        bloco_atual.linhas.append(linha.indice)
        paragrafo_aberto = True

    # Cabeçalho sem nenhuma fala embaixo (ex.: bloco só de nota) não deve
    # aparecer como bloco vazio no plano de edição. Reindexa as linhas junto,
    # senão linha.bloco aponta para a posição antiga da lista.
    sobreviventes = [i for i, b in enumerate(blocos) if b.linhas]
    novo_indice = {antigo: novo for novo, antigo in enumerate(sobreviventes)}
    blocos = [blocos[i] for i in sobreviventes]
    for linha in linhas:
        linha.bloco = novo_indice[linha.bloco]

    return Roteiro(
        blocos=blocos,
        linhas=linhas,
        origem="cabecalhos" if tem_cabecalho else "paragrafos",
    )
