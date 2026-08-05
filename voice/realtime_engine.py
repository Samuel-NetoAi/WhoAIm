"""Motor de voz do Alpha Voice: OpenAI Realtime API via WebSocket puro.

WebSocket direto (sem SDK) porque o protocolo JSON é estável e assim o
receptor pode aceitar tanto os nomes de evento beta (response.audio.delta)
quanto os GA (response.output_audio.delta) sem depender da versão da lib.

Áudio: PCM16 mono 24kHz nos dois sentidos, capturado/tocado com sounddevice.
Enquanto o Alpha fala, o microfone não é enviado (sem cancelamento de eco
local, o modelo ouviria a si mesmo pelos alto-falantes).
"""

from __future__ import annotations

import asyncio
import base64
import json
import threading
import traceback
from typing import Callable

import sounddevice as sd
import websockets

SAMPLE_RATE = 24000
CHANNELS = 1
CHUNK_SIZE = 1024
REALTIME_URL = "wss://api.openai.com/v1/realtime?model=gpt-realtime"


class RealtimeEngine:
    def __init__(
        self,
        api_key: str,
        instructions: str,
        tools: list[dict],
        tool_executor: Callable[[str, dict], str],
        ui,
        voice: str = "cedar",
    ):
        self.api_key = api_key
        self.instructions = instructions
        self.tools = tools
        self.tool_executor = tool_executor
        self.ui = ui
        self.voice = voice

        self.ws = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._play_queue: asyncio.Queue | None = None
        self._mic_queue: asyncio.Queue | None = None
        self._is_speaking = False
        self._speaking_lock = threading.Lock()

        self.ui.on_text_command = self._on_text_command

    # ---------- estado ----------

    def _set_speaking(self, value: bool) -> None:
        with self._speaking_lock:
            self._is_speaking = value
        if value:
            self.ui.set_state("SPEAKING")
        elif not self.ui.muted:
            self.ui.set_state("LISTENING")

    # ---------- envio ----------

    async def _send(self, event: dict) -> None:
        if self.ws:
            await self.ws.send(json.dumps(event))

    def _send_threadsafe(self, event: dict) -> None:
        if self._loop and self.ws:
            asyncio.run_coroutine_threadsafe(self._send(event), self._loop)

    def _on_text_command(self, text: str) -> None:
        self._send_threadsafe(
            {
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": text}],
                },
            }
        )
        self._send_threadsafe({"type": "response.create"})

    def speak(self, text: str) -> None:
        """Pede ao modelo que fale um aviso (usado pelos callbacks de tools)."""
        self._on_text_command(f"[Avise o usuário]: {text}")

    # ---------- sessão ----------

    def _session_update(self) -> dict:
        # Formato GA da Realtime API (o shape beta está desabilitado para
        # contas novas — o servidor responde beta_api_shape_disabled).
        return {
            "type": "session.update",
            "session": {
                "type": "realtime",
                "instructions": self.instructions,
                "output_modalities": ["audio"],
                "audio": {
                    "input": {
                        "format": {"type": "audio/pcm", "rate": SAMPLE_RATE},
                        "turn_detection": {"type": "server_vad"},
                        "transcription": {"model": "whisper-1"},
                    },
                    "output": {
                        "format": {"type": "audio/pcm", "rate": SAMPLE_RATE},
                        "voice": self.voice,
                    },
                },
                "tools": self.tools,
                "tool_choice": "auto",
            },
        }

    # ---------- áudio ----------

    async def _mic_task(self) -> None:
        loop = asyncio.get_event_loop()

        def callback(indata, frames, time_info, status):
            with self._speaking_lock:
                speaking = self._is_speaking
            if not speaking and not self.ui.muted:
                data = bytes(indata)
                loop.call_soon_threadsafe(self._mic_queue.put_nowait, data)

        with sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            blocksize=CHUNK_SIZE,
            callback=callback,
        ):
            print("[VOICE] Mic aberto")
            while True:
                chunk = await self._mic_queue.get()
                await self._send(
                    {
                        "type": "input_audio_buffer.append",
                        "audio": base64.b64encode(chunk).decode("ascii"),
                    }
                )

    async def _player_task(self) -> None:
        stream = sd.RawOutputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            blocksize=CHUNK_SIZE,
        )
        stream.start()
        print("[VOICE] Playback aberto")
        try:
            while True:
                try:
                    chunk = await asyncio.wait_for(
                        self._play_queue.get(), timeout=0.35
                    )
                except asyncio.TimeoutError:
                    # Fila secou: se estávamos falando, voltamos a ouvir.
                    if self._is_speaking:
                        self._set_speaking(False)
                    continue
                self._set_speaking(True)
                await asyncio.to_thread(stream.write, chunk)
        finally:
            stream.stop()
            stream.close()

    def _clear_playback(self) -> None:
        if self._play_queue:
            while not self._play_queue.empty():
                try:
                    self._play_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break

    # ---------- ferramentas ----------

    async def _handle_function_call(self, call_id: str, name: str, args_json: str) -> None:
        self.ui.set_state("THINKING")
        try:
            args = json.loads(args_json or "{}")
        except json.JSONDecodeError:
            args = {}
        print(f"[VOICE] tool {name} {args}")
        result = await asyncio.to_thread(self.tool_executor, name, args)
        self.ui.write_log(f"TOOL {name}: {str(result)[:100]}")
        await self._send(
            {
                "type": "conversation.item.create",
                "item": {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": str(result),
                },
            }
        )
        await self._send({"type": "response.create"})
        if not self.ui.muted:
            self.ui.set_state("LISTENING")

    # ---------- recepção ----------

    async def _recv_task(self) -> None:
        async for raw in self.ws:
            event = json.loads(raw)
            etype = event.get("type", "")

            if etype in ("response.audio.delta", "response.output_audio.delta"):
                self._play_queue.put_nowait(base64.b64decode(event["delta"]))

            elif etype == "input_audio_buffer.speech_started":
                # Barge-in: o usuário começou a falar por cima.
                self._clear_playback()
                await self._send({"type": "response.cancel"})
                self._set_speaking(False)

            elif etype == "conversation.item.input_audio_transcription.completed":
                txt = (event.get("transcript") or "").strip()
                if txt:
                    self.ui.write_log(f"Você: {txt}")

            elif etype in (
                "response.audio_transcript.done",
                "response.output_audio_transcript.done",
            ):
                txt = (event.get("transcript") or "").strip()
                if txt:
                    self.ui.write_log(f"Alpha: {txt}")

            elif etype == "response.function_call_arguments.done":
                asyncio.create_task(
                    self._handle_function_call(
                        event.get("call_id", ""),
                        event.get("name", ""),
                        event.get("arguments", ""),
                    )
                )

            elif etype == "error":
                err = event.get("error", {})
                # response.cancel sem resposta ativa é inofensivo
                if err.get("code") != "response_cancel_not_active":
                    print(f"[VOICE] API error: {err}")
                    self.ui.write_log(f"ERR: {err.get('message', '?')[:90]}")

    # ---------- loop principal ----------

    async def run(self) -> None:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        while True:
            try:
                self.ui.set_state("THINKING")
                print("[VOICE] Conectando...")
                async with websockets.connect(
                    REALTIME_URL,
                    additional_headers=headers,
                    max_size=1 << 24,
                ) as ws:
                    self.ws = ws
                    self._loop = asyncio.get_event_loop()
                    self._play_queue = asyncio.Queue()
                    self._mic_queue = asyncio.Queue()

                    await self._send(self._session_update())
                    print("[VOICE] Conectado.")
                    self.ui.write_log("SYS: Alpha Voice online (OpenAI Realtime).")
                    if not self.ui.muted:
                        self.ui.set_state("LISTENING")

                    async with asyncio.TaskGroup() as tg:
                        tg.create_task(self._recv_task())
                        tg.create_task(self._mic_task())
                        tg.create_task(self._player_task())

            except BaseException as e:  # noqa: BLE001 — loop de resiliência
                if isinstance(e, (KeyboardInterrupt, SystemExit)):
                    raise
                # TaskGroup entrega ExceptionGroup; conexões diretas entregam
                # a exceção simples — normalizamos tudo para texto.
                if isinstance(e, BaseExceptionGroup):
                    reason = "; ".join(str(x) for x in e.exceptions)
                else:
                    reason = str(e)
                if "insufficient_quota" in reason:
                    # Conta OpenAI sem saldo — não adianta martelar a cada 3s.
                    self.ui.write_log(
                        "ERR: conta OpenAI sem créditos — adicione saldo em "
                        "platform.openai.com (Billing) para a voz funcionar"
                    )
                    print("[VOICE] Sem quota na OpenAI; nova tentativa em 60s.")
                    self._set_speaking(False)
                    self.ui.set_state("THINKING")
                    await asyncio.sleep(60)
                    continue
                print(f"[VOICE] {reason[:200]}")
                traceback.print_exc()

            self._set_speaking(False)
            self.ui.set_state("THINKING")
            print("[VOICE] Reconectando em 3s...")
            await asyncio.sleep(3)
