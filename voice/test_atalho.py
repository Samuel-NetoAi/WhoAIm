"""Verifica o atalho global (Ctrl+Espaço) até onde é honestamente verificável.

O QUE ESTE TESTE PROVA:
  1. a tecla é registrada no Windows (e o registro é exclusivo — dois OMEGA
     abertos não brigam calados pela mesma tecla);
  2. o caminho da thread do atalho até a thread da UI funciona — é a parte
     perigosa, porque tocar em widget da thread errada trava o Qt;
  3. a tecla é DEVOLVIDA ao fechar. Sem isso ela fica presa até o Windows
     reiniciar e a próxima execução do OMEGA perde o atalho em silêncio.

O QUE ELE NÃO PROVA: o aperto físico. Entrada sintética (`SendInput`,
`keybd_event`) não dispara hotkey global neste ambiente — testado, chega zero
WM_HOTKEY mesmo com o registro bem-sucedido. Então a última milha é sua:
abra o OMEGA, aperte Ctrl+Espaço com a janela em segundo plano e veja a linha
"Ctrl+Espaço — pode falar" no log.

Foi por causa deste teste que o crash apareceu: a primeira versão colhia o
WM_HOTKEY em `nativeEvent`, que o Qt chama para toda mensagem do Windows, e
o app morria com 0xC000041D e log vazio.
"""

from __future__ import annotations

import ctypes
import platform
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

if platform.system() != "Windows":
    print("PULADO: atalho global só existe no Windows.")
    raise SystemExit(0)

from PyQt6.QtCore import QTimer  # noqa: E402
from PyQt6.QtWidgets import QApplication  # noqa: E402

import ui as ui_mod  # noqa: E402

MOD_CONTROL, MOD_NOREPEAT, VK_SPACE = 0x0002, 0x4000, 0x20


def _tecla_esta_livre(ident: int = 0xA17B) -> bool:
    """True se ninguém está com o Ctrl+Espaço."""
    u = ctypes.windll.user32
    if u.RegisterHotKey(None, ident, MOD_CONTROL | MOD_NOREPEAT, VK_SPACE):
        u.UnregisterHotKey(None, ident)
        return True
    return False


def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    janela = ui_mod.MainWindow(str(Path("face.png")))
    janela.show()
    app.processEvents()

    falhas = []

    # 1) registro
    disparos = []
    registrado = janela.registrar_atalho_global(lambda: disparos.append(1))
    print(f"[1] registrou a tecla            : {registrado}")
    if not registrado:
        print("    PULADO: outro programa já usa Ctrl+Espaço nesta máquina.")
        janela._encerrar_atalho()
        return 0

    # 2) exclusividade: enquanto o OMEGA a tem, ninguém mais consegue
    livre_durante = _tecla_esta_livre()
    print(f"[2] tecla ocupada enquanto ativa : {not livre_durante}")
    if livre_durante:
        falhas.append("a tecla não ficou reservada — dois OMEGA brigariam por ela")

    # 3) o pulo do gato: da thread do atalho para a thread da UI
    threading.Thread(target=janela._atalho_sig.emit, daemon=True).start()
    fim = time.time() + 3
    while not disparos and time.time() < fim:
        app.processEvents()
        time.sleep(0.02)
    print(f"[3] chegou na thread da UI       : {bool(disparos)}")
    if not disparos:
        falhas.append("o sinal da thread do atalho não chegou à UI")

    # 4) devolução
    janela._encerrar_atalho()
    janela.close()
    app.processEvents()
    livre_depois = _tecla_esta_livre()
    print(f"[4] devolveu a tecla ao fechar   : {livre_depois}")
    if not livre_depois:
        falhas.append("a tecla ficou presa — a próxima execução perde o atalho")

    if falhas:
        print("\nFALHOU:")
        for f in falhas:
            print("  -", f)
        return 1
    print("\nPASSOU: registro, exclusividade, travessia de thread e devolução.")
    print("FALTA VOCÊ: abrir o OMEGA e apertar Ctrl+Espaço de outro programa.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
