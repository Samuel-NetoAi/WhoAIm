#!/usr/bin/env python3
"""
Portão de entrega da skill whoiam, executado por código (hook do Claude Code).

Existe porque a lista de regras escrita no SKILL.md não era seguida: o Claude escrevia
prompts de memória e os arquivos chegavam à extensão do navegador sem o aviso de
destino, sem a ordem dos passos e sem caminhos (2026-10-06). Regra que depende de
alguém lembrar não é regra.

Dois modos:
  --lembrete   (hook UserPromptSubmit) se a mensagem do Samuel fala de bloco/cena/
               referência/prompt/componente, imprime o portão de entrega, que entra
               no contexto do Claude antes de ele responder.
  --validar    (hook PostToolUse em Write/Edit) se o arquivo salvo é um prompt de
               produção em C:\\Ai-Project\\Criaturas, confere as regras e, se faltar
               algo, sai com código 2: o erro volta para o Claude, que tem de corrigir.

Também roda à mão:  python validar_bloco.py --arquivo "<caminho>"
"""

import json
import re
import sys
from pathlib import Path

GATILHO = re.compile(r"\b(bloco|cena|refer[eê]ncia|prompt|componente|model sheet|element)", re.I)

LEMBRETE = """\
[PORTÃO DE ENTREGA — skill whoiam — obrigatório antes de escrever qualquer prompt de produção]
Antes de escrever: abrir com a ferramenta Skill a `whoiam` e ler o arquivo da etapa
(etapa-2-componentes.md / etapa-3-referencias.md / etapa-4-cena.md) e estilo-e-contencao.md.
Não escrever de memória.
1. A etapa anterior está aprovada pelo Samuel?
2. O bloco tem EXECUTAR.md (o mapa) com os passos em ordem: imagens no ChatGPT → aprovação →
   Elements → vídeo, cada um com ponto de PARAR. A extensão NÃO lê o disco: ela recebe só a pasta
   _pacote_passoN, montada com scripts/montar_pacote.py (prompts dentro, anexos copiados).
3. Topo de todo arquivo e de todo item de imagem: "ChatGPT, imagem nativa do GPT — NÃO usar o MCP
   do Higgsfield". Topo do cena: "PASSO 4 de 4 — não começar por aqui".
4. Caminhos completos: anexos, onde salvar cada imagem, onde salvar o vídeo.
5. 3 a 4 cortes; no máximo 1 ação principal a cada 3 s por beat; nenhuma instrução anula outra.
6. Na resposta ao Samuel: qual pasta _pacote_passoN arrastar para a extensão, e que ele diga
   "pronto" quando ela terminar, para o Claude Code rodar receber_pacote.py.
O hook validar_bloco.py confere isso quando o arquivo é salvo."""

RAIZ = "ai-project" + "\\" + "criaturas"


def _tem(texto: str, *frases: str) -> bool:
    t = texto.lower()
    return all(f.lower() in t for f in frases)


def validar(caminho: Path) -> list[str]:
    nome = caminho.name.lower()
    texto = caminho.read_text(encoding="utf-8", errors="replace")
    erros: list[str] = []
    pasta = caminho.parent

    if "_antigas" in str(caminho).lower():
        return []

    if nome.startswith("cena"):
        if not _tem(texto, "passo 4 de 4"):
            erros.append("cena sem o aviso 'PASSO 4 de 4 — não começar por aqui' no topo")
        if not (_tem(texto, "nativa do gpt") and _tem(texto, "mcp")):
            erros.append("cena sem lembrar que as imagens vêm do ChatGPT (imagem nativa), NÃO do MCP do Higgsfield")
        if not re.search(r"PASTA DAS IMAGENS:\s*C:\\", texto):
            erros.append("cena sem 'PASTA DAS IMAGENS: C:\\...' (caminho completo)")
        if not re.search(r"SALVAR O V[ÍI]DEO GERADO EM:\s*C:\\", texto):
            erros.append("cena sem 'SALVAR O VÍDEO GERADO EM: C:\\...' (caminho completo)")
        if not _tem(texto, "480p"):
            erros.append("cena sem 480p")
        for secao in ("CAST AND REFERENCES", "CONTINUITY", "REVEAL", "BEATS", "SOUND",
                      "POSITIVE LOCKS", "RECAP"):
            if secao not in texto:
                erros.append(f"cena sem a seção {secao}")
        if re.search(r"\bHold\.\s*$|END hold|\blast frame of (the )?(shot|scene)|\bfirst frame of shot", texto, re.M | re.I):
            erros.append("cena com quadro parado ('Hold.', 'last/first frame of shot'): a referência é um "
                         "momento por onde a ação passa; nenhum beat começa ou termina parado")
        cortes = texto.count("\nCUT TO")
        if cortes > 3:
            erros.append(f"cena com {cortes} cortes: o máximo é 3 cortes (4 planos) em 30 s")
        if not (pasta / "EXECUTAR.md").exists():
            erros.append(f"falta EXECUTAR.md em {pasta} — é o mapa do bloco")

    elif nome in ("referencias.md", "componentes.md"):
        if not (_tem(texto, "nativa do gpt") and _tem(texto, "não usar o mcp do higgsfield")):
            erros.append(f"{nome} sem o aviso no topo: 'ChatGPT, imagem nativa do GPT — NÃO usar o MCP do Higgsfield'")
        if not _tem(texto, "passo 1"):
            erros.append(f"{nome} sem dizer que é o PASSO 1 e onde parar")
        salvar = re.findall(r"^SALVAR COMO:\s*(.*)$", texto, re.M)
        destino = re.findall(r"^DESTINO:\s*ChatGPT", texto, re.M)
        if len(destino) < len(salvar):
            erros.append(f"{nome}: {len(salvar)} itens com SALVAR COMO, mas só {len(destino)} com 'DESTINO: ChatGPT — imagem nativa (NÃO usar o MCP do Higgsfield)'")
        for s in salvar:
            if not s.strip().startswith("C:\\"):
                erros.append(f"{nome}: SALVAR COMO sem caminho completo: {s.strip()}")
        for a in re.findall(r"^ANEXAR NO GPT:\s*(.*)$", texto, re.M):
            for parte in a.split("·"):
                p = parte.strip()
                if p and not p.lower().startswith(("c:\\", "nada")):
                    erros.append(f"{nome}: anexo sem caminho completo: {p}")
        if nome == "referencias.md" and not (pasta / "EXECUTAR.md").exists():
            erros.append(f"falta EXECUTAR.md em {pasta}")

    elif nome == "executar.md":
        if not _tem(texto, "passo 1 de"):
            erros.append("EXECUTAR.md sem os passos numerados ('PASSO 1 de N')")
        if not _tem(texto, "não usar o mcp do higgsfield"):
            erros.append("EXECUTAR.md sem 'NÃO usar o MCP do Higgsfield' no passo das imagens")
        if not _tem(texto, "parar"):
            erros.append("EXECUTAR.md sem os pontos de PARAR")
        if not _tem(texto, "_pacote_passo1"):
            erros.append("EXECUTAR.md não diz qual pasta _pacote_passoN vai para a extensão (ela não lê o disco)")
        if not _tem(texto, "receber_pacote"):
            erros.append("EXECUTAR.md não diz que o Claude Code recebe os downloads com receber_pacote.py")
        if _tem(texto, "cinema studio") and not _tem(texto, "ok do samuel"):
            erros.append("EXECUTAR.md: o passo do vídeo não pede o OK do Samuel antes de gastar crédito")

    return erros


def _eh_arquivo_de_producao(caminho: str) -> bool:
    c = caminho.replace("/", "\\").lower()
    nome = Path(c).name
    return RAIZ in c and (nome.startswith("cena") or nome in ("referencias.md", "componentes.md", "executar.md"))


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    modo = sys.argv[1] if len(sys.argv) > 1 else ""

    if modo == "--arquivo":
        erros = validar(Path(sys.argv[2]))
        print("\n".join(erros) if erros else "OK — passou no portão de entrega")
        return 1 if erros else 0

    try:
        dados = json.load(sys.stdin)
    except Exception:
        return 0

    if modo == "--lembrete":
        if GATILHO.search(dados.get("prompt", "")):
            print(LEMBRETE)
        return 0

    if modo == "--validar":
        caminho = (dados.get("tool_input") or {}).get("file_path", "")
        if not caminho or not _eh_arquivo_de_producao(caminho) or not Path(caminho).exists():
            return 0
        erros = validar(Path(caminho))
        if erros:
            print("PORTÃO DE ENTREGA REPROVOU " + caminho + ":\n- " + "\n- ".join(erros)
                  + "\nCorrigir antes de entregar ao Samuel. Regras: skill whoiam, SKILL.md "
                  "(PORTÃO DE ENTREGA) e etapa-*.md.", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
