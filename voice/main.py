"""Alpha Voice — o Alpha do canal WhoIAm.

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

from ui import AlphaUI
from realtime_engine import RealtimeEngine
from free_engine import FreeEngine
from tools import studio_control, pipeline_criatura, handle_local_command
from tools.local_commands import handle as _local
from tools.notify import definir_notificador

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config" / "api_keys.json"

INSTRUCTIONS = """Você é o ALPHA do canal WhoIAm — o assistente de produção de vídeos
de mitologia e criaturas do Samuel. Fale SEMPRE em português do Brasil,
trate o usuário por "senhor", seja conciso e direto como o ALPHA do Homem
de Ferro (uma ou duas frases quando possível, leve ironia elegante é bem-vinda).

Suas capacidades reais são as ferramentas:
- studio_control: controla o Alpha Studio (lista projetos de vídeo, analisa
  clipes+narração, renderiza vídeo completo ou Short, consulta progresso,
  abre o projeto no navegador).
- pipeline_criatura: dispara o Claude Code para pesquisar uma criatura nova
  (fase pesquisa → dossiê) ou gerar roteiro e prompts (fase producao).
- exibir: mostra conteúdo NA PRÓPRIA TELA do Alpha — dossiê, roteiro,
  prompts ou o vídeo renderizado. Use SEMPRE que o usuário pedir para ver,
  ler, mostrar ou assistir algo; nunca leia um documento inteiro em voz alta,
  exiba na tela e comente em uma frase.

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
            "Mostra conteúdo na tela do Alpha: o dossiê da pesquisa, o "
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
]

def make_tool_executor(ui):
    """A ferramenta `exibir` precisa da UI, então o executor é uma closure."""

    def exibir(args: dict) -> str:
        tipo = (args.get("tipo") or "").strip()
        criatura = (args.get("criatura") or "").strip()
        comando = tipo if tipo == "projetos" else f"{tipo} {criatura}"
        resposta = _local(comando, ui)
        return resposta or f"Não consegui exibir {tipo} de {criatura}."

    impls = {
        "studio_control": studio_control,
        "pipeline_criatura": pipeline_criatura,
        "exibir": exibir,
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
        ui.write_log(f"ALPHA: {texto}" if falar else f"SYS: {texto}")
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
    """'realtime' (OpenAI, melhor) ou 'free' (Vosk+Gemini+SAPI, custo zero).
    O padrão 'auto' testa o saldo da OpenAI e cai para o gratuito sozinho."""
    modo = (cfg.get("engine") or "auto").strip().lower()
    if modo in ("free", "realtime"):
        return modo
    return "realtime" if openai_tem_saldo(cfg.get("openai_api_key", "")) else "free"


def main() -> None:
    cfg = load_config()
    ui = AlphaUI(str(BASE_DIR / "face.png"))

    def runner():
        ui.wait_for_api_key()
        motor = escolher_motor(cfg)

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
