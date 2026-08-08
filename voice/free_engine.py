"""Motor de voz GRATUITO do OMEGA — funciona sem gastar um centavo.

Cadeia: ouvidos = Whisper local na GPU (tools/transcritor.py),
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
from difflib import SequenceMatcher
import re
import threading
import time
import unicodedata
from pathlib import Path

import requests
import sounddevice as sd

from clap import DetectorDePalmas
from tools.vocabulario import corrigir as corrigir_vocabulario

BASE_DIR = Path(__file__).resolve().parent
MODELO_PT = BASE_DIR / "models" / "pt-br"
TAXA = 16000
BLOCO = 8000

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-flash-latest:generateContent"
)

# Palavra de ativação: sem ela, qualquer conversa no ambiente viraria
# comando. As variantes abaixo são as que os transcritores REALMENTE
# produzem para "Ômega" — observadas no log, não imaginadas.
DESPERTAR = ("omega", "o mega", "omegas", "amega", "omeca",
             "omida", "omeda", "omena", "nega", "amiga", "omeya")

# Quantas palavras iniciais podem vir antes do nome. O Vosk costuma grudar
# um "é", "ó" ou ruído no começo da frase; exigir que o nome seja a PRIMEIRA
# palavra fazia o comando inteiro ser descartado em silêncio.
MARGEM_DESPERTAR = 3

# Depois de atendido, o OMEGA continua ouvindo por este tempo sem exigir o
# nome de novo — conversa em vez de interrogatório.
JANELA_CONVERSA = 25.0

# Quantas trocas ficam na memória de conversa. Oito cobre um assunto inteiro
# sem inflar cada requisição — e a cota gratuita do Gemini é apertada.
MAX_TURNOS_MEMORIA = 8

# Depois deste silêncio a conversa é considerada outra. Sem isto, um "sim"
# dito de manhã responderia a uma pergunta feita na véspera.
MEMORIA_EXPIRA = 900.0

# Ela reabre a cada resposta, contando do momento em que o OMEGA cala a
# boca. Na prática: o nome só é preciso para começar; a partir daí a
# conversa segue solta enquanto não houver 25 s de silêncio.



# Palavras que interrompem uma leitura. Regex em vez de lista exata porque
# durante a leitura o que chega pelo microfone vem misturado com o eco da
# própria voz — basta a palavra aparecer.
_E_PARADA = re.compile(r'\b(parar?|pare|chega|silencio|cale|cala)\b')

def _sem_acento(texto: str) -> str:
    """O Whisper devolve acentuado ("Ômega"); a lista está sem acento."""
    return "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )

class FreeEngine:
    def __init__(
        self,
        gemini_key: str,
        instructions: str,
        tool_executor,
        ui,
        local_handler=None,
        tools=None,
    ):
        self.gemini_key = gemini_key
        self.instructions = instructions
        self.tool_executor = tool_executor
        self.ui = ui
        self.local_handler = local_handler
        self.tools = tools or []

        self._fila: queue.Queue[bytes] = queue.Queue()
        self._falando = threading.Event()
        self._parar = threading.Event()
        self._janela_ate = 0.0  # fim da janela de conversa (time.monotonic)
        self._voz = None
        self._voz_indisponivel = False
        # Os avisos de progresso (pesquisa, render) chegam de threads próprias:
        # sem serializar, duas falas se sobrepõem e o pyttsx3 quebra.
        self._trava_voz = threading.Lock()
        # Duas palmas trazem a janela de volta. Escuta o MESMO fluxo do Vosk —
        # nenhuma segunda captura do microfone.
        self._palmas = DetectorDePalmas(taxa=TAXA, ao_detectar=self._ao_bater_palmas)
        # MEMÓRIA DE CONVERSA. Sem ela cada frase abria uma sessão nova com o
        # Gemini, e "e o roteiro dela?" era impossível de responder — não por
        # falha de escuta, mas porque ele não tinha como saber quem era "ela".
        self._historico: list[dict] = []
        self._ultima_fala = 0.0

        self.ui.on_text_command = self.processar_texto
        # Ctrl+Espaço: a saída para quando o nome não é reconhecido. Não
        # substitui o "Ômega" — ele continua servindo de longe —, mas quando o
        # Samuel está na frente do PC a tecla nunca erra, e reconhecimento de
        # fala erra sempre um pouco.
        registrar = getattr(self.ui, "registrar_atalho_global", None)
        if registrar:
            registrar(self._ao_atalho_global)
        # Os comandos locais precisam falar (leitura de documentos em voz
        # alta); expomos a fala pela UI para não acoplar os dois módulos.
        self.ui.falar = self.falar
        # Mesma razão: os comandos locais precisam poder zerar o assunto sem
        # conhecer o motor.
        self.ui.esquecer = self.esquecer

    # ---------- voz (SAPI / Maria pt-BR) ----------

    def _falar_elevenlabs(self, texto: str) -> bool:
        """Fala pela ElevenLabs. False = não deu, use a voz do Windows."""
        try:
            from tools import elevenlabs_voz

            if not elevenlabs_voz.disponivel():
                return False
            wav = elevenlabs_voz.sintetizar(texto)
            if not wav:
                if elevenlabs_voz._estado["sem_credito"]:
                    self.ui.write_log(
                        "SYS: créditos da ElevenLabs acabaram — voltando à voz do Windows."
                    )
                return False

            import wave

            with wave.open(str(wav), "rb") as f:
                taxa, canais = f.getframerate(), f.getnchannels()
                dados = f.readframes(f.getnframes())

            # RawOutputStream evita depender do numpy (que não está instalado)
            # e é o mesmo mecanismo já usado no resto do motor.
            stream = sd.RawOutputStream(
                samplerate=taxa, channels=canais, dtype="int16"
            )
            stream.start()
            try:
                stream.write(dados)
            finally:
                stream.stop()
                stream.close()
            return True
        except Exception as e:  # noqa: BLE001 — qualquer falha volta pra Maria
            self.ui.write_log(f"SYS: ElevenLabs falhou ({str(e)[:50]}) — voz local.")
            return False

    def _init_voz(self):
        import pyttsx3

        motor = pyttsx3.init()
        for v in motor.getProperty("voices"):
            if "portug" in v.name.lower() or "maria" in v.name.lower():
                motor.setProperty("voice", v.id)
                break
        motor.setProperty("rate", 190)
        return motor

    def falar(self, texto: str, economico: bool = False) -> None:
        """Fala uma resposta.

        `economico=True` pula a ElevenLabs e usa a voz do Windows. Serve para
        LEITURA de documentos: um dossiê tem ~27 mil caracteres e a conta
        gratuita da ElevenLabs dá 10 mil créditos POR MÊS — ler um único
        documento com ela consumiria quase três meses de cota.
        """
        if not texto:
            return
        self.ui.write_log(f"OMEGA: {texto}")
        # Máquina sem saída de áudio (o Linux secundário) não deve tentar falar
        # a cada resposta: um motor novo por fala custa caro e a falha se
        # repetiria em todas. A resposta continua no log, que é o que importa
        # no modo digitado.
        if self._voz_indisponivel:
            return
        # O microfone é ignorado enquanto fala, senão o Vosk transcreve a
        # própria voz do OMEGA saindo pelos alto-falantes.
        with self._trava_voz:
            self._falando.set()
            self.ui.set_state("SPEAKING")
            try:
                # Primeiro a ElevenLabs (natural); se não houver chave ou
                # crédito, cai para a Maria do Windows — ficar mudo seria pior
                # que soar robótico.
                if not economico and self._falar_elevenlabs(texto):
                    return
                # pyttsx3 não é seguro entre threads: um motor por fala.
                motor = self._init_voz()
                motor.say(texto)
                motor.runAndWait()
                motor.stop()
            except Exception as e:  # noqa: BLE001
                self._voz_indisponivel = True
                self.ui.write_log(
                    f"SYS: voz indisponível ({str(e)[:60]}) — sigo por texto."
                )
            finally:
                self._falando.clear()
                # A janela de conversa conta a partir do SILÊNCIO, não do
                # pedido. Abrindo-a só antes de responder, uma resposta de 30 s
                # a consumia inteira e o nome voltava a ser obrigatório a cada
                # frase — exatamente o interrogatório que ela existe para evitar.
                from tools import leitura as _leitura

                if not _leitura.lendo():
                    self._abrir_janela()
                if not self.ui.muted:
                    self.ui.set_state("LISTENING")

    # ---------- cérebro (Gemini) ----------

    def _declaracoes(self) -> list[dict]:
        """As ferramentas do `main.py` no formato que o Gemini espera.

        A lista é escrita no formato da OpenAI Realtime (com a chave "type");
        o Gemini quer só nome, descrição e parâmetros. Converter aqui evita
        manter duas listas de ferramentas em sincronia.
        """
        return [
            {
                "name": t["name"],
                "description": t.get("description", ""),
                "parameters": t.get("parameters", {"type": "object", "properties": {}}),
            }
            for t in self.tools
        ]

    def _instrucoes_com_estado(self) -> str:
        """As instruções fixas MAIS o que existe agora no disco.

        Sem a lista de projetos o modelo não tem como resolver "me arruma
        aquele negócio da Medusa": ele sabe usar as ferramentas, mas não sabe
        que "Medusa" e "IT A Coisa" são as coisas que existem. A lista muda
        quando o Samuel cria uma criatura nova, então é lida na hora.
        """
        try:
            from tools.projetos import listar_pastas

            nomes = [p.name for p in listar_pastas()]
        except Exception:  # noqa: BLE001 — sem disco, seguimos sem a lista
            nomes = []
        if not nomes:
            return self.instructions
        return (
            f"{self.instructions}\n\n"
            f"PROJETOS QUE EXISTEM AGORA: {', '.join(nomes)}.\n"
            "Quando o usuário citar uma criatura de forma aproximada ou "
            "errada, case com um destes nomes e siga; só pergunte se duas "
            "opções empatarem de verdade."
        )

    def _lembrar(self, pergunta: str, resposta: str) -> None:
        """Guarda a troca para o próximo turno entender pronome e retomada."""
        agora = time.monotonic()
        if agora - self._ultima_fala > MEMORIA_EXPIRA:
            self._historico.clear()
        self._ultima_fala = agora
        self._historico.append({"role": "user", "parts": [{"text": pergunta}]})
        self._historico.append({"role": "model", "parts": [{"text": resposta}]})
        # Guardamos só o texto das trocas, não as chamadas de ferramenta: o
        # que o turno seguinte precisa é do ASSUNTO, e o histórico cru de
        # functionCall/functionResponse triplicaria o tamanho de cada
        # requisição numa cota que já vive dando 429.
        del self._historico[: -2 * MAX_TURNOS_MEMORIA]

    def esquecer(self) -> str:
        self._historico.clear()
        return "Esqueci o assunto anterior. Pode começar de novo."

    def _chamar_gemini(self, contents: list[dict]) -> dict:
        corpo: dict = {
            "systemInstruction": {"parts": [{"text": self._instrucoes_com_estado()}]},
            "contents": contents,
            "generationConfig": {"maxOutputTokens": 220, "temperature": 0.7},
        }
        declaracoes = self._declaracoes()
        if declaracoes:
            corpo["tools"] = [{"functionDeclarations": declaracoes}]

        r = requests.post(
            GEMINI_URL, params={"key": self.gemini_key}, json=corpo, timeout=45
        )
        if not r.ok:
            raise RuntimeError(f"O Gemini recusou: {r.status_code}.")
        return r.json()

    def _perguntar_gemini(self, texto: str) -> str:
        """Conversa com o Gemini, EXECUTANDO as ferramentas que ele pedir.

        Sem isto o motor gratuito só conversava: o `tool_executor` chegava aqui
        e nunca era chamado, então um pedido como "pesquisa a Quimera" fazia o
        OMEGA responder que tinha começado — sem nada ter acontecido. Mentir
        sobre execução é pior do que não ter a função.
        """
        # O histórico vem ANTES da pergunta: é o que permite "e o roteiro
        # dela?" logo depois de "me mostra a pesquisa da Medusa".
        if time.monotonic() - self._ultima_fala > MEMORIA_EXPIRA:
            self._historico.clear()
        contents: list[dict] = list(self._historico)
        contents.append({"role": "user", "parts": [{"text": texto}]})

        # Poucas rodadas de propósito: uma cadeia longa de chamadas na camada
        # gratuita gasta cota e demora mais do que a paciência de quem falou.
        for _ in range(3):
            try:
                dados = self._chamar_gemini(contents)
            except RuntimeError as e:
                return str(e)

            try:
                partes = dados["candidates"][0]["content"]["parts"]
            except (KeyError, IndexError):
                return "Não consegui interpretar a resposta do Gemini."

            chamadas = [p["functionCall"] for p in partes if "functionCall" in p]
            if not chamadas:
                texto_final = "".join(p.get("text", "") for p in partes).strip()
                texto_final = texto_final or "Pronto."
                self._lembrar(texto, texto_final)
                return texto_final

            contents.append({"role": "model", "parts": partes})
            respostas = []
            for chamada in chamadas:
                nome = chamada.get("name", "")
                args = chamada.get("args", {}) or {}
                self.ui.write_log(f"SYS: executando {nome}({json.dumps(args, ensure_ascii=False)})")
                resultado = self.tool_executor(nome, args)
                respostas.append(
                    {
                        "functionResponse": {
                            "name": nome,
                            "response": {"result": resultado},
                        }
                    }
                )
            contents.append({"role": "user", "parts": respostas})

        return "Fiquei em looping de ferramentas e parei. Tente pelo comando digitado."

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
                    # O comando local também entra na memória. É o caso mais
                    # comum — "pesquisa da Medusa" nem chega ao Gemini —, e sem
                    # isto o "e o roteiro dela?" seguinte cairia num modelo que
                    # nunca ouviu falar da Medusa.
                    self._lembrar(texto, resposta)
                    self.falar(resposta)
                    return
            self.falar(self._perguntar_gemini(texto))
        except Exception as e:  # noqa: BLE001
            self.falar(f"Falhou: {str(e)[:120]}")

    # ---------- ouvidos (Vosk) ----------

    def _ao_atalho_global(self) -> None:
        """Ctrl+Espaço: abre a escuta sem exigir a palavra de ativação.

        Também interrompe a leitura, pela mesma razão das palmas: o gesto
        mais fácil de alcançar tem que ser o que faz ele calar a boca.
        """
        from tools import leitura as _leitura

        if _leitura.lendo():
            self.ui.write_log("SYS: Ctrl+Espaço — " + _leitura.parar())
            return
        if self.ui.muted:
            # Mudo é uma decisão dele; a tecla avisa em vez de desfazer calada.
            self.ui.write_log("SYS: Ctrl+Espaço — o microfone está mudo.")
            return
        self._abrir_janela()
        self.ui.write_log(
            f"SYS: Ctrl+Espaço — pode falar, sem dizer o nome "
            f"({int(JANELA_CONVERSA)}s)."
        )

    def _ao_bater_palmas(self) -> None:
        # Lendo? As palmas interrompem. É a saída física para calar uma
        # leitura de 27 minutos sem depender do microfone entender "parar"
        # por cima da própria voz saindo dos alto-falantes.
        from tools import leitura as _leitura

        if _leitura.lendo():
            self.ui.write_log("SYS: duas palmas — " + _leitura.parar())
            return
        self.ui.write_log("SYS: duas palmas — trazendo a janela para a frente.")
        self.ui.trazer_para_frente()

    def _callback(self, indata, frames, tempo, status):
        dados = bytes(indata)
        # As palmas são ouvidas SEMPRE — inclusive enquanto o OMEGA fala. O
        # gesto é a saída física para interromper uma leitura longa, e antes
        # ele morria aqui junto com o resto do áudio.
        self._palmas.alimentar(dados)

        if self.ui.muted:
            return

        if self._falando.is_set():
            # Durante uma LEITURA o microfone continua aberto: sem isso o
            # "parar" nunca era ouvido, porque o OMEGA passava minutos
            # falando de boca cheia e surdo. Fora da leitura seguimos surdos
            # de propósito, senão ele transcreve a própria voz nos alto-falantes.
            from tools import leitura as _leitura

            if not _leitura.lendo():
                return

        self._fila.put(dados)

    def run(self) -> None:
        from tools import transcritor

        self.ui.write_log("SYS: carregando reconhecimento de fala (Whisper)...")
        try:
            _modelo, dispositivo = transcritor.carregar()
        except Exception as e:  # noqa: BLE001
            self.ui.write_log(f"ERR: não consegui carregar o Whisper: {str(e)[:70]}")
            return
        detector = transcritor.DetectorDeFala(TAXA)

        self.ui.write_log(
            f"SYS: OMEGA ouvindo ({dispositivo.upper()}). Comece a frase com 'Omega'."
        )
        if not self.ui.muted:
            self.ui.set_state("LISTENING")

        try:
            entrada = sd.RawInputStream(
                samplerate=TAXA,
                blocksize=BLOCO,
                dtype="int16",
                channels=1,
                callback=self._callback,
            )
        except Exception as e:  # noqa: BLE001 — sem placa, driver ausente, ocupada
            # Abrir o stream é o ÚNICO teste honesto: o ALSA anuncia um
            # dispositivo "default" mesmo numa máquina sem áudio, então
            # perguntar antes devolve "tem microfone" e mente.
            # Sem microfone o OMEGA não fica inútil: o campo de comando já está
            # ligado desde o __init__ e a janela continua servindo por texto.
            self.ui.write_log(
                f"SYS: microfone indisponível ({str(e)[:60]}) — MODO DIGITADO. "
                "Use o campo de comando ('ajuda' lista tudo)."
            )
            return

        with entrada:
            while not self._parar.is_set():
                try:
                    dados = self._fila.get(timeout=0.5)
                except queue.Empty:
                    continue
                # O Whisper transcreve a frase INTEIRA, não pedaço a pedaço
                # como o Vosk: o detector acumula até o silêncio fechar.
                trecho = detector.alimentar(dados)
                if trecho is None:
                    continue
                self.ui.set_state("THINKING")
                try:
                    frase = transcritor.transcrever(trecho).strip()
                except Exception as e:  # noqa: BLE001
                    self.ui.write_log(f"ERR: transcrição falhou ({str(e)[:50]})")
                    continue
                finally:
                    if not self.ui.muted and not self._falando.is_set():
                        self.ui.set_state("LISTENING")
                if not frase:
                    continue
                # O modelo é de português comum: nome estrangeiro e jargão do
                # canal saem deformados. Corrige antes de interpretar.
                bruta = frase
                frase = corrigir_vocabulario(frase)
                if frase != bruta:
                    self.ui.write_log(f"Você: {frase}   [ouvi: {bruta}]")
                else:
                    self.ui.write_log(f"Você: {frase}")

                # Durante a leitura o microfone fica aberto só para poder
                # parar. Tudo o mais é descartado: o que chega ali é, na
                # maioria das vezes, o eco da própria voz nos alto-falantes.
                from tools import leitura as _leitura

                if _leitura.lendo():
                    if _E_PARADA.search(_sem_acento(frase.lower())):
                        self.ui.write_log(_leitura.parar())
                    continue

                comando = self._extrair_comando(frase)

                if comando is None:
                    # Não era para o OMEGA. Avisa DISCRETAMENTE no log em vez
                    # de sumir: sem isso parece que o app está quebrado.
                    self.ui.write_log("   (ignorado — comece com 'Omega')")
                    continue

                self._abrir_janela()
                if not comando:
                    self.falar("Pois não, senhor?")
                    continue
                self.processar_texto(comando)

    # ---------- palavra de ativação ----------

    def _abrir_janela(self) -> None:
        self._janela_ate = time.monotonic() + JANELA_CONVERSA

    def _extrair_comando(self, frase: str) -> str | None:
        """Decide o que fazer com uma frase transcrita.

        None  -> não era para o OMEGA (ignorar)
        ""    -> chamaram só o nome (responder "pois não?")
        texto -> o comando em si
        """
        palavras = frase.split()
        if not palavras:
            return None

        # Já estamos conversando: não exige o nome de novo.
        if time.monotonic() < getattr(self, "_janela_ate", 0.0):
            return frase.strip(" ,.")

        # O nome pode não ser a primeira palavra — o Vosk gruda ruído antes.
        for i, palavra in enumerate(palavras[:MARGEM_DESPERTAR]):
            limpa = _sem_acento(palavra.lower().strip(",.!?;:¿¡"))
            # Semelhança em vez de igualdade: o modelo entrega "alta",
            # "elfa", "auf" para a mesma palavra falada. Exigir a grafia
            # exata fazia o OMEGA parecer surdo ao próprio nome.
            if limpa in DESPERTAR or any(
                SequenceMatcher(None, limpa, nome).ratio() >= 0.75
                for nome in ("omega", "ômega")
            ):
                return " ".join(palavras[i + 1:]).strip(" ,.")
        return None

    def stop(self) -> None:
        self._parar.set()
