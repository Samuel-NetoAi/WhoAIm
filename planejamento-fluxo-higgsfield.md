# Planejamento do novo fluxo — WhoIAm no Higgsfield

Data: 19/08/2026 · Todos os preços foram medidos na API do Higgsfield neste dia com `get_cost`,
não estimados.

---

## 1. Onde o seu plano não fecha (o mais importante primeiro)

### 1.1. Os "75 pontos por vídeo" são 480p

| Seedance 2.5 | Créditos | cr/segundo |
|---|---|---|
| 30s · **480p** | **75** | 2,5 |
| 30s · 720p | **195** | 6,5 |
| 30s · 1080p | **270** | 9,0 |

O número que você viu na interface existe — só que é a resolução mais baixa. 480p num vídeo de 10
minutos no YouTube não é entregável, e nem os 720p são óbvios: numa TV, um vídeo de criatura em close
com pele/escama/textura em 720p entrega bem menos do que o padrão "ultra-realista" que a skill inteira
foi construída para defender.

**Proveniência confirmada (19/08/2026):** os "75 créditos" que você originalmente viu na interface
eram especificamente **Seedance 2.5 · 480p rodado dentro do Cinema Studio** — bate exatamente com o
valor medido via `get_cost` na API acima. Isso é uma confirmação de que o preço no Cinema Studio e
na API são o mesmo para esse par modelo/resolução, não uma divergência a investigar.

### 1.2. CORRIGIDO EM 19/08/2026 — o Ultra escala até 9.000 créditos

**Esta seção original dizia "não existe plano de 9.000 créditos" — está errada.** O Samuel
confirmou que o Ultra tem uma função para escalar até 9.000 créditos/mês. Os planos base expostos
continuam sendo **Plus (1.000 cr/mês, US$49)** e **Ultra (3.000 cr/mês, US$129 — ou US$99 no
anual)**, mas o Ultra aparentemente não trava em 3.000 — existe um caminho para chegar a 9.000.

**Mecanismo confirmado por print da página de preços (19/08/2026): é um SLIDER dentro do próprio
Ultra** (3.000 / 6.000 / 9.000 créditos/mês), não um top-up separado nem um tier/produto diferente
— "Ultra" é o plano, o slider escolhe a quota mensal dentro dele. Na posição de 9.000, o preço
mostrado é **US$270/mês no anual** (riscado US$387, "30% OFF"). Ainda falta uma peça: comparar essa
razão cr/US$ contra a posição de 3.000 **na mesma condição de cobrança/desconto** (o valor de
US$99/mês anual para 3.000 registrado antes pode ter vindo de um desconto promocional diferente) —
sem isso, não dá pra saber se subir o slider é proporcional (custo por vídeo igual, só destrava
volume) ou mais barato por crédito (aí a tabela de vídeos/mês da seção 1.3 melhora de verdade).
Print a comparar quando possível: a mesma página, slider na posição 3.000, cobrança anual.

A conta original de "9.000 ÷ 75 × 20 = 6 vídeos" ainda tinha o problema do denominador (75 = 480p,
não o padrão do canal) mesmo que o numerador (9.000) estivesse certo — esse ponto da seção 1.1
continua válido.

### 1.3. A conta real, com 3.000 créditos/mês

Um vídeo de 10 min = 600 segundos de vídeo gerado. Com fator de retrabalho ×1,4 (40% de regeração —
orçamento conservador, ainda não medido no seu canal):

| Modelo dos blocos | Créditos/vídeo de 10 min | **Vídeos/mês** |
|---|---|---|
| Seedance 2.5 · 1080p | 7.560 | 0,40 |
| Seedance 2.5 · 720p | 5.460 | 0,55 |
| Seedance 2.0 · 720p | 3.780 | 0,79 |
| Cinema Studio Video · pro (12s) | 1.680 | 1,79 |
| Cinema Studio Video · std (12s) | 1.260 | **2,38** |

**Os 4 vídeos/mês que você imaginou não cabem em nenhuma linha dessa tabela — calculada com o teto
base de 3.000 créditos.** Um único vídeo de 10 min em Seedance 2.5 a 720p custa quase o dobro do seu
mês inteiro de plano nesse teto. **Isto muda se o teto real de uso for 9.000 (seção 1.2, corrigida
em 19/08) e o mecanismo de chegar lá não distorcer o custo por crédito** — nesse caso os números de
vídeos/mês desta tabela sobem proporcionalmente (até ~3x). Não recalculei a tabela abaixo porque o
mecanismo do 9.000 ainda não foi verificado (ver seção 8) — tratar os números atuais como piso, não
teto, até essa verificação acontecer.

E o problema não para no ritmo mensal: a skill `postagem` exige **8–10 vídeos prontos antes da estreia**
(a gaveta de adiantados, aula 10 [09:20]). Isso é 80–120 minutos de vídeo gerado — na hipótese mais
barata da tabela, **4 a 5 meses de plano só para poder estrear**.

### 1.4. O que isso significa de verdade

O gargalo do canal mudou de lugar. No Leonardo, o gargalo era o seu tempo — a conta rendia 4 prompts de
15s por crédito, e você produzia até onde aguentava. No Higgsfield, **o gargalo é o orçamento**, e ele
é duro: não se resolve trabalhando mais.

Foi por isso que eu enfiei um **PORTÃO DE CRÉDITO** na Fase 1 da `whoiam`: antes de gerar bloco nenhum,
sai a conta do vídeo inteiro com o saldo do mês do lado. Descobrir no bloco 14 que o mês acabou é o modo
específico de falhar que esse portão existe para impedir.

---

## 2. A contradição no meio do pedido: Cinema Studio × MCP

Você pediu duas coisas que, hoje, moram em portas diferentes:

| | Cinema Studio (web) | MCP (o agente) |
|---|---|---|
| Gênero, Era, Tempo de montagem, câmera, lente, abertura, roda de emoção, paleta, 30+ movimentos, AI Cast | **sim** | **não** (o Seedance 2.5 via MCP só aceita duração, resolução, áudio e referências) |
| "Unlimited" e Free Gens do plano | **sim** | **não** — a nota de compliance do Higgsfield diz explicitamente que Unlimited e Free Generations só existem em higgsfield.ai, não em MCP/CLI/Canvas |
| Automação pelo agente | não | sim |

Você escolheu **híbrido**, e eu concordo — mas por um motivo específico que vale registrar, porque não é
o motivo óbvio: **imagem no Higgsfield custa 1 a 2 créditos.** Praticamente nada. Isso inverte uma
economia que estruturou a skill inteira: "gerar de novo" deixou de ser custo e passou a ser o
comportamento correto. Painel crítico avulso em resolução cheia, duas versões de thumbnail de verdade em
vez de dois prompts, regenerar a folha inteira sem pensar duas vezes — tudo isso ficou grátis. O caro é
só o vídeo, e é exatamente ali que os controles do Cinema Studio compram algo que o texto do prompt não
compra.

**Divisão que ficou:**
- **Imagens (MCP, agente):** model sheets, environment sheets, mood sheet, folhas de storyboard, painéis
  avulsos, thumbnail. Registrados como **Elements** depois de aprovados.
- **Vídeo (você, no Cinema Studio web):** com a **ficha de controles** que a skill agora entrega junto
  de cada prompt.

### 2.1. A mudança doutrinária que isso força

No fluxo Leonardo, TODA a direção morava no texto: `[LIGHTING]`, `[STYLE]`, lente escrita na frase,
movimento de câmera por extenso. No Cinema Studio isso **duplica**, e duplicar é pior que faltar —
controle e texto disputam. A orientação da própria documentação é: descreva o que está na cena, deixe a
técnica para os controles.

Então a skill passou a entregar, por bloco, prompt **+** ficha:

```
CONTROLES CINEMA STUDIO — Bloco 7
Gênero: horror              ← vem da INTENÇÃO DRAMÁTICA (passo 1 da direcao-cinematografica)
Era: 2020s                  ← padrão do canal; só muda com motivo declarado
Tempo/Montagem: Calm        ← vem do RITMO do bloco (contemplativo/narrativo/ação)
Câmera: Modern              ← padrão ultra-realista
Lente: Clean Sharp          ← vem da tabela lente-como-psicologia
Abertura: f/1.4             ← intimidade/close; f/11 para escala
Movimento: [preset]         ← um por shot, com justificativa dramática escrita
Emoção: @criatura → fear
Paleta/Grading: [preset]
```

A **âncora de realismo é a única coisa técnica que continua obrigatória no texto** — ela existe porque
o assunto (criatura mitológica) puxa o gerador para concept art, e nenhum controle de câmera resolve isso.

### 2.2. Sobre o "melhorar prompt" do Higgsfield: recomendo **desligado**

Isso é opinião minha, não medição, e vou marcar como tal sempre. O raciocínio: seus prompts são
hiperespecificados de propósito e carregam três coisas que um reescritor genérico tende a apagar — a
âncora de realismo, as regras negativas testadas (sem música, sem texto no painel, sem simetria de
confronto em cena mundana) e a geometria de relação declarada sujeito por sujeito. Enhancer de
plataforma otimiza para "cinematográfico bonito", que é literalmente o default que a
`direcao-cinematografica.md` existe para combater.

**Teste barato para eu estar errado:** um bloco, duas gerações, mesmos controles e mesma referência —
uma com o prompt como está, outra com o enhancer ligado. Se ele ganhar, o registro empírico muda e eu
mudo com ele.

---

## 3. A saída que faz a conta fechar: roteamento de modelo por bloco

Aqui a coisa boa. A skill `teste` existia para comparar o Seedance com o Magnific — e ficou obsoleta,
porque a **ferramenta barata alternativa agora está dentro da mesma plataforma**. Mas a parte útil dela,
a classificação de cada bloco em **AÇÃO** ou **SIMPLES**, é exatamente o que resolve o orçamento. Ela
migrou para dentro da `whoiam` como regra de produção.

- **AÇÃO / clímax / criatura em movimento pesado** → **Seedance 2.5**, 6,5 cr/s (720p), até 30s. É onde
  o crédito compra o que o modelo barato não entrega: física, peso, dinamismo sustentado.
- **SIMPLES / contemplativo / estabelecimento / revelação estática** → **Cinema Studio Video**,
  1,5–2,0 cr/s, até 12s. Um plano parado com luz boa não precisa do modelo caro.

**Exemplo real, vídeo de 8 min (480s) com 25% de ação:**

```
8 blocos AÇÃO   × 30s = 240s × 6,5 = 1.560 cr
20 blocos SIMPLES × 12s = 240s × 1,5 =   360 cr
                              total = 1.920 cr  (×1,4 = 2.688)
```

Contra **3.120 cr (×1,4 = 4.368)** se tudo fosse Seedance 2.5. Economia de ~38%, e ela não sai da
qualidade dos blocos que importam.

**Consequência que precisa estar clara:** a duração do bloco deixou de ser constante do canal. O
Cinema Studio Video corta em 12s. Isso muda o orçamento de narração (o roteiro precisa de ~8–10 linhas
para um bloco de 30s e ~3–4 para um de 12s) e muda a heurística de painéis.

### 3.1. Frequência: o número honesto

Com Ultra (3.000 cr/mês), vídeos de 8–12 min e a maioria dos blocos no modelo barato, o teto real é
**~2 vídeos por mês**. Para chegar aos 4/mês você precisa de uma destas: vídeos de ~5 min (que perdem o
anúncio intermediário), praticamente tudo no modelo barato **+** um top-up de créditos, ou um plano maior.

E aqui vale o argumento do próprio curso, que é o que me faz insistir: a regra repetida em **três aulas
diferentes** é *nunca postar com menos frequência do que já vinha* (aula 12 [02:20]; aula 10 [08:49];
aula 13 [19:56]). Estrear em 2/semana sem poder sustentar é escolher, de antemão, cometer o erro que o
curso mais insiste em evitar. Baixar a frequência antes de estrear é grátis; depois, não é.

O curso também dá a base para a alternativa, sem jeitinho: *"mantenha um cronograma de postagem regular
(**semanal ou quinzenal**) e cumpra"* (aula 1 [04:03]; start [03:51]). **Quinzenal é cronograma
legítimo dentro do material.** Minha recomendação: estrear quinzenal, com gaveta de 4–5 vídeos (desvio
registrado no `canal-estado.md`, com a regra contrariada e a justificativa), e subir para semanal quando
o orçamento permitir — nunca o contrário.

---

## 4. Painéis por bloco de 30s

Você levantou 1 painel por segundo. Eu recomendei 2 folhas de 8–10 e você escolheu **1 folha de 12–15**.
Aplicado — com as mitigações, porque o risco é o que você mesmo registrou em produção.

| Bloco | Ritmo | Painéis | Grid |
|---|---|---|---|
| 30s (Seedance 2.5) | contemplativo/transformação | 12 | 4x3 |
| 30s | narrativo | 12–15 | 4x3 / 5x3 |
| 30s | ação/clímax | 15 | 5x3 |
| ≤12s (Cinema Studio) | qualquer | 6–8 | 3x2 / 4x2 |

**Por que 30 painéis foi descartado:** num grid de 30 quadros cada painel entra na faixa em que o
gerador inventa — "painel pequeno alucina" é a sua causa raiz nº 1 registrada, e o teto de 10 existia por
causa dela. O objetivo por trás da sua ideia (amarrar o modelo a cada acontecimento) é atendido por outra
via: **mais intermediários por shot**. Intermediário é amarração temporal sem miniaturizar o painel — e
como ele repete o enquadramento, ele *reduz* o que o gerador precisa acertar em cada quadro pequeno.

**Mitigações que passaram a ser obrigatórias no bloco de 30s:**
- Painel crítico (rosto, revelação, insert decisivo) **sai avulso em resolução cheia, por padrão** — não
  "pode sair". Imagem custa 1–2 créditos.
- Auditoria painel por painel antes de aprovar a folha, não bater o olho no conjunto.
- **Tripwire de reversão:** simplificar composições → painel crítico avulso → **quebrar em duas folhas de
  8** → só então rediscutir a densidade. A opção que você recusou fica registrada como o primeiro degrau
  da reversão, não como ideia morta.

---

## 5. Música: o que eu verifiquei do repertório do YouTube Studio

**Resposta curta: sim, hoje dá para usar sem problema — e é a fonte mais segura que você tem.**

- Faixas da Biblioteca de áudio são gratuitas, **monetizáveis** dentro do YPP e **não são reclamadas
  pelo Content ID**. Isso remove uma categoria inteira de risco.
- Reclamação indevida acontece raramente e se contesta linkando a página da faixa.
- **Faixas `Creative Commons — Attribution (CC BY 4.0)` exigem crédito ao artista + link na descrição.**
  A coluna "Tipo de licença" no Studio é onde se lê. Faixas de licença padrão não exigem nada.
- Cuidado com faixas marcadas **"somente YouTube"**: não podem sair da plataforma (nada de reaproveitar
  num corte para TikTok).

**A ressalva honesta:** o acervo é forte em jazz, rock, reggae, pop, folk e country — e fraco exatamente
no que a sua paleta pede (drone grave, cluster dissonante de metais, percussão de guerra, crescendo
glacial). Então eu **inverti a hierarquia** na skill em vez de trocar de fonte: Biblioteca do YouTube
passa a ser a **primária**, Suno passa a ser o **complemento** para os climas que ela não cobre. E o
mapa de trilha ganhou uma coluna de licença/crédito, que alimenta o bloco de créditos da descrição na
`postagem` — faixa CC BY sem crédito é descumprimento de licença, e isso é termo de licença, não regra
de curso.

Sobre o Suno, para o registro: uso comercial exige plano pago (Pro ou Premier; Studio só no Premier), e
o direito vale para as faixas geradas enquanto a assinatura estava ativa mesmo depois de cancelar.
Música 100% gerada por IA não tem proteção de copyright — ou seja, você também não registra no Content
ID nem impede outro canal de usar a mesma faixa. Não é risco de strike; é só uma expectativa que não
deve existir.

**A regra que você pediu já existia e está correta:** o cue segue a **sequência emocional**, não o bloco.
Três blocos de suspense recebem UMA música, não três. Estava assim desde jul/2026 no `pos-producao.md`.

---

## 6. Legenda prévia: também já existia

Você pediu uma legenda prévia para saber onde a narração entra antes de gastar geração. Isso é o
**Documento 1a — RASCUNHO DE LEGENDAS COM PLACEMENT**, decidido em jul/2026: depois que a montagem trava
as durações em `cenas-travadas-<criatura>.md`, sai o roteiro dividido por sequência com o custo estimado
de cada trecho contra a duração real, você ajusta a palavra vendo o encaixe, e só então o ElevenLabs é
acionado.

O que **mudou** aqui: a constante do orçamento (custo ≈ 33 por bloco de 15s) foi calibrada no fluxo
antigo e **nunca foi verificada em bloco de 30s**. Escalar para 66 é hipótese, não medição — está
marcado como tal e entra na lista de calibração do primeiro vídeo.

---

## 7. Ganhos técnicos novos que a skill passou a usar

| Recurso | O que ele aposenta |
|---|---|
| **`generate_audio: false` / `sound: off`** | A mendicância "No music. No score. No soundtrack." no texto. Agora é parâmetro. **Efeito colateral:** o clipe vem MUDO, e os SFX passam a ser camada de pós (Biblioteca de efeitos do YouTube ou gerados). A frase negativa fica no texto como cinto e suspensório. |
| **`end_image`** | A hipótese H4 (frame inicial + final + "mostre o meio") virou recurso nativo. Caminho para metamorfose e deslocamento grande. |
| **`video_extension`** (forward/backward) | Salvar um bloco 3s curto sem regerar os 30s; emendar blocos com continuidade em vez de corte seco. Nunca testado. |
| **`multi_shots`** (Cinema Studio Video) | Até 6 shots dirigidos por parâmetro, **sem custo extra** (medido: 24 cr com e sem). Equivalente estrutural dos `[SHOT n]`, mas como parâmetro. |
| **Elements** | "use IMAGE 1 as strict character reference". Model sheet aprovado → Element → `<<<element_id>>>` no prompt. A frase de texto dependia de você anexar a imagem certa na ordem certa em cada geração; o Element é a mesma promessa sem o passo manual que falha. |
| **Fim do limite de caracteres** | Os três números morreram: 1.494 (Leonardo), ~3.500 (terceiro sem lastro) e 5.000 (lido errado — era sobre o modo de 180 s). 🟢 Medido em 02/09/2026: **nenhum modelo do Higgsfield declara limite**; 🎓 8 dos 10 prompts oficiais passam de 5.000. A compressão telegráfica que mutilava o `[ACTION]` deixa de ser obrigatória. ⚫ O prompt é tão detalhado quanto a cena precisar. (Não é licença para encher: prompt longo e vago continua pior que curto e preciso.) |

---

## 8. O que eu NÃO consegui verificar — e por isso está marcado como hipótese

Não quero que nada disso passe por medição:

- **Cinema Studio 4.0 na web anuncia até 30s (e a página de produto fala de "até 1 minuto" e 4K nativo).**
  Via MCP, o modelo Cinema Studio Video para em 12s. Se a versão da web for mais generosa, a economia do
  roteamento fica ainda melhor — mas o preço dos modelos exclusivos da web eu não consigo medir daqui.
  **Confira o custo em créditos de cada modelo dentro do Cinema Studio antes de padronizar**, comparando
  com a régua de cr/segundo da tabela.
- **Element funciona com Seedance 2.5?** A documentação de Elements lista Seedance 2.0, Kling 3.0, Cinema
  Studio Video 2/3.0 e os modelos de imagem — **não menciona o 2.5**. Se não pegar, o fallback é o de
  sempre (`image_references` / `start_image`).
- **O padrão "metade ótima, metade mediana" do Seedance 2.0 em 15s se repete em 30s?** Se sim, dois blocos
  de 15s custam exatamente o mesmo que um de 30s e dão duas aberturas de alta energia em vez de uma. É o
  teste nº 1 a fazer, e ele pode derrubar a premissa de padronizar 30s.
- **Fator de retrabalho real.** Orçei ×1,4 sem nenhum dado seu. Se o real for ×2, todas as contas deste
  documento pioram 40%.
- **[NOVO 19/08/2026] Mecanismo real de escalar o Ultra até 9.000 créditos/mês** — top-up pago
  proporcional (mesma razão cr/US$ do plano base), tier/add-on com razão diferente, ou outra coisa?
  Determina se a tabela de vídeos/mês da seção 1.3 precisa ser refeita de verdade ou só lida como
  "vezes ~3" enquanto o custo por crédito não muda. Confirmar via `get_cost`/página de cobrança
  quando a conta Higgsfield for aberta (mês que vem, conforme o Samuel).
- **Enhancer de prompt** — não consegui confirmar o nome exato nem o comportamento da função.
- ~~**Limite de caracteres do Higgsfield** (~3.500 é fonte de terceiro).~~ **RESOLVIDO em
  02/09/2026 — não existe teto conhecido.** 🟢 Catálogo ao vivo: nenhum modelo declara `maxLength`.
  O ~3.500 não tinha lastro (10 fontes, 4 oficiais, não aparece em nenhuma). E o 5.000 **nós lemos
  errado** — era sobre o modo de vídeo longo de 180 s, não sobre o prompt normal. 🎓 8 dos 10
  prompts do guia oficial passam de 5.000 (faixa 1.020–7.084, mediana ~6.300). ⚫ Decisão do Samuel:
  o prompt é tão detalhado quanto a cena precisar — nem teto nem piso. Ver
  `PESQUISA-2026-09-02-limite-prosa-json-direcao.md` §1.
- Tentei transcrever os tutoriais de Cinema Studio no YouTube com o script da `pesquisa-seres`; o YouTube
  bloqueou o acesso deste ambiente. O que está aqui vem do blog oficial do Higgsfield, da página de
  produto e de dois tutoriais escritos.

---

## 9. Ordem de execução sugerida

1. **Assinar o Ultra e medir, não produzir.** Primeiro vídeo é vídeo-cobaia, não vídeo de gaveta.
2. **Vídeo-piloto curto** (4–5 blocos, ~2 min), gastando de propósito nos testes que derrubam premissas:
   - um bloco de 30s vs. dois de 15s (mesmo conteúdo, mesmo custo) → decide o padrão de duração;
   - o MESMO bloco contemplativo em Seedance 2.5 e em Cinema Studio Video → decide se o roteamento
     barato é aceitável (é a decisão que vale mais dinheiro de todas);
   - uma folha de 12–15 painéis → o tripwire de alucinação aguenta?
   - enhancer ligado vs. desligado no mesmo bloco.
3. **Anotar o fator de retrabalho real** e recalcular tudo com o número seu, não com o meu ×1,4.
4. **Só então** decidir frequência, tamanho de gaveta e data de estreia — com o custo por vídeo medido
   em vez de estimado.
5. Rodar o **Produto D** da `postagem` (Sobre, template de descrição, banner, playlists, checklist) —
   isso é barato e independe de crédito, pode andar em paralelo.

O que eu recomendo **não** fazer: começar a encher a gaveta de 8–10 vídeos com premissas não testadas.
No preço novo, um erro de método custa dinheiro de verdade, e ele se multiplica por 8.
