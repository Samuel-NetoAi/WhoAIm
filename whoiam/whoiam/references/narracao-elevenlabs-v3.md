# Narração — ElevenLabs v3 (audio tags)

> **Nomes usados aqui (todos da etapa 6, pós-produção):** Documento 1/1a = legenda-base (o texto
> da narração encaixado na montagem travada) · Documento 4 = narração marcada para o ElevenLabs v3 ·
> Documento 6 = cortes para Shorts · Documento 7 = mapa de trilha · Documento 8 = mapa de edição.
> Nenhum deles é gerado antes de os 20 takes estarem aprovados e montados no Studio.

Referência do Documento 4. Substitui o formato Suno para NARRAÇÃO (decisão de jul/2026).
O Suno continua APENAS para trilha musical (Documento 7) — não gerar narração no Suno.

## Como o v3 funciona (o que importa para nós)

- **Audio tags** são direções de performance entre colchetes, inseridas inline no texto:
  `[whispers]`, `[awe]`, `[pause]`, `[dramatic tone]`. O modelo as interpreta como direção,
  não como texto a ser lido.
- Uma tag afeta o texto seguinte até aparecer outra tag. Tags podem ser combinadas:
  `[hushed][ominous] E então... a porta se abriu.`
- **Não existe SSML `<break>` no v3.** Pausa e ritmo se controlam com: reticências (...),
  a tag `[pause]`, e a própria estrutura das frases. Ênfase = palavra em MAIÚSCULO.
- **Compatibilidade com o Documento 1:** as convenções do nosso roteiro (frases curtas,
  reticências para pausa dramática, MAIÚSCULO para ênfase) JÁ SÃO a sintaxe nativa do v3.
  O trabalho do Documento 4 é só a passada de marcação: inserir tags nos beats emocionais.

## Configurações (na UI do ElevenLabs)

- **Modelo:** Eleven v3 (alpha). Idioma: o v3 lê o texto em PT-BR diretamente.
- **Stability — o ajuste mais importante:**
  - `Creative` → máxima expressividade e resposta às tags, mas propenso a alucinação.
  - `Natural` → equilíbrio; ponto de partida padrão para o canal.
  - `Robust` → muito estável, porém responde MAL às tags. Evitar quando o trecho tem direção emocional.
- **Voz:** parâmetro mais decisivo do v3. A tag precisa ser compatível com o caráter da voz —
  voz meditativa não grita com `[shouting]`; voz agitada não sussurra bem. Preferir vozes da
  Voice Library ou Instant Voice Clones; Professional Voice Clones ainda não estão otimizados
  para o v3 (alpha).
- **Comprimento:** prompts muito curtos saem inconsistentes. Gerar por SEQUÊNCIA do vídeo
  (blocos de texto > 250 caracteres), nunca linha a linha.
- **Não determinismo:** o v3 varia entre gerações. Regra do canal: **gerar 2–3 takes por
  sequência e escolher o melhor.** Nunca esperar acerto de primeira; pequenos ajustes de
  posição de tag mudam muito o resultado.

## Vocabulário de tags do canal (narração documental sombria)

Usar POUCAS tags — 1 a cada 2–4 linhas, nos beats que realmente mudam. Excesso de tag vira ruído
e aumenta alucinação. Tags fora deste vocabulário só se o usuário pedir.

| Intenção | Tags |
|---|---|
| Abertura / mistério | `[hushed]` `[ominous]` `[mysterious tone]` |
| Revelação / assombro | `[awe]` `[dramatic tone]` |
| Tensão crescente | `[intense]` `[tense]` |
| Segredo / proximidade | `[whispers]` |
| Peso / tragédia | `[somber]` `[sorrowful]` |
| Ritmo | `[pause]` `[slow]` `[drawn out]` (usar com parcimônia; reticências resolvem a maioria) |
| Fechamento perturbador | `[quietly]` `[cold tone]` |

**PROIBIDO no registro do canal:** `[laughs]`, `[giggles]`, `[excited]`, `[cheerful]`,
`[playfully]` e afins — quebram o tom documental sombrio. Também evitar tags de efeito sonoro
(`[gunshot]`, `[explosion]`): som é trabalho da trilha e do Seedance, não da voz.

## Perfil de voz por tipo de criatura (procurar na Voice Library)

A tabela antiga (Suno) traduzida para o v3: agora o que se escolhe é a VOZ + a paleta de tags
que ela aceita. Testar a voz com um trecho curto antes de gerar o vídeo inteiro; registrar
abaixo as vozes aprovadas (nome exato na biblioteca) conforme forem testadas.

| Tipo | Perfil de voz a procurar | Paleta de tags dominante |
|---|---|---|
| Cósmica/épica (Cthulhu, Leviatã) | Masculina grave, autoritária, registro de documentário BBC, ritmo lento | `[ominous]` `[awe]` `[dramatic tone]` |
| Trágico (Medusa, Sereia) | Feminina suave, melancólica, ritmo emocional lento | `[somber]` `[sorrowful]` `[whispers]` |
| Nórdica (Jormungandr, Nidhogg) | Masculina áspera e profunda, tom de saga | `[intense]` `[dramatic tone]` |
| Deus olímpico (Zeus) | Masculina imponente, clássica, ritmo medido | `[dramatic tone]` `[awe]` |
| Folclore BR (Boi Tatá) | Masculina brasileira grave, tom místico de contador | `[mysterious tone]` `[hushed]` |

Vozes aprovadas em teste (atualizar aqui quando o usuário validar):
- (nenhuma registrada ainda)

## Orçamento de duração por bloco (~15s) — com dívida de pausa

Contar só palavras é pseudo-precisão: reticências e [pause] consomem tempo. Orçamento por bloco:

```
custo = palavras + 1,5 × (nº de reticências) + 2 × (nº de [pause])
alvo  : custo ≈ 33 por bloco de 15s   (constante inicial ≈ 2,2 palavras/segundo)
tolerância: ±4 de custo (≈ ±2 segundos)
```

**CALIBRAÇÃO OBRIGATÓRIA no primeiro vídeo com cada voz:** gerar a sequência 1, medir a duração
real do áudio, recalcular a constante (custo total ÷ segundos medidos) e registrar no Registro
empírico abaixo. A partir daí, usar a constante calibrada, não a inicial. Recalibrar se trocar a voz.

A duração-alvo de cada sequência vem do vídeo montado (pos-producao.md). O orçamento existe para
a narração CABER — a sincronia fina continua desnecessária pela narração dissociada (única âncora
obrigatória: nome da criatura na 1ª vez ↔ imagem forte).

## ⚫ A NARRAÇÃO PARA QUANDO HÁ DIÁLOGO NA CENA (decisão do Samuel, 2026-09-02)

> **O canal passa a ter diálogo em algumas cenas. Narração e diálogo NUNCA se sobrepõem.**

Quando um bloco é de diálogo, a narração **termina antes dele e recomeça depois**. O Samuel avisa
quais blocos são dialogados. Motivo, nas palavras dele: *"para mais estanqueidade"* — as duas vozes
disputam a mesma atenção, e sobrepor é o que faz o vídeo soar como podcast com imagem.

**O que isso exige desta etapa:**

1. **O roteiro de narração é escrito em torno dos buracos**, não por cima deles. Cada bloco
   dialogado é um vão: a narração fecha uma ideia antes, e **reabre** depois — não continua a frase
   do outro lado.
2. **Não usar o vão como suspense barato.** A narração que para no meio de uma oração e volta
   depois do diálogo soa como falha técnica. Fechar antes, retomar com entrada nova.
3. **A retomada precisa de gancho curto**, porque o espectador acabou de ouvir outras vozes: uma
   frase que reancora quem está falando e onde estamos.
4. **Orçamento de duração:** o vão dialogado **não** entra na conta de segundos de narração. Ao
   somar a duração da narração do vídeo, descontar os blocos de diálogo.

**Fronteira:** a fala **dentro da cena** é gerada pelo modelo de vídeo (Seedance), não aqui. Esta
skill só cuida da voz de narração. Hoje o canal não tem fala dentro da cena: o vídeo sai só com
o som do ambiente.

---

## Mapa de narradores (1 voz por padrão; multi-voz é exceção declarada)

Padrão do canal: UM narrador por vídeo. Quando o usuário pedir dinamismo com mais de um narrador
(ex.: personagem em 1ª pessoa que abre o vídeo → narrador mítico geral após um gatilho), gerar um
**MAPA DE NARRADORES** no topo do Documento 4:

| Narrador | Voz (perfil/nome) | Registro | Sequências | Passagem de bastão |
|---|---|---|---|---|
| ex.: O neto (1ª pessoa) | masculina jovem, tensa, intimista | MODO PERSONAGEM | 1–3 | ao abrir o diário (seq. 3 → 4) |
| ex.: Narrador mítico | perfil cósmico da tabela | dissociada padrão | 4–12 | — |

Regras do multi-voz:
- Gerar cada narrador em GERAÇÕES SEPARADAS no ElevenLabs (uma voz por geração) — não misturar
  vozes num prompt só; a mixagem une os arquivos no CapCut.
- A passagem de bastão precisa de um marco AUDÍVEL e VISÍVEL (objeto, gesto, corte) definido no mapa.
- **MODO PERSONAGEM — exceção sancionada à narração dissociada:** só existe quando o usuário pede.
  A 1ª pessoa narra ESTADO INTERNO e DESCOBERTA da lore ("eu não deveria ter aberto aquele diário"),
  nunca descrição shot-a-shot da própria ação na tela ("eu caminho até a mesa" é PROIBIDO) — assim
  a fala continua independente do timing dos cortes, que é o benefício que a dissociação protege.
  Fora das sequências designadas no mapa, a regra dissociada volta a valer integralmente.
- O usuário descreve a ideia da narração (quem narra, quando vira); a skill segue o modelo dele
  e preenche o mapa — não inventa dispositivo narrativo que ele não pediu.

## Insumo: cenas travadas do vídeo montado

O Documento 4 só nasce depois do vídeo montado. Seu insumo é o arquivo
`cenas-travadas-<criatura>.md` (gerado no fluxo de pós-produção): a lista de sequências finais
com duração real de cada uma e o que aparece na tela. Se o arquivo não existir, criar na hora com
o usuário (ele descreve o vídeo como ficou) e salvar em output/ — é ele que fixa as durações-alvo
dos blocos e os pontos de passagem de bastão. Skill não guarda estado entre sessões; o arquivo guarda.

## Passada de marcação — processo

1. **Diagnóstico (3 linhas):** tipo de história, tom dominante, arco emocional por sequência.
2. **Verificações antes de marcar:** o texto já tem tags? (não duplicar); o conteúdo bate com as
   cenas travadas? (avisar divergência, não "consertar" sozinho).
3. **Preservação absoluta:** marcar é adicionar tags e ajustar pontuação para a síntese. NUNCA
   reescrever, expandir ou "melhorar" o texto — texto curto não se expande por conta própria
   (expansão inventa lore); se estiver curto para a duração-alvo, DIZER ao usuário e deixar ele decidir.
4. Aplicar o vocabulário de tags do canal + orçamento de duração por bloco. Regras de inserção:
   tag marca MUDANÇA de estado emocional, não repete o vigente; nunca no meio de frase curta —
   no início da frase ou do beat; manter reticências e MAIÚSCULAS do Documento 1 (trabalham junto
   com as tags); se a sequência sair errada nos 2–3 takes, ajustar a POSIÇÃO da tag antes de trocá-la.
5. Entregar 1 versão marcada por sequência (não 3 variações tonais — o canal tem UM registro;
   a variação certa é gerar 2–3 TAKES do mesmo texto no ElevenLabs e escolher).

## FORMATO DE ENTREGA — bloco de colagem SEPARADO das anotações

⚠️ O v3 interpreta QUALQUER `[colchete]` como direção de performance. Portanto, dentro do bloco
pronto-para-colar: SÓ texto de narração + tags válidas do vocabulário. É DEFEITO GRAVE incluir:
- marcação de cena tipo `[A sacerdotisa no templo]` → o modelo tenta "performar" isso;
- indicação de tempo tipo `- 15 segundos` → o modelo LÊ EM VOZ ALTA ("quinze segundos");
- nomes de bloco, timestamps, notas de direção.

Anotações de produção ficam FORA do bloco de colagem:

```
─── SEQUÊNCIA 2 · cena: a sacerdotisa no templo · alvo 15s · custo 31/33 · voz: [nome] · stability: Natural ───
COLAR NO ELEVENLABS:
[solemn] Muito antes do monstro... existiu uma mulher.
Medusa.
Sacerdotisa do templo de Atena.
Devota... Serena... Humana.
[gentle] Ela servia aos deuses com fé.
─── fim da sequência 2 ───
```

## Registro empírico (mesmo padrão do `receituario.md`)

Quando o usuário relatar comportamento observado do v3 (tag que a voz X ignora, alucinação
recorrente, take que só funciona com Creative...), registrar AQUI, com data. Isto é um
receituário vivo — teste real vence teoria.

- (nenhum registro ainda)
