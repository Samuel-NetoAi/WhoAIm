# Rubrica de aceitação de take — quando APROVAR

> Criado em **2026-09-02**. Preenche o buraco que a gente sabia ter: existia ordem de correção
> para quando o take **falha**, e nenhum critério escrito para quando ele **passa**.
>
> Fonte: 🎓 curso *How to evaluate AI filmmaking demos* (11 aulas), em
> `ESTUDO-ACADEMY-HIGGSFIELD-completo.md` §8. Marcadores: 🎓 Academy · ⚫ decisão do Samuel.

---

## 1. ⚫ A RÉGUA — decisão do Samuel, 2026-09-02

> **Aprovar o BOM. Rejeitar só o que está abaixo de mediano.**

**Por quê, nas palavras dele:** *"precisamos de conteúdo nesse começo de canal, não podemos nos dar
ao luxo de desperdiçar uma cena que ficou boa mas não excelente."*

- **Excelente** → aprova.
- **Boa, não excelente** → **aprova.** Não regerar atrás de excelente. Este é o ponto da decisão.
- **Mediana** → aprova se nada da §3 estiver quebrado. É o piso.
- **Abaixo de mediana, ou qualquer item da §3 quebrado** → rejeita.

> ⚠️ **Tensão registrada, de propósito.** 🎓 A Academy prega o oposto: *"Each one is pretty minor,
> but together, they're the difference between an ad and an AI ad."* — a soma de defeitos pequenos
> é o que denuncia vídeo de IA. **Isto é uma troca consciente de qualidade por volume, tomada para
> a largada do canal**, não um desacordo técnico. Revisitar quando a gaveta estiver cheia.
>
> O que a tensão **não** autoriza: deixar passar item da §3. Aqueles não são "defeito pequeno",
> são o que faz o espectador sentir que é IA.

---

## 2. O SINAL MAIS IMPORTANTE — corte rápido é esconderijo

🎓 *"watch how it cuts. Fast, chaotic, new angle every second. And I'll tell you why. **It's
hiding.** Quick cuts are what this model does when it can't animate the motion underneath."*
🎓 *"When this model can't hold the movement, it cuts away and hopes you won't notice."*

> **Corte rápido que você NÃO pediu = rejeição automática.** Não é estilo, é o modelo escondendo
> movimento que não conseguiu animar. E é o sinal de que o bloco era AÇÃO tratado como SIMPLES —
> ver `direcao-bloco-acao.md` §1.

---

## 3. REPROVAÇÃO AUTOMÁTICA — não passa, mesmo com pressa

| Área | O que reprova |
|---|---|
| **Corte** | picotagem que não foi pedida (§2) |
| **Peso** | golpe que não deixa marca; brasa que some em vez de cair e assentar; criatura pesada sem escala sentida |
| **Morte/remoção** | 🎓 *"doesn't just die so much as get deleted. One frame he's there, next frame he's gone"* |
| **Coreografia** | membros que se atravessam; postura que "reseta" entre passos |
| **Continuidade do personagem** | cicatriz, roupa rasgada ou proporção que muda entre planos |
| **Olhar** | 🎓 *"his eye tracking was a bit messed up. He was looking all over the place"* |
| **Duração** | 🎓 *"15 seconds ran out at the exact peak of the drama"* — o plano acaba antes da batida |

---

## 4. OLHAR COM ATENÇÃO — pesa, mas não reprova sozinho

Com a régua da §1, estes descem de "rejeitar" para "notar, e só rejeitar se vierem em bando":

- **Rosto sob esforço** — 🎓 *"Screaming is where AI faces usually fall apart because the whole face
  has to commit."*
- **Lente de verdade × filtro** — fisheye real: *"his hand warps before his face does"*. Falso:
  *"the edges of the frame curve and nothing else does."*
- **Materiais** — brilho ou maquiagem que "vira mingau" quando a cabeça gira.
- **Reflexos.**
- **Luz através dos cortes** — 🎓 *"The candle flicker matches across every single angle. The light
  source keeps its rhythm across cuts."*

---

## 5. ⚫ FUNDO E FIGURANTES — decisão do Samuel, 2026-09-02

> **O fundo tem comportamento coerente, descrito em uma linha. Nem abandonado, nem detalhado.**

**O erro a evitar:** os personagens principais fazendo algo enquanto os figurantes ao fundo estão
parados, repetindo um gesto, ou fazendo coisa que não bate com o que deveriam estar fazendo. Fundo
morto denuncia a cena inteira.

**O erro oposto, igualmente caro:** detalhar figurante a ponto de disputar o foco. O fundo existe
para ser **orgânico**, não para ser lido.

**Como escrever, na prática:**

- **Uma linha por camada de fundo**, dizendo a ATIVIDADE, não o indivíduo. *"remadores mantendo o
  ritmo, alguns olhando para o combate"* — não *"um remador de barba ruiva vira a cabeça"*.
- **Por classe, não por pessoa** (ver `direcao-bloco-acao.md` §3.2).
- **Coerente com o que a cena pede deles.** Se a tripulação está sob ataque, ninguém ao fundo está
  remando tranquilo.
- **Sem nome, sem rosto declarado, sem ação própria que compita** com a ação principal.

### 5.1. O blur de fundo é ferramenta de pós, e é barata

⚫ **Decisão do Samuel:** quando um elemento de fundo atrapalha num take que no resto está bom,
**mascarar com desfoque na pós é preferível a refazer a cena.** Refazer custa 75 créditos; o
desfoque custa zero e roda local.

Vale também como escolha de direção, não só como remendo: profundidade de campo rasa é linguagem
de cinema, e 🎓 a névoa cumpre o mesmo papel dentro do prompt (`direcao-bloco-acao.md` §3.3).

> **Ordem quando o fundo estragou um take bom:** (1) desfoque ou recorte na pós → (2) usar o melhor
> quadro como referência de uma nova geração → (3) só então regerar do zero.

---

## 6. COMO USAR ISTO COM A RÉGUA 4/4

A régua 4/4 (`direcao-bloco-acao.md` §4.1) e esta rubrica trabalham juntas:

1. Gerar 4 (bloco de ação) ou 1 (bloco simples).
2. Passar cada take pela §2 e pela §3.
3. **Todos os 4 reprovados na mesma coisa → o prompt está quebrado.** Consertar só aquilo.
4. **1 ou 2 reprovados → foi sorte.** Pegar o melhor e seguir.
5. Entre os aprovados, **escolher e seguir** — não regerar atrás de excelente (§1).
