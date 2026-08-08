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

from tools import aula as _aula

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

# Como a Live API diz "acabou a cota". Ela NÃO manda 429 pelo WebSocket: manda
# o código de fechamento 1008 ("policy violation") com "operation was aborted"
# — e eu só procurava por "429". Resultado no uso real: três tentativas
# inúteis, uma atrás da outra, com o Samuel olhando erro em inglês na tela.
_SINAIS_DE_COTA = ("1008", "429", "resource_exhausted", "quota",
                   "policy violation", "operation was aborted")


def _e_falta_de_cota(razao: str) -> bool:
    baixo = (razao or "").lower()
    return any(s in baixo for s in _SINAIS_DE_COTA)

# Quanto tempo a conversa segue aberta depois da última interação. Mais longo
# que os 25 s do motor local porque aqui a conversa é fluida de verdade — e o
# relógio conta a partir do fim da fala DELE, não do pedido.
JANELA_CONVERSA = 60.0


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

        # Portão da palavra de ativação. `sempre_ouvindo` no config desliga,
        # para quem prefira a conversa contínua e aceite o OMEGA comentando o
        # que se fala na sala.
        self._janela_ate = 0.0
        # MICROFONE TRAVADO (a tecla como "o chão é meu"). O Samuel reclamou
        # de ser cortado enquanto ainda formulava a frase: o modelo decide o
        # fim do turno pelo silêncio, e pensar no meio da frase parece fim.
        # Com o microfone travado, NADA vai ao Gemini até ele soltar — então
        # não há como o modelo responder antes da hora.
        self._travado = False
        self._fala_presa: list[bytes] = []
        self._portao = None
        if not self._sempre_ouvindo():
            from tools.despertar import Portao

            self._portao = Portao(
                ao_abrir=lambda frase: self.ui.write_log(f"Você: {frase}")
            )

        self.ui.on_text_command = self.processar_texto
        self.ui.falar = self.falar
        # Leitura de documento NÃO passa pelo modelo — ver `falar_leitura`.
        self.ui.falar_leitura = self.falar_leitura
        self.ui.esquecer = self.esquecer
        # Duas palmas: a saída física para calar uma leitura longa. No motor
        # local isso já existia; aqui faltava, e sem o gesto a única saída
        # durante a leitura seria o teclado — que é justamente o que o Samuel
        # não tem à mão quando está longe do PC.
        from clap import DetectorDePalmas

        self._palmas = DetectorDePalmas(taxa=TAXA_ENTRADA,
                                        ao_detectar=self._ao_bater_palmas)
        registrar = getattr(self.ui, "registrar_atalho_global", None)
        if registrar:
            try:
                registrar(self._ao_atalho_global)
            except Exception as e:  # noqa: BLE001
                # Uma tecla que não registra é um incômodo; derrubar o
                # motor por causa dela deixa o OMEGA surdo. Já aconteceu:
                # a exceção subia daqui e matava a thread inteira.
                self.ui.write_log(f"SYS: atalho global indisponível ({str(e)[:60]}).")

    @staticmethod
    def _sempre_ouvindo() -> bool:
        try:
            import json
            from pathlib import Path

            cfg = json.loads(
                (Path(__file__).resolve().parent / "config" / "api_keys.json")
                .read_text(encoding="utf-8-sig")
            )
            return bool(cfg.get("sempre_ouvindo"))
        except Exception:  # noqa: BLE001
            return False

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
        """A tecla é um INTERRUPTOR: aperta, fala à vontade, aperta de novo.

        Enquanto travado o áudio fica guardado aqui e o Gemini não vê nada —
        é isso que impede ele de responder no meio de uma frase ainda sendo
        pensada. Ao soltar, tudo vai de uma vez, como um turno só.
        """
        from tools import leitura as _leitura

        if _leitura.lendo():
            self.ui.write_log("SYS: atalho — " + _leitura.parar())
            return

        if self._travado:
            self._travado = False
            presa, self._fala_presa = self._fala_presa, []
            segundos = sum(len(b) for b in presa) / 2 / TAXA_ENTRADA
            if segundos < 0.4:
                self.ui.write_log("SYS: microfone liberado (não ouvi nada).")
                return
            self._abrir_janela()
            for pedaco in presa:
                self._entrada.put(pedaco)
            self._fim_de_turno()
            self.ui.write_log(f"SYS: ▸ enviado ({segundos:.0f}s). "
                              "Agora ele responde.")
            return

        # Travando: cala o OMEGA se estiver falando e toma a palavra.
        self._descartar_saida()
        self._travado = True
        self._fala_presa = []
        self.ui.write_log("SYS: ● microfone SEU — fale à vontade, sem pressa. "
                          "Aperte de novo quando terminar.")

    def _fim_de_turno(self) -> None:
        """Diz ao Gemini que a fala acabou, para ele responder agora."""
        if not self._laco or not self._ws:
            return
        asyncio.run_coroutine_threadsafe(
            self._ws.send(json.dumps({"realtimeInput": {"audioStreamEnd": True}})),
            self._laco,
        )

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
        dados = bytes(indata)
        # As palmas são ouvidas SEMPRE, inclusive durante a leitura.
        self._palmas.alimentar(dados)

        if self.ui.muted:
            return

        from tools import leitura as _leitura

        if _leitura.lendo():
            # Durante uma leitura o microfone NÃO vai para o modelo: a voz da
            # leitura sai pelos alto-falantes, voltaria pelo microfone, e o
            # Gemini responderia ao próprio dossiê — gastando cota para
            # comentar o que ele mesmo está lendo. Para interromper: duas
            # palmas, Ctrl+Espaço, ou o botão de parar.
            return

        if self._travado:
            # Guardado, não enviado: o turno só existe quando ele soltar.
            self._fala_presa.append(dados)
            return

        # PORTÃO DA PALAVRA DE ATIVAÇÃO. Sem ele o OMEGA responde a qualquer
        # conversa da sala — aconteceu no primeiro uso real, com ele opinando
        # sobre um assunto que não era com ele. Enquanto fechado, nada chega
        # ao Gemini; o `tiny` local decide, em 0,07 s, se chamaram pelo nome.
        if self._portao is not None and not self._aberto():
            trecho = self._portao.alimentar(dados)
            if trecho is None:
                return
            # Chamaram: a frase INTEIRA que estava sendo gravada vai junto,
            # senão "Ômega, monta o vídeo da Medusa" abriria o portão e
            # perderia o comando.
            self._abrir_janela()
            self._entrada.put(trecho)
            return

        self._entrada.put(dados)

    # ---------- janela de conversa ----------

    def _aberto(self) -> bool:
        return time.monotonic() < self._janela_ate

    def _abrir_janela(self) -> None:
        estava_fechado = not self._aberto()
        self._janela_ate = time.monotonic() + JANELA_CONVERSA
        if estava_fechado:
            self.ui.write_log("SYS: pois não, senhor? (ouvindo)")
            if not self.ui.muted:
                self.ui.set_state("LISTENING")
            if self._portao is not None:
                self._portao.limpar()

    def _ao_bater_palmas(self) -> None:
        from tools import leitura as _leitura

        if _leitura.lendo():
            self.ui.write_log("SYS: duas palmas — " + _leitura.parar())
            return
        # Longe do PC, as palmas fazem o mesmo que a tecla — inclusive soltar
        # o microfone travado, senão ele ficaria preso sem teclado por perto.
        if self._travado:
            self._ao_atalho_global()
            return
        if self._portao is not None and not self._aberto():
            self._abrir_janela()
            return
        self.ui.write_log("SYS: duas palmas — trazendo a janela para a frente.")
        self.ui.trazer_para_frente()

    def falar_leitura(self, texto: str, economico: bool = True) -> None:
        """Fala um bloco de documento com a voz DESTA MÁQUINA.

        Separado de `falar` de propósito: `falar` entrega o texto ao modelo,
        que é o certo para uma resposta de conversa e errado para um dossiê —
        27 mil caracteres queimariam a cota e o modelo resumiria em vez de ler.
        """
        from tools import voz_local

        voz_local.falar(texto, economico=economico, log=self.ui.write_log)

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
        if self._falando.is_set():
            self._falando.clear()
            _aula.retomar()

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
                        _aula.retomar()
                        if not self.ui.muted:
                            self.ui.set_state("LISTENING")
                    continue
                if not self._falando.is_set():
                    self._falando.set()
                    self.ui.set_state("SPEAKING")
                    # A aula grava o que sai pelos alto-falantes: sem pausar,
                    # a voz do modelo entra na transcrição do curso.
                    _aula.pausar()
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

            if self._portao is None:
                self.ui.write_log(
                    "SYS: voz em tempo real ligada, SEMPRE ouvindo. Pode falar "
                    "e pode me interromper — mas eu respondo a qualquer "
                    "conversa perto do microfone.")
            else:
                self.ui.write_log(
                    "SYS: voz em tempo real ligada. Diga 'Ômega' (ou bata duas "
                    "palmas) e depois converse à vontade — pode me interromper.")
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
                # A janela conta a partir do fim da fala DELE. Contando do
                # pedido, uma resposta longa a consumiria inteira e o nome
                # voltaria a ser obrigatório a cada frase — o mesmo defeito
                # que o motor local já teve.
                if self._portao is not None:
                    self._janela_ate = time.monotonic() + JANELA_CONVERSA
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
                    razao = str(e)[:160]
                    # Cota estourada não se resolve tentando de novo — e
                    # insistir três vezes só enche a tela de erro em inglês.
                    if _e_falta_de_cota(razao):
                        self.motivo_da_queda = "a cota gratuita do Gemini acabou"
                        break
                    self.motivo_da_queda = razao
                    self.ui.write_log(
                        f"SYS: a voz em tempo real caiu — tentativa {falhas} "
                        f"de {MAX_FALHAS}. ({razao[:70]})")
                    time.sleep(2 * falhas)
                finally:
                    self._ws = None
                    laco.close()

        if falhas >= MAX_FALHAS or self.motivo_da_queda:
            return False
        return True

    def stop(self) -> None:
        self._parar.set()
