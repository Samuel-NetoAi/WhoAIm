# Atuação, diálogo e som — dirigir o ator, não só a câmera

> Criado em **2026-09-02**, do vídeo 🎥 *"master AI realism"* (`https://youtu.be/Zo8KaTs0l6k`),
> transcrito na íntegra. Preenche um buraco: o corpus dirigia **câmera e luz** com profundidade e
> tratava **atuação** como uma linha solta no bloco CAMERA + PERFORMANCE.
>
> ⚠️ **Proveniência:** o vídeo é **patrocinado pelo Higgsfield** e ele declara isso. Método
> atravessa; **recomendação de modelo é colocação paga** e está marcada como tal abaixo.

---

## 1. A TESE — realismo é IMPERFEIÇÃO, e é por isso que o nosso "polido" sai falso

🎥 O vídeo abre pelo **vale da estranheza** (*uncanny valley*) e o argumento é direto:

> *"That is the thing that most people overlook when making AI images because **it's too polished,
> it's too perfect.** And that's when you miss that spot. (…) **realism is imperfection**."*

**O que isso corrige no nosso corpus:** a nossa **âncora de realismo** persegue realismo
*técnico* — lente, grão, luz motivada. Ela não diz nada sobre **imperfeição humana**, e o modelo,
deixado sozinho, entrega pele perfeita, simetria perfeita, rosto de catálogo. Tecnicamente
realista e humanamente falso.

**Isto é a terceira fonte a dizer a mesma coisa**, e as três se reforçam:
- 🎓 O motor anti-retoque da skill `character-sheet` do fabricante (`model-sheet-storyboard.md`).
- 🎥 `do not beautify` na passagem da folha de personagem.
- 🎥 Esta tese, explicando **por quê**.

Exemplo do que ele considera acerto, verbatim: *"all of the imperfections on this guy's face. It's
not fully sharp. (…) He has bags under his eyes. He has wrinkles. He doesn't have the best
hairline (…) **but that is what makes us human.**"*

> **Regra:** todo personagem humano do canal recebe **imperfeições nomeadas** na folha — olheira,
> ruga, assimetria, entrada de cabelo, cicatriz, dente torto, pele não uniforme. Não como defeito
> tolerado: **como especificação.**

---

## 1b. ⚫ NARRAÇÃO E DIÁLOGO NÃO SE SOBREPÕEM — decisão do Samuel, 2026-09-02

> **O canal passa a ter diálogo em algumas cenas. Quando há diálogo, a narração PARA — e volta
> depois.** Nunca as duas vozes ao mesmo tempo.

**Por quê, nas palavras dele:** *"para mais estanqueidade"*. Narração e diálogo disputam a mesma
faixa de atenção; sobrepor as duas é o que faz vídeo de IA soar como podcast com imagem.

**Como isso muda cada etapa:**

| Etapa | O que muda |
|---|---|
| **Roteiro** | O bloco declara o **regime de voz**: `VOZ: narração` ou `VOZ: diálogo`. Não existe bloco misto. |
| **Narração (ElevenLabs)** | O texto da narração **termina antes** do bloco de diálogo e **recomeça depois**. Não escrever narração que atravessa a cena dialogada. |
| **Prompt de vídeo** | Bloco de diálogo é o único que precisa de fala escrita, sotaque, e da estrutura em três tempos (§2 e §3). Bloco de narração não leva fala nenhuma. |
| **Áudio nativo** | Bloco de diálogo pode precisar de `generate_audio: true` para a fala sair na boca certa — **e isso muda o custo**. Bloco de narração continua com áudio desligado. |
| **Montagem** | A emenda narração → diálogo → narração é ponto de corte natural. Usar. |

> ⚠️ **A conferir antes do primeiro bloco dialogado:** quanto o `generate_audio: true` encarece o
> Seedance 2.5 a 480p. Está fora da conta de 75 cr/bloco, que foi medida com áudio desligado.
> **Medir com `get_cost` antes de orçar um vídeo com diálogo.**

**Fronteira com a narração de canal:** a voz de narração continua sendo ElevenLabs v3
(`narracao-elevenlabs-v3.md`), gerada fora. A fala **dentro da cena** é do modelo de vídeo. São
duas coisas diferentes e não se misturam no mesmo bloco.

---

## 2. DIÁLOGO — a estrutura em três tempos

🎥 O modelo não recebe "eles discutem". Recebe **três blocos por segmento**:

| Bloco | O que escrever |
|---|---|
| **Stage** | onde a cena se passa e quem está lá — *"walking out of a dim bedroom into the open living room lit by a single warm lamp. **They're alone in the house, no one else is present**"* |
| **Primary event** | o que acontece, com a atuação dentro: *"the man speaks first, **quiet and broken, eyes wet, struggling to get the words out**. An apology with no real explanation behind it. **Before he can finish**, the woman cuts him off sharply, telling him to stop talking, **her face already tight with anger**"* |
| **End state** | onde tudo termina: *"the two are close together, **him mid-sentence and glassy-eyed, her jaw clenched**, having just cut him off"* |

🎥 *"That is explaining to **the actor** what you want to see on the screen. That includes the
action, the words they need to say, **the shift in the tone**, but also **the pauses**, and lastly
**the emotion** at these moments."*

**Quatro coisas por fala, então:** ação · palavras exatas · mudança de tom · pausas · emoção.
E o **end state** é o que faltava por inteiro no nosso STAGES — declaramos o que acontece, nunca
onde o segmento **termina**. É ele que amarra o corte seguinte (ver a trava de pose,
`REGRAS-PRODUCAO-VIDEO.md` §4).

---

## 3. SOTAQUE E VOZ — a receita em cinco campos

🎥 Não funciona escrever *"add an Irish accent"*. A ordem que funciona:

**nomear o falante → região de origem → ritmo → energia → estado emocional → a fala exata**

Exemplo verbatim: *"I named him Clement. **He speaks English with an unhurried Kingston accent,
natural, not exaggerated, not a comedy voice.** When the shock hits, the voice jumps and the words
get short."*

> Reparar em duas coisas: **"not a comedy voice"** é negativa **acompanhada** (vem depois de
> *"natural"*) — segue a regra da §7.4b do REGRAS. E **o sotaque tem gatilho**: *"when the shock
> hits, the voice jumps"* — a voz muda por evento, não é um preset constante.

---

## 4. PALAVRAS DE ATUAÇÃO — o corpo, batida a batida

🎥 Em vez de "ele foge com medo", uma cadeia de estados corporais, cada um com verbo concreto:

> *"riding happily with **loose shoulders** and a broad smile → [footstep] → he **loses the smile**
> and **tightens the fingers** → looks behind **slowly and reluctantly** → **freezes** and screams
> **involuntarily** → pedaling with **frantic uneven force** → leaves the bicycle and hides →
> **covering his mouth**, **remaining rigidly still**, waiting for the footsteps to recede → then
> **releases one shaky breath**"*

**Isto é a nossa antecipação → ação → consequência**, mas escrita **no corpo** em vez de na câmera.
E casa com a regra dos números (`direcao-cinematografica.md`): cada estado é observável, nenhum é
adjetivo de grau.

🎥 **E ele declara o tamanho:** *"I do want to note that **this is a four-page prompt**."* — mais
uma confirmação de que não há teto de caracteres, e de que prompt longo **denso** é o padrão de
quem acerta.

**Emoção com gatilho:** descrever *o que causa* a emoção (um som, um objeto, uma revelação), não
só a emoção. Emoção sem causa no quadro é adjetivo.

---

## 5. CÂMERA — foco e ângulo como decisão, não como enfeite

**Foco com gatilho.** 🎥 Declarar **em que** a câmera foca, e **quando muda**: *"a deliberate rack
focus (…) **after he crawls, then we see the focus change**"*. Foco é evento, com disparo nomeado.

**A sequência de ângulos de uma cena de ação** — ordem que ele demonstra, e ela é reaproveitável:

1. **Establishing** — estabelece a geografia (*"the three-lane layout"*). Casa com o plano aberto
   que trava a marcação (`REGRAS` §4).
2. **Enquadramento fechado / insert** — o detalhe que carrega o esforço (*"the shoe insert"*).
3. **Alternar sujeito ↔ ameaça** — *"alternating between myself and the truck, **which reinforces
   the widening gap**"*. A alternância é o que constrói a distância, não a descrição dela.
4. **Wide estático e ininterrupto** para a ação que precisa ser legível — *"we're **not introducing
   distracting cuts** there"*.
5. **Escalada final** com câmera baixa montada.

> ⚠️ O ponto 4 conversa direto com a rubrica: **corte rápido é esconderijo**
> (`rubrica-aceitacao-take.md` §2). Ação legível pede plano **sustentado**, não picotado.

🎥 *"Camera movement isn't style. **It's emotion.**"* — é a nossa justificativa dramática
obrigatória por shot, dita por outra fonte.

---

## 6. SOM — diegético × não-diegético, e a notação

🎥 **Confirma a notação de símbolos** que estava na fila (agora com segunda fonte):

| Símbolo | Para |
|---|---|
| `( )` | música |
| `< >` | efeito sonoro |
| `{ }` | diálogo |
| `【 】` | legenda |

**Diegético** = o que os personagens ouvem. **Não-diegético** = música, sub-bass, efeitos que só o
público ouve.

**O nível de detalhe que ele usa é muito acima do nosso** — verbatim:
> *"a soft hydraulic door closing with a hiss, with a heavy steel door slam. **Each step produces
> one closed rubber sole squeak followed immediately by one small wet splash beneath the
> corresponding foot.**"*

E o não-diegético **ancorado no frame**: *"a hard non-diegetic sub-bass hit that lands on **the
exact frame** the light goes dark."*

⚠️ **Cuidado com o nosso caso:** o canal usa `generate_audio: false` / `sound: off` por decisão de
custo e porque a narração é ElevenLabs. Esta seção vale para **quando** o áudio nativo for usado —
e a marcação de diálogo `{ }` continua útil para o modelo entender **que aquilo é fala**, mesmo
com o áudio desligado.

---

## 7. PÓS-PRODUÇÃO — quatro ajustes baratos, e um deles é o que mais entrega

🎥 Todos rodam no editor, custam **zero crédito**, e ele os apresenta como o que separa "quase" de
"crível":

1. **Cortar o slow-motion.** *"That makes it unbelievable to me."* Ele corta fora o trecho lento
   e o resultado fica mais rápido e mais real. **O slow-motion que o modelo entrega sozinho é
   sintoma, não estilo** — bate com a §2 da rubrica.
2. **Zoom in/out no editor**, 100% → 120% lento, para dirigir a atenção sem gastar geração.
3. **RUÍDO — e este é o que mais entrega.** *"Especially the **noise** plays a huge part in making
   it look more believable."* Uma pitada, não muito. É o antídoto direto do "plástico demais".
4. **Blur nas bordas** — faz parecer captado por câmera. ⚫ Conversa com a sua decisão de usar
   desfoque para mascarar fundo (`rubrica-aceitacao-take.md` §5.1).
5. **Barras de cinema**, 10–15% em cima e embaixo.

> **Os quatro somados são a versão barata do que a Academy chama de regra de acúmulo** — cada um é
> pequeno, juntos mudam a leitura do vídeo. E nenhum custa crédito.

---

## 8. MODELOS QUE ELE RECOMENDA — ⚠️ colocação paga, ler com desconto

O vídeo é **patrocinado pelo Higgsfield**. Registrar o que ele diz, marcado:

- ⚫ **ADOTADO (decisão do Samuel, 2026-09-02): Soul passa a ser o modelo de imagem de personagem.**
  🎥 *"this model really focuses on creating cinematic type images of people (…) with all of the
  imperfections."* 🟢 Confirmado no catálogo: `soul_2` / `soul_v2` (Soul 2.0, **aceita `unlim` do
  trial**), `soul_cinematic` (Soul Cinema) e **`soul_cast` — "consistent cinematic character
  identity"**, que merece investigação própria como alternativa à folha.

  > **Consequência de orçamento — e ela é pequena.** Isto devolve imagem para a conta de créditos
  > (o Samuel gerava fora, no GPT Plus / Nano Banana). Mas 🎓 Soul é barato ao ponto de ser ruído:
  > *"Four generations cost only half a credit"* · *"eight batches just for one credit"*. Contra
  > ~2.200 créditos de vídeo por vídeo, a imagem continua sem pesar. **E o Soul 2.0 aceita geração
  > ilimitada do trial**, então durante o trial custa zero.
  >
  > **O que NÃO muda:** iterar folha continua barato o bastante para não aceitar folha mediana.
- 🎥 **Contra GPT Image 2 para folha de personagem** — *"way too noisy (…) each time the image
  gets slightly worse."* ⚠️ Isto é opinião dele, num vídeo pago pelo concorrente do GPT Image 2.
  **Não adotar como regra** — mas vale como hipótese a observar, porque o Samuel gera no GPT Plus.
- 🎥 Ele passou a usar **"Seedream 5.0 Pro"** (a transcrição diz "SeaArt", provável erro de
  legenda) a 2K, 16:9. **Não localizado no catálogo do Higgsfield** na varredura de 02/09 —
  confirmar antes de citar.

---

## 9. DETALHE PEQUENO NA FOLHA = PROBLEMA GRANDE NO VÍDEO

🎥 Ele **remove o chapéu** do personagem antes de gerar a folha: *"this is a small hat and you
don't want the AI to use such small details when it makes videos, because (…) it's not going to
look sharp, it's not going to look real. **It might even change the characteristics of your
character.**"*

> **Regra:** adorno pequeno e destacado (chapéu miúdo, brinco, anel, fivela) na folha vira ruído no
> vídeo — e pode arrastar a identidade junto. **Ou o detalhe é grande e definidor** (as garras de
> bronze, a textura de serpente), **ou sai da folha.** Se for narrativamente necessário, entra como
> prop declarado no bloco, não como microdetalhe da folha.
