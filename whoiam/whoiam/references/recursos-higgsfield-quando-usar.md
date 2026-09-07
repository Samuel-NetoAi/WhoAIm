# Recursos do Higgsfield — QUANDO usar cada um (camada de decisão)

Este arquivo existe por um pedido explícito do usuário (ago/2026): *"eu não sou diretor de cinema,
posso pensar nas cenas, mas nem sempre saberei quando usar esses recursos diversos do Higgsfield —
gostaria que você decidisse qual efeito usar e quando, eles nem sempre estarão nos meus prompts."*

**Regra que governa o arquivo inteiro:** o usuário descreve O QUE ACONTECE. A skill decide QUAL
RECURSO usa e **propõe** — sempre com o porquê e o custo ao lado, sempre no checkpoint, nunca em
silêncio. Recurso proposto sem justificativa dramática é o mesmo default que a
`direcao-cinematografica.md` combate; recurso aplicado sem avisar é gasto de crédito sem
consentimento. Os dois são erro.

**Onde isso entra no fluxo:** na Fase 1, cada bloco recebe uma linha `RECURSOS:` com o que a skill
está propondo e por quê. Bloco sem essa linha (mesmo que seja `RECURSOS: nenhum`) está incompleto.

> A redação anterior dizia *"junto da classificação AÇÃO/SIMPLES"*. ⚫ **Essa classificação foi
> descontinuada em 28/08/2026** — todo bloco sai em Seedance 2.5, 30 s, 480p. A linha `RECURSOS:`
> continua obrigatória; o que sumiu foi a classificação ao lado dela.

Preços: `higgsfield-cinema-studio.md`, seção 2. Tudo que diz [MEDIDO] foi lido via `get_cost`.

---

## 1. OS PARÂMETROS QUE VOCÊ DECIDE EM TODO BLOCO (não são opcionais, são default explícito)

Estes não são "efeitos" — são knobs que existem em toda geração e que alguém decide, mesmo quando
ninguém pensa neles. Se a skill não decidir, o valor de fábrica decide. Declarar sempre:

| Parâmetro | Padrão do canal | Quando fugir do padrão |
|---|---|---|
| `generate_audio` / `sound` | **off** | Nunca, enquanto a decisão de trilha holística valer. Ver `pos-producao.md` §2b. |
| `resolution` (vídeo) | **por bloco, não por canal** — ver abaixo | 480p = 2,5 cr/s · 720p = 6,5 · 1080p = 9,0 |
| `cfg_scale` (Cinema Studio Video, 0–1, padrão 0,5) | **0,7–0,8** | Este canal escreve prompt hiperespecificado de propósito: geometria de relação declarada, população do quadro, pré-ação no painel 1. Aderência baixa joga isso fora e devolve o default bonito. Baixar para ~0,4 só quando o resultado sair rígido/artificial e você quiser dar liberdade de movimento ao modelo. **[A TESTAR — nunca medido no canal]** |
| `genre` (Cinema Studio Video) | deriva da INTENÇÃO DRAMÁTICA | `horror` (ameaça, criatura), `suspense` (espera, ameaça latente), `spectacle` (escala, revelação divina, destruição, impacto colossal), `intimate` (luto, transformação, rosto). **`action` é armadilha — ver abaixo.** `western`/`comedy`: praticamente nunca. |
| `count` (imagem) | **sempre 4** | Nunca. `count:4` custa o mesmo que `count:1` [MEDIDO em 3 modelos]. Gerar imagem única é erro de operação, não economia. |

### O gênero `action` é uma armadilha para este canal

Guia de terceiro (19/08/2026) descreve os gêneros como "motores de física" e diz que `action` induz
**whip pans e trepidação de câmera**. Se for verdade — plausível, não medido —, ele colide de frente
com o "dono do olhar = testemunha invisível" da `direcao-cinematografica.md`, que manda câmera
estática ou movimento lento e deliberado, **sem handheld**, nos blocos de lore.

Então: bloco classificado como `AÇÃO` **não** recebe `genre: action` por default. Ação neste canal é
quase sempre criatura com massa — impacto, esmagamento, algo colossal se movendo —, e isso é
**`spectacle`** ou **`horror`**. `action` fica reservado para perseguição humana em primeira pessoa, se
um dia existir. A confusão vem do nome: o rótulo `AÇÃO` da nossa classificação é sobre CUSTO e
modelo, não sobre o gênero da interface.
| `speedramp` | **linear** por padrão | Ver seção 2. É o recurso mais subutilizado da plataforma. |
| `multi_shots` | **true** quando o bloco tem 2+ shots | Não custa a mais [MEDIDO: 24 cr com e sem]. Deixar `false` só em plano-sequência declarado (luta corpo a corpo, elemento isolado). |
| `bitrate_mode` | standard | `high` no bloco final/clímax se houver banding visível em gradiente escuro (este canal é quase todo penumbra — é onde banding aparece). |

---

## 1b. RESOLUÇÃO DE VÍDEO — decisão permanente do canal

> **INSTRUÇÃO PERMANENTE DO USUÁRIO, registrada em 19/08/2026 (deveria estar salva antes e não
> estava — falha da skill):**
> **"Sempre usar a menor qualidade na geração, para os créditos durarem mais; o upscale vem depois,
> na pós."** Isso não é preferência a ser reconfirmada a cada vídeo — é o padrão do canal. Só se
> discute de novo se um teste real derrubar.
>
> A skill fixou 720p sozinha em ago/2026, sem perguntar. Errado duas vezes: por não perguntar, e por
> contrariar uma instrução que já existia.

**Preços medidos: 480p = 2,5 cr/s · 720p = 6,5 · 1080p = 9,0.** Um vídeo de 10 min sai por 1.500,
3.900 ou 5.400 créditos.

### A economia do "gerar baixo + upscale" — a conta que decide

A pergunta certa não é "upscale é tão bom quanto nativo" (não é, ver abaixo) — é **quanto custa cada
caminho pelo mesmo segundo de vídeo**:

- Subir de 480p para 720p na geração custa **+4,0 créditos Higgsfield por segundo**.
- O upscale observado na interface (Kairogen, 4K, com interpolação de frames a 120fps) custou
  **6 créditos para 2 segundos = 3 cr/s Kairogen**. Crédito Kairogen vale **R$ 0,1448** [MEDIDO via
  `get_me_context`, plano Precision] → **≈ R$ 0,43 por segundo de vídeo**.
- 4 créditos Higgsfield, no Ultra, saem a ~US$ 0,17/s.

**A conclusão inverte o senso comum: o upscale sai mais barato que gerar mais alto**, mesmo na
configuração cara que apareceu no print. Ou seja, **a instrução permanente do usuário está
economicamente certa** — e a skill estava errada ao empurrar 720p como padrão.

**MAS — o achado que corta o custo pela metade de novo:** o print mostrava **interpolação de frames
ligada, saída a 120fps**. Isso é desperdício duplo neste canal: o YouTube entrega a 24/30/60 (os
120fps são jogados fora) e interpolar material de IA cria morphing nas bordas — exatamente o artefato
que a âncora de realismo combate. **Desligar a interpolação antes de qualquer conta de upscale.**
[A MEDIR: quanto o custo cai com ela desligada — teste de 30 segundos, upscalar um clipe de 10s com e
sem, e ler o número de créditos.]

**O limite que ainda derruba tudo:** upscale cobrado POR SEGUNDO não escala para vídeo de 10 min.
A 3 cr/s, 600s = 1.800 créditos Kairogen — mais que o plano mensal inteiro dele (1.720). Se o upscale
do fluxo for por segundo na nuvem, ele precisa ser barato o suficiente ou o vídeo precisa ser mais
curto. **Upscale de custo fixo resolve isso de vez** e é a única forma de o custo de upscale ficar
independente da duração.

### O STUDIO — o editor próprio do usuário (registrado 19/08/2026)

"O Studio" é um **site que o próprio usuário desenvolveu com Claude Code**. Ele faz: edição, legendas
sobrepostas ao vídeo (para ver onde a narração encaixa), filtros, biblioteca de músicas, **interpolação
de frames e upscale**. A skill NÃO tem acesso ao código dele.

Isso muda a arquitetura do orçamento, porque um upscale próprio tem **custo marginal zero por
segundo** — que é exatamente a condição que faz "gerar em 480p e subir depois" ser definitivamente a
melhor estratégia. **Mas o usuário declarou que a interpolação e o upscale do Studio nunca foram
usados num vídeo completo — não se sabe se funcionam.**

**Portanto: o Studio está no caminho crítico de uma decisão de milhares de créditos e está NÃO
TESTADO.** Nada na skill pode assumir que ele funciona. Enquanto não houver veredito:
- o padrão de geração continua 480p (instrução permanente);
- o ECU da revelação sai em **720p** e passa pelo upscale do Studio depois (decisão do usuário,
  28/08/2026 — ver seção 1c/vitrine abaixo para o porquê e o custo);
- o plano B de upscale é o Kairogen/Higgsfield por segundo, com o custo que isso implica.

### AUDITADO — o que o Studio faz de fato (código lido em 19/08/2026)

**Repositório:** `github.com/Samuel-NetoAi/WhoAIm`, pasta `studio/`. Stack: **Next.js 16 + Remotion
4.0.495**, render server-side via `@remotion/renderer`, pós-processo por ffmpeg local
(`studio/bin/ffmpeg.exe`, build completo, Windows). Sem ONNX, sem ffmpeg.wasm, sem cliente de
Replicate/fal — **nada roda no navegador do usuário e nada é cobrado por segundo.** Custo marginal de
pós-processamento: **zero.**

| Peça | O que é de fato | Veredito |
|---|---|---|
| **Upscale** (`lib/render/postprocess.ts`) | `scale=iw*2:ih*2:flags=lanczos` | **Reamostragem clássica, NÃO é modelo aprendido. Não inventa textura.** O próprio comentário do código diz: *"Real-ESRGAN (AI) is the planned upgrade for detail synthesis"* |
| **Resolução de saída** (`lib/edit-plan/output-resolution.ts`) | composição renderiza com no mínimo **1080p no lado curto**, independente do clipe; o clipe de 480p é escalado UMA vez pelo compositor | **Boa decisão de engenharia** — mantém legenda e overlay nítidos, que rasterizados a 480p seriam irrecuperáveis. Mas o comentário é explícito: *"This does NOT invent detail in the footage."* |
| **Interpolação** | ffmpeg `minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1` | Compensação de movimento clássica, **não é RIFE**. Lenta (CPU) e o próprio `SUGESTOES.md` registra que *"borra em movimento rápido"* |

**A CONCLUSÃO QUE MUDA A EXPECTATIVA (não o orçamento):** hoje, "480p + upscale do Studio" entrega
**detalhe de 480p esticado para 1080p**, com bordas nítidas e nenhuma micro-textura nova. A economia
continua real (US$ 64 contra US$ 164 por vídeo); o que não existe é a recuperação de textura que a
palavra "upscale" sugere. A instrução permanente de gerar baixo **continua valendo** — mas ela precisa
da proteção do bloco nativo, não do upscale.

### O BLOCO-VITRINE e o ENVELOPE — como a previsão de 4 vídeos/mês para de balançar

Problema levantado pelo usuário (19/08/2026, e ele está certo): se o número de blocos em alta
resolução varia por vídeo — um tem 3, outro tem 1 — **a previsão mensal deixa de existir**. Não dá
para planejar calendário em cima de um custo que muda a cada criatura.

**Solução em duas camadas, e a ordem importa:**

**1. ENVELOPE DE CRÉDITO POR VÍDEO — é isto que garante a previsão.**
Fixa-se o dinheiro, não a contagem de cenas caras. Meta de 4 vídeos/mês em 9.000 créditos =
**2.250 créditos por vídeo (~US$ 68)**. Toda alocação acontece dentro do envelope: se uma criatura
pedir duas vitrines, a skill compensa em outro lugar (encurta um bloco, troca 1080p por 720p na
segunda vitrine, corta um bloco de transição) — nunca estoura o envelope em silêncio. É assim que
orçamento de produção funciona de verdade: trava-se a verba, não a lista de planos caros.
Rodar: `python3 scripts/orcamento.py --envelope --saldo 9000 --meta-videos 4 --duracao-video 480`

**2. BLOCO-VITRINE — a alocação padrão dentro do envelope.**
Um bloco por vídeo, ~30s, extreme close-up da criatura. **Decisão do usuário (28/08/2026): gerado em
720p e upscalado depois no Studio** (não 1080p nativo) — meio-termo entre o custo do 1080p e a perda
de detalhe do 480p num plano onde textura é o ponto inteiro. Além de resolver a textura, vira
**padrão editorial**: a "revelação" no mesmo lugar de todo vídeo é exatamente o tipo de repetição que
a `postagem` quer (o curso manda repetir o que funciona).
**Sempre plano único, um só prompt de cena — nunca multi-shot.** Normalmente é o momento da
revelação da criatura. (Correção 28/08/2026: a versão anterior deste arquivo recomendava 2–3 shots
dentro do bloco pra não cansar 30s num plano só — o usuário decidiu o oposto: a vitrine é
deliberadamente 1 prompt, 1 plano, do início ao fim.)

**A CONTA — e o resultado é contraintuitivo** (10 min = 600s, 8 min = 480s, resto em 480p):

| Vídeo | Vitrine | Custo | Retrabalho máx. p/ 4 vídeos/mês | 4/mês? |
|---|---|---|---|---|
| 10 min | 30s @1080p | 1.695 | **×1,33** | ✗ (3,79) |
| 10 min | 30s @720p | 1.620 | ×1,39 | ✗ (3,97) |
| 9 min | 30s @1080p | 1.545 | ×1,46 | ✓ (4,16) |
| **8 min** | **30s @1080p** | **1.395** | **×1,61** | **✓ (4,61)** |
| 8 min | 30s @720p | 1.320 | ×1,70 | ✓ (4,87) |

**A vitrine não é o que decide.** 1080p contra 720p nela são 75 créditos — 3% do vídeo. Quem decide
são **a duração do vídeo** e **o fator de retrabalho**, que ninguém mediu ainda. Por isso:

- **Duração-alvo do canal: 8–9 min, não 10.** Continua dentro da faixa que a `postagem` exige (8–12 min,
  acima de 8 libera anúncio intermediário) e é o que compra margem: a 8 min você pode regerar 61% dos
  blocos e ainda fechar 4/mês; a 10 min só 33%.
- **A vitrine sai em 720p + upscale do Studio, sem culpa.** Mais barata que 1080p nativo (195 cr
  contra 270 — economia de 75 cr, ~28%) e ainda assim acima do 480p do resto do vídeo.
- **A primeira coisa a medir no vídeo-piloto é o retrabalho**, não a qualidade da vitrine. Ele é a
  única variável que ainda pode derrubar a previsão.

### O que fazer com isso

1. **Manter 480p como padrão de geração.** A economia é real e a maioria dos blocos (plano aberto,
   atmosfera, silhueta) não tem micro-textura a perder — Lanczos + composição em 1080p resolve.
2. **ECU da revelação em 720p, sempre com upscale do Studio em cima (decisão do usuário, 28/08/2026).**
   Sai de "1080p nativo, sem exceção" pra um meio-termo: mais detalhe de base que o 480p padrão, mais
   barato que 1080p nativo. Custa ~195 créditos (30s @720p) antes do upscale, que é grátis no Studio.
3. **Interpolação: DESLIGADA.** Três motivos somados — o YouTube não precisa de 60fps neste conteúdo,
   o minterpolate borra movimento rápido (registrado pelo próprio projeto), e interpolar material de
   IA acrescenta morphing. Não gastar tempo de CPU nisso.
4. **Real-ESRGAN vale a pena, mas COMO FERRAMENTA PONTUAL, não como passe do vídeo inteiro.**
   `PLANO-ALPHA.md` §181 já tem o roteiro (binário `realesrgan-ncnn-vulkan` em `studio\bin\`, GPU
   NVIDIA presente, gratuito). Duas ressalvas que o plano não menciona:
   - **Cintilação temporal:** Real-ESRGAN sobe frame a frame, sem consciência do frame vizinho —
     texturas "fervem" entre quadros. Num canal que vende pele e escama, isso pode ficar PIOR que a
     suavidade limpa do Lanczos. Testar antes de adotar.
   - **Escala:** 10 min a 30fps = 18.000 frames, com dezenas de GB de PNG intermediário e horas de
     GPU. Rodar num vídeo inteiro é inviável na prática; rodar **só nos blocos de close-up**
     (10–15% dos frames) é viável e é onde o ganho existe.
5. **Se um dia a textura precisar ser resolvida no vídeo inteiro**, a resposta é upscaler com
   consciência temporal (classe Topaz), não Real-ESRGAN frame a frame.

**O TESTE QUE FECHA A ARQUITETURA INTEIRA — 345 créditos:** gerar o MESMO bloco em 480p (75 cr) e em
1080p nativo (270 cr); passar o de 480p pelo upscale do Studio; assistir os dois **na TV**, lado a
lado, no bloco de ECU da criatura. Isso responde de uma vez: se o Studio serve, quanto o upscale
recupera, e se a instrução permanente se sustenta na prática. É o teste com maior retorno por crédito
de todo o pipeline — vale ~US$ 100 por vídeo.

### O que o upscale NÃO devolve — e o único bloco onde isso importa

Upscaler reconstrói detalhe plausível, não restaura o que nunca foi capturado. Em 480p o próprio
modelo de difusão aloca menos estrutura fina: ele decide onde a escama termina com menos informação.
O Topaz depois inventa a micro-textura por estatística — ele não sabe que aquilo é escama, sabe que
"tem uma borda aqui, dá para deixar nítida".

Isso importa pouco em plano aberto (a criatura ocupa 100px de qualquer jeito, nativo ou não) e importa
**muito** em EXTREME CLOSE-UP, onde o rosto/pele ocupa o quadro inteiro: subir um rosto que só teve
360 linhas de informação para 4K é exatamente de onde vem o aspecto ceroso.

**O usuário já resolveu isso sozinho ao dizer que a revelação do ser sempre terá um extreme close-up
para abusar da textura.** Esse é o bloco — e é UM bloco por vídeo — que foge do padrão.

| Tipo de bloco | Resolução de geração | Por quê |
|---|---|---|
| **Tudo, por padrão** | **480p** | instrução permanente; o upscale cobre |
| **ECU da revelação da criatura** (e qualquer insert de textura que o roteiro marque como vitrine) | **720p, sempre com upscale do Studio depois** | decisão do usuário (28/08/2026); meio-termo entre custo e detalhe — 30s a 720p = 195 créditos, upscale grátis |
| Frame que vira thumbnail ou Short | 1080p, ou gerar a thumb como IMAGEM (mais barato e melhor) | 480p não dá pixel para thumb |

A skill propõe a resolução bloco a bloco no checkpoint e o total vai para o orçamento. O padrão é
480p; fugir dele exige justificativa escrita, não o contrário.

**Teste que fecha a questão, 270 créditos:** o MESMO bloco em 480p+upscale e em 720p nativo, mesma
referência e mesmo prompt, assistidos **na TV**. Registrar o veredito na seção 7 do
`higgsfield-cinema-studio.md`.

---

## 2. SPEEDRAMP — o recurso que o usuário nunca vai pedir e que muda mais o resultado

O Cinema Studio Video tem rampa de velocidade nativa: `auto · linear · slowmo · speedup · impact`.
Isso é decisão de montagem, não de prompt, e é exatamente o tipo de coisa que ele pediu para a skill
assumir. Mapeamento:

| Situação na cena | speedramp | Por quê |
|---|---|---|
| Impacto de criatura, garra que fecha, corpo que atinge o chão, portão que arrebenta | **impact** | O ramp desacelera no frame do contato e acelera na saída — é o que vende peso e massa. A `direcao-cinematografica.md` já pede "reação do ambiente" no follow-through; o impact ramp é a versão temporal disso. |
| Revelação da criatura, primeiro olhar, a coisa se erguendo | **slowmo** | Massa grande move devagar (regra da anatomia do movimento). Slowmo entrega isso sem gastar segundos de prompt pedindo "slowly". |
| Perseguição, fuga, algo cruzando o quadro | **speedup** | Comprime o deslocamento sem cortar. |
| Contemplativo, estabelecimento, luto, plano parado | **linear** | Rampa em cena parada chama atenção para si mesma. |
| Bloco de transformação | **slowmo** no shot do pico, `linear` no resto | A exceção de transformação da heurística rege RITMO — o ramp é a ferramenta certa para ela. |

Não empilhar: **um ramp por bloco.** Dois ramps no mesmo clipe leem como videoclipe, não como
documentário — e o registro do canal é documental sombrio.

---

## 3. TABELA DE DECISÃO — gatilho na cena → recurso

Leia como: *se a cena descrita pelo usuário contém X, a skill propõe Y.*

| O que o usuário descreveu | Recurso a propor | Custo | Cuidado |
|---|---|---|---|
| Metamorfose, transformação, "ele vira", "a pele se abre" | **`end_image`** — gerar o painel do estado FINAL como imagem avulsa e passar como frame final | +1–2 cr (a imagem) | Em multi-shot com personagens o end frame pode ficar indisponível — **[A CONFIRMAR]**. Se ficar, usar bloco de shot único. |
| Deslocamento grande entre dois estados difíceis de descrever ("do cais até o convés") | **`end_image`** | +1–2 cr | Mesma ressalva. |
| Bloco ficou 2–4s curto na montagem | **`video_extension`** (`forward`) | cobrado pela extensão | Mais barato que regerar o bloco inteiro. **[A TESTAR]** |
| Dois blocos consecutivos que deveriam ser contínuos, não corte seco | **`video_extension`** em vez de gerar o segundo do zero | idem | **[A TESTAR]** |
| Bloco quase certo, erro pontual ("a mão está errada", "tirar o objeto") | **`seedance_2_5` mode `video_edit`** | cobrado pela duração do vídeo | Compare com o custo de regerar: em bloco de 30s, editar e regerar podem custar quase igual. |
| Personagem/criatura recorrente | **Element** (`show_reference_elements`) | grátis | Sempre. É a Fase 1, não um extra. |
| Ambiente que se repete em 2+ blocos | **Element de environment** | grátis | Sempre. |
| Criatura precisa repetir uma coreografia específica que já existe em vídeo de referência | **`motion_control`** (Kling 3.0) | 720p/1080p | Só com clipe de referência que o usuário tenha direito de usar. Não usar filme de terceiro como driving clip. |
| Painel crítico ficou pequeno demais na folha | **gerar avulso** + `upscale_image` se for virar thumbnail | 1–2 cr + upscale | Já é padrão no bloco de 30s. |
| Thumbnail | `generate_image` + workflow `youtube-thumbnail-generator` + `upscale_image` 4K | 1–2 cr + upscale | Regras da `postagem` vencem as do workflow em conflito. |
| Folha de storyboard boa mas com enquadramento apertado | **`outpaint_image`** | barato | Mais barato que regerar a folha inteira; conferir se a calha não vazou. |
| Vídeo final com ruído/artefato de IA | **`upscale_video`** provider `bytedance`, preset **`aigc`** | por duração | O preset `aigc` existe exatamente para saída de IA. Aplicar no vídeo MONTADO, uma vez — não bloco a bloco. |
| Short vertical 9:16 | **NÃO usar `reframe` do Higgsfield** | **145 cr para 30s/720p [MEDIDO]** | Quase o preço de gerar o bloco. Reenquadrar com ffmpeg (`conversao-midia.md`) ou no CapCut custa zero. Esta é a economia mais óbvia do arquivo. |
| Cortar Shorts do vídeo já publicado | `personal_clipper` / `clipify` (URL do YouTube → cortes) | — | Alternativa ao Documento 6 manual. **[A TESTAR]** |
| Criatura precisa aparecer em ângulo que o model sheet não cobre | gerar painel avulso citando o Element, não regerar o model sheet | 1–2 cr | Model sheet aprovado é contrato; não mexer nele. |

---

## 3b. ASPECT RATIO 21:9 — a decisão que o guia trata como óbvia e não é

O guia de terceiro recomenda 21:9 anamórfico como sinal de "produção de alto nível". Medi: **21:9
custa exatamente o mesmo que 16:9** (195 cr para 30s em 720p). O preço não é em crédito.

O preço é em **tela**. O player do YouTube é 16:9: um vídeo 21:9 entra letterboxed e a imagem
ocupa ~75% da altura disponível. Num canal cujo material da `postagem` gira em torno de legibilidade
em tela pequena — thumb que precisa funcionar a 120px, criatura reconhecível de relance — abrir mão
de um quarto da altura no celular é uma escolha com custo real. E reaproveitar um 21:9 num Short 9:16
é pior ainda: sobra quase nada de altura para recortar.

Os dois lados, honestamente:
- **A favor:** o letterbox é um sinal de linguagem. Muitos canais dark cinematográficos usam, e
  funciona — a barra preta comunica "isto é cinema" antes de qualquer plano aparecer.
- **Contra:** a promessa deste canal é criatura em detalhe fotográfico. Detalhe mora em pixel, e o
  21:9 entrega menos pixel de assunto na tela onde a maioria assiste.

**Recomendação: 16:9 como padrão do canal; 21:9 só se testado em UM vídeo inteiro e comparado na
retenção.** Meia medida (uns blocos em 21:9, outros em 16:9) é o pior dos mundos — quebra o padrão
visual que a `postagem` manda manter. Decisão é do usuário; o que não pode é adotar por soar
profissional.

---

## 4. OS PRESETS — a maior armadilha da plataforma para ESTE canal

`presets_show` devolve ~60 presets prontos (EARTH ZOOM, ORBIT 360, ICE STATUE, ACTION FIGURE,
STICKER PEEL, CLAY FIGURINE, SELFIE TWIN, RED CARPET, PAPARAZZI, KUNG FU HIT…). São potentes e
tentadores. **A maioria esmagadora é veneno para o WhoIAm:** foram desenhados para conteúdo viral de
selfie/UGC e carregam uma assinatura visual (mão que entra no quadro, transformação em brinquedo,
estética de jogo retrô, VHS, broadcast esportivo) que quebra na hora a promessa central do canal —
"criatura física fotografada, nunca fantasy art, nunca estilizado".

**Regra dura:** preset só entra se ele passar nos três testes, e a skill escreve os três no
checkpoint:
1. O resultado continua parecendo **filmagem real**, não efeito?
2. Ele serve a **intenção dramática do bloco**, ou só é bonito?
3. Ele existe sem a "mão do criador" (nada de alguém pegando o sujeito, sticker, boneco, tela de
   menu de jogo)?

Os poucos candidatos plausíveis, e ainda assim como **teste**, nunca como padrão:
- **ORBIT 360** — revelação de criatura estática, se a órbita for lenta e a criatura maciça.
- **EARTH ZOOM** (in/out) — abertura de vídeo com escala cósmica/geográfica; combina com abertura
  de lore ("num lugar do mundo…"). Risco: cheira a template.
- **STORM GIANT** — escala colossal emergindo. Risco alto de estética blockbuster.
- **DISINTEGRATION** — desfecho de criatura que se desfaz.

Todo o resto: **não propor.** Se o usuário pedir um pelo nome, aplicar — é o canal dele — mas
apontar em uma frase qual das três perguntas o preset reprova.

---

## 5. MODELO: quando fugir do padrão (padrão de roteamento descontinuado, 28/08/2026)

> O roteamento `AÇÃO → Seedance 2.5` / `SIMPLES → Cinema Studio Video` foi **descontinuado** por
> decisão do usuário — hoje o padrão é **sempre Seedance 2.5, sempre 30s, sempre 480p** (ver
> `higgsfield-cinema-studio.md` seção 3 e `SKILL.md` Fase 1 Passo 4). As linhas abaixo continuam
> valendo como EXCEÇÕES ao Seedance 2.5, não como um segundo braço de um roteamento por custo.

Exceções que a skill deve propor por conta própria:

- **Criatura precisa falar / boca sincronizada:** nenhum dos dois. É `video_speak`/dublagem em pós,
  ou a cena se resolve sem mostrar a boca — que é o padrão do canal de qualquer jeito (narração
  dissociada).
- **Bloco com 2 personagens em relação complexa e a consistência de rosto está falhando:**
  `minimax_h3` (keyframes + referências, 2K) ou `kling3_0` como plano B. Registrar o resultado.
- **Bloco puramente atmosférico sem criatura nem personagem** (céu, mar, fogo, névoa), se o usuário
  quiser reabrir a possibilidade de economizar: Cinema Studio Video é mais barato, mas isso volta a
  ser exceção pontual proposta e aprovada, não default do canal.

---

## 6. O QUE NÃO EXISTE VIA MCP (para não prometer)

Correção de um erro de leitura anterior desta skill: **os modelos do Cinema Studio ESTÃO acessíveis
por MCP** — `cinematic_studio_video_v2` (vídeo) e `cinematic_studio_2_5` (imagem), com `genre`,
`mode`, `sound`, `speedramp`, `multi_shots`, `multi_shot_mode`, `cfg_scale` e `preset_id`. O que
**não** vem pelo MCP é a camada de interface do Cinema Studio 4.0:

- Era (60s/80s/90s/2000s/2020s), tipo de câmera (35mm/8mm/DV), lente (anamórfica, halation…),
  abertura (f/1.4 / f/4 / f/11), roda de emoção por personagem, paleta nomeada, AI Cast, os 30+
  movimentos de câmera da biblioteca da UI;
- os 30s do modelo nativo do Cinema Studio (via MCP ele para em 12s);
- os benefícios "Unlimited" e "Free Gens" do plano, que por regra do Higgsfield só valem no site.

Consequência prática no modo híbrido: o que a skill **pode executar** (imagens, Elements, orçamento)
ela executa; o que depende da UI vira **ficha de controles** para o usuário aplicar. E o que existe
nos dois lugares (gênero, speedramp, multi-shot, cfg_scale) a skill decide e escreve na ficha, para
o valor ser o mesmo independente de onde o vídeo for gerado.

---

## 7. REGISTRO — o que foi proposto, aplicado e o que deu

Sem isto, a camada de decisão vira palpite reciclado. Uma linha por uso real:

| Data | Bloco | Recurso proposto | Aceito? | Resultado | Manter na tabela? |
|---|---|---|---|---|---|
| — | — | — | — | — | — |
