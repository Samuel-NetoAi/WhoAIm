# Direção Cinematográfica — conversão de descrição em cena (Documentos 2 e 3)

Este arquivo destila o processo diretorial que converte a descrição do usuário em cena
cinematográfica. Escrito pelo Claude Fable 5 (jul/2026) para ser executado por qualquer modelo.
A regra que carrega todo o resto: **NENHUMA escolha de câmera sem justificativa dramática.**
Shot sem porquê é default; default é o que separa prompt genérico de direção.

> **ONDE A DIREÇÃO É EXECUTADA MUDOU (ago/2026).** O algoritmo abaixo continua inteiro — ele é o que
> decide *o que* filmar e *por quê*. O que mudou é para onde a decisão vai: no Cinema Studio do
> Higgsfield, gênero, era, tempo de montagem, tipo de câmera, lente, abertura, movimento de câmera e
> emoção do personagem são **controles da interface**, não frases do prompt. Escrever a mesma coisa nos
> dois lugares faz controle e texto disputarem. Mapeamento: passo 1 (intenção dramática) → Gênero;
> ritmo do bloco → Tempo/Montagem; tabela lente-como-psicologia → Lente + Abertura; fraseado de
> movimento → preset de movimento; padrão de montagem (passo 5a) → escolhe Gênero + Tempo e segue
> governando a ORDEM dos shots no storyboard. Tabela completa em `higgsfield-cinema-studio.md`, seção 4.
> **A justificativa dramática por shot continua obrigatória** — ela agora é escrita na ficha de
> controles, não no prompt. Controle escolhido sem porquê é o mesmo default de antes, com outra roupa.

## CONTRATO COM O USUÁRIO

- Os elementos que o usuário descreveu são INVIOLÁVEIS (quem aparece, o que acontece, onde).
- A direção ADICIONA em cima: câmera, encenação, luz, ritmo, lente. Nunca substitui.
- Se a direção pedir para alterar um elemento descrito ("funcionaria melhor se a camponesa
  parasse ANTES do beco"), PERGUNTAR ao usuário — sugestão, não decisão.

## O ALGORITMO — executar nesta ordem para cada bloco

**1. Intenção dramática (uma frase).** Antes de qualquer câmera: qual é o trabalho emocional
deste bloco? (pavor crescente / assombro / tragédia / ameaça latente / revelação / luto).
Um bloco = UMA intenção dominante. Tudo abaixo deriva dela. Escrever a frase na ficha do bloco.

**2. Dono do olhar.** De quem a câmera simpatiza neste bloco — a vítima, a criatura, ou uma
testemunha invisível (registro documental)? Isso decide os ângulos inteiros:
- olhar da vítima → criatura em contra-plongée (low angle), shots da vítima em ângulo neutro/alto,
  POV parciais (o que ela consegue ver);
- olhar da criatura → humanos pequenos no quadro, high angle, distâncias que encurtam;
- testemunha invisível (padrão do canal p/ blocos de lore) → câmera estática ou movimentos lentos
  e deliberados, observação fria, sem handheld.
O dono do olhar pode TROCAR entre blocos (é uma ferramenta de arco), nunca dentro de um shot.

**3. Anatomia do movimento.** Toda ação física tem três tempos, e os três aparecem nos painéis:
`ANTECIPAÇÃO (o corpo se prepara: recuo, tensão, respiração) → AÇÃO (o gesto) → CONSEQUÊNCIA
(follow-through + reação do ambiente)`. O erro amador é desenhar só o gesto. A antecipação é o
que cria tensão; a reação do ambiente (poeira que sobe, água que se fecha, pássaros que fogem,
tecido que assenta) é o que vende peso e escala. Criatura colossal move-se DEVAGAR — velocidade
é inversamente proporcional à massa; quebrar isso mata a fisicalidade.

**4. Três planos de profundidade — declarar os três em CADA painel/shot:**
`PRIMEIRO PLANO (o que está entre a câmera e o sujeito) / SUJEITO / FUNDO`.
Quadro sem primeiro plano é quadro chapado. Primeiro plano oclusivo (galho, ombro, batente,
névoa) = espreita/voyeurismo — ferramenta principal para ameaça latente. Fundo comandado por
tamanho/foco/luz (regra existente).

**5. Escolher os shots pela GRAMÁTICA (abaixo), um porquê por shot, escrito na ficha.**

> 📖 **Ponto de partida pronto: `bibliotecas-camera-emocao.md` §4.** Tabela mestra que vai do
> **tipo de cena do canal** (abertura · ameaça latente · presságio · aproximação · revelação
> parcial · revelação total · reação · fuga · perseguição · confronto · maldição · consequência ·
> luto) direto para **movimento nomeado · altura em metros · tamanho de plano com orçamento de
> detalhe · verbete de emoção**. Ela é o ponto de partida de cada linha, **não** substitui este
> algoritmo: a justificativa dramática por shot continua obrigatória, e sair da tabela é permitido
> — sair dela **sem porquê escrito** é o default de sempre com roupa nova.

**5a. ESCOLHER O PADRÃO DE MONTAGEM (biblioteca em vendor-visual-skills/patterns-and-genres.md):**
Antes de montar a cobertura, identificar o TIPO da cena e partir do padrão profissional
correspondente — Escalation (revelação/tensão crescente: wide → medium → close → macro → reação →
impacto; ex.: a Chama), Anxiety (pressão psicológica), Discovery (descoberta/exploração),
Catastrophe (desastre), e os módulos de gênero (drama psicológico = quadros travados e espaço
negativo; ação = clareza espacial acima de tudo, wides entre closes). O padrão é ponto de
partida a ADAPTAR à intenção do bloco, nunca fôrma; declarar na ficha qual padrão foi usado e o
que foi adaptado. Para aprofundar blocking/staging/ritmo: vendor-visual-skills/dramaturgy.md.

**5b. PLANO DE COBERTURA — o piso de riqueza visual (correção jul/2026, caso "A Chama"):**
Monotonia também é default. Todo bloco DEVE conter, salvo pedido explícito de plano-sequência:
- pelo menos 3 TAMANHOS de plano distintos (da escada wide → medium → close → extreme close-up);
- pelo menos 1 INSERT de detalhe (extreme close-up do elemento crítico/em transformação — a chama
  mudando de cor por dentro, a mão que hesita, o olho que abre). O insert é o shot que o usuário
  sente falta quando não existe.
O plano de cobertura tem DOIS eixos: tamanhos de plano E POPULAÇÃO (quem aparece em cada painel —
two-shot/single/insert; com 2+ personagens importantes, ≥1 single/close de reação por personagem;
ver "População do quadro" no model-sheet-storyboard.md). Declarar também o REGIME do bloco:
plano-sequência ou setups isolados.
Escrever o plano de cobertura na ficha ANTES dos painéis: "Shot A wide (2 frames) / Shot B ECU
insert no núcleo da chama (2) / Shot C medium contra-plongée forma final (2)".
IMPORTANTE — a exceção de transformação rege o RITMO (lento, sem cortes rápidos, frames que
seguram), NÃO o tamanho de plano: transformação lenta corta para o insert e volta sem quebrar o
peso. Um eixo único do início ao fim do bloco só existe se o usuário pedir plano-sequência.

**5c. LEI DOS DETALHES (adaptada de smixs/visual-skills):** cada shot possui TRÊS detalhes
concretos, escritos no painel (Doc 2) e no [ACTION]/[AUDIO] (Doc 3):
1. pressão ambiental (a luz fria que vaza, o vento arrastando poeira, o calor distorcendo o ar);
2. micro-ação física (brasas estalando, mandíbula travando, tecido assentando);
3. um motivo sonoro ou visual (o som que assina a cena, o objeto que retorna).
Shot sem os três é shot genérico. E BANIR adjetivos que não renderizam: "cinematic", "epic",
"stunning", "masterpiece", "breathtaking" — no lugar deles, o ofício concreto (lente, luz, ação).
("cinema camera" na âncora de realismo é termo técnico e permanece.)

### 🎓 NÚMERO E COMPARAÇÃO no lugar do adjetivo (set/2026)

**Por que estávamos meio errados:** a regra acima bania o adjetivo *vazio* ("épico") mas aceitava o
adjetivo *de grau* ("dramaticamente", "rapidamente", "lentamente"). Esses também não renderizam —
o modelo não tem escala para eles. 🎓 *"video models prefer **arithmetic** over vague words like
'dramatically'"* · *"AI models don't really get big descriptions, but they understand **direct
comparisons**."*

| Em vez de | Escrever |
|---|---|
| "a câmera se aproxima dramaticamente" | "órbita de 8 m para 4 m, altura de 3 m para 2 m" |
| "rápido" | "três vezes mais rápido que um dolly cinematográfico típico" |
| "ele se levanta" | "mão no chão em 0,5 s, elmo erguido em 1,5 s, de pé em 3 s" |
| "a criatura é enorme" | "a cabeça dela ocupa 40% da altura do quadro" |
| "ela se transforma" | "0,4 s, snap seco — arma sendo sacada, não magia" |

🎓 *"When the timing is locked, the model can't rush it or skip stages."* — o número não é preciosismo,
é o que impede o modelo de pular etapa da ação.

**Duas travas de vocabulário que vieram junto:**

- 🟡 **Nunca escrever idade em palavra** ("engine rule 1" da skill da comunidade). Em vez de "um
  homem de 50 anos", descrever por **papel, porte, roupa e ação** — o modelo responde melhor e para
  de puxar para o rosto jovem arredondado. Casa com a estrutura facial adulta declarada
  (`model-sheet-storyboard.md`).
- 🟡 **Nomear personagem por marcador VISÍVEL, nunca pelo handle da referência.** Escrever *"o homem
  de capa vermelha"*, não *"@Image 1"* nem *"o Personagem A"*. O handle serve para declarar a
  referência; a linha de ação precisa de algo que exista no quadro.

**6. Luz motivada + lente (tabelas abaixo).** Fonte de luz sempre existente no mundo da cena
(lua, tocha, relâmpago, brasa). A direção da luz diz quem domina o quadro; revelar a criatura
POR PARTES (luz parcial — uma garra, um contorno, um olho) até o bloco de revelação total.

**7. Escrever os painéis (Doc 2) e os [SHOT] (Doc 3) com esse vocabulário**, mantendo todas as
regras vigentes (grid, painel 1 pré-ação, intermediários, âncora de realismo).
> O teto de **1.494 chars saiu desta lista em set/2026** — era do Leonardo e a plataforma mudou.
> Não há teto de plataforma; a regra de tamanho está em `higgsfield-cinema-studio.md`, seção 6.

## GRAMÁTICA — ângulo/movimento → efeito (escolher PELO efeito, nunca por variedade)

| Recurso | Efeito dramático | Usar quando |
|---|---|---|
| Low angle (contra-plongée) | poder, ameaça, divindade | criatura domina; deuses; revelação de escala |
| High angle (plongée) | vulnerabilidade, insignificância | vítima; humanos diante do colossal |
| Dutch/canted | mundo errado, instabilidade | maldição agindo; sanidade ruindo |
| Extreme close-up | detalhe como presságio | a mão que hesita, o olho que dilata, o amuleto |
| Close-up | interioridade | decisão, medo, luto — o rosto é a cena |
| Wide/establishing | solidão, escala, geografia | abertura de bloco; humano engolido pelo espaço |
| Over-the-shoulder | perseguição, ponto de vista | algo segue; alguém observa |
| Silhueta/contraluz | mito, não pessoa | criatura como forma antes de ser corpo |
| Push-in lento | tensão que aperta | aproximação do inevitável |
| Pull-back | revelação de contexto, abandono | mostrar onde aquilo realmente está; deixar a vítima só |
| Câmera estática, movimento interno | observação fria, documental | blocos de lore; o mundo age, a câmera testemunha |
| Handheld sutil | pânico humano | fuga, desespero — NUNCA em shot da criatura |
| Foreground occlusion | espreita | ameaça latente; ver sem ser visto |

Regras de combinação:
- UM movimento de câmera por shot, no máximo (regra existente — mantida).
- Eixo de 180°: dentro do mesmo shot e entre intermediários, os lados NUNCA se invertem
  (sujeito olhando para a direita continua olhando para a direita). Quebrar o eixo é permitido
  UMA vez por vídeo, deliberadamente, no pico de desorientação.

  > ⚠️ **E ele tem que ser ESCRITO DENTRO DO PROMPT, não só respeitado por nós (set/2026).**
  >
  > **Por que estávamos errados:** o eixo era regra *nossa*, aplicada na hora de escolher os
  > painéis. O modelo nunca era informado dele — então em multi-shot ele reposicionava a câmera
  > livremente e trocava os lados no corte. Nós obedecíamos a regra; o gerador não sabia que ela
  > existia.
  >
  > 🎓 Como a Academy escreve, e é para copiar a forma: eixo de 180° **mantido pela cena inteira**,
  > câmera estática, personagem A sempre do mesmo ângulo nas falas dela, corte para B **por cima do
  > ombro esquerdo dela** nas falas dele, *"no drift mid-segment"*, horizonte nivelado. Os corpos
  > orientados para **direções de quadro nomeadas**, para preservar a geografia de tela.
  >
  > Fraseado a usar: `180-degree axis held for the entire scene; [A] always framed from
  > camera-left, [B] always from camera-right; cut to [B] over [A]'s left shoulder; no drift
  > mid-segment; horizon level.`
- Direção de tela: a criatura entra/avança do MESMO lado do quadro ao longo do vídeo (presença
  que se repete = reconhecimento); inverter no clímax = confronto.
- Contraste de ritmo: tensão se constrói lento-lento-RÁPIDO. Três shots rápidos seguidos de um
  longo valem mais que seis médios.

## FRASEADO DE MOVIMENTO — o que o Seedance entende (usar literalmente no [SHOT])

`slow dolly forward` · `slow push-in on [alvo]` · `pull back to reveal [contexto]` ·
`orbit slowly around [sujeito]` · `handheld, slight shake` · `whip pan to [alvo]` ·
`snap zoom on [detalhe]` · `rack focus from [primeiro plano] to [fundo]` ·
`tilt up from [base] to [topo]` · `crane up, revealing [escala]` · `static camera, locked off`.
Especificidade vence adjetivo: "rack focus from the ember to the silhouette behind it" renderiza;
"dynamic camera work" não.

## LENTE COMO PSICOLOGIA (declarar no [STYLE]/âncora)

| Lente | Efeito | Usar quando |
|---|---|---|
| 24–35mm (ampla) | espaço engole o humano; distorção nas bordas | wides de escala; arquitetura opressiva |
| 50mm | neutra, olho humano | blocos documentais |
| 85–135mm (longa) | compressão; fundo esmagado sobre o sujeito | claustrofobia; a criatura "em cima" da vítima mesmo longe |
| Shallow DOF | isolar; só isto importa | rostos, objetos-presságio |
| Deep focus | a ameaça mora no ambiente inteiro | o fundo precisa assustar junto |

## REFERÊNCIAS DO BLOCO — obrigatório em todo Documento 2 e 3

Todo bloco abre com a declaração de quais referências aprovadas entram nele — personagem, e
também ambiente/mood quando existirem (decisão jul/2026):

```
REFERÊNCIAS DESTE BLOCO:
- IMAGE 1 = model sheet [Personagem A] (aprovado em [data]) → painéis 1–6 / [SHOT 1–2]
- IMAGE 2 = model sheet [Personagem B] → painéis 4–6 / [SHOT 3]
- IMAGE 3 = environment sheet [Nome do Ambiente] (se o bloco usa ambiente recorrente)
- IMAGE 4 = mood/style sheet do vídeo (se foi gerado)
```

E dentro do prompt: "use IMAGE n as strict character reference for [personagem]" / "use IMAGE n as
strict environment reference" / "match lighting and color grading of IMAGE n (mood sheet)". Bloco
sem essa declaração está incompleto — é ela que garante que o usuário anexe as imagens certas na
geração e que a consistência visual (personagem, ambiente E tom) atravesse o vídeo. Personagem ou
ambiente recorrente aparecendo em bloco SEM sua referência listada = erro a corrigir antes de
entregar. Ambiente e mood são OPCIONAIS por bloco (só quando existirem e forem aplicáveis);
personagem continua obrigatório sempre que aparecer.

## AUTOAVALIAÇÃO antes de entregar o bloco (o filtro anti-default)

Reler os prompts do bloco e responder na ficha, em uma linha cada:
1. Qual a intenção dramática, e cada shot serve a ela? (shot que não serve → cortar ou trocar)
2. Quem é o dono do olhar, e os ângulos obedecem?
3. A ação tem antecipação e consequência visíveis, ou só o gesto?
4. Todo painel tem primeiro plano declarado?
5. A luz tem fonte no mundo da cena?
6. Dois defaults, dois pecados: algum shot existe só "por variedade" (sem porquê dramático)?
   → trocar pela gramática. E o oposto: o bloco tem ≥3 tamanhos de plano e ≥1 insert de detalhe?
   → se não tem, MONOTONIA é o default em vigor; aplicar o plano de cobertura.
7. Cada shot tem os três detalhes da Lei dos Detalhes? Algum adjetivo banido sobrou no prompt?
8. População: há single/close de reação para cada personagem importante, ou todos os painéis são
   two-shots? Alguém encara a câmera sem motivação? Corpos apontam para o alvo da atenção?
Se alguma resposta falhar, corrigir ANTES de entregar — não entregar com ressalva.
