# Como escrever um prompt para o Seedance 2.5

> Guia de método, autocontido. Escrito para ser lido por um modelo de linguagem que vai
> **escrever prompts de vídeo** para o Seedance 2.5 (Higgsfield).
>
> Origem: guia oficial de prompt do Higgsfield, 7 cursos da Higgsfield Academy, catálogo ao vivo
> da plataforma, e bibliotecas públicas de movimento de câmera e direção de atuação.
> Levantado em setembro de 2026.
>
> **Não** contém decisões de orçamento, de resolução ou de canal — só o que é sobre o modelo.

---

## 1. A REGRA QUE CARREGA TODAS AS OUTRAS

> ## Descreva o que você QUER ver. Nunca só o que não quer.

O modelo atende ao substantivo que você escreve, mesmo dentro de uma negação. Escrever
*"not a video game"* uma dúzia de vezes entrega um videogame — ele lê "videogame" doze vezes e
ignora o "not".

**Isso não proíbe a negativa. Proíbe a negativa ÓRFÃ.**

> **Toda negativa precisa de uma afirmação positiva da mesma restrição ao lado — de preferência
> antes dela.** Se você não consegue escrever a versão positiva, a negativa não deve entrar.

| ❌ Órfã | ✅ Acompanhada |
|---|---|
| `no shaky camera` | `locked-off tripod shot, no shaky camera` |
| `not a video game` | `35mm anamorphic, natural contrast, visible film grain — no video-game look` |
| `he's not crying` | `an anxious look, jaw tight, eyes dry — not crying` |
| `no music` | `diegetic room tone only — no music, no subtitles` |

O guia oficial do Higgsfield segue esse padrão sem exceção — e o bloco onde ele guarda suas
negativas chama-se, literalmente, **`POSITIVE LOCKS:`**. Ele não chama aquilo de negativa. Chama
de trava.

---

## 2. FORMATO: PROSA COM SEÇÕES ROTULADAS — não JSON

O modelo espera **prosa contínua, com seções em caixa alta**. Nenhuma fonte primária recomenda
JSON para o Seedance.

```
GLOBAL STYLE   → gênero, grade de cor, película/digital, proporção, obturador
SCENE          → uma linha de logline
CHARACTERS     → cada pessoa: rosto, cabelo, porte, figurino
LOCATION       → o espaço e os objetos, separado das pessoas
FIRST FRAME AND BLOCKING → posições exatas no instante zero, quem está onde, virado para onde
Shot 1..N      → tipo de plano + ação em uma ou duas frases, terminando em "Hard cut"
OPTICS and CAMERA → lente, altura de câmera, movimento, por plano
PHYSICS        → tecido, fumaça, cabelo, líquido
LIGHTING       → fonte motivada, direção, como cai no rosto
AUDIO          → ambiência, efeitos, e o que não deve existir
POSITIVE LOCKS → o que precisa permanecer verdadeiro do começo ao fim
```

> *"Most working Seedance 2.5 prompts follow the same shape: one visual rule at the top, one sound
> rule at the bottom, and everything in between broken into shots."*

**Se você trabalha com estrutura interna (campos, template, geração em lote), tudo bem — mas
serialize para esta prosa na hora de entregar.** O formato em que se pensa não precisa ser o
formato em que se entrega.

---

## 3. TAMANHO: NÃO EXISTE TETO CONHECIDO

- Nenhum modelo do Higgsfield declara limite de caracteres no schema.
- Os **10 prompts do guia oficial** medem de **1.020 a 7.084 caracteres**, mediana ~6.300 —
  **8 dos 10 passam de 5.000.**
- Prompts de quatro páginas são normais entre quem acerta.

> **O prompt é tão detalhado quanto a cena precisar. Nem teto, nem piso.**
>
> ⚠️ A ressalva que continua valendo: **prompt longo e vago é pior que prompt curto e preciso.**
> Os prompts oficiais são longos porque são **densos** — medidas, segundos, negativas acompanhadas
> — não porque são prolixos.

---

## 4. PARÂMETRO NÃO É TEXTO DE PROMPT

> *"Generation parameters are not prompt text."*

Resolução, duração e proporção **se escolhem no gerador**. Escrevê-las na prosa não faz nada — e
faz o texto disputar com o parâmetro. O mesmo vale para qualquer controle que a interface ofereça.

---

## 5. NÚMERO E COMPARAÇÃO NO LUGAR DE ADJETIVO

> *"Video models prefer arithmetic over vague words like 'dramatically'."*
> *"AI models don't really get big descriptions, but they understand direct comparisons."*

| ❌ | ✅ |
|---|---|
| "a câmera se aproxima dramaticamente" | "órbita de 8 m para 4 m, altura de 3 m para 2 m" |
| "rápido" | "três vezes mais rápido que um dolly cinematográfico típico" |
| "ele se levanta" | "mão no chão em 0,5 s, elmo erguido em 1,5 s, de pé em 3 s" |
| "a criatura é enorme" | "a cabeça dela ocupa 40% da altura do quadro" |
| "ela se transforma" | "0,4 s, snap seco — arma sendo sacada, não magia" |

> *"When the timing is locked, the model can't rush it or skip stages."* O número não é
> preciosismo: é o que impede o modelo de pular etapa.

**Duas travas de vocabulário:**
- **Nunca escrever idade em palavra nem em número.** Use papel, porte, roupa e ação — o modelo
  responde melhor e para de puxar para o rosto jovem arredondado.
- **Nomeie o personagem por marcador visível**, nunca pelo handle da referência. Escreva *"o homem
  de capa vermelha"*, não *"@Image 1"* nem *"Personagem A"*. O handle serve para declarar a
  referência; a linha de ação precisa de algo que exista no quadro.

---

## 6. REFERÊNCIAS: PAPEL + EXCLUSÃO + GRAU

Cada referência declara **três** coisas, não uma:

| Campo | Exemplo |
|---|---|
| **Papel** | `@Image 1 defines the man's face and proportions` |
| **Exclusão** | `Do not recast. Do not beautify. Do not use as an image background. Do not take the studio backdrop, the sheet layout, any labels or the palette strip.` |
| **Grau de fidelidade** | `full-preserve` · `partial-preserve` · `attribute-transfer` (nomeando o alvo) · `loose-guide` |

**Sem o grau, tudo vira full-preserve** e as âncoras brigam entre si.

> ⚠️ **A armadilha mais comum:** passar uma folha de personagem (character sheet) como referência
> **sem exclusão**. O modelo não sabe que o fundo de estúdio e os rótulos são artifício de
> produção — para ele aquilo é o cenário, e a tipografia é texto que existe no mundo. Sintomas:
> fundo virando estúdio liso, texto inexplicável no quadro, personagem duplicado em várias vistas.
>
> **`do not recast`** é a frase mais importante das três: impede o modelo de trocar a pessoa por
> outra parecida.

**Detalhe pequeno na folha vira ruído no vídeo.** Adorno miúdo e destacado (chapéu pequeno, brinco,
fivela) degrada a geração e pode até arrastar a identidade junto. Ou o detalhe é grande e
definidor, ou sai da referência.

---

## 7. STAGES: SEGUNDOS SÃO ORÇAMENTO, NÃO PONTO DE CORTE

Multi-shot dentro de um prompt, com segundo de início, nome do segmento, o que acontece e como
está enquadrado:

```
Shot 1 (0–9s) — "the approach" — wide establishing, the figure enters from frame-left. Hard cut.
Shot 2 (9–15s) — "the recognition" — tight close-up on the face. Hard cut.
```

**Nomear cada stage** dá ao modelo um identificador por segmento em vez de um bloco corrido.

⚠️ **Os timestamps alocam duração; não marcam frame exato.** Não pendure uma batida dramática num
segundo específico, e não trate divergência de meio segundo como falha do prompt.

**Declare o END STATE de cada segmento** — onde os corpos estão, para onde olham, o que seguram no
último instante. É o que amarra o corte seguinte.

---

## 8. CÂMERA: QUATRO CAMPOS

Toda instrução de movimento se escreve assim:

```
[NOME DO MOVIMENTO].
Movement: [o que a câmera faz fisicamente]
Speed:    [o ritmo, descrito — não adjetivado]
Framing:  [o que precisa CONTINUAR LEGÍVEL durante o movimento]
End:      [onde o movimento assenta]
```

Exemplo:
> **pan right.** Movement: rotate the camera horizontally from left to right from one fixed point.
> Speed: smooth constant rotation. Framing: keep the horizon level while new space enters from the
> right side of the frame. End: settle on a clear final composition.

**`Framing` não é o enquadramento inicial** — é o que não pode se perder *enquanto* a câmera se
move. **`End` é onde o movimento assenta.** Os dois são os campos mais esquecidos e os que mais
mudam o resultado.

### Altura da câmera: pense em metros, depois converta

| Altura | Frase a escrever |
|---|---|
| até ~0,95 m | *a low knee-level angle looking up at the subject* |
| 0,95–1,25 m | *a low hip-level angle* |
| 1,25–1,50 m | *chest level* |
| 1,50–1,80 m | *eye level* |
| 1,80–2,50 m | *a high angle looking down at the subject* |
| acima de 2,50 m | *a directly overhead bird's-eye view looking down at the subject* |

### Tamanho de plano = ORÇAMENTO DE DETALHE

O tamanho não é só enquadramento: diz ao modelo **onde gastar resolução**. Escrever o tamanho sem
a cláusula deixa essa decisão com o gerador.

| Tamanho | Cláusula a colar junto |
|---|---|
| extreme close-up | *ultra-realistic skin texture with visible pores and micro-detail, tack-sharp eyes, shallow depth of field* |
| close-up | *ultra-realistic skin texture and fine facial detail, soft background blur, shallow depth of field* |
| medium shot | *balanced detail on the subject and the surrounding space, moderate depth of field* |
| wide shot | *full body in a richly detailed environment, deep focus* |
| extreme wide shot | *a small figure within a vast, highly detailed environment, epic sense of scale, deep focus* |

### Eixo de 180°: escreva DENTRO do prompt

Não basta respeitar o eixo ao planejar — o modelo precisa ser informado dele, ou reposiciona a
câmera no corte:

```
180-degree axis held for the entire scene; [A] always framed from camera-left, [B] always from
camera-right; cut to [B] over [A]'s left shoulder; no drift mid-segment; horizon level.
```

---

## 9. ATUAÇÃO: DESCREVA O CORPO, NUNCA NOMEIE A EMOÇÃO

"Ele está com raiva" é adjetivo. Isto é direção:

> *The eyebrows slam down and inward, the upper lip peels back from the teeth, the nostrils flare,
> the neck tendons tighten, and the head pushes forward. The snarl holds as hard breaths move
> through the nose.*

**O padrão:** uma cadeia de micro-ações ordenadas, terminando num estado que se sustenta.

Para ação física, a mesma coisa em cadeia:
> *riding with loose shoulders and a broad smile → [footstep] → he loses the smile and tightens the
> fingers → looks behind slowly and reluctantly → freezes and screams involuntarily → pedaling with
> frantic uneven force → covering his mouth, remaining rigidly still → then releases one shaky breath*

**Emoção precisa de gatilho:** descreva *o que causa* a emoção (um som, um objeto, uma revelação),
não só a emoção. Emoção sem causa no quadro é adjetivo disfarçado.

---

## 10. DIÁLOGO: TRÊS TEMPOS

| Bloco | O que escrever |
|---|---|
| **Stage** | onde se passa e quem está lá — *"they're alone in the house, no one else is present"* |
| **Primary event** | o que acontece, com a atuação dentro — *"the man speaks first, quiet and broken, eyes wet, struggling to get the words out. Before he can finish, the woman cuts him off sharply, her face already tight with anger"* |
| **End state** | onde termina — *"him mid-sentence and glassy-eyed, her jaw clenched"* |

Cinco coisas por fala: **ação · palavras exatas · mudança de tom · pausas · emoção.**

**Sotaque, em cinco campos:** nomear o falante → região → ritmo → energia → estado emocional → a
fala exata.
> *"He speaks English with an unhurried Kingston accent, natural, not exaggerated, not a comedy
> voice. When the shock hits, the voice jumps and the words get short."*

Repare: a voz muda **por gatilho**, não é um preset constante.

---

## 11. SOM

| Símbolo | Para |
|---|---|
| `( )` | música |
| `< >` | efeito sonoro |
| `{ }` | diálogo |
| `【 】` | legenda |

**Diegético** = o que os personagens ouvem. **Não-diegético** = música e efeitos que só o público
ouve. O nível de detalhe que funciona é alto:

> *"Each step produces one closed rubber sole squeak followed immediately by one small wet splash
> beneath the corresponding foot."*
> *"A hard non-diegetic sub-bass hit that lands on the exact frame the light goes dark."*

---

## 12. CONTINUIDADE ENTRE CENAS: TRÊS ENTRADAS, NÃO UMA

| Entrada | Para onde vai | Para quê |
|---|---|---|
| **Prompt da cena anterior** | para o modelo de linguagem | para quem escreve saber o que acabou de acontecer |
| **Keyframe da cena anterior** | como referência de estilo | trava luz, paleta e textura |
| **Vídeo anterior** | para o Seedance | trava movimento e emenda |

**Trava de pose no corte:** *"The poses at the end of shot one exactly match the start of shot two.
If you don't spell this out, the AI treats the cut as a brand new scene and throws away the poses."*

**Plano aberto no início trava a marcação:** *"Start the video with a wide establishing shot. That
way Seedance places everyone exactly where they need to be and they stay locked for the entire
video."*

**Cena com contracampo exige referência de ambiente dos DOIS lados.** Com uma vista só, o modelo
inventa o que está atrás do personagem — e inventa diferente a cada geração. É a causa do fundo
que "pula" entre cortes.

---

## 13. REALISMO É IMPERFEIÇÃO

O erro mais comum não é falta de qualidade — é **excesso de polimento**. Pele perfeita, simetria
perfeita, rosto de catálogo: tecnicamente realista, humanamente falso. É o vale da estranheza.

**Imperfeição é especificação, não defeito tolerado.** Nomeie pelo menos três: olheira, ruga,
assimetria, entrada de cabelo, pele não uniforme, cicatriz, dente torto.

Bloco pronto para personagem fotorrealista:
> *visible fine skin texture with natural pores, fine lines, subtle asymmetries and texture
> irregularities, natural visible makeup with slightly uneven blending rather than flawless
> coverage, slight natural sheen rather than glossy retouched finish, no digital smoothing, no
> beauty filter, no AI-airbrushed look, matte-to-natural complexion*

E a cláusula anti-brilho no olho, que resolve um defeito recorrente:
> *naturally muted catchlights, no oversized specular glare in the iris, eye color muted rather
> than glowing*

---

## 14. QUANDO SAI ERRADO: DIAGNOSTICAR ANTES DE REESCREVER

> ### Gere mais de um take. 4 de 4 errados = o problema é o PROMPT. 1 ou 2 errados = foi sorte.

*"Knowing the difference between a broken prompt and a bad roll is how you save credits."*

Sem essa régua, reescreve-se prompt que estava certo — o caminho mais caro que existe.

**Escada de correção, do mais barato ao mais caro:**
1. Recortar o melhor quadro da tentativa e usá-lo como referência da próxima.
2. Multi-shot falhou → cair para **um plano contínuo**.
3. Cena apertada → **partir em duas**.
4. Plano chapado → **aumentar a cobertura** (2 planos viram 3, com ângulos diferentes).
5. Remover uma referência (âncora demais briga entre si).
6. **Só então** reescrever o texto.

*"That's the actual skill in this workflow. Not writing one genius prompt, but reading what broke
and fixing only that."*

**Mudança de estado resolve-se com ASSET, não com texto.** Roupa rasgada que "se remenda" no plano
seguinte → gere uma nova referência já com a roupa rasgada. Vale para ferimento, sujeira,
transformação parcial, envelhecimento.

---

## 15. COMO SABER SE O TAKE PASSA

**O sinal mais importante:** *"Watch how it cuts. Fast, chaotic, new angle every second. It's
hiding. Quick cuts are what this model does when it can't animate the motion underneath."*

> **Corte rápido que você não pediu é rejeição.** Não é estilo — é o modelo escondendo movimento
> que não conseguiu animar.

**Reprova também:** golpe que não deixa marca · personagem que "é deletado" em vez de morrer
(*"one frame he's there, next frame he's gone"*) · membros que se atravessam em movimento rápido ·
postura que "reseta" entre passos · cicatriz ou roupa que muda entre planos · olhar perdido ·
plano que acaba antes da batida dramática.

**Olhar com atenção, mas não reprova sozinho:** rosto sob esforço (gritar é onde rostos de IA
quebram) · fisheye falso (*"the edges curve and nothing else does — more of a filter than a
lens"*) · brilho que "vira mingau" quando a cabeça gira · luz que não bate entre os cortes.

*"Each one is pretty minor, but together, they're the difference between an ad and an AI ad."*

---

## 16. AÇÃO E MULTIDÃO

**Faça o blueprint antes do movimento** — e ele custa zero: um desenho tosco de quem está onde e
por onde entra o golpe resolve o que parágrafo nenhum resolve. *"One drawing tells the model what
10 sentences can't."*

**Uma regra física dura, declarada:** *"Skip 'sword clash' and map out the angles. The vertical
chop meeting a diagonal parry. Set one hard rule. Crystal always beats steel."* Sem ela, os dois
materiais empatam.

**Multidão: nunca peça número.** *"The prompt never says 'show a thousand soldiers'. It just fills
the frame in three layers. One sharp warrior up front, a dense crowd behind him, and silhouettes
fading into the mist."* Pedir "50 soldados" dá contagem errada e rostos derretidos.

**Figurante se constrói por CLASSE**, não como massa — dois ou três arquétipos distintos dão
variedade de silhueta e mantêm consistência.

**Névoa é a limpeza mais barata que existe.** Limitar a visibilidade a ~20 m esconde exatamente
onde o modelo quebra, que é o fundo lotado. *"If your scene is packed, fog is the cheapest cleanup
you'll ever do."*

**A cura do "cara de videogame":** *"One long, unbroken take is exactly how video games look. Real
movies cut."* A cura é cobertura variada dentro do plano gerado — quatro cortes secos, cada um com
sua ótica. E o sintoma a evitar: **câmera flutuando atrás do personagem** é enquadramento de jogo
em terceira pessoa.

---

## 17. PÓS-PRODUÇÃO: QUATRO AJUSTES QUE CUSTAM ZERO

1. **Corte fora o slow-motion** que o modelo inventa — ele quebra a credibilidade.
2. **Zoom in/out no editor** (100% → 120% lento) para dirigir a atenção sem gastar geração.
3. **RUÍDO — é o que mais entrega.** Uma pitada de grão é o antídoto do "plástico demais".
4. **Blur leve nas bordas** e **barras de cinema** (10–15%).

Somados, são a versão barata da regra de acúmulo: cada um é pequeno, juntos mudam a leitura.

---

## RESUMO EM DEZ LINHAS

1. Descreva o que quer. Negativa nunca aparece sozinha.
2. Prosa com seções em caixa alta. Não JSON.
3. Sem teto de tamanho — mas denso, não prolixo.
4. Parâmetro não vai no texto.
5. Número e comparação no lugar de adjetivo. Nunca escreva idade.
6. Referência declara papel + exclusão + grau. `do not recast` sempre.
7. Câmera em quatro campos: Movement · Speed · Framing · End. Altura em metros.
8. Atuação é o corpo descrito, nunca a emoção nomeada.
9. Declare o END STATE de tudo — do movimento, do segmento, da fala.
10. Gere mais de um. 4/4 errados é prompt; 1 ou 2 é sorte.
