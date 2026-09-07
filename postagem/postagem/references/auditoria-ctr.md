# Auditoria pós-publicação

O Samuel cola os números do YouTube Studio e você diz o que mexer, em que ordem e quando. Este
arquivo é a árvore de decisão que o curso ensina.

## Antes de diagnosticar qualquer coisa

**Pergunte quanto tempo o vídeo tem no ar.** Quase todo diagnóstico do curso é condicionado ao
tempo: a janela para trocar a thumb é **1–2 semanas** (aula 1, [01:20]–[01:50]), e depois de uma
troca o curso manda dar **alguns dias** para o efeito aparecer (aula 1, [01:38]–[02:33]). Um vídeo
com dois dias no ar não tem diagnóstico — tem ansiedade.

**Confira o que falta.** CTR sem impressões não significa nada: 3% sobre 500 impressões é ruído;
3% sobre 500 mil é um problema caro. O próprio curso mostra que uma **CTR menor em % pode valer
mais views** que uma maior, se o volume de impressões for muito maior (aula 2-studios, [25:12]).
Se faltar número, peça — não estime.

**Não invente analytics.** Se ele não colou, você não sabe. Isso vale também para comparar com
"a média do nicho": você não tem essa média.

---

## Os patamares que o curso dá

| Métrica | Referência | Fonte |
|---|---|---|
| CTR boa | **~5%** | aula 1, [03:56]; aula 05, [05:52] (média) |
| CTR alvo | 5% a 9% | aula 3, [09:17]–[10:37] |
| CTR 6–9%+ | possível, mas difícil | aula 1, [03:56] (citado de memória, sem print) |
| Gatilho de troca | **abaixo de 5%** | aula 05, [04:53]–[05:07] (print: CTR 2,6% / 521,5 mil impressões) |
| Retenção mediana | 40%–50% | aula 3-tecnicas |
| Retenção alta | 50%–70% | aula 3-tecnicas |
| Perda no 1º minuto | 20–30% é normal, até 50% acontece | aula 3-tecnicas |
| Vídeo curto (5–7 min) | precisa de 50–70% de retenção **ou** CTR acima de 10% | aula 05, [09:11] (média) |

---

## A árvore

### 1. CTR abaixo de 5%

O curso nomeia **três causas possíveis, nessa ordem de investigação: tema, thumbnail, título**
(aula 2-studios, [19:18]–[19:56], com print de um vídeo a 2,9%).

Ordem de intervenção, que o curso dá explicitamente:

1. **Troque a thumbnail primeiro.** Só troque o título depois, se a thumb não resolver (aula 1,
   [01:20]–[01:50]). Manualmente, não pelo A/B nativo (aula 05, [03:54]; decisão do canal).
2. Deixe a thumb mais chamativa, com mais cores (aula 2-studios, [14:01]–[14:28]).
3. Se não resolver, título mais chamativo com palavras fortes (aula 2-studios, [14:28]–[14:58] —
   confiança média, o professor não detalha quais).
4. Se nem isso resolver, o problema pode ser o **tema** — e aí a resposta não é mexer neste vídeo,
   é escolher melhor o próximo. O curso sugere ainda repostar o vídeo aproveitando um hype futuro
   do tema (aula 2-studios, [20:44] — média).

Trocar thumb e título de um vídeo já publicado vem **antes** de reeditar o vídeo (aula 2-studios,
[20:21]–[21:52] — média, o "90% das vezes" é estimativa falada).

### 2. CTR ok, mas poucas views

Olhe as **impressões**, na aba Alcance (aula 2-studios, [17:57]–[19:05]). CTR boa com poucas
impressões significa que o YouTube não está distribuindo — e o que faz ele distribuir é o conjunto
**retenção + minutos assistidos + taxa de clique** (aula 3-tecnicas). Se retenção e minutos estão
bem e as impressões não sobem, o problema tende a ser de tema/nicho, não de embalagem.

### 3. Retenção baixa

Fora do escopo desta skill — retenção é edição e roteiro, território da `whoiam`. O que cabe aqui:
sinalizar, com o número, que o próximo vídeo precisa de atenção no roteiro e principalmente na
introdução (aula 3-tecnicas), e não recomendar troca de thumb como se fosse resolver retenção.

Uma exceção que vale citar porque é contraintuitiva: uma thumb muito chamativa (mas coerente com o
vídeo) pode multiplicar impressões e views **mesmo com retenção mediana** (aula 2-studios,
[23:57]–[25:12] — confiança média; a fala do professor não bate exatamente com o print).

### 4. Duração curta demais

Se o vídeo tem menos de 8 min, registre no diagnóstico: ele está sem anúncio intermediário
(aula 13, [11:37]) e, sendo de 5–7 min, precisa de patamares mais altos que o normal para viralizar
(aula 05, [09:11]). Isso não se conserta depois de publicado — é informação para o próximo lote.

### 5. O canal inteiro travado

O curso lista, para destravar (aula 05, [03:26]–[05:07]): títulos melhores, tags de vídeos que
estão bombando no nicho, variações de descrição com e sem tags, aumentar a frequência em 1–2
vídeos por semana, trocar thumb e título abaixo de 5% de CTR. Quase todas são de confiança média —
apresente como cardápio, não como plano.

**A que você não deve recomendar sozinho:** aumentar a frequência. Ela só sobe se a gaveta
sustentar, senão você troca um problema por uma quebra de padrão, que o curso trata como o erro
mais caro de todos (três aulas).

---

## O teste de tags

Enquanto o lote dividido estiver rodando, toda auditoria deve atualizar a tabela de tags do
`canal-estado.md` e, quando houver 4+ vídeos de cada lado, apresentar a comparação: CTR média,
impressões médias, e a ressalva honesta de que a amostra é pequena e os vídeos não são idênticos.

O curso pediu o teste (repetida em 2 aulas, alta) mas não disse como ler o resultado. Se a
diferença for pequena, diga que foi pequena. Fabricar uma conclusão de um teste de 8 vídeos seria
exatamente o tipo de coisa que esta skill existe para não fazer.

---

## Formato do diagnóstico

```markdown
# Auditoria — <Criatura>, publicado em <data> (<n> dias no ar)

## Números
<tabela do que ele colou, e o que faltou>

## Leitura
<uma frase por métrica; o que está fora do patamar do curso e por quanto>

## Ação recomendada, em ordem
1. <o quê> — <regra + citação> — <quando avaliar de novo>
2. ...

## O que NÃO fazer agora
<e por quê — geralmente: cedo demais, ou mexe numa variável em teste>

## Atualização do estado
<as linhas que vão para o canal-estado.md>
```
