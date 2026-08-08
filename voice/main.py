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

Suas capacidades reais são as ferramentas:
- studio_control: controla o Alpha Studio (lista projetos de vídeo, analisa
  clipes+narração, renderiza vídeo completo ou Short, consulta progresso,
  abre o projeto no navegador).
- pipeline_criatura: dispara o Claude Code para pesquisar uma criatura nova
  (fase pesquisa → dossiê) ou gerar roteiro e prompts (fase producao).
- exibir: mostra conteúdo NA PRÓPRIA TELA do Omega — dossiê, roteiro,
  prompts ou o vídeo renderizado. Use SEMPRE que o usuário pedir para ver,
  ler, mostrar ou assistir algo; nunca leia um documento inteiro em voz alta,
  exiba na tela e comente em uma frase.
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
            "consulta o andamento."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["start", "status"]},
                "creature": {"type": "string", "description": "Nome da criatura"},
                "phase": {"type": "string", "enum": ["pesquisa", "producao"]},
            },
            "required": ["action"],
        },
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

    impls = {
        "studio_control": studio_control,
        "pipeline_criatura": pipeline_criatura,
        "exibir": exibir,
        "apagar": apagar,
        "conferir": conferir,
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
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


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
