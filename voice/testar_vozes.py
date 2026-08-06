"""Audição de vozes: fala a mesma frase com várias vozes da sua conta
ElevenLabs para você escolher a do OMEGA de ouvido.

Rodar:  python testar_vozes.py            (as candidatas do perfil JARVIS)
        python testar_vozes.py --todas    (todas as vozes da conta)
        python testar_vozes.py --listar   (só lista, não gasta crédito)

Ao escolher, ponha o id em "elevenlabs_voice_id" no config/api_keys.json —
ou peça para o Claude fazer isso.

ATENÇÃO: cada audição gasta créditos (≈1 por caractere). A frase é curta de
propósito; ouvir 5 vozes custa ~350 créditos dos 10.000 do mês.
"""

from __future__ import annotations

import sys
import wave
from pathlib import Path

import sounddevice as sd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tools import elevenlabs_voz as ev  # noqa: E402

FRASE = (
    "Boa noite, senhor. Sou o OMEGA. "
    "O render do Short da Medusa está em setenta por cento."
)


def tocar(caminho: Path) -> None:
    with wave.open(str(caminho), "rb") as f:
        taxa, canais = f.getframerate(), f.getnchannels()
        dados = f.readframes(f.getnframes())
    stream = sd.RawOutputStream(samplerate=taxa, channels=canais, dtype="int16")
    stream.start()
    try:
        stream.write(dados)
    finally:
        stream.stop()
        stream.close()


def main() -> int:
    if not ev.disponivel():
        print("Sem chave da ElevenLabs em config/api_keys.json.")
        return 1

    vozes = ev.listar_vozes()
    if not vozes:
        print("Não consegui listar as vozes (chave inválida ou sem rede?).")
        return 1

    print(f"{len(vozes)} vozes na conta.\n")
    if "--listar" in sys.argv:
        for v in vozes:
            extra = " · ".join(x for x in (v["genero"], v["sotaque"], v["descricao"]) if x)
            print(f"  {v['nome']:<18} {v['id']}   {extra}")
        print("\n(--listar não gasta crédito)")
        return 0

    if "--todas" in sys.argv:
        candidatas = vozes
    else:
        por_nome = {v["nome"].strip().lower(): v for v in vozes}
        candidatas = [por_nome[n] for n in ev.PREFERENCIA if n in por_nome]
        if not candidatas:
            candidatas = [v for v in vozes if v["genero"].lower() == "male"][:5]

    if not candidatas:
        print("Nenhuma candidata encontrada; tente --todas.")
        return 1

    custo = len(FRASE) * len(candidatas)
    print(f"Vou falar a mesma frase com {len(candidatas)} voz(es).")
    print(f"Custo estimado: ~{custo} créditos.\n")

    for i, v in enumerate(candidatas, 1):
        extra = " · ".join(x for x in (v["genero"], v["sotaque"]) if x)
        print(f"[{i}/{len(candidatas)}] {v['nome']}  ({extra})")
        print(f"        id: {v['id']}")
        # Força ESTA voz, ignorando a preferência/config.
        ev._estado["voz_resolvida"] = v["id"]
        wav = ev.sintetizar(FRASE)
        if not wav:
            print("        (falhou — sem crédito ou erro na API)\n")
            break
        tocar(wav)
        print()

    print("Escolha o id que soou melhor e ponha em 'elevenlabs_voice_id'.")
    print(ev.assinatura())
    return 0


if __name__ == "__main__":
    sys.exit(main())
