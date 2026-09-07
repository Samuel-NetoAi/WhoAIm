# Model Sheet + Storyboard — padrão ultra-realista (Documento 2)

Regra de ouro extraída dos exemplos aprovados pelo usuário (jul/2026): a ESTRUTURA vem dos
formatos de model sheet e storyboard profissionais; o ACABAMENTO vem de fotografia cinematográfica
real. Nunca importar o acabamento ilustrado/pintado/3D dos formatos de referência — o canal é
photoreal "vida real".

## FORMATO UNIVERSAL — TÍTULO + PRÉVIA PT-BR (decisão jul/2026, obrigatório em TODO prompt)

Todo prompt entregue por esta skill — model sheet (2a), storyboard (2b) ou Seedance (Documento 3)
— abre com duas linhas em PORTUGUÊS, ANTES do prompt em inglês, que NÃO fazem parte do texto a
colar na ferramenta:

```
TÍTULO: [nome curto da cena/bloco/personagem]
PRÉVIA (PT-BR — não copiar; não entra no prompt): [1–2 frases explicando ao usuário o que é essa
cena/bloco, o que ele combinou que aconteceria aqui — um resumo de orientação, não o prompt
traduzido]

[a partir daqui, o prompt em inglês, sem nenhuma linha em português misturada]
```

A prévia é para o usuário se situar antes de ler/colar um bloco de inglês denso — não é tradução
do prompt, é lembrete do que foi combinado para aquela cena. O prompt em si permanece 100% em
inglês, íntegro, sem português infiltrado.

## ÂNCORA DE REALISMO — bloco obrigatório em TODO prompt de imagem

Um adjetivo "photorealistic" não segura criatura mitológica: o assunto puxa o gerador para
concept art. Colar este bloco (adaptando lente/luz à cena) no FINAL de todo prompt do Documento 2:

```
RAW photo, ultra-realistic, real-life. Shot on cinema camera, 35mm lens [ou 85mm para retrato],
shallow depth of field. Natural skin texture with pores, subsurface scattering, fine hair detail,
realistic fabric and material wear, physically accurate lighting and shadows, film grain.
Absolutely NO illustration, NO painting, NO concept art, NO anime, NO 3D render, NO cartoon,
NO stylized art. It must look like a photograph of something real.
```

Para a criatura: tratar como criatura FÍSICA fotografada — próteses/animatrônico de cinema de
altíssimo orçamento, pele/escama/textura com imperfeição real — nunca "fantasy art".

## ⚠️ EXCLUSÃO DE FOLHA — a regra que faltava, e nós estávamos errados (set/2026)

> **Toda vez que uma FOLHA entra como referência num prompt de vídeo, o prompt precisa declarar o
> que NÃO deve ser lido dela.** Sem isso, o gerador trata a folha como imagem da cena.

**Por que estávamos errados:** montamos as folhas como material de estúdio — fundo neutro escuro,
**rótulos de seção em tipografia**, **tira de paleta**, layout em grade. Depois passamos essa
imagem como *"strict character reference"* e **não dissemos nada sobre o resto da imagem.** O
gerador não sabe que o fundo é um artifício de produção: para ele é o cenário, e a tipografia é
texto que existe no mundo.

🟡 A skill da comunidade nomeia isso para a folha de personagem (*"Character sheets require
exclusions — 'Do not take the gray backdrop'"*). **No nosso caso é pior**, porque as nossas folhas
carregam três coisas vazáveis, não uma.

**Bloco obrigatório em TODO prompt de vídeo que use uma folha como referência:**

```
Use IMAGE [n] for [o que exatamente — ex.: his identity].
Do not recast. Do not beautify. Do not use as an image background.
Do NOT take from IMAGE [n]: the studio backdrop, the sheet layout or grid, any section
labels or typography, the palette strip, the multi-view arrangement.
Take ONLY: [face and proportions / costume and materials / the location's materials and
architecture] — place it in the scene described below.
```

> 🎥 **Terceira fonte independente confirma a regra, e ela deu duas exclusões que faltavam.**
> No vídeo *"master AI realism"* (2026-09), o autor escreve literalmente, ao passar a folha:
> *"Image one is used for his identity (…) **do not recast, do not beautify, do not use as an
> image background**."*
>
> - **`do not recast`** — impede o modelo de trocar a pessoa por outra parecida. É o defeito de
>   consistência mais caro que existe, e não tínhamos frase para ele.
> - **`do not beautify`** — impede o embelezamento automático. Casa exatamente com o motor
>   anti-IA da skill do fabricante: **realismo é imperfeição**, e o modelo puxa para o oposto.
> - `do not use as an image background` — é a nossa exclusão de fundo, com outras palavras.
>
> Agora são **três fontes independentes** dizendo a mesma coisa (fabricante 🎓, comunidade 🟡,
> vídeo 🎥). A regra sai de "adotar com teste" para **regra**.

**Ler junto:** o que se toma vem primeiro, o que não se toma vem logo depois. 🎓 A regra da §7.4b do
`REGRAS-PRODUCAO-VIDEO.md` continua valendo — **exclusão amarrada a uma referência funciona**
(é escopo de leitura do material), e é diferente de negar um estilo em prosa, que não funciona.

**Sintomas de que a exclusão faltou:** fundo da cena vira estúdio liso · aparece texto/legenda
inexplicável no quadro · o personagem aparece duplicado ou em várias vistas · a paleta aparece como
faixa de cor no canto · o quadro fica com "cara de catálogo".

⚫ **A solução estrutural está na folha simplificada abaixo:** o que entra no prompt de vídeo passa
a ser o **starting frame** (imagem já de cena), não a folha. Sem layout, não há layout para vazar.

---

## MODEL SHEET (bíblia de personagem) — um por personagem recorrente

Gerado ANTES do primeiro bloco (checkpoint). É a referência de consistência que acompanha todos
os prompts seguintes ("use IMAGE 1 as strict character reference"). Não é start frame do Seedance,
então rótulos curtos de seção são permitidos aqui.

### ⚫ FOLHA SIMPLIFICADA — decisão do Samuel, 2026-09-02. Substitui a folha elaborada.

> **A folha elaborada morreu.** Ela tinha 3 painéis principais + turnaround de 5 vistas + coluna de
> 4 expressões + 2 macros + tira de paleta + rótulos tipográficos — **seis coisas para vazar para
> dentro da cena**, e era justamente ela a origem do problema descrito acima.

**Por que estávamos errados:** confundimos **folha de animação** com **referência de IA**. Numa
produção de animação, o model sheet existe para um humano desenhar o personagem de qualquer ângulo
— por isso o turnaround, por isso as expressões. O gerador de vídeo **não precisa disso**: ele
precisa de identidade travada e de um bom close do rosto. Todo o resto era layout que ele lia como
cenário.

🎥 *"we have a good close-up of his face"* — é o que o autor destaca como o que importa na folha.

**O fluxo agora tem três etapas, e a terceira é nova:**

```
1. IMAGEM DE PERSONAGEM   → um retrato cinematográfico, prompt curto, com imperfeições
2. FOLHA                  → gerada a partir dela, simples, 2K, 16:9, bom close de rosto
3. STARTING FRAME         → folha + retrato como referência, já na cena e com a lente declarada
                            ↳ É ESTE que entra no Seedance, não a folha
```

**Etapa 1 — imagem de personagem** (prompt curto; a imperfeição é a especificação):

```
TÍTULO: Personagem — [NOME]
PRÉVIA (PT-BR — não copiar): retrato base de [personagem]; origem da folha.

"[uma frase de identidade: idade aparente, papel, porte, roupa]. [IMPERFEIÇÕES NOMEADAS —
olheiras, rugas, assimetria, entrada de cabelo, pele não uniforme, cicatriz, dente torto:
pelo menos três]. Not fully sharp. [ÂNCORA DE REALISMO]"
```

> **Nunca escrever idade em número nem em palavra** — papel, porte, roupa e ação
> (`direcao-cinematografica.md`). E **imperfeição é campo obrigatório**, não tempero: é o que tira
> o rosto do vale da estranheza (`atuacao-dialogo-som.md` §1).

**Etapa 2 — a folha, simples:**

```
TÍTULO: Folha — [NOME]
PRÉVIA (PT-BR — não copiar): referência de consistência de [personagem].

"Character reference sheet of the SAME original character as the reference image.
Full body standing view, plus a large clear close-up of the face.
Plain neutral background. No section labels, no palette strip, no typography.
CHARACTER SPECIFICS: [descrição FECHADA — pele/textura, olhos, cabelo, vestes com material e
desgaste, cicatrizes, proporções, altura relativa. Contrato de consistência: fixa aqui, nunca
se redescreve nos blocos.]
[ÂNCORA DE REALISMO]"
```
Gerar em **2K, 16:9**.

> ⚠️ **Tirar da folha todo adorno pequeno e destacado** (chapéu miúdo, brinco, fivela) — ver a
> seção "DETALHE PEQUENO NA FOLHA" no fim deste arquivo. Ou o detalhe é grande e definidor, ou sai.

**Etapa 3 — o starting frame, que é o que realmente entra no vídeo:**

Passa-se **a folha E o retrato** como referências, e escreve-se:

```
Image one is used for [NOME]'s identity. [detalhes do que ele é].
Do not recast. Do not beautify. Do not use as an image background.
[o que se quer ver no primeiro quadro — o personagem já na cena, na pose e no lugar]
Shot on a 35mm lens, aperture f/1.8, shallow depth of field, visible fine film grain,
muted desaturated color grade.
```

🎥 *"this is what's needed to have the baseline for your videos. **Don't underestimate your images,
because this is the part where you could save so much time and credits.** If your starting frame
doesn't look cinematic, you can still achieve cinematic realistic videos, but it's going to be a
little bit harder."*

> **A folha deixa de ser a imagem que entra no prompt de vídeo.** Ela é o contrato de consistência;
> **o starting frame é a referência de produção.** Isso resolve por construção o vazamento de
> layout descrito no topo deste arquivo — o que entra no Seedance já é uma imagem de cena.

Regras:
- A aparência da criatura/personagem se descreve NO MODEL SHEET, exaustivamente, e em nenhum outro
  lugar (os storyboards e o prompt de vídeo referenciam a imagem, não redescrevem — redescrição gera deriva).
- Um model sheet por personagem recorrente; humanos de papel único não precisam.
- Gerar o model sheet, obter aprovação do usuário, e SÓ ENTÃO produzir storyboards.
- **Depois de aprovado, registrar como ELEMENT no Higgsfield** (`show_reference_elements`
  action=create) e passar a citá-lo por placeholder `<<<element_id>>>` nos prompts, em vez de
  "use IMAGE 1 as strict character reference". O texto continua válido como fallback — para geração
  na web, ou se o modelo escolhido não aceitar Element (ver `higgsfield-cinema-studio.md`, seção 5).
  Motivo: a frase de texto depende de o usuário anexar a imagem certa na ordem certa em cada geração;
  o Element é a mesma promessa sem o passo manual que falha.

## 🎓 O QUE A SKILL OFICIAL DO HIGGSFIELD ACRESCENTA (lida via MCP em 2026-09-02)

O fabricante publica uma skill `character-sheet` no próprio MCP. Ela **não substitui** o nosso model
sheet — a arquitetura bate. Mas traz cinco coisas que não tínhamos, e todas são de graça:

**1. O motor anti-IA — é o truque central deles, e o nosso ponto mais fraco.**
🎓 *"Photorealism means anti-retouch, never idealized. 'Realistic' is never a synonym for flawless."*
Bloco literal a colar no prompt de personagem fotorrealista:

> `visible fine skin texture with natural pores, fine lines, subtle asymmetries and texture
> irregularities, natural visible makeup with slightly uneven blending rather than flawless
> coverage, slight natural sheen rather than glossy or dewy retouched finish, no digital smoothing,
> no beauty filter, no AI-airbrushed look, skin completely free of artificial glare, shine or
> highlight blooms, matte-to-natural complexion`

Mais **âncoras de imperfeição** nomeadas: *"a few faint freckles, a small mole near the collarbone"*.

**2. A cláusula anti-brilho no olho** — defeito recorrente que não tínhamos nomeado:
> `naturally muted catchlights, no oversized specular glare in the iris, eye color muted rather
> than glowing`

**3. Estrutura facial adulta declarada.** 🎓 *"actively avoid babyface / youthful rounded
proportions"* — mandíbula e maçãs **definidas**, terços faciais longos, proporção adulta. E na
negativa: `no babyface, no overly youthful rounded proportions`. Para Teseu e para tripulação
adulta isto importa: o default do modelo puxa para o rosto jovem arredondado.

**4. A negativa que impede a folha de duplicar figura** — o que mais quebra folha, segundo eles:
> `single subject only, exactly one person, only the character in frame, no other people, no
> duplicate figures, no mannequin, no reflections, no props, no furniture, no background objects,
> empty seamless studio`

**5. A ordem dos slots** (o modelo pesa mais o começo): composição → *identical original character
on all views* → fundo → identidade → rosto → olhos → sobrancelha → cabelo → **módulo de realismo** →
corpo → figurino da cabeça aos pés → luz → cauda de qualidade → **negativa**.

> ⚠️ **Onde divergimos, e é decisão nossa:** a composição padrão deles é **split-screen** (corpo
> inteiro à esquerda + close à direita). A nossa é de **três painéis** (frente, costas, close), e ela
> serve melhor ao canal porque o Seedance precisa das costas para não chutar o fundo. **Mantemos os
> três painéis**; o `turnaround` deles (frente · 3/4 · perfil · costas) é a variante mais próxima e
> está disponível se um personagem precisar de mais ângulos.
>
> ⚫ **Nota de fluxo (set/2026):** o Samuel gera as imagens **fora do Higgsfield** (GPT Plus, Nano
> Banana Pro). A skill entrega o **prompt pronto para colar**, nunca gera a imagem. Como imagem
> deixou de custar crédito, **iterar a folha até acertar é de graça** — não aceitar folha mediana.

---

## AMBIENTE DE REFERÊNCIA (Environment Sheet) — decisão jul/2026, mesmo princípio do Model Sheet

Buraco identificado: cenário e luz eram redescritos do zero em CADA painel — mesma armadilha que o
Model Sheet resolveu para personagem, nunca aplicada ao lugar. Se dois ou mais blocos do vídeo
acontecem no MESMO ambiente (o santuário, o cais, a floresta), redescrever gera deriva visual
(pedra muda de cor, luz muda de direção, sem ninguém perceber até comparar os blocos lado a lado).

**Quando gerar:** só para ambiente RECORRENTE (2+ blocos no mesmo lugar) — mesmo critério do Model
Sheet ("um por personagem recorrente"). Ambiente de uso único não precisa; descrever direto no
painel, como já se fazia.

**CLEAN PLATE — melhoria ago/2026, absorvida de guia externo do Cinema Studio.** Além da folha de
referência descrita abaixo, gerar também o **cenário VAZIO**, com `no people` explícito no prompt, e
registrá-lo como Element. A diferença importa: a folha de referência *descreve* o lugar; o clean
plate **É** o lugar, e pode ser usado direto como start frame, como base de composição, ou para
inserir personagem depois mantendo a geografia exata. É prática de set real (placa limpa), não jargão.
Custa 1–2 créditos e resolve o buraco de "os blocos acontecem no mesmo salão, mas a pedra mudou de
cor entre eles". Gerar com `count: 4` — não custa mais — e escolher o melhor.

**Estrutura do prompt** (uma imagem, layout de folha de referência), gerado na Fase 1 junto dos
model sheets, mesmo lote:

```
TÍTULO: Environment Sheet — [NOME DO AMBIENTE]
PRÉVIA (PT-BR — não copiar): referência de cenário/luz para todos os blocos que acontecem em
[nome do ambiente].

"Ultra-realistic environment reference sheet for '[NOME DO AMBIENTE]', [uma frase de identidade
do lugar]. Layout on organized as a professional set-design reference:
— WIDE establishing view of the full location;
— DETAIL strip: 3-4 close-ups of key materials/textures/props that define the place (the stone,
  the wood grain, a defining object);
— TOP-DOWN or side floor plan, marking key camera positions/angles already used or planned for
  this location (labeled simply, e.g. '1 — wide establishing', '2 — close on the altar');
— PALETTE strip: the location's color palette;
— section labels in small clean typography.
LOCATION SPECIFICS: [descrição minuciosa e FECHADA — material predominante, época/desgaste, fonte
de luz natural do lugar (não da cena — a luz que MORA ali), clima/atmosfera padrão, escala. Este é
o contrato de consistência de ambiente: fixa aqui, nunca se redescreve nos storyboards.]
[ÂNCORA DE REALISMO]"
```

### ⚠️ ÂNGULO REVERSO DO AMBIENTE — obrigatório quando há contracampo (set/2026)

> **Uma vista só do ambiente não basta. Cena com contracampo exige os DOIS lados da sala.**

🎓 *"If you're doing a dialogue scene with reverse angles, you must generate reverse angle
environment references of the same room. Feed the model images of what both sides of the room look
like. That gives the model a blueprint of the room and **the background stops jumping between
cuts**."* · E na cena de ação: 🎓 *"We explicitly built two distinct angles. A front view with a
single crimson tree and a completely empty back view. **Locking in both sides matters for action
scenes. The AI stops guessing what's behind the character and the batches stop drifting.**"*

**Por que estávamos errados:** o Environment Sheet acima tem WIDE + DETAIL + planta baixa. Tudo
olhando **para o mesmo lado**. Quando o bloco corta para o contracampo, o modelo **inventa** o que
está atrás do personagem — e inventa diferente a cada geração. É por isso que o fundo "pula" entre
cortes do mesmo bloco, e nós vínhamos culpando o prompt.

**O que acrescentar ao Environment Sheet:**

```
— REVERSE view: the same location seen from the opposite side, as if the camera turned 180°,
  showing what stands BEHIND the first camera position (labeled 'reverse — what the first
  camera has at its back').
```

Ou, mais barato e mais confiável: **duas imagens irmãs** — `Environment Sheet — [LUGAR] (A)` e
`(B — reverso)` — e as duas entram em REFERÊNCIAS DESTE BLOCO. ⚫ Imagem não custa crédito
(set/2026), então **gerar as duas é o padrão**, não o luxo.

**Quando é obrigatório:** qualquer bloco com contracampo (diálogo, confronto) e **todo bloco de
ação** — ver `direcao-bloco-acao.md` §2.3.

Regras (espelham o Model Sheet):
- O ambiente se descreve NO ENVIRONMENT SHEET, exaustivamente, e em nenhum outro lugar — os
  storyboards passam a referenciar a imagem ("use IMAGE N as strict environment reference"), sem
  redescrever material/cor/luz de base do lugar. O painel ainda declara a AÇÃO e o momento
  específico (hora do dia, clima daquele bloco) por cima da referência, não o ambiente inteiro.
- Entra em REFERÊNCIAS DESTE BLOCO junto com o(s) model sheet(s) de personagem, quando aplicável.
- Não é obrigatório — só quando o ambiente se repete. Vídeo com cenários todos diferentes (um por
  bloco) não precisa disso.

## MOOD/STYLE SHEET — referência única de luz/paleta/lente para o vídeo inteiro (decisão jul/2026)

Buraco identificado: a consistência de luz/paleta/lente hoje só existe em REGRA DE TEXTO (âncora
de realismo, tabela de lente, "manter paleta consistente entre storyboards") — nunca como imagem
de ancoragem visual que o gerador possa referenciar diretamente. Condicionamento visual costuma
ser mais forte que descrição textual para casar estilo entre gerações.

**Quando gerar:** opcional, recomendado para vídeos onde consistência tonal é crítica (a maioria).
Uma vez por vídeo — não por bloco, não por personagem — na Fase 1, junto do resto do checkpoint.

**Estrutura do prompt** (uma imagem, mood board):

```
TÍTULO: Mood/Style Sheet — [NOME DO VÍDEO/CRIATURA]
PRÉVIA (PT-BR — não copiar): referência única de luz, paleta e lente para todo o vídeo; todo
storyboard e frame de referência aponta de volta para esta imagem.

"Ultra-realistic cinematography mood board for '[TÍTULO DO VÍDEO]'. Grid of 4-6 representative
stills capturing the film's visual identity: lighting quality and direction, color grading,
atmosphere, film grain — NOT specific characters or plot moments, just tone and texture.
PALETTE strip below. MOOD KEYWORDS in small typography: [3-5 palavras — ex.: 'somber, ancient,
damp, firelit, dread']. LENS/STYLE NOTE: [lente predominante e por quê — usar a tabela
lente-como-psicologia de direcao-cinematografica.md; ex.: '85mm compression for claustrophobic
intimacy throughout'].
[ÂNCORA DE REALISMO]"
```

Regras:
- Gerado ANTES dos storyboards, junto do checkpoint da Fase 1 — o usuário aprova junto com os
  model sheets.
- Todo prompt de storyboard/frame de referência subsequente pode citar "match the lighting and
  color grading of IMAGE N (Mood Sheet)", além da referência de personagem/ambiente.
- Não substitui a âncora de realismo nem a lógica de luz por sequência (continuam obrigatórias em
  cada prompt) — é reforço visual, não substituto da regra de texto.

## STORYBOARD por bloco — painéis limpos, ficha rica

Estrutura em duas partes INSEPARÁVEIS:

**Parte A — o prompt do storyboard (gera a imagem que vira start frame).** TÍTULO + PRÉVIA
PT-BR obrigatórios antes do prompt:

```
TÍTULO: Bloco [N] — [nome do bloco]
PRÉVIA (PT-BR — não copiar): [1–2 frases do que acontece nesta cena, o que foi combinado]

"Cinematic storyboard titled '[NOME DO BLOCO]'. Arranged in a STRICT [C]x[R] grid of [N] equal-sized
16:9 panels, separated by thick solid black gutters. Each panel is a fully self-contained composition
with its own complete background — like [N] separate photographs placed on a black board.
Use IMAGE 1 as strict character reference for [personagem] — same face, same body, same wardrobe.
Panel 1 — [TIPO DE SHOT]: [descrição narrativa rica do momento — UM sujeito, UMA ação; ambiente,
  atmosfera, hora do dia, clima, profundidade]
Panel 2 — [TIPO DE SHOT]: [...]
STRICT PANEL SEPARATION: no element, character, background or lighting may cross, touch or overlap
a gutter; no collage style; no panoramic background flowing across panels.
No text on the panels. No captions. No timestamps. No panel numbers rendered inside the frames.
Consistent lighting logic and color grading across all panels: [descrever a luz da sequência].
[ÂNCORA DE REALISMO]"
```

**GEOMETRIA DO GRID — regras duras (causa raiz do sangramento entre painéis):**
- Declarar SEMPRE o layout explícito (6 painéis = 3x2; 8 = 4x2; 9 = 3x3; 10 = 5x2; **12 = 4x3;
  15 = 5x3**). Nunca deixar o gerador decidir a disposição — ambiguidade de geometria é o que produz
  colagem com fundo escorrendo.
- Aritmética de resolução: o storyboard é UMA imagem; cada painel é pequeno SEMPRE — logo composição
  simples e legível por painel é LEI, não recomendação (um sujeito, uma ação, sem fundo carregado).
  Intermediários do mesmo shot ajudam aqui: repetir o enquadramento reduz o que o gerador precisa
  acertar em cada painel pequeno.
- **BLOCO DE 30s = FOLHA DE 12–15 PAINÉIS (decisão do usuário, ago/2026).** É o ponto de maior risco
  técnico do novo fluxo: num 5x3 cada painel tem ~40% da área que tinha num 3x2, e "painel pequeno
  alucina" é a causa raiz nº 1 já registrada em produção. Por isso, no bloco de 30s:
  - **painel crítico sai avulso em resolução cheia POR PADRÃO** (rosto, revelação, insert que decide
    o bloco) — não "pode sair", sai. Imagem custa 1–2 créditos no Higgsfield; a economia que
    justificava enfiar tudo na folha deixou de existir.
  - a auditoria de composição simples passa a ser explícita: conferir os 12–15 painéis um por um antes
    de aprovar a folha, não bater o olho no conjunto.
  - **tripwire de reversão:** simplificar composições → painel crítico avulso → **quebrar em duas
    folhas de 8** → só então rediscutir a densidade. Registrar o que aconteceu no receituário.
  - a alternativa recusada (duas folhas de 8–10 por bloco de 30s) fica registrada aqui como o
    primeiro degrau da reversão, não como ideia descartada.
- Verificação antes de aprovar a folha: algum elemento tocando/atravessando calha? Fundos de painéis
  vizinhos se emendando? Painéis de tamanhos desiguais? → regenerar a folha (ou o painel isolado);
  NÃO enviar folha sangrada ao Seedance "para ver se cola".

**Parte B — a ficha do bloco (anotação para o usuário e para o Documento 3; NUNCA vai na imagem):**
Para cada painel, linha terse de specs seguida da ação (formato mais escaneável, decisão jul/2026):
`[lente]mm | [duração]s | [movimento] | [tipo de shot]` — depois `AÇÃO: [uma frase]` —
`SFX/ATMOSFERA: [sons e clima]`. Ex.: `85mm | 3s | PUSH-IN | CLOSE-UP — AÇÃO: ele alcança a mesa,
os olhos travam em algo entre as evidências — SFX: papel remexendo, relógio distante`. Lente vem
da tabela lente-como-psicologia (direcao-cinematografica.md); movimento vem do fraseado Seedance
da mesma referência. Esta ficha alimenta o [AUDIO] e os [SHOT] do prompt Seedance.

**Vocabulário de shots (variar entre painéis — nunca repetir o mesmo enquadramento em painéis
consecutivos):** extreme close-up (detalhe: olho, mão, objeto) · close-up · medium shot ·
wide/establishing · top-down/overhead · low angle · high angle · over-the-shoulder ·
dutch/canted angle · silhouette contra luz · foreground focus (objeto em primeiro plano) ·
tracking implícito (sujeito em movimento com fundo varrido).

Regras que permanecem invioláveis (testadas em produção):
- NENHUM texto renderizado nos painéis — legendas/timestamps confundem o Seedance.
- Um sujeito, uma ação por painel (densidade = alucinação).
- Nº de painéis vem da heurística de ritmo do SKILL.md, nunca fixo.
- 1º painel = estado inicial do bloco.

## PAINÉIS SÃO KEYFRAMES TEMPORAIS, não "melhores momentos" (causa raiz do vídeo estático e do início perdido)

O vício natural do gerador: pedido "o padre destrói o santuário", ele renderiza o clímax do verbo
(madeira caindo, poeira) em TODOS os painéis — porque essa é a imagem mais representativa da ação.
Resultado: painéis que mostram o mesmo estado ≈ nada para o Seedance animar entre eles ≈ vídeo
estático; e painel 1 no meio da ação ≈ o começo da cena não existe em nenhuma referência.

**Método de composição da folha (DECISÃO DE PRODUÇÃO jul/2026 — piso 6, teto 10 painéis):**
1. Listar os ESTADOS do arco do bloco — `ANTES → primeiro contato → PICO → consequência`
   (nem todo bloco tem os quatro). Esses são os KEYFRAMES.
2. Agrupar os keyframes em 2–4 SHOTS (as mesmas fronteiras dos [SHOT] do Documento 3).
3. Preencher cada shot com INTERMEDIÁRIOS até somar 6–10 painéis: painéis do MESMO
   enquadramento/ângulo do shot, com a ação avançada entre um e outro — como frames consecutivos
   de um filme. O ângulo SÓ muda na fronteira de shot; 6–10 ângulos diferentes = picote, PROIBIDO.
   **DELTA ENTRE INTERMEDIÁRIOS (caso Sobek, jul/2026):** o gerador não resolve micro-mudança
   fisiológica (pupila, respiração, tensão de músculo) em fotos estáticas — pares saem
   quase-duplicatas mesmo com o prompt declarando a diferença. O delta precisa ser BINÁRIO
   (presença/ausência clara: pálpebra aberta vs fechada, não "pupila contrai") ou AMBIENTAL (algo
   entra/sai de quadro, sombra muda, água ondula) — nunca só o corpo fazendo um micro-movimento.
   Micro-movimento fisiológico só vale como delta em ECU quando ELE PRÓPRIO é o assunto do painel
   (mandíbula abrindo = estrutural, não sutil). Detalhe no seedance-receituario.md.
4. Cada painel recebe no prompt o rótulo `Shot A – frame 1/3` etc., e a instrução global:
   "Panels within the same shot keep the EXACT same camera angle and framing — only the action
   advances between them, like consecutive film frames."
Motivo empírico: o Seedance não preenche o entre-cenas de folhas esparsas (3 painéis saíram
quase estáticos em produção); a progressão densa dá a ele o caminho do movimento.

**REGRA DURA DO PAINEL 1 — pré-ação:**
- O painel 1 mostra o instante IMEDIATAMENTE ANTERIOR ao verbo começar. É PROIBIDO usar o verbo
  da ação (ou gerúndio dele) na descrição do painel 1 — gerador renderiza verbo como ação em curso.
- Descrever o tableau parado e declarar o que AINDA NÃO aconteceu. Frases-modelo para o prompt:
  "the very instant BEFORE the action begins", "the shrine is still fully intact and untouched",
  "his hands have not yet reached the wood", "everything is still — the moment before".
- Exemplo (padre): painel 1 = padre parado diante do santuário INTACTO, mãos ao lado do corpo,
  medindo-o com o olhar. Painel 2 = mãos agarram a madeira (primeiro contato). Painel 3 = a
  estrutura tomba, poeira (pico). Painel 4 = destroços assentados, ele ofegante (consequência).

**Último painel = estado FINAL do bloco** (a consequência visível), nunca o pico. O pico fica nos
painéis do meio. Assim o Seedance recebe começo e fim reais para interpolar.

**GEOMETRIA DE RELAÇÃO ENTRE SUJEITOS — "encara X" não funciona (caso Besta, jul/2026):**
Dois sujeitos no mesmo painel sem eixo de relação declarado = viés de retrato: o gerador os
compõe lado a lado, ambos de frente para a câmera, como companheiros — mesmo quando a cena é um
confronto. E cuidado com "de frente": em prompt vira "facing front" = de frente para a CÂMERA,
não um para o outro. Regras:
- Painel com 2+ sujeitos DEVE declarar, para cada um: posição no quadro (frame-left/right/center),
  direção do olhar/corpo, e a distância entre eles.
- A exceção à regra "um sujeito, uma ação" é exatamente esta: painel de relação tem 2 sujeitos e
  UMA relação — e a relação é a ação do painel; declarar a geometria é o que a torna legível.
- Manter a coerência com o eixo de 180° e a direção de tela (direcao-cinematografica.md) entre
  os painéis do mesmo shot.

**"3/4" TEM TRÊS SENTIDOS E DOIS DELES SÃO VIVOS — desambiguação obrigatória (set/2026):**
O termo é ambíguo em português e **já vazou uma vez** (caso da porta da cabana, jul/2026). Antes de
escrever ou de corrigir qualquer painel com "3/4", identificar de qual se trata:

| Sentido | Status | O que é |
|---|---|---|
| **3/4 de LOCAÇÃO** | ✅ **VIVO** 🎓 | Câmera posicionada de modo que **duas paredes do ambiente** apareçam e o espaço ganhe profundidade. É sobre CENÁRIO, não sobre corpo. A Higgsfield Academy usa exatamente assim: *"shot from a 3/4 angle so two walls of the room are visible and the space reads with depth"*. |
| **3/4 de PESSOA, assimétrico** | ✅ **VIVO** | UMA figura em 3/4 **e a outra não** (quase de perfil, de costas, encostada). É o instrumento ANTI-espelho — serve para as duas justamente **não** ficarem na mesma angulação. É o que a regra abaixo manda fazer. |
| **3/4 de PESSOA, espelhado** | ❌ **MORTO** ⚫ | As **duas** figuras giradas no mesmo ângulo para a lente, de corpo inteiro, simétricas. Vinha da IA achar que todo mundo precisa aparecer inteiro. Não é natural nem orgânico. **Decisão do Samuel — não ressuscitar.** |

> **O erro nunca foi o ângulo 3/4. Foi a SIMETRIA e o corpo inteiro obrigatório.** Quem lê "3/4
> morreu" e apaga o 3/4 de locação ou o 3/4 assimétrico está desfazendo regra que funciona.
> 🎓 Confirmação independente: na aula de diálogo da Academy, duas pessoas conversando são encenadas
> com **eixo de 180°, over-the-shoulder e close médio** — o oposto de "os dois virados para a câmera".

**INTENÇÃO DA CENA DECIDE SIMETRIA OU ASSIMETRIA (caso porta da cabana, jul/2026 — refinamento):**
A simetria de perfil-contra-perfil resolve o viés de retrato, mas virou o novo default rígido: duas
figuras espelhadas, exatamente opostas, mesmo numa cena mundana — lê como duelo, não como duas
pessoas reais numa porta. Antes de escolher a encenação, classificar a intenção:
- **CONFRONTO HOSTIL/ÉPICO** (deus vs. vítima, monstro vs. herói, embate declarado): a simetria é
  proposital — reforça oposição. Usar OVER-THE-SHOULDER ("seen from behind [A], [B] head-on in the
  distance, facing [A] directly") ou perfil contra perfil simétrico ("facing EACH OTHER in profile,
  [A] on frame-left facing right, [B] on frame-right facing left").
- **ENCONTRO SOCIAL/COTIDIANO** (visita, conversa, entrega, pedido, qualquer interação sem
  hostilidade declarada): NUNCA espelhar. Assimetria é o que parece real — pessoas de verdade não
  se posicionam como peças de xadrez. Declarar explicitamente a diferença entre as duas figuras:
  ângulos diferentes (uma em 3/4, outra quase de perfil — não as duas na mesma angulação), peso do
  corpo desigual (uma apoiada no batente, outra parada), profundidade desigual (uma mais perto da
  câmera que a outra, não lado a lado na mesma distância), e leve deslocamento do eixo central —
  quem recebe (a anfitriã) tende a ocupar menos espaço de quadro e estar mais estática; quem chega
  (a visitante) tende a ter mais peso postural (inclinação, mão, hesitação). Ex.: "[A], slightly
  turned at a natural 3/4 angle, weight on one leg, standing a step back from the threshold; [B] in
  the doorway, body angled slightly OUT of strict profile, one hand on the frame — NOT a mirrored
  stance, an ordinary asymmetric moment between two people."
- Regra de bolso: se o painel parecer bonito demais para a cena que ele descreve, provavelmente é
  simetria vazando de um confronto para um momento comum. Perguntar: essas duas pessoas têm razão
  para se posicionar como um espelho? Se não, quebrar a simetria.

**POPULAÇÃO DO QUADRO — co-presença é default, e default é vício (casos Nero/Dullahan, jul/2026):**
Dois personagens no mesmo ambiente NÃO significam dois personagens em todos os painéis. A cobertura
profissional de cena com 2+ personagens é composta de:
- MASTER/TWO-SHOT: os dois juntos, estabelecendo a geografia (1–2 painéis bastam);
- SINGLES: painéis de UM personagem só — em especial o CLOSE DE REAÇÃO (o rosto de um deles
  reagindo; a unidade emocional básica do cinema). Todo bloco com 2+ personagens importantes DEVE
  conter ao menos um single/reação por personagem importante, salvo pedido contrário;
- INSERTS: o detalhe (mão, objeto, olho).
Excluir um personagem de um painel DE PROPÓSITO é ferramenta, não erro — mesmo ambiente ≠ 100% de
tempo de tela compartilhado. Declarar a população de cada painel na ficha ("P3: single da vítima").

**ORIENTAÇÃO MOTIVADA DO CORPO — ninguém encara a câmera por default:**
O corpo de cada personagem aponta para o alvo da sua ATENÇÃO (a ameaça, o objeto, o horizonte),
nunca para a câmera — "de frente para a câmera" só com motivação dramática explícita (raríssimo no
canal). Declarar por personagem, por painel: para onde olha, para onde o corpo aponta.
REAÇÃO CORPORAL ENCENADA: quando algo chega/muda, o corpo mostra o estágio da reação — a cabeça
gira ANTES do corpo (meia-volta sobre o ombro), recuo, congelamento. Ex. correto para "criatura
chega por trás do bandido": bandido de COSTAS para a câmera em primeiro plano, cabeça virada sobre
o ombro direito em meia-volta, criatura ao fundo pequena e fora de foco — nunca os dois lado a
lado olhando a câmera.

**PLANO-SEQUÊNCIA × SETUPS ISOLADOS — declarar o regime do bloco:**
Alguns blocos são um plano-sequência (painéis = intermediários de um take contínuo); outros são
montagem de setups isolados (cada painel/shot é uma câmera diferente: two-shot, single, insert).
A ficha do bloco declara o regime; o padrão de montagem escolhido (passo 5a da direção) costuma
decidir. Não ter medo de alternar os regimes entre blocos do mesmo vídeo.

**ENCENAÇÃO DE PROFUNDIDADE — "ao fundo" não funciona:**
Gerador ignora advérbio de lugar e puxa o sujeito para onde fica legível. Para manter algo no
fundo, comandar com tamanho-no-quadro, foco e luz, explicitamente:
"in the FAR background, at the very end of the alley, tiny in frame, barely-visible silhouettes
half-hidden in shadow, out of focus — the foreground subject is [X], sharply in focus".
Se o elemento de fundo saiu grande/nítido/à frente, o painel falhou: regenerar (a progressão
"eles se aproximam" pertence aos painéis SEGUINTES, um estado por painel).

**Ponte com o Documento 3 (anti-estático):** o [SHOT 1] do prompt Seedance segura o estado do
painel 1 por ~0,5–1s antes do primeiro movimento (respiro que ancora o começo), e o [ACTION]
descreve o movimento CONTÍNUO que liga um keyframe ao seguinte — os painéis são os postes, o
texto do Seedance é o fio.

## RETROFIT — consertar painéis já gerados sem refazer a folha

Para acervo antigo com os vícios acima, editar o PAINEL (recortado da folha), não a folha inteira.
Dois templates (preencher os colchetes; conferir identidade/figurino após a edição — edição pode
derivar o rosto; se derivar, regenerar o painel avulso citando o model sheet sai mais barato):

TEMPLATE A — re-encenar staging/orientação:
"Edit this image. Keep the EXACT same characters (same faces, wardrobe, proportions), the same
environment, lighting, color grading and ultra-realistic photographic style. Change ONLY the
staging and body orientation: [novo blocking — ex.: 'the old bandit now has his BACK to the
camera in the foreground, head turned over his right shoulder in mid-turn, reacting; the headless
armored figure approaches from the deep background, small in frame, out of focus']. No character
faces the camera — each body faces what that character is looking at."

TEMPLATE B — extrair um single/reação de um two-shot:
"Using this image as strict reference for identity, wardrobe, lighting and environment, generate
a NEW panel: an isolated close-up (reaction shot) of ONLY [personagem] — [micro-ação: eyes
widening, jaw tightening, breath caught]; all other characters completely out of frame; same
location behind, out of focus; same photographic style and color grading. The character looks at
[alvo da atenção], off-frame [direção] — never at the camera."

## Diagnóstico rápido quando o resultado sair "ilustrado" ou sangrado

000. Todos os painéis mostram todos os personagens juntos? → co-presença é default; faltam
     singles/closes de reação (população do quadro). Alguém de frente para a câmera sem motivação?
     → orientação do corpo segue a atenção, não a lente.
0000. Duas figuras perfeitamente espelhadas (mesma pose, mesmo ângulo, oposta) numa cena SEM
      hostilidade declarada (visita, conversa, entrega)? → simetria de confronto vazou para cena
      mundana; quebrar com ângulos/pesos/profundidades diferentes entre as duas figuras.
00. Dois sujeitos lado a lado olhando a câmera quando a cena era confronto/relação? → faltou a
    geometria de relação (posição + direção do olhar + distância por sujeito; OTS ou perfil×perfil).
0. Painéis se emendando / elemento cruzando calha? → o prompt declarou o grid explícito ([C]x[R],
   equal-sized, thick black gutters, self-contained) e a cláusula STRICT PANEL SEPARATION? (causa nº 1
   do sangramento — e folha sangrada NÃO vai para o Seedance)
1. A âncora de realismo estava no prompt, completa, no final? (causa nº 1 do acabamento ilustrado)
2. O prompt redescreveu a aparência da criatura em linguagem fantasy ("majestic mythical beast")?
   → remover; a referência de imagem cuida da criatura, o texto só da ação/cena.
3. Palavras-gatilho de ilustração no prompt ("epic", "artstation", "fantasy art", "concept")? → remover.
4. Persistindo: gerar o painel problemático isolado (fora do grid) com a âncora e recompor.

Registrar aqui padrões observados (o que o gerador ignora, o que vaza estilo), com data:
- (nenhum registro ainda)
