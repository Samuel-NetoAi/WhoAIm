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

# A palavra de ativação vive em tools/despertar.py, que é a MESMA definição
# usada pelo portão do motor Live. Ter duas listas divergindo foi o que fez
# "a minha amiga falou que o filme é bom" acordar o OMEGA: "amiga" tinha
# entrado como variante na época do Vosk e virou armadilha depois.

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

# Frases que o OMEGA usa quando NÃO resolveu. É por elas que o diário de
# aprendizado sabe o que falhou — sem isto, "não entendi qual projeto" seria
# registrado como sucesso e a lista de coisas a ensinar nunca cresceria.
_NAO_RESOLVEU = (
    "não entendi", "nao entendi", "não sei", "nao sei", "falhou",
    "não consegui", "nao consegui", "recusou", "desconhecid",
    "não encontrei", "nao encontrei", "não existe", "nao existe",
)


def _deu_certo(resposta: str) -> bool:
    baixa = (resposta or "").lower()
    return bool(baixa) and not any(m in baixa for m in _NAO_RESOLVEU)

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
            try:
                registrar(self._ao_atalho_global)
            except Exception as e:  # noqa: BLE001
                # Uma tecla que não registra é um incômodo; derrubar o
                # motor por causa dela deixa o OMEGA surdo. Já aconteceu:
                # a exceção subia daqui e matava a thread inteira.
                self.ui.write_log(f"SYS: atalho global indisponível ({str(e)[:60]}).")
        # Os comandos locais precisam falar (leitura de documentos em voz
        # alta); expomos a fala pela UI para não acoplar os dois módulos.
        self.ui.falar = self.falar
        # Mesma razão: os comandos locais precisam poder zerar o assunto sem
        # conhecer o motor.
        self.ui.esquecer = self.esquecer

    # ---------- voz (SAPI / Maria pt-BR) ----------

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
                # A síntese em si vive em tools/voz_local.py: o motor Live
                # precisa exatamente da mesma coisa para ler documento, e duas
                # cópias da mesma voz divergiriam com o tempo.
                from tools import voz_local

                voz_local.falar(texto, economico=economico,
                                log=self.ui.write_log)
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
            # 220 cortava respostas com lista (tendências, comparação de regras)
            # no meio da frase, que é pior que ser breve. Isto é teto, não
            # meta: a instrução manda ser conciso, e a maioria das respostas
            # continua com duas frases.
            "generationConfig": {"maxOutputTokens": 600, "temperature": 0.7},
        }
        declaracoes = self._declaracoes()
        if declaracoes:
            corpo["tools"] = [{"functionDeclarations": declaracoes}]

        try:
            r = requests.post(
                GEMINI_URL, params={"key": self.gemini_key}, json=corpo, timeout=45
            )
        except requests.Timeout:
            # Falha de rede vira frase em português. Antes a exceção subia crua
            # e o OMEGA dizia "Falhou: HTTPSConnectionPool(host=..." em voz alta.
            raise RuntimeError("O Gemini demorou demais para responder.") from None
        except requests.RequestException:
            raise RuntimeError("Estou sem conexão com o Gemini agora.") from None
        if r.status_code == 429:
            raise RuntimeError("A cota gratuita do Gemini estourou. "
                               "Os comandos locais continuam funcionando.")
        if not r.ok:
            raise RuntimeError(f"O Gemini recusou: {r.status_code}.")
        try:
            return r.json()
        except ValueError:
            raise RuntimeError("O Gemini devolveu uma resposta ilegível.") from None

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
        bruta = getattr(self, "_ultima_bruta", "") or texto
        self._ultima_bruta = ""
        try:
            if self.local_handler:
                resposta = self.local_handler(texto, self.ui)
                if resposta is not None:
                    # O comando local também entra na memória. É o caso mais
                    # comum — "pesquisa da Medusa" nem chega ao Gemini —, e sem
                    # isto o "e o roteiro dela?" seguinte cairia num modelo que
                    # nunca ouviu falar da Medusa.
                    self._lembrar(texto, resposta)
                    self._anotar(bruta, texto, "local", _deu_certo(resposta))
                    self.falar(resposta)
                    return
            resposta = self._perguntar_gemini(texto)
            self._anotar(bruta, texto, "gemini", _deu_certo(resposta))
            self.falar(resposta)
        except Exception as e:  # noqa: BLE001
            self._anotar(bruta, texto, "erro", False)
            self.falar(f"Falhou: {str(e)[:120]}")

    def _anotar(self, bruta: str, corrigida: str, rota: str, ok: bool) -> None:
        try:
            from tools import aprendizado

            aprendizado.registrar(bruta, corrigida, rota, ok)
        except Exception:  # noqa: BLE001 — o diário nunca pode derrubar a voz
            pass

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
                # Guardado para o diário de aprendizado: o par (o que ouvi,
                # o que entendi) é o que mostra se o dicionário está
                # ajudando ou atrapalhando.
                self._ultima_bruta = bruta
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

        # O nome pode não ser a primeira palavra — o modelo gruda ruído antes.
        from tools.despertar import encontrar_nome

        chamaram, resto = encontrar_nome(frase)
        return resto if chamaram else None

    def stop(self) -> None:
        self._parar.set()
