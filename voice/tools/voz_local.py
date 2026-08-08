"""Voz sintetizada NESTA máquina — ElevenLabs, ou a Maria do Windows.

Existia dentro do `free_engine`, e o motor Live precisou da mesma coisa: ler
um documento em voz alta não pode passar pelo modelo. Um dossiê tem ~27 mil
caracteres; mandá-lo para o Gemini dizer queimaria a cota inteira para fazer
o que a máquina faz de graça — e, pior, o modelo resumiria em vez de LER.

Duas vozes, e a escolha é dinheiro:

  economico=True   Maria pt-BR (SAPI do Windows). Seca, grátis, ilimitada.
                   É a certa para documento longo.
  economico=False  ElevenLabs. Tem emoção, e é o que o Samuel quer ouvir numa
                   narração — mas ~1 crédito por caractere numa cota de 10 mil
                   por mês. Quem decide o custo é `tools/leitura.py`, que
                   pergunta antes quando o texto é grande.

Nunca fica mudo: sem chave, sem crédito ou com erro, cai para a Maria.
"""

from __future__ import annotations

import threading
import wave

import sounddevice as sd

# pyttsx3 não é seguro entre threads e trava quando o motor é reusado num
# laço (o `test_escuta` esbarrou nisso gerando áudio). Um motor por fala, e
# uma trava para os avisos que chegam de threads próprias não se atropelarem.
_trava = threading.Lock()


def _novo_motor():
    import pyttsx3

    motor = pyttsx3.init()
    for v in motor.getProperty("voices"):
        if "portug" in v.name.lower() or "maria" in v.name.lower():
            motor.setProperty("voice", v.id)
            break
    motor.setProperty("rate", 190)
    return motor


def _pela_elevenlabs(texto: str, log) -> bool:
    """True = falou. False = não deu; use a voz do Windows."""
    try:
        from . import elevenlabs_voz

        if not elevenlabs_voz.disponivel():
            return False
        arquivo = elevenlabs_voz.sintetizar(texto)
        if not arquivo:
            if elevenlabs_voz._estado["sem_credito"]:
                log("SYS: créditos da ElevenLabs acabaram — voltando à voz do Windows.")
            return False

        with wave.open(str(arquivo), "rb") as f:
            taxa, canais = f.getframerate(), f.getnchannels()
            dados = f.readframes(f.getnframes())

        # RawOutputStream evita depender do numpy e é o mesmo mecanismo do
        # resto do áudio aqui.
        stream = sd.RawOutputStream(samplerate=taxa, channels=canais, dtype="int16")
        stream.start()
        try:
            stream.write(dados)
        finally:
            stream.stop()
            stream.close()
        return True
    except Exception as e:  # noqa: BLE001 — qualquer falha volta para a Maria
        log(f"SYS: ElevenLabs falhou ({str(e)[:50]}) — voz local.")
        return False


def falar(texto: str, economico: bool = False, log=None) -> None:
    """Diz o texto pelos alto-falantes desta máquina. Bloqueia até terminar."""
    if not texto:
        return
    log = log or (lambda _m: None)
    with _trava:
        try:
            if not economico and _pela_elevenlabs(texto, log):
                return
            motor = _novo_motor()
            motor.say(texto)
            motor.runAndWait()
            motor.stop()
        except Exception as e:  # noqa: BLE001
            log(f"SYS: voz indisponível ({str(e)[:60]}) — sigo por texto.")
