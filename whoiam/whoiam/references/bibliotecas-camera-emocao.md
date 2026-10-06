# Bibliotecas de câmera e emoção — vocabulário pronto, com estrutura

> Levantado em **2026-09-02** dos três sites citados no vídeo 🎥 *"master AI realism"*.
> Marcadores: 🎥 do autor do vídeo · 🟢 extraído do código-fonte do próprio site.
>
> | Site | O que é | Publicado |
> |---|---|---|
> | `aicameramovements.com` | 45 movimentos de câmera, texto pronto | 2026-07-14 |
> | `seedance-emotion-direction.vercel.app` | 25 emoções como descrição anatômica | — |
> | `aicameracontrol.com` | marcação 3D → prompt escrito automaticamente | — |
>
> ⚠️ **Proveniência:** os três são do autor do vídeo patrocinado pelo Higgsfield. São material de
> terceiro competente, **não** documentação do fabricante. Valem como vocabulário e como estrutura;
> não valem como prova de comportamento do modelo.

---

## 0. ⚠️ O ACHADO QUE ATRAVESSA OS TRÊS — e ele mexe no teste da negativa

**Nenhuma das três bibliotecas usa negação. Nenhuma.** 45 movimentos de câmera, 25 emoções e um
gerador de prompt inteiro, **escritos 100% no positivo.** Zero *"no dolly"*, zero *"not angry"*.

Isso **não** contradiz a §7.4b do `REGRAS-PRODUCAO-VIDEO.md` — reforça a leitura dela por outro
lado. A negativa exaustiva do prompt bank do Higgsfield **não é obrigatória**: dá para especificar
movimento de câmera com precisão total sem negar nada, desde que se declare os quatro campos da §1.

> **Consequência para o teste da §7.4c:** o braço "positivo" ganhou uma forma canônica para ser
> testado — os quatro campos abaixo — em vez de ser só "o prompt sem as negativas".

---

## 1. MOVIMENTO DE CÂMERA — a estrutura em quatro campos

🟢 Todos os 45 verbetes seguem exatamente a mesma forma, e é ela que importa mais que a lista:

```
[NOME DO MOVIMENTO].
Movement: [o que a câmera faz fisicamente]
Speed:    [o ritmo, descrito — não adjetivado]
Framing:  [o que precisa CONTINUAR LEGÍVEL durante o movimento]
End:      [onde o movimento termina e assenta]
```

**Os dois campos que nós não tínhamos:**

- **`Framing`** — não é o enquadramento inicial, é **o que não pode se perder enquanto a câmera se
  move**. *"keep the horizon level"*, *"keep foreground, subject and background layers readable as
  parallax shifts"*, *"keep the subject centered while the background rotates around them"*.
  É a trava de legibilidade do movimento.
- **`End`** — **onde o movimento assenta.** *"settle on a clear final composition"*, *"land on the
  upper target"*. Mesmo princípio do **end state** do diálogo (`atuacao-dialogo-som.md` §2) e da
  trava de pose no corte (`REGRAS` §4). **Declarar o fim é um padrão do sistema inteiro, não um
  detalhe de câmera.**

**Exemplos verbatim, para copiar a forma:**

> **pan right.** Movement: rotate the camera horizontally from left to right from one fixed point.
> Speed: smooth constant rotation. Framing: keep the horizon level while new space enters from the
> right side of the frame. End: settle on a clear final composition.

> **locked-off static shot.** Movement: hold one fixed camera position for the full clip.
> Speed: still and steady. Framing: keep the same angle, height, lens distance and composition.
> End: finish with the same framing and camera position.

> **orbit (clockwise).** Movement: circle clockwise around the main subject at a consistent radius.
> Speed: smooth controlled orbit. Framing: keep the subject centered while the background rotates
> around them. End: complete the intended arc or full circle with stable framing.

### 1.1. Os 45 movimentos, por categoria

**Estático** — locked-off static shot · locked-camera time-lapse
**Pan e tilt** — pan right/left · whip pan right/left · tilt up/down
**Zoom e foco** — slow zoom in/out · fast zoom in/out · crash zoom in/out · infinite zoom ·
earth zoom out · tilt-shift miniature view
**Dolly e translação** — dolly in/out · truck right/left · pedestal up/down · slider right/left ·
push past · pass-through movement
**Arco e órbita** — arc right/left · clockwise orbit · counterclockwise orbit
**Acompanhamento** — tracking shot · follow shot from behind · reverse tracking shot ·
side tracking shot · low tracking shot · vehicle tracking shot · chase shot
**Corpo** — handheld shot · body-mounted Snorricam · first-person view
**Aéreo** — crane up/down · drone push in · drone pull back · helicopter-style aerial shot

> **Os que servem ao canal e não estavam no nosso vocabulário:** `push past` (passar por um objeto
> de primeiro plano — resolve os três planos de profundidade em movimento), `pass-through movement`
> (atravessar uma superfície para o espaço além — transição sem corte), `body-mounted Snorricam`
> (câmera presa ao corpo, fundo girando — desorientação de maldição), `low tracking shot` (altura
> do chão, para criatura pesada), `reverse tracking shot` (andando de costas à frente do sujeito).

---

## 2. EMOÇÃO — 25 verbetes, e o método é o que vale

🟢 Estrutura de cada verbete: `nome · família · intensidade · gatilho · prompt`.

> ### O método: **a emoção nunca é nomeada no prompt. Só o corpo é descrito.**
>
> O verbete "Rage" **não contém a palavra "raiva"**. Contém: *"The eyebrows slam down and inward,
> the upper lip peels back from the teeth, the nostrils flare, the neck tendons tighten, and the
> head pushes forward."*

Isto é a regra dos números (`direcao-cinematografica.md`) aplicada ao rosto: **descrever o
observável, nunca o rótulo.** "Ele está com raiva" é adjetivo; a sequência acima é direção.

E repare no padrão de cada verbete: **uma cadeia de micro-ações ordenadas, terminando num estado
que se sustenta** (*"The snarl holds as hard breaths move through the nose"*). De novo o **end
state**.

**Famílias:** Joy · Surprise · Fear · Anger · Disgust · Sadness · Physical · Social · Drive
**Intensidades:** Subtle · Medium · Explosive

### 2.1. Os 25 verbetes (prompt verbatim — é para colar)

| Emoção | Int. | Gatilho | Prompt |
|---|---|---|---|
| **Joy / Laughter** | Expl. | Laughter breaks loose | The eyes squeeze into crinkled slits, the mouth opens wide showing teeth, the head drops forward and tips back, and the shoulders bounce with each breath. The laugh settles into a wide lingering grin. |
| **Shock** | Expl. | Sudden disbelief | The eyes snap wide with white visible above the iris, the eyebrows shoot up, the jaw drops fully open, and the head jerks back. The face freezes in that expression before a single blink. |
| **Terror** | Expl. | Fear refuses to release | The eyebrows pull up and together, the eyes lock wide open without blinking, the mouth stretches open, the chin tucks back, and the chest rises and falls with fast, shallow breaths. |
| **Rage** | Expl. | Control breaks open | The eyebrows slam down and inward, the upper lip peels back from the teeth, the nostrils flare, the neck tendons tighten, and the head pushes forward. The snarl holds as hard breaths move through the nose. |
| **Disgust** | Méd. | Full recoil | The nose wrinkles hard and pulls the upper lip upward, the eyes squint nearly shut, the chin draws in, and the head recoils and turns away. The revolted expression holds. |
| **Crying** | Expl. | Composure collapses | The eyes and nose flush red, tears spill over the lower lid, the breath catches in visible stutters, the mouth pulls into a square shape, and the chin crumples and trembles. The shoulders begin to shake. |
| **Pain / Wince** | Expl. | Sharp jolt | The eyes clamp shut, the teeth bare in a hard grimace, the head snaps to one side, and one shoulder rises toward the ear. The face stays contracted before easing only slightly. |
| **Eye Roll** | Méd. | Patience is gone | The eyes roll in a full, slow arc while the head tilts with the movement. Air pushes out through the nose, the eyes return with lowered lids, and a flat stare holds before the gaze turns away. |
| **Suspicion** | Sutil | Something does not add up | The chin drops while the eyes stay lifted. One eyebrow rises higher, the head turns slightly so the gaze lands sideways, and the mouth tightens at one corner. The stare holds without blinking. |
| **Flirtation** | Sutil | Playful restraint | The chin lowers, the gaze returns with a slow, deliberate blink, and a warm, playful half-smile grows at one corner of the mouth. The expression holds without rushing or breaking eye contact. |
| **Smug / Gloating** | Méd. | Quiet superiority | The eyelids lower, one corner of the mouth pulls into a slow smirk, the eyebrows rise once and settle, and the chin lifts slightly. The smirk holds through unbroken eye contact. |
| **Boredom** | Sutil | Attention drains away | The eyelids grow heavy, the gaze drifts and loses focus, a slow blink lasts too long, the jaw slackens, and a long sigh lowers the chest. The head sinks and the body settles into stillness. |
| **Confusion** | Méd. | Meaning will not settle | The eyebrows become asymmetric, one raised and one lowered. The eyes search rapidly, the head tilts sharply, and the mouth hangs slightly open. The puzzled expression deepens instead of resolving. |
| **Realization** | Méd. | The answer lands | A blank thinking expression breaks as the eyes widen, the eyebrows jump, the lips part on a silent breath, and focus snaps back. A slow nod follows while the knowing, slightly stunned look holds. |
| **Awe / Wonder** | Méd. | Drawn toward wonder | The eyes widen gradually without tension in the brow, the mouth opens little by little, the head tilts upward, and the body leans forward. The open, reverent expression never drops. |
| **Determination** | Méd. | Resolve locks in | The eyes lift and lock forward, a deep breath expands the chest, the jaw sets visibly at the hinge, the eyes narrow, and the shoulders roll back. One sharp nod completes the change. |
| **Frustration** | Méd. | Effort turns to defeat | The eyes clamp shut, the jaw slides from side to side, a sharp breath pushes through the nose, and the head shakes once. The head tips back as one long defeated breath leaves the tension in the face. |
| **Anxiety** | Méd. | Restlessness will not stop | The eyebrows stay knitted, the eyes flick rapidly from side to side, the lower lip pulls between the teeth, and breathing remains shallow and quick. The hands grip together as the weight keeps shifting. |
| **Sadness** | Sutil | Quiet hurt | The inner corners of the eyebrows pull up and together, the mouth corners drag down, the chin trembles once, and the gaze sinks as the head lowers. A slow blink and hard swallow fail to change the expression. |
| **Guilt** | Sutil | The truth weighs down | The mouth opens but no words come. The eyes slide down and away, the head lowers, a hard swallow moves through the throat, and one hand reaches to the back of the neck. The gaze stays on the floor. |
| **Embarrassment** | Méd. | Confidence folds inward | Color rises in the cheeks, the eyes dart down and to the side, and an awkward pressed-lip half-smile appears. The head ducks and turns away while one hand rises near the mouth. The eyes stay lowered. |
| **Exhaustion** | Sutil | Nothing left to give | The eyelids drag downward, a long blink stays closed too long, the head drifts down and lifts again slowly, the jaw hangs slack, and one long breath empties out. The eyes reopen only halfway. |
| **Relief** | Méd. | Pressure finally releases | A large visible exhale empties the chest, the eyes close, the raised eyebrows drop to neutral, and the shoulders collapse downward. One hand rises to the forehead. A small, shaky smile appears only after the breath finishes. |
| **Pride** | Sutil | Satisfaction held quietly | The chin lifts, the chest expands, and a closed-lip smile spreads slowly and evenly. The shoulders roll back, followed by one slow, satisfied blink. The smile remains as the arms fold. |
| **Nervous Fake Smile** | Sutil | Smile without warmth | The mouth stretches into a smile while the eyes stay flat, with no crinkling at the corners. Blinking speeds up, the throat makes a hard swallow, and the gaze drops before the strained smile snaps back into place. |

> **Para o canal:** Terror, Shock, Awe/Wonder, Dread (usar Terror em intensidade menor),
> Determination e Realization são os que mais aparecem em mitologia. **Awe/Wonder é o verbete da
> revelação da criatura** — e repare que ele é explicitamente *sem tensão na testa*, o que separa
> maravilhamento de medo.

---

## 3. MARCAÇÃO 3D → PROMPT — as duas tabelas de conversão

O terceiro site é uma ferramenta: bloqueia-se o plano em 3D, exporta-se o quadro de referência e
ele escreve o prompt. 🟢 As duas tabelas de conversão que ele usa internamente valem sozinhas.

### 3.1. Altura da câmera em METROS → ângulo nomeado

| Altura | Rótulo | Frase que ele escreve |
|---|---|---|
| até ~0,95 m | knee level | *a low knee-level angle looking up at the subject* |
| 0,95–1,25 m | hip level | *a low hip-level angle* |
| 1,25–1,50 m | chest level | *chest level* |
| 1,50–1,80 m | eye level | *eye level* |
| 1,80–2,50 m | high angle | *a high angle looking down at the subject* |
| acima de 2,50 m | overhead | *a directly overhead bird's-eye view looking down at the subject* |

**Isto fecha a regra dos números para altura de câmera.** Em vez de "contra-plongée", pensar em
metros e converter. E dá a régua para as medidas do blueprint de ação
(`direcao-bloco-acao.md` §2.2), que pede altura em metros e não dizia como traduzir.

### 3.2. Tamanho de plano → ORÇAMENTO DE DETALHE

🟢 Cada tamanho carrega uma cláusula de contexto — **e ela diz ao modelo quanto detalhe gastar**:

| Tamanho | Cláusula |
|---|---|
| extreme close-up | *ultra-realistic skin texture with visible pores and micro-detail, tack-sharp eyes, shallow depth of field* |
| close-up | *ultra-realistic skin texture and fine facial detail, soft background blur, shallow depth of field* |
| medium shot | *balanced detail on the subject and the surrounding space, moderate depth of field* |
| wide shot | *full body in a richly detailed environment, deep focus* |
| extreme wide shot | *a small figure within a vast, highly detailed environment, epic sense of scale, deep focus* |

> **É a peça que faltava para o nosso problema de painel pequeno.** O tamanho do plano não é só
> enquadramento — é **onde o modelo deve gastar resolução**. Close pede poro e olho nítido; wide
> pede foco profundo e ambiente. Escrever o tamanho sem a cláusula deixa essa decisão para o
> gerador, e ele erra para o lado do rosto de catálogo.

### 3.3. Vista (continua abaixo — a ponte para o canal está na §4)

Frase por vista, no mesmo padrão: *"seen from the front, the face toward the camera"* ·
*"seen from directly behind, the back of the head toward the camera"*. Casa com a orientação
motivada do corpo (`model-sheet-storyboard.md`).

---

## 4. ⚫ A PONTE — do NOSSO tipo de cena para o movimento certo

> **Decisão do Samuel, 2026-09-02:** *"o repertório e essa base que ele nos proporciona é válida,
> nós só precisamos ter uma base para o TIPO DE CENA que nós precisamos."*
>
> As §1–§3 são repertório genérico. **Esta seção é o canal.** É a tabela de consulta única:
> achou o tipo de cena, tem o movimento, a altura, o tamanho e a emoção.

**Como usar:** o algoritmo do `direcao-cinematografica.md` continua mandando — intenção dramática
primeiro, dono do olhar depois, e **justificativa dramática obrigatória por shot**. Esta tabela é o
**ponto de partida** de cada linha, não o substituto do algoritmo. Sair dela é permitido e às vezes
certo; sair dela **sem porquê escrito** é o default de sempre com roupa nova.

### 4.1. Tabela mestra

| Tipo de cena | Intenção | Movimento (§1) | Altura (§3.1) | Tamanho (§3.2) | Emoção (§2) |
|---|---|---|---|---|---|
| **Abertura / estabelecimento** | lore fria | `helicopter-style aerial` ou `crane down` · `locked-off static` | overhead → eye level | extreme wide | — |
| **Ameaça latente** (está ali, não se vê) | ameaça latente | `locked-off static` com primeiro plano oclusivo · `slider` lento | eye level | wide | — |
| **Presságio / objeto** | presságio | `slow zoom in` · `locked-off static` | chest/eye level | extreme close-up | *Suspicion* |
| **Aproximação do inevitável** | pavor crescente | `dolly in` lento · `push past` (por galho/batente) | eye level | medium → close-up | *Anxiety* |
| **Revelação PARCIAL** (garra, contorno, olho) | pavor crescente | `slider` · `arc` lento · `tilt up` parcial | knee/hip level | extreme close-up | *Terror* (subtil) |
| **Revelação TOTAL / escala** | assombro | `tilt up` · `drone pull back` · `crane up` | knee level → overhead | wide → extreme wide | *Awe / Wonder* |
| **Reação da vítima** | pavor / assombro | `locked-off static` · `slow zoom in` | eye level | close-up | *Shock* · *Terror* |
| **Fuga** | pânico | `chase shot` · `follow shot from behind` · `handheld` | hip/chest level | medium | *Terror* |
| **Perseguição** | pânico | `low tracking shot` · `reverse tracking shot` · `side tracking` | knee/hip level | medium → wide | *Terror* |
| **Confronto / luta** | ameaça | `arc` · `orbit` · `low tracking` · `crash zoom in` no impacto | knee level (baixo domina) | medium | *Rage* · *Determination* |
| **Maldição / sanidade ruindo** | tragédia | `body-mounted Snorricam` · `arc` acelerando | eye level | close-up | *Confusion* → *Terror* |
| **Consequência / morte** | tragédia | `pedestal down` · `locked-off static` sustentado | high angle | wide | *Crying* · *Guilt* |
| **Luto / encerramento** | luto | `slow zoom out` · `drone pull back` · `locked-camera time-lapse` | eye → high angle | wide → extreme wide | *Exhaustion* · *Relief* |

### 4.2. As três regras que a tabela NÃO dispensa

**1. Criatura em contra-plongée, e a altura é o instrumento.** A tabela põe `knee level` nas linhas
de criatura de propósito — 🟢 a conversão da §3.1 diz que abaixo de 0,95 m a frase é *"a low
knee-level angle **looking up at the subject**"*. É a nossa regra "low angle = poder, ameaça,
divindade" com número em vez de adjetivo.

**2. Revelação é POR PARTES antes de ser total.** As duas linhas de revelação estão separadas de
propósito e nessa ordem. Fazer a revelação total sem a parcial antes queima o único momento caro
do vídeo. E o `extreme close-up` da parcial já vem com o orçamento de detalhe certo (poro, olho
nítido) — ver §3.2.

**3. Assombro ≠ medo, e o verbete prova.** *Awe / Wonder* é explicitamente **sem tensão na testa**
(*"the eyes widen gradually **without tension in the brow**"*), ao contrário de *Terror* (*"the
eyebrows pull up and together"*). **É a diferença entre a criatura ser sublime e ser só assustadora
— e o canal vive dessa diferença.** Errar isso transforma mitologia em filme de susto.

### 4.3. Onde a gente vai ALÉM do repertório dele

⚫ *"nosso foco é fazer ainda melhor."* O que temos e a biblioteca dele não tem:

- **Justificativa dramática obrigatória por shot** — ele entrega movimento; nós exigimos o porquê.
- **Três planos de profundidade declarados** (primeiro plano / sujeito / fundo) em cada shot. A
  biblioteca dele fala de `Framing` durante o movimento, nunca de profundidade. **O primeiro plano
  oclusivo — galho, ombro, batente, névoa — é a nossa ferramenta principal de ameaça latente**, e
  não existe na lista dele.
- **Luz motivada** — fonte existente no mundo da cena. A biblioteca dele é muda sobre luz.
- **Anatomia do movimento em três tempos** (antecipação → ação → consequência) e a reação do
  ambiente, que é o que vende peso.
- **Velocidade inversamente proporcional à massa** — criatura colossal move-se devagar.
- **A régua de aceitação** (`rubrica-aceitacao-take.md`) — ele mostra o acerto, não o critério.

> **Resumo honesto:** a biblioteca dele é **vocabulário**, e é bom. A nossa direção é **gramática**.
> Vocabulário sem gramática dá frase bonita e cena genérica — que é exatamente o que o resultado
> dele mostra quando se olha duas vezes.
