# Limite de caracteres, prosa × JSON, e o contrato de direção

> Apurado em **2026-09-02**. Fecha duas perguntas que estavam abertas há semanas
> e registra uma decisão nova do Samuel.
>
> Marcadores: 🟢 catálogo ao vivo · 🎓 material oficial Higgsfield ·
> 🟡 terceiro · ⚫ decisão do Samuel.

---

## 1. LIMITE DE CARACTERES — resolvido, e o teto não é onde a gente achava

### O que cada número era

| Número | Origem | Veredito |
|---|---|---|
| **1.494** | Leonardo | **Morto.** Outra ferramenta, outro tempo |
| **3.500** | "fonte de terceiro" no `planejamento-fluxo-higgsfield.md` §8 | **Sem lastro.** O Salomão varreu 10 fontes, incluindo 4 páginas oficiais do Higgsfield — o número **não aparece em nenhuma**. Não dá nem para chamar de "reza a lenda": ele não circula |
| **5.000** | 🎥 aula do Seedance 2.5 no YouTube | **Mal lido por nós.** A frase da aula é sobre o **modo de vídeo longo (180 s)**, argumentando que 5.000 caracteres é pouco para descrever 3 minutos. Nunca foi anunciado como teto do prompt normal |

### As três evidências que fecham

🟢 **O schema não declara limite.** O `param_schema` do Seedance 2.5 e do
Seedance 2.0 no catálogo ao vivo **não tem `maxLength`**. Em 72 KB de catálogo
não existe um único limite de texto, em nenhum modelo. Se houvesse validação
rígida de tamanho, é aqui que ela apareceria.

🎓 **A única menção oficial é qualitativa e não tem número.** Help Center do
Higgsfield (2026-08-01): *"prompts muito longos ou complexos e arquivos de
entrada pesados podem falhar ou demorar mais que o normal: simplifique e tente
de novo"* — listado ao lado de filtro NSFW e captcha. É **degradação
probabilística**, não validação que rejeita o input.

🎓 **E a prova empírica, que é a boa: os prompts oficiais deles são enormes.**
O guia oficial *Seedance 2.5: Complete Prompting Guide* (2026-08-13) publica
10 prompts testados em várias gerações. Medidos:

| | chars |
|---|---|
| menor | **1.020** |
| maior (fronteira limpa) | **7.084** |
| mediana | **~6.300** |
| **acima de 5.000** | **8 dos 10** |

> **Oito dos dez prompts oficiais do próprio Higgsfield passam de 5.000
> caracteres.** O teto que a gente respeitava é menor que a mediana do que eles
> publicam como boa prática.

### O que fica valendo

**Não existe teto conhecido.** O escopo está liberado, como o Samuel decidiu.
A faixa de trabalho observada no material oficial é **1.000 a 7.000**, com a
massa entre 5.000 e 7.000.

⚠️ A ressalva que continua de pé, e não é a mesma coisa: **prompt longo e vago
continua pior que curto e preciso.** O ganho é poder detalhar, não encher
linguiça. Os prompts oficiais são longos porque são **densos** — medidas,
segundos, negativas —, não porque são prolixos.

🎓 **E existe um caminho barato para medir a fronteira real se um dia importar:**
o Help Center diz que geração falhada **devolve o crédito automaticamente**
(exceção nomeada: Grok). Uma escada de prompts — 5.000 / 8.000 / 12.000 —
mede onde quebra gastando quase nada.

---

## 2. PROSA × JSON — a resposta tem nuance, e ela é aproveitável

### O que a fonte primária diz

🎓 **O guia oficial do Higgsfield manda PROSA, em bloco contínuo, com seções
rotuladas em caixa alta.** Não é JSON. A ordem oficial:

```
GLOBAL STYLE  → gênero, grade de cor, película/digital, proporção,
                obturador, e o que NÃO deve aparecer
SCENE         → uma linha de logline
CHARACTERS    → cada pessoa: rosto, cabelo, porte, figurino
LOCATION      → o espaço e os objetos, separado das pessoas
FIRST FRAME AND BLOCKING → posições exatas no instante zero, quem está onde,
                virado para onde
Shot 1..N     → tipo de plano + ação em uma ou duas frases,
                terminando em "Hard cut" onde houver corte
OPTICS and CAMERA → lente, altura de câmera, handheld/dolly/crane por plano
PHYSICS       → tecido, fumaça, cabelo, líquido
LIGHTING      → fonte motivada, direção, como cai no rosto
AUDIO         → ambiência, efeitos, e o que não deve existir
```

🎓 Frase deles sobre a forma: *"Most working Seedance 2.5 prompts follow the
same shape: one visual rule at the top, one sound rule at the bottom, and
everything in between broken into shots."*

🎓 E uma que confirma a nossa §2.1 palavra por palavra: **"Generation parameters
are not prompt text"** — resolução, duração e proporção se escolhem no gerador,
escrevê-las na prosa **não faz nada**.

🟡 A skill de prompt da comunidade (OSideMedia) diz o mesmo: *"prompts can be
written entirely in natural language"*, e a **única notação estruturada** que ela
recomenda dentro da prosa são colchetes de áudio:

| Notação | Para |
|---|---|
| `( )` | música |
| `< >` | efeito sonoro |
| `{ }` | diálogo |
| `【 】` | legenda |

**Isso é novo para nós e é barato de adotar.**

### O que dizem sobre JSON

🟡 A análise mais direta que existe (Morph Studio) conclui que **nenhum dos dois
é inerentemente melhor** — o modelo tokeniza os dois igual. E é honesta sobre
não ter medido nada: é argumento, não experimento.

| JSON ganha | JSON perde |
|---|---|
| define parâmetro explícito, reduz improviso | rigidez estrutural limita exploração criativa |
| bom em multi-cena e especificação de produto | curva de aprendizado |
| **reuso de template e geração em lote** | editar dá mais trabalho e convida erro de sintaxe |
| **pipeline programático** | — |

### A recomendação — e ela não é escolher um dos dois

> **Prosa é o formato de ENTREGA. JSON é o formato de TRABALHO.**

O Omega mantém o bloco como estrutura interna — campo a campo, validável,
reusável, comparável entre blocos, fácil de gerar em lote — e **serializa para
prosa com seções rotuladas na hora de montar o prompt**. Ganha as duas colunas
da tabela: template e lote do lado do agente, formato nativo do lado do modelo.

Isto **não é** adotar JSON no prompt. É separar o formato em que a gente pensa
do formato em que a gente entrega. A fonte primária é clara sobre o que o modelo
quer receber, e não há nenhuma fonte primária recomendando JSON para Seedance.

**Quando o JSON iria de fato para o prompt:** nunca, no que a gente faz hoje. Se
um dia aparecer um modelo cuja documentação **primária** peça JSON, aí muda — e
muda com fonte, não por gosto.

---

## 3. O que os prompts oficiais fazem e nós NÃO fazemos

Do prompt de drama, verbatim — vale mais que qualquer resumo:

- **Geografia de tela declarada por personagem:**
  *"THE WOMAN, always on the man's LEFT side"*. Não é enquadramento, é
  ancoragem — impede a troca de lado entre planos.
- **Trilha de eventos com segundos, para o ambiente:**
  *"SEA AND WIND EVENT TRACK: The sea is an event track, not a texture. Wave
  impacts arrive at irregular intervals, no two identical. 0.0s… 1.2s, WAVE 1
  strikes the forward boulders, bursting spray to 12 percent of frame height…
  2.4s, GUST 1…"* — o cenário recebe partitura própria, separada da ação.
- **Medida numérica em tudo:** *"the sun four degrees above the sea horizon"*,
  *"two meters above the waterline"*, *"five to eight meters out"*,
  *"12 percent of frame height"*.
- **Negativa colada no sujeito, não numa lista no fim:** *"No logos, no readable
  text on anything. A wholly original, invented face."*
- **Trava de elenco:** *"Only these two people exist in the entire video. No
  other figures, no boats, no birds close to camera, no animals on the rocks."*

E vale notar o que esse mesmo prompt faz com **duas pessoas conversando**, que é
exatamente a nossa questão: plano aberto segurando o casal e o mar juntos nos
segmentos 1 e 5, **lentes fechadas em cada rosto** nos segmentos 2 e 3, uma fala
por vez. Nada de dois corpos virados para a câmera.

---

## 4. Achados de catálogo que corrigem documento nosso

🟢 **`turbo` mata o 480p.** No Seedance 2.5, `turbo: true` restringe a resolução
a 720p/1080p. Quem ligar turbo perde a regra de resolução sem perceber e paga
2,6× — o mesmo modo de falhar que a §1 do `REGRAS-PRODUCAO-VIDEO.md` existe para
impedir. **Precisa virar aviso escrito.**

🟢 **As 50 referências agora têm a conta fechada:** 30 imagens + 10 vídeos
(até 30 s no total) + 10 áudios (até 30 s no total) = 50. Bate com o que a aula
dizia; agora está confirmado no schema.

🟢 **Seedance 2.0 aceita só 4 imagens de referência** (contra 30 do 2.5) e vai
até 15 s (contra 30 s). Rotear um bloco para o 2.0 por preço custa 26 âncoras.

🎓 **4K no Seedance 2.5 é upscale, não geração nativa.** O guia oficial diz
*"The model generates natively up to 1080p"*, e o catálogo oferece 4K assim
mesmo. Reforça a nossa arquitetura: gerar baixo e subir depois é o que a própria
ferramenta faz por dentro — só que a nossa RTX 3050 faz de graça.

---

## 5. ⚫ CONTRATO DE DIREÇÃO — decisão do Samuel, 2026-09-02

> **O Samuel dita a CENA. O agente dirige.**

- **O Samuel entrega:** o que acontece, quem está lá, onde, e a emoção/intenção
  do momento.
- **O agente decide:** enquadramento, ângulo, altura de câmera, lente,
  movimento, posicionamento dos corpos, cobertura, onde corta, ritmo.

**Por quê:** o Samuel não é diretor de cinema e **não deve precisar aprender
vocabulário técnico para fazer um vídeo**. Toda a biblioteca de câmera, lente e
movimento existe para o agente usar por conta própria, derivando da intenção
dramática — não para virar um formulário que o Samuel precisa preencher.

**Corolário operacional:** o prompt nunca volta para ele com pergunta de
técnica. "Qual lente você quer?" é pergunta errada. Se houver dúvida, ela é
sobre a **intenção** ("essa cena é de ameaça ou de tristeza?"), nunca sobre o
meio de conseguir a intenção. Quando a decisão técnica for arriscada ou cara,
o agente **decide e declara** o que decidiu e por quê — não devolve a decisão.
