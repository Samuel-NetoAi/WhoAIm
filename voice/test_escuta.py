"""Mede a escuta do OMEGA: com viés de vocabulário contra sem.

Existe porque "melhorou" sem número é opinião. O experimento que aposentou o
Vosk foi exatamente este: gerar áudio das frases que o Samuel realmente fala,
transcrever, contar acertos.

DUAS FORMAS DE USAR:

  python test_escuta.py            -> áudio sintético (voz do Windows)
  python test_escuta.py gravacoes  -> os SEUS .wav, que é o que vale de fato

O áudio sintético é um piso, não uma prova: a voz do Windows articula melhor
que gente e não tem ruído de sala, então o acerto aqui sai otimista. Ele serve
para pegar regressão e para comparar as duas configurações entre si — o
número absoluto só tem valor com a sua voz. Para gravar as suas: fale cada
frase da lista e salve como `gravacoes/01.wav` ... na mesma ordem (16 kHz mono).
"""

from __future__ import annotations

import sys
import unicodedata
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# As frases que importam: nome do assistente, criaturas com nome estrangeiro
# (onde o modelo mais erra) e os comandos de verdade.
FRASES = [
    "Ômega, me mostra a pesquisa da Medusa",
    "Ômega, monta o vídeo do Cthullhu",
    "Ômega, lê o roteiro do Umibozu",
    "Ômega, quero as cenas do Orphanim",
    "Ômega, pesquisa sobre o Sobek",
    "Ômega, abre a pesquisa do Dullhan",
    "Ômega, me mostra os projetos",
    "Ômega, narra a pesquisa da Baba Yaga",
    "Ômega, faz o corte do Djin",
    "Ômega, como está o andamento da Driade",
    "Ômega, mostra a pesquisa do IT A Coisa",
    "Ômega, monta o vídeo dos Dragões Ocidentais",
]

# O que NÃO PODE errar em cada frase: acertar "me mostra" e perder "Medusa"
# é falhar. Só estas palavras entram na conta.
#
# São RADICAIS, não a palavra inteira: a pasta do Samuel é "Cthullhu" e a
# grafia corrente é "Cthulhu" — as duas resolvem para o mesmo projeto via
# `projetos.resolver`, então exigir uma delas mediria a minha grafia, não a
# escuta do OMEGA.
CRITICAS = [
    ("omega", "pesquisa", "medusa"),
    ("omega", "video", "cthul"),
    ("omega", "roteiro", "umibozu"),
    ("omega", "cenas", "orphanim"),
    ("omega", "pesquisa", "sobek"),
    ("omega", "pesquisa", "dullhan"),
    ("omega", "projetos"),
    ("omega", "narra", "baba", "yaga"),
    ("omega", "corte", "djin"),
    ("omega", "andamento", "driade"),
    ("omega", "pesquisa", "coisa"),
    ("omega", "video", "dragoes"),
]


def _sem_acento(t: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", t.lower())
        if unicodedata.category(c) != "Mn"
    )


def _acertos(ouvido: str, criticas: tuple[str, ...]) -> tuple[int, list[str]]:
    texto = _sem_acento(ouvido)
    perdidas = [p for p in criticas if p not in texto]
    return len(criticas) - len(perdidas), perdidas


def _gerar_audio(destino: Path) -> list[Path]:
    """Sintetiza as frases com a voz do Windows, a 16 kHz mono."""
    import pyttsx3

    destino.mkdir(parents=True, exist_ok=True)
    caminhos = []
    for i, frase in enumerate(FRASES, 1):
        alvo = destino / f"{i:02d}.wav"
        if not alvo.exists():
            # UM MOTOR POR ARQUIVO. Reusar o motor num laço trava o pyttsx3 no
            # segundo `runAndWait()` — o mesmo motivo pelo qual `falar()` cria
            # um motor por fala. Custa alguns segundos e não trava.
            motor = pyttsx3.init()
            for v in motor.getProperty("voices"):
                if "portug" in v.name.lower() or "brazil" in v.name.lower():
                    motor.setProperty("voice", v.id)
                    break
            motor.setProperty("rate", 165)
            motor.save_to_file(frase, str(alvo))
            motor.runAndWait()
            motor.stop()
            del motor
        caminhos.append(alvo)
        print(f"  áudio {i}/{len(FRASES)}", flush=True)
    return caminhos


# A conversão mora em tools/transcritor.py: a captura do som do PC precisa da
# mesma coisa, e duas cópias divergiriam. Este alias mantém o nome usado pelos
# outros testes.
from tools.transcritor import ler_wav_16k as _ler_wav_16k  # noqa: E402


def main() -> int:
    from tools import transcritor
    from tools import contexto_fala

    pasta = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("_audio_teste")
    proprias = len(sys.argv) > 1

    if proprias:
        arquivos = sorted(pasta.glob("*.wav"))
        if not arquivos:
            print(f"Nenhum .wav em {pasta}.")
            return 1
        print(f"Usando SUAS gravações: {len(arquivos)} arquivos de {pasta}.")
    else:
        print("Gerando áudio sintético (voz do Windows) — piso, não prova.")
        arquivos = _gerar_audio(pasta)

    print(contexto_fala.diagnostico().splitlines()[0])
    modelo, dispositivo = transcritor.carregar()
    print(f"Modelo: {transcritor.nome_do_modelo()} em {dispositivo.upper()}\n")

    placar = {True: 0, False: 0}
    total = 0
    for i, arq in enumerate(arquivos):
        if i >= len(CRITICAS):
            break
        audio = _ler_wav_16k(arq)
        criticas = CRITICAS[i]
        total += len(criticas)
        linha = []
        for viesar in (False, True):
            ouvido = transcritor.transcrever(audio, viesar=viesar)
            n, perdidas = _acertos(ouvido, criticas)
            placar[viesar] += n
            linha.append((n, perdidas, ouvido))
        (n0, p0, o0), (n1, p1, o1) = linha
        marca = "  " if n1 == n0 else ("^^" if n1 > n0 else "vv")
        print(f"{marca} [{i+1:02d}] {FRASES[i] if i < len(FRASES) else arq.name}")
        print(f"      sem viés {n0}/{len(criticas)}: {o0}")
        if o1 != o0:
            print(f"      COM viés {n1}/{len(criticas)}: {o1}")
        if p1:
            print(f"      ainda erra: {', '.join(p1)}")

    print(f"\n{'':4}palavras críticas: {total}")
    print(f"{'':4}sem viés : {placar[False]}/{total} "
          f"({100*placar[False]/max(total,1):.0f}%)")
    print(f"{'':4}COM viés : {placar[True]}/{total} "
          f"({100*placar[True]/max(total,1):.0f}%)")
    delta = placar[True] - placar[False]
    print(f"{'':4}diferença: {delta:+d} palavra(s)")
    if not proprias:
        print("\nEste número é otimista (voz sintética, sem ruído). "
              "Grave as suas em 'gravacoes/' e rode: python test_escuta.py gravacoes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
