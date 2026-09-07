# Omega — leia o vault antes de reler o projeto

Existe um segundo cérebro nesta máquina: **`D:\Agentes`**, um vault do Obsidian.
As notas de `D:\Agentes\_registros\` são **resumos curados** dos documentos longos deste
repositório. **Ler a nota curta primeiro e parar ali é o comportamento correto**, não um atalho.

## Ordem de leitura — e onde PARAR

1. **`D:\Agentes\_registros\ESTADO.md`** (2,8 KB) — sempre. É o estado da casa, gerado de fatos
   verificáveis, e traz a tabela de para-onde-ir.
2. **A nota do assunto**, da tabela abaixo. **Pare aqui na maioria das tarefas.**
3. **O documento longo em `Omega\`** — só quando a nota não bastou. São 30 KB cada; a nota tem 5.

As notas de `_registros` existem para você **não** abrir os documentos longos. Se você abriu o
documento longo e a nota já respondia, você gastou contexto à toa.

## Roteamento por assunto

| A tarefa toca... | Nota curta (leia esta) | Documento longo (só se faltar) |
|---|---|---|
| gasto de crédito, resolução, modelo de vídeo | `_registros\HIGGSFIELD.md` | `REGRAS-PRODUCAO-VIDEO.md`, `planejamento-fluxo-higgsfield.md` |
| Blender, blockout, previz, cena 3D | `_registros\BLENDER.md` | `ESTUDO-BLENDER-2026-09-06.md` |
| escrever prompt de Seedance | `_registros\HIGGSFIELD.md` | `GUIA-PROMPT-SEEDANCE-2-5.md` |
| Higgsfield Academy, padrões da coleção | `_registros\HIGGSFIELD.md` | `ESTUDO-ACADEMY-HIGGSFIELD-completo.md` |
| publicar vídeo, upload, API do YouTube | `_registros\YOUTUBE.md` | a skill `postagem` |
| edição, render, Studio, legendas | — *(sem nota ainda)* | `ESTUDO-STUDIO-melhorias-2026-09-02.md` |
| Alpha / Telegram / 2FA | `_registros\ALPHA.md` | `PLANO-ALPHA.md` |
| regras que valem para todos os agentes | `_registros\CONSTELACAO.md` | — |
| erro que já cometemos antes | `_aprendizado\LICOES.md` | as lições em `_aprendizado\licoes\` |
| o que espera decisão do Samuel | `_registros\PENDENTE-SAMUEL.md` | `SUGESTOES.md` |

## Gatilhos — consultar ANTES de agir, não "quando lembrar"

Estes disparam por **artefato**, não por intenção. Se você está prestes a fazer o da esquerda,
a leitura da direita não é opcional:

- **escrever qualquer chamada de vídeo** (`resolution`, `turbo`, escolha de modelo) → `HIGGSFIELD.md`
- **abrir o Blender** → `BLENDER.md` §0 — há **dois portões de aprovação do Samuel**, e o primeiro
  é avisar antes de abrir
- **propor qualquer gasto de crédito** → `HIGGSFIELD.md`
- **escrever script `bpy`** → `ESTUDO-BLENDER-2026-09-06.md` §4 — quatro mudanças de API da 5.x que
  quebram script de 4.x
- **pesquisar qualquer coisa na web** → chamar `salomao_lembrar` PRIMEIRO. Já aconteceu de
  repesquisarmos um assunto que o Salomão tinha apurado 11 dias antes.

## Duas regras de manutenção

**A verdade do repositório vence o resumo do vault.** Se a nota discordar do código ou do
documento longo, o repositório está certo — e a nota tem que ser corrigida, não ignorada em
silêncio.

**`ESTADO.md` e `MISSOES.md` são GERADAS** por `python -m _comum.estado` (rodar de `D:\Agentes`).
Edição à mão nelas é perdida na próxima geração. Conteúdo escrito à mão vai nas outras notas de
`_registros\`.
