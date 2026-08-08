"""O OMEGA aprendendo com o uso — que é o que substitui "treinar o modelo".

Ninguém retreina reconhecimento de fala para um assistente entender
"Cthullhu". O que se faz em produção é um laço: registrar o que foi dito,
marcar o que falhou, e realimentar o vocabulário com as falhas reais. É
barato, é honesto, e melhora com o uso em vez de com suposição.

Isto substitui o `nao-entendidas.txt`, que só guardava a frase solta e que
ninguém nunca leu de volta. Aqui cada fala guarda:

  bruta      o que o reconhecimento entregou, sem tratamento
  corrigida  depois do dicionário
  rota       quem atendeu: local, gemini, live, ou nada
  ok         se resolveu

O par (bruta, corrigida) é o que dá valor: mostra se o dicionário está
ajudando ou atrapalhando. E `bruta` das falhas é a matéria-prima do que
ainda falta ensinar.

O ARQUIVO CONTÉM O QUE O SAMUEL FALA — fica fora do git, e o `revisar`
mostra na tela dele, não manda para lugar nenhum.

Se um dia valer a pena treinar de verdade (LoRA do Whisper na voz dele),
este arquivo é o conjunto de dados. Mas isso só com centenas de amostras;
até lá, viés de vocabulário resolve mais por muito menos.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DIARIO = BASE / "aprendizado.jsonl"
APRENDIDO = BASE / "config" / "vocabulario-aprendido.json"

# Acima disto o arquivo é cortado pela metade. Não há valor em guardar um ano
# de falas, e um jsonl gigante torna o `revisar` lento.
MAX_LINHAS = 4000

# Português comum. A lista de candidatos só vale se contiver NOMES — se
# "aquele" e "negócio" aparecem nela, ela vira ruído e ninguém a lê. Cresce
# quando aparecer palavra comum na sugestão, que é fácil de notar em uso.
_VAZIAS = {
    "o", "a", "os", "as", "de", "do", "da", "e", "em", "no", "na", "um",
    "uma", "para", "pra", "com", "que", "me", "meu", "minha", "isso", "aqui",
    "ali", "por", "favor", "voce", "vc", "ta", "ne", "ai", "la", "sim", "nao",
    # pronomes e determinantes
    "aquele", "aquela", "aquilo", "esse", "essa", "este", "esta", "dele",
    "dela", "seu", "sua", "nosso", "nossa", "qual", "quais", "quando",
    "onde", "como", "porque", "tudo", "todo", "toda", "nada", "algum",
    "alguma", "outro", "outra", "mesmo", "mesma", "cada", "muito", "muita",
    # verbos que aparecem em qualquer pedido
    "arruma", "arrumar", "pega", "pegar", "poder", "pode", "quero", "queria",
    "fazer", "faca", "faz", "estar", "esta", "estou", "tenho", "tem", "ter",
    "vamos", "vai", "vou", "dar", "deixa", "coloca", "bota", "manda",
    "preciso", "gostaria", "consegue", "sabe", "diga", "fala", "falar",
    # substantivos genéricos
    "negocio", "coisa", "coisas", "treco", "bagulho", "parada", "lance",
    "agora", "depois", "antes", "hoje", "ontem", "amanha", "vez", "vezes",
    "bom", "boa", "dia", "tarde", "noite", "obrigado", "obrigada",
}


def _sem_acento(t: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", t.lower())
                   if unicodedata.category(c) != "Mn")


def registrar(bruta: str, corrigida: str, rota: str, ok: bool) -> None:
    """Guarda uma fala. Nunca levanta exceção: log não pode derrubar a voz."""
    try:
        linha = json.dumps({
            "quando": datetime.now().isoformat(timespec="seconds"),
            "bruta": (bruta or "").strip(),
            "corrigida": (corrigida or "").strip(),
            "rota": rota,
            "ok": bool(ok),
        }, ensure_ascii=False)
        with DIARIO.open("a", encoding="utf-8") as f:
            f.write(linha + "\n")
        _podar()
    except Exception:  # noqa: BLE001
        pass


def _podar() -> None:
    try:
        linhas = DIARIO.read_text(encoding="utf-8").splitlines()
        if len(linhas) > MAX_LINHAS:
            DIARIO.write_text(
                "\n".join(linhas[-MAX_LINHAS // 2:]) + "\n", encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass


def ler(limite: int = 500) -> list[dict]:
    try:
        linhas = DIARIO.read_text(encoding="utf-8").splitlines()[-limite:]
    except Exception:  # noqa: BLE001
        return []
    saida = []
    for l in linhas:
        try:
            saida.append(json.loads(l))
        except Exception:  # noqa: BLE001
            continue
    return saida


# ---------- vocabulário aprendido ----------

def aprendidos() -> dict[str, str]:
    """{forma errada normalizada: forma certa}. Cresce com o `ensinar`."""
    try:
        return json.loads(APRENDIDO.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}


def ensinar(errado: str, certo: str) -> str:
    """Grava uma correção dita pelo Samuel.

    Vai para um JSON, e não para dentro do `vocabulario.py`: código que se
    reescreve sozinho é código que ninguém consegue revisar depois.
    """
    errado, certo = (errado or "").strip(), (certo or "").strip()
    if not errado or not certo:
        return "Preciso das duas formas: o que ouvi e o que era."
    mapa = aprendidos()
    mapa[_sem_acento(errado)] = certo
    try:
        APRENDIDO.parent.mkdir(parents=True, exist_ok=True)
        APRENDIDO.write_text(
            json.dumps(mapa, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        return f"Não consegui gravar: {str(e)[:60]}"
    # Sem isto a lição só valeria na próxima abertura do app.
    try:
        from . import contexto_fala, vocabulario

        vocabulario.recarregar()
        contexto_fala.hotwords(forcar=True)
    except Exception:  # noqa: BLE001
        pass
    return f"Anotado: quando eu ouvir '{errado}', é '{certo}'."


# ---------- revisão ----------

def candidatos(minimo: int = 2) -> list[tuple[str, int]]:
    """Palavras que aparecem nas falas que FALHARAM e não conhecemos.

    É a lista do que ainda falta ensinar — tirada do uso real, não de
    suposição sobre o que ele diria.
    """
    from . import contexto_fala

    conhecidas = {_sem_acento(p) for p in contexto_fala.hotwords().split(", ")}
    aprendidas = set(aprendidos())
    contagem: Counter[str] = Counter()
    for reg in ler():
        if reg.get("ok"):
            continue
        for palavra in re.findall(r"[\wÀ-ÿ]{4,}", reg.get("bruta", "")):
            chave = _sem_acento(palavra)
            if chave in _VAZIAS or chave in conhecidas or chave in aprendidas:
                continue
            contagem[chave] += 1
    return [(p, n) for p, n in contagem.most_common(12) if n >= minimo]


def resumo() -> str:
    """O que mostrar no comando `revisar`."""
    registros = ler()
    if not registros:
        return ("Ainda não tenho histórico de fala. Converse comigo um pouco "
                "e depois peça 'revisar'.")

    total = len(registros)
    falhas = [r for r in registros if not r.get("ok")]
    corrigidas = sum(1 for r in registros
                     if r.get("bruta") and r["bruta"] != r.get("corrigida"))

    linhas = [
        f"# Como estou te entendendo",
        "",
        f"- **{total}** falas registradas; **{total - len(falhas)}** resolveram "
        f"({100 * (total - len(falhas)) // max(total, 1)}%).",
        f"- O dicionário consertou **{corrigidas}** transcrições.",
    ]

    sugestoes = candidatos()
    if sugestoes:
        linhas += [
            "",
            "## Palavras que eu não conheço e você repete",
            "",
            "Diga **`ensinar <o que ouvi> é <o que era>`** para cada uma:",
            "",
        ]
        linhas += [f"- `{p}` — {n}x" for p, n in sugestoes]

    if falhas:
        linhas += ["", "## Últimas falas que eu não resolvi", ""]
        for r in falhas[-8:]:
            bruta = r.get("bruta", "")
            corr = r.get("corrigida", "")
            extra = f"  *(entendi: {corr})*" if corr and corr != bruta else ""
            linhas.append(f"- {r.get('quando','')[11:16]} — \"{bruta}\"{extra}")

    if not sugestoes and not falhas:
        linhas += ["", "Nenhuma falha registrada. Estou te entendendo bem."]

    linhas += [
        "",
        "---",
        "*Este arquivo fica só na sua máquina (`voice/aprendizado.jsonl`, "
        "fora do git).*",
    ]
    return "\n".join(linhas)
