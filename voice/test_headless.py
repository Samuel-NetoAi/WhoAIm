"""Teste do Alpha Voice sem microfone: valida chave, protocolo Realtime,
declaração de tools, round-trip de function call com o Studio REAL e
resposta final em texto. Rodar: python test_headless.py
"""

from __future__ import annotations

import asyncio
import json

import websockets

from main import INSTRUCTIONS, TOOLS, make_tool_executor, load_api_key
from realtime_engine import REALTIME_URL


class _FakeUI:
    """UI de mentira: registra o que seria exibido, para o teste rodar sem janela."""

    def __init__(self):
        self.shown: list[str] = []

    def show_document(self, title, text):
        self.shown.append(f"documento:{title} ({len(text)} chars)")

    def show_video(self, title, path):
        self.shown.append(f"video:{title}")

    def show_hud(self):
        self.shown.append("hud")


execute_tool = make_tool_executor(_FakeUI())


async def run_test() -> None:
    key = load_api_key()
    headers = {"Authorization": f"Bearer {key}"}
    tool_calls: list[str] = []
    final_text: list[str] = []

    async with websockets.connect(
        REALTIME_URL, additional_headers=headers, max_size=1 << 24
    ) as ws:
        async def send(ev: dict) -> None:
            await ws.send(json.dumps(ev))

        await send(
            {
                "type": "session.update",
                "session": {
                    "type": "realtime",
                    "instructions": INSTRUCTIONS,
                    "output_modalities": ["text"],
                    "tools": TOOLS,
                    "tool_choice": "auto",
                },
            }
        )
        await send(
            {
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "Quantos projetos temos no estúdio e como estão?",
                        }
                    ],
                },
            }
        )
        await send({"type": "response.create"})

        async with asyncio.timeout(90):
            async for raw in ws:
                ev = json.loads(raw)
                etype = ev.get("type", "")

                if etype == "session.updated":
                    print("OK  session.updated aceito (tools registradas)")

                elif etype == "response.function_call_arguments.done":
                    name = ev.get("name", "")
                    args = json.loads(ev.get("arguments") or "{}")
                    print(f"OK  modelo chamou tool: {name} {args}")
                    tool_calls.append(name)
                    result = execute_tool(name, args)
                    print(f"OK  tool executou: {result[:120]}")
                    await send(
                        {
                            "type": "conversation.item.create",
                            "item": {
                                "type": "function_call_output",
                                "call_id": ev.get("call_id", ""),
                                "output": result,
                            },
                        }
                    )
                    await send({"type": "response.create"})

                elif etype in ("response.text.done", "response.output_text.done"):
                    txt = (ev.get("text") or "").strip()
                    if txt:
                        final_text.append(txt)

                elif etype == "response.done" and (final_text or not tool_calls):
                    break

                elif etype == "error":
                    print(f"ERR {ev.get('error')}")
                    raise SystemExit(1)

    print("\n===== RESULTADO =====")
    print(f"tools chamadas : {tool_calls}")
    print(f"resposta final : {' '.join(final_text)}")
    assert "studio_control" in tool_calls, "modelo não chamou studio_control"
    assert final_text, "sem resposta final em texto"
    print("TESTE PASSOU")


if __name__ == "__main__":
    asyncio.run(run_test())
