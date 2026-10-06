# Dossiê — Higgsfield Academy, seção **Movie making**

> Levantado pelo Salomão em **2026-09-02**. Entrada nova no esquema de proveniência
> do `REGRAS-PRODUCAO-VIDEO.md`:
>
> 🎓 = **material oficial da Academy do Higgsfield** (higgsfield.ai/academy), lido em 2026-09-02.
> Peso: é o fabricante falando da própria ferramenta — mais forte que 🟡 (observação de terceiros),
> mais fraco que 🔵 (medido por nós) para qualquer número de custo.

---

## 0. Aviso de calibragem — ler ANTES de aplicar qualquer coisa daqui

**Praticamente todo o material da Academy é demonstrado em Seedance 2.0 / "Seedance 4K".**
O nosso alvo é **Seedance 2.5 a 480p + upscale local na RTX 3050**.

> **Método atravessa. Número não atravessa.**
> Nada neste dossiê toca a §1 do `REGRAS-PRODUCAO-VIDEO.md` — a resolução é decisão de
> orçamento (⚫ do Samuel + 🔵 medido), não de gosto, e o marketing 4K deles não é evidência
> contra ela. Aliás o curso de VFX **confirma o upscale como etapa normal do pipeline**, que é
> exatamente o nosso caminho.

**Limitação de leitura, declarada:** as páginas de aula montam por JavaScript e o vídeo em si
não foi transcrito. O que está abaixo veio do HTML servido — títulos, descrições, "what you'll
learn" e, em **4 aulas**, o texto do prompt de exemplo que veio no SSR. Onde não deu para ler,
está escrito que não deu. Não foi inventado nada a partir do título da aula.

---

## 1. Inventário — os 7 cursos de Movie making

| # | Curso | Nível | Módulos | Duração | Link |
|---|---|---|---|---|---|
| 1 | Blockbuster 4K: The AI Filmmaking Pipeline | Intermediate | 10 | 40 min | `/academy/courses/blockbuster-4k` |
| 2 | Build an Ultra-Realistic Short Film in 4K (*"Santiago"*) | Intermediate | 19 | 33 min | `/academy/courses/santiago-cinematic` |
| 3 | Add AI VFX to Real Footage | Advanced | 11 | 12 min | `/academy/courses/ai-vfx-real-footage` |
| 4 | Make an AI Animated Short | Intermediate | 11 | 17 min | `/academy/courses/ai-animated-short` |
| 5 | How to evaluate AI filmmaking demos | Beginner | 11 | 20 min | `/academy/courses/seedance-25-ai-filmmaking` |
| 6 | Seedance 4K: Cinematic Realism | Intermediate | 8 | 14 min | `/academy/courses/cinematic-realism-4k` |
| 7 | Direct AI fight scenes through controlled iteration | Intermediate | 5 | 16 min | `/academy/courses/direct-ai-fight-scenes` |

Fora do escopo pedido, mas registrado porque existe: **UGC & Social Content** (7 cursos) e
**Automate & Agents** (2 cursos) — nestes últimos, dois são sobre **canal faceless automatizado
conectando Claude + Higgsfield**, que é literalmente a arquitetura do WhoIAm. Vale um segundo
levantamento depois; não é este.

### Índices de aula lidos

**#2 Santiago (19 aulas)** — 1 Thinking like a director · 2 Watch the short · 3 Write the script
with story structure · 4 Character sheets in Soul Cinema · 5 **Locations with the 3/4 angle** ·
6 **The prompt-builder skill and first Seedance run** · 7 **Read your failed takes** · 8 The Dutch
angle and combining takes · 9 Scene 2 assets · 10 The match cut, flares, fog and handheld ·
11 One-off characters · 12 Establishing shots and realistic hands · 13 The speed ramp ·
14 The whip pan and readable text · 15 Age your character for flashbacks · 16 Directing the
voice-over · 17 Dialogue pacing after a flashback · 18 The final scene in three shots · 19 Recap.

**#1 Blockbuster (10 aulas)** — Stage 1 Writing the Script with Claude · Stage 2 Building
Character, Location and Prop Assets · Stage 3 Scene Generation with the Prompt-Builder Skill ·
depois 5 aulas de cena e o recap.

**#7 Fight scenes (5 aulas)** — Blueprint the Fight Before Motion · Diagnose and Repair a Complex
Shot · Direct Scale and Transformation with Measurements · Preserve Physics Through the Impact
Cut · Replace Game-Like Coverage with Cinematic Direction.

**#3 VFX (11 aulas)** — video-to-video · world swap andando · world swap dirigindo · cabeça em
chamas · mão vira cobra · criatura por imagem de referência · handheld showcase · templo desabando
· saurópodes na chuva · kraken · recap.

---

## 2. O que CONFIRMA o que já tínhamos

Nada disto é novidade — o valor é ser **confirmação por fonte independente** da aula de YouTube
que sustenta metade do `REGRAS-PRODUCAO-VIDEO.md`.

🎓 **Pipeline em estágios** — roteiro → assets → geração cena a cena. É a nossa divisão de fases.

🎓 **Character sheet de três painéis.** A aula "Character sheets in Soul Cinema" especifica: frente,
costas e close-up de rosto; fundo de estúdio cinza liso com divisórias finas escuras; luz neutra
*soft wrap-around* a **5600K**, sombra mínima; e o que eles chamam de *quality locks* — **mesma
pessoa, mesma roupa, mesmas proporções, mesmo fundo em todos os painéis**. É o nosso model sheet
(`model-sheet-storyboard.md`), com outro nome. A ficha inclui altura em metros (~1,82 m), formato
de rosto, cor de olho, cabelo, barba por fazer irregular "para parecer vivido", e paleta de roupa
nomeada cor por cor.

🎓 **Âncora de realismo, com o vocabulário deles.** O prompt de exemplo da aula 6 do Santiago abre
com: *8K IMAX, photorealistic, 24fps, 21:9* · referência a **Emmanuel Lubezki e Roger Deakins** ·
*natural light only, contre-jour backlight, ~4800K* · *pore-level realism*. É exatamente a função
da nossa âncora de realismo — e a existência dela no material oficial mata o argumento de que ela
seria firula nossa.

🎓 **Negativa de áudio dentro do texto.** O mesmo prompt fecha com *diegetic room tone only — no
music, no subtitles*. Ou seja: mesmo tendo parâmetro, eles **mantêm a frase negativa no texto**.
Isso valida o "cinto e suspensório" registrado na tabela da §7 do `planejamento-fluxo-higgsfield.md`.

🎓 **Multi-shot dentro de UM prompt, com segundos.** *"Shot 1 (0–9s) wide establishing · Shot 2
(9–15s) tight closeup · one hard cut, no transitions"*. É o bloco **STAGES** do §3 do
`REGRAS-PRODUCAO-VIDEO.md`, com o mesmo desenho: segundo de início, o que acontece, como está
enquadrado.

🎓 **Geração ruim é matéria-prima, não crédito perdido.** A aula 7 do Santiago chama-se literalmente
*"Read your failed takes"*, e o curso de luta traz *"diagnose whether the failure came from the
instruction or the output, then adjust only the problematic variable"*. É a nossa §5 inteira —
inclusive a ordem de tentativa. **Duas fontes independentes agora dizem a mesma coisa.**

---

## 3. O que é NOVO — não tínhamos isto em lugar nenhum

### 3.1. 🎓 Existe uma skill oficial de construção de prompt — `higgsfield-seedance-prompt.skill`

Baixável na aula **Stage 3** do Blockbuster, junto de um *scene asset pack*. É um construtor de
prompt do próprio fabricante, empacotado como skill do Claude.

> **Isto é a coisa mais importante do dossiê.** Antes de reescrever uma linha do nosso formato de
> prompt, baixar essa skill e comparar **campo a campo** com o formato avançado do §3. Se os campos
> baterem, o nosso formato ganha respaldo do fabricante. Se divergirem, a divergência precisa de
> decisão consciente — não de adoção automática.

### 3.2. 🎓 Ângulo 3/4 **de locação** (não de pessoa)

Texto lido, verbatim: *"shot from a 3/4 angle so two walls of the room are visible and the space
reads with depth"*. Vem acompanhado de encenação métrica — duas poltronas de couro tan a **~1,5 m
uma da outra**, mesa redonda de madeira entre elas — e de luz (*soft golden daylight, gentle warm
shadow, shallow depth of field, soft bokeh, fine 35mm film grain*).

Ver §4.1 antes de aplicar. **Isto não é o 45° de personagem que o Samuel matou.**

### 3.3. 🎓 Eixo de 180° declarado DENTRO do prompt de diálogo

Da aula "Scene 4: The Twist and Dialogue Scenes": eixo de 180° mantido pela cena inteira;
**over-the-shoulder** e **medium close-up**; *"no drift mid-segment"*; horizonte nivelado com
Dutch tilt usado por exceção; e os corpos orientados para direções de quadro específicas
**para preservar a geografia de tela**. Direção de atuação: *naturalistic and restrained*, reação
física carregando a emoção, microexpressão e respiração visíveis.

### 3.4. 🎓 Ótica declarada em GRAUS de campo de visão, não em milímetros

O prompt bank público deles escreve `de [84] graus para [29 ou 18]`, `84° wide`, `47° medium`.
Nosso `direcao-cinematografica.md` fala em mm (28mm, 100mm — que também aparecem na Academy).
São dois vocabulários e o modelo entende os dois; o deles é o que aparece nos exemplos prontos.

### 3.5. 🎓 Prompt bank público — 46 exemplos só de câmera, texto pronto

Fora dos cursos, aberto na própria página da Academy. E ele revela uma técnica que não está no
nosso material: **o movimento é escrito por NEGAÇÃO, exaustivamente.** Exemplo do "Pan right":
*"no sideways travel, no dolly, no truck, no arc, no slide, no zoom, no tilt"*. O "Static shot"
gasta a frase inteira negando: *"no drift, no shake, no breathing, no stabilization float, no
micro-drift"*.

Matéria-prima direta para o `direcao-cinematografica.md` e para as fichas de controle. Categorias:
Static · Pan & tilt · Zoom & focus · Aerial & crane · Dolly & tracking.

### 3.6. 🎓 Bloco de AÇÃO — temos quase nada, eles têm um curso inteiro

*"Blueprint the fight before motion"* · medidas numéricas (metros, segundos) para escala e
transformação · *"preserve physics through the impact cut"* · *"replace game-like coverage with
cinematic direction"* · prompts com **componentes nomeados, medidas espaciais, timing de movimento
e limitações construtivas**.

Nossa classificação AÇÃO/SIMPLES (§3 do `planejamento-fluxo-higgsfield.md`) diz **quanto gastar**
num bloco de ação. Não diz **como dirigi-lo**. Este curso é o buraco.

### 3.7. 🎓 video-to-video sobre footage real

Curso inteiro sobre trocar mundo, adicionar criatura e casar cor com footage de câmera comum.
**Não existe uma linha sobre isso em nenhum documento nosso.** Pode ou não servir ao WhoIAm — é
decisão do Samuel, não do agente.

### 3.8. 🎓 Rubrica de aceitação de take

O curso #5 é sobre **como avaliar** uma demo: evidência visual de que um movimento de câmera se
sustenta, performance sob pressão, continuidade espacial, arco emocional, e o *tradeoff* de
produção. Nós temos ordem de correção quando o take falha; **não temos critério escrito de quando
um take passa.**

---

## 4. O que BATE DE FRENTE — e o veredito de cada um

### 4.1. O "3/4 angle" × a correção do Samuel sobre as duas pessoas a 45°

**Parece contradição. Não é. E a prova está no material deles mesmo.**

- O 3/4 da Academy é enquadramento de **SALA**: a câmera vê duas paredes, o espaço ganha
  profundidade. É sobre **cenário**.
- O erro que o Samuel matou era de **PESSOA**: dois corpos espelhados, girados para a lente,
  ambos de corpo inteiro — a IA achando que todo mundo precisa aparecer inteiro.
- Na aula de diálogo **deles**, duas pessoas conversando são encenadas com **eixo de 180°,
  over-the-shoulder e close médio** (§3.3). Isso é o **oposto** de "os dois virados para a câmera".

**Veredito: manter a nossa regra.** E — recomendação — **escrever a distinção em uma linha
explícita** no `model-sheet-storyboard.md`, porque "3/4" é ambíguo em português e é exatamente o
tipo de termo que faz a regra velha voltar a vazar. Já existe registro nosso do vazamento (o caso
da porta da cabana, jul/2026, em `seedance-receituario.md`).

### 4.2. 4K / Seedance 2.0 em todo o marketing

**Não muda nada.** Ver §0. E o curso de VFX confirma upscale como etapa normal do pipeline.

### 4.3. Storyboard

Eles **não** entregam storyboard como artefato — entregam **asset sheets** (personagem, locação,
prop) + shotlist + prompt com stages. Isso **reforça** a decisão ⚫ do Samuel de não produzir
storyboard separado, e **não** responde P2 nem P3 da §6 (que continuam abertas). Registrado como
reforço, não como resposta.

---

## 5. LIMITE DE CARACTERES — estado real, hoje

| Número | De onde veio | Situação |
|---|---|---|
| **1.494** | Leonardo | **MORTO.** Ainda listado como "regra vigente" em `references/direcao-cinematografica.md:95` — corrigir |
| **5.000** | 🎥 aula do Seedance 2.5 (YouTube) | É limite **do modelo**, e é o que sustenta o argumento de não usar o modo de vídeo longo (§4) |
| **3.500** | "fonte de terceiro" sobre o Higgsfield, `planejamento-fluxo-higgsfield.md` §8 | **Nunca verificado.** Origem não localizada |

🎓 **A Academy não publica número nenhum.** Os prompts de exemplo que consegui ler passam folgado
dos 1.494 e ficam confortavelmente abaixo de 5.000.

> **Conclusão honesta: nada encontrado hoje justifica um teto abaixo de 5.000.**
> O 3.500 não tem lastro. O 1.494 é de outra ferramenta. O único número com fonte é 5.000, e é
> do modelo, não da plataforma.

---

## 6. O que este levantamento NÃO cobriu

- **O áudio/vídeo das 7 aulas.** As páginas montam por JS e várias respondem "this lesson couldn't
  be rendered" ao leitor. Só 4 aulas entregaram prompt no HTML.
- **A skill `higgsfield-seedance-prompt.skill`** — identificada, não baixada.
- **5 dos 7 cursos** só tiveram o índice lido, não o conteúdo.
- Os 9 cursos das outras duas categorias — incluindo os dois de **canal faceless com Claude +
  Higgsfield**, que são o nosso caso de uso exato.
