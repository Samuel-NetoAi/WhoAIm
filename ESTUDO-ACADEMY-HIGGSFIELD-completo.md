# Estudo completo — Higgsfield Academy, seção Movie making

> **75 aulas, 7 cursos, transcritas integralmente em 2026-09-02.**
> Transcrição bruta com carimbo de tempo em
> `D:\Agentes\SALOMAO\estudos\academy-higgsfield\` (um `.md` por curso).
> O guia oficial de prompt do Seedance 2.5 está no mesmo diretório como
> `_guia-oficial-prompt-seedance-2-5.md`.
>
> Marcador de proveniência: 🎓 = Academy oficial. Onde a citação é literal, ela
> vem entre aspas com curso e aula. Onde é leitura minha, está dito.

---

## 0. Como isto foi obtido, e o que isso custou de aprendizado

Os vídeos das aulas são **MP4 abertos no CloudFront**, sem DRM e sem login, e o
HTML de **uma** aula lista os MP4 de **todas** as aulas do curso. Nenhum
navegador foi necessário. 75 de 75 transcritas, zero falhas, com
`whisper large-v3-turbo` em CPU (~1,5× o tempo real).

Três defeitos nossos precisaram ser consertados antes:

| Defeito | Efeito | Onde |
|---|---|---|
| `mcp_server.py` escrevia JSON-RPC em cp1252 | uma seta `→` derrubava a resposta **depois** do trabalho todo feito; o sintoma era sempre "a ferramenta falhou" | corrigido |
| `video.py` chamava `processo.rodar` sem importar `processo` | baixar mídia fora do YouTube **nunca funcionou** | corrigido |
| o fallback CPU do Whisper envolvia só a construção do modelo | o erro de cuBLAS só estoura na inferência e passava reto | corrigido |

> **Consequência para o registro:** o estudo antigo do Seedance 2.5 (🎥) saiu de
> **legenda do YouTube**, não de transcrição. O Whisper local nunca havia rodado
> nesta máquina. A GPU segue sem carregar a cuBLAS; roda em CPU.

⚠️ **Calibragem que atravessa o documento inteiro.** A Academy demonstra em
**Seedance 2.0 / 4K**; nós rodamos **Seedance 2.5 a 480p + upscale local**.
**Método atravessa. Número não atravessa.** Nada aqui toca a §1 do
`REGRAS-PRODUCAO-VIDEO.md`.

Também há **datas diferentes dentro da própria Academy**: o curso *"How to
evaluate AI filmmaking demos"* é anterior e afirma que *"everything you just
watched from 2.5 was 720p"* enquanto *"2.0 renders in 4K"*. Isso é foto de um
momento, não spec atual — e é a origem provável da frase 🎥 *"you can only do
720p for now"* que já está tratada na §1 do REGRAS.

---

## 1. O PIPELINE — três estágios, e o mesmo em todos os cursos

Todos os sete cursos rodam a mesma espinha:

```
ROTEIRO  →  ASSETS  →  GERAÇÃO CENA A CENA  →  MONTAGEM
```

### 1.1. Roteiro — nunca "escreva um roteiro"

🎓 *Blockbuster, aula 2:* **"And no, I didn't just say 'write me a script'. That
always turns out terrible. I asked it to expand my idea instead. And it starts
asking me questions. What's the runtime? Which settings do you want? Want me to
suggest a couple of plot twists? (...) So we built it step by step. Nothing good
comes out of one lazy request."**

🎓 *Santiago, aula 3 — a estrutura:* **setup → rising action → climax →
resolution.** Ele chama de "director's tip number one" e usa a estrutura como
pedido explícito ao Claude.

🎓 *Santiago, aula 3 — e este é o detalhe operacional que mais importa:*
**"ask for a two-minute script with every shot, 15 seconds max. That's one
Seedance generation per shot."**

> **O roteiro é escrito na unidade de geração.** Cada plano do roteiro é uma
> chamada ao modelo. Isso não é formatação — é o que faz o orçamento ser
> previsível antes de gerar qualquer coisa.

### 1.2. Assets antes de qualquer vídeo

🎓 *Blockbuster, aula 3:* pasta por cena, subpasta por asset.
**"Trust me, two weeks and 400 generations later, you'll be glad you did this."**

---

## 2. ASSETS — as regras, uma a uma

### 2.1. Folha de personagem

🎓 **Três painéis: frente, costas e um close-up de rosto separado.**
*Santiago, aula 4:* **"Keep it on a gray background with three angles. Front,
back, and a separate close-up headshot."**
*Blockbuster, aula 3:* **"The close-up gives the model the exact face to lock
onto, and the full body gives it his height."**

🎓 **Fundo cinza, e o motivo é medido:** *Blockbuster, aula 3:* **"ask for a gray
background. We found that the win rate is much higher. There's zero background
clutter, which means more usable generations."**

🎓 **UM rosto por folha — e este é o erro que mata a continuidade.**
*Blockbuster, aula 3:* **"Our character sheet has multiple faces in one image.
It looks fine, but when we animate later, Seedance doesn't understand which face
to grab. So it drifts, a little in every scene. And by scene 5, our hero is a
stranger."** A correção deles: **apagar o rosto do painel de corpo inteiro**,
deixando só o close-up com rosto.

> Isto é diferente do que a nossa `model-sheet-storyboard.md` prescreve hoje
> (turnaround com cinco vistas de corpo inteiro). **Não estou dizendo que o
> nosso está errado** — estou dizendo que existe um modo de falhar nomeado pelo
> fabricante e que a nossa folha se expõe a ele.

🎓 **Critério de aceitação da folha** — *Santiago, aula 4:* **"it's really
important that the light is soft with no harsh shadows on the face and no glare
in the hair. (...) the main secret of cinematic AI videos is that you'll need a
high-quality image of your character."** Ele rejeita opções por lado do rosto
escuro e por brilho no cabelo.

🎓 **A folha de personagem também trava a VOZ.** *Santiago, aula 6:*
**"When you create the character sheet for each person, Seedance automatically
generates a unique voice for them, and it matches the tone right to how they
look. So, by locking in the visuals, you also lock in the voice."**

### 2.2. Locação

🎓 **Sempre pedir ângulo de 3/4 — e é de LOCAÇÃO, nunca de pessoa.**
*Santiago, aula 5:* **"Whenever you generate a location, write three quarters
angle right in the prompt. It adds volume and depth, and the model gets a much
better sense of the distance between objects and where everything is."**
*Blockbuster, aula 3:* **"It adds depth, which gives the camera way more to hold
on to when it moves. You'll get a much higher win rate than you would with a flat
head-on shot."**

🎓 **A locação carrega o filme.** *Blockbuster, aula 3:* **"Locations carry the
whole film. If the setting looks cheap, every shot inside it does too, and no
amount of prompting fixes that later."**

🎓 **Duas fontes de luz fizeram a locação vencedora** (lanterna + raios de luz
pelas frestas). *Blockbuster, aula 3:* **"Small details like the light rays are
what make a generation feel real."**

🎓 **Sub-locação que a cena precisa e a locação não tem vira ASSET PRÓPRIO.**
*Blockbuster, aula 7 — o oásis:* **"we treated the oasis as its own separate
location asset. Now the model knows the spot and the landscape around it. So the
oasis looks the same in every generation."**

🎓 **Paleta declarada a cada troca de locação ou flashback.** *Santiago, aula 9:*
**"When we transition to a different location, or like now, cut to a flashback
scene, always set the color palette in the prompt."** No Santiago, um flashback é
frio e o outro é quente, de propósito.

### 2.3. Props

🎓 **Prop recorrente ganha folha própria, com MÚLTIPLOS ÂNGULOS.**
*Animated Short, aula 3 — o relógio que aparece nas 8 cenas:* **"most
importantly, multiple angles. That last part is very important. Seedance needs to
know what this watch looks like from every direction to keep it consistent across
eight shots."**

### 2.4. Figurantes e personagens de uma aparição só

🎓 **Personagem que aparece UMA vez não precisa de folha.** *Santiago, aula 11:*
**"I didn't create a separate image for the old man here and just got him from
the prompt. If a character appears only once in a prompt, you can usually get
away with something like this."**

🎓 **Multidão não se pede como multidão — se constrói por CLASSES.**
*Fight scenes, aula 2:* **"the army looked like a crowd of identical clones. To
fix this, you shouldn't just ask for a crowd. You need to build distinct
character classes for your extras. I created two new classes, a heavy masked
brute and a light scout. This gives you instant silhouette variety, making the
army look real and keeps the same exact warriors consistent across every
generation."**

### 2.5. Nomear e registrar

🎓 *Blockbuster, aula 3 — "the step that looks boring, but pays off the most":*
**nomear cada asset → apresentar ao Claude por esse nome → registrar no
Higgsfield como Element com o nome EXATAMENTE igual.** *"during scene generation,
the prompts will auto-match your inputs by these tags, so nothing gets mixed
up."*
*Fight scenes, aula 1:* **"attach your assets with their names. So Claude writes
the tags, like @Rocco, @Monster, directly into the prompt."**

---

## 3. O PROMPT — estrutura e linguagem

### 3.1. A estrutura oficial (guia de prompt, não aula)

🎓 **Prosa em bloco contínuo, com seções rotuladas em caixa alta**, nesta ordem:

```
GLOBAL STYLE → SCENE → CHARACTERS → LOCATION → FIRST FRAME AND BLOCKING
→ Shot 1..N (cada um terminando em "Hard cut" onde houver corte)
→ OPTICS and CAMERA → PHYSICS → LIGHTING → AUDIO
```

🎓 **"Most working Seedance 2.5 prompts follow the same shape: one visual rule at
the top, one sound rule at the bottom, and everything in between broken into
shots."**

🎓 E a frase que confirma a nossa §2.1 literalmente:
**"Generation parameters are not prompt text"** — resolução, duração e proporção
se escolhem no gerador; escrevê-las na prosa não faz nada.

🎓 **Notação de áudio dentro da prosa:** `( )` música · `< >` efeito sonoro ·
`{ }` diálogo · `【 】` legenda.

### 3.2. Tamanho real dos prompts oficiais — medido

| | chars |
|---|---|
| menor | **1.020** |
| maior (fronteira limpa) | **7.084** |
| mediana | **~6.300** |
| acima de 5.000 | **8 dos 10** |

> Isto corrige um número que entrou no nosso corpus como "grosso modo entre 2.000
> e 4.000". **Está errado.** A massa dos prompts oficiais está entre 5.000 e
> 7.000.

### 3.3. ⚠️ A ARMADILHA DA NEGAÇÃO — e ela derruba doutrina nossa

**Três aulas independentes dizem a mesma coisa, e a terceira dá o nome:**

🎓 *Santiago, aula 7:* **"There are positive prompts and negative ones. And with
Seedance, we don't need the negative at all because the model doesn't get them
and does quite the opposite. Like if you write 'he's not crying', Seedance just
gets confused. Tell it what you want instead. For example, an anxious look."**

🎓 *Fight scenes, aula 2:* **"Even though the prompt explicitly said 'no held
objects, no handle', it still forced a hand holding a sword. Telling the model
what not to do rarely works. And as we found out, negative prompting here was the
wrong play. And the fix, you are gonna laugh. Just ask the model to raise his arm
so that the model actually sees it."**

🎓 *Fight scenes, aula 5 — **"the negation trap"**:* **"Even though we wrote 'not
a game, no CGI' a dozen times, we fell right back into the negation trap. Look,
now we know that AI models completely ignore the word 'not'. It just sees 'game'
a dozen times and goes with it."** → **"Step one, swap bans for direct
descriptions. AI gives you what you ask for, not what you ban. So instead of
telling it 'no cheap effects', just describe the actual lighting and textures you
want. Focus on what you want and just delete the rest."**

**O conflito, declarado:** o **guia oficial de prompt do mesmo Higgsfield** usa
negativas o tempo todo — *"No logos, no readable text on anything"*, *"no music,
no discernible dialogue"* — e o prompt bank público escreve movimento de câmera
inteiramente por negação: *"no dolly, no truck, no arc, no slide, no zoom, no
tilt"*.

**São duas fontes oficiais da mesma empresa em desacordo.** Não escolho.

**Leitura minha, marcada como minha:** o modo de falhar nomeado é o modelo
**atender ao substantivo dentro da negação** — "not a game" entrega jogo. Isso é
devastador quando o substantivo negado é **um estilo ou um estado vívido**
("jogo", "CGI", "chorando") e inofensivo quando é **um objeto ausente e genérico**
("logo", "texto"). A regra que sobrevive aos dois lados e não depende do meu
palpite: **descrever o que se quer é obrigatório; negar é, no máximo, cinto de
segurança, nunca o mecanismo.**

**O que isso toca no nosso corpus:** as "regras negativas testadas" do
`seedance-receituario.md`, o bloco `NEGATIVES` da §3 do `REGRAS-PRODUCAO-VIDEO.md`
e a mendicância *"No music. No score."* Nada disso deve ser apagado sem teste —
mas nenhum deles deve continuar sendo o **mecanismo principal**.

### 3.4. Números no lugar de adjetivos

🎓 *Fight scenes, aula 2:* **"Notice we didn't just say 'fast', we said 'three
times faster than a typical cinematic dolly pull'. AI models don't really get big
descriptions, but they understand direct comparisons."**

🎓 *Fight scenes, aula 3:* **"the shot comes down to math instead of adjectives.
The camera orbit is written in raw numbers, eight meters down to four, three
meters high down to two, because video models prefer arithmetic over vague words
like 'dramatically'."**

🎓 *Fight scenes, aula 3 — ação em passos de meio segundo:* **"We break down the
foreground rise into half-second steps, hand at 0.5, helmet at 1.5, standing by
three. When the timing is locked, the model can't rush it or skip stages."**

🎓 *Fight scenes, aula 4 — tensão em centímetros:* **"we didn't just say 'time
slows down'. We mapped out the distance between the blades second by second."**

### 3.5. Mostrar em vez de descrever

🎓 *Blockbuster, aula 6 — e este é um método que não temos:* **"Instead of
explaining the geometry in words, I give Claude a picture. I literally draw where
the cannonball should hit and where everyone stands. One drawing tells the model
what 10 sentences can't. Also, every failed batch you avoid saves you credits."**

🎓 *VFX, aula 6:* **"when you already know exactly what you want, it's better to
show the AI than to describe it."**

### 3.6. Palavras-chave de estilo carregam a cena inteira

🎓 *Animated Short, aula 4:* **"Two phrases are really important here: 'French
graphic novel style' and 'futuristic environment'. Swap those out and you get a
completely different scene."**

---

## 4. DIREÇÃO — o que a skill deles decide sozinha

### 4.1. O contrato, na voz do fabricante

🎓 *Santiago, aula 6:* **"I built a custom prompt builder skill loaded with
director hacks that handles everything for you. It splits the scene into shots
automatically and picks the framing, close-ups, medium shots, all of it. That way
you get real camera angle changes in your generations, just like an actual
movie."**

🎓 *Blockbuster, aula 4:* **"I don't write prompts by hand. I use a skill I built
in Claude. (...) It splits the scenes into shots and writes detailed prompts that
enhance your idea. (...) upload all the assets the shot needs, plus the script,
and tell what happens in the first scene."**

🎓 *Fight scenes, aula 1 — o que a skill deles faz, em quatro partes:* **"It tags
your assets with simple anchors, locks spatial coordinates in meters, writes
time-coded movements in seconds, and sets strict rules to stop the model from
hallucinating."**

> **Isto é o contrato de direção do Samuel, validado por quem construiu a
> ferramenta.** A pessoa entrega o que acontece na cena; a skill quebra em planos
> e escolhe o enquadramento.

### 4.2. Diálogo entre duas pessoas — a regra dos 180° e o que a sustenta

🎓 *Blockbuster, aula 9:* **"I'm telling Claude to keep the camera completely
static, showing Cindy from the exact same angle during her lines, and cutting to
the main character over her left shoulder during his lines. So that's the 180
degree rule. Break it, and the audience stops knowing who's standing where."**

🎓 **E a técnica que faz isso funcionar de verdade — referência de ângulo reverso
do AMBIENTE:** *Blockbuster, aula 9:* **"Cindy's background changes from
generation to generation, and if your background shifts when you cut between
characters, the scene will never piece together in the edit. (...) When making a
dialogue scene with reverse angles, you must generate reverse angle environment
references of the same room. Feed the model images of what both sides of the room
look like. That gives the model a blueprint of the room and the background stops
jumping between cuts."**

🎓 **O mesmo princípio, na cena de ação:** *Fight scenes, aula 1:* **"We
explicitly built two distinct angles. A front view with a single crimson tree and
a completely empty back view. Locking in both sides matters for action scenes.
The AI stops guessing what's behind the character and the batches stop
drifting."**

🎓 **Plano aberto de estabelecimento trava a marcação.** *Santiago, aula 12:*
**"If you're struggling with positioning your characters where you want them to
be, start the video with a wide establishing shot. That way Seedance places
everyone exactly where they need to be and they stay locked for the entire
video."**

> Estas três técnicas atacam exatamente o problema que o Samuel corrigiu à mão —
> duas pessoas conversando que saíam artificiais. E nenhuma delas está no nosso
> corpus.

### 4.3. Movimentos e o que cada um compra

| Movimento | Para quê | Regra de uso | Fonte |
|---|---|---|---|
| **Dutch angle** | tensão, desconforto, personagem perdendo o controle | deixar **quase nenhum espaço** entre personagem e borda do quadro = sensação de encurralado | Santiago 8 |
| **Speed ramp** | congelar o instante decisivo | a velocidade muda **dentro** do plano: cai em slow-mo e volta ao normal no impacto | Santiago 13 |
| **Whip pan** | transição, segurar atenção | **dar duração** e **rotular os sujeitos A, B, C**; e **tem de terminar no mesmo tipo de plano em que começou** — médio→close é erro | Santiago 14 |
| **Match cut** | emendar cenas | anexar o **último frame** da cena anterior como referência | Santiago 10 |
| **Handheld** | presença de operador | *"subtle movements from walking and breathing"* | Santiago 10 |
| **Bullet time** | impacto | é o mais caro: força o modelo a rastrear física, dois corpos, dilatação de tempo e arco de 180° ao mesmo tempo | Fight 4 |

🎓 *Santiago, aula 8:* **"in a good film, the movement alone isn't enough to carry
the emotion. You need dynamic camera work to take over."**

### 4.4. A cura para o "cara de videogame"

🎓 *Fight scenes, aula 5 — o problema:* **"the fight looks sick, but it feels like
a video game cutscene (...) that continuous camera floating right behind the
hero, that's straight out of a third-person video game. Real movies don't shoot
like that."**

🎓 **A cura, e ela é estrutural:** **"one long, unbroken take is exactly how video
games look. Real movies cut. So we made the model edit like a director. Four hard
cuts, each with its own camera setup. A 50mm orbit, a 24mm low angle, an 85mm
close-up, and a 35mm wide."**

> **Cobertura variada dentro do mesmo plano gerado é o que separa cinema de
> gameplay.** Isso vale para bloco de criatura tanto quanto para luta.

---

## 5. ITERAÇÃO — ler o que quebrou e consertar só aquilo

### 5.1. A regra de diagnóstico, e ela é barata

🎓 *Fight scenes, aula 2:* **"Always generate four at once. That way, if a take
looks weird, you immediately know if it's a random glitch or your prompt."**

🎓 *Santiago, aula 7:* **"If all four videos in your batch came out wrong, the
issue is probably in the prompt."**

🎓 *Fight scenes, aula 4:* **"this wasn't a prompt issue, it was just a batching
game. (...) Knowing the difference between a broken prompt and a bad roll is how
you save credits."**

> **4/4 errados = prompt. 1 ou 2 errados = sorte.** É a régua de diagnóstico mais
> barata que existe, e nós não temos nenhuma.

### 5.2. O laço

🎓 *Blockbuster, aula 6:* **"Run it, look at it, ask for the exact changes, and
run it again. It's a skill that gets better with practice."**

🎓 *Fight scenes, aula 2 — e esta é a frase que resume o curso inteiro:*
**"That's the actual skill in this workflow. Not writing one genius prompt, but
reading what broke and fixing only that. So that's the playbook. Look at the
generation, call out what's broken in simple words, and let Claude rebuild the
prompt."**

### 5.3. Escada de simplificação quando o plano não fecha

1. 🎓 **Multi-shot falhou → cair para UM plano contínuo.** *Blockbuster, aula 8:*
   **"Since the multi-shot approach failed, I decided to focus only on the opening
   POV shot."**
2. 🎓 **Cena apertada demais → partir em duas.** *Santiago, aula 17:* **"since
   there's so much happening in just 15 seconds, the scene feels way too rushed.
   (...) I'm going to split the scene in two so it doesn't feel rushed anymore."**
3. 🎓 **Cena grande demais → Claude escreve o prompt inteiro e depois divide.**
   *Santiago, aula 18:* **"have Claude write out the full prompt first and then
   split it into three separate scenes (...) 8A, 8B and 8C."**
4. 🎓 **Plano chapado → aumentar a cobertura.** *Santiago, aula 8:* **"Let's split
   the scene into three shots instead of two and bring in some interesting camera
   angles."**

### 5.4. Consertos nomeados nas aulas

| Defeito | Conserto | Fonte |
|---|---|---|
| objeto some/aparece entre planos (terceira cadeira) | descrever posição no primeiro frame | Santiago 7 |
| evento acontece em lugar diferente a cada geração (bala de canhão) | pôr o evento **no primeiro frame** + desenhar a geometria | Blockbuster 6 |
| figurino muda de estado e "se remenda" sozinho | **gerar nova folha de personagem já com o estado novo** (calça rasgada) | Blockbuster 8 |
| personagem correndo na direção errada | declarar a direção ("sempre em direção ao oásis") | Blockbuster 7 |
| perseguidores colados demais para haver perseguição | afastar por instrução explícita | Blockbuster 7 |
| criatura cartunesca demais | **trocar o asset**, não o texto | Blockbuster 8 |
| membro/anatomia impossível que o modelo insiste em "consertar" | **fazer o personagem levantar o braço** para o modelo VER | Fight 2 |
| POV interpretado ao pé da letra | descrever a mecânica ("o olho abre como persiana") | Blockbuster 8 |
| escrita ilegível na tela | regerar — *"AI slop has no place in a cinematic film"* | Santiago 14 |
| mão plastificada e perfeita demais | pedir realismo explícito | Santiago 12 |
| plano que não pertence à sequência | mandar apagar o plano | Blockbuster 6 / Santiago 12 |
| emoção incoerente com a cena anterior | **dar o contexto da situação ao Claude** | Santiago 14 |

🎓 *Blockbuster, aula 8 — trocar asset é normal:* **"Changing your assets
mid-duration is completely normal if you want to avoid a plastic look or make the
action clearer. I always keep a few asset variations ready just for moments like
this."**

---

## 6. CONTINUIDADE ENTRE CENAS

🎓 **A receita completa de encadeamento** — *Animated Short, aula 4:*
**"I'm uploading that keyframe into Claude along with the prompt from the previous
animation. So Claude knows exactly what happened in scene 1, he keeps the style,
the character, the teleport effect. (...) Then I feed Seedance the prompt, the
keyframe for style reference, and most importantly the previous video. That's how
you keep a story consistent across scenes."**

> Três entradas: **prompt anterior → para o Claude** · **keyframe → estilo** ·
> **vídeo anterior → para o Seedance**. A nossa §4 do REGRAS já tinha a terceira;
> as duas primeiras são novas.

🎓 **Continuidade de pose através do corte** — *Fight scenes, aula 4:* **"We give
the model a strict instruction. The poses at the end of shot one exactly match
the start of shot two. If you don't spell this out, the AI treats the cut as a
brand new scene and throws away the poses."**

🎓 **Envelhecer/rejuvenescer personagem para flashback** — *Santiago, aula 15:*
anexar a folha normal e pedir prompt que o transforme em criança de sete anos.

🎓 **Ritmo entre cenas** — *Santiago, aula 17:* **"you cannot jump straight into
dialogue right after a flashback. There needs to be a one to two second pause for
the character to process it."**

🎓 **Narração como geração separada** — *Santiago, aula 16:* gerar um plano só
para colher a fala e sobrepor, descrevendo **tom e pausas**: *"with micro pauses,
a little self resentment and a trembling voice."*

---

## 7. ESCALA, AÇÃO E FÍSICA

🎓 **Escala em três camadas, nunca por número** — *Fight scenes, aula 3:* **"The
prompt never says 'show a thousand soldiers'. It just fills the frame in three
layers. One sharp warrior up front, a dense crowd behind him, and silhouettes
fading into the mist. You only see about 40 soldiers clearly, but your brain fills
in the rest."**

🎓 **Névoa como limpeza barata** — *Fight scenes, aula 3:* **"We intentionally put
the scene in thick fog, capping visibility at 20 meters. At this scale, the AI
will glitch out in the background. The fog simply hides those mistakes. (...) If
your scene is packed, fog is the cheapest cleanup you'll ever do."**

🎓 **Transformação: número duro + enquadrar como mecânica, não como magia** —
*Fight scenes, aula 3:* **"We gave it a hard number, 0.4 seconds. And to make the
reveal epic, we told the model straight up, this is a weapon deploying, not a
magic sequence, because if you let a transformation take its time, you get a
glowing anime power up. Every single time. The instant snap is what keeps it
real."**

> **Isto serve diretamente às metamorfoses de criatura do canal.** É a diferença
> entre transformação com peso e brilho de anime.

🎓 **Impacto escrito como física** — *Fight scenes, aula 4:* **"Skip 'sword clash'
and map out the angles. The vertical chop meeting a diagonal parry. Set one hard
rule. Crystal always beats steel. The model gets the hint, and steel shatters."**

🎓 **Finalização que dá corte de graça** — *Fight scenes, aula 3:* **"The entire
army drops into a stance at once, their eyes glow red, and everything freezes. It
creates instant tension, and a free cliffhanger for the edit."**

---

## 8. RUBRICA DE ACEITAÇÃO — como ler um take

Do curso de avaliação, e é o material que preenche o buraco que tínhamos: sabíamos
corrigir, não sabíamos **quando aprovar**.

### 8.1. O sinal mais importante: corte rápido é ESCONDERIJO, não estilo

🎓 *Evaluate, aula 2:* **"watch how it cuts. Fast, chaotic, new angle every
second. And I'll tell you why. It's hiding. Quick cuts are what this model does
when it can't animate the motion underneath."**
🎓 *Evaluate, aula 5:* **"When this model can't hold the movement, it cuts away
and hopes you won't notice."**

### 8.2. Checklist derivada das aulas

| Área | O que procurar |
|---|---|
| **Peso** | o golpe **deixa marca**; brasas **caem e assentam** em vez de sumir; criatura pesada "you can feel the scale" |
| **Morte/remoção** | *"doesn't just die so much as get deleted. One frame he's there, next frame he's gone"* = reprovado |
| **Rosto sob esforço** | *"Screaming is where AI faces usually fall apart because the whole face has to commit"* |
| **Lente de verdade** | fisheye real: *"his hand warps before his face does"*. Fisheye falso: *"the edges of the frame curve and nothing else does. It's more of a filter than a lens"* |
| **Coreografia** | membros que se atravessam nos movimentos rápidos; postura que "reseta" entre passos |
| **Materiais** | maquiagem/brilho que "vira mingau" quando a cabeça vira |
| **Reflexos** | *"Reflections used to be a dead giveaway"* |
| **Luz através dos cortes** | *"The candle flicker matches across every single angle. The light source keeps its rhythm across cuts"* |
| **Continuidade do personagem** | *"The scars, the torn clothes, locked. Every angle, every lighting change, same monster"* |
| **Olhar** | rejeitado por *"his eye tracking was a bit messed up. He was looking all over the place"* |
| **Câmera como objeto** | no registro UGC: *"It understands that the camera is a phone, not a floating viewpoint. A physical object with a body. The pan moves like a wrist and not a crane"* |
| **Duração** | *"15 seconds ran out at the exact peak of the drama"* — o plano não pode acabar antes da batida |

🎓 **E a regra de acúmulo, que é a que mais importa:** *Evaluate, aula 7:*
**"Each one is pretty minor, but together, they're the difference between an ad
and an AI ad."**

---

## 9. ECONOMIA

🎓 **Imagem é praticamente de graça, e isso mudou o comportamento certo.**
Soul Cinema: *"Four generations cost only half a credit"* (Animated 3);
*"eight batches just for one credit"* (Realism 6). **Regenerar é o comportamento
correto, não o desperdício.**

🎓 **Sempre 4 de uma vez** — é diagnóstico, não luxo (ver §5.1).

🎓 **Combinar pedaços de gerações diferentes é o padrão, não o remendo.** Aparece
em praticamente todas as aulas: abertura de um batch, reação de outro, corrida de
um terceiro.

🎓 **Cada batch falho evitado é crédito salvo** — *Blockbuster, aula 6.*

🎓 **Personagem de uma aparição só não consome asset** (§2.4).

---

## 10. ROTEAMENTO DE FERRAMENTA

🎓 *Realism, aula 6 — a regra explícita:*

| Para | Modelo | Por quê |
|---|---|---|
| personagens, locações, keyframes | **Soul Cinema** | *"eight batches just for one credit, and it just gives you a much more cinematic shot by default"* |
| **texto, movimento ou storyboard** | **GPT Image 2** | *"GPT Image 2 is your best option"* |
| editar/corrigir personagem existente | **Nano Banana Pro** | *"Soul Cinema gives you the style, but Nano Banana Pro fixes the character"* (Animated 5) |
| folha de personagem fotorrealista com referência | **GPT Image 2** | *"the best model right now for editing and creating a photorealistic character sheet when you already have a reference"* (Blockbuster 3) |

🎓 **Cor em 10 bits** — *Realism, aula 5:* **"Seedance outputs in 10-bit color
now. (...) More colors mean smoother blends. So the smoke and reds melt together
instead of stepping into those ugly bands. (...) To take advantage of that, just
set the bit rate to high right here."** Parâmetro que não conhecíamos.

🎓 **O enhancer — e aqui há uma nuance contra a nossa doutrina.** *Animated, aula
3:* **"Turn on the enhancer in Soul Cinema, type something as simple as 'cartoon
style man waking up in the bedroom' and just let it go wild. It's incredibly
creative and you'll get styles that you might have never even thought to ask
for."**

> **Não contradiz a nossa recomendação de enhancer desligado.** O uso deles é
> **exploração de estilo em IMAGEM**, com prompt curto e proposital. A nossa
> recomendação é sobre o **prompt de vídeo hiperespecificado**, onde o reescritor
> apagaria a âncora de realismo. São dois usos diferentes — vale registrar a
> distinção em vez de tratar como conflito.

---

## 11. VÍDEO SOBRE FOOTAGE REAL — capacidade que não temos registrada

🎓 **Claude lê vídeo como FRAMES** — *VFX, aula 2:* **"it doesn't watch the video
the way you and I do. It reads it as a set of frames (...) so it understands
exactly what's in the shot."**

🎓 **A LISTA DE PRESERVAÇÃO** — *VFX, aula 2:* **"the skill writes down everything
that has to stay exactly as I shot it. My face, my walk, the rings on my hand,
every gesture, and the exact handheld camera move, and locks it. It also writes
the exact seconds to change the background."**

> **Uma lista explícita do que NÃO pode mudar, com os segundos da mudança.**
> É uma estrutura transferível para qualquer prompt nosso, não só para VFX.

🎓 **Relighting automático** — *VFX, aula 3:* **"Seedance pulled the light straight
from the generated environment and bounced it onto me."** E física não pedida:
*"It adds a breeze blowing through my hair, even though my original shot didn't
have it."*

🎓 **Plano travado é fácil, handheld é o caso difícil** — *VFX, aula 7:* **"On
locked off or steady shots, the AI has it easy. The frame barely changes, so it
just paints the effects in. But the second the camera's in your hand, everything's
moving chaotically."**

---

## 12. O QUE NÃO SE APLICA A NÓS

- **Todo número de resolução e duração.** Eles rodam 4K/15s (2.0) e 30s (2.5).
  Nós rodamos 480p.
- **Cinema Studio como lugar de trabalho** — eles usam a interface web com Canvas
  e Elements. Parte disso é acessível a nós, parte não; isso é decisão de
  arquitetura, não achado.
- **"4K resolve slop"** aparece em vários cursos como argumento de qualidade.
  É verdade deles e irrelevante para o nosso orçamento — o nosso caminho é gerar
  baixo e fazer upscale local de graça.
- **O curso de VFX inteiro** só serve se o canal passar a usar footage real.
  Decisão do Samuel, não achado.

---

## 13. O QUE FICOU EM ABERTO

1. **A skill oficial `higgsfield-seedance-prompt.skill`** — mencionada em quatro
   cursos, baixável no post de cada um. **Não foi baixada.** É o item de maior
   valor ainda por buscar: é o construtor de prompt do fabricante, e as aulas
   descrevem o que ele faz (tags, coordenadas em metros, movimento com segundos,
   regras anti-alucinação) sem mostrar o interior.
2. **Os posts de blog de cada curso** trazem *"the full script, every single
   prompt, the asset sheets"*. Nenhum foi lido.
3. **A contradição das negativas** (§3.3) não tem resolução com fonte.
4. **Os 9 cursos das outras duas categorias**, incluindo dois sobre canal faceless
   com Claude + Higgsfield, que é a nossa arquitetura exata.
