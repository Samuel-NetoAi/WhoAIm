"""O que as pessoas estão procurando — para escolher a próxima criatura.

O Samuel pediu para o OMEGA "abrir e analisar o Google Trends" e achar o que
está em alta, para lançar um vídeo antes dos outros. Fui medir antes de
construir, e o resultado mudou o desenho:

1. O "EM ALTA" DO BRASIL NÃO SERVE PARA ESTE CANAL. Medido no RSS oficial:
   "santos futebol clube", "brasileirão série a", "grêmio vs são paulo".
   É futebol e notícia — o país inteiro somado. Um canal de mitologia não
   tira nada dali, e abrir a página do Trends só mostraria isso maior.

2. A API DO TRENDS QUE SERVIRIA É INSTÁVEL. As "consultas em ascensão" de um
   termo (ex.: o que está subindo dentro de "mitologia") existem, mas vêm de
   uma API interna: o passo `explore` responde 200 e o `widgetdata` responde
   **429** com frequência. Fica aqui como melhor-esforço, e quando falha o
   OMEGA DIZ que falhou em vez de fingir que não havia nada.

3. O AUTOCOMPLETE DO YOUTUBE É MELHOR PARA O CASO DELE, e foi o achado. É o
   que as pessoas digitam **no YouTube**, que é onde os vídeos dele vivem —
   não no Google. Responde 200, sem chave e sem cota, e devolveu de cara
   "criatura cabeça de bode", "criaturas estranhas capturadas por câmeras",
   "lendas urbanas de terror". Isso é pauta; "brasileirão série a" não é.

POR QUE NÃO PELO NAVEGADOR: abrir a página renderizada daria um print para o
Samuel ler sozinho. Pegando os dados, o OMEGA consegue cruzar com as pastas
de `Criaturas/` e dizer o que está em alta e ele **ainda não fez** — que é a
pergunta de verdade por trás do pedido.
"""

from __future__ import annotations

import json
import re
import time
import unicodedata

import requests

_CABECALHOS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}
TEMPO_LIMITE = 25

# Sementes do canal. É por elas que se pergunta "o que está subindo AQUI
# DENTRO", em vez de perguntar o que o Brasil inteiro está buscando.
SEMENTES = ("criatura", "mitologia", "lenda", "monstro", "folclore",
            "criaturas assustadoras", "mitos")


def _sem_acento(t: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", t.lower())
                   if unicodedata.category(c) != "Mn")


# ---------- YouTube: o que se digita LÁ ----------

def sugestoes_youtube(semente: str, limite: int = 10) -> list[str]:
    """O autocomplete do YouTube. É a fonte mais direta do que o público busca."""
    try:
        r = requests.get(
            "https://suggestqueries-clients6.youtube.com/complete/search",
            params={"client": "youtube", "ds": "yt", "hl": "pt", "gl": "br",
                    "q": semente},
            headers=_CABECALHOS, timeout=TEMPO_LIMITE,
        )
        texto = r.text
        # A resposta vem embrulhada em JSONP quando o cliente é o do YouTube.
        i, j = texto.find("("), texto.rfind(")")
        dados = json.loads(texto[i + 1:j] if i > 0 else texto)
        return [x[0] for x in dados[1][:limite]]
    except Exception:  # noqa: BLE001 — sem internet é "não sei", não erro
        return []


# ---------- Google Trends: melhor-esforço ----------

def _sessao_trends():
    """O Trends exige um cookie da home antes de aceitar a API interna."""
    s = requests.Session()
    s.headers.update(_CABECALHOS)
    try:
        s.get("https://trends.google.com/trends/?geo=BR", timeout=TEMPO_LIMITE)
    except Exception:  # noqa: BLE001
        pass
    return s


def em_ascensao(termo: str, tentativas: int = 3) -> tuple[list[str], str]:
    """(consultas em ascensão, motivo se falhou).

    Melhor-esforço de propósito: o `widgetdata` do Trends devolve 429 com
    frequência, e insistir para sempre travaria o comando. Falhar dizendo o
    porquê é melhor que devolver lista vazia como se nada estivesse subindo.
    """
    s = _sessao_trends()
    req = {"comparisonItem": [{"keyword": termo, "geo": "BR",
                               "time": "today 12-m"}],
           "category": 0, "property": ""}
    try:
        r = s.get("https://trends.google.com/trends/api/explore",
                  params={"hl": "pt-BR", "tz": "180", "req": json.dumps(req)},
                  timeout=TEMPO_LIMITE)
        if not r.ok:
            return [], f"o Trends recusou a consulta ({r.status_code})"
        widgets = {w["id"]: w for w in json.loads(r.text[4:])["widgets"]}
    except Exception as e:  # noqa: BLE001
        return [], f"não consegui falar com o Trends ({str(e)[:40]})"

    alvo = widgets.get("RELATED_QUERIES") or widgets.get("RELATED_QUERIES_0")
    if not alvo:
        return [], "o Trends não tem consultas relacionadas para esse termo"

    for n in range(tentativas):
        try:
            r2 = s.get(
                "https://trends.google.com/trends/api/widgetdata/relatedsearches",
                params={"hl": "pt-BR", "tz": "180",
                        "req": json.dumps(alvo["request"]),
                        "token": alvo["token"]},
                timeout=TEMPO_LIMITE)
            if r2.ok:
                listas = json.loads(r2.text[5:])["default"]["rankedList"]
                # A segunda lista é a de ASCENSÃO; a primeira é só volume, e
                # volume alto costuma ser assunto já saturado.
                grupo = listas[1] if len(listas) > 1 else listas[0]
                return [f"{k['query']} ({k.get('formattedValue', '')})"
                        for k in grupo["rankedKeyword"][:10]], ""
            if r2.status_code == 429:
                time.sleep(2 * (n + 1))
                continue
            return [], f"o Trends respondeu {r2.status_code}"
        except Exception as e:  # noqa: BLE001
            return [], f"falha lendo o Trends ({str(e)[:40]})"
    return [], "o Trends está limitando as consultas agora (429)"


def alta_do_dia(geo: str = "BR", limite: int = 10) -> list[str]:
    """O 'em alta' geral. Guardado com a ressalva de que raramente serve."""
    try:
        r = requests.get(f"https://trends.google.com/trending/rss?geo={geo}",
                         headers=_CABECALHOS, timeout=TEMPO_LIMITE)
        titulos = re.findall(r"<title>(.*?)</title>", r.text, re.S)[1:]
        return [re.sub(r"<!\[CDATA\[|\]\]>", "", t).strip()
                for t in titulos[:limite]]
    except Exception:  # noqa: BLE001
        return []


# ---------- o que ele AINDA NÃO FEZ ----------

def _ja_tem() -> set[str]:
    try:
        from .projetos import listar_pastas

        return {_sem_acento(p.name) for p in listar_pastas()}
    except Exception:  # noqa: BLE001
        return set()


def _e_novidade(frase: str, feitos: set[str]) -> bool:
    """A sugestão fala de algo que ele ainda não produziu?"""
    limpa = _sem_acento(frase)
    return not any(f and f in limpa for f in feitos)


def pesquisar(assunto: str = "") -> str:
    """Material para o modelo analisar — não um veredito.

    Mesmo desenho de `web.conferir`: quem conclui é o modelo. O que este
    módulo garante é que a conclusão saia de dado buscado agora, e que o que
    ele já produziu seja separado do que é pauta nova.
    """
    assunto = (assunto or "").strip()
    sementes = [assunto] if assunto else list(SEMENTES)
    feitos = _ja_tem()

    partes: list[str] = []
    vistas: set[str] = set()
    novas, repetidas = [], []

    for semente in sementes[:7]:
        for s in sugestoes_youtube(semente):
            chave = _sem_acento(s)
            if chave in vistas or chave == _sem_acento(semente):
                continue
            vistas.add(chave)
            (novas if _e_novidade(s, feitos) else repetidas).append(s)

    if novas:
        partes.append("BUSCADO NO YOUTUBE — e o canal AINDA NÃO TEM:\n"
                      + "\n".join(f"- {s}" for s in novas[:25]))
    if repetidas:
        partes.append("Já existe projeto parecido para: "
                      + ", ".join(repetidas[:8]))

    # O Trends entra como reforço; quando falha, o motivo é dito.
    subindo, motivo = em_ascensao(assunto or "mitologia")
    if subindo:
        partes.append("EM ASCENSÃO no Google (12 meses, Brasil):\n"
                      + "\n".join(f"- {q}" for q in subindo))
    else:
        partes.append(f"(Google Trends indisponível agora: {motivo}. "
                      "Não trate isso como 'nada em alta'.)")

    if not novas and not subindo:
        return ("NÃO CONSEGUI DADOS de tendência agora. Diga isso ao senhor e "
                "ofereça tentar de novo — não invente o que está em alta.")

    return (
        f"TENDÊNCIAS BUSCADAS AGORA{f' sobre {assunto}' if assunto else ''}:\n\n"
        + "\n\n".join(partes)
        + "\n\n---\nISTO VAI SER FALADO EM VOZ ALTA: diga as 3 melhores "
        "pautas, UMA FRASE cada, na ordem em que apostaria, dizendo de onde "
        "saiu (YouTube ou Trends, com o número quando houver). Sem markdown e "
        "sem lista numerada — a voz lê os símbolos, e o detalhe já está na "
        "tela dele. Prefira o que o canal ainda não tem. Isto é sinal de "
        "busca, não garantia: não prometa alcance nem ranqueamento. Se houver "
        "regra do curso que se aplique ao título, use-a e cite a aula."
    )
