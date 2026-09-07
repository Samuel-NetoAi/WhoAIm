# Higgsfield — plataforma, custos e Cinema Studio (substitui o fluxo Leonardo)

Decisão de ago/2026: a geração de vídeo migrou do Leonardo para o **Higgsfield**. Este arquivo é a
base factual dessa migração. Tudo marcado **[MEDIDO]** foi lido da API do Higgsfield em 19/08/2026
e pode ser reconferido a qualquer momento com `get_cost: true`. Tudo marcado **[A CONFIRMAR]** é
leitura de material de terceiros ou da interface web e vira regra só depois de teste real.

Regra de manutenção: quando um preço ou limite mudar, **remeça com `get_cost` e atualize aqui** —
nunca deixe um número velho valendo por inércia.

---

## 1. A FRONTEIRA QUE MUDA TUDO: web × MCP

O Higgsfield tem duas portas, e elas **não** oferecem as mesmas coisas.

| | **Cinema Studio (web, higgsfield.ai)** | **MCP (o agente gera daqui)** |
|---|---|---|
| Controles de direção | Gênero, Era, Tempo/Montagem, tipo de câmera, lente, abertura, roda de emoção, paleta, presets de luz, 30+ movimentos de câmera | Só `duration`, `resolution`, `generate_audio`, `bitrate_mode`, referências. No modelo Cinema Studio Video: `genre`, `speedramp`, `multi_shots`, `cfg_scale`, `preset_id` |
| Duração máx. | até 30s (Cinema Studio 4.0); a página de produto anuncia até 1 min **[A CONFIRMAR]** | Seedance 2.5: 30s. Cinema Studio Video: 12s **[MEDIDO]** |
| Referências | até 50 por geração **[A CONFIRMAR]** | Elements + start/end frame + image/video/audio references |
| "Unlimited" e Free Gens do plano | **valem aqui** | **NÃO valem** — a nota de compliance do próprio Higgsfield diz que Unlimited e Free Generations só existem em higgsfield.ai, não em MCP/CLI/Canvas/Supercomputer |
| Automação | nenhuma (trabalho manual) | total |

**Modo de produção do canal (decisão do usuário, ago/2026): HÍBRIDO.**
- **Imagens** (model sheets, environment sheets, mood sheet, folhas de storyboard, painel avulso,
  thumbnail) → **MCP**. Imagem custa 1–2 créditos [MEDIDO], é ruído no orçamento; regenerar à
  vontade deixou de ser luxo e passou a ser o comportamento correto.
- **Vídeo** → **Cinema Studio na web**, onde estão os controles de direção e os benefícios do plano.
- O agente entrega, para cada bloco, **o prompt + a ficha de controles do Cinema Studio** (seção 4),
  não só o texto. Bloco entregue sem a ficha de controles está incompleto.

---

## 2. CUSTO EM CRÉDITOS — [MEDIDO] em 19/08/2026

Sempre em créditos por geração. A coluna que importa de verdade é **créditos por segundo**, porque
é ela que permite comparar modelos de durações diferentes.

| Modelo | Config | Créditos | **cr/s** |
|---|---|---|---|
| Seedance 2.5 | 30s · 1080p | 270 | **9,0** |
| Seedance 2.5 | 30s · 720p | 195 | **6,5** |
| Seedance 2.5 | 15s · 1080p | 135 | 9,0 |
| Seedance 2.5 | 15s · 720p | 97,5 | 6,5 |
| Seedance 2.5 | 30s · 480p | 75 | 2,5 |
| Seedance 2.0 (std) | 15s · 1080p | 135 | 9,0 |
| Seedance 2.0 (std) | 15s · 720p | 67,5 | **4,5** |
| Seedance 2.0 Mini | 15s · 720p | 37,5 | **2,5** |
| Cinema Studio Video (pro) | 12s | 24 | **2,0** |
| Cinema Studio Video (std) | 12s | 18 | **1,5** |

### Imagem — tabela completa [MEDIDO], sempre com `count: 4` (que custa o mesmo que `count: 1`)

| Modelo | 1K | 2K | 4K | Observação |
|---|---|---|---|---|
| **Soul Cinema** (`soul_cinematic`) | — | **0,12** | — | "cinema-grade stills"; 21:9 nativo; orientado a personagem/still único |
| Soul Cast (`soul_cast`) | 0,12 | — | — | trava de identidade, 16:9 |
| Seedream 4.5 (`seedream_v4_5`) | **1** (basic, até 4K) | — | 1 | mais barato dos "grandes"; controle preciso |
| **Nano Banana Pro** (`nano_banana_pro`) | — | **2** | 4 | *"ultimate quality, text and diagrams"* — melhor candidato para GRID |
| Nano Banana 2 (`nano_banana_2`) | 1,5 | 2 | 3 | |
| Cinema Studio Image 2.5 (`cinematic_studio_2_5`) | 2 | 2 | 4 | |
| GPT Image 2 (`gpt_image_2`) | 0,5 (low) | — | 4 (high) | |

> **CORREÇÃO IMPORTANTE (19/08/2026) — no plano Ultra Annual, imagem é DE GRAÇA no site.** O painel
> "Unlimited & Free generations" do plano lista **365-day unlimited** para Seedream 5.0 Lite,
> Flux.2 Pro (1K), **Seedream 4.5 (4K)**, **Nano Banana**, Kling O1 Image e **GPT Image**, mais
> **10.000 free gens** de Soul V2 & Cinema. Isso muda o cálculo de imagem para zero — **mas só no
> higgsfield.ai**, porque a nota de compliance do próprio Higgsfield diz que Unlimited e Free Gens
> não valem em MCP/CLI/Canvas. Consequência prática: **as folhas em lote (storyboards, sheets, clean
> plates) valem mais a pena geradas no site**, de graça; o MCP fica para iteração rápida e para
> quando o agente estiver trabalhando sozinho, a 2 créditos por folha — que sobre 9.000 créditos é
> 0,02%, ou seja, escolha de conveniência, não de dinheiro.

**PADRÃO DE QUALIDADE DE IMAGEM DO CANAL (decisão do usuário, ago/2026 — "um pouco mais de qualidade,
não o máximo"): `nano_banana_pro` em `2k`, `count: 4` = 2 créditos** (ou grátis no site, se o modelo
estiver na lista de unlimited do plano). Vale para folha de storyboard,
model sheet, environment sheet, clean plate, mood sheet e painel avulso. Racional: a folha de
storyboard é tarefa de **layout** (grid rígido, calhas, 12–15 painéis autocontidos) e o Nano Banana Pro
é o modelo declaradamente forte em texto e diagramas — grid é diagrama. 2K e não 4K porque a folha é
ativo intermediário: ela vira start frame de um vídeo em 720p/1080p, então 4K dobra o custo sem chegar
na tela.

**Exceção — thumbnail: 4K.** É o único ativo que justifica o máximo: vai para o editor levar texto, é
vista em tamanhos variados, e é a peça que a `postagem` mais cobra. `nano_banana_pro` @ 4k = 4 créditos.

**Ordem de grandeza que fecha o assunto:** um vídeo inteiro usa ~25 imagens. A 2 créditos cada, são
**~50 créditos** — contra 1.900 a 3.900 do vídeo. Qualidade de imagem não é onde o orçamento se decide;
economizar aqui é economizar no lugar errado.


**O erro de origem que este arquivo existe para corrigir:** os "75 créditos por vídeo" observados na
interface são **Seedance 2.5 em 480p**. 480p não é entregável num vídeo de YouTube de 10 minutos. O
preço real do padrão do canal é 195 (720p) ou 270 (1080p) por bloco de 30s.

**Plano do canal: ULTRA no degrau de 9.000 créditos/mês — US$ 270/mês, cobrado anualmente**
(confirmado por print da página de preços em 19/08/2026). O Ultra tem um seletor de volume:
3.000 / 6.000 / **9.000** créditos por mês. A API do MCP só devolve o degrau de 3.000, por isso uma
leitura anterior desta skill afirmou que o tier de 9.000 não existia — **estava errada, corrigido.**

**O que 9.000 créditos custam por vídeo, para a decisão não sair barata na cabeça:** US$ 270 ÷ 9.000 =
**US$ 0,03 por crédito**. Logo:
- bloco de 30s em 480p (75 cr) = **US$ 2,25**
- bloco de 30s em 720p (195 cr) = US$ 5,85
- bloco de 30s em 1080p (270 cr) = US$ 8,10
- vídeo de ~10 min todo em 480p, com retrabalho ×1,4 ≈ 2.121 cr = **US$ 64 por vídeo**
- o mesmo vídeo todo em 720p ≈ 5.460 cr = **US$ 164 por vídeo**

A diferença entre as duas linhas — **~US$ 100 por vídeo** — é o que está em jogo na decisão de
resolução + upscale. Por isso o teste de 345 créditos descrito em
`recursos-higgsfield-quando-usar.md` §1b é o de maior retorno de todo o pipeline.

### Custo de um vídeo inteiro (600s = 10 min), SEM retrabalho

| Modelo | Créditos/vídeo de 10 min | Vídeos/mês em Ultra (3.000) |
|---|---|---|
| Seedance 2.5 · 1080p | 5.400 | 0,55 |
| Seedance 2.5 · 720p | 3.900 | 0,77 |
| Seedance 2.0 · 720p | 2.700 | 1,1 |
| Seedance 2.0 Mini · 720p | 1.500 | 2,0 |
| Cinema Studio Video · pro | 1.200 | 2,5 |
| Cinema Studio Video · std | 900 | 3,3 |

**Fator de retrabalho:** todo bloco regenerado é preço cheio de novo. Até haver medição real do
canal, orçar com **×1,4** (40% de regeração) e registrar o fator observado neste arquivo depois do
primeiro vídeo. Com ×1,4, o mais barato da tabela entrega ~2,4 vídeos de 10 min por mês.

### O PORTÃO DE CRÉDITO — obrigatório no checkpoint da Fase 1

Antes de gerar qualquer vídeo, a Fase 1 fecha com esta conta explícita no checkpoint:

```
Blocos: N   |   Duração por bloco: Xs   |   Total: N·X s
Modelo/resolução escolhidos: ...  (cr/s = Y)
Custo estimado sem retrabalho: N·X·Y créditos
Custo estimado com retrabalho ×1,4: ...
Saldo do mês: ... (rodar `balance`)   |   Sobra depois deste vídeo: ...
```

Se o custo estimado passar do saldo, **dizer isso antes de começar**, com as três saídas na mesa
(encurtar o vídeo, trocar o modelo dos blocos simples, comprar top-up) — nunca começar a produzir e
descobrir no bloco 14 que o mês acabou. Use `scripts/orcamento.py` para a conta.

---

## 3. ROTEAMENTO DE MODELO POR BLOCO — DESCONTINUADO (decisão do usuário, 28/08/2026)

> **Esta seção inteira é registro histórico, não regra ativa.** O usuário decidiu: sempre Seedance
> 2.5, sempre 30s, sempre 480p — sem classificação AÇÃO/SIMPLES nem roteamento pro Cinema Studio
> Video. Motivo prático: a conta abaixo comparava Seedance 2.5 a **720p** (6,5 cr/s) contra Cinema
> Studio Video — mas a regra permanente do canal é 480p pra todo vídeo (seção 1b de
> `recursos-higgsfield-quando-usar.md`), e a 480p o Seedance 2.5 custa **2,5 cr/s**, quase no mesmo
> patamar do Cinema Studio Video. A economia de ~40% calculada abaixo não existe mais nessa
> proporção — ver a conta refeita em `SKILL.md`, Fase 1 Passo 4. Mantido aqui só pra explicar por
> que a arquitetura antiga existia, caso precise ser revisitada.

A skill `teste` existia para comparar o Seedance com uma ferramenta externa (Magnific). Isso ficou
obsoleto: a ferramenta barata alternativa agora está **dentro da mesma plataforma**. A parte útil da
`teste` — classificar cada bloco em AÇÃO ou SIMPLES — vira regra de produção aqui.

Classificar cada bloco no checkpoint da Fase 1:

- **AÇÃO / CLÍMAX / criatura em movimento pesado** → Seedance 2.5 (6,5 cr/s em 720p). É onde os
  créditos compram algo que os modelos baratos não entregam: física, peso, dinamismo sustentado.
- **SIMPLES / CONTEMPLATIVO / estabelecimento / revelação estática** → Cinema Studio Video
  (1,5–2,0 cr/s). Um plano parado com luz boa não precisa do modelo caro.

Exemplo de orçamento misto num vídeo de 8 min (480s) com 25% de ação:
`120s × 6,5 = 780` + `360s × 1,5 = 540` = **1.320 créditos** (×1,4 = 1.848) — contra 3.120 se tudo
fosse Seedance 2.5 em 720p. A economia é de ~40% e ela não vem de baixar a qualidade dos blocos que
importam.

**A classificação é proposta pelo agente e aprovada pelo usuário**, bloco a bloco, no checkpoint —
nunca decidida em silêncio. E o relatório final do vídeo informa quantos blocos foram por cada
modelo e o custo real, para a decisão do próximo vídeo ser melhor que a deste.

**Limite estrutural a respeitar:** Cinema Studio Video corta em **12s**. Bloco classificado como
SIMPLES é dimensionado para ≤12s; bloco de 30s só existe em Seedance 2.5. Isso significa que a
duração do bloco deixou de ser constante do canal e passou a ser **consequência da classificação**
— o que precisa aparecer no roteiro (Documento 1) e no orçamento de narração.

---

## 4. PROMPT × CONTROLES — a mudança doutrinária mais importante

No fluxo Leonardo, TODA a direção morava no texto: `[LIGHTING]`, `[STYLE]`, lente escrita na frase,
movimento de câmera descrito por extenso. No Cinema Studio isso **duplica** — e duplicar é pior que
faltar, porque o controle e o texto disputam. A orientação da própria documentação é: descreva o que
está na cena; deixe a técnica para os controles.

**Divisão de trabalho:**

| Vai no PROMPT (texto) | Vai nos CONTROLES do Cinema Studio |
|---|---|
| Sujeito e ação (o quê, quem, o micro-movimento, a velocidade, o peso) | Gênero (mapeia a intenção dramática do bloco) |
| Cenário, objetos, profundidade, o que entra/sai de quadro | Era (grão, grading, caráter de lente) |
| Direção do olhar, geometria de relação, população do quadro | Tempo/Montagem (Chaotic / Dynamic / Calm / Single Shot) |
| Qualidade e direção da luz **quando ela é diegética e específica da cena** (a tocha na mão dele) | Presets de iluminação (Silhouette, Practicals, Window, Contre-jour…) |
| SFX diegéticos | Tipo de câmera, lente, abertura, movimento de câmera |
| | Emoção do personagem (roda de emoção) |
| | Paleta / color grading |

**A ficha de controles** passa a ser parte obrigatória da entrega de cada bloco, ao lado do prompt:

```
CONTROLES CINEMA STUDIO — Bloco [N]
Gênero: [General / Epic / Drama / Noir / Comedy / Horror / Action]  ← catálogo real da aba Genre do
                                                                       Film Setup (web), confirmado por
                                                                       print 24/08/2026; deriva da
                                                                       INTENÇÃO DRAMÁTICA (passo 1 da
                                                                       direção). Ver tabela de
                                                                       mapeamento em `higgsfield-presets.md`.
Era: [Auto / 1960s / 1980s / 1990s / 2000s / 2020s]  ← catálogo real confirmado 24/08/2026; NÃO cobre
                                                        nada antes de 1960s — usar Auto pra criaturas de
                                                        período anterior. Padrão do canal: 2020s.
Tempo/Montagem: [Auto / Calm / Single shot / Dynamic / Chaotic]  ← catálogo real confirmado 24/08/2026;
                                                                    deriva do RITMO (contemplativo/
                                                                    narrativo/ação)
Câmera: [Modern | DV Camcorder | 35mm Film | 8mm Film | Auto]    ← Modern é o padrão ultra-realista
Lente: [Clean Sharp | Halation Vintage | Anamorphic | Vintage Anamorphic | Warm Vintage | Auto]
Abertura: [f/1.4 Wide Open | f/4 Moderate | f/11 Deep Focus | Auto]  ← f/1.4 pra intimidade/close;
                                                                        f/11 pra escala
Movimento de câmera: [preset]                    ← um por shot, com justificativa dramática
Emoção do personagem: [@personagem → emoção]     ← roda de emoção da UI; catálogo NUNCA fotografado,
                                                    ver LACUNA em `higgsfield-presets.md`
Paleta/Grading: [preset ou ajuste]               ← catálogo completo (50 nomes) em `higgsfield-presets.md`
```

**⚠️ Não confundir com o parâmetro `genre` do MCP.** O `cinematic_studio_video_v2` (chamado via MCP,
`recursos-higgsfield-quando-usar.md` §1) tem seu PRÓPRIO enum de gênero — `auto, action, horror,
comedy, western, suspense, intimate, spectacle` [MEDIDO via `models_explore get`, 28/08/2026] —, que
é **diferente** do Genre da aba Film Setup da web acima (General/Epic/Drama/Noir/Comedy/Horror/Action).
São dois campos distintos em duas portas distintas; nunca copiar o valor de um pro outro. Quando o
bloco for gerado pelo agente via MCP, use o enum do MCP (mapeamento em
`recursos-higgsfield-quando-usar.md` §1); quando o bloco for gerado pelo usuário no Cinema Studio da
web, use o Genre real da tabela acima.

**Catálogo completo confirmado por print (24/08/2026) de Genre/Era/Tempo/Lighting/Color palette, e as
tabelas de derivação (ângulo→Movement, lente-como-psicologia→Lens/Aperture, fraseado de
movimento→preset): `references/higgsfield-presets.md`** (regra genérica, vale pra qualquer criatura)
e `references/higgsfield-presets-exemplo-cthulhu.md` (aplicação real, gabarito de conferência).

**Mapeamentos que já existem na skill e agora viram controle:**
- `direcao-cinematogafica.md` passo 1 (intenção dramática) → **Gênero**.
- Heurística de ritmo do SKILL.md (contemplativo / narrativo / ação) → **Tempo/Montagem**.
- Tabela lente-como-psicologia → **Lente + Abertura**.
- Fraseado de movimento de câmera → **preset de movimento** (e sai do texto do prompt).
- Padrão de montagem (Escalation / Anxiety / Discovery / Catastrophe) → escolhe Gênero + Tempo, e
  segue governando a ORDEM dos shots, que continua sendo trabalho do storyboard.

**O que NÃO sai do texto, em nenhuma hipótese:** a ÂNCORA DE REALISMO. Ela existe porque o assunto
(criatura mitológica) puxa o gerador para concept art, e nenhum controle de câmera resolve isso.
Ela continua no final de todo prompt de imagem.

### Enhancer de prompt do Higgsfield — recomendação: DESLIGADO por padrão

O usuário levantou a função de "melhorar prompt" da plataforma. Posição desta skill, declarada como
**leitura nossa, não como fato medido**: ligar o enhancer num prompt do canal tende a *destruir*
trabalho, não a somar. Motivo concreto: os prompts daqui já são hiperespecificados de propósito, e
carregam três coisas que um reescritor genérico costuma apagar — a âncora de realismo (anti concept
art), as regras negativas testadas (sem música, sem texto no painel, sem simetria de confronto em
cena mundana) e a geometria de relação declarada sujeito por sujeito. Enhancer de plataforma otimiza
para "cinematográfico bonito", que é exatamente o default que a `direcao-cinematografica.md` existe
para combater.

Como testar sem apostar o vídeo: **um bloco, duas gerações** — uma com o prompt como está, outra com
o enhancer ligado, mesmos controles e mesma referência. Comparar e registrar o veredito na seção 7.
Até esse teste existir, deixar desligado e dizer ao usuário que a recomendação é uma opinião, não um
resultado.

---

## 5. ELEMENTS — o model sheet deixa de ser texto e passa a ser objeto

O Higgsfield tem **Elements**: personagens, ambientes e props reutilizáveis, salvos no workspace e
chamados dentro do prompt. Isso é exatamente a doutrina de Model Sheet / Environment Sheet da skill,
só que executável em vez de recomendada.

Fluxo novo da Fase 1:
1. Gerar o model sheet / environment sheet / mood sheet por MCP (`generate_image`, 1–2 créditos).
2. Usuário aprova.
3. **Registrar o aprovado como Element** (`show_reference_elements` action=create).
4. Dali para frente, todo prompt referencia o Element pelo placeholder `<<<element_id>>>`, que o
   backend troca por `@nome-do-element` e injeta a imagem.

O que isso resolve, e que a regra de texto nunca resolveu de verdade: a frase "use IMAGE 1 as strict
character reference" depende do usuário anexar a imagem certa em cada geração, na ordem certa.
Element é a mesma promessa sem o passo manual que falha.

Notas de compatibilidade **[A CONFIRMAR no primeiro uso]**:
- A documentação de Elements lista suporte em Nano Banana Pro/2, GPT Image 2, Seedream 4.5 / 5 lite,
  Cinema Studio Image 2.5, Cinema Studio Video 2 / 3.0, Seedance 2.0 e Kling 3.0 — **não menciona
  Seedance 2.5**. Se o Element não pegar no 2.5, o caminho é o de sempre: passar a folha aprovada
  como `image_references` / `start_image`.
- Soul (identidade treinada) é para UMA pessoa e só funciona em Soul V2 / Soul Cinema. Cena com dois
  personagens exige Elements. Para criaturas, Elements é o caminho — não treinar Soul.

---

## 6. GANHOS TÉCNICOS NOVOS (e o que eles aposentam)

**`generate_audio: false` — o fim da mendicância anti-trilha.**
A regra "todo prompt Seedance inclui *No music. No score. No soundtrack.*" existe porque o Seedance
inseria trilha por conta própria (caso Medusa/águia). No Higgsfield isso é um **parâmetro**: áudio
desligado é áudio desligado. Consequência: o vídeo vem **mudo** — e o `[AUDIO]` de SFX diegéticos do
prompt deixa de produzir qualquer coisa. Decisão que isso força (ver `pos-producao.md`): a camada de
SFX passa a ser montada na pós, com efeitos da Biblioteca de áudio do YouTube (centenas, gratuitos)
ou gerados. **Manter a frase negativa no texto do prompt** de qualquer forma, como cinto e
suspensório para gerações feitas na web onde o parâmetro pode passar batido.

**`end_image` — a hipótese H4 virou recurso nativo.**
Frame inicial + frame final numa mesma geração. É o caminho para metamorfose, deslocamento grande e
transição difícil de descrever: em vez de rezar para o modelo inventar o meio, você entrega os dois
extremos. Atenção: em multi-shot com personagens, a documentação do Cinema Studio 2.0 registra que o
end frame fica indisponível **[A CONFIRMAR na versão 4.0]**.

**`video_extension` (forward/backward) — costura de blocos.**
Estende um clipe existente. Duas utilidades reais: (a) salvar um bloco que ficou 3s curto sem
regerar os 30s; (b) emendar dois blocos consecutivos com continuidade de movimento em vez de corte
seco. Cobrado pela duração estendida. **[A TESTAR]** — nunca usado no canal.

**`multi_shots` no Cinema Studio Video.**
O modelo aceita multi-shot dirigido por `multi_prompt` (até 6 shots, 1–12s cada, 12s no total na v2)
e **não cobra a mais por isso** [MEDIDO: 24 créditos com e sem `multi_shots`]. É o equivalente
estrutural dos `[SHOT n]` do Documento 3 — e aqui é parâmetro, não convenção de texto.

**Tamanho do prompt — não existe teto de plataforma.**

🟢 **MEDIDO em 2026-09-02**, varrendo o catálogo ao vivo (`models_explore`, 40 modelos de vídeo):
**nenhum modelo do Higgsfield declara limite de caracteres.** Os parâmetros que existem no contrato
são duração, resolução, modo, gênero e áudio — `prompt` não tem restrição de tamanho nenhuma.

Consequência: os dois números que circulavam estão resolvidos.

🎓 **A única menção oficial é qualitativa e sem número.** Help Center do Higgsfield (2026-08-01):
*"prompts muito longos ou complexos podem falhar ou demorar mais que o normal"* — listado ao lado
de filtro NSFW e captcha. É **degradação probabilística**, não validação que rejeita o input.

**Os três números que circulavam, e o que cada um era:**

| Número | Veredito |
|---|---|
| **1.494** | **MORTO.** Era do Leonardo, plataforma que não usamos mais. |
| **~3.500** | **MORTO.** Fonte de terceiro, nunca teve lastro. 10 fontes varridas em 02/09/2026, 4 delas oficiais — o número **não aparece em nenhuma**. Não é "[A CONFIRMAR]": foi procurado e não existe. |
| **5.000** | **MAL LIDO POR NÓS.** 🎥 A frase da aula é sobre o **modo de vídeo longo (180 s)** — o argumento é que 5.000 caracteres é *pouco* para descrever 3 minutos. Nunca foi anunciado como teto do prompt normal. Continua válido **só** naquele contexto (§4 do REGRAS). |

🎓 **E a prova empírica, que é a que vale:** o guia oficial *Seedance 2.5: Complete Prompting Guide*
(2026-08-13) publica 10 prompts testados. Medidos: menor **1.020**, maior **7.084**, mediana
**~6.300** — e **8 dos 10 passam de 5.000 caracteres**. O teto que a gente respeitava é menor que a
mediana do que o próprio fabricante publica como boa prática.

⚫ **Decisão do Samuel (set/2026): o prompt de cena é tão detalhado quanto a cena precisar.**
Nem teto nem piso. O tamanho é consequência do que a cena exige — não uma cota a cumprir nem uma
cota a respeitar. Nem o chat do Omega nem a skill devem comprimir um prompt para caber em número
nenhum, nem inflar um que já está completo.

**Faixa de trabalho observada no material oficial: 1.000 a 7.000, com a massa entre 5.000 e 7.000.**
É calibragem de intuição, não regra: um prompt de cena saindo com 600 caracteres quase certamente
tem falta de ofício. Isso é sinal de alerta, **não** um mínimo a bater.

🎓 **Se um dia importar medir a fronteira real, é barato:** o Help Center diz que geração falhada
**devolve o crédito automaticamente** (exceção nomeada: Grok). Uma escada de 5.000 / 8.000 / 12.000
mede onde quebra gastando quase nada.

**A única regra que continua valendo:** prompt longo e vago é pior que prompt curto e preciso.
Escrever mais só vale quando o que se escreve é ofício concreto (lente, luz, ação, geometria,
antecipação, reação do ambiente) — nunca adjetivo empilhado. Onde gastar o espaço está no
`SKILL.md`, seção "PROMPT LONGO".

---

## 6b. GUIA DE TERCEIRO — "Guia Definitivo Higgsfield Cinema Studio (v3.5 e 4.0)"

O usuário forneceu em 19/08/2026 um guia em .docx sobre o Cinema Studio. Documento denso e útil,
**sem nenhuma fonte citada** — então foi tratado como relato de terceiro e cada número checável foi
medido com `get_cost` antes de entrar aqui. Resultado da checagem:

| Afirmação do guia | Veredito | Medição |
|---|---|---|
| **"2x2 Grid: quatro opções pelo custo de uma"** | ✅ **CONFIRMADO — e vale para todo modelo de imagem** | `count:4` custa o MESMO que `count:1`: Cinema Studio Image 2.5 = 2 cr nos dois; Nano Banana 2 = 1,5 nos dois; Seedream 4.5 = 1 nos dois |
| "AI Cast custa 0,5 crédito" | ✅ aproximado, na verdade **mais barato** | `soul_cast` = **0,12 cr**; `soul_cinematic` (Soul Cinema) = **0,12 cr** em 2K |
| **"96 vezes mais barato que GPT Image 2"** | ❌ **FALSO** | GPT Image 2 = 0,5 cr (quality low) / 4 cr (high). Contra 0,12 do Soul Cast dá 4x a 33x — não 96x. O número foi inventado; a direção está certa. |
| "Teto nativo de saída de vídeo costuma ser 720p; gerar nativo em resolução maior consome créditos desproporcionalmente" | ✅ coerente com o medido | 720p = 6,5 cr/s vs 1080p = 9,0 cr/s no Seedance 2.5 (+38%) |
| "21:9 sinaliza cinema" | ⚠️ **não custa nada, mas o guia ignora o custo real** | 21:9 = 195 cr para 30s/720p, idêntico ao 16:9. O preço não é em crédito, é em tela — ver seção 4 do `recursos-higgsfield-quando-usar.md` |
| "Gênero Action induz whip pans e trepidação" | ⚠️ **plausível e é um ALERTA, não uma dica** | Colide com o "dono do olhar = testemunha invisível" do canal (câmera estática ou movimento lento e deliberado, sem handheld). Ver decisão na camada de recursos. |
| "Upscale RIA/Topaz entrega 4K real e economiza até 70%" | ❓ **[A MEDIR]** | `upscale_video` provider `topaz` existe (1080p/2160p), mas **não suporta preflight de custo**. Medir na primeira execução real antes de adotar como estratégia. |

### O que foi ABSORVIDO do guia (porque melhora o que já existe)

- **"Ativos primeiro" (AI Cast → Locations → Cameras → Video).** É a Fase 1 desta skill com outro
  nome. Convergência independente vale como confirmação.
- **CLEAN PLATE — melhora concreta ao Environment Sheet.** O guia manda gerar o cenário VAZIO, com
  `no people` no prompt, e salvá-lo como elemento reutilizável. Isso é mais acionável que a folha de
  referência de ambiente que a skill tinha: uma folha de referência descreve o lugar; um clean plate
  **é** o lugar, pronto para virar start frame. Adotado em `model-sheet-storyboard.md`.
- **MANUAL STYLE — travar paleta e grão entre clipes.** Resolve por parâmetro o que o Mood Sheet
  tentava resolver por condicionamento visual. Usar os dois: Mood Sheet ancora a intenção, Manual
  Style trava a execução.
- **AI Cast / Soul Cast como trava de identidade (0,12 cr).** MAS: o guia diz que ele entrega uma
  character sheet de **três ângulos** (frente, costas, close-up). O model sheet deste canal é mais
  rico de propósito — turnaround de 5 vistas, coluna de expressões, macros de detalhe, paleta. **AI
  Cast não substitui o model sheet; ele é a trava de identidade que roda por cima dele.** Usar os
  dois, nesta ordem: model sheet completo (contrato visual) → registrar como Element → AI Cast/Soul
  para consistência de rosto quando houver deriva.
- **Timestamps explícitos no prompt de vídeo** (`0-3s: … 3-6s: …`). A skill já faz isso com
  `[SHOT n]`. Confirmação externa da prática.
- **Soul Cinema (`soul_cinematic`) a 0,12 cr, com 21:9 nativo**, descrito como "cinema-grade stills".
  É **12x mais barato** que o Cinema Studio Image 2.5 e 12x mais que o Nano Banana 2. Candidato forte
  para stills de imagem única (model sheet, mood sheet, painel crítico avulso, frame-chave).
  **Ressalva:** modelos Soul são orientados a personagem/retrato — folha de storyboard é tarefa de
  LAYOUT (grid de 12–15 painéis, calhas rígidas), onde Nano Banana Pro / Seedream / GPT Image tendem
  a ser mais fiéis. Roteamento proposto: **Soul Cinema para imagem única, Nano Banana/Seedream para
  grid.** [A TESTAR]

### A regra operacional que sai disso — vale para TODA imagem, sempre

**Gerar sempre com `count: 4`.** Não custa mais nada [MEDIDO em três modelos diferentes]. Escolher a
melhor das quatro e descartar as outras. Isso vale para model sheet, environment sheet, mood sheet,
folha de storyboard, painel avulso e thumbnail — e faz a exigência do curso de "sempre duas opções de
thumbnail" virar quatro, de graça. Gerar `count: 1` em imagem passa a ser considerado erro de
operação, não economia.

---

## 7. REGISTRO EMPÍRICO — Higgsfield (preencher a cada teste real)

Mesma disciplina do `seedance-receituario.md`: nada aqui vira regra sem veredito do usuário.

- [~] **Fator de retrabalho — primeira medição real (19/08/2026): ~×1,2 em IMAGEM.** A galeria do
      Kairogen do projeto Cthulhu tem 50 gerações de storyboard para 41 cenas únicas → ~20% de
      regeração. Ressalvas: é imagem, não vídeo (vídeo erra mais), e a distribuição não é uniforme —
      `Collision Course` e `The Clash` foram regerados 3× cada, ou seja, cena de embate/colisão
      concentra o retrabalho. **Manter o orçamento em ×1,4 até haver medição de VÍDEO**, mas saber que
      o número pode cair para ×1,25 e liberar folga real no envelope.
- [ ] Seedance 2.5 em 30s: ele sustenta 30 segundos de dinamismo, ou repete o padrão "metade ótima,
      metade mediana" que o 2.0 fazia em 15s? (se repetir, o bloco de 30s pode ser pior negócio que
      dois de 15s pelo mesmo preço)
- [ ] Seedance 2.5 respeita `[SHOT n]` em texto, ou precisa do multi-shot como parâmetro?
- [ ] Cinema Studio Video (std vs pro): a diferença de 18 vs 24 créditos aparece na tela?
- [ ] Qualidade do Cinema Studio Video em bloco contemplativo vs Seedance 2.5 no MESMO bloco
- [ ] Element funciona com Seedance 2.5?
- [ ] Enhancer de prompt: ligado × desligado no mesmo bloco
- [ ] `video_extension` costura dois blocos sem emenda visível?
- [ ] Controles do Cinema Studio: quais realmente mudam o resultado e quais são decorativos
- [ ] 480p/720p/1080p: onde está o piso aceitável para o canal na TV e no celular
