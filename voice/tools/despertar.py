"""A palavra de ativação — quem decide se o OMEGA está sendo chamado.

POR QUE ISTO EXISTE. No motor Live o áudio vai direto ao Gemini, e o efeito
colateral apareceu no primeiro uso real: ele **respondeu a uma conversa da
sala que não era com ele** (o log pegou uma conversa sobre jogo, e o OMEGA
opinou). Fora o constrangimento, cada frase dessas é cota gratuita queimada.

A saída óbvia seria exigir a tecla, mas o Samuel escolheu "nome + tecla"
justamente porque nem sempre está na frente do PC. Então o nome precisa
funcionar também no Live — e para isso alguém tem que ouvir ANTES do Gemini.

MODELO `tiny`, e a escolha é medida, não intuição. Para achar UMA palavra
não é preciso o modelo grande:

    tiny    0,07 s/frase   achou o nome 6/6   0 falsos em 10 frases de sala
    base    0,30 s/frase   achou o nome 3/6   (pior que o tiny, e mais lento)
    small   0,56 s/frase   achou o nome 6/6

O `tiny` ganhou nos dois eixos. Ele custa ~75 MB e roda ao lado do modelo
grande sem incomodar.

O ÁUDIO NÃO SE PERDE: quando o nome é reconhecido, o trecho inteiro já
gravado é entregue a quem chamou. Sem isso, "Ômega, monta o vídeo da Medusa"
abriria o portão e perderia o comando, obrigando a repetir tudo — que é
exatamente a experiência que este trabalho todo existe para acabar.
"""

from __future__ import annotations

import unicodedata
from difflib import SequenceMatcher

import numpy as np

from .transcritor import VAD, DetectorDeFala, TAXA, _preparar_cuda

# As formas que os transcritores REALMENTE produzem para "Ômega" — observadas
# no log, não imaginadas.
#
# "amiga" e "nega" SAÍRAM da lista, e o motivo importa: elas entraram na época
# do Vosk, que destruía o nome. Com o Whisper elas voltaram a ser o que sempre
# foram — palavras portuguesas comuns. Medido: "a minha amiga falou que o
# filme é muito bom" acordava o OMEGA. Uma variante que também é palavra de
# verdade não é tolerância, é armadilha.
# (A semelhança delas com "omega" é 0,60 e 0,67, abaixo do LIMIAR, então sair
# da lista exata basta para não abrirem mais.)
NOMES = ("omega", "o mega", "omegas", "amega", "omeca", "omida", "omeda",
         "omena", "omeya", "omeja", "omeg")

# Quantas palavras podem vir antes do nome. O modelo gruda "é", "ó" e ruído
# no começo; exigir que o nome seja a PRIMEIRA palavra descartava a frase
# inteira em silêncio.
MARGEM = 3

# Abaixo disto a semelhança é coincidência. 0,75 foi calibrado com os erros
# reais; subir demais torna o OMEGA surdo ao próprio nome.
LIMIAR = 0.75

MODELO = "tiny"

_modelo = {"obj": None}


def _sem_acento(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto.lower())
                   if unicodedata.category(c) != "Mn")


def encontrar_nome(frase: str) -> tuple[bool, str]:
    """(chamaram?, o que veio depois do nome).

    Usada tanto aqui quanto pelo motor local, para haver UMA definição do que
    conta como "me chamaram".
    """
    palavras = (frase or "").split()
    if not palavras:
        return False, ""
    for i, palavra in enumerate(palavras[:MARGEM]):
        limpa = _sem_acento(palavra.strip(",.!?;:¿¡"))
        if limpa in NOMES or any(
            SequenceMatcher(None, limpa, nome).ratio() >= LIMIAR
            for nome in ("omega", "ômega")
        ):
            return True, " ".join(palavras[i + 1:]).strip(" ,.")
    return False, ""


def carregar():
    """Carrega o modelo pequeno da palavra de ativação (uma vez)."""
    if _modelo["obj"] is not None:
        return _modelo["obj"]
    _preparar_cuda()
    from faster_whisper import WhisperModel

    try:
        obj = WhisperModel(MODELO, device="cuda", compute_type="int8_float16")
        obj.transcribe(np.zeros(TAXA // 2, dtype=np.float32), language="pt")
    except Exception:  # noqa: BLE001 — sem GPU, na CPU o tiny ainda é rápido
        obj = WhisperModel(MODELO, device="cpu", compute_type="int8")
    _modelo["obj"] = obj
    return obj


def transcrever_curto(audio_int16: bytes) -> str:
    """Transcrição rápida e rasa — só para decidir se o nome está ali."""
    modelo = carregar()
    amostras = np.frombuffer(audio_int16, dtype=np.int16).astype(np.float32) / 32768.0
    if amostras.size < TAXA * 0.3:
        return ""
    segmentos, _ = modelo.transcribe(
        amostras,
        language="pt",
        # beam_size=1: é uma decisão binária, não vale pagar busca em feixe.
        beam_size=1,
        hotwords="Ômega",
        condition_on_previous_text=False,
        vad_filter=True,
        vad_parameters=VAD,
    )
    return " ".join(s.text for s in segmentos).strip()


class Portao:
    """Fica fechado até alguém chamar o OMEGA pelo nome.

    Enquanto fechado, nada chega ao Gemini. Aberto, tudo passa — é o que
    devolve a naturalidade da conversa contínua sem transformar o assistente
    num ouvinte de tudo que se fala na sala.
    """

    def __init__(self, ao_abrir=None):
        self.detector = DetectorDeFala(TAXA)
        self.ao_abrir = ao_abrir

    def alimentar(self, bloco: bytes) -> bytes | None:
        """Devolve o áudio a encaminhar quando o nome é reconhecido.

        None = não era para o OMEGA (ou a frase ainda não acabou).
        """
        trecho = self.detector.alimentar(bloco)
        if trecho is None:
            return None
        try:
            frase = transcrever_curto(trecho)
        except Exception:  # noqa: BLE001 — falha no portão não pode calar tudo
            return None
        if not frase:
            return None
        chamaram, _resto = encontrar_nome(frase)
        if not chamaram:
            return None
        if self.ao_abrir:
            self.ao_abrir(frase)
        # O trecho inteiro, e não só o que veio depois do nome: cortar o áudio
        # no meio da palavra estraga o que o Gemini vai ouvir, e ele lida bem
        # com o próprio nome no começo da frase.
        return trecho

    def limpar(self) -> None:
        self.detector.limpar()
