"""Testa o motor gratuito sem microfone: modelo Vosk carrega, Gemini
responde e a voz Maria fala. Rodar: python test_free.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from free_engine import MODELO_PT, FreeEngine  # noqa: E402


class UIFalsa:
    """Dublê da interface: guarda o log em vez de desenhar."""

    muted = False
    on_text_command = None
    linhas: list[str] = []

    def write_log(self, t):
        self.linhas.append(t)
        print("   log:", t)

    def set_state(self, s):
        pass


def main() -> int:
    falhas = []
    chaves = json.loads(
        (BASE_DIR / "config" / "api_keys.json").read_text(encoding="utf-8")
    )
    ui = UIFalsa()
    motor = FreeEngine(
        gemini_key=chaves.get("gemini_api_key", ""),
        instructions="Você é o ALPHA. Responda em uma frase curta, em português.",
        tool_executor=lambda n, a: "ok",
        ui=ui,
    )

    print("[1] modelo de voz (Vosk pt-BR)")
    if MODELO_PT.exists():
        try:
            from vosk import Model, SetLogLevel

            SetLogLevel(-1)
            Model(str(MODELO_PT))
            print("    OK — modelo carrega")
        except Exception as e:  # noqa: BLE001
            falhas.append(f"Vosk: {e}")
            print(f"    FALHA: {e}")
    else:
        falhas.append("modelo pt-br ausente")
        print("    FALHA: models/pt-br não existe")

    print("[2] cérebro (Gemini)")
    resposta = motor._perguntar_gemini("Diga apenas: sistemas operacionais.")
    print(f"    resposta: {resposta!r}")
    if not resposta or "recusou" in resposta or "Não consegui" in resposta:
        falhas.append(f"Gemini: {resposta}")

    print("[3] voz (SAPI Maria pt-BR)")
    try:
        motor.falar("Alpha operacional em modo gratuito.")
        print("    OK — falou sem erro")
    except Exception as e:  # noqa: BLE001
        falhas.append(f"TTS: {e}")
        print(f"    FALHA: {e}")

    print()
    if falhas:
        print("FALHAS:", falhas)
        return 1
    print("PASSOU: motor gratuito pronto (ouvir + pensar + falar)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
