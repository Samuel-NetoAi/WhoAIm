"""Motor de voz em tempo real do OMEGA, pela Live API do Gemini.

O QUE MUDA EM RELAÇÃO AO MOTOR LOCAL: aqui não existe transcrição no meio.
O áudio do microfone vai direto para o modelo, que ouve, entende e responde
falando. A etapa que mais errava — o Whisper decidindo que "Ômega" era
"amiga" e o resto da frase morrendo com ela — deixa de existir.

De brinde vêm coisas que no motor local são gambiarra: interromper falando
por cima (barge-in), fim de turno decidido pelo modelo em vez de por um
temporizador de silêncio, e memória da conversa mantida pela própria sessão.

HISTÓRICO QUE IMPORTA: em 03/08/2026 nenhum modelo desta conta suportava
`bidiGenerateContent` e este caminho foi descartado. Em 07/08 voltei a
testar e estava liberado. Se um dia parar de funcionar, o teste é
`test_live.py` — ele diz se é a conta, a cota ou o código.

POR QUE NÃO O `google-genai`: o pacote não está instalado e traz uma árvore
de dependências para fazer o que `websockets` (já instalado, já usado pelo
`realtime_engine.py`) faz em algumas dezenas de linhas. O protocolo foi
verificado à mão contra a conta do Samuel antes de escrever isto.

FORMATOS, medidos e não supostos:
  entrada  PCM 16 bits mono 16 kHz  -> realtimeInput.audio (base64)
  saída    PCM 16 bits mono 24 kHz  <- serverContent.modelTurn.parts[].inlineData
E o modelo `gemini-3.1-flash-live-preview` só aceita `responseModalities:
["AUDIO"]` — pedir TEXT derruba a conexão com 1007. As transcrições que
aparecem no log vêm de `inputAudioTranscription`/`outputAudioTranscription`,
que são campos à parte.
"""

from __future__ import annotations

import asyncio
import base64
import json
import queue
import threading
import time

import numpy as np
import sounddevice as sd
import websockets

URL = ("wss://generativelanguage.googleapis.com/ws/"
       "google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent")

MODELO = "models/gemini-3.1-flash-live-preview"

TAXA_ENTRADA = 16000
TAXA_SAIDA = 24000
BLOCO = 1600            # 100 ms — pedaço pequeno o bastante para barge-in

# Quantas falhas seguidas antes de desistir e cair para o motor local. Uma
# queda isolada é internet oscilando; três seguidas é a cota gratuita tendo
# acabado, e insistir só faz o OMEGA ficar mudo mais tempo.
MAX_FALHAS = 3


class LiveEngine:
    """Mesma interface do `FreeEngine`: `run()`, `falar()`, `processar_texto()`."""

    def __init__(self, gemini_key, instructions, tool_executor, ui,
                 local_handler=None, tools=None):
        self.gemini_key = gemini_key
        self.instructions = instructions
        self.tool_executor = tool_executor
        self.ui = ui
        self.local_handler = local_handler
        self.tools = tools or []

        self._parar = threading.Event()
        self._entrada: queue.Queue[bytes] = queue.Queue()
        self._saida: queue.Queue[bytes] = queue.Queue()
        self._falando = threading.Event()
        self._laco: asyncio.AbstractEventLoop | None = None
        self._ws = None
        self._para_dizer: queue.Queue[str] = queue.Queue()

        # Motivo pelo qual caiu, para o main.py explicar em português em vez
        # de mostrar um traceback.
        self.motivo_da_queda = ""

        self.ui.on_text_command = self.processar_texto
        self.ui.falar = self.falar
        self.ui.esquecer = self.esquecer
        registrar = getattr(self.ui, "registrar_atalho_global", None)
        if registrar:
            registrar(self._ao_atalho_global)

    # ---------- interface comum com o motor local ----------

    def falar(self, texto: str, economico: bool = False) -> None:
        """Faz o OMEGA dizer algo por iniciativa própria (avisos de render).

        No motor local isto sintetiza voz; aqui o texto é entregue ao modelo,
        que o diz com a própria voz — senão o aviso sairia com outra voz no
        meio da conversa, o que soa como um segundo assistente falando.
        """
        if not texto:
            return
        self.ui.write_log(f"OMEGA: {texto}")
        self._para_dizer.put(texto)

    def esquecer(self) -> str:
        # A sessão da Live API guarda a conversa inteira; para esquecer, o
        # jeito honesto é começar outra.
        self._reconectar = True
        return "Vou começar do zero. Um instante."

    def processar_texto(self, texto: str) -> None:
        texto = (texto or "").strip()
        if not texto:
            return
        if self.local_handler:
            try:
                resposta = self.local_handler(texto, self.ui)
            except Exception as e:  # noqa: BLE001
                self.ui.write_log(f"ERR: {str(e)[:110]}")
                return
            if resposta is not None:
                self.ui.write_log(f"» {resposta}")
                return
        self._enviar_texto(texto)

    def _ao_atalho_global(self) -> None:
        from tools import leitura as _leitura

        if _leitura.lendo():
            self.ui.write_log("SYS: Ctrl+Espaço — " + _leitura.parar())
            return
        # Na Live não existe palavra de ativação: o modelo já está ouvindo.
        # A tecla serve para calar o OMEGA no meio de uma resposta longa.
        self._descartar_saida()
        self.ui.write_log("SYS: Ctrl+Espaço — pode falar.")

    # ---------- ferramentas ----------

    def _declaracoes(self) -> list[dict]:
        """As mesmas ferramentas do `main.py`, no formato do Gemini."""
        return [
            {"name": t["name"],
             "description": t.get("description", ""),
             "parameters": t.get("parameters", {"type": "object", "properties": {}})}
            for t in self.tools if t.get("name")
        ]

    # ---------- áudio ----------

    def _ao_capturar(self, indata, frames, tempo, status):
        if self.ui.muted:
            return
        self._entrada.put(bytes(indata))

    def _descartar_saida(self) -> None:
        """Joga fora o áudio ainda não tocado — é isto que faz o barge-in.

        Sem isto, interromper o modelo pararia a GERAÇÃO mas o que já chegou
        continuaria saindo pelos alto-falantes por vários segundos, e a
        interrupção pareceria não ter funcionado.
        """
        while True:
            try:
                self._saida.get_nowait()
            except queue.Empty:
                break
        self._falando.clear()

    def _tocar(self) -> None:
        """Thread que toca o áudio do modelo assim que ele chega."""
        try:
            stream = sd.RawOutputStream(
                samplerate=TAXA_SAIDA, channels=1, dtype="int16", blocksize=1200)
        except Exception as e:  # noqa: BLE001
            self.ui.write_log(f"SYS: sem saída de áudio ({str(e)[:50]}).")
            return
        with stream:
            while not self._parar.is_set():
                try:
                    pedaco = self._saida.get(timeout=0.2)
                except queue.Empty:
                    if self._falando.is_set():
                        self._falando.clear()
                        if not self.ui.muted:
                            self.ui.set_state("LISTENING")
                    continue
                if not self._falando.is_set():
                    self._falando.set()
                    self.ui.set_state("SPEAKING")
                try:
                    stream.write(pedaco)
                except Exception:  # noqa: BLE001
                    break

    # ---------- sessão ----------

    def _enviar_texto(self, texto: str) -> None:
        if not self._laco or not self._ws:
            self.ui.write_log("SYS: a sessão de voz não está aberta.")
            return
        asyncio.run_coroutine_threadsafe(
            self._ws.send(json.dumps({"clientContent": {
                "turns": [{"role": "user", "parts": [{"text": texto}]}],
                "turnComplete": True}})),
            self._laco,
        )

    def _setup(self) -> dict:
        return {"setup": {
            "model": MODELO,
            "generationConfig": {"responseModalities": ["AUDIO"]},
            "systemInstruction": {"parts": [{"text": self._instrucoes()}]},
            "tools": [{"functionDeclarations": self._declaracoes()}],
            # As duas transcrições existem para o LOG. Sem elas a janela do
            # OMEGA fica muda enquanto ele conversa, e não há como depurar
            # nada depois — foi como o motor local ganhou as linhas "Você:".
            "inputAudioTranscription": {},
            "outputAudioTranscription": {},
        }}

    def _instrucoes(self) -> str:
        try:
            from tools.projetos import listar_pastas

            nomes = [p.name for p in listar_pastas()]
        except Exception:  # noqa: BLE001
            nomes = []
        extra = (f"\n\nPROJETOS QUE EXISTEM AGORA: {', '.join(nomes)}."
                 if nomes else "")
        return (
            f"{self.instructions}{extra}\n\n"
            "Você está numa conversa por voz: frases curtas, sem listas e sem "
            "markdown. O senhor pode te interromper a qualquer momento — "
            "quando isso acontecer, pare e ouça."
        )

    async def _sessao(self) -> None:
        async with websockets.connect(
            f"{URL}?key={self.gemini_key}", max_size=None, open_timeout=30
        ) as ws:
            self._ws = ws
            await ws.send(json.dumps(self._setup()))
            resposta = json.loads(await asyncio.wait_for(ws.recv(), timeout=30))
            if "setupComplete" not in resposta:
                raise RuntimeError(f"a sessão não abriu: {list(resposta)[:2]}")

            self.ui.write_log("SYS: voz em tempo real ligada. Pode falar — "
                              "sem precisar dizer o nome, e pode me interromper.")
            if not self.ui.muted:
                self.ui.set_state("LISTENING")

            await asyncio.gather(
                self._bombear_microfone(ws),
                self._receber(ws),
                self._bombear_avisos(ws),
            )

    async def _bombear_microfone(self, ws) -> None:
        """Do microfone para o modelo, em pedaços de 100 ms."""
        while not self._parar.is_set():
            try:
                pedaco = self._entrada.get_nowait()
            except queue.Empty:
                await asyncio.sleep(0.02)
                continue
            await ws.send(json.dumps({"realtimeInput": {"audio": {
                "mimeType": f"audio/pcm;rate={TAXA_ENTRADA}",
                "data": base64.b64encode(pedaco).decode(),
            }}}))

    async def _bombear_avisos(self, ws) -> None:
        """Avisos de render/pesquisa ditos com a MESMA voz da conversa."""
        while not self._parar.is_set():
            try:
                texto = self._para_dizer.get_nowait()
            except queue.Empty:
                await asyncio.sleep(0.1)
                continue
            await ws.send(json.dumps({"clientContent": {
                "turns": [{"role": "user", "parts": [{"text":
                    f"[aviso do sistema, diga ao senhor com suas palavras] {texto}"}]}],
                "turnComplete": True}}))

    async def _receber(self, ws) -> None:
        ouvido: list[str] = []
        dito: list[str] = []
        while not self._parar.is_set():
            cru = await ws.recv()
            dados = json.loads(cru if isinstance(cru, str) else cru.decode())

            if "toolCall" in dados:
                await self._executar_ferramentas(ws, dados["toolCall"])
                continue

            conteudo = dados.get("serverContent")
            if not conteudo:
                continue

            if conteudo.get("interrupted"):
                # O modelo detectou que o senhor voltou a falar por cima.
                self._descartar_saida()
                self.ui.write_log("SYS: (interrompido)")
                continue

            trecho = conteudo.get("inputTranscription", {}).get("text")
            if trecho:
                ouvido.append(trecho)
            trecho = conteudo.get("outputTranscription", {}).get("text")
            if trecho:
                dito.append(trecho)

            for parte in conteudo.get("modelTurn", {}).get("parts", []):
                bruto = parte.get("inlineData", {}).get("data")
                if bruto:
                    self._saida.put(base64.b64decode(bruto))

            if conteudo.get("turnComplete"):
                if ouvido:
                    self.ui.write_log(f"Você: {''.join(ouvido).strip()}")
                    ouvido.clear()
                if dito:
                    self.ui.write_log(f"OMEGA: {''.join(dito).strip()}")
                    dito.clear()

    async def _executar_ferramentas(self, ws, chamada: dict) -> None:
        respostas = []
        for f in chamada.get("functionCalls", []):
            nome, args = f.get("name", ""), f.get("args", {}) or {}
            self.ui.write_log(
                f"SYS: executando {nome}({json.dumps(args, ensure_ascii=False)})")
            # As ferramentas são síncronas e algumas demoram (render, pesquisa):
            # rodar numa thread evita congelar o áudio da conversa inteira.
            try:
                resultado = await asyncio.to_thread(self.tool_executor, nome, args)
            except Exception as e:  # noqa: BLE001
                resultado = f"A ferramenta {nome} falhou: {str(e)[:150]}"
            respostas.append({"id": f.get("id"), "name": nome,
                              "response": {"result": resultado}})
        if respostas:
            await ws.send(json.dumps(
                {"toolResponse": {"functionResponses": respostas}}))

    # ---------- laço principal ----------

    def run(self) -> bool:
        """True = rodou. False = não deu; o `main.py` deve usar o motor local."""
        try:
            entrada = sd.RawInputStream(
                samplerate=TAXA_ENTRADA, blocksize=BLOCO, dtype="int16",
                channels=1, callback=self._ao_capturar)
        except Exception as e:  # noqa: BLE001
            self.motivo_da_queda = f"microfone indisponível ({str(e)[:60]})"
            return False

        threading.Thread(target=self._tocar, name="voz-live", daemon=True).start()

        falhas = 0
        with entrada:
            while not self._parar.is_set() and falhas < MAX_FALHAS:
                self._reconectar = False
                laco = asyncio.new_event_loop()
                self._laco = laco
                try:
                    laco.run_until_complete(self._sessao())
                    falhas = 0
                except Exception as e:  # noqa: BLE001
                    falhas += 1
                    razao = str(e)[:120]
                    self.motivo_da_queda = razao
                    self.ui.write_log(
                        f"SYS: a voz em tempo real caiu ({razao}) — "
                        f"tentativa {falhas} de {MAX_FALHAS}.")
                    # Cota estourada não se resolve tentando de novo.
                    if "429" in razao or "RESOURCE_EXHAUSTED" in razao.upper():
                        self.motivo_da_queda = "a cota gratuita do Gemini acabou"
                        break
                    time.sleep(2 * falhas)
                finally:
                    self._ws = None
                    laco.close()

        if falhas >= MAX_FALHAS or self.motivo_da_queda:
            return False
        return True

    def stop(self) -> None:
        self._parar.set()
