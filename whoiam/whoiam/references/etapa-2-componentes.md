# Etapa 2 — Componentes (model sheets que viram Elements)

> Componente é tudo o que precisa sair **igual em vários blocos**: a criatura, os personagens
> recorrentes, os ambientes recorrentes e os objetos de continuidade. Ele é gerado **uma vez**, no
> GPT, aprovado pelo Samuel e cadastrado como **Element** no Higgsfield. Dali em diante o prompt de
> cena chama o Element pelo label (`@per_johansen`), sem redescrever a aparência.

---

## 1. Ler o roteiro e decidir o que vira componente

Passar pelas 20 partes e montar a **tabela de presença**: quem, onde e qual objeto aparece em cada
parte. Depois decidir:

| Vira componente | Não vira componente (vai como referência do bloco, Etapa 3) |
|---|---|
| criatura: **sempre** | figurante sem rosto em destaque |
| humano que aparece em **2+ blocos**, ou em close em qualquer bloco | ambiente usado em um bloco só |
| ambiente onde se passam **2+ blocos** | objeto que aparece uma vez |
| objeto que **passa de mão**, reaparece, ou precisa ser idêntico (o chapéu, o livro, o ídolo) | variação de pose, ângulo ou momento |
| **estado recorrente**: ferido, molhado, transformado, em **2+ blocos** seguidos | estado que dura um bloco só |

Estado recorrente vira componente próprio com o estado no slug (`per_johansen-ferido`), gerado a
partir do componente base anexado. Estado de um bloco só é referência daquele bloco.

**Ambiente recorrente sai sempre em duas imagens:** frente e reverso (`amb_alert-conves` +
`amb_alert-conves_reverso`). Sem o reverso, todo corte para contracampo faz o modelo inventar o que
está atrás do personagem, e o fundo "pula" entre cortes.

---

## 2. Nomes, pastas e o `registro.json`

- Pasta: `C:\Ai-Project\Criaturas\<Nome>\componentes\`
- Arquivo: `<prefixo>_<slug>.png` — prefixos `cri_` criatura · `per_` personagem · `amb_` ambiente
  · `obj_` objeto. Slug em minúsculas, sem acento, hífen entre palavras, até ~24 caracteres.
- **Label do Element = nome do arquivo sem `.png`.** Sem exceção, sem apelido: `obj_chapeu-collins.png`
  é `@obj_chapeu-collins`. Assim o Claude que escreve o prompt e a extensão que cadastra nunca
  divergem.

`registro.json` (a extensão atualiza ao cadastrar; o Claude lê antes de escrever qualquer prompt):

```json
{
  "criatura": "Cthulhu",
  "componentes": {
    "per_johansen": {
      "tipo": "personagem",
      "estilo": "naturalista",
      "arquivo": "per_johansen.png",
      "element": "@per_johansen",
      "categoria_higgsfield": "Character",
      "blocos": [1, 6, 7, 8],
      "status": "aprovado",
      "aprovado_em": "2026-10-06",
      "gerado_em": "GPT",
      "observacao": ""
    }
  }
}
```

`status` só pode ser `a-gerar` · `gerado` (esperando o Samuel) · `aprovado` · `cadastrado` (Element
criado e conferido) · `reprovado`. O prompt de cena só cita Element com status `cadastrado`.

---

## 3. O formato de `componentes.md`

```markdown
# <Criatura> — Componentes

> 🟢 **PASSO 1 da etapa de componentes** (ordem no `EXECUTAR.md` de `componentes\`: gerar no GPT →
> aprovação do Samuel → cadastrar Elements). PARAR depois de gerar.
>
> ⚠️ **PROMPT DE IMAGEM DE REFERÊNCIA — gerar no ChatGPT, com a geração de imagem nativa do GPT.**
> **NÃO usar o MCP do Higgsfield nem o site do Higgsfield para gerar estas imagens.**

> Roteiro lido em <data>. <N> componentes. Estilo: cri_ ultra-realista; per_/amb_/obj_ naturalista.

| Label | Tipo | Blocos | Por que é componente |
|---|---|---|---|
| @cri_cthulhu | criatura | 18–20 | sempre |
| @per_johansen | personagem | 1, 6–14 | protagonista, close em vários blocos |
| @amb_alert-conves | ambiente | 6–8 | três blocos no mesmo convés |
| @amb_alert-conves_reverso | ambiente | 6–8 | contracampo |
| @obj_chapeu-collins | objeto | 7, 8 | passa de mão |

---

## @per_johansen
DESTINO: ChatGPT — geração de imagem nativa do GPT (NÃO usar o MCP do Higgsfield)
PRÉVIA (PT-BR, não colar): segundo-piloto do Alert, o protagonista humano.
ANEXAR NO GPT: nada (primeira geração)   |   ou: per_johansen.png (variação de estado)
SALVAR COMO: C:\Ai-Project\Criaturas\Cthulhu\componentes\per_johansen.png
ELEMENT: label `per_johansen` · categoria Character

PROMPT (colar inteiro no GPT):
```
<prompt em inglês, do template da §4, terminando com as âncoras corretas>
```
```

**O aviso de destino é obrigatório:** no topo do arquivo e na primeira linha de cada item, para a
extensão nunca confundir prompt de imagem com prompt de vídeo.

Ordem dentro do arquivo: **criatura → personagens → ambientes → objetos**. Componente que depende
de outro (o estado `-ferido`, o objeto que é do personagem) vem depois dele e diz o que anexar.

---

## 4. Templates de prompt por tipo

Regras que valem para os quatro:
- **A aparência se descreve AQUI, inteira, e em nenhum outro lugar.** O prompt de cena chama o
  Element e não redescreve, porque redescrever gera deriva.
- **Fundo neutro e liso, sem rótulos, sem tira de paleta, sem tipografia, sem grade.** A folha
  elaborada antiga (turnaround, expressões, rótulos) morreu: tudo isso vazava para dentro da cena.
- **Nunca escrever idade** em número nem em palavra. Descrever por papel, porte, roupa e marcas.
- **Adorno pequeno sai da folha:** brinco, anel, fivela ou chapéu miúdo vira ruído no vídeo e pode
  arrastar a identidade. Ou o detalhe é grande e definidor, ou vira um `obj_` próprio.
- 16:9, a maior resolução que o GPT der.

### `cri_` — criatura (âncora A)

```
Creature reference sheet of one single original creature, the same creature in every view.
Left: full body, standing in its natural posture, the whole silhouette readable against the
background. Right: a large, clear close-up of the head and face. Plain neutral dark-grey seamless
background. No section labels, no palette strip, no typography, no other creatures.
CREATURE SPECIFICS: <descrição FECHADA — anatomia, proporções e escala relativa a um humano
(em números: "a human reaches its knee"), pele/escama/textura com imperfeições (cicatrizes,
manchas, lascas), olhos, boca, membros, como o peso se distribui no corpo>.
A physical creature photographed for real: high-budget practical effects and animatronics,
skin with real imperfection, wet and weighted, never fantasy art.
<ÂNCORA A>
```

### `per_` — personagem humano (âncoras B + D)

```
Character reference sheet of one single person, the same person in both views. Left: full body,
standing, relaxed natural posture, the whole costume visible from head to boots. Right: a large,
clear close-up of the face, eye level. Plain neutral grey seamless background. Single subject
only, no other people, no duplicate figures. No section labels, no palette strip, no typography.
CHARACTER SPECIFICS: <papel, porte, altura relativa; rosto: formato, estrutura adulta definida,
cabelo, barba; pelo menos três imperfeições nomeadas; figurino com material, cor e desgaste,
peça por peça, da cabeça aos pés; marcas de época e ofício>.
<ÂNCORA D>
<ÂNCORA B>
```

Se o rosto não estiver saindo com cara de gente de verdade, gerar **antes** um retrato simples
(prompt curto: uma frase de identidade + três imperfeições + "not fully sharp" + âncoras B e D) e
anexar esse retrato na geração da folha.

### `amb_` — ambiente (âncoras B + C), em duas imagens

Frente:
```
Wide establishing photograph of <lugar>, empty of people: a clean plate of the location as it
stands. <identidade do lugar em uma frase>. LOCATION SPECIFICS: <material predominante, época e
desgaste, escala em números (altura do mastro, largura do convés), objetos fixos e onde ficam,
a luz que mora ali (não a luz de uma cena), o clima padrão>. Camera at standing eye height,
1.7 m, looking <direção: "from the stern toward the bow">.
<ÂNCORA C>
<ÂNCORA B>
```
Reverso: o mesmo texto, trocando a última frase da câmera para a direção oposta
(`"from the bow toward the stern, the reverse of the first view"`), **anexando a imagem da frente**
e acrescentando: `Same location, same materials and light as the attached image, seen from the
opposite side.`

Ambiente que muda de estado ao longo do roteiro (intacto → em chamas → destruído): o componente é
o estado **base**; os outros estados são referência de bloco, gerados a partir dele.

### `obj_` — objeto de continuidade (âncora B)

```
Product-style reference photograph of one single object: <objeto>, three-quarter view, resting on
a plain neutral surface against a plain grey background, the whole object in frame and in sharp
focus. OBJECT SPECIFICS: <material, cor, tamanho em centímetros, desgaste, marcas, o detalhe que
o torna reconhecível>. No hands, no people, no other objects.
<ÂNCORA B>
```
Objeto que pertence a um personagem (o chapéu do capitão): anexar o `per_` dele e escrever
`identical to the one worn in the attached character sheet`.

---

## 5. Portão

A extensão gera e salva; **o Samuel aprova cada imagem** antes do cadastro. Iterar no GPT não custa
crédito, então folha mediana não se aceita: refaz. Só depois de aprovada a extensão cria o Element
e marca `cadastrado` no `registro.json`.

Quando um Element já existe na conta do Samuel com outro label (projeto anterior ao padrão), ele
**não** é renomeado no meio de uma produção: o `registro.json` registra o label real no campo
`element` e o prompt usa esse label. Renomear só entre produções.
