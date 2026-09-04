# Studio — auditoria e plano de melhoria

> Apurado em **2026-09-02**. Duas partes: (A) **auditoria do que existe hoje**,
> lida no código, com arquivo e linha; (B) **pesquisa** do Salomão e complementar,
> com fonte e data.
>
> Marcadores: 🔍 lido no nosso código · 📚 fonte externa com data · 🧠 leitura
> minha, não é fonte · ⚫ decisão do Samuel.
>
> Dossiês brutos do Salomão em `D:\Agentes\SALOMAO\missoes\2026-09-02-*`.

---

## RESUMO — as sete coisas que importam

| # | Achado | Gravidade |
|---|---|---|
| 1 | ✅ **RESOLVIDO 04/09/2026.** ~~As legendas já são geradas e nunca são usadas.~~ O `align` escreve `captions.json` "para o Studio/Remotion queimar no Short" — e o Studio não lê esse arquivo em lugar nenhum | **Alta — trabalho já pago, jogado fora** |
| 2 | ✅ **RESOLVIDO 04/09/2026.** ~~O Short não é 9:16.~~ `buildShortPlan` herda `width/height` do plano cheio; é um corte 16:9 mais curto | **Alta — o formato está errado** |
| 3 | **O upscale roda, mas não é upscale de IA.** É `scale=lanczos` — não inventa detalhe nenhum. O próprio comentário do código admite | Média |
| 4 | **A ordem upscale/interpolação está invertida** em relação à única orientação que achei | Média — testar, não virar no escuro |
| 5 | **O ASR do alinhador é Vosk, descrito no próprio código como "qualidade medíocre"** — e o `faster-whisper` passou a funcionar nesta máquina hoje | Média — troca barata, ganho direto |
| 6 | **O render final não declara bitrate nem CRF.** A fonte diz que esse é "o maior erro" de pipeline de upscale | Média |
| 7 | **A interpolação para 60fps pode estar ativamente prejudicando** vídeo gerado por IA — e é o passo mais caro do pipeline | **Pergunta para o Samuel, não decisão minha** |

---

# PARTE A — O QUE TEMOS HOJE

## A1. Upscale

🔍 [`lib/render/postprocess.ts`](../../Ai-Project/Omega/studio/lib/render/postprocess.ts) — filtro
`scale=-2:{alvo}:flags=lanczos`, alvo = lado curto de 1080 px
([`output-resolution.ts:MINIMUM_SHORT_SIDE`](../../Ai-Project/Omega/studio/lib/edit-plan/output-resolution.ts)).

**Está rodando?** Sim. `planEnhancement` pula clipe que já está no alvo, guarda o
original em `videos-original/`, e o `enhanceProjectClips` roda **antes** do
`analyze` — de propósito, para o EditPlan medir a duração real depois da
alteração. Essa arquitetura está certa e é a parte boa: elimina por construção a
classe de bug de dessincronia áudio/vídeo.

**É a melhor forma?** Não, e o código sabe disso: *"Real-ESRGAN (AI) is the
planned upgrade for real detail synthesis (this never invents detail)"*.

## A2. Interpolação

🔍 `minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1`, CPU,
`CONCURRENCY = 2`. Custo medido registrado no próprio código: **~79 s para um
clipe de 15 s a 480p**.

🧠 **Extrapolando para um vídeo de 10 min** (40 clipes de 15 s): ~53 min de CPU,
~26 min com a concorrência de 2. **É o passo mais caro do pipeline inteiro**, e
roda em toda geração.

🔍 Há uma correção de deriva bem feita depois: o `minterpolate` desloca a duração
em 75–90 ms, e um segundo passe reescala PTS (`setpts`) para fechar em 8 ms.
Documentado com o que foi tentado e rejeitado antes. Isso é bom trabalho.

## A3. Shorts

🔍 [`lib/edit-plan/build-short-plan.ts`](../../Ai-Project/Omega/studio/lib/edit-plan/build-short-plan.ts)
— pega um **prefixo** do plano cheio até o corte mais próximo de 30 s, reaproveita
os cues de trilha, e chama `applyBoundaries(... fullPlan.width, fullPlan.height)`.

> **O Short sai em 16:9.** Não há reenquadramento, não há detecção de sujeito,
> não há nada de 9:16 em lugar nenhum do repositório.

## A4. Legendas — o achado que mais dói

🔍 `align/README.md` declara, na tabela "O que sai":

| Arquivo | Para quê |
|---|---|
| `captions.pt.srt` | legendas prontas para subir no YouTube |
| `captions.json` | **as mesmas legendas para o Studio/Remotion queimar no Short** |

🔍 E o `align/alpha_align/legendas.py` é sério: 42 caracteres por linha, no máximo
2 linhas, piso e teto de duração (1 s / 7 s), 17 caracteres por segundo, quebra
equilibrada sem partir palavra, e uma nota de que são as convenções de
legendagem Netflix/BBC. Também exporta SRT e VTT.

🔍 **E o Studio nunca lê esse arquivo.** O `load-alignment.ts` valida um schema
que só tem `blocos` — descarta `palavras` e `falas`. A composição
[`remotion/EditedVideo.tsx`](../../Ai-Project/Omega/studio/remotion/EditedVideo.tsx)
tem clipes, narração e música. **Nenhuma camada de texto.**

Ironia registrada: o comentário do `output-resolution.ts` justifica renderizar a
1080p dizendo *"gives crisp overlays for free"* e *"including captions and any
overlay drawn by Remotion"* — overlays que não existem.

## A5. ASR

🔍 `align/alpha_align/asr.py`, docstring literal: *"Backend atual: **Vosk offline
pt-BR** (...) **A qualidade da transcrição é medíocre** — e isso é tolerável por
desenho (...) **Trocar por WhisperX/MFA depois é trocar esta função**: a saída é
uma lista de `PalavraASR` e nada mais do sistema sabe de onde ela veio."

O alinhador só usa as palavras que o ASR acertou como âncora, e interpola o
resto. **Mais palavras acertadas = mais âncoras = tempos melhores e confiança
maior.**

## A6. Render final

🔍 [`lib/render/render-composition.ts`](../../Ai-Project/Omega/studio/lib/render/render-composition.ts)
— `renderMedia({ codec: "h264", ... })`. **Sem `crf`, sem `videoBitrate`, sem
`x264Preset`.** Fica no padrão do Remotion.

🔍 Cadeia de encodes por clipe: enhance (x264 CRF 18) → [retime, se interpolou:
x264 CRF 18 de novo] → decode no Chrome → render final (h264 padrão). **Três
gerações de compressão** no caminho que interpola.

## A7. Interface

🔍 Uma página de 868 linhas com cinco passos: 1 Enviar · 1.5 Melhorar clipes ·
2 Prévia (com `<Player>` e grade de cenas) · 3 Renderizar · 4 Notas. Mais
`CutTimeline` (177 linhas) e `NotesPanel` (83).

🔍 Seis filtros CSS (`remotion/filters.ts`), transições com presets shader
(WebGL2 via ANGLE — com o motivo documentado), ducking de trilha, modo de áudio
por clipe (`mix`/`replace`/`muted`), zoom lento no frame congelado.

**É mais completo do que aparenta.** Os buracos são de recurso, não de fundação.

---

# PARTE B — O QUE A PESQUISA DIZ

## B1. Upscale — o que rodaria melhor nesta máquina

📚 **Real-ESRGAN tem build `ncnn-vulkan` que roda sem CUDA e sem PyTorch**, em
GPU Intel/AMD/NVIDIA no Windows — *Firme*, fonte primária
([repositório do autor](https://github.com/xinntao/Real-ESRGAN-ncnn-vulkan),
2021-07-31) e confirmação independente
([videoproc, teste em 2026-01-22](https://www.videoproc.com/video-editor/open-source-video-upscaler.htm)).

> **Isto importa muito para nós:** hoje descobrimos que a **cuBLAS não carrega
> nesta máquina** (o Whisper caiu para CPU por causa disso). O caminho Vulkan é
> uma pista completamente diferente e **não depende do que está quebrado.**

📚 **`Video2X` orquestra Real-ESRGAN, Real-CUGAN e RIFE**, decodifica/codifica com
FFmpeg e **não escreve frames intermediários em disco**. Requisito: GPU com
Vulkan de 2012 em diante.

📚 **Real-ESRGAN cintila em movimento** — três fontes independentes. Ele processa
frame a frame e não modela consistência temporal.

📚 **Os modelos que resolvem a cintilação (SeedVR2, FlashVSR) são PyTorch/CUDA,
não Vulkan**, e o requisito de VRAM está em **conflito aberto** entre fontes: uma
diz que cabe em 8 GB com GGUF + BlockSwap + VAE tiling, outra diz 12–16 GB, outra
24 GB+. **Nenhum relato datado de qualquer um dos dois rodando em 8 GB.** O único
relato local datado é numa RTX 5070 Ti de 16 GB a ~2,0 fps.

📚 **480p → 4K é reconstrução, não restauração.** *"the model invents 35 of every
36 pixels"*, *"stylized 4K, not native 4K"*.

📚 **Para vídeo GERADO POR IA, use difusão e não CNN clássico** — três fontes,
mas **todas comerciais e sem medição**. O argumento (vídeo de IA é
out-of-distribution para CNN treinado em degradação real) é coerente; argumento
coerente não é evidência.

📚 **O maior erro de pipeline de upscale é exportar com bitrate de consumidor:**
*"At that bitrate, the encoder throws away much of the detail the upscaler just
invented."* Régua declarada: **H.264 40–60 Mbps para master 4K; H.265 25–40**.

📚 **Ordem: upscale espacial primeiro, interpolação depois.** *"Do spatial
upscaling first, then interpolate, not the reverse."* — **fonte única**, sem
corroboração.

🔍 **Nós fazemos o contrário:** a cadeia de filtros é `minterpolate,scale`.

🧠 **Mas há um argumento de custo do outro lado que a fonte não considera:**
interpolar a 480p é muito mais barato que interpolar a 1080p — inverter a ordem
multiplica o custo do passo mais caro do pipeline por ~5. **Não inverta no
escuro. Teste um clipe nas duas ordens e olhe.**

## B2. Interpolação — RIFE × minterpolate

📚 **O Salomão não achou material.** *"ffmpeg `minterpolate`: ZERO material (...)
RIFE aparece exatamente três vezes, sempre de passagem (...) efeito soap opera:
zero material."* Registro a lacuna em vez de preencher.

📚 Do que achei por fora:
[RIFE](https://github.com/hzwer/ECCV2022-RIFE) é rede neural (IFNet) que estima
fluxo intermediário ponta a ponta, **4 a 27× mais rápido que DAIN/SuperSloMo**,
30+ fps para 2× em 720p numa 2080Ti, e é descrito como livre do *ghosting* e do
borrão típicos da interpolação tradicional. `minterpolate` é estimativa de
movimento por blocos — família anterior.

🧠 **E a pergunta que ninguém respondeu, que é a que mais vale dinheiro:**
**devemos interpolar?** Três motivos para duvidar:

1. **Custo.** É o passo mais caro do pipeline — ~26 min por vídeo de 10 min, toda
   vez.
2. **Estética.** 24 fps é a cadência que o corpus inteiro defende ("cinematic",
   "24fps" na âncora de realismo). Subir para 60 fps é exatamente o que produz o
   *soap opera look*.
3. 🧠 **Técnico, e é o argumento mais forte:** estimativa de movimento por blocos
   pressupõe **movimento rígido**. Vídeo gerado por IA tem *morphing* não rígido —
   textura que nasce e morre entre frames. É o pior caso possível para o
   `minterpolate`, e nada garante que o RIFE se saia bem nele.

> **Isto é pergunta para o Samuel, não decisão minha.** Um teste barato responde:
> o mesmo clipe, com e sem interpolação, lado a lado.

## B3. Reenquadramento 9:16

📚 **`PyAutoFlip`** (MIT, `pip install pyautoflip`, Python 3.10+ e FFmpeg) —
*Firme*, [fonte primária](https://github.com/AhmedHisham1/pyautoflip), 2025-03-28.
Faz exatamente o que o Samuel descreveu:

- **Quem é o relevante:** dois métodos. `detection` (InsightFace para rosto +
  MediaPipe para objetos, com **pesos de prioridade rosto > pessoa > animal >
  texto**) e `saliency` (mapas UNISAL via ONNX Runtime em CPU + rosto). O corte é
  uma **janela de largura fixa centrada no centro de massa da saliência** — não é
  "o maior rosto", é o centro de massa da atenção.
- **Filtro de rosto falso:** descarta rosto pequeno demais — o retrato na parede,
  o pôster ao fundo. 🧠 Para o nosso canal isso importa: cenas de mitologia têm
  estátua, pintura e relevo com rosto.
- **Não tremer:** cena detectada com PySceneDetect → análise por quadros-chave
  **por cena**, não quadro a quadro → **classificação do movimento de câmera em
  ESTACIONÁRIA / PANORÂMICA / RASTREANDO** com suavização de trajetória →
  `--motion-threshold` (0.0 estável, 1.0 permite movimento).
- **Duas pessoas longe demais:** detecta e renderiza **tela dividida em dois
  painéis**.

📚 **O AutoFlip original do Google está declarado como não mantido** — mas quem
diz é o autor da alternativa, e **não há fonte do Google no material**. *Mediana*.

📚 **O README não declara instruções para Windows** — nem que funciona, nem que
não. É a lacuna que decide se dá para usar direto.

## B4. Tipografia para legenda

📚 **[Inter](https://rsms.me/inter/)** — licença **SIL Open Font License**, livre
para uso comercial, altura de x alta, desenhada para tela, gratuita no Google
Fonts. É a recomendação mais segura do ponto de vista de licença.

📚 **Montserrat Bold** aparece como a escolha dominante para conteúdo curto
(Shorts/Reels/TikTok) em 2026 — formas geométricas e bold que aguentam tela
pequena. Também OFL.

📚 O consenso das fontes: **sans-serif, bold, altura de x generosa, contraforma
aberta, diferenciação clara entre caracteres parecidos**. Roboto, Open Sans,
Inter, Montserrat, Poppins, Lato, Source Sans, Noto Sans.

🧠 **Recomendação para o WhoIAm**, e é opinião: **Inter** para a legenda corrida
do vídeo longo (neutra, não disputa com a imagem) e **Montserrat Bold** para o
Short. Para a cartela de local/ano, uma **mono** (JetBrains Mono ou Roboto Mono,
ambas OFL) — split-flap e máquina de escrever só ficam bons em largura fixa,
senão o texto "dança" enquanto digita.

## B5. Split Flap e máquina de escrever no Remotion

📚 O Salomão não achou nada; achei por fora. A regra oficial do Remotion para
efeito de digitação é específica e vale registrar:

> 📚 *"Based on `useCurrentFrame()`, reduce the string character by character (...)
> **Always use string slicing for typewriter effects and never use per-character
> opacity**"* — [remotion-dev/skills](https://github.com/remotion-dev/skills/blob/main/skills/remotion/rules/text-animations.md)

🧠 Split-flap é o mesmo princípio, com um passo a mais: por caractere, um
contador que percorre um alfabeto até parar na letra certa, com atraso escalonado
por índice. Não precisa de biblioteca — `useCurrentFrame` + `interpolate` bastam,
e é determinístico (essencial: o render precisa bater com a prévia).

📚 **`@remotion/captions` existe** (tipo `Caption` padronizado, conversores) e
**`@remotion/google-fonts` também** — 🔍 **nenhum dos dois está instalado** no
`package.json`. Instalados hoje: bundler, cli, media, media-parser, media-utils,
paths, player, renderer, shapes, streaming, studio, transitions, zod-types.

---

# PARTE C — O QUE FAZER, EM ORDEM

Ordenado por **valor ÷ custo**, não por empolgação.

### 1. Consumir as legendas que já existem 🥇

O trabalho pesado está feito e testado. Falta o consumidor: ler `captions.json`,
estender o schema do `load-alignment.ts` (hoje descarta `palavras` e `falas`), e
uma camada `<Captions>` na composição.

**Custo:** baixo. **Ganho:** legenda queimada com tipografia nossa, e o `.srt`
para subir no YouTube já existe de graça.

### 2. Cartela de local/ano no canto inferior esquerdo

Pedido explícito do Samuel: aparece rápido e some, em **split-flap** ou **máquina
de escrever**. Fonte mono, `useCurrentFrame` + `interpolate`, string slicing.

**Onde o dado mora:** 🧠 precisa de decisão — o mais natural é um campo por cena
no `EditPlan` (`location`, `year`), preenchido pelo roteiro. **Perguntar ao
Samuel** se ele quer isso por cena ou só na primeira cena de cada locação.

### 3. Short em 9:16 de verdade

🧠 **Recomendação de arquitetura, e ela evita um erro caro:** **não** rode o
PyAutoFlip como reencode do vídeo pronto. Rode-o (ou só as partes dele) como
**analisador que produz uma trilha de recorte** — um JSON de `{cena, cx, cy,
largura}` — e deixe o **Remotion aplicar o recorte na composição**, com
`width: 1080, height: 1920`.

Três motivos: (a) evita uma geração inteira de recompressão; (b) as legendas e a
cartela são desenhadas **depois** do recorte, então saem nítidas e no lugar certo
do quadro vertical; (c) o `output-resolution.ts` já foi escrito com essa
separação em mente.

**Risco declarado:** o PyAutoFlip não declara suporte a Windows. Verificar antes
de planejar em cima dele.

### 4. Trocar o ASR do alinhador: Vosk → faster-whisper

O próprio `asr.py` já prevê a troca e isola a interface. E **o `faster-whisper`
passou a funcionar nesta máquina hoje** — `large-v3-turbo` em CPU, ~1,5× o tempo
real, com `word_timestamps` disponíveis.

**Ganho:** mais palavras acertadas = mais âncoras = corte de cena e legenda mais
precisos, e a confiança do alinhamento sobe. **Custo:** uma função.

### 5. Declarar a qualidade do encode final

🔍 Hoje `renderMedia` não passa `crf` nem `videoBitrate`. 📚 A fonte é dura sobre
isso ser o erro mais caro. Declarar explicitamente e medir o arquivo de saída.

🧠 E revisar a cadeia de três encodes: dá para o passo de retime virar `-c:v copy`
em alguns casos, ou para o enhance sair em qualidade quase-sem-perda já que ele é
**intermediário**, não entregável.

### 6. Real-ESRGAN ncnn-vulkan como opção de upscale

Não substituir o Lanczos — **acrescentar como escolha**, no mesmo lugar da UI onde
já se escolhe interpolação e alvo de upscale. O Lanczos continua sendo o caminho
rápido e previsível; o Real-ESRGAN entra quando o clipe importa.

⚠️ **Duas advertências que precisam estar na interface:** ele **cintila** em
movimento (três fontes) e o fluxo ncnn autônomo **exige extrair e remontar frames
com FFmpeg**. E 📚 o README primário é de **2021** e declara um bug de "imagem
preta" em alguns PCs — **conferir o estado do repositório antes de baixar**.

### 7. A pergunta da interpolação

Antes de investir em RIFE, responder se **queremos** 60 fps. Teste: um clipe, três
saídas — sem interpolação, `minterpolate`, e (se instalado) RIFE. Olhar.
**É a decisão que mais economiza tempo de máquina, nos dois sentidos.**

---

## D. Ideias de interface que o material sugere

🧠 Tudo aqui é sugestão minha, marcada como tal.

- **Prévia do Short lado a lado com o vídeo cheio** — hoje a prévia é só do plano
  cheio, e o Short é gerado às cegas.
- **Editor de legenda na prévia** — o `captions.json` tem `confianca` por
  legenda; destacar em vermelho as de confiança baixa leva o olho direto ao que o
  ASR errou, em vez de reler tudo.
- **Aviso de frame congelado.** O `align/README.md` já calcula "quanto falta ou
  sobra de clipe" e imprime no terminal. Isso deveria estar na grade de cenas: um
  bloco com 7 s de frame congelado é um problema de produção, e hoje só aparece
  para quem roda o alinhador na mão.
- **Orçamento de tempo antes de renderizar** — com o custo medido de
  interpolação (~79 s por clipe de 15 s), dá para dizer "isto vai levar ~26 min"
  antes de começar, em vez de descobrir depois.
- **Quebrar a página de 868 linhas.** Cinco passos num arquivo só; cada passo já
  é um componente natural.
- **Preset de canal** — filtro, fonte de legenda, posição da cartela e alvo de
  upscale como um preset salvo, em vez de escolher a cada projeto.

---

## E. O QUE NÃO FOI CONFIRMADO

1. **`minterpolate` × RIFE**: nenhuma medição, em nenhuma fonte. Nem qualidade,
   nem velocidade.
2. **Efeito soap opera em vídeo de IA**: zero material.
3. **Qualquer número medido em RTX 3050 de 8 GB.** O mais próximo é uma RTX 3060.
4. **Se SeedVR2/FlashVSR cabem em 8 GB.** Conflito aberto entre três fontes.
5. **PyAutoFlip no Windows.** Não declarado.
6. **Estado atual do repositório Real-ESRGAN-ncnn-vulkan.** Fonte primária de
   2021; a via GitHub não retornou nada nesta coleta.
7. **`ffmpeg scale=lanczos`**: nenhuma das 8 fontes menciona filtro clássico de
   escala uma única vez. Não há base para comparar nosso baseline com nada.
8. **A API exata do `@remotion/captions`** na versão 4.0.495 — a documentação não
   abriu a lista completa. Conferir antes de instalar.


---

## Fechamento parcial — 04/09/2026

**Achados 1 e 2 (os dois de gravidade alta) resolvidos e verificados com render
real**, não só com typecheck: projeto de teste com dois clipes da Medusa,
narração cortada em 24 s e um `captions.json` sintético no formato exato do
align. Saída medida com `ffprobe`: **1080x1920**, legendas queimadas e legíveis
em quadro claro e escuro.

- **Legendas:** `lib/alignment/load-captions.ts` lê o arquivo, elas viajam
  dentro do `EditPlan` (`captions` + `burnCaptions`), e `remotion/Captions.tsx`
  desenha. Ligado no Short, **desligado no vídeo cheio** de propósito — o
  YouTube recebe o `.srt` que o align já escreve, e legenda queimada o
  espectador não desliga.
- **Short 9:16:** `SHORT_RESOLUTION = 1080x1920` em `output-resolution.ts`, com
  o recorte feito na composição (`object-fit:cover` + `cropX` por clipe), como
  a §C3 recomendava — sem reencode.

**Dois defeitos que só o render pegou** (nenhum teste pegaria):

1. A quebra de 42 caracteres do align é para quadro LARGO. No 9:16 ela não
   cabe e cada linha quebrava de novo, com palavra órfã. No vertical o texto
   agora reflui como parágrafo único.
2. O cache do bundle do Remotion é chaveado só no `publicDir` — editar a
   composição não invalidava nada, e o mesmo conserto renderizou frame
   idêntico byte a byte duas vezes. Em desenvolvimento o cache agora é pulado.

**O que continua aberto nesta lista:** §C2 (cartela de local/ano), §C4 (ASR
Vosk → faster-whisper), §C5 (bitrate/CRF no encode final), §C6 (Real-ESRGAN
como opção), §C7 (a pergunta da interpolação) e todo o §D de interface. E o
`cropX` continua 0,5 em tudo: o recorte é centralizado, não segue o
personagem — num dos frames do teste o rosto saiu descentralizado, que é
exatamente o caso que a análise de reenquadramento resolveria.
