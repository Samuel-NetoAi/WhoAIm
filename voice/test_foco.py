"""Testa o gesto de palmas do ponto que falhava: a janela volta ao foco?

Abre a janela, MINIMIZA, chama o mesmo caminho que o detector de palmas usa
e pergunta ao Windows quem está em primeiro plano. Sem isto, o log dizia
"trazendo a janela para a frente" e nada acontecia.

ESTE TESTE DEPENDE DO AMBIENTE, e isso já custou uma caçada: ele falhou três
vezes seguidas logo depois de o `test_navegador.py --real` abrir o Chrome, e
voltou a passar cinco vezes seguidas com o Chrome fechado — mesmo código. O
Windows não deixa qualquer processo tomar o primeiro plano, e uma janela
recém-aberta de outro programa ganha a disputa. Por isso, ao falhar, ele diz
QUEM está com o foco: quase sempre a resposta está aí, e não no código.

Rodar: python test_foco.py   (de preferência sem outra janela abrindo junto)
"""

from __future__ import annotations

import ctypes
import os
import platform
import sys
from pathlib import Path

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ui import OmegaUI  # noqa: E402


def em_primeiro_plano(hwnd: int) -> bool:
    return ctypes.windll.user32.GetForegroundWindow() == hwnd


def quem_esta_na_frente() -> str:
    """O título da janela que ganhou o foco — o diagnóstico da falha."""
    try:
        u = ctypes.windll.user32
        hwnd = u.GetForegroundWindow()
        buf = ctypes.create_unicode_buffer(256)
        u.GetWindowTextW(hwnd, buf, 256)
        return buf.value or f"(sem título, hwnd {hwnd})"
    except Exception:  # noqa: BLE001
        return "(não consegui descobrir)"


def aprovado(r: dict) -> bool:
    return bool(
        r.get("minimizou") and not r.get("minimizada_depois") and r.get("em_foco")
    )


def relatar(r: dict) -> None:
    print(f"minimizou antes do gesto : {r.get('minimizou')}")
    print(f"ainda minimizada depois  : {r.get('minimizada_depois')}")
    print(f"em primeiro plano        : {r.get('em_foco')}")
    if not r.get("minimizou"):
        print("INCONCLUSIVO: a janela não chegou a minimizar.")
    elif r.get("minimizada_depois"):
        print("FALHA: continuou minimizada.")
    elif not r.get("em_foco"):
        print("FALHA: restaurou, mas não ficou em primeiro plano.")
        print(f"  quem está na frente: {r.get('ladrao_do_foco')}")
        print("  Se for outro programa (Chrome, terminal), é disputa de foco "
              "do Windows e não defeito — feche-o e rode de novo.")
    else:
        print("PASSOU: o gesto traz a janela de volta e com foco.")


def main() -> int:
    if platform.system() != "Windows":
        print("Teste específico do Windows.")
        return 0

    app = QApplication.instance() or QApplication(sys.argv)
    ui = OmegaUI(str(Path(__file__).resolve().parent / "face.png"))
    janela = ui._win
    resultado: dict = {}

    def minimizar():
        janela.showMinimized()
        QTimer.singleShot(1500, conferir_minimizada)

    def conferir_minimizada():
        resultado["minimizou"] = janela.isMinimized()
        # Mesmo caminho do gesto de palmas.
        ui.trazer_para_frente()
        QTimer.singleShot(1500, conferir_frente)

    def conferir_frente():
        resultado["minimizada_depois"] = janela.isMinimized()
        resultado["em_foco"] = em_primeiro_plano(int(janela.winId()))
        if not resultado["em_foco"]:
            resultado["ladrao_do_foco"] = quem_esta_na_frente()
        # Relata e encerra AQUI. Desmontar o QWebEngineView do núcleo derruba
        # o processo (0xC0000409) antes de qualquer print pós-exec, e o teste
        # ficava mudo mesmo tendo passado.
        relatar(resultado)
        sys.stdout.flush()
        os._exit(0 if aprovado(resultado) else 1)

    QTimer.singleShot(2500, minimizar)
    QTimer.singleShot(12000, app.quit)
    app.exec()

    # Se chegou aqui, o encerramento veio antes da sondagem.
    print("INCONCLUSIVO: o teste terminou sem medir.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
