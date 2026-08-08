"""Corrige o que o Vosk transcreve errado no vocabulário do canal.

O modelo é treinado em português comum: nome estrangeiro ("Pennywise",
"Cthulhu") e jargão de produção ("Short", "render") saem deformados. Em vez
de trocar o modelo por um maior — o que ajuda mas não resolve nome próprio
inglês —, mapeamos o que ele REALMENTE produz para o que se quis dizer.

Como crescer: rode o OMEGA, veja no log a linha "Você: ..." com o erro, e
acrescente a forma errada aqui. É a lista de erros observados, não de erros
imaginados.
"""

from __future__ import annotations

import re
import unicodedata

# Cada entrada: forma correta -> variantes que o Vosk produz.
# Comparação sem acento e em minúsculas, então basta escrever simples.
CORRECOES: dict[str, tuple[str, ...]] = {
    # --- criaturas / personagens ---
    "Pennywise": (
        "peniwase", "peni wase", "penny wise", "peni uais", "pena wise",
        "penivais", "peni vais", "pen y wise", "penes",
    ),
    "Cthulhu": ("catulu", "ktulu", "cthulu", "tulu", "catulo", "ca tulu"),
    "Medusa": ("medusa", "meduza", "me dusa"),
    "Baba Yaga": ("baba iaga", "babaiaga", "baba yagá", "baba jaga"),
    "Slenderman": ("slender man", "esplenderman", "slandermen", "eslenderman"),
    "Wendigo": ("wendigo", "uendigo", "vendigo", "wendego"),
    "Krampus": ("crampus", "krampos", "cramps"),
    "Banshee": ("banshi", "banche", "ban chi", "banshee"),

    # --- erros REAIS observados no log do Samuel ---
    # "dossiê" é palavra francesa e o modelo destrói: virou "torcedor" e
    # "doce e do lixo". Por isso o comando passou a se chamar "pesquisa";
    # estas linhas ainda salvam quem falar a palavra antiga.
    "pesquisa": ("torcedor", "doce e do lixo", "doce e", "docie", "do se e"),

    # --- jargão de produção ---
    "Short": ("short", "chorte", "xorte", "shorts", "chorts"),
    "render": ("render", "hender", "randa", "rende"),
    "dossiê": ("dossie", "dossiê", "do se", "dossier"),
    "roteiro": ("roteiro", "ro teiro"),
    "prompts": ("prompts", "prontos", "prompt", "promptes"),
}

# Mapa invertido e normalizado, montado uma vez.
_MAPA: dict[str, str] = {}


def _normalizar(texto: str) -> str:
    sem_acento = "".join(
        c for c in unicodedata.normalize("NFD", texto.lower())
        if unicodedata.category(c) != "Mn"
    )
    return re.sub(r"\s+", " ", sem_acento).strip()


def recarregar() -> None:
    """(Re)monta o mapa: a lista fixa daqui MAIS o que o Samuel ensinou.

    As lições dele vêm por último de propósito — quem corrige o assistente
    ao vivo sabe mais sobre a própria fala do que uma lista escrita meses
    antes. Ver `tools/aprendizado.py`.
    """
    _MAPA.clear()
    for correto, variantes in CORRECOES.items():
        for v in variantes:
            _MAPA[_normalizar(v)] = correto
    try:
        from .aprendizado import aprendidos

        for errado, certo in aprendidos().items():
            _MAPA[_normalizar(errado)] = certo
    except Exception:  # noqa: BLE001 — sem as lições, a lista fixa ainda vale
        pass


recarregar()


# Seres que têm mais de um nome. Sem isto o OMEGA pesquisa "Pennywise" e
# "IT" como se fossem criaturas diferentes — foi o que aconteceu de fato,
# gerando dois projetos para o mesmo ser.
APELIDOS: tuple[tuple[str, ...], ...] = (
    ("pennywise", "it", "it a coisa", "a coisa", "palhaco assassino"),
    ("cthulhu", "ktulu", "grande antigo"),
    ("baba yaga", "babayaga", "bruxa da isba"),
    ("slenderman", "homem magro", "slender"),
    ("wendigo", "windigo"),
    ("medusa", "gorgona", "gorgone"),
)


def mesma_criatura(a: str, b: str) -> bool:
    """Os dois nomes se referem ao mesmo ser?"""
    na, nb = _normalizar(a), _normalizar(b)
    if na == nb:
        return True
    for grupo in APELIDOS:
        if na in grupo and nb in grupo:
            return True
    return False


def corrigir(frase: str) -> str:
    """Troca as variantes conhecidas pela forma correta.

    Trabalha por janelas de palavras (4 a 1) para pegar nomes compostos
    como "baba iaga" antes de tentar palavra por palavra. Quatro porque um
    erro observado ("doce e do lixo" por "dossiê") tem esse tamanho — com
    janela de 3 só metade era corrigida.
    """
    if not frase.strip():
        return frase

    palavras = frase.split()
    saida: list[str] = []
    i = 0
    while i < len(palavras):
        casou = False
        for tamanho in (4, 3, 2, 1):
            if i + tamanho > len(palavras):
                continue
            trecho = " ".join(palavras[i:i + tamanho])
            correto = _MAPA.get(_normalizar(trecho))
            if correto:
                saida.append(correto)
                i += tamanho
                casou = True
                break
        if not casou:
            saida.append(palavras[i])
            i += 1
    return " ".join(saida)
