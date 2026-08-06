"""Verifica se o núcleo 3D realmente carrega dentro do QtWebEngine.

Abre só a cena numa janela, espera, e pergunta à própria página se o
three.js subiu (canvas com WebGL) ou se caiu no fallback offline.
Rodar: python test_nucleo.py
"""

from __future__ import annotations

import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from ui import NeuralScene, _WEBENGINE

SONDA = """
(() => {
  const c = document.querySelector('canvas');
  const gl = c && (c.getContext('webgl2') || c.getContext('webgl'));
  const fb = document.getElementById('fallback');
  return JSON.stringify({
    canvas: !!c,
    tamanho: c ? c.width + 'x' + c.height : null,
    webgl: !!gl,
    fallback: fb ? getComputedStyle(fb).display : '?',
    ponte: typeof window.omegaState
  });
})();
"""


def main() -> int:
    if not _WEBENGINE:
        print("FALHA: PyQt6-WebEngine não está instalado")
        return 1

    app = QApplication(sys.argv)
    cena = NeuralScene()
    cena.resize(900, 600)
    cena.show()

    resultado: dict = {}

    def sondar_inicial():
        cena.page().runJavaScript(SONDA, receber_inicial)

    def receber_inicial(bruto):
        resultado["inicial"] = bruto
        # O caso que quebrou de verdade: o widget cresce DEPOIS da carga
        # (o layout do Qt só dá o tamanho final mais tarde). O canvas tem
        # que acompanhar, senão a cena fica num quadrado no canto.
        cena.resize(1320, 780)
        QTimer.singleShot(2500, sondar_final)

    def sondar_final():
        cena.page().runJavaScript(SONDA, receber_final)

    def receber_final(bruto):
        resultado["final"] = bruto
        app.quit()

    QTimer.singleShot(9000, sondar_inicial)
    QTimer.singleShot(22000, app.quit)
    app.exec()

    inicial, final = resultado.get("inicial"), resultado.get("final")
    print("após carregar :", inicial)
    print("após redimens.:", final)
    if not inicial or not final:
        print("FALHA: a página não respondeu")
        return 1

    limpo = inicial.replace(" ", "")
    if '"fallback":"none"' not in limpo or '"webgl":true' not in limpo:
        print("FALHA: núcleo caiu no fallback (sem three.js)")
        return 1
    if '"1320x780"' not in final.replace(" ", ""):
        print("FALHA: o canvas não acompanhou o novo tamanho do widget")
        return 1
    print("PASSOU: núcleo 3D ativo e preenchendo o widget")
    return 0


if __name__ == "__main__":
    sys.exit(main())
