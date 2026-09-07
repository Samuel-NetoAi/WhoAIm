# Receituário Seedance — observações empíricas

Padrões observados em produção real do canal. NÃO são teoria de cinema genérica — são o que o Seedance
faz de fato com cada tipo de instrução. Atualizar conforme novos testes. O que não foi testado fica
marcado como HIPÓTESE, não como regra.

> **AVISO DE ESCOPO (ago/2026).** Tudo abaixo foi observado no **Seedance 2.0, em blocos de 15s, via
> Leonardo**. A produção migrou para **Seedance 2.5 (até 30s) no Higgsfield** — plataforma diferente,
> versão de modelo diferente, duração diferente. **Nenhum padrão daqui está automaticamente válido no
> 2.5**, e três deles têm motivo específico para serem reavaliados primeiro:
> 1. **"Metade ótima, metade mediana" dentro do bloco** — se o efeito se repetir num bloco de 30s, o
>    bloco longo é pior negócio que dois de 15s pelo mesmo preço. É o teste nº 1 a fazer.
> 2. **"Perda de dinamismo ao seguir o start frame"** — pode ter sido corrigido na versão nova.
> 3. **"Imagem-referência sobrescreve atmosfera"** — o Higgsfield aceita muito mais referências e tem
>    Elements; o comportamento pode ser outro.
> Os itens de **densidade de painel/composição** (duplicação, co-presença, simetria, delta entre
> intermediários) são sobre como o gerador LÊ a folha de storyboard e continuam sendo a aposta mais
> segura de permanecerem válidos. Ao usar qualquer regra daqui num prompt do 2.5, tratá-la como
> hipótese até o primeiro veredito real e registrar o resultado.
> Custos, limites e o que é parâmetro em vez de texto: `higgsfield-cinema-studio.md`.

---

## O QUE FUNCIONA (confirmado em teste)

- **Plano-sequência único de luta — TESTADO SÓ COM HUMANOS COMUNS (corpo a corpo, sem poderes):**
  ótimo resultado. Alucina raramente. Para esse tipo de cena, 1 ou 2 cortes no máximo — não fragmentar muito.
  ATENÇÃO ao escopo: luta entre CRIATURAS, ou entre seres com superpoderes (energia, voo, escala
  gigante, destruição de cenário), NÃO foi testada — não estender esta regra para esses casos.
  Tratar como HIPÓTESE H7 (abaixo) até o primeiro teste real.
- **Plano-sequência focado em um elemento isolado (ex: mão da criatura cortando o ar/chuva, água pingando,
  impacto na água):** excelente quando o foco é UM elemento fechado e a câmera acompanha só ele.

## O QUE FALHA OU É ARRISCADO (confirmado em teste)

### 1. Perda de dinamismo ao seguir o start frame — o problema mais grave
O Seedance trata o start frame como âncora e tende a DESACELERAR o movimento para não se afastar dele.
Sintomas reais observados:
- Tentáculos chegam violentos, mas depois seguram os personagens parados como "bonecos".
- O puxão para dentro do portão (que era pra ser veloz) saiu lento; personagens "encolheram" em vez de
  serem arrancados com força.
- Personagens capturados ficavam quase estáticos, só com micro-tremores de pavor.

**Mitigações no [ACTION]:**
- Declarar movimento CRESCENTE e contínuo: "velocity increases throughout", "no slowing, no settling, no freezing".
- Descrever a violência do movimento em cada beat, não só no início.
- Para captura/arrasto: "yanked violently and instantly out of frame", evitar "pulled" (sai lento).

### 2. Posição do pico dentro dos 15s
Padrão recorrente: o bloco entrega ~metade excelente e ~metade mediana (7 ótimos + 8 medianos, ou o inverso).
**Mitigação preferida (respeita a economia de tokens — ver abaixo):** posicionar o momento de PICO no
início do bloco, onde o Seedance tem mais energia, e usar os segundos finais para a saída/resolução do
movimento. Não colocar o clímax nos últimos segundos, onde ele desacelera.
**HIPÓTESE reaberta pelo Higgsfield:** encurtar o bloco de pico. No Leonardo isso era desperdício
(4 prompts de 15s por crédito, encurtar não devolvia nada). **No Higgsfield o preço é por segundo**
[MEDIDO: Seedance 2.5 = 6,5 cr/s em 720p], então bloco curto custa proporcionalmente menos e a objeção
econômica desapareceu. Passa a ser teste legítimo e barato: dois blocos de 15s custam exatamente o
mesmo que um de 30s, e dão duas aberturas de alta energia em vez de uma. Testar antes de padronizar
30s em bloco de ação.

### 3. Imagem-referência sobrescreve atmosfera/cenário pedidos
Quando se envia o modelo de um personagem/criatura, o Seedance prioriza replicar o modelo e IGNORA instruções
de cenário (ex: pediu "Cthulhu sobre névoa densa", veio o modelo limpo sem névoa — e o modelo parecia "bonequinho").
**Mitigação:** atmosfera e ambientação vão no START FRAME (prompt de imagem do ChatGPT, Documento 2), não confiadas
ao texto do Seedance. Se a névoa tem que estar lá, ela tem que estar na imagem de referência.

### 4. Duplicação do personagem de referência — CAUSA RAIZ CONFIRMADA: densidade de composição
Diagnóstico refinado em produção (Cthulhu, bloco do ataque): a duplicação/alucinação acontece quando o
PAINEL do storyboard tem composição complexa — múltiplos sujeitos e ações no mesmo quadro ("três homens
agarrados por tentáculos simultaneamente"). O Seedance não lê composições densas e inventa, repetindo
personagens. Ocorre com um ou vários personagens, geralmente em um momento do vídeo (não os 15s inteiros).
**Mitigação — no Documento 2 (storyboard/ChatGPT), confirmada em teste:**
- UM sujeito, UMA ação por painel. Composições simples, focadas e legíveis.
- Ação complexa = MAIS painéis simples ("um tentáculo, um homem" em quadros separados), nunca um painel denso.
- Refazer o bloco do ataque com 6 painéis simples e descrições ricas FUNCIONOU.
- Sem timestamps desenhados nos quadros ("No timestamps on the panels") — confundem a leitura.
- Nunca repetir o mesmo personagem em painéis adjacentes com pose/enquadramento similar.
- Personagem de fundo que não precisa de consistência: NÃO enviar referência dele (deixar genérico).

---

## HIPÓTESES DE MATERIAL EXTERNO (Seedance 2.0 — NÃO testadas no canal)

Fonte: guias/resumos de terceiros sobre Seedance 2.0 (jun/2026). NADA daqui é regra.
Cada item vira regra SÓ depois de teste real em bloco do canal — aí migra para "O QUE FUNCIONA"
ou é deletado. Ao usar uma hipótese num prompt, avisar o usuário explicitamente que é teste.

### Hipóteses a testar (compatíveis com o fluxo Leonardo/15s)

- **H1 — Logic Rules (PRIORIDADE BAIXA — só se o problema aparecer):** linha final no prompt
  declarando o que NÃO pode mudar entre shots. Relato do usuário: o Seedance JÁ mantém aparência de
  personagem e cenário sem isso. O teste só faz sentido para continuidade de AÇÃO/objeto entre cortes
  (ex: "segura a lanterna em todos os shots") e SÓ se uma inconsistência for observada. Não gastar
  caracteres com isso preventivamente.
- **H2 — Character sheet com FUNDO BRANCO:** ao gerar a bíblia de personagens (frente/perfil/costas),
  pedir fundo branco no ChatGPT. Tese: isola a geometria facial e reduz interferência de cenário no
  mapeamento. Compatível com a regra existente da bíblia — muda só o fundo.
- **H3 — Grade 2x2 de variações faciais:** se um rosto for bloqueado por filtro de segurança,
  enviar grade 2x2 com variações em vez da foto única. Só testar SE o bloqueio acontecer.
- **H4 — Interpolação "in-between":** frame inicial + frame final + prompt "show me what happens
  in between". VIÁVEL: o Leonardo aceita até 4 imagens de referência no Seedance. Útil para
  transições difíceis de descrever (metamorfose, deslocamento grande entre dois estados).
- **H5 — Arco emocional implícito:** em vez de descrever a expressão ("rosto de pavor"), descrever a
  situação ("ele percebe que a porta está trancada") e deixar o modelo inferir a emoção.
  Pode economizar caracteres no [ACTION].
- **H6 — Plural para forçar cortes:** "cinematic camera angles" (plural) induziria multi-shot.
  Provavelmente REDUNDANTE — a estrutura [SHOT n] já força os cortes. Só testar se o modelo
  estiver fundindo shots que deveriam ser separados.
- **H7 — Luta entre criaturas / seres com superpoderes:** território totalmente não testado.
  No primeiro bloco desse tipo, testar primeiro o plano-sequência (transferindo a regra da luta
  humana) e, se alucinar, cair para a fragmentação da heurística de ação (4–6 cortes secos,
  um elemento por shot). Registrar o resultado aqui.

### Conflitos registrados (regra atual do canal VENCE até teste provar o contrário)

- **"Sweet spot de 5–7 cenas em 15s"** (material externo) vs. heurística testada do canal
  (luta humana = plano-sequência 1–2 cortes; transformação = 2–3 shots longos). A heurística
  do canal vem de teste real; o "5–7" é média genérica. Manter a heurística.
- **"Use negative prompt"** (material externo) vs. regra do canal "NUNCA usar bloco
  [QUALITY AND RESTRICTIONS]". Manter a regra do canal.

### Registrado e descartado (não se aplica ao fluxo atual)

- **Features "de outra plataforma" — o item inteiro caducou (reescrito limpo em set/2026).**
  Este item existia para dizer que durações de 50s, "Step into Set"/Martini, Multiplayer e o limite
  de ~3.500 chars eram coisa do Higgsfield e portanto irrelevantes para nós, que estávamos no
  Leonardo. **A premissa virou do avesso: a plataforma agora É o Higgsfield.** O que vale hoje:
  - **Limite de caracteres: não existe teto conhecido.** O 1.494 morreu com o Leonardo; o ~3.500
    nunca teve lastro (🟢 catálogo ao vivo 02/09/2026 não declara `maxLength` em modelo nenhum;
    10 fontes varridas, 4 oficiais, o número não aparece em nenhuma); e o 5.000 era sobre o modo de
    vídeo longo de 180 s, não sobre o prompt normal. 🎓 8 dos 10 prompts do guia oficial passam de
    5.000. Ver `higgsfield-cinema-studio.md`, seção 6.
  - **Duração:** blocos podem ir a 30s no Seedance 2.5. O slot fixo de 15s do Leonardo morreu.
- **`end_image`, `video_extension` e `multi_shots` deixaram de ser "features de outra plataforma" e
  passaram a ser recursos disponíveis** — H4 (interpolação entre frame inicial e final) é nativa
  agora. Ver seção 6 da referência de plataforma.
- ~~**Tradução do prompt para chinês** (compressão de caracteres): último recurso, nunca padrão.~~
  **MORTO em set/2026.** Existia só para caber num teto que não existe mais. Comprimir prompt para
  economizar caractere deixou de ser um problema a resolver — e o custo (o usuário perde a capacidade
  de revisar o próprio prompt) nunca teve contrapartida.
- **HandBrake (reexportar MP4 30fps):** só relevante para upload de VÍDEO de referência
  (video-to-video/VFX). O fluxo do canal usa IMAGEM como start frame. Guardar como nota: se um dia
  um upload de vídeo falhar na renderização, reexportar via HandBrake antes de culpar o prompt.
- **Sintaxe @image1:** o canal usa `[IMAGE 1 as first frame]`, que funciona. Não trocar sem motivo.

---

## REGRA DE PRODUÇÃO — BÍBLIA DE PERSONAGENS (antes da primeira cena)

Decisão do usuário: antes de produzir qualquer bloco, definir TODOS os personagens recorrentes da história e
gerar um modelo de cada um em várias posições, para usar como referência consistente ao longo do vídeo.
Fazer isso no checkpoint, junto da aprovação do roteiro. Sem a bíblia de personagens definida, não começar os blocos.

---

## TIMING — luta vs. impacto vs. contemplação (resumo acionável)
- Luta humana: plano-sequência, 1–2 cortes. Não fragmentar.
- Impacto de criatura / pico de ação: pico no INÍCIO do bloco, [ACTION] com aceleração contínua.
- Contemplação/revelação estática: shots longos, poucos cortes (ver heurística no SKILL.md).

## Padrão observado — start frame no meio da ação (jul/2026, produção Dullahan/padre)
- O Seedance trata o painel 1 do storyboard como frame literal de abertura: se o painel 1 mostra a
  ação em curso (ex.: santuário já tombando), o vídeo COMEÇA do meio — o início da ação não existe
  para ele reconstruir. Mitigação na origem: regra dura do painel 1 pré-ação
  (model-sheet-storyboard.md) — painel 1 sem o verbo da ação, tableau intacto.
- Sintoma associado: blocos com painéis que mostram todos o mesmo estado (só "melhores momentos")
  saem estáticos — sem mudança de estado entre keyframes, o modelo não anima. Mitigação: contagem
  de estados (antes → contato → pico → consequência) define os painéis; [SHOT 1] segura o estado
  inicial ~0,5–1s; [ACTION] descreve o movimento contínuo entre keyframes.
- Elementos "ao fundo" migram para a frente do quadro se não forem comandados por tamanho/foco/luz
  ("tiny in frame, far background, out of focus, half-hidden in shadow").

## Decisão de produção — storyboards densos (jul/2026, empírica do usuário)
- Observado em produção: o Seedance NÃO interpola o entre-cenas de folhas esparsas — storyboards
  de 3 painéis geraram vídeo quase estático, mesmo com estados distintos entre keyframes.
- Decisão do usuário: piso de 6 painéis, teto 10, compostos como keyframes + INTERMEDIÁRIOS
  (mesmo enquadramento dentro do shot, ação avançada; ângulo muda só na fronteira de shot).
- Tripwire de reversão parcial: se painéis pequenos começarem a alucinar/perder fidelidade com o
  piso de 6, a escada é: simplificar composições → painel crítico avulso em resolução cheia →
  só então rediscutir o piso.

## Padrão observado — viés de retrato em painéis de 2 sujeitos (jul/2026, produção da Besta)
- Sem eixo de relação declarado, o gerador compõe 2 sujeitos lado a lado, ambos de frente para a
  câmera ("como amigos"), mesmo em cena de confronto. "Encarando de frente" vira "facing front"
  (de frente para a câmera) na tradução do prompt — ambiguidade que causa exatamente isso.
- Mitigação: geometria de relação obrigatória (model-sheet-storyboard.md) — posição no quadro +
  direção do olhar + distância por sujeito; confronto = OTS ou perfil contra perfil.

## Padrão observado — micro-mudança fisiológica não é delta suficiente (jul/2026, produção Sobek)

Confirmado em produção (blocos "Os Olhos Que Vigiam" e "A Mandíbula Que Não Escolhe",
contemplativos): painéis intermediários descritos com mudança FISIOLÓGICA sutil — pupila
contraindo, peito expandindo com a respiração, tensão muscular sob a pele — saem como
quase-duplicatas visuais. O gerador não tem resolução para diferenciar esse tipo de variação em
fotos estáticas, mesmo quando o prompt declara a mudança explicitamente.

**Sintoma:** dois painéis do mesmo shot, mesmo enquadramento, mesma pose — visualmente
indistinguíveis mesmo com estados "diferentes" no texto do prompt.

**Regra corrigida:** em pares de painéis contemplativos/lentos (piso de 6, exceção de
transformação ou revelação estática), o delta entre intermediários do MESMO shot precisa ser um
dos dois tipos:
- BINÁRIO: presença/ausência clara, nunca gradação (ex.: pálpebra ABERTA vs FECHADA, não "pupila
  contrai"; água AUSENTE vs gota já formada e nítida em outra posição, não "gota começando a se
  formar").
- AMBIENTAL: algo entra/sai do quadro ou o ambiente muda de forma óbvia (um pássaro cruza ao
  fundo, a sombra alonga porque o sol desceu, uma ondulação cruza a água) — nunca o corpo do
  sujeito sozinho fazendo um micro-movimento fisiológico.

Micro-movimento fisiológico (respirar, pupila, tensão de músculo) só funciona como delta em ECU
quando o PRÓPRIO movimento É o assunto do painel (ex.: mandíbula abrindo — mudança grande e
estrutural, não sutil) — nunca como o único delta entre dois painéis largos/médios ou entre dois
ECUs de repouso.

**Retrofit (correção de acervo já gerado):** editar o painel isolado, não a folha inteira —
reforçar o delta como binário/ambiental explícito. Ex.: "remove ALL trace of X, completely
absent" no painel "antes"; "X now fully present/changed, unmistakably different position/state"
no painel "depois".
- Bloco de transformação saiu com 2 shots/1 eixo: obediência à exceção de transformação (que regia
  enquadramento em vez de ritmo) + autoavaliação que punia só variedade, não monotonia. Corrigido:
  plano de cobertura obrigatório (≥3 tamanhos de plano, ≥1 insert ECU), exceção reescrita para
  reger ritmo, autoavaliação bilateral, Lei dos Detalhes e fraseado de movimento Seedance
  (direcao-cinematografica.md).

## Padrão observado — co-presença total + frontalidade (jul/2026, folhas Nero e Dullahan)
- Com 2 personagens importantes, o gerador (e o executor da skill) colocou ambos em TODOS os
  painéis, de frente para a câmera, sem reação corporal — inclusive com ameaça chegando por trás
  (o corpo deveria estar de costas/meia-volta). Mitigações: População do quadro (singles/closes de
  reação obrigatórios), orientação motivada do corpo, regime declarado do bloco, e templates de
  retrofit para acervo antigo (model-sheet-storyboard.md).

## Regra fixa — sem música no Seedance, só SFX (jul/2026, caso Medusa/abertura da águia)
- O Seedance insere trilha de fundo por conta própria mesmo sem pedido (ex.: música "esperançosa"
  sob a águia sobrevoando a Grécia). Proibido a partir de agora: trilha é decidida holisticamente
  no Documento 7 (Suno, pós-produção) — música por bloco não conversa entre blocos e corta feio ao
  concatenar. Todo prompt Seedance inclui "No music. No score. No soundtrack. Sound effects only."

## Padrão observado — simetria de confronto vazando para cena mundana (jul/2026, caso porta da cabana)
- A regra de geometria de relação (perfil×perfil) resolveu o viés de retrato do caso Besta, mas
  virou novo default rígido: duas figuras espelhadas mesmo em cena SEM hostilidade (visitante e
  anfitriã numa porta) — lê como duelo, não como encontro comum. Mitigação: classificar a intenção
  da cena antes de encenar — confronto hostil/épico usa simetria proposital (OTS ou perfil×perfil
  espelhado); encontro social/cotidiano exige assimetria deliberada (ângulos diferentes, peso de
  corpo desigual, profundidade desigual entre as duas figuras) — ver model-sheet-storyboard.md,
  "Intenção da cena decide simetria ou assimetria".
