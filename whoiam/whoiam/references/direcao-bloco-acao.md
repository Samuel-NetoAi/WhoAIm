# Direção de bloco de AÇÃO — blueprint antes do movimento

> Criado em **2026-09-02**. Preenche um buraco declarado: a classificação AÇÃO/SIMPLES dizia
> **quanto gastar** num bloco de ação, nunca **como dirigi-lo**.
>
> Fonte: 🎓 curso *Direct AI fight scenes through controlled iteration* (5 aulas) e o curso de
> escala do mesmo pacote, transcritos em `ESTUDO-ACADEMY-HIGGSFIELD-completo.md` §7.
> Marcadores: 🎓 Academy · 🟢 catálogo ao vivo · 🔵 medido por nós · ⚫ decisão do Samuel.

---

## 1. O QUE CONTA COMO BLOCO DE AÇÃO

Não é lista de gêneros, é teste físico. **O critério é o que o modelo precisa animar**, não o
clima da cena. Um bloco é AÇÃO se tiver **qualquer uma** destas:

| Gatilho | Por quê | Exemplo do canal |
|---|---|---|
| **Contato entre corpos** | o modelo precisa preservar física através do impacto | Teseu golpeia o Minotauro; abordagem entre tripulações |
| **Transformação ou mudança de estado no plano** | o modelo tende a virar "power up de anime" | metamorfose de criatura; mastro que parte; parede que desaba |
| **3+ corpos em movimento coordenado** | multidão é onde o fundo quebra | as duas tripulações no convés; exército |
| **Câmera e sujeito rápidos ao mesmo tempo** | é o caso difícil declarado | fuga pelo labirinto; perseguição |

**Não é ação** (é SIMPLES, mesmo sendo tenso): criatura andando; revelação por luz parcial;
alguém correndo sozinho em quadro estável; diálogo, por mais carregado que esteja.

### 1.1. ⚫ PORTÃO — o blueprint não roda por padrão

> **Decisão do Samuel, set/2026: quem converte o prompt bruto dele (o Omega, o chat, quem for)
> tem que RECONHECER quando a ferramenta se aplica. Blueprint em cena que não é de ação é
> desperdício de tempo e de atenção — e polui o prompt.**

**Antes de abrir o blueprint, responder à tabela da §1.** Nenhum gatilho marcado → **bloco SIMPLES,
segue o fluxo normal**, sem esquema, sem medidas em metros, sem 2 takes.

E declarar a escolha na ficha do bloco, em uma linha, para ela ser auditável:

```
CLASSIFICAÇÃO: SIMPLES — nenhum gatilho de ação
CLASSIFICAÇÃO: AÇÃO — contato entre corpos (Teseu golpeia) + 3+ corpos (tripulação)
```

⚠️ **Errar para o lado caro também é erro.** Marcar tudo como ação "por segurança" é o mesmo que
aplicar 4/4 em tudo: derruba o canal de 4,3 para 1,5 vídeos/mês (§4.2). O portão existe nos dois
sentidos.

> ⚠️ **O sintoma de ter errado a classificação:** o take sai **picotando sozinho**, cortando a
> cada segundo. 🎓 *"Quick cuts are what this model does when it can't animate the motion
> underneath."* Corte rápido que você não pediu é o modelo escondendo movimento que não deu conta.
> Bloco que faz isso era AÇÃO e foi tratado como SIMPLES.

---

## 2. O BLUEPRINT — e ele custa ZERO crédito

**Isto é trabalho de papel, feito ANTES de qualquer geração.** 🎓 *"Blueprint the fight before
motion."* O gasto do bloco de ação não está aqui — está no §4. Não economizar nesta etapa é o que
torna o §4 pagável.

### 2.1. Desenhar a geometria, não descrevê-la

🎓 *"Instead of explaining the geometry in words, I give Claude a picture. I literally draw where
the cannonball should hit and where everyone stands. **One drawing tells the model what 10
sentences can't.**"*

Um esquema tosco — bonecos de palito e setas — resolve o que parágrafo nenhum resolve: quem está
onde, quem olha para onde, por onde entra o golpe, para onde o corpo cai.

### 2.2. Medida numérica em tudo

🎓 *"video models prefer arithmetic over vague words like 'dramatically'."* Trocar adjetivo por
número ou por comparação:

| Em vez de | Escrever |
|---|---|
| "a câmera se aproxima dramaticamente" | "órbita de 8 m para 4 m, altura de 3 m para 2 m" |
| "rápido" | "três vezes mais rápido que um dolly cinematográfico típico" |
| "ele se levanta" | "mão no chão em 0,5 s, elmo erguido em 1,5 s, de pé em 3 s" |
| "ela se transforma" | "0,4 s, snap seco" (ver 2.5) |

🎓 *"When the timing is locked, the model can't rush it or skip stages."*

### 2.3. Referência de locação nos DOIS ângulos

🎓 *Fight scenes, aula 1:* *"We explicitly built two distinct angles. A front view with a single
crimson tree and a completely empty back view. **Locking in both sides matters for action scenes.
The AI stops guessing what's behind the character and the batches stop drifting.**"*

Gerar a locação **de frente e de costas** e alimentar as duas. Custa 2 imagens (ruído no orçamento,
ver §4) e é o que impede o fundo de pular entre os cortes.

### 2.4. Plano aberto de estabelecimento primeiro

🎓 *"start the video with a wide establishing shot. That way Seedance places everyone exactly where
they need to be and **they stay locked for the entire video**."*

Numa cena com muita gente, o plano aberto não é enfeite: é o que trava a marcação de todo mundo
para o resto do bloco.

### 2.5. UMA regra física dura, declarada

🎓 *"Skip 'sword clash' and map out the angles. The vertical chop meeting a diagonal parry. **Set
one hard rule. Crystal always beats steel.** The model gets the hint, and steel shatters."*

Uma frase que diz o que vence o quê. Sem ela o modelo faz os dois materiais empatarem.

E para transformação: 🎓 *"this is **a weapon deploying, not a magic sequence**, because if you let
a transformation take its time, you get a glowing anime power up. Every single time. The instant
snap is what keeps it real."* → **número duro + enquadrar como mecânica.**

---

## 3. MULTIDÃO E ESCALA — a batalha grande

### 3.1. Nunca pedir número

🎓 *"The prompt never says 'show a thousand soldiers'. It just fills the frame in **three layers**.
One sharp warrior up front, a dense crowd behind him, and silhouettes fading into the mist. You
only see about 40 soldiers clearly, but your brain fills in the rest."*

**As três camadas:** (1) um sujeito nítido à frente · (2) massa densa atrás · (3) silhuetas
sumindo. Pedir "50 marinheiros" produz contagem errada e rostos derretidos.

### 3.2. Figurante se constrói por CLASSE, não como massa

Dois ou três arquétipos distintos (ex.: remador de torso nu · besteiro de gibão · timoneiro de
capa) dão variedade de silhueta **e** consistência. "Uma multidão de piratas" não dá nem uma coisa
nem outra.

### 3.3. Névoa é a limpeza mais barata que existe

🎓 *"We intentionally put the scene in thick fog, capping visibility at 20 meters. At this scale,
the AI will glitch out in the background. The fog simply hides those mistakes. **If your scene is
packed, fog is the cheapest cleanup you'll ever do.**"*

**Para a batalha no mar isto é de graça e é diegético:** bruma marinha, spray das ondas, fumaça de
canhão. Limitar a visibilidade a ~20 m esconde exatamente onde o modelo quebra — o fundo lotado.

### 3.4. Finalização que dá corte de graça

🎓 *"The entire army drops into a stance at once, their eyes glow red, and everything freezes. It
creates instant tension, and a free cliffhanger for the edit."* Terminar o bloco num congelamento
coletivo entrega o corte pronto para a montagem.

---

## 4. O QUE CUSTA — e a decisão de onde aplicar

**O blueprint é de graça.** O desenho é papel.

⚫ **E as imagens saíram do orçamento de crédito por completo (decisão do Samuel, set/2026):** ele
gera model sheets, locações e keyframes **fora do Higgsfield** — GPT Plus, Nano Banana Pro, Nano
Banana. Consequência dupla:

1. **Imagem não consome crédito do plano.** Os ~50 créditos/vídeo que a conta reservava para
   imagem somem. Todo o orçamento é vídeo.
2. **Iterar folha de personagem passou a ser de graça.** Não há mais razão para aceitar um model
   sheet mediano — regerar até acertar não custa nada. Isso vale especialmente para a referência de
   locação nos dois ângulos (§2.3), que antes parecia luxo e agora é gratuita.

> **A skill precisa ENTREGAR o prompt de imagem, não gerar a imagem.** O produto da Fase 1 é texto
> pronto para colar na ferramenta dele.

**O que custa é o número de takes de VÍDEO.**

### 4.1. A régua de diagnóstico

🎓 *"**Always generate four at once.** That way, if a take looks weird, you immediately know if
it's a random glitch or your prompt."* · 🎓 *"Knowing the difference between a broken prompt and a
bad roll is how you save credits."*

> **4 de 4 errados → o problema é o PROMPT. 1 ou 2 errados → foi sorte; regere.**

Isto substitui o palpite. Sem ele, reescreve-se prompt que estava certo — que é 🟡 o caminho que
mais custou no estudo dos 62.

### 4.2. A conta, no plano de 9.000

🔵 Base: Seedance 2.5 · 480p · 30 s = **75 créditos**. Vídeo padrão = 20 blocos = 10 min.
Retrabalho orçado ×1,4.

**Primeiro, o custo de UM bloco isolado** — é aqui que a conta costuma se perder:

| Takes por bloco | Conta | Custo do bloco |
|---|---|---|
| 1 take | 75 | **75** |
| 1 take + retrabalho ×1,4 | 75 × 1,4 | 105 |
| **2 takes** | 75 × 2 | **150** |
| 4/4 | 75 × 4 | **300** |

**Uma luta de 3 blocos, portanto, custa de 225 (1 take cada) a 900 (4/4).** O blueprint não entra
nessa conta — ele é zero.

**Agora o vídeo inteiro** (20 blocos = 10 min, sendo 3 de ação e 17 simples com retrabalho ×1,4):

| Regime nos blocos de AÇÃO | ação (3) | simples (17) | cr/vídeo | vídeos/mês em 9.000 |
|---|---|---|---|---|
| 1 take + retrabalho | 315 | 1.785 | 2.100 | **4,3** |
| **2 takes** ← recomendado | 450 | 1.785 | 2.235 | **4,0** |
| 4/4 | 900 | 1.785 | 2.685 | **3,3** |
| 4/4 em TUDO (não fazer) | 900 | 5.100 | 6.000 | **1,5** |

> ⚫ **Regra: começar com 2 takes no bloco de AÇÃO. Subir para 4/4 só no bloco que resistir.**
> Nos blocos SIMPLES, 1 take e regeração só se falhar.
>
> **Por quê 2 e não 4:** subir de 1 para 2 takes nos blocos de ação custa **0,3 vídeo por mês**.
> Subir para 4/4 custa **1 vídeo inteiro por mês**. Com 2 takes você já separa "os dois quebraram
> igual" (prompt) de "um saiu torto" (sorte) — é a mesma pergunta da régua, com menos resolução.
> O 4/4 vira útil quando o bloco já falhou uma vez e você precisa saber **se é o prompt** antes de
> reescrever. Aí os 300 créditos são mais baratos que reescrever um prompt que estava certo.

### 4.3. ⚫ A alavanca de custo mais forte é de DIREÇÃO, não de orçamento

**Desfocar o fundo e focar nos principais é mais barato que gerar a multidão.** Decisão do Samuel
para a batalha naval, e ela generaliza: profundidade de campo rasa + névoa transformam a tripulação
de fundo em **textura**, não em coreografia — e o modelo deixa de precisar animar 3+ corpos
coordenados com nitidez, que é exatamente o gatilho caro da §1.

Ela não deixa de ser cena de ação (os principais ainda se batem), mas **encolhe o número de blocos
de multidão**, que é o que pesa:

| Batalha naval | Custo |
|---|---|
| 5 blocos de multidão nítida, 4/4 | **1.500** (17% do mês) |
| 3 blocos focados nos principais, fundo desfocado, 2 takes | **450** |

**~1.050 créditos economizados por uma escolha de direção, não por corte de roteiro.** E o
resultado é melhor: multidão nítida é onde o modelo quebra rosto e conta gente errado.

### 4.4. Onde ainda dá para economizar sem perder a régua

### 4.3. Onde ainda dá para economizar sem perder a régua

- **Primeiro bloco de cada cena nova também merece 4/4**, mesmo sendo simples — é onde o prompt
  ainda não está provado. Depois que o prompt da cena acertou, os blocos seguintes herdam.
- 🎓 **Recortar o melhor quadro de uma tentativa e reusar como referência** continua sendo a
  primeira linha de correção (§5 do `REGRAS-PRODUCAO-VIDEO.md`) — o 4/4 dá 4 quadros bons para
  escolher, não só 4 vídeos.

---

## 5. ESCADA QUANDO O BLOCO DE AÇÃO NÃO FECHA

Na ordem, do mais barato ao mais caro:

1. **Multi-shot falhou → cair para UM plano contínuo.**
2. **Cena apertada → partir em duas.**
3. **Cena grande → escrever o prompt inteiro e depois dividir** (8A, 8B, 8C).
4. **Plano chapado → aumentar a cobertura** (2 planos viram 3, com ângulos diferentes).
5. **Só então** reescrever o texto.

🎓 A frase que resume o curso: *"That's the actual skill in this workflow. **Not writing one genius
prompt, but reading what broke and fixing only that.**"*

---

## 6. A CURA DO "CARA DE VIDEOGAME"

🎓 *"one long, unbroken take is exactly how video games look. **Real movies cut.**"*

A cura é **cobertura variada dentro do bloco gerado**: quatro cortes secos, cada um com sua ótica —
órbita 50 mm · contra-plongée 24 mm · close 85 mm · aberto 35 mm.

⚠️ **O sintoma a evitar: câmera flutuando atrás do personagem** é enquadramento de jogo em terceira
pessoa. Se o plano parece um gameplay, é porque a câmera virou um viewpoint em vez de um objeto.
