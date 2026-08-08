"""Busca na web para o OMEGA conferir um fato por conta própria.

Motivo: hoje toda dúvida vira `pesquisar <criatura>`, que dispara o Claude
Code com a skill `pesquisa-seres` — minutos de trabalho e créditos gastos para
responder "em que ano saiu o conto do Cthulhu?". Faltava o degrau de baixo.

POR QUE NÃO A BUSCA DO GOOGLE DO GEMINI: seria o caminho óbvio (basta declarar
`googleSearch` como ferramenta), e foi o que tentei primeiro. A conta do Samuel
responde **429 nessa ferramenta especificamente** — o texto puro do mesmo
modelo responde 200. O grounding tem cota própria e ela está esgotada. Daí a
busca aqui ser feita à mão, sem chave e sem cota.

FRONTEIRA COM A SKILL — importa não borrar:
  `conferir`        checagem rápida de um fato, segundos, cita a fonte
  `pesquisar <X>`   dossiê completo com camadas de fonte e veredito

Um não substitui o outro, e o OMEGA deve dizer qual usou. Uma resposta de
`conferir` não vira material de roteiro: ela é o primeiro resultado de uma
busca, não uma apuração.

REGRA: nunca responder sem fonte. Se a busca não trouxe nada utilizável, a
resposta certa é "não consegui confirmar" — inventar é pior do que calar,
porque isso aqui alimenta vídeo publicado.
"""

from __future__ import annotations

import html
import re
import unicodedata
from urllib.parse import quote, urlparse

import requests

# Sem isto o DuckDuckGo devolve página vazia e a Wikipédia bloqueia.
_CABECALHOS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}

TEMPO_LIMITE = 20
MAX_RESULTADOS = 5
MAX_TEXTO_PAGINA = 4000


def _sem_acento(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto.lower())
                   if unicodedata.category(c) != "Mn")


def _limpar_html(trecho: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", trecho)).strip()


def buscar_wikipedia(pergunta: str, idioma: str = "pt",
                     limite: int = 3) -> list[dict]:
    """Busca DENTRO da Wikipédia. É a via mais confiável que existe sem chave.

    Testado: HTTP 200 consistente em pt e en. Também resolve grafia — o
    Samuel tem a pasta "Umibozu" e o verbete é "Umibōzu", com mácron.
    """
    try:
        r = requests.get(
            f"https://{idioma}.wikipedia.org/w/api.php",
            headers=_CABECALHOS,
            timeout=TEMPO_LIMITE,
            params={
                "action": "query", "list": "search", "srsearch": pergunta,
                "format": "json", "srlimit": limite,
            },
        )
        r.raise_for_status()
        achados = r.json().get("query", {}).get("search", [])
    except Exception:  # noqa: BLE001
        return []
    return [
        {
            "titulo": s["title"],
            "resumo": _limpar_html(s.get("snippet", "")),
            "url": f"https://{idioma}.wikipedia.org/wiki/"
                   f"{quote(s['title'].replace(' ', '_'))}",
        }
        for s in achados
    ]


def buscar(pergunta: str, limite: int = MAX_RESULTADOS) -> list[dict]:
    """Busca geral pelo DuckDuckGo. Lista vazia = não achou.

    Usa a API de resposta instantânea (JSON), não a raspagem do HTML: a
    página HTML passou a responder 202 com um layout diferente quando o
    DuckDuckGo estrangula raspagem, e os resultados somem em silêncio — do
    tipo de falha que só aparece meses depois, quando ninguém lembra.

    O 202 é aceito de propósito: a API devolve conteúdo bom com esse status.
    """
    try:
        r = requests.get(
            "https://api.duckduckgo.com/",
            headers=_CABECALHOS,
            timeout=TEMPO_LIMITE,
            params={"q": pergunta, "format": "json", "no_html": 1,
                    "skip_disambig": 1},
        )
        dados = r.json()
    except Exception:  # noqa: BLE001 — sem internet é "não confirmei", não erro
        return []

    saida: list[dict] = []
    if dados.get("AbstractText"):
        saida.append({
            "titulo": dados.get("Heading") or pergunta,
            "url": dados.get("AbstractURL", ""),
            "resumo": dados["AbstractText"],
        })
    for t in dados.get("RelatedTopics", []):
        # Os agrupados vêm aninhados em "Topics"; achatamos um nível.
        for item in (t.get("Topics") or [t]):
            if item.get("Text") and item.get("FirstURL"):
                saida.append({
                    "titulo": item["Text"].split(" - ")[0][:80],
                    "url": item["FirstURL"],
                    "resumo": item["Text"],
                })
            if len(saida) >= limite:
                return saida
    return saida[:limite]


def wikipedia(termo: str, idioma: str = "pt") -> dict | None:
    """Resumo da Wikipédia. É a fonte mais estável para nome de criatura."""
    try:
        r = requests.get(
            f"https://{idioma}.wikipedia.org/api/rest_v1/page/summary/"
            f"{quote(termo.replace(' ', '_'))}",
            headers=_CABECALHOS,
            timeout=TEMPO_LIMITE,
        )
        if r.status_code == 404 and idioma == "pt":
            return wikipedia(termo, idioma="en")  # muita criatura só tem verbete em inglês
        r.raise_for_status()
        dados = r.json()
    except Exception:  # noqa: BLE001
        return None
    if not dados.get("extract"):
        return None
    return {
        "titulo": dados.get("title", termo),
        "resumo": dados["extract"],
        "url": (dados.get("content_urls", {}).get("desktop", {}).get("page")
                or f"https://{idioma}.wikipedia.org/wiki/{quote(termo)}"),
        "idioma": idioma,
    }


def ler_pagina(url: str, maximo: int = MAX_TEXTO_PAGINA) -> str:
    """Texto legível de uma página. Vazio = não deu para ler."""
    try:
        r = requests.get(url, headers=_CABECALHOS, timeout=TEMPO_LIMITE)
        r.raise_for_status()
    except Exception:  # noqa: BLE001
        return ""
    corpo = r.text
    corpo = re.sub(r"<(script|style|nav|footer|header)[^>]*>.*?</\1>", " ", corpo,
                   flags=re.S | re.I)
    texto = _limpar_html(corpo)
    return re.sub(r"\s{2,}", " ", texto)[:maximo]


# Palavras que aparecem em qualquer pergunta e só atrapalham a busca.
_VAZIAS = {
    "o", "a", "os", "as", "de", "do", "da", "dos", "das", "e", "em", "no",
    "na", "um", "uma", "para", "pra", "com", "que", "qual", "quais", "quem",
    "quando", "onde", "como", "por", "ano", "sobre", "ser", "e", "foi",
    "origem", "historia", "história", "lenda", "mito", "mitologia",
    "folclore", "criatura", "verdade", "significa", "confere", "conferir",
    "me", "diz", "sabe", "se", "isso", "isto", "aquilo", "essa", "esse",
    "aquele", "aquela", "coisa", "negocio", "negócio", "tal",
}


def _termos_chave(pergunta: str) -> list[str]:
    """Consultas alternativas, da mais específica para a mais ampla.

    A busca da Wikipédia exige TODAS as palavras, então uma pergunta em frase
    ("Umibozu origem folclore") não acha nada mesmo quando o verbete existe.
    Foi exatamente assim que a primeira versão falhou: o modelo pergunta em
    frase, como gente, e a API responde vazio. Recuar para o nome próprio é o
    que uma pessoa faria ao ver zero resultados.
    """
    palavras = re.findall(r"[\wÀ-ÿ'-]+", pergunta)
    proprios = [p for p in palavras
                if p[:1].isupper() and p.lower() not in _VAZIAS]
    uteis = [p for p in palavras if p.lower() not in _VAZIAS and len(p) > 2]

    tentativas: list[str] = []
    if proprios:
        tentativas.append(" ".join(proprios))
        if len(proprios) > 1:
            tentativas.append(proprios[0])
    if uteis:
        tentativas.append(" ".join(uteis[:3]))
        # Uma palavra sozinha SÓ quando não há nome próprio. "Mais longa" não
        # é o mesmo que "mais distintiva": em "Zxqwbrtl Vplmqx criatura
        # inventada", a mais longa é "inventada", e buscá-la trouxe artigos
        # sobre a Inglaterra e a Itália. Fonte irrelevante é pior que fonte
        # nenhuma, porque convida o modelo a costurar uma resposta.
        if not proprios:
            tentativas.append(max(uteis, key=len))

    vistos, saida = set(), []
    for t in tentativas:
        chave = t.lower()
        if chave and chave != pergunta.lower().strip() and chave not in vistos:
            vistos.add(chave)
            saida.append(t)
    return saida


def conferir(pergunta: str) -> str:
    """O material para o modelo responder — sempre com as fontes junto.

    Devolve TEXTO, não uma resposta pronta: quem conclui é o modelo, que tem o
    contexto da conversa. O que este módulo garante é que ele conclua a partir
    de algo que foi lido agora, e não da memória de treino.
    """
    pergunta = (pergunta or "").strip()
    if not pergunta:
        return "Conferir o quê, senhor?"

    partes: list[str] = []
    vistas: set[str] = set()

    # As palavras que a fonte PRECISA mencionar para valer alguma coisa. Sem
    # esta trava, o recuo para termos mais amplos devolve material que não tem
    # relação com a pergunta — e o modelo, recebendo "fontes consultadas",
    # tende a costurar uma resposta a partir delas. A regra de nunca inventar
    # não se sustenta só na instrução; o material entregue tem que ser limpo.
    distintivas = {
        _sem_acento(p) for p in re.findall(r"[\wÀ-ÿ'-]+", pergunta)
        if len(p) > 3 and p.lower() not in _VAZIAS
    }

    def relevante(titulo: str, resumo: str) -> bool:
        if not distintivas:
            return True
        texto = _sem_acento(f"{titulo} {resumo}")
        return any(termo in texto for termo in distintivas)

    def juntar(titulo: str, resumo: str, url: str) -> None:
        if not resumo or url in vistas:
            return
        if not relevante(titulo, resumo):
            return
        vistas.add(url)
        partes.append(f"{titulo}\n{resumo}\nFonte: {url}")

    # A pergunta como veio primeiro; se não render, os termos-chave dela.
    for consulta in [pergunta, *_termos_chave(pergunta)]:
        verbete = wikipedia(consulta)
        if verbete:
            marca = "" if verbete["idioma"] == "pt" else " (verbete em inglês)"
            juntar(f"WIKIPÉDIA — {verbete['titulo']}{marca}",
                   verbete["resumo"], verbete["url"])

        for a in buscar_wikipedia(consulta) or buscar_wikipedia(consulta, "en"):
            juntar(f"WIKIPÉDIA — {a['titulo']}", a["resumo"], a["url"])

        for achado in buscar(consulta, limite=3):
            juntar(achado["titulo"], achado["resumo"], achado["url"])

        # Achou material suficiente: parar de gastar requisição.
        if len(partes) >= 3:
            break

    if not partes:
        # Silêncio honesto. O modelo é instruído a não preencher a lacuna.
        return (
            f"NADA ENCONTRADO sobre: {pergunta}\n"
            "Não confirme nada a partir disto — diga que não conseguiu "
            "confirmar e ofereça a pesquisa completa."
        )

    return (
        f"FONTES CONSULTADAS AGORA para: {pergunta}\n\n"
        + "\n\n".join(partes)
        + "\n\n---\nResponda em uma ou duas frases, CITANDO a fonte. Isto é "
        "uma checagem rápida, não uma apuração: se o assunto for virar "
        "roteiro, diga que o certo é a pesquisa completa da criatura."
    )
