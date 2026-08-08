"""Omega Voice — o Omega do canal WhoIAm.

UI (rosto/HUD PyQt6) herdada do Mark-XXXIX; motor de voz OpenAI Realtime;
ferramentas focadas no pipeline do canal (Alpha Studio + Claude Code).
Rodar: python main.py   (ou run.bat)
"""

from __future__ import annotations

import asyncio
import json
import sys
import threading
from pathlib import Path

from ui import OmegaUI
from realtime_engine import RealtimeEngine
from free_engine import FreeEngine
from tools import studio_control, pipeline_criatura, handle_local_command
from tools.local_commands import handle as _local
from tools.notify import definir_notificador

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config" / "api_keys.json"

INSTRUCTIONS = """Você é o OMEGA do canal WhoIAm — o assistente de produção de vídeos
de mitologia e criaturas do Samuel. Fale SEMPRE em português do Brasil,
trate o usuário por "senhor", seja conciso e direto como o OMEGA do Homem
de Ferro (uma ou duas frases quando possível, leve ironia elegante é bem-vinda).

TUDO O QUE VOCÊ RESPONDE É FALADO EM VOZ ALTA. Escreva como se fala: nada de
markdown, asterisco, marcador ou numeração — a voz lê os símbolos. Quando a
resposta for uma lista, diga "primeiro… segundo…" em frases corridas, e deixe
o detalhe para a tela.

Suas capacidades reais são as ferramentas:
- studio_control: controla o Alpha Studio (lista projetos de vídeo, analisa
  clipes+narração, renderiza vídeo completo ou Short, consulta progresso,
  abre o projeto no navegador).
- pipeline_criatura: dispara o Claude Code para pesquisar uma criatura nova
  (fase pesquisa → dossiê) ou gerar roteiro e prompts (fase producao).
  Custa minutos e créditos: só dispare quando o senhor pedir para PRODUZIR
  algo que ainda não existe. action 'cancelar' aborta o que estiver em curso.
- exibir: mostra conteúdo NA PRÓPRIA TELA do Omega — dossiê, roteiro,
  prompts ou o vídeo renderizado. Use quando o senhor pedir para VER algo.
- ler: lê um documento em voz alta, do começo ao fim. Use quando ele pedir
  para OUVIR — "me lê", "narra", "conta". `voz='boa'` quando ele disser
  narrar/interpretar/com emoção; `voz='comum'` no resto.
  NÃO tente recitar o documento você mesmo: chame a ferramenta, que ela lê
  por blocos e obedece a "parar". E NUNCA confunda um pedido de LEITURA com
  um pedido de PRODUÇÃO — "narre a pesquisa" é ler o que já existe, jamais
  gerar roteiro novo. Na dúvida entre ler e produzir, pergunte.
- parar_leitura: interrompe a leitura em curso.
- gravar_aula: começa, para e consulta a gravação da aula do curso. Use
  sempre que o senhor mandar iniciar ou encerrar, dito de qualquer jeito.
  NUNCA diga que parou sem chamar a ferramenta — e se ele perguntar se a aula
  foi gravada, consulte 'situacao' em vez de responder de memória.
- trecho_recente: transcreve o último minuto e meio da AULA que está sendo
  gravada. Use quando o senhor perguntar o que o professor acabou de dizer,
  ou pedir para explicar/repetir o que passou agora no vídeo.
- tendencias: busca AGORA o que está sendo procurado (autocomplete do YouTube
  + Google Trends), já separando o que o canal ainda não tem. Use quando ele
  perguntar o que está em alta ou sobre o que fazer o próximo vídeo. É sinal
  de busca, não garantia de alcance — não prometa resultado.
- avaliar_seo: confere um título/descrição/plano de postagem contra as regras
  do curso de YouTube que ele aprovou. Use SEMPRE que ele propuser um título
  ou pedir opinião de SEO, mesmo sem citar o curso — foi para isso que ele
  assistiu às aulas. Cite a aula e o minuto; se nenhuma regra cobrir o caso,
  diga que o curso não falou disso em vez de opinar por conta própria.
- apagar: remove projetos ou renders, SEMPRE em dois passos. Primeiro
  'preparar' (só mostra o que seria apagado), leia em voz alta o que será
  removido, e só chame 'confirmar' DEPOIS que o senhor confirmar de viva voz.
  Jamais confirme sozinho, mesmo que o pedido pareça óbvio.
- conferir: consulta a internet AGORA para checar um fato pontual. Use
  sempre que o senhor perguntar algo verificável e você não tiver certeza —
  é melhor conferir do que responder de memória.

SOBRE FATOS: este canal publica o que você diz. Nunca afirme data, origem ou
autoria de memória: ou você confere e cita a fonte, ou diz que não sabe.
"Não consegui confirmar" é uma resposta aceitável; inventar não é.

Não confunda as duas profundidades: `conferir` é a checagem de segundos, e
`pipeline_criatura` com phase 'pesquisa' é a apuração de verdade, que é o que
alimenta roteiro. Diga qual das duas você usou.

NUNCA finja que executou algo — sempre chame a ferramenta. Se uma ferramenta
retornar erro, leia o erro para o usuário com sinceridade. Os projetos vivem
nas pastas Criaturas (Medusa, Baba Yaga, Cthulhu, Sobek...) e Animes."""

TOOLS = [
    {
        "type": "function",
        "name": "studio_control",
        "description": (
            "Controla o Alpha Studio (editor de vídeo do canal). Ações: "
            "list_projects (listar projetos), analyze (analisar clipes e narração, "
            "gera o plano de edição), render_full (renderizar vídeo completo), "
            "render_short (renderizar Short curto), status (progresso dos renders), "
            "open (abrir o projeto no navegador)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "list_projects",
                        "analyze",
                        "render_full",
                        "render_short",
                        "status",
                        "open",
                    ],
                },
                "project": {
                    "type": "string",
                    "description": "Nome falado do projeto/criatura, ex.: 'medusa'",
                },
                "target_seconds": {
                    "type": "number",
                    "description": "Duração alvo do Short em segundos (padrão 30)",
                },
            },
            "required": ["action"],
        },
    },
    {
        "type": "function",
        "name": "exibir",
        "description": (
            "Mostra conteúdo na tela do Omega: o dossiê da pesquisa, o "
            "roteiro de narração, os prompts, ou reproduz o vídeo renderizado. "
            "Use para qualquer pedido de ver/ler/mostrar/assistir."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "tipo": {
                    "type": "string",
                    "enum": ["dossie", "roteiro", "prompts", "video", "projetos"],
                },
                "criatura": {
                    "type": "string",
                    "description": "Nome da criatura (não precisa para 'projetos')",
                },
            },
            "required": ["tipo"],
        },
    },
    {
        "type": "function",
        "name": "apagar",
        "description": (
            "Apaga coisas do projeto, SEMPRE em dois passos. Use acao "
            "'preparar' com o alvo ('projeto Pennywise', 'renders da Medusa') "
            "para MOSTRAR o que seria apagado — isso nao apaga nada. Só depois "
            "que o usuário disser que confirma, chame acao 'confirmar'. "
            "Nunca chame 'confirmar' por conta própria."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "acao": {
                    "type": "string",
                    "enum": ["preparar", "confirmar", "cancelar"],
                },
                "alvo": {
                    "type": "string",
                    "description": "O que apagar, ex.: 'projeto Pennywise'",
                },
            },
            "required": ["acao"],
        },
    },
    {
        "type": "function",
        "name": "pipeline_criatura",
        "description": (
            "Dispara o Claude Code para trabalhar numa criatura nova do canal. "
            "phase 'pesquisa' = monta o dossiê (fase 0); phase 'producao' = gera "
            "roteiro e prompts a partir do dossiê (fases 1-2). action 'status' "
            "consulta o andamento e action 'cancelar' ABORTA o que está em "
            "curso — use assim que o senhor disser que não quer mais, sem "
            "argumentar que já começou."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {"type": "string",
                           "enum": ["start", "status", "cancelar"]},
                "creature": {"type": "string", "description": "Nome da criatura"},
                "phase": {"type": "string", "enum": ["pesquisa", "producao"]},
            },
            "required": ["action"],
        },
    },
    {
        "type": "function",
        "name": "ler",
        "description": (
            "Lê um documento do projeto EM VOZ ALTA, inteiro, por blocos. "
            "Use quando o senhor pedir para ouvir: 'me lê a pesquisa da X', "
            "'narra o roteiro da X', 'conta a pesquisa'. "
            "Isto LÊ o que já existe — nunca gera nada novo. Se o documento "
            "não existir, diga isso; não ofereça produzir sem ele pedir."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "criatura": {"type": "string",
                             "description": "Nome da criatura/projeto."},
                "tipo": {"type": "string",
                         "enum": ["pesquisa", "roteiro", "cenas"],
                         "description": "O que ler. Padrão: pesquisa."},
                "voz": {
                    "type": "string",
                    "enum": ["comum", "boa"],
                    "description": (
                        "'comum' = voz do Windows, grátis e ilimitada. "
                        "'boa' = ElevenLabs, com emoção, mas gasta créditos "
                        "de uma cota mensal pequena — use quando ele disser "
                        "narrar, interpretar, ou pedir emoção/impacto."
                    ),
                },
            },
            "required": ["criatura"],
        },
    },
    {
        "type": "function",
        "name": "parar_leitura",
        "description": "Interrompe a leitura em voz alta que está em curso.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "type": "function",
        "name": "tendencias",
        "description": (
            "Busca AGORA o que as pessoas estão procurando, para escolher a "
            "próxima criatura do canal: autocomplete do YouTube (o que se "
            "digita lá) e consultas em ascensão do Google Trends. Já separa o "
            "que o canal ainda não tem. Use quando o senhor perguntar o que "
            "está em alta, o que postar, sobre o que fazer o próximo vídeo, "
            "ou pedir para olhar o Google Trends. Deixe o parâmetro vazio "
            "para varrer os temas do canal, ou passe um assunto específico."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "assunto": {
                    "type": "string",
                    "description": "Tema para aprofundar; vazio varre o canal.",
                },
            },
        },
    },
    {
        "type": "function",
        "name": "avaliar_seo",
        "description": (
            "Confere um título, descrição, thumbnail ou plano de postagem "
            "contra as REGRAS DO CURSO de YouTube que o senhor aprovou. "
            "Use SEMPRE que ele propuser um título/descrição, pedir opinião "
            "sobre SEO, ou perguntar quando/como postar — mesmo que ele não "
            "cite o curso. É para isso que ele assistiu às aulas: para você "
            "lembrar do que ele esqueceu, e discordar quando for o caso. "
            "Cite a aula e o minuto ao concordar ou discordar."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "proposta": {
                    "type": "string",
                    "description": "O título/descrição/plano que ele propôs.",
                },
            },
            "required": ["proposta"],
        },
    },
    {
        "type": "function",
        "name": "gravar_aula",
        "description": (
            "Controla a gravação da aula do curso. 'iniciar' começa a gravar "
            "o som do PC e a tirar print da tela; 'parar' encerra e deixa a "
            "aula pronta para processar; 'situacao' diz se está gravando e há "
            "quanto tempo. Use SEMPRE que o senhor mandar começar ou parar a "
            "aula, de qualquer jeito que ele diga — 'pode parar de gravar', "
            "'a aula acabou', 'encerra isso aí'. NUNCA responda que parou sem "
            "chamar esta ferramenta: quem grava é ela, não você."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "acao": {"type": "string",
                         "enum": ["iniciar", "parar", "situacao"]},
                "titulo": {"type": "string",
                           "description": "Nome da aula, só para 'iniciar'."},
            },
            "required": ["acao"],
        },
    },
    {
        "type": "function",
        "name": "trecho_recente",
        "description": (
            "Transcreve o último minuto e meio da AULA que está sendo gravada "
            "e devolve o texto. Use quando o senhor perguntar o que o "
            "professor acabou de dizer, pedir para repetir, explicar ou "
            "resumir o que passou agora. Responda com base NO TEXTO devolvido; "
            "se vier vazio, diga que não pegou o trecho."
        ),
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "type": "function",
        "name": "conferir",
        "description": (
            "Consulta a internet AGORA para confirmar um fato pontual (uma "
            "data, uma origem, uma grafia, se algo é verdade). Devolve os "
            "trechos das fontes; responda em uma ou duas frases CITANDO a "
            "fonte. Se voltar 'NADA ENCONTRADO', diga que não conseguiu "
            "confirmar — nunca preencha a lacuna de memória. "
            "NÃO use para montar dossiê nem material de roteiro: para isso "
            "existe pipeline_criatura com phase 'pesquisa', que apura de "
            "verdade. Esta aqui é a checagem rápida."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "pergunta": {
                    "type": "string",
                    "description": "O que precisa ser confirmado.",
                },
            },
            "required": ["pergunta"],
        },
    },
]

def make_tool_executor(ui):
    """A ferramenta `exibir` precisa da UI, então o executor é uma closure."""

    def exibir(args: dict) -> str:
        tipo = (args.get("tipo") or "").strip()
        criatura = (args.get("criatura") or "").strip()
        comando = tipo if tipo == "projetos" else f"{tipo} {criatura}"
        resposta = _local(comando, ui)
        return resposta or f"Não consegui exibir {tipo} de {criatura}."

    def apagar(args: dict) -> str:
        from tools import apagar as mod

        acao = (args.get("acao") or "preparar").strip()
        if acao == "confirmar":
            return mod.confirmar()
        if acao == "cancelar":
            return mod.cancelar()
        return mod.preparar(args.get("alvo") or "")

    def conferir(args: dict) -> str:
        from tools import web

        pergunta = (args.get("pergunta") or "").strip()
        ui.write_log(f"SYS: conferindo na web — {pergunta}")
        return web.conferir(pergunta)

    def ler(args: dict) -> str:
        """Lê um documento em voz alta.

        Passa pelo MESMO caminho do comando digitado (`local_commands`), para
        não existirem duas implementações de leitura divergindo. O verbo é
        montado aqui: "ler" usa a voz grátis, "narrar" a da ElevenLabs.
        """
        criatura = (args.get("criatura") or "").strip()
        tipo = (args.get("tipo") or "pesquisa").strip()
        verbo = "narrar" if (args.get("voz") or "comum") == "boa" else "ler"
        if not criatura:
            return "Preciso saber de qual criatura."
        resposta = _local(f"{verbo} {tipo} {criatura}", ui)
        return resposta or f"Não achei {tipo} de {criatura}."

    def parar_leitura(_args: dict) -> str:
        from tools import leitura as mod

        return mod.parar()

    def tendencias(args: dict) -> str:
        from tools import tendencias as mod

        assunto = (args.get("assunto") or "").strip()
        ui.write_log(f"SYS: buscando tendências{f' — {assunto}' if assunto else ''}...")
        return mod.pesquisar(assunto)

    def avaliar_seo(args: dict) -> str:
        from tools import curso

        return curso.avaliar(args.get("proposta") or "")

    def gravar_aula(args: dict) -> str:
        from tools import aula

        acao = (args.get("acao") or "situacao").strip()
        if acao == "iniciar":
            return aula.iniciar(aula.curso_atual(),
                                (args.get("titulo") or "").strip() or "aula sem nome",
                                avisar=ui.write_log)
        if acao == "parar":
            return aula.parar()
        return aula.situacao()

    def trecho_recente(_args: dict) -> str:
        from tools import aula, transcritor

        if not aula.gravando():
            return ("Não estou gravando aula nenhuma. Diga 'assistir <nome da "
                    "aula>' antes de começar o vídeo.")
        audio = aula.trecho_recente()
        if len(audio) < 2 * 16000:  # menos de 1 segundo
            return "Ainda não tenho áudio suficiente da aula."
        ui.write_log("SYS: transcrevendo o trecho recente da aula...")
        texto = transcritor.transcrever(audio)
        if not texto:
            return "Não consegui entender o trecho — talvez estivesse em silêncio."
        return f"O QUE O PROFESSOR DISSE NOS ÚLTIMOS {len(audio)//2//16000}s:\n{texto}"

    impls = {
        "studio_control": studio_control,
        "pipeline_criatura": pipeline_criatura,
        "exibir": exibir,
        "apagar": apagar,
        "conferir": conferir,
        "trecho_recente": trecho_recente,
        "gravar_aula": gravar_aula,
        "avaliar_seo": avaliar_seo,
        "tendencias": tendencias,
        "ler": ler,
        "parar_leitura": parar_leitura,
    }

    def execute_tool(name: str, args: dict) -> str:
        impl = impls.get(name)
        if impl is None:
            return f"Ferramenta desconhecida: {name}"
        try:
            return impl(args)
        except Exception as e:  # noqa: BLE001 — o modelo lê o erro em voz alta
            return f"A ferramenta {name} falhou: {str(e)[:150]}"

    return execute_tool


def ligar_avisos(ui, engine=None) -> None:
    """Liga o canal de aviso das ferramentas na janela.

    As tarefas longas (pesquisa, render) rodam em thread e não conhecem a UI;
    elas publicam em `tools.notify` e é aqui que isso vira log — e voz, nos
    marcos. `ui.write_log` emite um sinal Qt, então é seguro entre threads.
    """

    def notificador(texto: str, *, falar: bool) -> None:
        ui.write_log(f"OMEGA: {texto}" if falar else f"SYS: {texto}")
        # Só o motor gratuito sabe falar um texto arbitrário; o Realtime fala
        # pelo próprio modelo, então ali o aviso fica no log.
        if falar and engine is not None and hasattr(engine, "falar"):
            engine.falar(texto)

    definir_notificador(notificador)


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8-sig"))


def openai_tem_saldo(key: str) -> bool:
    """Sonda barata: uma resposta de 1 token revela se a conta tem crédito.
    Sem isso o app só descobriria a falta de saldo ao abrir o WebSocket da
    Realtime, que fecha a conexão inteira (nem ouvir funciona)."""
    if not key:
        return False
    try:
        import requests

        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "."}],
                "max_tokens": 1,
            },
            timeout=20,
        )
        return r.status_code == 200
    except Exception:  # noqa: BLE001 — sem rede = sem Realtime
        return False


def escolher_motor(cfg: dict) -> str:
    """Qual motor de voz usar.

    'live'     — Gemini Live: o senhor fala e ele ouve o ÁUDIO, sem
                 transcrição no meio. É o mais natural e é gratuito, mas a
                 cota da camada gratuita estoura com frequência.
    'realtime' — OpenAI Realtime: equivalente, porém pago (a conta está sem
                 saldo hoje).
    'free'     — Whisper local + Gemini texto + voz do Windows. Menos fluido,
                 mas funciona offline e não depende de cota nenhuma.

    O padrão 'auto' tenta o Live primeiro e cai para o local sozinho. A queda
    não é hipótese: a mesma cota que dá 429 no dia a dia derruba a sessão de
    voz, e sem o local por baixo o OMEGA ficaria mudo quando isso acontecer.
    """
    modo = (cfg.get("engine") or "auto").strip().lower()
    if modo in ("free", "realtime", "live"):
        return modo
    if cfg.get("gemini_api_key"):
        return "live"
    return "realtime" if openai_tem_saldo(cfg.get("openai_api_key", "")) else "free"


def main() -> None:
    cfg = load_config()
    ui = OmegaUI(str(BASE_DIR / "face.png"))

    def runner():
        ui.wait_for_api_key()
        motor = escolher_motor(cfg)

        if motor == "live":
            from live_engine import LiveEngine

            ui.write_log("SYS: voz em tempo real (Gemini Live) — abrindo...")
            engine = LiveEngine(
                gemini_key=cfg.get("gemini_api_key", ""),
                instructions=INSTRUCTIONS,
                tool_executor=make_tool_executor(ui),
                ui=ui,
                local_handler=handle_local_command,
                tools=TOOLS,
            )
            ligar_avisos(ui, engine)
            try:
                if engine.run():
                    return
            except KeyboardInterrupt:
                print("\nEncerrando...")
                return
            # Caiu. Em vez de morrer, continua no motor local — e diz por quê,
            # senão a troca de voz no meio do dia parece defeito.
            ui.write_log(
                f"SYS: {engine.motivo_da_queda or 'a voz em tempo real não abriu'}"
                " — seguindo pelo motor local (Whisper + Gemini + voz do Windows)."
            )
            motor = "free"

        if motor == "free":
            ui.write_log("SYS: motor GRATUITO (Vosk + Gemini + voz do Windows).")
            engine = FreeEngine(
                gemini_key=cfg.get("gemini_api_key", ""),
                instructions=INSTRUCTIONS,
                tool_executor=make_tool_executor(ui),
                ui=ui,
                local_handler=handle_local_command,
                # As MESMAS ferramentas da Realtime: sem elas o Gemini só
                # conversava e dizia ter executado o que nunca rodou.
                tools=TOOLS,
            )
            ligar_avisos(ui, engine)
            try:
                engine.run()  # o motor gratuito já trata local antes do Gemini
            except KeyboardInterrupt:
                print("\nEncerrando...")
            return

        ui.write_log("SYS: motor OpenAI Realtime (voz nativa).")
        engine = RealtimeEngine(
            api_key=cfg.get("openai_api_key", ""),
            instructions=INSTRUCTIONS,
            tools=TOOLS,
            tool_executor=make_tool_executor(ui),
            ui=ui,
        )
        ligar_avisos(ui, engine)

        # O campo de texto tenta primeiro os comandos locais (funcionam sem
        # créditos e sem internet); só o que não for comando conhecido vai
        # para o modelo de voz.
        para_a_voz = ui.on_text_command

        def on_text(texto: str) -> None:
            try:
                resposta = handle_local_command(texto, ui)
            except Exception as e:  # noqa: BLE001
                ui.write_log(f"ERR: {str(e)[:110]}")
                return
            if resposta is not None:
                ui.write_log(f"» {resposta}")
                return
            para_a_voz(texto)

        ui.on_text_command = on_text
        ui.write_log("SYS: modo local pronto — digite 'ajuda' para os comandos.")

        try:
            asyncio.run(engine.run())
        except KeyboardInterrupt:
            print("\nEncerrando...")

    threading.Thread(target=runner, daemon=True).start()
    ui.root.mainloop()


if __name__ == "__main__":
    main()
