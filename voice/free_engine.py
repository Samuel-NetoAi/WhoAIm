"""Motor de voz GRATUITO do ALPHA — funciona sem gastar um centavo.

Cadeia: ouvidos = Vosk (offline, modelo pt-BR em models/pt-br),
cérebro = Gemini (chave do Samuel, camada gratuita) apenas quando o texto
não é um comando local, voz = SAPI do Windows (Maria pt-BR, offline).

Serve de alternativa ao `realtime_engine` da OpenAI: mesma interface
(`run()`, `ui`, `tool_executor`), então o `main.py` escolhe um ou outro.
Qualidade é menor que a Realtime API, mas custa zero e roda offline
(exceto o Gemini, usado só para frases livres).
"""

from __future__ import annotations

import json
import queue
import threading
import time
from pathlib import Path

import requests
import sounddevice as sd

BASE_DIR = Path(__file__).resolve().parent
MODELO_PT = BASE_DIR / "models" / "pt-br"
TAXA = 16000
BLOCO = 8000

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-flash-latest:generateContent"
)

# Palavra de ativação: sem ela, o Vosk transcreveria conversa aleatória do
# ambiente e o ALPHA responderia sozinho o tempo todo.
DESPERTAR = ("alpha", "alfa")


class FreeEngine:
    def __init__(
        self,
        gemini_key: str,
        instructions: str,
        tool_executor,
        ui,
        local_handler=None,
    ):
        self.gemini_key = gemini_key
        self.instructions = instructions
        self.tool_executor = tool_executor
        self.ui = ui
        self.local_handler = local_handler

        self._fila: queue.Queue[bytes] = queue.Queue()
        self._falando = threading.Event()
        self._parar = threading.Event()
        self._voz = None

        self.ui.on_text_command = self.processar_texto

    # ---------- voz (SAPI / Maria pt-BR) ----------

    def _init_voz(self):
        import pyttsx3

        motor = pyttsx3.init()
        for v in motor.getProperty("voices"):
            if "portug" in v.name.lower() or "maria" in v.name.lower():
                motor.setProperty("voice", v.id)
                break
        motor.setProperty("rate", 190)
        return motor

    def falar(self, texto: str) -> None:
        if not texto:
            return
        self.ui.write_log(f"ALPHA: {texto}")
        # O microfone é ignorado enquanto fala, senão o Vosk transcreve a
        # própria voz do ALPHA saindo pelos alto-falantes.
        self._falando.set()
        self.ui.set_state("SPEAKING")
        try:
            # pyttsx3 não é seguro entre threads: um motor por fala.
            motor = self._init_voz()
            motor.say(texto)
            motor.runAndWait()
            motor.stop()
        except Exception as e:  # noqa: BLE001
            print(f"[FREE] TTS falhou: {e}")
        finally:
            self._falando.clear()
            if not self.ui.muted:
                self.ui.set_state("LISTENING")

    # ---------- cérebro (Gemini) ----------

    def _perguntar_gemini(self, texto: str) -> str:
        corpo = {
            "systemInstruction": {"parts": [{"text": self.instructions}]},
            "contents": [{"role": "user", "parts": [{"text": texto}]}],
            "generationConfig": {"maxOutputTokens": 220, "temperature": 0.7},
        }
        r = requests.post(
            GEMINI_URL,
            params={"key": self.gemini_key},
            json=corpo,
            timeout=45,
        )
        if not r.ok:
            return f"O Gemini recusou: {r.status_code}."
        dados = r.json()
        try:
            partes = dados["candidates"][0]["content"]["parts"]
            return "".join(p.get("text", "") for p in partes).strip()
        except (KeyError, IndexError):
            return "Não consegui interpretar a resposta do Gemini."

    # ---------- despacho ----------

    def processar_texto(self, texto: str) -> None:
        """Um comando (de voz ou digitado): tenta local, senão Gemini."""
        texto = (texto or "").strip()
        if not texto:
            return
        self.ui.set_state("THINKING")
        try:
            if self.local_handler:
                resposta = self.local_handler(texto, self.ui)
                if resposta is not None:
                    self.falar(resposta)
                    return
            self.falar(self._perguntar_gemini(texto))
        except Exception as e:  # noqa: BLE001
            self.falar(f"Falhou: {str(e)[:120]}")

    # ---------- ouvidos (Vosk) ----------

    def _callback(self, indata, frames, tempo, status):
        if not self._falando.is_set() and not self.ui.muted:
            self._fila.put(bytes(indata))

    def run(self) -> None:
        if not MODELO_PT.exists():
            self.ui.write_log("ERR: modelo de voz não encontrado em models/pt-br")
            return

        from vosk import KaldiRecognizer, Model, SetLogLevel

        SetLogLevel(-1)
        self.ui.write_log("SYS: carregando modelo de voz (offline)...")
        modelo = Model(str(MODELO_PT))
        rec = KaldiRecognizer(modelo, TAXA)
        rec.SetWords(False)

        self.ui.write_log(
            "SYS: ALPHA ouvindo (modo gratuito). Comece a frase com 'Alpha'."
        )
        if not self.ui.muted:
            self.ui.set_state("LISTENING")

        with sd.RawInputStream(
            samplerate=TAXA,
            blocksize=BLOCO,
            dtype="int16",
            channels=1,
            callback=self._callback,
        ):
            while not self._parar.is_set():
                try:
                    dados = self._fila.get(timeout=0.5)
                except queue.Empty:
                    continue
                if not rec.AcceptWaveform(dados):
                    continue
                frase = json.loads(rec.Result()).get("text", "").strip()
                if not frase:
                    continue
                self.ui.write_log(f"Você: {frase}")

                baixo = frase.lower()
                gatilho = next((p for p in DESPERTAR if baixo.startswith(p)), None)
                if gatilho is None:
                    continue  # não era para o ALPHA
                comando = frase[len(gatilho):].strip(" ,.")
                if comando:
                    self.processar_texto(comando)

    def stop(self) -> None:
        self._parar.set()
