"""O alinhamento em si: roteiro conhecido + transcrição imperfeita → tempos.

Premissa central (medida, não suposta): o ASR NÃO precisa acertar a
transcrição. Testado com Vosk pt-BR sobre voz sintética ruim, ele reconheceu
11 de ~25 palavras — mas as 11 vieram na ordem certa e no tempo certo. É disso
que o algoritmo vive: **âncoras**, não transcrição.

Como funciona:

1. As palavras do roteiro e as do ASR viram chaves normalizadas.
2. `difflib.SequenceMatcher` acha a maior subsequência comum — os trechos em
   que o ASR concordou com o roteiro. Cada palavra desses trechos vira uma
   ÂNCORA e recebe o tempo real medido no áudio.
3. As palavras entre duas âncoras são interpoladas proporcionalmente ao seu
   tamanho (palavra longa ocupa mais tempo que palavra curta).
4. Cada linha e cada bloco recebe um índice de confiança = proporção de
   palavras ancoradas. É esse número que diz ONDE olhar quando a legenda
   sair torta — em vez de reconferir o vídeo inteiro.

O texto final é SEMPRE o do roteiro. O ASR só empresta o relógio, nunca as
palavras — por isso um erro de reconhecimento não vira erro de legenda.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from difflib import SequenceMatcher

from .roteiro import Roteiro

# Âncora isolada de palavra curta ("de", "e", "que") é a fonte mais provável
# de casamento por acaso. Descartada quando não faz parte de um trecho maior.
TAMANHO_MINIMO_ANCORA_ISOLADA = 4

# Quanto uma âncora pode discordar da posição esperada, como fração da duração
# do áudio. A narração é lida em linha reta: a palavra que está a 30% do texto
# cai por volta de 30% do áudio. Uma âncora que viola isso casou com a
# ocorrência errada de uma palavra repetida ("lenda", "terra", "noite") — e uma
# só dessas arrasta todo o resto junto. Medido: sem esse filtro, transcrições
# muito ruins produzem erro mediano de dezenas de segundos.
BANDA_COERENCIA = 0.15

# Fração do áudio que as palavras reconhecidas precisam abranger para servirem
# de régua de posição (ver `_ancorar`).
COBERTURA_MINIMA_DA_FALA = 0.5


@dataclass
class PalavraASR:
    palavra: str
    chave: str
    t0: float
    t1: float
    conf: float = 1.0


@dataclass
class PalavraAlinhada:
    texto: str
    chave: str
    linha: int
    bloco: int
    t0: float
    t1: float
    ancora: bool
    # Posição na linha de origem — é por aqui que a legenda recupera o texto
    # original com pontuação (ver legendas.py).
    inicio: int = 0
    fim: int = 0


@dataclass
class Trecho:
    """Linha ou bloco já com tempo — o que o Studio e as legendas consomem."""

    indice: int
    texto: str
    t0: float
    t1: float
    confianca: float
    rotulo: str = ""
    linhas: list[int] = field(default_factory=list)
    abrange: int = 1  # quantos blocos/clipes de produção este trecho cobre

    @property
    def duracao(self) -> float:
        return round(self.t1 - self.t0, 3)


@dataclass
class Alinhamento:
    palavras: list[PalavraAlinhada]
    linhas: list[Trecho]
    blocos: list[Trecho]
    duracao_audio: float
    confianca: float
    origem_blocos: str

    @property
    def cortes(self) -> list[float]:
        """Limites de cena em segundos — 0, fim de cada bloco, fim do áudio."""
        if not self.blocos:
            return [0.0, self.duracao_audio]
        return [0.0] + [round(b.t1, 3) for b in self.blocos[:-1]] + [
            round(self.duracao_audio, 3)
        ]


def _peso(chave: str) -> float:
    """Quanto tempo esta palavra provavelmente ocupa, em unidades relativas.

    Contar caracteres é grosseiro mas robusto; contar sílabas exigiria um
    silabador pt-BR e o ganho só apareceria dentro de um vão já pequeno.
    O +1 impede que uma palavra de 1 letra receba tempo zero.
    """
    return len(chave) + 1.0


def _posicoes_relativas(chaves: list[str]) -> list[float]:
    """Onde cada palavra deve cair no áudio, de 0 a 1, se o ritmo for constante.

    Usa o mesmo peso da interpolação (tamanho da palavra), então a estimativa é
    coerente com o resto do algoritmo.
    """
    pesos = [_peso(c) for c in chaves]
    total = sum(pesos)
    posicoes: list[float] = []
    acumulado = 0.0
    for peso in pesos:
        posicoes.append((acumulado + peso / 2) / total)
        acumulado += peso
    return posicoes


def _ancorar(
    chaves_roteiro: list[str], asr: list[PalavraASR], duracao_audio: float
) -> dict[int, PalavraASR]:
    """Índice da palavra do roteiro → palavra do ASR que a confirma."""
    chaves_asr = [p.chave for p in asr]
    matcher = SequenceMatcher(None, chaves_roteiro, chaves_asr, autojunk=False)
    esperado = _posicoes_relativas(chaves_roteiro)

    # A posição relativa é medida dentro do TRECHO FALADO, não do arquivo:
    # narração costuma vir com silêncio no começo e no fim, e normalizar pela
    # duração total deslocaria todas as frações — rejeitando âncoras boas.
    inicio_fala = asr[0].t0 if asr else 0.0
    janela_fala = (asr[-1].t1 - inicio_fala) if asr else duracao_audio

    # ...mas só dá para chamar de "trecho falado" o que cobre boa parte do
    # áudio. Com meia dúzia de palavras reconhecidas num canto, o trecho não
    # descreve nada e a referência volta a ser o arquivo inteiro.
    if janela_fala < COBERTURA_MINIMA_DA_FALA * duracao_audio:
        inicio_fala, janela_fala = 0.0, duracao_audio

    ancoras: dict[int, PalavraASR] = {}
    for i, j, tamanho in matcher.get_matching_blocks():
        if tamanho == 0:
            continue
        for k in range(tamanho):
            indice = i + k
            palavra = asr[j + k]

            isolada = tamanho == 1
            if isolada and len(chaves_roteiro[indice]) < TAMANHO_MINIMO_ANCORA_ISOLADA:
                continue

            if janela_fala > 0:
                meio = (palavra.t0 + palavra.t1) / 2
                medido = (meio - inicio_fala) / janela_fala
                if abs(medido - esperado[indice]) > BANDA_COERENCIA:
                    continue

            ancoras[indice] = palavra
    return ancoras


def _interpolar(
    chaves: list[str],
    ancoras: dict[int, PalavraASR],
    duracao_audio: float,
) -> list[tuple[float, float]]:
    """Tempos de todas as palavras: medidos nas âncoras, estimados no resto."""
    total = len(chaves)
    tempos: list[tuple[float, float]] = [(0.0, 0.0)] * total

    indices_ancorados = sorted(ancoras)
    for i in indices_ancorados:
        tempos[i] = (ancoras[i].t0, ancoras[i].t1)

    # Cada vão é o intervalo entre duas âncoras (ou entre uma borda do áudio e
    # a primeira/última âncora), repartido proporcionalmente ao peso.
    bordas = [-1, *indices_ancorados, total]
    for esquerda, direita in zip(bordas, bordas[1:]):
        vao = list(range(esquerda + 1, direita))
        if not vao:
            continue

        inicio = tempos[esquerda][1] if esquerda >= 0 else 0.0
        fim = tempos[direita][0] if direita < total else duracao_audio
        if fim <= inicio:
            # Âncoras coladas (ou fora de ordem por ruído do ASR): distribui
            # um intervalo mínimo para não gerar duração negativa.
            fim = inicio + 0.001 * len(vao)

        pesos = [_peso(chaves[i]) for i in vao]
        soma = sum(pesos)
        cursor = inicio
        for i, peso in zip(vao, pesos):
            fatia = (fim - inicio) * (peso / soma)
            tempos[i] = (cursor, cursor + fatia)
            cursor += fatia

    return tempos


def _monotonizar(tempos: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Garante que o tempo nunca anda para trás (ASR devolve sobreposições)."""
    saida: list[tuple[float, float]] = []
    anterior = 0.0
    for t0, t1 in tempos:
        t0 = max(t0, anterior)
        t1 = max(t1, t0)
        saida.append((round(t0, 3), round(t1, 3)))
        anterior = t0
    return saida


def alinhar(
    roteiro: Roteiro, asr: list[PalavraASR], duracao_audio: float
) -> Alinhamento:
    chaves = roteiro.chaves
    if not chaves:
        raise ValueError("Roteiro sem nenhuma palavra narrada.")

    ancoras = _ancorar(chaves, asr, duracao_audio)
    tempos = _monotonizar(_interpolar(chaves, ancoras, duracao_audio))

    palavras: list[PalavraAlinhada] = []
    cursor = 0
    for linha in roteiro.linhas:
        for token in linha.tokens:
            t0, t1 = tempos[cursor]
            palavras.append(
                PalavraAlinhada(
                    texto=token.texto,
                    chave=token.chave,
                    linha=linha.indice,
                    bloco=linha.bloco,
                    t0=t0,
                    t1=t1,
                    ancora=cursor in ancoras,
                    inicio=token.inicio,
                    fim=token.fim,
                )
            )
            cursor += 1

    linhas = _agrupar(palavras, roteiro, por="linha")
    blocos = _agrupar(palavras, roteiro, por="bloco")

    return Alinhamento(
        palavras=palavras,
        linhas=linhas,
        blocos=blocos,
        duracao_audio=round(duracao_audio, 3),
        confianca=round(len(ancoras) / len(chaves), 3),
        origem_blocos=roteiro.origem,
    )


def _agrupar(
    palavras: list[PalavraAlinhada], roteiro: Roteiro, *, por: str
) -> list[Trecho]:
    chave_grupo = (lambda p: p.linha) if por == "linha" else (lambda p: p.bloco)
    total = len(roteiro.linhas) if por == "linha" else len(roteiro.blocos)

    trechos: list[Trecho] = []
    for indice in range(total):
        do_grupo = [p for p in palavras if chave_grupo(p) == indice]
        if not do_grupo:
            continue

        if por == "linha":
            texto = roteiro.linhas[indice].texto
            rotulo = ""
            linhas_do_trecho = [indice]
            abrange = 1
        else:
            bloco = roteiro.blocos[indice]
            texto = " ".join(roteiro.linhas[i].texto for i in bloco.linhas)
            rotulo = bloco.rotulo
            linhas_do_trecho = list(bloco.linhas)
            abrange = bloco.abrange

        ancoradas = sum(1 for p in do_grupo if p.ancora)
        trechos.append(
            Trecho(
                indice=indice,
                texto=texto,
                t0=do_grupo[0].t0,
                t1=do_grupo[-1].t1,
                confianca=round(ancoradas / len(do_grupo), 3),
                rotulo=rotulo,
                linhas=linhas_do_trecho,
                abrange=abrange,
            )
        )
    return trechos
