# Regras de produção de vídeo — WhoIAm

> Atualizado em **2026-08-28**. Substitui o entendimento anterior sobre
> resolução, storyboard e formato de prompt.
>
> **Origem de cada coisa está marcada.** Não é tudo do mesmo peso:
> 🟢 catálogo ao vivo da plataforma · 🔵 medido na nossa produção ·
> 🟡 observado em 62 projetos da coleção Higgsfield ·
> 🎥 aula em vídeo sobre Seedance 2.5 (transcrição completa em
> `D:\Agentes\SALOMAO\estudos\video-seedance-2-5\`) ·
> 🎓 **material oficial da Higgsfield Academy** (higgsfield.ai/academy), lido em 2026-09-02.
> É o fabricante falando da própria ferramenta: mais forte que 🟡, mais fraco que 🔵 para
> qualquer número de custo. Dossiê completo em `ACADEMY-HIGGSFIELD-2026-09-02.md` ·
> ⚫ **decisão do Samuel** — não é achado, é escolha dele
>
> ⚠️ **Calibragem da Academy:** eles demonstram em Seedance 2.0 / 4K; nós rodamos Seedance 2.5 a
> 480p + upscale local. **Método atravessa. Número não atravessa.** Nada de lá toca a §1.

---

## 1. RESOLUÇÃO — a regra que não se negocia

> ### Toda chamada de vídeo escreve `resolution: "480p"`, por extenso.

🟢 **480p existe.** Consulta ao catálogo de modelos em 2026-08-27: é oferecido
por Seedance 2.5, Seedance 2.0, Seedance 2.0 Mini, Seedance 1.5 Pro, Wan 3.0,
Wan 3.0 Prime, Grok Video 1.5, Cinema Studio 3.0, Marketing Studio e Ad
Multiplier.

🟢 **E o padrão de `resolution` é `720p` em TODOS eles. Sem exceção.**

> **Chamada que não escreve a resolução recebe 720p e cobra 720p — sem erro,
> sem aviso, sem confirmação.** Não basta a receita *dizer* 480p no texto ao
> redor: o parâmetro tem que estar escrito na chamada.

### Por que nunca subir

🔵 Medido, Seedance 2.5 · 30 s:

| | Créditos | vs. 480p | Vídeos de 10 min por mês (3.000 cr, retrabalho ×1,4) |
|---|---|---|---|
| **480p** | **75** | — | **1,43** |
| 720p | 195 | **2,6×** | 0,55 |
| 1080p | 270 | **3,6×** | 0,40 |

**Subir a resolução não encarece o vídeo — apaga o vídeo.** A 720p não sai nem
um por mês.

### Modelos FORA da receita (não oferecem 480p)

🟢 FLUX 3 Video · Kling 3.0 Turbo · Kling 2.6 · Kling v3.0 · Wan 2.6 ·
MiniMax H3 (só 2K) · Gemini Omni (só 720p) · Veo 3 / 3.1 / 3.1 Lite ·
Happy Horse. **Por melhor que seja o resultado deles.**

🟢 **Trava de fábrica:** *Seedance 2.0 Mini* oferece 480p e 720p e nada mais.
Não chega a 1080p nem a 4K nem por engano.

### ⚠️ A armadilha do `turbo` — descoberta em 2026-09-02

🟢 **No Kairogen, o Seedance 2.5 tem um parâmetro `turbo` (default `false`) cujo texto de ajuda
diz, literalmente: *"Geração mais rápida; restringe a resolução a 720p/1080p."*** A tabela de
preço do próprio modelo confirma: as condições com `turbo: true` só existem para 720p e 1080p —
**não há linha de 480p com turbo ligado.**

> **Ligar `turbo` apaga o 480p sem aviso e faz a chamada cair no preço de 720p — 2,6×.**
> É exatamente o mesmo modo de falhar que esta seção existe para impedir, só que por outra porta.
> **`turbo` fica desligado. Sempre.** Se algum dia houver motivo para ligar, ele custa 2,6× e
> precisa ser decidido como gasto, não escolhido como "mais rápido".

🟢 **Escopo, medido:** isto é do **Kairogen**. O catálogo do Higgsfield via MCP **não expõe
`turbo`** no `seedance_2_5` — lá os parâmetros são `mode`, `duration`, `resolution`,
`generate_audio`, `bitrate_mode` e `extension_mode`. Ou seja: a armadilha existe numa das duas
superfícies, não nas duas. **Conferir antes de assumir que a chamada está protegida.**

### Duas frases da aula que NÃO contradizem isto

🎥 A aula diz *"you can only do 720p for now"*. **Contexto:** era o teto da
modalidade de **30 segundos** naquela data — não afirma que 480p não exista, e
o catálogo ao vivo confirma que existe.

🎥 A aula diz *"Even though it's 720p, it just looks the most realistic"*.
**Contexto: ele está comparando MODELOS** — Seedance 2.5 contra Seedance 2 e
Kling — não resoluções. Ler isso como "use 720p" é distorcer a frase.

🎥 E ele mesmo confirma o nosso caminho: *"you still have to upscale this to get
this in a better version"*. **Gerar em 480p e fazer upscale local** é o que a
aula descreve como prática normal — e o upscale roda na RTX 3050 da casa,
custando **zero crédito**.

---

## 2. STORYBOARD — o que muda, e o que NÃO muda

⚫ **Decisão do Samuel: não vamos produzir storyboard como artefato separado.**

> **Isto é escolha dele, não conclusão do estudo.** As perguntas P2 e P3 —
> "descrição minuciosa vs. personagem e cenário constantes" e "storyboard rígido
> ajuda ou atrapalha" — **ainda não foram respondidas**. Está registrado assim
> de propósito: quando o estudo responder, ou confirma ou desmente, e ninguém
> vai confundir a decisão com evidência.

### O que a aula mostra, e é uma nuance importante

🎥 O formato avançado de prompt do Seedance 2.5 tem **as duas coisas dentro do
mesmo prompt**:

- um bloco de **continuidade** — *"Character A, what they look like and what
  they wear **the whole way through**"* — que é exatamente o personagem
  constante que o Samuel propôs;
- e um bloco de **stages**, onde cada plano recebe **segundo de início, um nome,
  o que acontece e como está enquadrado**.

**Ou seja: o enquadramento por plano não desaparece — ele muda de lugar.** Sai
de um documento separado e entra no próprio prompt, como "stage".

**Leitura prática:** abandonar o storyboard como *entregável* está sustentado.
Abandonar a *descrição de enquadramento por plano* **não está** — a aula mostra
o oposto, e chama isso de pensar como diretor.

🎥 A aula é explícita sobre o custo de não pensar: *"The process here is a lot
more complex and a lot more time consuming than just using this like a slot
machine. **You don't want to do that anymore.** You just want to be aware
because you're spending good amount of money on each generation."*

---

## 3. O FORMATO DE PROMPT DO SEEDANCE 2.5

🎥 Dois formatos. O segundo é o que ele usa na maior parte do trabalho sério.

### Formato simples

Contexto das referências (*"Image one is a guy in his mid-20s…"*, *"Audio one is
a voice reference"*) → contexto de cena (onde, quem, é plano contínuo?) →
detalhes técnicos (lente, profundidade de campo, grain) → idioma e sotaque do
diálogo → descrição do que acontece **em cada corte** (cut one, cut two…), sem
marcar segundos.

### Formato avançado — a ordem importa

| # | Bloco | O que vai dentro |
|---|---|---|
| 1 | **GOAL** | o que faz este vídeo ser um sucesso; duração (opcional — dá para escolher no gerador) |
| 2 | **REFERENCES** | o que cada referência é. **Agrupar** as que forem do mesmo personagem/objeto em ângulos diferentes |
| 3 | **CONTINUITY** | Personagem A: aparência e roupa **do começo ao fim**. Personagem B: idem. Depois a cena/locação |
| 4 | **STAGES** | por plano: **segundo de início · um NOME para o segmento · o que acontece · como está enquadrado** |
| 5 | **LOOK** | nitidez, formato, cor, grain, luz, sombra, clima |
| 6 | **CAMERA + PERFORMANCE** | movimento e atuação |
| 7 | **NEGATIVES** | *"do not include brand logos, extra people, text on screen"* |

🎥 **Teto de referências: 50 referências, sendo até 30 imagens.** É muito, e é o
que sustenta personagem constante sem storyboard separado.

🟢 **A conta das 50 fecha, confirmada no schema em 2026-09-02:** 30 imagens + 10 vídeos + 10
áudios, com vídeos e áudios limitados a 30 s no total **em cada categoria**.

> 🟢 **Rotear um bloco para o Seedance 2.0 por preço custaria 26 âncoras.** O 2.0 aceita **só 4
> imagens** de referência (contra 30 do 2.5) e para em **15 s** (contra 30 s).
>
> **Não há nada a recalcular:** ⚫ o roteamento de modelo por bloco **já foi descontinuado pelo
> Samuel em 28/08/2026** (todo bloco sai em Seedance 2.5, 30 s, 480p). Este número entra como
> *reforço* daquela decisão — o roteamento barato custaria consistência de personagem, não só
> crédito —, não como pendência aberta.

🎓 **4K no Seedance 2.5 é upscale, não geração nativa.** O guia oficial diz *"the model generates
natively up to 1080p"*, e o catálogo oferece 4K assim mesmo. Reforça a §1: gerar baixo e subir
depois é o que a própria ferramenta faz por dentro — só que a nossa RTX 3050 faz de graça.

🎥 **Nomear cada stage** é detalhe barato e que aparece no método dele — dá ao
modelo um identificador por segmento em vez de um bloco de texto corrido.

### 🟡 Cada REFERÊNCIA declara PAPEL, EXCLUSÃO e GRAU (set/2026)

**Por que estávamos errados:** o nosso bloco REFERENCES dizia **o que cada referência é**
("IMAGE 1 é o model sheet do Teseu"). Não dizia **o que tomar dela**, **o que não tomar**, nem
**com que força**. Resultado: o modelo decidia sozinho os três — e o fundo de estúdio da folha
vazava para a cena (ver `model-sheet-storyboard.md`, "EXCLUSÃO DE FOLHA").

Três campos por referência, não um:

| Campo | O que escrever |
|---|---|
| **Papel** | `@Image 1 defines Teseu's face and proportions` |
| **Exclusão** | `Do not take the studio backdrop, the sheet layout, the section labels or the palette strip` |
| **Grau de fidelidade** | `full-preserve` · `partial-preserve` · `attribute-transfer` (nomeando o alvo) · `loose-guide` |

O **grau** é o que faltava por inteiro: sem ele, toda referência é tratada como se fosse
full-preserve, e âncoras demais brigam entre si — que é exatamente o item 3 da ordem de tentativa
da §5.

> 🟡 Isto vem da skill da **comunidade** (OSideMedia, MIT), não do fabricante. **Testar antes de
> virar lei** — mas a exclusão de fundo já se justifica sozinha pelo dano que evita.

### 🟡 Timestamp é ORÇAMENTO DE TEMPO, não ponto de corte

Os segundos do bloco STAGES **alocam duração**, não marcam frame exato. Escrever `0–9s` não garante
que o corte caia em 9,0 s — garante que aquele segmento receba cerca de 9 segundos do total.
Consequência prática: **não pendurar uma batida dramática num segundo exato** e não tratar
divergência de meio segundo como falha do prompt.

> ⚠️ **NÃO existe teto conhecido de caracteres. Corrigido em 2026-09-02.**
>
> Aqui estava escrito *"limite de 5.000 caracteres por prompt"*. **Nós lemos a aula errado:**
> a frase dos 5.000 é sobre o **modo de vídeo longo (180 s)** — o argumento é que 5.000 é
> *pouco* para descrever 3 minutos. Ela continua válida naquele contexto (§4), e só nele.
>
> 🟢 **Catálogo ao vivo (2026-09-02, 40 modelos de vídeo): nenhum modelo do Higgsfield declara
> limite de caracteres.** Os parâmetros do contrato são duração, resolução, modo, gênero e
> áudio — `prompt` não tem `maxLength`. O ~3.500 que circulava como "limite do Higgsfield"
> também morreu: 10 fontes varridas, 4 oficiais, o número não aparece em nenhuma.
>
> 🎓 **A prova empírica:** o guia oficial *Seedance 2.5: Complete Prompting Guide* publica 10
> prompts testados — menor 1.020, maior 7.084, mediana ~6.300, e **8 dos 10 passam de 5.000**.
> O teto que respeitávamos era menor que a mediana do que o fabricante publica como boa prática.
>
> ⚫ **Decisão do Samuel (set/2026): o prompt de cena é tão detalhado quanto a cena precisar.**
> Nem teto nem piso. Nem o chat do Omega nem a skill devem comprimir um prompt para caber em
> número nenhum. Faixa de trabalho observada: **1.000–7.000, massa em 5.000–7.000** — calibragem,
> não meta. A ressalva que sobrevive: **prompt longo e vago continua pior que curto e preciso.**

---

## 4. ECONOMIA — o que a aula manda evitar

🎥 **NÃO usar o modo de vídeo longo (180 s).** *"basically what it is, it is six
30-second videos stitched together and that's all based on ONE prompt. And one
prompt is only like 5,000 characters, so there's not a lot of detail you can add
into like a 3-minute video. So, I would recommend not using that."*

🎥 **O que fazer no lugar — e isto resolve continuidade:** usar **o vídeo
anterior como referência** e descrever o que acontece em seguida. Permite
introduzir referências novas no meio (novo personagem, novo objeto) e emenda sem
costura. Dá para passar `video one, video two` e pedir combinação contínua.

### 🎓 A receita completa são TRÊS entradas — nós usávamos UMA (set/2026)

**Por que estávamos errados:** passávamos o vídeo anterior para o Seedance e achávamos que isso
bastava. O gerador recebia o pixel, mas **quem escreve o prompt do bloco seguinte não recebia nada**
— então o texto do bloco 8 era escrito sem saber o que tinha acontecido no bloco 7, e a emenda
dependia de sorte.

| Entrada | Para quem vai | Para quê | Tínhamos? |
|---|---|---|---|
| **Prompt da cena anterior** | para o **Claude** | para quem escreve saber o que acabou de acontecer | ❌ |
| **Keyframe da cena anterior** | como **referência de estilo** | trava luz, paleta e textura | ❌ |
| **Vídeo anterior** | para o **Seedance** | trava movimento e emenda | ✅ |

### 🎓 E a trava de POSE no corte — a que faltava e explica muita emenda ruim

*"The poses at the end of shot one exactly match the start of shot two. **If you don't spell this
out, the AI treats the cut as a brand new scene and throws away the poses.**"*

O corte precisa ser **escrito**: onde cada corpo está, para onde olha, o que segura — no último
instante do bloco anterior e no primeiro do seguinte, **idênticos**. Sem isso o modelo trata o
corte como cena nova e recomeça a marcação do zero.

### 🎓 O plano aberto de estabelecimento TRAVA a marcação

*"If you're struggling with positioning your characters where you want them to be, **start the
video with a wide establishing shot. That way Seedance places everyone exactly where they need to
be and they stay locked for the entire video.**"*

Não é enfeite de abertura: num bloco com mais de um corpo, o plano aberto no início é o que fixa
quem está onde pelo resto do bloco. **Bloco de multidão ou de confronto abre aberto** — e isso
conversa direto com a §1 do `direcao-bloco-acao.md`.

🟡 E do estudo dos 62, o que mais barateia:
- O custo por segundo acabado varia **37×** entre projetos (3,3 a 123,6 cr/s).
  Essa variação é maior que qualquer economia de resolução.
- O projeto **mais barato** (3,3 cr/s) foi também um dos **mais curtidos** —
  e o stack dele era **56,4% imagem**, não vídeo.
- **Volume não compra recepção:** 2.060 gerações → 1.337 views; 250 gerações →
  32.346 views.

---

## 5. QUANDO UMA CENA DÁ ERRADO

🎥 **A técnica de correção, e ela é a mais valiosa da aula:**

> *"use your previous generations, **cut out scenes of the parts that you like**,
> and then repurpose that… you cut out the perfect scene or the frame that you
> want to use, and you regenerate it using that new frame that already has the
> good look and feel to it, and then you can just prompt it to do it better than
> what you did originally."*

**Geração ruim não é crédito perdido — é matéria-prima.** Recortar o quadro bom
de uma tentativa falha e usá-lo como referência da próxima é a diferença entre
pagar duas vezes e pagar uma vez e meia.

🎥 *"you don't got to give up on your first generation because now you can
actually make them good."*

🟡 E o estudo dos 62 aponta na mesma direção, por outro caminho: **quando o
plano não fecha, simplificar o PLANO, não o texto** — *"se a ação erra em duas
tomadas de três, o prompt não é reescrito, a corrida é partida ao meio"* ·
*"menos âncoras ganham de instruções melhores"*.

### 🎓 A régua de diagnóstico — vem ANTES da ordem de tentativa

*"**Always generate four at once.** That way, if a take looks weird, you immediately
know if it's a random glitch or your prompt."* · *"Knowing the difference between a
broken prompt and a bad roll is how you save credits."*

> **4 de 4 errados → o problema é o PROMPT. 1 ou 2 errados → foi sorte; regere.**

Sem esta régua, reescreve-se prompt que estava certo — e reescrever texto é 🟡 o
caminho que mais custou no estudo dos 62. **Ela decide se a ordem abaixo sequer
deve ser executada.**

⚫ **Onde aplicar (decisão do Samuel, set/2026): 4/4 só em bloco de AÇÃO.** Em bloco
simples, 1 take e regeração só se falhar. 🔵 Aplicar 4/4 em tudo custa 300 cr/bloco e
derruba o canal de **4,3 para 1,5 vídeos/mês** no plano de 9.000. Conta completa e
critério do que é bloco de ação em `direcao-bloco-acao.md`.

**Ordem de tentativa quando um bloco sai errado:**
1. Recortar o melhor quadro da tentativa e usá-lo como referência da próxima
2. Partir o plano em dois planos mais simples
3. Remover uma referência (âncora demais briga entre si)
4. **Só então** reescrever o texto — é o caminho que mais custou no estudo

🎓 **A escada completa quando o plano não fecha** (do mais barato ao mais caro):
multi-shot falhou → cair para UM plano contínuo · cena apertada → partir em duas ·
cena grande → escrever o prompt inteiro e **depois** dividir (8A, 8B, 8C) · plano
chapado → **aumentar** a cobertura (2 planos viram 3, com ângulos diferentes).

### 🎓 E quando o take PASSA — a rubrica

Tínhamos ordem de correção para o take que falha e nenhum critério para o que passa.
Agora existe: `rubrica-aceitacao-take.md`. O sinal mais importante:

> **Corte rápido que você não pediu é rejeição automática.** *"Quick cuts are what
> this model does when it can't animate the motion underneath."* Não é estilo — é o
> modelo escondendo movimento que não conseguiu animar.

⚫ **A régua do Samuel (set/2026): aprova o bom, não regera atrás de excelente.**
Rejeita o que está abaixo de mediano ou quebra item da lista de reprovação automática.

---

## 6. O QUE O ESTUDO AINDA NÃO RESPONDEU

Não decidir por conta própria nenhuma destas. Estão em fila no Salomão:

- **P2** descrição minuciosa vs. personagem e cenário constantes
- **P3** storyboard rígido ajuda ou atrapalha
- **P4** como quebrar a história em cenas — e se dá para derivar de uma história
  corrida em vez de decidir cena por cena
- **P5** vocabulário de direção transcrito termo a termo
- **P6** o que muda com criatura em close
- **P7** o que eles escreveram para corrigir uma cena que deu errado

🟡 **Base já classificada:** dos 62 projetos da coleção, **33 são
fotorrealistas** (o registro que nos serve) e **24 deles trazem receita de
verdade no brief**. É desse subconjunto que sai regra de aparência. Padrão de
**método** pode sair dos 62 — método atravessa registro; aparência não.

---

## 7. HIGGSFIELD ACADEMY — o que entrou em 2026-09-02

Levantamento dos 7 cursos de *Movie making*. Dossiê completo, com o que foi lido e o que **não**
deu para ler, em `ACADEMY-HIGGSFIELD-2026-09-02.md`.

### 7.1. O que ela CONFIRMA (fonte independente, não novidade)

🎓 Pipeline em estágios (roteiro → assets → cena a cena) · character sheet de três painéis com
*quality locks* (é o nosso model sheet com outro nome) · âncora de realismo com o vocabulário deles
(*8K IMAX, photorealistic, pore-level realism*, Lubezki e Deakins citados) · negativa de áudio
mantida **no texto** mesmo havendo parâmetro (valida o cinto-e-suspensório) · multi-shot dentro de UM
prompt com segundos de início (é o nosso bloco STAGES) · **"Read your failed takes"** — geração ruim
é matéria-prima, não crédito perdido. **A §5 inteira agora tem duas fontes independentes.**

### 7.2. O que ela ABRE, e que não temos (não é edição, é fila de trabalho)

- ~~🎓 Existe uma skill oficial do fabricante, `higgsfield-seedance-prompt.skill`.~~
  **PROCURADA EM 2026-09-02 — e a premissa não se sustenta como estava escrita.** O que foi feito e
  o que voltou:
  - 🟢 **O MCP do próprio Higgsfield serve 16 workflows** (`get_workflow_instructions`) e **nenhum
    deles é um construtor de prompt do Seedance.** Se o fabricante empacotasse essa skill, é aqui
    que ela estaria.
  - A aula Stage 3 (`/academy/courses/santiago-cinematic/prompt-builder-skill-first-run`) **não
    expõe download nenhum** no HTML servido — só o prompt de exemplo.
  - O que existe publicamente com esse nome é **`OSideMedia/higgsfield-ai-prompt-skill`** no
    GitHub — **comunidade, não fabricante.** Já está classificada 🟡 no nosso material.

  > **Correção de proveniência, encerrada em 2026-09-02:** o próprio README do repo **se declara
  > community-made** — *"This is community-made, not official Higgsfield material"* (OSideMedia,
  > MIT, v3.35.0). É o autor dizendo, não inferência nossa. **Ela é 🟡. Não é 🎓.** Continua sem
  > haver prova de que exista uma skill de prompt do fabricante; se um dia aparecer atrás do login
  > da Academy, comparar de novo.

- ✅ **Comparação campo a campo FEITA (2026-09-02), com a skill 🟡 da comunidade.** Resultado: os
  três formatos são compatíveis — o nosso não precisa ser reescrito. Mapa:

  | Nosso (🎥 §3) | Guia oficial (🎓) | OSideMedia (🟡) |
  |---|---|---|
  | GOAL | — | — |
  | REFERENCES | — | role + **exclusão** + **grau de fidelidade** |
  | CONTINUITY | CHARACTERS · LOCATION | Scene and Environment |
  | STAGES | FIRST FRAME AND BLOCKING · Shot 1..N | formato estagiado |
  | LOOK | GLOBAL STYLE · LIGHTING · PHYSICS | Visual Style |
  | CAMERA + PERFORMANCE | OPTICS and CAMERA | Camera |
  | NEGATIVES | negativa colada no sujeito | só exclusões "Do not" |

  **O que ela acrescenta e vale adotar (tudo 🟡 — testar antes de virar lei):**
  - ⚠️ **Folha de personagem exige exclusão explícita do fundo:** *"Do not take the gray backdrop"*.
    **Isto é uma armadilha que nós pegaríamos** — o nosso model sheet usa fundo de estúdio cinza
    liso, e alimentá-lo como referência sem exclusão vaza o cinza para dentro da cena.
  - **Grau de fidelidade por referência:** `full-preserve` · `partial-preserve` ·
    `attribute-transfer` (nomeando o alvo) · `loose-guide`. Não temos nada disso.
  - **Nomear personagem por marcador visível, nunca pelo handle da referência** — escrever *"o homem
    de capa vermelha"*, não *"@Image 1"*.
  - **Nunca escrever idade em palavra** ("engine rule 1") — usar papel, porte, roupa e ação.
  - **Timestamp é orçamento de tempo, não ponto de corte exato** — tempera o nosso bloco STAGES.
  - **Primeiro e último frame precisam ter a mesma proporção**; a proporção trava na primeira imagem.

- ✅ 🎓 **A skill `character-sheet` do fabricante, essa sim, foi lida** (via MCP, 2026-09-02) e o que
  ela acrescenta ao nosso model sheet já está incorporado em `model-sheet-storyboard.md`: o motor
  anti-IA (anti-retoque), a cláusula anti-brilho no olho, estrutura facial adulta declarada, a
  negativa que impede figura duplicada, e a ordem dos slots. **A arquitetura bateu com a nossa** —
  o nosso model sheet ganhou respaldo do fabricante em vez de ser desmentido.
- 🎓 **Direção de bloco de AÇÃO.** Eles têm um curso inteiro (*blueprint the fight before motion*,
  medidas em metros e segundos, *preserve physics through the impact cut*). Nossa classificação
  AÇÃO/SIMPLES diz **quanto gastar** num bloco de ação; não diz **como dirigi-lo**. É buraco real.
- 🎓 **Rubrica de aceitação de take.** Temos ordem de correção quando o take falha; **não temos
  critério escrito de quando um take passa.**
- 🎓 **Movimento de câmera escrito por NEGAÇÃO exaustiva.** O prompt bank público (46 exemplos de
  câmera) escreve *"no dolly, no truck, no arc, no slide, no zoom, no tilt"* para fixar um pan.
  Matéria-prima direta para `direcao-cinematografica.md`.
- 🎓 **Ótica em GRAUS de campo de visão** (`84° wide`, `47° medium`) além dos mm que já usamos.
  Dois vocabulários, o modelo entende os dois — o deles é o que aparece nos exemplos prontos.
- 🎓 **video-to-video sobre footage real.** Curso inteiro; **zero linha nossa sobre isso.** Pode ou
  não servir ao WhoIAm — decisão do Samuel, não do agente.

### 7.3. O que ela NÃO responde

🎓 Eles **não** entregam storyboard como artefato — entregam asset sheets + shotlist + prompt com
stages. Isso **reforça** a decisão ⚫ da §2, mas **não responde P2 nem P3**. Registrado como reforço,
não como resposta. **P2–P7 continuam abertas.**

### 7.4. O contrato de direção — ⚫ decisão do Samuel, 2026-09-02

> **O Samuel dita a CENA. O agente dirige.**

- **O Samuel entrega:** o que acontece, quem está lá, onde, e a emoção/intenção do momento.
- **O agente decide:** enquadramento, ângulo, altura de câmera, lente, movimento, posicionamento
  dos corpos, cobertura, ritmo e onde corta.

**Por quê:** ele não é diretor de cinema e **não deve precisar aprender vocabulário técnico para
fazer um vídeo.** Toda a biblioteca de câmera, lente e movimento existe para o agente usar por
conta própria, derivando da intenção dramática — não para virar formulário que o Samuel preenche.

**Corolário que muda o comportamento do chat:** o prompt **nunca** volta para ele com pergunta de
técnica. *"Qual lente você quer?"* é pergunta errada. Se houver dúvida, ela é sobre a **intenção**
(*"essa cena é de ameaça ou de tristeza?"*), nunca sobre o meio de conseguir a intenção. Decisão
técnica cara ou arriscada: o agente **decide e declara** o que decidiu e por quê — não devolve a
decisão.

> ⚠️ **Isto convive com a ordem de perguntar em caso de dúvida, não a contradiz.** A dúvida que se
> pergunta é de **intenção e de comportamento**. A de ofício de câmera, não.

### 7.4b. ⚠️ A ARMADILHA DA NEGAÇÃO — contradição VIVA, registrada e não resolvida

**Três aulas da Academy dizem que negativa não funciona:** 🎓 *"we don't need the negative at all
because the model doesn't get them and does quite the opposite"* · 🎓 *"Telling the model what not
to do rarely works"* · 🎓 **"the negation trap"** — *"AI models completely ignore the word 'not'. It
just sees 'game' a dozen times and goes with it."*

**E o guia oficial da MESMA empresa usa negativa o tempo todo** — *"No logos, no readable text"* —
e o prompt bank escreve movimento de câmera inteiramente por negação (*"no dolly, no truck, no
arc"*). **Duas fontes oficiais em desacordo. Não escolhemos.**

### ✅ RESOLVIDA em 2026-09-02, lendo o guia oficial na fonte

**Fui ler o guia oficial inteiro** (`D:\Agentes\SALOMAO\estudos\academy-higgsfield\_guia-oficial-prompt-seedance-2-5.md`,
729 linhas) e catalogar **cada negativa que ele usa**. O padrão é inequívoco:

> ## A negativa NUNCA aparece sozinha.
> **Toda negativa do guia oficial acompanha uma afirmação POSITIVA da mesma restrição.**

Evidência, verbatim — a afirmação positiva está em **negrito**:

- *"**The group is exactly four members** across all beats, no fifth member, no duplicate member"*
- *"**Real-time 24fps**, no slow motion, no speed ramps, no ghosting or trails"*
- *"**Every beat has a moving camera and hard motion**, no static holds"*
- *"**one fixed focal length for all thirty seconds, framing changed only by walking closer or
  further** (…) no slow pans, no isolated shots"*
- *"**Screen direction never flips, the sedan arrives from screen-right, the woman travels
  right-to-left.** No subtitles, no captions, no on-screen text **other than the neon word HOTEL**"*
  — a negativa até carrega a exceção positiva dentro dela
- *"**heavy charcoal wool blanket with a frayed edge, cream cable-knit sweater collar, dark
  trousers, worn leather boots.** No logos, no readable text on anything"* — guarda-roupa descrito
  à exaustão primeiro; a negativa só apara o que sobrou

🟢 **E o bloco onde elas moram chama-se, no próprio guia, `POSITIVE LOCKS:`.** O fabricante não
chama aquilo de negativa — chama de trava.

**Isso explica os fracassos das aulas sem contradizer ninguém.** Todos os exemplos que quebraram
são **negativas ÓRFÃS**, sem nenhuma afirmação positiva ao lado: *"not a game, no CGI"* (repetido
uma dúzia de vezes, sem dizer o que a imagem **é**) · *"he's not crying"* (sem dizer qual é a
expressão) · *"no held objects, no handle"* (sem dizer o que a mão **faz** — e o conserto que
funcionou foi justamente *"ask the model to raise his arm"*, uma afirmação positiva).

> ### A regra, e ela é simples de auditar
>
> **Negativa órfã = defeito de prompt.** Toda negativa precisa de uma afirmação positiva da mesma
> restrição ao lado — antes, de preferência. Se você não consegue escrever a versão positiva, a
> negativa não deve entrar.
>
> - ❌ `no shaky camera` → ✅ `locked-off tripod shot, no shaky camera`
> - ❌ `not a video game` → ✅ `35mm anamorphic, natural contrast, visible film grain — no video-game look`
> - ❌ `no music` (sozinho) → ✅ `diegetic room tone only — no music, no subtitles` *(o que já fazíamos)*

**Consequência para o nosso corpus:** o bloco `NEGATIVES` da §3 **continua existindo, mas deixa de
ser uma lista solta no fim.** Cada item dele tem que ter par positivo em algum lugar do prompt — e
onde não tiver, o par se escreve. As negativas de áudio já eram assim (*"cinto e suspensório"*);
o resto do corpus é que precisa passar pela mesma peneira.

⚠️ **E o movimento de câmera por negação exaustiva do prompt bank deixa de ser conflito:**
*"**Pan right**… no sideways travel, no dolly, no truck, no arc, no slide, no zoom, no tilt"* —
*"pan right"* é a afirmação positiva. O prompt bank segue o mesmo padrão. **Pode ser adotado**,
desde que a negação exaustiva venha sempre depois do movimento nomeado, nunca no lugar dele.

> 🔵 **Isto é leitura de fonte primária, não medição nossa.** O teste da §7.4c confirma ou desmente.

### 7.4c. ⚫ TESTE DA NEGATIVA — desenho do Samuel, a rodar no primeiro projeto

⚫ **Decisão do Samuel (set/2026):** o teste roda **dentro do primeiro vídeo real**, não numa
bancada separada. **Cenas pouco importantes, sem muita ação** — uma ou duas por braço.

**Por que cena sem ação, e ele está certo:** bloco de ação falha por conta própria (física,
coreografia, multidão). O ruído afogaria o efeito que se quer medir. Bloco simples isola a
variável.

**O que testar mudou depois do achado da §7.4b.** Não é mais "negativa × sem negativa" — é:

| Braço | Prompt |
|---|---|
| **A — negativa órfã** | movimento escrito só por negação: *"no dolly, no truck, no arc, no slide, no zoom, no tilt"* — **sem nomear o movimento** |
| **B — negativa acompanhada** | *"**slow pan right**, no dolly, no truck, no arc, no slide, no zoom, no tilt"* — idêntico, mais a afirmação positiva na frente |
| **C — positivo puro, quatro campos** | *"pan right. **Movement:** rotate the camera horizontally from left to right from one fixed point. **Speed:** smooth constant rotation. **Framing:** keep the horizon level while new space enters from the right. **End:** settle on a clear final composition."* — zero negação |

> **O braço C entrou em 02/09** depois de ler as três bibliotecas do autor do vídeo
> (`bibliotecas-camera-emocao.md`): **45 movimentos, 25 emoções e um gerador inteiro, todos
> escritos 100% no positivo, sem uma única negação.** Se C empatar ou ganhar de B, a negação
> exaustiva é dispensável e o vocabulário de quatro campos vira o padrão do canal.

**Tudo o mais idêntico:** mesmo bloco, mesmas referências, mesma duração, mesma resolução, mesma
semente se houver. A ÚNICA diferença entre A e B é a frase positiva.

**Custo, e ele é baixo:** 🔵 2 takes por braço (1 take não distingue falha de azar — §5) =
4 × 75 = **300 créditos por par**. Dois pares = **600 créditos, ~6,7% do mês**. Cabe no
vídeo-cobaia sem comprometer a gaveta.

**Como ler o resultado:**
- **B nitidamente melhor que A** → a §7.4b está confirmada. A regra "negativa órfã é defeito"
  vira lei, e o prompt bank pode ser adotado inteiro.
- **A e B equivalentes** → a negação exaustiva funciona sozinha; a §7.4b está errada e a leitura
  do guia oficial era coincidência de estilo. Reabrir.
- **Os dois ruins** → o problema não é a negativa, é o bloco. Não conclui nada — refazer com
  outro bloco.

**Registrar o resultado aqui**, com data e os quatro vídeos guardados. Enquanto não rodar, a
§7.4b permanece **leitura de fonte primária**, não medição nossa.

### 7.5. Prosa é ENTREGA, JSON é TRABALHO — 🎓 resolvido pela fonte primária

O guia oficial do Higgsfield manda **prosa em bloco contínuo, com seções rotuladas em caixa alta**.
Nenhuma fonte primária recomenda JSON para Seedance. Ordem oficial das seções:

```
GLOBAL STYLE → SCENE → CHARACTERS → LOCATION → FIRST FRAME AND BLOCKING
→ Shot 1..N (cada um terminando em "Hard cut" onde houver corte)
→ OPTICS and CAMERA → PHYSICS → LIGHTING → AUDIO
```

🎓 *"Most working Seedance 2.5 prompts follow the same shape: one visual rule at the top, one sound
rule at the bottom, and everything in between broken into shots."*

**Como fica para nós:** o Omega mantém o bloco como **estrutura interna** (campo a campo,
validável, reusável, comparável entre blocos, fácil de gerar em lote) e **serializa para prosa
rotulada na hora de montar o prompt**. Não é adotar JSON no prompt — é separar o formato em que se
*pensa* do formato em que se *entrega*.

🎓 **Confirmação literal da nossa regra de parâmetros:** *"Generation parameters are not prompt
text"* — resolução, duração e proporção se escolhem no gerador; escrevê-las na prosa não faz nada.

🟡 **Notação de áudio dentro da prosa (nova para nós, barata de adotar):**
`( )` música · `< >` efeito sonoro · `{ }` diálogo · `【 】` legenda.

### 7.6. O choque do "3/4" — resolvido, e a distinção está escrita

Parecia contradizer a correção do Samuel sobre as duas pessoas a 45°. **Não contradiz.** O 3/4 da
Academy é de **LOCAÇÃO** (duas paredes visíveis, profundidade) e o que morreu é o 3/4 de **PESSOA
espelhado** (as duas giradas no mesmo ângulo para a lente, de corpo inteiro). Existe ainda um
terceiro sentido, **vivo e em uso**: o 3/4 de pessoa *assimétrico*, que é justamente o instrumento
anti-espelho. A tabela com os três sentidos foi escrita em `model-sheet-storyboard.md` para o termo
não vazar de novo.
