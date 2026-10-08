# Estilo e contenção — as âncoras do canal (fonte única)

> ⚫ **Decisão do Samuel, 2026-10-06, a partir de testes:** a âncora ultra-realista atual é melhor
> para a **criatura**; para **humanos, ambientes e objetos**, a versão **naturalista** é melhor.
> Cena com os dois mistura: criatura ultra-realista, o resto naturalista.
>
> **Este é o único lugar onde as âncoras estão escritas.** Qualquer outro arquivo, prompt antigo
> ou nota que traga uma âncora diferente está desatualizado.

---

## 1. Qual âncora vai em cada coisa

| O que está sendo gerado | Âncora |
|---|---|
| Componente `cri_` (model sheet da criatura) | **A — CRIATURA** |
| Componente `per_` (personagem humano) | **B — NATURALISTA** + **D — PELE HUMANA** |
| Componente `amb_` (ambiente) | **B — NATURALISTA** + **C — FÍSICA DA CENA** |
| Componente `obj_` (objeto) | **B — NATURALISTA** |
| Referência de bloco **sem** a criatura | **C** (1–3 frases) + **D** se houver rosto + **B** no fim |
| Referência de bloco **com** a criatura | **C** (1–3 frases) + **E — MISTA** + **B** no fim |
| Prompt de cena (vídeo) | bloco `LOOK` da `etapa-4-cena.md`, montado a partir de **B** (e **E** se houver criatura); física específica em `PHYSICS AND RESTRAINT` |

A âncora vai **no fim** do prompt de imagem, colada sem edição. Lente e luz da cena podem ser
ajustadas no corpo do prompt, nunca dentro da âncora.

---

## 2. As âncoras, para colar

### A — CRIATURA (ultra-realista, a atual, mantida porque funciona)

```
RAW photo, ultra-realistic, real-life. Shot on cinema camera, 35mm lens, shallow depth of field.
Natural skin texture with pores, subsurface scattering, fine hair detail, realistic fabric and
material wear, physically accurate lighting and shadows, film grain. Absolutely NO illustration,
NO painting, NO concept art, NO anime, NO 3D render, NO cartoon, NO stylized art. It must look
like a photograph of something real.
```

E no corpo do prompt da criatura, sempre: tratar como **criatura física fotografada** (prótese e
animatrônico de cinema de altíssimo orçamento, pele, escama e textura com imperfeição real), nunca
"fantasy art". Por que o ultra-realista funciona aqui e não no resto: o assunto puxa o gerador
para concept art, e só uma âncora forte segura isso. Em humano e paisagem, a mesma força vira
exagero (ver §3).

### B — NATURALISTA (bloco padrão: humanos, ambientes, objetos)

⚫ **Revisto em 2026-10-06 a partir da análise do GPT do Samuel.** Substitui a antiga dupla
"naturalista + contenção": a versão anterior era verbosa e repetia proibições ("avoid…", "no
excessive…"), o que dilui o que importa. Esta descreve **como os fenômenos se comportam** e pede
efeitos **proporcionais à causa física** — não "poucas partículas" (isso deixaria uma onda batendo
no casco artificialmente limpa).

```
Photographic naturalism with restrained cinematic styling. The scene should feel physically
plausible and observational, as if captured by a real cinematographer during an actual event.
Environmental effects remain naturally distributed, irregular and localized rather than uniformly
dramatic. Water, foam, spray, rain, mist, smoke, clouds, fire, vegetation and airborne particles
appear only where physically justified, with realistic density, scale and persistence,
proportional to their physical cause. Allow calm, visually quiet areas within the frame. Not every
wave breaks, not every surface carries droplets, not every cloud is sharply defined, and not every
fire produces dense smoke, sparks or glowing reflections. Cinematic quality comes from framing,
lens choice, depth, lighting and composition, not from atmospheric spectacle or extreme contrast.
Preserve natural imperfections, asymmetry and visual breathing room. Favor physically
proportional, understated naturalism over visually amplified realism: let the event provide the
drama. Shot on a cinema camera with a 35mm lens and visible fine film grain.
```

### C — FÍSICA DA CENA (1 a 3 frases, específicas daquela imagem)

Depois do bloco B, cada prompt acrescenta **só de 1 a 3 frases** sobre o fenômeno que aparece
naquela imagem, tiradas da §4 (mar, chuva, fumaça e fogo, nuvens, vegetação, névoa) ou escritas no
mesmo estilo: o que a matéria **faz**, não o que ela **não** faz. Isso é mais importante do que
repetir "less foam" vinte vezes. Imagem sem fenômeno ambiental não leva C.

### D — PELE HUMANA (personagem humano; e toda referência com rosto em close)

```
Visible fine skin texture with natural pores, fine lines, subtle asymmetries and irregular
tone; slight natural sheen rather than a glossy retouched finish; naturally muted catchlights in
the eyes; defined adult facial structure. No digital smoothing, no beauty filter, no
AI-airbrushed look.
```

Junto com a âncora D, o prompt do personagem nomeia **pelo menos três imperfeições** dele (olheira,
ruga, assimetria, entrada de cabelo, cicatriz, dente torto, pele irregular). Imperfeição é
especificação: o polido demais é o que sai falso.

### E — MISTA (imagem ou cena em que a criatura aparece junto de gente, lugar ou objeto)

```
The creature is photographed as a real physical being: ultra-realistic surface detail, wet and
weighted skin, practical-effects realism, never illustration or concept art. Everything else —
people, location, objects and weather — follows photographic naturalism: grounded real-life
appearance, restrained contrast, natural exposure, physically plausible materials, shot as if by
a real cinematographer documenting an actual event, on a cinema camera with a 35mm lens and
visible fine film grain.
```

---

## 3. Por que existe a contenção — o defeito que ela corrige

Nas imagens geradas até out/2026, o realismo técnico estava certo (material, luz, textura), e o que
denunciava a IA era o **excesso de informação física**: toda onda com espuma, toda superfície com
gotícula, todo incêndio refletindo laranja em tudo, a tempestade inteira no ápice ao mesmo tempo.

Palavras como *storm*, *rain sideways*, *physically accurate*, *ultra-realistic* e *cinematic* são
lidas como "maximize todos os sinais de tempestade". O resultado fica realista no detalhe e
estatisticamente falso.

**A regra de fundo:** ⚫ *o perigo vem da situação, não do efeito visual.* Um navio pegando fogo
numa tempestade já tem drama suficiente; ele não precisa de onda enorme, espuma enorme, 500
gotículas, fumaça volumétrica, faísca, chuva perfeitamente visível e reflexo laranja em tudo, tudo
junto. **Cinematográfico não quer dizer espetacular:** a imagem é cinematográfica pelo enquadramento,
pela lente, pela luz e pela marcação, e o mundo fotografado continua contido.

---

## 4. Física por efeito — descrever o comportamento, não o adjetivo

Em vez de "violent storm, huge waves", escrever **como a matéria se comporta**. Frases prontas:

**Mar agitado**
```
Rough open sea with heavy rolling swells rather than constantly breaking waves. Most wave
surfaces remain dark and relatively smooth, with whitecaps appearing only intermittently. Spray
occurs mainly where waves physically strike the hull. Minimal airborne droplets. Foam is
localized, irregular and short-lived rather than covering every crest.
```

**Chuva**
```
Visible rainfall is subtle and intermittent in the exposure; individual raindrops are rarely
resolved by the camera. Wet surfaces carry the rain: dark planks, beaded fabric, water running
off edges, rather than a curtain of bright streaks or dense suspended droplets.
```

**Fumaça e fogo**
```
Smoke is uneven, partially transparent and dispersed by wind, with large areas of relatively
clear air. Limited embers and sparks. Fire illuminates only nearby wet surfaces rather than
casting orange highlights across the entire scene.
```

**Nuvens**
```
Natural storm-cloud structure with broad, soft tonal masses and irregular transitions, rather
than hyper-detailed billowing formations or repeated dramatic shapes.
```

**Vegetação**
```
Natural vegetation density and irregularity: gaps, dead material, sparse areas and natural
asymmetry, rather than uniformly lush foliage filling every empty space.
```

**Névoa** (quando ela é ferramenta de limpeza de fundo, `direcao-bloco-acao.md` §3.3)
```
Low, uneven mist with irregular density, thinning and thickening with the wind, leaving distant
shapes partly readable.
```

Repare na forma: cada frase diz **o que acontece** primeiro, e a negativa só aparece como contraste
("rather than…"). Negativa solta não funciona (ver `etapa-4-cena.md`, regra das travas).

---

## 5. Pedido de efeito do Samuel

Quando o roteiro pede um efeito (câmera lenta, água parada no ar, a criatura emergindo de uma onda
gigante), **o pedido vence a contenção naquele ponto e só nele**: o efeito pedido é o único
elemento dramático no auge, e o resto do quadro segue contido para não competir com ele. Escrever
isso explicitamente no prompt: *"the wave is the only dramatic element in this beat; sky, rain and
deck stay understated."*
