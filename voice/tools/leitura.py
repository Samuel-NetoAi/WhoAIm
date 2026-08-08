"""Leitura em voz alta dos documentos do projeto (pesquisa, roteiro, cenas).

Existe porque o Samuel nem sempre está na frente do PC: exibir na tela não
serve quando ele está montando cenário ou gravando. Ler resolve — mas ler
tem três armadilhas que este módulo trata:

1. CUSTO. Um dossiê tem ~27 mil caracteres e a conta gratuita da ElevenLabs
   dá 10 mil créditos POR MÊS. Ler um documento com ela torraria quase três
   meses de cota, então leitura longa vai SEMPRE na voz do Windows, que é
   grátis e ilimitada. A ElevenLabs fica para o diálogo curto.
2. MARKDOWN. Sem limpeza, a voz lê "asterisco asterisco título" e o texto
   vira ruído.
3. INTERRUPÇÃO. Um texto longo não pode virar uma sentença de dez minutos
   sem escapatória: a leitura é por blocos e obedece a "parar".
"""

from __future__ import annotations

import re
import threading

# Blocos curtos o bastante para "parar" responder rápido, longos o bastante
# para a fala não soar picotada.
# Blocos menores = 'parar' responde mais rápido (a checagem acontece entre
# blocos, e cada bloco só termina quando a voz acaba de falar).
MAX_BLOCO = 170

_estado: dict = {"lendo": False, "parar": False, "titulo": ""}

# Acima disto, narrar com a voz boa pede confirmação: a cota gratuita da
# ElevenLabs é de 10 mil créditos por MÊS e ~1 crédito por caractere.
LIMITE_SEM_PERGUNTAR = 1500
_pendente: dict = {}


def _limpar_markdown(texto: str) -> str:
    """Deixa só o que faz sentido ouvir."""
    t = texto
    t = re.sub(r"```.*?```", " ", t, flags=re.S)          # blocos de código
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", t)            # imagens
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", t)         # links -> texto
    t = re.sub(r"^\s*#{1,6}\s*", "", t, flags=re.M)        # títulos
    t = re.sub(r"^\s*\|.*\|\s*$", " ", t, flags=re.M)      # tabelas
    t = re.sub(r"^\s*[-*+]\s+", "", t, flags=re.M)         # marcadores
    t = re.sub(r"^\s*>\s?", "", t, flags=re.M)             # citações
    t = re.sub(r"[*_`~]+", "", t)                          # ênfases
    t = re.sub(r"https?://\S+", "", t)                     # URLs cruas
    t = re.sub(r"\n{2,}", "\n\n", t)
    return t.strip()


def _blocos(texto: str) -> list[str]:
    """Quebra em pedaços falaveis, respeitando fim de frase."""
    saida: list[str] = []
    for paragrafo in texto.split("\n\n"):
        paragrafo = " ".join(paragrafo.split())
        if not paragrafo:
            continue
        while len(paragrafo) > MAX_BLOCO:
            corte = paragrafo.rfind(". ", 0, MAX_BLOCO)
            if corte < 80:  # sem ponto útil: corta no espaço mais próximo
                corte = paragrafo.rfind(" ", 0, MAX_BLOCO)
            if corte <= 0:
                corte = MAX_BLOCO
            saida.append(paragrafo[: corte + 1].strip())
            paragrafo = paragrafo[corte + 1:].strip()
        if paragrafo:
            saida.append(paragrafo)
    return saida


def lendo() -> bool:
    return _estado["lendo"]


def confirmar_narracao() -> str | None:
    """Executa a narração cara que ficou aguardando. None = não havia nada."""
    if not _pendente:
        return None
    dados = dict(_pendente)
    _pendente.clear()
    return ler(dados["titulo"], dados["conteudo"], dados["ui"],
               bonita=True, ja_confirmado=True)


def parar() -> str:
    if not _estado["lendo"]:
        return "Não estou lendo nada, senhor."
    _estado["parar"] = True
    return "Interrompendo a leitura."


def ler(titulo: str, conteudo: str, ui, bonita: bool = False,
        ja_confirmado: bool = False) -> str:
    """Começa a ler em voz alta, numa thread própria.

    Devolve imediatamente a frase de confirmação — quem chama não pode ficar
    bloqueado por minutos de leitura.
    """
    # `falar_leitura` existe para o motor Live: lá, `falar` entrega o texto ao
    # MODELO dizer, o que para um dossiê de 27 mil caracteres queimaria a cota
    # e — pior — faria o modelo resumir em vez de ler. Ler é sempre com a voz
    # desta máquina. Quem não define o gancho (o motor local) usa `falar`, que
    # já sintetiza aqui mesmo.
    falar = getattr(ui, "falar_leitura", None) or getattr(ui, "falar", None)
    if falar is None:
        return "A voz não está disponível agora; o texto está na tela."
    if _estado["lendo"]:
        return f"Já estou lendo {_estado['titulo']}. Diga 'parar' antes."

    blocos = _blocos(_limpar_markdown(conteudo))
    if not blocos:
        return "Esse documento está vazio."

    caracteres = sum(len(b) for b in blocos)
    if bonita and not ja_confirmado and caracteres > LIMITE_SEM_PERGUNTAR:
        # Custo à vista ANTES de gastar: é dinheiro do usuário, e a conta
        # gratuita não aguenta um dossiê inteiro.
        _pendente.update({"titulo": titulo, "conteudo": conteudo, "ui": ui})
        return (
            f"Narrar {titulo} com a voz boa custa cerca de {caracteres} créditos "
            "da ElevenLabs, e a cota gratuita é de dez mil por mês. "
            "Diga 'confirmar' para narrar assim mesmo, ou 'ler' para a voz "
            "comum, que é ilimitada."
        )

    _estado.update({"lendo": True, "parar": False, "titulo": titulo})

    def laco() -> None:
        try:
            for i, bloco in enumerate(blocos, 1):
                if _estado["parar"]:
                    ui.write_log(f"SYS: leitura interrompida em {i} de {len(blocos)}.")
                    return
                # economico=True: voz do Windows. Ver o porquê no topo.
                falar(bloco, economico=not bonita)
            if not _estado["parar"]:
                ui.write_log(f"SYS: terminei de ler {titulo}.")
        finally:
            _estado.update({"lendo": False, "parar": False, "titulo": ""})

    threading.Thread(target=laco, daemon=True).start()

    minutos = max(1, round(sum(len(b) for b in blocos) / 900))
    return (
        f"Lendo {titulo} — {len(blocos)} trechos, uns {minutos} minuto(s). "
        "Diga 'parar' quando quiser."
    )
