---
name: whoiam
description: >
  Pipeline de PRODUÇÃO do canal WhoIAm (YouTube de mitologia/criaturas feito com IA), do roteiro
  pronto até o vídeo gerado no Higgsfield. Use SEMPRE que o Samuel entregar um roteiro (20 partes),
  pedir "os componentes de [X]", "as referências do bloco N", "o prompt da cena N", model sheet,
  Element do Higgsfield, ficha do Cinema Studio, orçamento em créditos, julgar um take que voltou,
  ou quando ele descrever/opinar sobre cenas de um vídeo em produção. Também cobre a pós-produção
  (montagem no Studio, legenda-base, narração ElevenLabs, trilha) quando ele pedir. Entrega
  arquivos prontos para a extensão do Claude no navegador executar: prompts de imagem para o GPT,
  nomes de arquivo, labels de Element e o prompt de cena para o Cinema Studio. FRONTEIRA: pesquisa
  de lore é a skill `pesquisa-seres` (rodada pelo Omega); o roteiro é escrito pelo Samuel; título,
  thumbnail, SEO e calendário são a skill `postagem`.
---

# WhoIAm — Pipeline de Produção

Esta skill pega o roteiro que o Samuel escreveu e transforma em vídeo: componentes (model sheets),
imagens de referência por bloco e o prompt de cena de cada bloco. Tudo sai em arquivos com nome e
pasta fixos, porque quem executa as gerações de imagem e o cadastro no Higgsfield é a **extensão do
Claude no navegador**, e ela precisa de instruções sem ambiguidade.

> ⚫ **Esta é a versão 2026-10-06 da skill, e ela substitui todas as anteriores.** Não existem mais
> storyboard, folha de painéis, Kairogen, Leonardo, roteamento de modelo, template
> `[SUBJECT]/[ACTION]`, nem formato `GOAL/STAGES/NEGATIVES`. Se você encontrar qualquer um desses em
> outro arquivo, pacote `.skill` antigo ou nota, **é histórico — não use**. O único formato de
> prompt de cena é o de `references/etapa-4-cena.md`.

---

## AS ETAPAS — uma de cada vez, cada uma com portão

| # | Etapa | Quem faz | Entra | Sai (arquivo) | Portão |
|---|---|---|---|---|---|
| 0 | **Pesquisa** | Omega, com a skill `pesquisa-seres` | o nome da criatura | `<nome>-video/notes/dossie.md` | Samuel leu |
| 1 | **Roteiro** | Samuel, acertando detalhes com o GPT | o dossiê | roteiro em **20 partes** | Samuel entrega aqui |
| 2 | **Componentes** | esta skill → extensão executa | roteiro + dossiê | `componentes/componentes.md` + imagens + Elements | Samuel aprova as imagens |
| 3 | **Referências do bloco** | esta skill → extensão executa | roteiro da parte N + componentes | `blocos/bloco-NN/referencias.md` + imagens `ref_` | Samuel aprova |
| 4 | **Prompt de cena** | esta skill | referências aprovadas + take anterior | `blocos/bloco-NN/cena.md` | Samuel aprova **antes do crédito** |
| 5 | **Geração e aceitação** | Cinema Studio (extensão ou Samuel) | `cena.md` | `blocos/bloco-NN/takes/` | rubrica de aceitação |
| 6 | **Pós-produção** | Studio + ElevenLabs + Samuel | os 20 takes aprovados | vídeo montado e narrado | Samuel |
| 7 | **Publicação** | skill `postagem` | vídeo final | — | — |

**Etapas 3 → 4 → 5 rodam bloco a bloco, em ordem.** O prompt do bloco N+1 é escrito depois que o
take do bloco N foi aprovado, porque a continuidade depende do que realmente saiu (último quadro,
última pose, estado dos personagens). Escrever os 20 de uma vez só se o Samuel pedir.

**Nunca abrir a etapa seguinte com a anterior pela metade.** Se o Samuel pedir para pular ou
juntar etapas, siga o pedido: as etapas são o padrão, não uma prisão.

### O que vem do roteiro

- **20 partes = 20 blocos = 20 gerações de 30 s** (~10 min de vídeo). A parte N vira o `bloco-NN`.
- O roteiro diz **o que acontece, quem está lá, onde, e a emoção do momento**. Às vezes traz um
  **efeito pedido** para uma cena ("quero câmera lenta aqui", "quero que a água pare no ar"): esse
  pedido é inviolável e entra no `cena.md` como `EFEITO PEDIDO`, com a forma de executá-lo.
- O roteiro do Samuel é a fonte. Lore extra do dossiê só entra se ele pediu.
- Roteiro antigo encontrado em `Criaturas\<Nome>\<nome>-video\notes\roteiro.md` é **anterior ao
  modelo atual**: serve de base, não é produto final.

---

## REGRAS QUE NÃO MUDAM ENTRE ETAPAS

1. **O Samuel dita a cena; a skill dirige.** Ele diz o que acontece. Enquadramento, lente,
   movimento, posição dos corpos, cortes e ritmo são decisão da skill, **declarada com o porquê**.
   Nunca devolver pergunta técnica ("qual lente?"). Pergunta de **intenção** é legítima ("essa
   cena é de ameaça ou de luto?"). Os elementos que ele descreveu são invioláveis; mudar um deles
   é sugestão, nunca decisão.
2. **Plataforma única:** vídeo no **Cinema Studio 4.0 (web)**, que roda o **Seedance 2.5** por
   baixo, com presets de câmera/luz/paleta escolhidos antes. **480p · 16:9 · 30 s · Áudio On.**
   Detalhe, custo e limites: `references/plataforma-e-custo.md`.
3. **Imagem não se gera no Higgsfield.** Componentes e referências são gerados no **GPT** pela
   extensão, para o crédito do Higgsfield ir inteiro para vídeo.
4. **Sem fala, sem música, sem texto na tela.** O vídeo sai com **som da cena apenas** (chuva,
   passos, madeira rangendo). Narração, legenda e trilha são pós-produção.
5. **3 a 4 cortes por bloco de 30 s. Nunca mais de 4.** Oito cortes geraram câmera lenta.
6. **Estilo em duas camadas:** criatura no padrão **ultra-realista** atual; humanos, ambientes e
   objetos no padrão **naturalista** com contenção. As âncoras exatas estão em
   `references/estilo-e-contencao.md`, e em nenhum outro lugar.
7. **Crédito só com OK do Samuel.** Gerar vídeo custa 75 créditos por bloco. Se o modelo não
   consegue atender o pedido (duração, efeito), avisar e perguntar **antes**, nunca substituir em
   silêncio.
8. **Aviso de destino no topo de todo prompt** (decisão do Samuel, 2026-10-06). Prompt de imagem
   (componente ou referência): *"PROMPT DE IMAGEM DE REFERÊNCIA — gerar no ChatGPT, com a geração de
   imagem nativa do GPT; NÃO usar o MCP do Higgsfield"*. Prompt de cena: *"PROMPT DE CENA (VÍDEO) —
   Higgsfield Cinema Studio 4.0, modo Video; não vai para o GPT"*. E todo arquivo diz **de que pasta
   sobem as imagens e onde salvar o que for gerado**, em caminho completo.
9. **Personagens de frente como prioridade** (Samuel, 2026-10-09). Em referências e vídeos,
   priorizar enquadramentos frontais ou em três quartos, com rosto e reação legíveis. Plano de
   costas é exceção com motivo narrativo declarado, não a composição padrão. Mostrar o rosto
   não significa olhar para a câmera: olhos, cabeça e corpo devem orientar a atenção para o alvo
   da cena. Aplicação e exceções em `references/direcao.md`, seção “Prioridade frontal e direção
   do olhar”.
10. **Geometria difícil** (escala, várias pessoas, perseguição) pode pedir um blockout no Blender.
   Abrir o Blender tem **dois portões de aprovação**: ver `D:\Agentes\_registros\BLENDER.md` §0.

---

## ⛔ PORTÃO DE ENTREGA — conferir TODA VEZ, antes de entregar qualquer prompt

Nenhum arquivo de prompt sai desta skill sem passar por esta lista. Item falhou: corrigir antes de
entregar, nunca entregar com ressalva. (Criado em 2026-10-06, depois de um `cena.txt` chegar sozinho
à extensão, sem ordem nem aviso de que as imagens vinham antes, no GPT.)

1. **Etapa certa?** A etapa anterior está aprovada pelo Samuel? (cena sem referências aprovadas não
   se entrega como pronta para gerar.)
2. **`EXECUTAR.md` do bloco escrito ou atualizado, e o pacote do passo montado?** O `EXECUTAR.md` é o
   mapa para o Samuel e o Claude Code. **A extensão não lê o disco:** ela recebe só a pasta
   `_pacote_passoN` (gerada por `scripts/montar_pacote.py`), arrastada pelo Samuel para o chat dela. O
   `EXECUTAR.md`
   lista os passos em ordem (imagens no GPT → aprovação → Elements → vídeo), cada um com arquivo,
   destino e ponto de parada.
3. **Aviso de destino no topo** de cada arquivo e de cada item: imagem = *ChatGPT, imagem nativa do
   GPT, NÃO o MCP do Higgsfield*; cena = *Cinema Studio 4.0, modo Video, não vai para o GPT*.
4. **"Passo N de M"** no topo de cada arquivo, e o `cena` diz em destaque que **não é o primeiro
   passo** e o que precisa existir antes, com a ordem de parar se não existir.
5. **Caminhos completos**: de onde sobem os anexos, onde salvar cada imagem, onde salvar o vídeo.
6. **Elements**: todo `@` usado existe no `registro.json`; os novos estão marcados para cadastro no
   `EXECUTAR.md`.
7. **Densidade** (`etapa-4-cena.md` §3, itens 13 e 14): cada beat cabe no tempo dele e nenhuma
   instrução anula outra.
8. **Na mensagem ao Samuel**, dizer explicitamente qual pasta arrastar para a extensão
   (*"arraste todos os arquivos de `…\_pacote_passo1\`"*) e que, quando ela terminar, ele me diga
   "pronto" para eu rodar `receber_pacote.py`. Protocolo completo: `references/extensao-navegador.md`.

**Esta lista é cobrada por código.** `scripts/validar_bloco.py` roda como hook do Claude Code
(`C:\Ai-Project\Omega\.claude\settings.json`): reprova o arquivo de produção no instante em que ele é
salvo e injeta esta lista quando o Samuel fala de bloco, cena, referência ou prompt. Reprovação do
hook = corrigir antes de responder. Nunca contornar o hook escrevendo o arquivo por script.

---

## PASTAS E NOMES — o contrato com a extensão

Tudo de uma criatura vive em `C:\Ai-Project\Criaturas\<Nome>\`:

```
<Nome>\
  <nome>-video\notes\        ← do Omega: dossie.md, roteiro.md (não mexer na estrutura)
  componentes\
    componentes.md           ← Etapa 2: lista + prompt de cada componente
    registro.json            ← arquivo ↔ label do Element ↔ tipo ↔ estilo ↔ status
    cri_<slug>.png           ← criatura
    per_<slug>.png           ← personagem humano
    amb_<slug>.png           ← ambiente (frente)   ·  amb_<slug>_reverso.png (contracampo)
    obj_<slug>.png           ← objeto de continuidade
  blocos\
    bloco-01\
      EXECUTAR.md            ← o mapa do bloco (Samuel e Claude Code): os passos em ordem
      _pacote_passo1\        ← o que vai para a extensão: PACOTE.md autocontido + anexos (montar_pacote.py)
      _pacote_passo4\        ← idem, para o vídeo
      referencias.md         ← Etapa 3: componentes do bloco + prompts das imagens de referência
      ref_01_<slug>.png      ← o número é o @Image do upload, na mesma ordem
      ref_02_<slug>.png
      cena.md                ← Etapa 4: settings + upload + Elements + prompt
      takes\                 ← take-1.mp4, take-2.mp4…, ultimo-quadro.png do aprovado
```

**Uma regra cobre os nomes: o nome do arquivo sem `.png` É o label do Element.** `per_johansen.png`
vira o Element `@per_johansen`. Slug em minúsculas, sem acento, hífen entre palavras
(`obj_chapeu-collins`). O prefixo também decide o estilo: `cri_` usa a âncora ultra-realista e os
demais a naturalista. Detalhe e formato do `registro.json` em `references/etapa-2-componentes.md`.

---

## ONDE ESTÁ CADA COISA — ler o arquivo da etapa antes de escrever

| Etapa / tarefa | Ler |
|---|---|
| 2 — componentes, model sheets, Elements | `references/etapa-2-componentes.md` + `references/estilo-e-contencao.md` |
| 3 — referências do bloco | `references/etapa-3-referencias.md` + `references/estilo-e-contencao.md` |
| 4 — prompt de cena | `references/etapa-4-cena.md` (o formato **definitivo**) + `references/direcao.md` |
| 4 — como prompts excelentes de outros filmes escrevem | `references/exemplos-externos.md` (Cane Men e Detour, comentados — método, não modelo de duração) |
| 4 — vocabulário de câmera e emoção | `references/bibliotecas-camera-emocao.md` (§4 é a tabela mestra) |
| 4 — bloco de ação (luta, multidão, perseguição) | `references/direcao-bloco-acao.md` |
| 4 — presets do Cinema Studio | `references/higgsfield-presets.md` (+ `higgsfield-presets-exemplo-cthulhu.md`) |
| 2/3/5 — o que a extensão faz e como | `references/extensao-navegador.md` |
| 5 — julgar o take e o que fazer quando falha | `references/rubrica-aceitacao-take.md` |
| comportamento observado do modelo | `references/receituario.md` |
| custo, orçamento, limites da plataforma | `references/plataforma-e-custo.md` + `scripts/orcamento.py` |
| 6 — pós-produção | `references/pos-producao.md`, `narracao-elevenlabs-v3.md`, `musicalidade.md`, `conversao-midia.md` |
| padrões profissionais de montagem e dramaturgia | `references/vendor-visual-skills/` (MIT) |

---

## ETAPA 6 — PÓS-PRODUÇÃO, em uma linha cada

1. Os 20 takes aprovados são montados no **Studio** (editor próprio, `Omega\studio`).
2. Com a montagem travada, gera-se a **legenda-base**: um rascunho do texto da narração encaixado
   cena a cena na duração real, para saber exatamente onde cada frase cabe.
3. A legenda-base aprovada vira a **narração no ElevenLabs v3** (`narracao-elevenlabs-v3.md`).
4. **Trilha** (Biblioteca do YouTube primeiro, Suno como complemento) e mixagem
   (`pos-producao.md`, `musicalidade.md`).
5. Cortes para Shorts e conversões com ffmpeg: `conversao-midia.md`.

A narração conta a lore e não descreve a ação da tela. Essa regra mora em `pos-producao.md`.

---

## REGRAS DO CANAL (valem para qualquer vertente)

- **Mitologia/folclore:** só criaturas de domínio público. **Anime/mangá e HQ:** IP protegido é
  escolha consciente do Samuel; não bloquear nem repetir aviso.
- **Gore:** implicar, nunca mostrar. Violência no tom, ausente nos detalhes gráficos.
- **Música:** nunca de terceiros sem licença (fonte e licenças em `pos-producao.md`).
