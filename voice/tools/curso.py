"""Transforma as aulas gravadas em REGRAS que guiam o SEO do canal.

O produto disto não é a transcrição. Transcrição de aula tem densidade
baixíssima — "então, tipo, né, beleza, vamos lá" — e um curso inteiro passa de
90 mil palavras, que não cabem em contexto nenhum e ninguém lê para estudar.

O produto é a REGRA, e o que dá valor a ela é a PROCEDÊNCIA: afirmação, porquê,
e de qual aula e minuto veio. É a fonte que permite o OMEGA dizer "o curso
falou isso na aula 4, aos 12 minutos" em vez de "eu acho" — que é exatamente a
diferença entre ajudar e atrapalhar quando o assunto é o que vai ao ar.

A transcrição fica guardada como fonte auditável: quando uma regra parecer
errada, dá para ir ao texto e ao print daquele minuto e conferir.

DOIS CUIDADOS QUE PARECEM DETALHE E NÃO SÃO:

1. MODELO PRÓPRIO. `transcritor.carregar()` guarda UM modelo em cache. Se o
   curso pedisse o turbo por ali, desalojaria o `large-v3` dos comandos e a
   escuta do OMEGA pioraria sem explicação nenhuma. Aqui carregamos uma
   instância separada e a soltamos no fim.
2. TURBO, e não o modelo grande. Medido nesta máquina: 1,7x contra 1,0x o tempo
   real — uma aula de 1 h em 35 min em vez de 63. O `large-v3` foi escolhido
   para os comandos por causa de *nome de criatura* (Orphanim, Dullhan), que
   aqui não existe: curso é prosa em português comum.
"""

from __future__ import annotations

import re
import subprocess
import threading
import time
from pathlib import Path

import numpy as np

# Importado como MÓDULO, não `from .aula import CURSOS`: importar a constante
# por valor congela o caminho no momento do import, e quem trocasse a raiz
# dos cursos em tempo de execução veria este módulo continuar olhando a
# pasta antiga — em silêncio.
from . import aula as _aula
from .notify import batimento, duracao_falada, notificar
from .pipeline import AI_PROJECT_ROOT, E_WINDOWS, _matar, _resolver_claude
from .transcritor import TAXA, VAD, _preparar_cuda, ler_wav_16k

MODELO = "large-v3-turbo"

# Quantos prints o Claude pode abrir por aula.
#
# O Samuel escolheu extrair das 38 aulas "a fundo", e "a fundo" não pode
# significar ler 96 imagens de uma aula só: são 1.595 prints no curso inteiro,
# e leitura de imagem é o item mais caro da conta — dominaria tudo o resto.
# Dez cobre os momentos em que a tela É o conteúdo (exemplo de título,
# thumbnail, gráfico de CTR), que é para isso que o print existe. O nome do
# arquivo é o segundo da aula, então a escolha pode ser guiada pela
# transcrição em vez de ser uma varredura cega.
TETO_TELAS = 10

# Abaixo disto o CLI nem chegou a trabalhar: uma extração de verdade leva
# minutos, então voltar em segundos só acontece quando ele recusa de saída.
RECUSA_INSTANTANEA = 30.0

# As decisões que uma regra pode governar. Fixas de propósito: é por elas que a
# consolidação agrupa 38 aulas por assunto, e vocabulário livre viraria vinte
# sinônimos de "título".
DECISOES = ("titulo", "thumbnail", "descricao", "tags", "quando-postar",
            "retencao", "ctr", "nicho", "tema", "canal")

# Jargão do curso. Mesmo mecanismo do viés de vocabulário dos comandos: dizer
# ao decoder o que esperar ANTES, em vez de consertar depois. Sem isto "CTR"
# vira "cetê erre" e "thumbnail" vira "tambinel".
VOCABULARIO = (
    "YouTube, algoritmo, CTR, taxa de cliques, retenção, thumbnail, "
    "miniatura, impressões, nicho, engajamento, inscritos, watch time, "
    "tempo de exibição, SEO, palavra-chave, título, descrição, tags, "
    "gancho, hook, Shorts, monetização, RPM, CPM, playlist, card, "
    "tela final, sessão, recomendados, feed, alcance"
)

_estado: dict = {"rodando": False, "aula": "", "resultado": None,
                 "proc": None, "cancelado": False}


def _pasta_do_curso(curso: str | None = None) -> Path:
    return _aula.CURSOS / (curso or _aula.curso_atual())


def aulas(curso: str | None = None) -> list[Path]:
    raiz = _pasta_do_curso(curso) / "aulas"
    if not raiz.is_dir():
        return []
    return sorted(p for p in raiz.iterdir() if p.is_dir())


def pendentes(curso: str | None = None) -> list[Path]:
    """Aulas gravadas que ainda não viraram transcrição."""
    return [p for p in aulas(curso)
            if (p / "audio.wav").exists() and not (p / "transcricao.md").exists()]


def sem_regras(curso: str | None = None) -> list[Path]:
    """Já transcritas, mas sem regras extraídas."""
    return [p for p in aulas(curso)
            if (p / "transcricao.md").exists() and not (p / "regras.md").exists()]


# ---------- transcrição ----------

def _carregar_modelo():
    """Instância PRÓPRIA — ver o cuidado nº 1 no topo do arquivo."""
    _preparar_cuda()
    from faster_whisper import WhisperModel

    try:
        return WhisperModel(MODELO, device="cuda", compute_type="int8_float16")
    except Exception:  # noqa: BLE001
        return WhisperModel("small", device="cpu", compute_type="int8")


def _mmss(segundos: float) -> str:
    return f"{int(segundos) // 60:02d}:{int(segundos) % 60:02d}"


def transcrever_aula(pasta: Path, modelo=None) -> str:
    """Escreve `transcricao.md` COM timestamps. Devolve um resumo curto."""
    wav = pasta / "audio.wav"
    if not wav.exists():
        return f"{pasta.name}: não há áudio."

    proprio = modelo is None
    modelo = modelo or _carregar_modelo()
    try:
        audio = ler_wav_16k(wav)
        amostras = np.frombuffer(audio, np.int16).astype(np.float32) / 32768.0
        duracao = len(amostras) / TAXA
        inicio = time.time()

        segmentos, _ = modelo.transcribe(
            amostras, language="pt", beam_size=5,
            hotwords=VOCABULARIO,
            condition_on_previous_text=False,
            vad_filter=True, vad_parameters=VAD,
        )

        # Os trechos em que o OMEGA falou por cima da aula. Marcados durante
        # a gravação (tools/aula.py) em vez de descartados na hora: assim a
        # aula não perde conteúdo e a limpeza acontece AQUI, onde é
        # reversível — se a marcação errar, o áudio continua inteiro no wav.
        mudos = []
        try:
            import json

            mudos = json.loads(
                (pasta / "falas-do-omega.json").read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            pass

        def e_do_omega(inicio: float, fim: float) -> bool:
            meio = (inicio + fim) / 2
            return any(a <= meio <= b for a, b in mudos)

        linhas = [f"# {pasta.name}", "",
                  f"Áudio: {_mmss(duracao)} · transcrito com {MODELO}", ""]
        descartados = 0
        for s in segmentos:
            if _estado["cancelado"]:
                return f"{pasta.name}: cancelado."
            texto = s.text.strip()
            if not texto:
                continue
            if e_do_omega(s.start, s.end):
                descartados += 1
                continue
            linhas.append(f"**[{_mmss(s.start)}]** {texto}")

        telas = sorted((pasta / "telas").glob("*.jpg")) if (pasta / "telas").is_dir() else []
        if telas:
            linhas += ["", "## Telas capturadas", ""]
            linhas += [f"- `telas/{t.name}` — aos {_mmss(int(t.stem[:5]))}"
                       for t in telas if t.stem[:5].isdigit()]

        (pasta / "transcricao.md").write_text("\n".join(linhas) + "\n",
                                              encoding="utf-8")
        gasto = time.time() - inicio
        extra = f", {descartados} trecho(s) da minha própria voz fora" if descartados else ""
        return (f"{pasta.name}: {_mmss(duracao)} de aula em "
                f"{duracao_falada(gasto)} ({duracao / max(gasto, 1):.1f}x), "
                f"{len(telas)} telas{extra}.")
    finally:
        if proprio:
            del modelo
            import gc

            gc.collect()


# ---------- extração das regras ----------

_PROMPT = """Você está lendo a transcrição de uma aula de um curso sobre o
ALGORITMO DO YOUTUBE, comprado pelo Samuel, dono do canal WhoIAm (mitologia e
criaturas, vídeos feitos com IA).

Leia {transcricao} primeiro, inteira.

Depois, os prints em {telas} — eles carregam o que o áudio não carrega (exemplo
de título, thumbnail, número de analytics na tela). São muitos: **leia no
máximo {teto_telas}**, e escolha pelos MINUTOS em que a transcrição indicar algo
visual ("olha esse título aqui", "vê essa thumbnail", "esse gráfico"). O nome do
arquivo é o segundo da aula, então dá para ir direto ao print do minuto certo.
Não varra a pasta inteira: a maioria é o professor falando.

Escreva {saida} com as REGRAS PRÁTICAS que a aula ensina. Formato, uma por bloco:

## <a regra em uma frase imperativa>
- **Decisão:** uma de titulo | thumbnail | descricao | tags | quando-postar |
  retencao | ctr | nicho | tema | canal
- **Por quê:** o motivo que o professor deu
- **Fonte:** {nome} — [mm:ss]{extra}
- **Confiança:** alta | média | baixa

A **Decisão** diz em que momento a regra serve, e é ela que depois agrupa as 38
aulas por assunto em vez de por aula. Escolha UMA, a que mais se aproxima; se
nenhuma servir, use `canal`.

REGRAS DA EXTRAÇÃO, e elas importam mais que a quantidade:
- Só escreva o que a AULA disse. Não complete com o que você sabe de YouTube:
  o valor disto é ser o que o curso ensinou, não conhecimento geral.
- Toda regra precisa do timestamp. Sem timestamp, não escreva a regra.
- Confiança BAIXA quando o trecho estiver confuso ou a transcrição truncada —
  o Samuel revisa antes de valer, e é ele quem decide o que fica.
- Prefira o específico ao genérico. "Título entre 40 e 60 caracteres" vale;
  "faça bons títulos" não vale nada.
- Se a aula mostrou número na tela (CTR, retenção), cite o número e diga em
  qual print apareceu.
- Nada de conselho seu. Se a aula não falou, não existe.

No fim do arquivo, uma seção `## Dúvidas` com o que ficou ambíguo — é o que o
Samuel vai querer conferir no vídeo."""


def extrair_regras(pasta: Path) -> str:
    """Dispara o Claude Code para virar transcrição+telas em regras."""
    transcricao = pasta / "transcricao.md"
    if not transcricao.exists():
        return f"{pasta.name}: transcreva antes."

    executavel = _resolver_claude()
    if executavel is None:
        return ("O Claude Code CLI não está instalado — sem ele não consigo "
                "extrair as regras. Instale com: npm install -g @anthropic-ai/claude-code")

    telas = pasta / "telas"
    n_telas = len(list(telas.glob("*.jpg"))) if telas.is_dir() else 0
    instrucao = pasta / "_instrucao.md"
    try:
        instrucao.write_text(_PROMPT.format(
            transcricao=transcricao, telas=telas, saida=pasta / "regras.md",
            nome=pasta.name, teto_telas=TETO_TELAS,
            extra=" (+ o print, quando o dado estiver na tela)" if n_telas else "",
        ), encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        return f"{pasta.name}: não consegui gravar a instrução ({str(e)[:60]})."

    # O PROMPT VAI POR ARQUIVO, e a linha de comando leva só o caminho.
    #
    # No Windows o CLI é um .CMD, então o Popen roda com `shell=True` — e o
    # cmd.exe CORTA a linha de comando na primeira quebra de linha. Este
    # prompt tem quinze. Medido: o Claude recebia só "Você está lendo a
    # transcrição de uma aula de um curso sobre o" e respondia "pode reenviar
    # a mensagem completa?", saindo com código 0 e sem gravar nada. Seriam 38
    # chamadas queimando crédito para produzir zero regra.
    #
    # O `pipeline.py` escapa disso porque o prompt dele é de uma linha só.
    # Aqui o prompt é longo de propósito, então ele vira arquivo — que ainda
    # tem a vantagem de ficar no disco para conferência quando a extração sair
    # estranha.
    pedido = (f"Leia {instrucao} e faça exatamente o que está escrito lá. "
              "O arquivo é a instrução completa, não um texto para resumir.")

    comeco = time.monotonic()
    try:
        proc = subprocess.Popen(
            [executavel, "-p", pedido, "--permission-mode", "acceptEdits",
             "--allowedTools", "Read", "Write", "Glob", "Grep"],
            cwd=str(AI_PROJECT_ROOT),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", errors="replace",
            shell=E_WINDOWS,
        )
        _estado["proc"] = proc
        try:
            fora, erro = proc.communicate(timeout=1800)
        except subprocess.TimeoutExpired:
            _matar(proc)
            return f"{pasta.name}: a extração passou de 30 minutos."
    except Exception as e:  # noqa: BLE001
        return f"{pasta.name}: falhou ao chamar o Claude ({str(e)[:80]})."

    if _estado["cancelado"]:
        return f"{pasta.name}: cancelado."
    if not (pasta / "regras.md").exists():
        saida = ((fora or "") + (erro or ""))[-200:]
        # RECUSA INSTANTÂNEA É LIMITE DE USO, não defeito da aula.
        #
        # Medido na primeira leva das 38: as onze primeiras levaram ~200 s cada
        # e extraíram bem; da décima segunda em diante o CLI passou a voltar em
        # CINCO SEGUNDOS sem gravar nada. Uma hora depois, a mesma aula extraiu
        # normalmente. Insistir na hora não adianta — o que resolve é esperar.
        #
        # Dizer isso em vez de "o Claude terminou mas não gravou" é a diferença
        # entre ele saber que é só aguardar e ele achar que a aula está
        # quebrada e ir mexer no que está certo.
        if time.monotonic() - comeco < RECUSA_INSTANTANEA:
            return (f"{pasta.name}: o Claude recusou em "
                    f"{time.monotonic() - comeco:.0f} segundos — isso é limite "
                    "de uso, não problema da aula. Espere alguns minutos e "
                    f"peça de novo. {saida}")
        # Sair com código 0 sem gravar arquivo já aconteceu antes (era falta de
        # --allowedTools). Dizer "pronto" aqui seria mentira descoberta tarde.
        return f"{pasta.name}: o Claude terminou mas não gravou regras.md. {saida}"
    return f"{pasta.name}: regras extraídas."


# ---------- o laço completo ----------

def _processar(curso: str, ui) -> None:
    passos: list[str] = []
    try:
        fila = pendentes(curso)
        if fila:
            modelo = _carregar_modelo()
            try:
                for p in fila:
                    if _estado["cancelado"]:
                        break
                    _estado["aula"] = p.name
                    ui.write_log(f"SYS: transcrevendo {p.name}...")
                    passos.append(transcrever_aula(p, modelo))
            finally:
                del modelo
                import gc

                gc.collect()

        for p in sem_regras(curso):
            if _estado["cancelado"]:
                break
            _estado["aula"] = p.name
            ui.write_log(f"SYS: extraindo regras de {p.name}...")
            passos.append(extrair_regras(p))

        if _estado["cancelado"]:
            _estado["resultado"] = "Processamento do curso cancelado."
        elif not passos:
            _estado["resultado"] = "Nenhuma aula pendente — tudo já processado."
        else:
            _estado["resultado"] = (
                f"Curso processado: {len(passos)} etapa(s). "
                + " ".join(passos[-3:])
                + " Diga 'revisar regras' para aprovar o que vale."
            )
    except Exception as e:  # noqa: BLE001 — vira frase falada, nunca crash
        _estado["resultado"] = f"Falhou processando o curso: {str(e)[:150]}"
    finally:
        _estado.update({"rodando": False, "aula": "", "proc": None})
        notificar(_estado["resultado"], falar=True)


def processar(ui, curso: str | None = None) -> str:
    """Transcreve o que falta e extrai as regras, em segundo plano."""
    if _estado["rodando"]:
        return f"Já estou processando {_estado['aula']}. Pergunte o andamento."

    curso = curso or _aula.curso_atual()
    fila = pendentes(curso)
    faltam_regras = sem_regras(curso)
    if not fila and not faltam_regras:
        return (f"Não há aula pendente no curso {curso}. "
                "Grave uma com 'assistir <nome da aula>'.")

    minutos = 0.0
    for p in fila:
        try:
            minutos += (p / "audio.wav").stat().st_size / 2 / TAXA / 60
        except OSError:
            pass

    _estado.update({"rodando": True, "aula": "", "resultado": None,
                    "proc": None, "cancelado": False})
    threading.Thread(target=_processar, args=(curso, ui),
                     name="curso", daemon=True).start()
    batimento(180,
              lambda d: f"Ainda processando o curso — {duracao_falada(d)} até agora.",
              lambda: _estado["rodando"])

    # 1,7x é o número medido nesta máquina; dizer a previsão evita o "travou?".
    previsao = int(minutos / 1.7) + 2 * len(fila or faltam_regras)
    return (f"Processando {len(fila)} aula(s) para transcrever e "
            f"{len(faltam_regras) + len(fila)} para extrair regras. "
            f"Deve levar uns {previsao} minutos — eu aviso quando terminar.")


def cancelar() -> str:
    if not _estado["rodando"]:
        return "Não estou processando curso nenhum."
    _estado["cancelado"] = True
    proc = _estado.get("proc")
    if proc is not None:
        _matar(proc)
    return "Vou parar o processamento do curso."


# ---------- aprovar: só o que ele confirmar passa a valer ----------
#
# Uma frase mal transcrita não pode virar estratégia do canal em silêncio. É a
# mesma lógica do `ensinar` em tools/aprendizado.py: quem corrige é quem sabe.

SKILL_WHOIAM = (Path.home() / ".claude" / "skills" / "whoiam" /
                "references" / "algoritmo-youtube.md")

_pendente_de_aprovacao: dict = {"itens": [], "curso": ""}


# Seções que o `regras.md` tem mas que NÃO são regras. Comparadas sem acento
# porque o Claude escreve "Dúvidas" e a transcrição às vezes devolve "Duvidas"
# — e um título de seção aprovado como regra vira lixo dentro da skill de SEO.
_NAO_SAO_REGRAS = ("duvidas", "observacoes", "notas", "resumo", "indice",
                   "sumario", "regras")


def _blocos_de_regras(texto: str) -> list[str]:
    """Quebra um regras.md nos blocos que começam com '## '."""
    saida = []
    for p in re.split(r"^## ", texto, flags=re.M)[1:]:
        if not p.strip():
            continue
        cabeca = _aula._sem_acento(p.splitlines()[0]).lower().strip(" :")
        if cabeca in _NAO_SAO_REGRAS:
            continue
        saida.append(("## " + p).rstrip())
    return saida


CONSOLIDADAS = "regras-consolidadas.md"

_PROMPT_CONSOLIDAR = """Você vai juntar as regras extraídas de um curso sobre o
ALGORITMO DO YOUTUBE, comprado pelo Samuel, dono do canal WhoIAm.

Leia TODOS os arquivos `regras.md` em {pasta}/aulas/*/regras.md. São {n_aulas}
aulas e cerca de {n_regras} regras — muita coisa repetida, porque um curso de
marketing insiste no mesmo ponto em aulas diferentes.

Escreva {saida} com a versão consolidada. Estrutura obrigatória:

Uma seção `# <decisão>` para cada uma destas, NESTA ORDEM, pulando as que não
tiverem regra nenhuma: titulo, thumbnail, descricao, tags, quando-postar,
retencao, ctr, nicho, tema, canal.

Dentro de cada seção, uma regra por bloco:

## <a regra em uma frase imperativa>
- **Por quê:** o motivo, na versão mais completa entre as fontes
- **Fonte:** todas as aulas e minutos em que ela apareceu, separados por `;`
- **Confiança:** alta | média | baixa

AS QUATRO COISAS QUE IMPORTAM AQUI:

1. FUNDIR o que é a mesma regra dita de formas diferentes. Uma regra que
   aparece em quatro aulas é mais forte que uma que apareceu em uma — e isso
   só fica visível se você guardar TODAS as fontes no mesmo bloco. Nunca jogue
   fonte fora.
2. NÃO INVENTAR. Nada de completar com o que você sabe de YouTube. Se as aulas
   não disseram, não existe. O valor disto é ser o que o curso ensinou.
3. Uma seção final `# Conflitos`, e ela é o ponto mais importante do arquivo:
   quando duas aulas se contradizem (uma diz título curto, outra diz longo),
   ponha as duas lado a lado com suas fontes e NÃO escolha por conta própria.
   Quem decide é o Samuel. Se você realmente não achar conflito nenhum, diga
   "nenhum conflito encontrado" — mas procure de verdade antes.
4. Preferir o específico. "Título entre 40 e 60 caracteres" vale; "faça bons
   títulos" não vale nada e deve ser descartado na fusão.

No fim, uma seção `# Descartadas na fusão` listando em uma linha cada regra
genérica demais que você tirou — para o Samuel conferir que não perdeu nada."""


def consolidar(curso: str | None = None) -> str:
    """Junta as 38 extrações num arquivo só, agrupado por DECISÃO.

    Sem este passo o arquivo de referência da skill vira ruído: 38 aulas de um
    curso de marketing repetem o mesmo conselho e às vezes se contradizem, e um
    OMEGA com 550 regras soltas consegue citar o curso para justificar
    qualquer coisa — o que é pior que não citar nada.
    """
    curso = curso or _aula.curso_atual()
    pasta = _pasta_do_curso(curso)
    arquivos = sorted(pasta.glob("aulas/*/regras.md"))
    if not arquivos:
        return ("Não há regras extraídas ainda. Diga 'processar curso' "
                "primeiro.")

    executavel = _resolver_claude()
    if executavel is None:
        return "O Claude Code CLI não está instalado."

    n_regras = sum(a.read_text(encoding="utf-8").count("**Fonte:**")
                   for a in arquivos)
    saida = pasta / CONSOLIDADAS
    instrucao = pasta / "_instrucao-consolidar.md"
    try:
        instrucao.write_text(_PROMPT_CONSOLIDAR.format(
            pasta=pasta, saida=saida, n_aulas=len(arquivos),
            n_regras=n_regras), encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        return f"Não consegui gravar a instrução: {str(e)[:60]}"

    # Instrução por arquivo, pelo mesmo motivo de `extrair_regras`: no Windows
    # o cmd.exe corta a linha de comando na primeira quebra de linha.
    pedido = (f"Leia {instrucao} e faça exatamente o que está escrito lá. "
              "O arquivo é a instrução completa, não um texto para resumir.")
    try:
        proc = subprocess.Popen(
            [executavel, "-p", pedido, "--permission-mode", "acceptEdits",
             "--allowedTools", "Read", "Write", "Glob", "Grep"],
            cwd=str(AI_PROJECT_ROOT), stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, encoding="utf-8",
            errors="replace", shell=E_WINDOWS)
        _estado["proc"] = proc
        fora, erro = proc.communicate(timeout=3600)
    except subprocess.TimeoutExpired:
        _matar(proc)
        return "A consolidação passou de uma hora."
    except Exception as e:  # noqa: BLE001
        return f"Falhou ao chamar o Claude: {str(e)[:80]}"

    if not saida.exists():
        return (f"O Claude terminou sem gravar {CONSOLIDADAS}. "
                + ((fora or "") + (erro or ""))[-200:])
    texto = saida.read_text(encoding="utf-8")
    return (f"Consolidei {n_regras} regras de {len(arquivos)} aulas em "
            f"{texto.count(chr(10) + '## ')} regras únicas. "
            "Diga 'revisar regras' para aprovar.")


def propostas(curso: str | None = None) -> list[tuple[Path, str]]:
    """As regras à espera de aprovação.

    Quando existe o arquivo consolidado, ele MANDA: aprovar 550 regras soltas,
    com a mesma coisa repetida quatro vezes, é trabalho que ninguém faz até o
    fim — e trabalho que não se faz vira regra nenhuma valendo.
    """
    curso = curso or _aula.curso_atual()
    juntas = _pasta_do_curso(curso) / CONSOLIDADAS
    if juntas.exists():
        return [(juntas.parent, bloco) for bloco
                in _blocos_de_regras(juntas.read_text(encoding="utf-8"))]

    saida = []
    for p in aulas(curso):
        arq = p / "regras.md"
        if arq.exists():
            for bloco in _blocos_de_regras(arq.read_text(encoding="utf-8")):
                saida.append((p, bloco))
    return saida


def _texto_aprovado(curso: str) -> str:
    arq = _pasta_do_curso(curso) / "regras-aprovadas.md"
    return arq.read_text(encoding="utf-8") if arq.exists() else ""


def revisar(ui, curso: str | None = None) -> str:
    """Mostra as regras propostas, numeradas, para ele decidir."""
    curso = curso or _aula.curso_atual()
    itens = propostas(curso)
    ja = _texto_aprovado(curso)
    # Uma regra já aprovada não volta à fila.
    novas = [(p, b) for p, b in itens if b.splitlines()[0][3:].strip() not in ja]

    if not novas:
        total = ja.count("\n## ")
        return (f"Nada novo para aprovar. O curso {curso} tem {total} regra(s) "
                "valendo." if total else
                f"Nenhuma regra extraída ainda no curso {curso}. "
                "Diga 'processar curso' depois de gravar uma aula.")

    _pendente_de_aprovacao.update({"itens": novas, "curso": curso})
    linhas = [f"# Regras do curso {curso} — aguardando você", "",
              f"{len(novas)} proposta(s). Diga **`aprovar todas`**, "
              "**`aprovar 1 3 5`** ou **`descartar 2`**.", ""]
    for i, (pasta, bloco) in enumerate(novas, 1):
        cabeca, *resto = bloco.splitlines()
        linhas.append(f"### {i}. {cabeca[3:].strip()}")
        linhas += [l for l in resto if l.strip()]
        linhas.append("")
    ui.show_document(f"Regras do curso — {curso}", "\n".join(linhas))
    return (f"{len(novas)} regra(s) na tela, com a aula e o minuto de cada uma. "
            "Diga 'aprovar todas' ou os números que quiser.")


def _espelhar_na_skill(curso: str) -> str:
    """Copia as aprovadas para dentro da skill que gera o SEO do canal."""
    conteudo = _texto_aprovado(curso)
    if not conteudo.strip():
        return ""
    cabecalho = (
        "<!-- GERADO por voice/tools/curso.py a partir do curso que o Samuel\n"
        "     comprou. NÃO editar à mão: 'aprovar'/'descartar' no OMEGA é que\n"
        "     mandam aqui. Material comprado — de uso interno; não republicar\n"
        "     nem citar como conteúdo do canal. -->\n\n"
        "# Algoritmo do YouTube — regras aprovadas pelo Samuel\n\n"
        "Use ao gerar o DOCUMENTO 5 (pacote de SEO). Cada regra tem a aula e o\n"
        "minuto de onde veio: **cite a fonte** ao recomendar. Se nenhuma regra\n"
        "cobrir o caso, diga isso — não invente recomendação com cara de curso.\n\n"
    )
    try:
        SKILL_WHOIAM.parent.mkdir(parents=True, exist_ok=True)
        SKILL_WHOIAM.write_text(cabecalho + conteudo, encoding="utf-8")
        return f" A skill de SEO já está usando ({SKILL_WHOIAM.name})."
    except Exception as e:  # noqa: BLE001
        return f" (não consegui atualizar a skill: {str(e)[:50]})"


def _decisoes_na_fila(itens) -> str:
    """Quais assuntos estão esperando decisão, e quantas regras cada um tem."""
    import collections

    conta = collections.Counter()
    for _, bloco in itens:
        achado = re.search(r"\*\*Decis[aã]o:\*\*\s*(\S+)", bloco)
        conta[achado.group(1).strip("`*") if achado else "sem etiqueta"] += 1
    return ", ".join(f"{d} ({n})" for d, n in conta.most_common())


def decidir(pedido: str) -> str:
    """`aprovar todas`, `aprovar 1 3`, `descartar 2` — sobre o que está na tela."""
    itens = _pendente_de_aprovacao.get("itens") or []
    if not itens:
        return "Não há regras esperando decisão. Diga 'revisar regras' antes."

    baixo = _aula._sem_acento(pedido.lower())
    descartar = baixo.startswith(("descart", "recus", "nao ", "joga"))
    numeros = [int(n) for n in re.findall(r"\d+", baixo)
               if 1 <= int(n) <= len(itens)]
    todas = "todas" in baixo or "tudo" in baixo

    # POR DECISÃO, e não só por número.
    #
    # São 38 aulas e mais de quinhentas regras. Aprovar de uma em uma, por
    # número, é trabalho que ninguém termina — e trabalho que não se termina
    # vira regra nenhuma valendo, ou seja, o curso inteiro desperdiçado. Dizer
    # "aprovar tudo de título" resolve um assunto de uma vez, e é assim que
    # ele pensa: por decisão, não por índice.
    grupo = next((d for d in DECISOES if d in baixo), "")
    if not grupo and "titulos" in baixo:
        grupo = "titulo"
    if grupo:
        alvo = {i for i, (_, b) in enumerate(itens, 1)
                if f"**Decisão:** {grupo}" in b}
        if not alvo:
            return (f"Nenhuma das {len(itens)} regras na fila é de {grupo}. "
                    f"As decisões em jogo: {_decisoes_na_fila(itens)}.")
    elif not numeros and not todas:
        return ("Diga quais: 'aprovar todas', 'aprovar tudo de título', "
                "'aprovar 1 3 5' ou 'descartar 2'.")
    else:
        alvo = set(range(1, len(itens) + 1)) if todas else set(numeros)
    if descartar and todas and not grupo:
        _pendente_de_aprovacao["itens"] = []
        return "Descartei todas. Nenhuma passou a valer."
    if descartar:
        # Descartar é só não aprovar: os blocos ficam no regras.md da aula, e
        # somem da fila. Nada é apagado do disco — a fonte continua auditável.
        restantes = [it for i, it in enumerate(itens, 1) if i not in alvo]
        _pendente_de_aprovacao["itens"] = restantes
        de = f" de {grupo}" if grupo else ""
        return (f"Descartei {len(alvo)}{de}. Sobraram {len(restantes)}: "
                f"{_decisoes_na_fila(restantes)}." if restantes else
                f"Descartei {len(alvo)}{de}. A fila ficou vazia.")

    curso = _pendente_de_aprovacao["curso"]
    escolhidas = [itens[i - 1] for i in sorted(alvo)]
    arq = _pasta_do_curso(curso) / "regras-aprovadas.md"
    try:
        arq.parent.mkdir(parents=True, exist_ok=True)
        anterior = _texto_aprovado(curso)
        if not anterior:
            anterior = f"# Regras aprovadas — {curso}\n"
        arq.write_text(
            anterior.rstrip() + "\n\n" + "\n\n".join(b for _, b in escolhidas) + "\n",
            encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        return f"Não consegui gravar: {str(e)[:70]}"

    _pendente_de_aprovacao["itens"] = [
        it for i, it in enumerate(itens, 1) if i not in alvo]
    sobrando = _pendente_de_aprovacao["itens"]
    quais = (f" Ainda restam {len(sobrando)}: {_decisoes_na_fila(sobrando)}."
             if sobrando else "")
    de = f" de {grupo}" if grupo else ""
    return (f"Aprovei {len(escolhidas)} regra(s){de}."
            + _espelhar_na_skill(curso) + quais)


# ---------- avaliar um título/descrição contra o que o curso ensinou ----------

def avaliar(proposta: str, curso: str | None = None) -> str:
    """Devolve o MATERIAL para o modelo julgar — não o veredito.

    Mesmo desenho de `tools/web.conferir`: quem conclui é o modelo, que tem o
    contexto da conversa; o que este módulo garante é que ele conclua a partir
    de regra aprovada, e não de palpite com cara de curso.
    """
    proposta = (proposta or "").strip()
    if not proposta:
        return "Avaliar o quê, senhor?"
    conteudo = _texto_aprovado(curso or _aula.curso_atual())
    if not conteudo.strip():
        return (
            "NÃO HÁ REGRA APROVADA do curso ainda.\n"
            "Diga que ainda não tem base do curso para opinar e ofereça "
            "processar as aulas. NÃO invente recomendação de SEO."
        )
    return (
        f"REGRAS DO CURSO APROVADAS PELO SENHOR:\n\n{conteudo}\n\n"
        f"---\nO QUE ELE PROPÔS:\n{proposta}\n\n"
        "---\nCompare uma coisa com a outra. Diga o que está de acordo e o que "
        "contraria, SEMPRE citando a aula e o minuto da regra. Se nenhuma regra "
        "cobrir algum aspecto, diga que o curso não falou disso em vez de "
        "opinar por conta própria. Seja curto: duas ou três frases."
    )


def orientar(decisoes: tuple[str, ...], sobre: str = "",
             curso: str | None = None) -> str:
    """As regras aprovadas que valem para ESTAS decisões, e mais nada.

    O lado proativo do `avaliar`: ele reage a uma proposta, este chega antes.
    Mesmo desenho dos dois — devolve MATERIAL, não veredito, porque quem tem o
    contexto da conversa é o modelo. O que este módulo garante é que a fala
    saia de regra aprovada com fonte, e não de palpite com cara de curso.

    O recorte por decisão existe porque despejar quinhentas regras a cada fase
    seria ruído: na fase 0 o que importa é tema e título; na 5, o pacote todo.
    """
    conteudo = _texto_aprovado(curso or _aula.curso_atual())
    if not conteudo.strip():
        return ""

    # Cada bloco começa em "## "; a etiqueta de decisão vive dentro dele.
    blocos = [b for b in _blocos_de_regras(conteudo)
              if any(f"**Decisão:** {d}" in b or f"# {d}" in b
                     for d in decisoes)]
    if not blocos:
        return ""
    alvo = f" para {sobre}" if sobre else ""
    return (
        f"REGRAS DO CURSO APROVADAS PELO SENHOR{alvo} "
        f"({', '.join(decisoes)}):\n\n" + "\n\n".join(blocos) + "\n\n---\n"
        "Diga em duas ou três frases o que estas regras recomendam aqui, "
        "SEMPRE citando a aula e o minuto. Não acrescente conselho seu: se o "
        "curso não falou de algo, esse algo não entra."
    )


def andamento() -> str:
    if _estado["rodando"]:
        return (f"Processando {_estado['aula'] or 'o curso'}. "
                "Diga 'cancelar curso' se quiser que eu pare.")
    if _estado["resultado"]:
        return _estado["resultado"]
    curso = _aula.curso_atual()
    return (f"Curso {curso}: {len(aulas(curso))} aula(s) gravada(s), "
            f"{len(pendentes(curso))} sem transcrever, "
            f"{len(sem_regras(curso))} sem regras.")
