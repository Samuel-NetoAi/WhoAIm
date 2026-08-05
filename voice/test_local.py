"""Testa os comandos locais sem janela e sem OpenAI.
Rodar: python test_local.py
"""

from __future__ import annotations

from tools import handle_local_command


class FakeUI:
    def __init__(self):
        self.last: tuple[str, str] | None = None

    def show_document(self, title, text):
        self.last = ("documento", f"{title} · {len(text)} chars")

    def show_video(self, title, path):
        self.last = ("video", f"{title} · {path}")

    def show_hud(self):
        self.last = ("hud", "")


def main() -> None:
    ui = FakeUI()
    casos = [
        "ajuda",
        "projetos",
        "dossie Medusa",
        "prompts Medusa",
        "video Medusa",
        "hud",
        "dossie CriaturaQueNaoExiste",
        "isso aqui nao e um comando local",
    ]
    falhas = 0
    for cmd in casos:
        resposta = handle_local_command(cmd, ui)
        exibido = f"  [exibiu {ui.last[0]}: {ui.last[1]}]" if ui.last else ""
        print(f"> {cmd}\n  {resposta}{exibido}")
        ui.last = None
        if cmd == "isso aqui nao e um comando local" and resposta is not None:
            print("  FALHA: deveria devolver None para cair na voz")
            falhas += 1
        if cmd in ("ajuda", "projetos") and resposta is None:
            print("  FALHA: comando conhecido não foi tratado")
            falhas += 1
    print()
    print("FALHAS:" , falhas)
    raise SystemExit(1 if falhas else 0)


if __name__ == "__main__":
    main()
