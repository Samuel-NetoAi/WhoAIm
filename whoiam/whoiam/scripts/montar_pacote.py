#!/usr/bin/env python3
"""
Monta o PACOTE que vai para a extensão do Claude no navegador.

Por que existe (2026-10-06): a extensão NÃO tem acesso ao disco. Um EXECUTAR.md que manda
"abrir C:\\...\\referencias.md", "anexar C:\\...\\johansen.png" e "conferir se o arquivo foi
salvo" é impossível de executar — ela parou, com razão. O pacote resolve as três coisas:

  - os prompts vão DENTRO do PACOTE.md (nenhum caminho para abrir);
  - as fichas que precisam ir como anexo são copiadas para a pasta do pacote, e o Samuel
    arrasta a pasta inteira para o chat da extensão;
  - imagem gerada num item e usada como anexo de outro vira "a imagem que você gerou acima
    nesta conversa" (não existe ainda no disco);
  - a extensão só baixa, em ordem; quem renomeia, move e confere é o Claude Code, com
    receber_pacote.py, que lê a lista ARQUIVOS ESPERADOS deste pacote.

Uso:
  python montar_pacote.py --referencias "<pasta do bloco>\\referencias.md"   (passo 1: imagens no GPT)
  python montar_pacote.py --cena "<pasta do bloco>\\cena.txt"                (passo 4: vídeo no Cinema Studio)
"""

import argparse
import datetime as dt
import re
import shutil
import sys
from pathlib import Path


def _norm(p: str) -> str:
    return p.strip().strip("`").replace("/", "\\").lower()


def _itens_referencias(texto: str) -> list[dict]:
    partes = re.split(r"^### ", texto, flags=re.M)[1:]
    itens = []
    for parte in partes:
        nome = parte.split()[0]
        # cada prompt pede a imagem com o nome do arquivo como título, para a extensão
        # e o Samuel conferirem a ordem dos downloads pelo nome que o ChatGPT mostra
        anexar = re.search(r"^ANEXAR NO GPT:\s*(.*)$", parte, re.M)
        salvar = re.search(r"^SALVAR COMO:\s*(.*)$", parte, re.M)
        prompt = re.search(r"^PROMPT:\s*\n```\n(.*?)\n```", parte, re.M | re.S)
        if not (salvar and prompt):
            continue
        anexos = []
        if anexar:
            anexos = [a.strip() for a in anexar.group(1).split("·") if a.strip()
                      and not a.strip().lower().startswith("nada")]
        itens.append({"nome": nome, "anexos": anexos, "salvar": salvar.group(1).strip(),
                      "prompt": prompt.group(1).rstrip()})
    return itens


CABECALHO = """\
# PACOTE — {titulo}

> **Para a extensão do Claude no navegador. Este arquivo é autocontido: tudo o que você precisa
> está aqui ou nos arquivos que o Samuel anexou nesta conversa.** Você não precisa — e não deve —
> abrir caminhos do disco do Samuel, nem usar a Biblioteca do ChatGPT ("Add from library"): lá
> estão imagens de tentativas anteriores que não servem.
>
> **Não revisar nem reescrever os prompts: executar.** Se algo não bater, parar e perguntar ao
> Samuel, sem gerar.

CRIADO EM: {criado}
"""


def pacote_referencias(arq: Path) -> Path:
    texto = arq.read_text(encoding="utf-8")
    itens = _itens_referencias(texto)
    if not itens:
        raise SystemExit("Nenhum item com SALVAR COMO + PROMPT encontrado em " + str(arq))
    titulo = texto.splitlines()[0].lstrip("# ").strip()
    pasta = arq.parent / "_pacote_passo1"
    if pasta.exists():
        shutil.rmtree(pasta)
    pasta.mkdir()

    gerados: dict[str, tuple] = {}    # caminho salvar normalizado -> (ordem, nome do arquivo)
    copiados: dict[str, str] = {}     # caminho de origem normalizado -> nome no pacote
    faltando: list[str] = []
    blocos: list[str] = []
    esperados: list[str] = []

    for n, it in enumerate(itens, 1):
        linhas_anexo = []
        for a in it["anexos"]:
            chave = _norm(a)
            if chave in gerados:
                ordem, nome_g = gerados[chave]
                linhas_anexo.append(f"a imagem **{nome_g}** que você gerou acima nesta conversa (a {ordem}ª imagem gerada)")
                continue
            origem = Path(a.strip().strip("`"))
            if chave not in copiados:
                if not origem.exists():
                    faltando.append(f"{it['nome']}: {a}")
                    continue
                nome_copia = f"anexo_{len(copiados) + 1:02d}_{origem.name}"
                shutil.copy2(origem, pasta / nome_copia)
                copiados[chave] = nome_copia
            linhas_anexo.append(f"o arquivo **{copiados[chave]}**, anexado pelo Samuel nesta conversa")
        destino_nome = Path(it["salvar"]).name
        gerados[_norm(it["salvar"])] = (n, destino_nome)
        esperados.append(it["salvar"])
        anexos_txt = "\n".join(f"  - {l}" for l in linhas_anexo) or "  - nenhum"
        anteriores = [(int(re.search(r"a (\d+)ª", l).group(1)), l.split("**")[1])
                      for l in linhas_anexo if "gerou acima" in l]
        prefixo = ""
        if anteriores:
            nomes = "; ".join(f"image number {o} that you generated in this conversation ({Path(x).stem})"
                              for o, x in anteriores)
            prefixo = f"Also use, as attached references, these earlier images from this conversation: {nomes}.\n\n"
        blocos.append(
            f"## IMAGEM {n} de {len(itens)} — {destino_nome}\n\n"
            f"**Anexar no ChatGPT antes de colar o prompt:**\n{anexos_txt}\n"
            + ("  (as imagens geradas acima não se anexam de novo: o prompt abaixo já começa\n"
               "  apontando para elas)\n" if anteriores else "")
            + f"\n**Prompt — colar inteiro, sem editar:**\n```\n{prefixo}{it['prompt']}\n```\n\n"
            f"**Depois:** baixar a imagem (botão de download do ChatGPT) e dizer no relatório:\n"
            f"`{n}. {destino_nome} — baixada como <nome que o Chrome deu>`. Só então seguir para a próxima.\n"
        )

    if faltando:
        shutil.rmtree(pasta)
        raise SystemExit("Anexos que não existem no disco (gerar ou corrigir antes):\n- " + "\n- ".join(faltando))

    criado = dt.datetime.now().isoformat(timespec="seconds")
    corpo = CABECALHO.format(titulo=titulo + " · PASSO 1: imagens no ChatGPT", criado=criado)
    corpo += f"""
## Como executar

> ⚠️ **ChatGPT, com a geração de imagem NATIVA do GPT. NÃO usar o MCP do Higgsfield. NÃO abrir o
> Higgsfield neste passo.**

1. Abrir uma **conversa NOVA** no chatgpt.com, sem nenhuma imagem anterior.
2. Gerar as **{len(itens)} imagens abaixo, nesta ordem**, todas nesta mesma conversa nova.
3. Em cada uma: anexar o que está indicado (só arquivos anexados nesta conversa pelo Samuel, ou a
   imagem gerada acima), colar o prompt inteiro, esperar, **baixar**. Cada download pede o OK do
   Samuel — é normal.
4. O nome com que o Chrome salva não importa: o Claude Code renomeia e move depois, pela ordem.
   **Não pular imagem e não baixar nada fora desta lista** — a ordem dos downloads é o que diz qual
   arquivo é qual.
5. Recusa do filtro: reescrever no máximo 2 vezes só a parte recusada; se não passar, registrar e
   seguir para a próxima (e dizer no relatório que aquela não foi baixada).
6. Se uma imagem precisar ser gerada de novo, a "image number N" citada nos prompts seguintes é a
   **versão aceita** dela: diga isso ao GPT numa linha antes de colar o prompt seguinte. E baixe só
   a versão aceita.
7. **Ao terminar, PARAR** e mandar o relatório: a lista numerada de downloads. O Samuel aprova as
   imagens; nada de Higgsfield antes disso.

"""
    corpo += "\n---\n\n".join(blocos)
    corpo += "\n---\n\n## ARQUIVOS ESPERADOS, NA ORDEM (para o receber_pacote.py)\n"
    corpo += "\n".join(f"{i}. {e}" for i, e in enumerate(esperados, 1)) + "\n"
    (pasta / "PACOTE.md").write_text(corpo, encoding="utf-8")
    return pasta


def pacote_cena(arq: Path) -> Path:
    texto = arq.read_text(encoding="utf-8")
    titulo = texto.splitlines()[0].lstrip("# ").strip()
    m_pasta = re.search(r"^PASTA DAS IMAGENS:\s*(.*)$", texto, re.M)
    m_video = re.search(r"^SALVAR O V[ÍI]DEO GERADO EM:\s*(.*)$", texto, re.M)
    m_settings = re.search(r"^## 1\. SETTINGS.*?$(.*?)^## 2\.", texto, re.M | re.S)
    m_elements = re.search(r"^## 3\. ELEMENTS.*?\n(.*?)\n", texto, re.M)
    m_prompt = re.search(r"^## 5\. PROMPT.*?```\n(.*?)\n```", texto, re.M | re.S)
    if not (m_pasta and m_video and m_settings and m_prompt):
        raise SystemExit("cena sem PASTA DAS IMAGENS, SALVAR O VÍDEO, SETTINGS ou PROMPT")
    origem = Path(m_pasta.group(1).strip())
    linhas = re.findall(r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", texto, re.M)
    pasta = arq.parent / "_pacote_passo4"
    if pasta.exists():
        shutil.rmtree(pasta)
    pasta.mkdir()
    faltando, tabela = [], []
    for num, nome, papel in linhas:
        f = origem / nome
        if not f.exists():
            faltando.append(str(f))
            continue
        # nome neutro: o arquivo enviado ao Higgsfield não carrega nome de personagem
        # (suspeita do bloqueio "pessoa real ou figura pública", 2026-10-08)
        copia = f"imagem_{int(num):02d}{f.suffix}"
        shutil.copy2(f, pasta / copia)
        tabela.append(f"| {num} | {copia} | {papel} |")
    if faltando:
        shutil.rmtree(pasta)
        raise SystemExit("Referências que ainda não estão na pasta (passo 1 e 2 primeiro):\n- " + "\n- ".join(faltando))
    take = m_video.group(1).strip().replace("<n>", "1")
    criado = dt.datetime.now().isoformat(timespec="seconds")
    corpo = CABECALHO.format(titulo=titulo + " · PASSO 4: vídeo no Cinema Studio", criado=criado)
    corpo += f"""
## Como executar

> ⚠️ **Higgsfield Cinema Studio 4.0, modo Video. Custa 75 créditos: precisa do OK do Samuel nesta
> conversa ANTES de clicar em gerar.**

1. Cinema Studio 4.0 → modo Video. Preencher as SETTINGS abaixo, uma por uma, e conferir **480p** no
   seletor (o padrão é 720p e cobra 720p sem avisar).
2. Subir as imagens anexadas nesta conversa, **nesta ordem** (imagem_01 = @Image 1):

| @Image | Arquivo anexado | Papel |
|---|---|---|
{chr(10).join(tabela)}

3. Colar o PROMPT abaixo inteiro, sem editar. Conferir que todos os `@` ficaram **verdes**:
   {m_elements.group(1).strip() if m_elements else ''}
   Algum não ficou verde: PARAR e avisar o Samuel.
4. **PARAR e pedir o OK do Samuel**, mostrando o custo que a tela indica.
5. Com o OK: gerar, esperar, baixar o vídeo. O Claude Code renomeia e move depois.

## SETTINGS
{m_settings.group(1).strip()}

## PROMPT — colar inteiro
```
{m_prompt.group(1).rstrip()}
```

## ARQUIVOS ESPERADOS, NA ORDEM (para o receber_pacote.py)
1. {take}
"""
    (pasta / "PACOTE.md").write_text(corpo, encoding="utf-8")
    return pasta


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Monta o pacote autocontido para a extensão")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--referencias", help="caminho do referencias.md (passo 1)")
    g.add_argument("--cena", help="caminho do cena.txt / cena.md (passo 4)")
    a = ap.parse_args()
    pasta = pacote_referencias(Path(a.referencias)) if a.referencias else pacote_cena(Path(a.cena))
    arquivos = sorted(p.name for p in pasta.iterdir())
    print(f"Pacote pronto: {pasta}")
    print("Arrastar TODOS estes arquivos para o chat da extensão:")
    for nome in arquivos:
        print("  -", nome)


if __name__ == "__main__":
    main()
