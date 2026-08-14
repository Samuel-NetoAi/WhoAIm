"""Dispara as fases 0-2 do canal (pesquisa/roteiro/prompts) via Claude Code CLI.

O trabalho criativo pesado continua sendo do Claude (skills pesquisa-seres e
whoiam) — esta ferramenta só é a ponte por voz. Roda em thread própria porque
uma pesquisa completa leva minutos; o resultado cai em notes/ do projeto.
"""

from __future__ import annotations

import os
import platform
import re
import shutil
import subprocess
import threading
import time
import unicodedata
from pathlib import Path

from .notify import batimento, duracao_falada, notificar
from .vocabulario import mesma_criatura

# Mesma variável que o Studio usa (lib/projects/constants.ts), para as duas
# metades do sistema concordarem sobre onde os projetos vivem. O padrão é a
# máquina principal; no Linux, exportar AI_PROJECT_ROOT.
AI_PROJECT_ROOT = Path(os.environ.get("AI_PROJECT_ROOT") or r"C:\Ai-Project")

E_WINDOWS = platform.system() == "Windows"

# ── Kairogen: geração de imagem nas fases 1 e 2 ───────────────────────────
#
# O ESCOPO ESTÁ TRAVADO NA LISTA, NÃO NA INTENÇÃO. O Samuel decidiu que o
# Kairogen entra só como gerador de IMAGEM; o vídeo ele produz à parte,
# porque a cadência que ele quer para o canal não cabe no orçamento de
# vídeo hoje. Por isso os nomes vão UM A UM e `generate_video` NÃO está
# entre eles. Em modo headless o CLI recusa toda ferramenta fora do
# --allowedTools, então a decisão fica garantida pelo código — não depende
# de o modelo se lembrar dela no meio de catorze blocos.
#
# O MODELO É FIXO POR CAUSA DE DINHEIRO. Medido em 13/08/2026 no plano
# PRECISION, com geração real e não com tabela de preço: `z-image-turbo`
# devolve `cost_credits: 0` e o saldo não se move (1780 -> 1780, status
# COMPLETED). Os outros vinte modelos de imagem custam de 1 a 13 créditos
# cada. Model sheet se acerta na tentativa, não na primeira — então o padrão
# tem que ser o ilimitado, ou uma noite de iteração come a reserva do mês.
#
# CUIDADO AO MEXER: `estimate_cost` devolve o preço de TABELA do modelo, que
# ignora a isenção do plano. Ele disse "1 crédito" para o z-image-turbo e
# estava errado sobre a cobrança real. Para saber se algo custa, gere e
# compare `get_credits` antes e depois — não pergunte ao estimador.
KAIROGEN_MODELO_IMAGEM = "z-image-turbo"

# `download_image_from_url` NÃO entra aqui, de propósito. Testado em
# 13/08/2026: ela grava 96 bytes de base64 de um PNG 1x1 — o placeholder
# transparente — e ainda relata sucesso. A imagem real está intacta no CDN
# (1024x1024, 1,3 MB) e baixa com um curl simples, sem autenticação. Então o
# download sai pelo Bash, que já está liberado e que eu consigo conferir.
# Sem esse teste, a fase 2 entregaria catorze painéis de 96 bytes.
KAIROGEN_FERRAMENTAS = (
    "mcp__kairogen__generate_image",
    "mcp__kairogen__get_generation",
    "mcp__kairogen__get_credits",
    "mcp__kairogen__estimate_cost",
)

# Abaixo disto o arquivo não é imagem — é mensagem de erro ou placeholder.
# Uma geração de verdade do z-image-turbo deu 1,3 MB.
KAIROGEN_MINIMO_BYTES = 10_000

# Teto do plano PRECISION (get_me_context, 14/08/2026). Vale mandar em lote
# até esse número: catorze painéis de storyboard saem em duas levas em vez
# de catorze esperas em fila.
KAIROGEN_IMAGENS_SIMULTANEAS = 8

# OS SLOTS DE PERSONAGEM NÃO SERVEM (ainda). Pareciam a resposta para a
# consistência entre a fase 1 e a fase 2 — "identidade fixa, reutilizável em
# todas as gerações", dez slots no plano. Medido em 14/08/2026:
#
#   1. `characters_generate_images` com o modelo gratuito devolve
#      GENERATION_QUOTE_MISMATCH nos modos síncrono E assíncrono. A própria
#      mensagem diz "o custo mudou para 0 créditos" — a ferramenta cota 3, o
#      backend recota 0, e ela não atualiza a própria cotação. Trava deles.
#   2. Sem o override, ela cai no `nano-banana-2`: 11 créditos por leva de 4
#      candidatos, e ainda faltariam os ângulos.
#
# Ou seja: personagem só roda gastando crédito, e crédito aqui é o recurso
# escasso. Enquanto for assim, a consistência continua saindo do model sheet
# em texto, que é o contrato que a whoiam já usa e que custa zero. Revisitar
# quando a Kairogen consertar a cotação.


def _instrucao_render(pasta: Path) -> str:
    """O trecho que manda renderizar de verdade, e não só descrever.

    `generate_image` é ASSÍNCRONO: devolve `QUEUED` com um id e nada mais. Sem
    a instrução de consultar `get_generation` até `COMPLETED`, a fase termina
    "com sucesso" e o disco fica vazio — a falha mais cara possível, porque
    parece que deu certo.
    """
    return (
        " Depois de salvar o arquivo, GERE as imagens de verdade com a "
        f"ferramenta generate_image do kairogen, sempre com "
        f"model='{KAIROGEN_MODELO_IMAGEM}'. Não use outro modelo: esse é o "
        "único ilimitado do plano, e os demais gastam crédito. A geração é "
        "assíncrona — guarde o generation_id e consulte get_generation até o "
        "status ficar COMPLETED, de onde sai a output_url. "
        f"Dispare até {KAIROGEN_IMAGENS_SIMULTANEAS} gerações ao mesmo tempo "
        "(é o teto do plano) e só então fique esperando: em fila de uma em "
        "uma, catorze painéis viram catorze esperas. "
        f"BAIXE cada imagem com o Bash, assim: curl -sS -L -o {pasta}/NOME.png "
        "\"URL\" — um arquivo por imagem, com nome que case com a seção do "
        "documento. NÃO use download_image_from_url: essa ferramenta grava um "
        "placeholder de 96 bytes e mente que deu certo. "
        f"CONFIRA cada arquivo baixado com `wc -c ARQUIVO` — use wc, NÃO use "
        "ls -la: no Windows o ls mostra o número do grupo numa coluna parecida "
        "com a do tamanho, e já houve relato de 197121 bytes lendo a coluna "
        f"errada. Se o wc der menos de {KAIROGEN_MINIMO_BYTES} bytes, não é "
        "imagem — tente de novo e, se insistir, diga no fim exatamente quais "
        "não saíram. Nunca relate sucesso sem ter conferido com o wc."
    )


# Onde procurar o CLI, do mais provável ao menos. No Windows o npm instala um
# .CMD que só o PATH resolve; no Linux/macOS o instalador global costuma cair
# em ~/.local/bin.
def _resolver_claude() -> str | None:
    do_path = shutil.which("claude")
    if do_path:
        return do_path
    candidatos = [
        Path.home() / ".local" / "bin" / "claude",
        Path.home() / ".claude" / "local" / "claude",
        Path.home() / ".npm-global" / "bin" / "claude",
    ]
    if E_WINDOWS:
        appdata = os.environ.get("APPDATA")
        if appdata:
            candidatos.insert(0, Path(appdata) / "npm" / "claude.CMD")
    for c in candidatos:
        if c.exists():
            return str(c)
    return None


def _slugify(value: str) -> str:
    """Mesma regra do create-project.ts do Studio, para os caminhos baterem."""
    text = unicodedata.normalize("NFD", value.strip().lower())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def _project_dir(creature: str) -> Path:
    """Pasta que o Alpha Studio reconhece como projeto desta criatura.

    O Studio resolve notas em <root>\\Criaturas\\<Nome>\\<slug>-video\\notes,
    então a pesquisa precisa cair exatamente aí para aparecer na aba Notas.
    """
    return AI_PROJECT_ROOT / "Criaturas" / creature / f"{_slugify(creature)}-video"


# O nome falado de cada fase. Serve de rótulo E de lista do que é aceito:
# antes havia duas checagens separadas com as fases escritas à mão, e acrescentar
# uma terceira teria deixado a validação para trás em silêncio.
ROTULOS = {
    "pesquisa": "pesquisa e dossiê",
    "model-sheets": "roteiro e model sheets",
    "storyboards": "storyboards e prompts",
    "producao": "roteiro e prompts",
}


def _arquivos_da_fase(creature: str, phase: str) -> list[Path]:
    """O que cada fase promete gravar — usado para conferir se de fato gravou."""
    notes = _project_dir(creature) / "notes"
    if phase == "pesquisa":
        return [notes / "dossie.md"]
    if phase == "model-sheets":
        return [notes / "roteiro.md", notes / "model-sheets.md"]
    if phase == "storyboards":
        return [notes / "prompts.md"]
    return [notes / "roteiro.md", notes / "prompts.md"]


def _ensure_project(creature: str) -> Path:
    project = _project_dir(creature)
    for sub in ("notes", "public/videos", "public/audio"):
        (project / sub).mkdir(parents=True, exist_ok=True)
    return project

# Estado do último pipeline disparado (um por vez é suficiente por voz).
# `proc` existe para poder CANCELAR. Antes o pipeline era disparado com
# subprocess.run, que bloqueia e não deixa referência nenhuma: quando o
# Samuel disse "não precisa gerar o roteiro ainda", o OMEGA respondeu que
# não dava para parar — e era verdade. Disparar algo de minutos sem botão
# de parada é um defeito, não uma limitação.
_current: dict = {"running": False, "creature": None, "result": None,
                  "proc": None, "cancelado": False}


def _matar(proc) -> None:
    """Encerra o processo E OS FILHOS DELE.

    No Windows matar o pai não mata os filhos, e o `claude` roda por baixo de
    um .CMD que abre o node: matar só o topo deixaria o trabalho rodando
    invisível, gastando créditos depois de o Samuel ter pedido para parar.
    """
    try:
        if E_WINDOWS:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                capture_output=True, timeout=20,
            )
        else:
            proc.terminate()
    except Exception:  # noqa: BLE001
        try:
            proc.kill()
        except Exception:  # noqa: BLE001
            pass


def cancelar() -> str:
    """Aborta o pipeline em curso."""
    if not _current["running"]:
        return "Não há nada rodando para cancelar, senhor."
    criatura = _current["creature"]
    proc = _current.get("proc")
    _current["cancelado"] = True
    if proc is None:
        # Ainda não chegou a abrir o processo; a flag basta.
        return f"Vou abortar a {criatura} assim que ela começar."
    _matar(proc)
    return f"Cancelado. Parei o trabalho na {criatura}."


# Qual número de fase cada trabalho do pipeline representa. Fica aqui, e não
# em `fases.py`, para o pipeline não precisar importar o outro no topo — eles
# se conhecem em círculo (fases chama pipeline para trabalhar, pipeline chama
# fases para anotar), e o import tardio dentro da função é o que quebra o laço.
_NUMERO_DA_FASE = {"pesquisa": 0, "model-sheets": 1, "storyboards": 2,
                   "producao": 2}


def _fim_de_fase(creature: str, phase: str) -> str:
    """Anota que a fase terminou e devolve o anúncio da próxima.

    É a peça que o Samuel pediu para não decorar quarenta comandos: terminada
    uma fase, ele mesmo diz qual vem, o que ela entrega e o que precisa. E
    quando a próxima é a 0 ou a 5, entra junto o que o curso ensinou sobre
    tema, título e thumbnail — as duas fases em que ele quis o curso agindo
    sozinho.
    """
    n = _NUMERO_DA_FASE.get(phase)
    if n is None:
        return ""
    try:
        from . import curso as _curso
        from . import fases as _fases

        _fases.marcar(creature, n, _fases.PRONTA)
        recado = " " + _fases.anunciar(creature, n)
        if n == 0:
            # Fase 0 recém-fechada: é a hora de escolher ângulo e título, e é
            # exatamente onde o curso tem o que dizer.
            material = _curso.orientar(("tema", "titulo", "thumbnail"),
                                       sobre=creature)
            if material:
                # O MATERIAL VAI PARA ARQUIVO, NÃO PARA A VOZ.
                #
                # Esta frase inteira é entregue com `falar=True`. Anexar as
                # regras aqui fazia o OMEGA começar a LER EM VOZ ALTA setenta
                # e seis mil caracteres de regra, uma atrás da outra, sem ter
                # como parar. Descoberto na primeira fase 0 de verdade.
                #
                # Em arquivo, ele cai na aba Notas do Studio — onde o Samuel
                # já lê o dossiê — e continua servindo de contexto para quem
                # for escrever o título.
                arquivo = _project_dir(creature) / "notes" / "curso-fase-0.md"
                try:
                    arquivo.write_text(material, encoding="utf-8")
                    recado += (f" Trouxe {material.count(chr(10) + '## ')} "
                               "regras do curso sobre tema, título e thumbnail "
                               "— estão em Notas, em curso-fase-0.")
                except Exception:  # noqa: BLE001
                    pass
        return recado
    except Exception:  # noqa: BLE001 — anotar não pode derrubar o pipeline
        return ""


def _run_claude(creature: str, phase: str) -> None:
    notes = _ensure_project(creature) / "notes"
    prompt = {
        "pesquisa": (
            f"Use a skill pesquisa-seres para montar o dossiê completo de {creature}. "
            f"Salve o dossiê final em {notes / 'dossie.md'}."
        ),
        # PARA no checkpoint que a própria skill já tem (passo 3 do FLUXO
        # GERAL). O motivo é dinheiro e tempo: se a cara de um personagem sair
        # errada, descobrir isso depois de catorze blocos de storyboard custa
        # os catorze. O model sheet é o contrato de consistência visual que
        # todos os storyboards referenciam — ele tem que ser aprovado antes.
        "model-sheets": (
            f"Use a skill whoiam para {creature}, a partir do dossiê em "
            f"{notes / 'dossie.md'}. Faça SOMENTE até o checkpoint do passo 3 do "
            f"FLUXO GERAL: o Documento 1 (roteiro de narração) e a BÍBLIA DE "
            f"PERSONAGENS com um MODEL SHEET ultra-realista para cada "
            f"personagem recorrente. NÃO gere storyboards nem prompts Seedance "
            f"agora. Salve o roteiro em {notes / 'roteiro.md'} e os model sheets "
            f"em {notes / 'model-sheets.md'}."
            + _instrucao_render(notes / "model-sheets")
        ),
        "storyboards": (
            f"Use a skill whoiam para {creature}. O roteiro já aprovado está em "
            f"{notes / 'roteiro.md'} e os model sheets aprovados em "
            f"{notes / 'model-sheets.md'} — use os model sheets como contrato "
            f"de consistência visual, não invente aparência nova. Gere agora o "
            f"Documento 2 (storyboards) e o Documento 3 (prompts Seedance) e "
            f"salve tudo em {notes / 'prompts.md'}."
            # Os prompts Seedance continuam sendo TEXTO: o vídeo é do Samuel.
            # O que se renderiza aqui são os painéis do storyboard.
            + _instrucao_render(notes / "storyboards")
        ),
        # Atalho "gera tudo de uma vez", para quando ele confiar no personagem.
        "producao": (
            f"Use a skill whoiam para gerar o pacote de produção de {creature} "
            f"a partir do dossiê em {notes / 'dossie.md'}. "
            f"Salve o roteiro de narração em {notes / 'roteiro.md'} e todos os "
            f"prompts (model sheets, storyboards, Seedance) em {notes / 'prompts.md'}."
        ),
    }[phase]
    executavel = _resolver_claude() or "claude"
    rotulo = ROTULOS.get(phase, "roteiro e prompts")
    inicio = time.monotonic()

    # Sinal de vida: sem isto, uma pesquisa de dez minutos parece um travamento.
    batimento(
        120,
        lambda d: f"Ainda trabalhando na {rotulo} de {creature} — {duracao_falada(d)} até agora.",
        lambda: _current["running"],
    )

    try:
        proc = subprocess.Popen(
            # --allowedTools é OBRIGATÓRIO: em modo headless o CLI começa sem
            # acesso à web, e a `pesquisa-seres` existe justamente para cruzar
            # web + transcrições do YouTube. Sem isto ela "termina" em ~1
            # minuto sem pesquisar nada nem gravar arquivo — o sintoma que
            # parecia bug de caminho. Bash entra por causa do script de
            # transcrição que a skill executa.
            [
                executavel,
                "-p",
                prompt,
                "--permission-mode",
                "acceptEdits",
                "--allowedTools",
                "WebSearch",
                "WebFetch",
                "Read",
                "Write",
                "Edit",
                "Bash",
                "Glob",
                "Grep",
                # Imagem, e só imagem — ver KAIROGEN_FERRAMENTAS.
                *KAIROGEN_FERRAMENTAS,
            ],
            cwd=str(AI_PROJECT_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            # shell=True só no Windows, onde o npm instala um .CMD que precisa
            # do interpretador. No POSIX, shell=True com LISTA roda
            # `sh -c "claude"` e joga fora todos os argumentos seguintes — o
            # prompt sumiria e o Claude abriria em modo interativo, travando
            # até o timeout de 30 minutos.
            shell=E_WINDOWS,
        )
        _current["proc"] = proc
        try:
            fora, erro = proc.communicate(timeout=1800)
        except subprocess.TimeoutExpired:
            _matar(proc)
            fora, erro = proc.communicate()
            raise
        if _current["cancelado"]:
            _current["result"] = (
                f"Cancelei a {rotulo} de {creature} a seu pedido. "
                "Nada foi gravado por essa execução."
            )
            return
        saida = (fora or "") + (erro or "")
        levou = duracao_falada(time.monotonic() - inicio)

        if proc.returncode == 0:
            # Os arquivos são gravados DENTRO da pasta do projeto, que é de onde
            # o Studio lê — então "gravou" e "chegou no Studio" são a mesma
            # coisa. Dizer o arquivo por nome poupa procurar.
            arquivos = _arquivos_da_fase(creature, phase)
            escritos = [a for a in arquivos if a.exists()]
            onde = (
                "na aba Notas, em Dossiê"
                if phase == "pesquisa"
                else "na aba Notas, em Roteiro e Prompts"
            )
            if escritos:
                lista = ", ".join(a.name for a in escritos)
                _current["result"] = (
                    f"{rotulo.capitalize()} de {creature} concluída em {levou}. "
                    f"Gravei {lista} no projeto — já aparece no Studio, {onde}."
                    + _fim_de_fase(creature, phase)
                )
            else:
                # Saiu com código 0 mas não escreveu nada: dizer "concluído"
                # aqui seria mentira, e é o tipo de mentira que só se descobre
                # abrindo a aba Notas e achando-a vazia.
                _current["result"] = (
                    f"O Claude terminou a {rotulo} de {creature} em {levou}, mas "
                    "não encontrei os arquivos esperados no projeto. "
                    "Confira a aba Notas antes de seguir."
                )
        elif "Not logged in" in saida or "/login" in saida:
            _current["result"] = (
                "O Claude Code está instalado mas não está logado. "
                "Abra um terminal, rode claude, e faça o login com sua conta. "
                "Depois disso essa função passa a funcionar."
            )
        else:
            _current["result"] = (
                f"A {rotulo} de {creature} terminou com erro: {saida[-150:]}"
            )
    except subprocess.TimeoutExpired:
        _current["result"] = (
            f"A {rotulo} de {creature} passou de 30 minutos e foi interrompida."
        )
    except Exception as e:  # noqa: BLE001 — vira frase falada, nunca crash
        _current["result"] = f"Falha ao rodar o Claude Code: {str(e)[:150]}"
    finally:
        _current["running"] = False
        # Marco: este é o aviso que o usuário está esperando, então fala.
        notificar(_current["result"], falar=True)


# Quão parecidos dois nomes precisam ser para eu suspeitar que são o mesmo ser.
#
# "Cthulhu" e "Cthullhu" davam 0,93 e ainda assim passavam como criaturas
# DIFERENTES, porque `mesma_criatura` compara por sinônimo e apelido, não por
# grafia. O resultado seria um projeto novo do lado de 741 MB de imagens já
# feitas — exatamente o caso "Pennywise/IT" que este guarda existe para pegar,
# derrotado por uma letra dobrada. Nome de criatura é escrito errado o tempo
# todo, por voz e por teclado.
QUASE_O_MESMO_NOME = 0.85


def _projeto_equivalente(creature: str) -> str | None:
    """Nome de um projeto já existente que seja o MESMO ser, ou None."""
    from difflib import SequenceMatcher

    raiz = AI_PROJECT_ROOT / "Criaturas"
    if not raiz.exists():
        return None
    alvo = _slugify(creature)
    for pasta in raiz.iterdir():
        if not pasta.is_dir():
            continue
        parecido = SequenceMatcher(
            None, alvo, _slugify(pasta.name)).ratio() >= QUASE_O_MESMO_NOME
        if not mesma_criatura(creature, pasta.name) and not parecido:
            continue
        # Só conta se a pesquisa realmente existir lá.
        if (pasta / f"{_slugify(pasta.name)}-video" / "notes" / "dossie.md").exists():
            return pasta.name
    return None


def pipeline_criatura(args: dict) -> str:
    action = (args.get("action") or "start").strip()

    if action in ("cancelar", "cancel", "parar", "abortar"):
        return cancelar()

    if action == "status":
        if _current["running"]:
            return (f"Ainda estou trabalhando na criatura {_current['creature']}. "
                    "Diga 'cancelar pesquisa' se quiser que eu pare.")
        if _current["result"]:
            return _current["result"]
        return "Nenhum pipeline de criatura foi iniciado nesta sessão."

    creature = (args.get("creature") or "").strip()
    phase = (args.get("phase") or "pesquisa").strip()
    if not creature:
        return "Me diga o nome da criatura."
    if phase not in ROTULOS:
        return f"Não conheço a fase {phase}. Tenho: {', '.join(ROTULOS)}."

    # Um ser com dois nomes viraria dois projetos (foi o que aconteceu com
    # "Pennywise" e "IT"). Avisa em vez de pesquisar de novo o que já existe.
    if phase == "pesquisa" and not args.get("forcar"):
        existente = _projeto_equivalente(creature)
        if existente:
            return (
                f"Já existe pesquisa para esse ser, no projeto {existente}. "
                f"{creature} e {existente} são o mesmo. Diga 'pesquisa de novo' "
                "se quiser refazer mesmo assim."
            )

    if _resolver_claude() is None:
        return (
            "O Claude Code CLI não está instalado neste computador, então não "
            "consigo disparar a pesquisa ainda. Instale com: "
            "npm install -g @anthropic-ai/claude-code — depois disso essa "
            "função passa a funcionar. (O app de desktop do Claude não serve: "
            "o que a ferramenta chama é o comando de terminal.)"
        )

    if not AI_PROJECT_ROOT.is_dir():
        return (
            f"A pasta dos projetos não existe em {AI_PROJECT_ROOT}. "
            "Aponte a variável AI_PROJECT_ROOT para a pasta certa antes."
        )

    if _current["running"]:
        return f"Já existe um pipeline rodando para {_current['creature']}. Pergunte o status."

    _current.update({"running": True, "creature": creature, "result": None,
                     "proc": None, "cancelado": False})
    threading.Thread(target=_run_claude, args=(creature, phase), daemon=True).start()
    nome_fase = ROTULOS.get(phase, "roteiro e prompts")
    return (
        f"Iniciei a fase de {nome_fase} da criatura {creature} com o Claude. "
        "Leva alguns minutos — vou avisando o andamento e falo quando terminar."
    )
