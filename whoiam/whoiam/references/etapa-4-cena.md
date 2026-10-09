# Etapa 4 — O prompt de cena (formato definitivo)

> ⚫ **Formato único do canal desde 2026-10-06.** Nasce do `cena.txt` dos blocos 7 e 8 do Cthulhu,
> fundido com o que os prompts reais de **Cane Men** e **Detour** fazem melhor (lidos na íntegra em
> 2026-10-06; trechos comentados em `exemplos-externos.md`). A mescla, em uma frase: **cabeçalho
> estruturado por beat** (nosso) + **corpo em prosa causal e densa** (deles) + seções **CRITICAL**,
> **LIGHT** e **RECAP** (deles) + **travas afirmativas e contenção física** (nossas).
> Qualquer outro formato encontrado (`[SUBJECT]/[ACTION]`, `GOAL/STAGES/NEGATIVES`,
> `GLOBAL STYLE/POSITIVE LOCKS` solto, storyboard) é histórico.
>
> **O que NÃO se copia dos dois filmes:** a duração deles (14 s, 16 s, 20 s), o número de cortes
> (até 8) e os `<<<uuid>>>`. Aqui é **30 s, 480p, presets do Cinema Studio 4.0, 3 a 4 cortes** e
> Elements por `@label`. Eles não usam o nosso fluxo; o método de escrita é o que atravessa.

Arquivo: `C:\Ai-Project\Criaturas\<Nome>\blocos\bloco-NN\cena.md` — um por bloco.

---

## 1. O esqueleto

As partes 1 a 4 são **instrução para quem gera** (PT-BR, não se colam). A parte 5 é o **prompt**, em
inglês, colado inteiro. A 6 são observações.

````markdown
# Bloco NN — <título>
> ⚠️ **PROMPT DE CENA (VÍDEO) — colar no Higgsfield Cinema Studio 4.0, modo Video.**
> **Não é prompt de imagem: não vai para o GPT.**
>
> ⛔ **ESTE É O PASSO 4 de 4. Não começar por aqui.** Antes dele: (1) as imagens de `referencias.md`,
> geradas no **ChatGPT com a imagem nativa do GPT — NÃO no Higgsfield, NÃO pelo MCP**; (2) aprovação
> do Samuel; (3) cadastro dos Elements novos. Ordem completa em `EXECUTAR.md`, nesta pasta. **Se as
> imagens `ref_` não estiverem na pasta, PARE e volte ao EXECUTAR.md.** Não revisar nem reescrever
> este prompt: executar ou perguntar ao Samuel.
PRÉVIA (PT-BR, não colar): <1–2 frases do que acontece>
CONTINUA DE: bloco-(N-1), última pose: <…>   |   nenhuma
EFEITO PEDIDO: <o pedido do Samuel e como foi executado>   |   nenhum
CUSTO: 75 créditos (30 s · 480p)   |   300 se 4 takes (bloco de ação)

## 1. SETTINGS — Cinema Studio 4.0, modo Video
Resolução: 480p · Proporção: 16:9 · Duração: 30s · Áudio: On · Quantidade: 1 · Enhancer: Off
Genre: <…> · Era: <…> · Tempo: <…>
Camera: <…> · Lens: <…> · Aperture: <…>
Color palette: <…> · Lighting: <…>
Emoção: <personagem> (<intervalo>): <…>
Por quê: <uma linha ligando os presets à intenção do bloco>

## 2. UPLOAD — imagens, nesta ordem (o número é o @Image)
PASTA DAS IMAGENS: C:\Ai-Project\Criaturas\<Nome>\blocos\bloco-NN\
| @Image | Arquivo | Papel |
|---|---|---|
| 1 | ref_01_<slug>.png | <…> |
Vídeo de referência: bloco-(N-1)\takes\take-<n>.mp4 (quando CONTINUA DE)   |   nenhum
SALVAR O VÍDEO GERADO EM: C:\Ai-Project\Criaturas\<Nome>\blocos\bloco-NN\takes\take-<n>.mp4
(n = número da tentativa: take-1, take-2…; do take aprovado sai também ultimo-quadro.png na mesma pasta)

## 3. ELEMENTS — digitar no prompt; todos têm que ficar verdes
@per_<…> · @obj_<…> · @amb_<…>
Se algum não ficar verde: parar e avisar. Não gerar.

## 4. CONFERÊNCIA ANTES DE GERAR
- [ ] 480p no seletor (o padrão da tela é 720p e cobra 720p)
- [ ] imagens na ordem da tabela
- [ ] todos os @ verdes
- [ ] OK do Samuel para gastar os créditos deste bloco

## 5. PROMPT — colar daqui até o fim
DESTINO: Higgsfield Cinema Studio 4.0 → modo Video → campo de prompt (NÃO é para o GPT)
```
<TÍTULO EM CAIXA ALTA> — <3 a 5 palavras-chave da sequência, separadas por " / ">
TONE AND PACE
LOOK
LIGHT
SCENE
CAST AND REFERENCES
CRITICAL — <elemento>        (0 a 3 blocos)
CONTINUITY
REVEAL
BEATS (3 a 4, separados por CUT TO)
BACKGROUND
PHYSICS AND RESTRAINT
SPEED
SOUND
POSITIVE LOCKS
RECAP
```

## 6. OBSERVAÇÕES (PT-BR)
- Cortes: <n> — <beat (s)> …
- Última pose do bloco: <onde cada um está, para onde olha, o que segura> (para o bloco seguinte)
- Risco principal: <o que tem mais chance de falhar> → coberto por CRITICAL <qual>
- Plano B: <qual beat isolar num clipe curto se falhar>
- Autoavaliação (§3): <uma linha por pergunta>
````

---

## 2. Cada seção do prompt

### Cabeçalho — o título e a sequência em palavras-chave
Uma linha em caixa alta com o nome do bloco e os momentos principais, como nos dois filmes:
`THE CAP CHANGES HANDS — LAST PUNCH / THE CAPTAIN DIES / THE CAP / THE ORDER`. Dá ao modelo o mapa
antes do detalhe.

### TONE AND PACE — o clima e o regime de montagem
Duas ou três frases: o tom (`Suspenseful, restrained, tragic.`) e **como o bloco é montado**
(`Four shots. Long takes; the second shot holds.`). Os prompts do Detour abrem assim
(`Suspenseful dramatic vibe. Long takes.`), e é o que impede o modelo de picotar um bloco que
pede respiro.

### LOOK — a regra visual
A âncora **E** (com criatura) ou **B** (sem), mais a **C** (contenção) resumida, adaptadas com uma
frase de grade de cor e de clima (`estilo-e-contencao.md`). Nada de parâmetro: resolução, duração e
proporção são do seletor.

### LIGHT — de onde vem, o que toca, o que fica no escuro
Seção própria, porque luz é o que mais decide o realismo e o modelo exagera quando não é contida.
- **Fonte no mundo da cena** e direção (`the only light comes from two swinging lanterns at
  camera-right and the dying fires behind`).
- **O que a luz toca, nomeado:** `it catches only fragments: the wet brim of the cap, the brass
  button, the edge of Johansen's cheek, the rain in front of the lanterns.`
- **O que fica no escuro**, e quanto: `most of the deck stays in deep shadow; do not expose the
  whole ship.`
- Se a fonte muda dentro do bloco (relâmpago, porta abrindo), o segundo em que muda.

### SCENE — a situação
Onde, quando, o que acabou de acontecer, o que está em jogo, em 3 a 6 frases. **Situação rende mais
que expressão:** "ele percebe que a porta está trancada" ganha de "rosto de pavor". Clima com
intensidade física (`rain falls steadily`), nunca rótulo (`violent storm`).

### CAST AND REFERENCES — papel, o que tomar, o que não tomar
- Cada Element uma vez, com o **marcador visível** que vai ser repetido nos beats:
  `@per_johansen — JOHANSEN = the broad sailor in the black oilskin jacket.`
- Cada `@Image N` em uma linha: **o que é · o que tomar · o que não tomar · com que força**
  (`match exactly` · `match pose and wardrobe` · `layout and scale only` · `background only,
  never a subject` · `screen content only, nothing else from the image`).
- Fecho obrigatório, do jeito que os dois filmes escrevem:
  `Identity comes only from the Elements: face, build and outfit. Use each element image for
  reference only and never include the scene, backdrop or layout of that image. Do not recast,
  do not beautify.`

### CRITICAL — o elemento que mais tende a dar errado (0 a 3 por bloco)
A maior lição do Cane Men. Para cada coisa que o modelo costuma estragar nesta cena (a forma de um
lugar, o olho de uma criatura, o lado do ferimento, um objeto que passa de mão, a escala), um bloco
próprio:
1. **Descrição positiva exaustiva primeiro:** o que é, do que é feito, como varia, onde fica.
   O Cane Men gasta dezenas de linhas dizendo como é a margem natural do lago (pedras desiguais,
   lama, raízes, grama, partes sem pedra) **antes** de dizer o que ela não é.
2. **Só depois, as formas proibidas**, em lista curta, coladas à descrição (`not a perfect circle,
   not a concrete ring`).
3. **Regra de classe**, quando é um grupo: `Every hooded cultist wears the same dark-brown wool
   robe and hood; none is ever seen with a bare face.` · `Every character and every boat exists
   exactly once.`

Bloco sem nada crítico não tem a seção. Mais de 3 dilui: o que é crítico demais vira trava.

### CONTINUITY — o primeiro quadro, o eixo, o estado
- **FIRST FRAME AND BLOCKING:** no instante zero, onde está cada corpo, virado para onde, a que
  distância, o que segura. Bloco com 2+ corpos **abre com um plano aberto** que fixa as posições.
- **Eixo e direção de tela**, por sujeito e por fundo: `Johansen moves left to right; Collins stays
  on camera-right; the cult ship is always on the right horizon; screen direction never flips.`
- **Estado com lado exato:** ferimento, sujeira, roupa molhada, objeto na mão, com o lado do corpo e
  o segundo em que muda (`a dark wet patch on the LEFT side of Collins's coat; it never moves`).
- **Escala relativa e instância única:** `the cult ship is a third the length of the Alert; each
  character exists exactly once.`
- **Emenda (quando CONTINUA DE):** o vídeo anterior sobe como referência e o beat 1 **repete o
  último ~1 s de ação dele**: `The scene opens on the final second of the reference video —
  <pose exata> — and continues from there.` A sobreposição sai na montagem.

### REVEAL — o que o espectador vê, e quando
- **o que fica escondido e até quando**, e **como** (foco, contraluz, primeiro plano oclusivo,
  tamanho no quadro, fora de quadro);
- **a câmera não denuncia antes da hora:** ela reage ao evento, nunca antecipa;
- **economia de revelação:** `never show everything at once; one or two details are emphasized at
  any moment` (Cane Men, a sala de ratos). O espectador entende o todo por fragmentos;
- criatura se revela **por partes** até o bloco da revelação total.
Bloco sem nada a esconder diz isso em uma linha e onde está o foco de atenção.

### BEATS — cabeçalho estruturado + corpo em prosa causal
3 a 4 beats, separados por `CUT TO`. Cada beat:

```
<NOME DO BEAT> — 00:00–00:08 — <tamanho de plano, altura da câmera em metros, lente se importa>
CAMERA: <Movement> · <Speed> · <Framing> · <End>          (@Image n, @Image m)
<prosa: dois a seis períodos que contam o beat em ordem, com causa e consequência>
END: <o quadro de chegada — onde cada corpo termina, para onde olha> (= @Image n, se existir)
```

O corpo em prosa é onde os dois filmes ganham de nós. Ele carrega, nesta ordem de importância:
1. **A ação em ordem causal**, com antecipação → ação → consequência, e os conectores que travam a
   sequência: `only after`, `as he passes`, `the instant the cap leaves his head`, `until`. O
   Detour chega a escrever `Only after Lisa fully exits frame does Rider counter-steer`.
2. **O corpo, peça por peça**, com número no lugar de adjetivo (`lifts him 20 cm`, `holds for a
   full beat`), e o **estado interno contido**: o que aparece e o que ele segura
   (`grief is building under the surface, but he holds it back; his jaw stays set`).
3. **Posição e direção na tela** de cada sujeito e do fundo (`at frame-left, facing right; the
   crewmen deep at frame-right`).
4. **Foco como sequência com gatilho:** `focus stays on Johansen until his knees hit the planks,
   then racks to Collins's hand.`
5. **Profundidade:** primeiro plano / sujeito / fundo, e o que acontece em cada camada.
6. **Tempo de leitura:** `hold long enough for the cap to register clearly.`

Regras do beat:
- **Um movimento de câmera por beat**, escrito nos quatro campos; câmera parada também se declara
  com a negação exaustiva depois do positivo: `Locked-off camera: no pan, no tilt, no push.`
- **Timecode é orçamento, não ponto de corte.** Sub-segundo só quando a ordem importa (Detour usa
  `0:03.80`); não pendurar uma batida num segundo exato.
- **Pico no começo** em bloco de impacto; o modelo desacelera no fim.
- Ação violenta leva aceleração declarada em cada beat (`velocity keeps increasing, no settling`).
- **Evento sem corte:** o que pode acontecer dentro da composição (um tripulante que cai ao fundo,
  um navio que se aproxima) não ganha corte próprio: `do not cut to it; let it happen in the
  distance inside the composition.`
- Composição final precisa → referência de quadro de chegada (Etapa 3) e o `END` cita o `@Image`.

### ⚫ A referência é um ponto de passagem, nunca um quadro parado (Samuel, 2026-10-07 — vale sempre)

As imagens de referência fixam **como a cena está num momento**, não o que a câmera mostra parada.
**A ação acontece antes, entre e depois delas.** Por isso:
- Todo beat **começa em movimento** — a ação já em curso no primeiro instante, nunca uma pose posada
  que "ganha vida".
- O `@Image` de um beat é citado como **o momento por onde a ação passa** (`the action passes through
  the moment of @Image 3`), nunca como "o último quadro" ou "o primeiro quadro".
- **Nenhum beat termina parado.** Proibido terminar com `Hold.` ou com todos imóveis: no fim do beat o
  corpo ainda respira, chora, se ajeita, a chuva cai, a câmera ainda se move ou o personagem ainda age.
  O corte entra **no meio** de um movimento.
- Câmera travada é permitida; **gente parada não**. Mesmo um tripulante que "só observa" muda o peso
  do corpo, respira forte, segura um ferimento.
- Conferir, beat a beat: se o beat pudesse ser trocado pela própria imagem de referência sem perder
  nada, ele está estático — reescrever.

### BACKGROUND — uma linha por camada de profundidade
Atividade por classe, não por indivíduo, coerente com a cena: `Midground: crewmen drag the wounded
toward the rail. Deep background: two last struggles end, out of focus.` E a frase que segura o foco:
`The background never becomes a shot of its own.` Quando um evento atravessa as camadas (a
perseguição do Cane Men: fundo → meio → frente → câmera), escrever a progressão.

### PHYSICS AND RESTRAINT — força, reação, limite, densidade
- **Cadeia de força**, quando há contato: `force passes only along this chain: the wave → the
  hull → the deck → Johansen's knees.`
- **Ordem de reação do corpo:** o veículo ou o golpe move primeiro, o corpo responde depois, de
  baixo para cima (`boots, knees, pelvis, chest, head; the head never swings apart from the
  chest`).
- **Limite de dano:** o que cede e o que aguenta (`the rail splinters but stays attached; the mast
  cracks, it does not fall`).
- **Origem restrita dos efeitos:** `sparks come only from the metal-on-metal contact`, `smoke rises
  only from the burning stern`.
- Peso e matéria (tecido encharcado, corpo mole quando erguido). Criatura colossal devagar.
- **Densidade dos efeitos**, com as frases de `estilo-e-contencao.md` §4 e o fecho
  `Do not make every visible element dramatic at the same time.`

### SPEED
Padrão: `Real-time 24 fps throughout, natural speed.` Câmera lenta e rampa só pedidas ou exigidas
pela intenção, **por trecho e com motivo**. A câmera lenta que o modelo inventa sozinho é sintoma.

### SOUND — lista, contagem e silêncio
```
Diegetic sound only, recorded on location: <sons da cena, do mais próximo ao mais distante>.
<eventos contados e sincronizados: "two heavy hull impacts", "the cap's brass button clicks once">.
<silêncios: "one beat of silence after 00:14">. No music, no score, no dialogue, no voices,
no narration.
```
Som específico e pequeno, nunca "sound effects". Contar eventos sonoros, como o Detour faz, amarra
o som à imagem. Regra de contraste quando servir (`the storm is visible but the deck goes quiet
around Johansen`). Nunca "no audio" ou "no sound": isso mata o som da cena.

### POSITIVE LOCKS — as travas, por ordem de importância
O que precisa ser verdade do começo ao fim, a mais importante primeiro. Cada trava diz o que **é** e
depois o que **não** é:

| ❌ Negativa solta | ✅ Trava |
|---|---|
| `No swords.` | `Every fight is bare-handed, no swords.` |
| `No blood.` | `Wounds are implied by dark wet patches on clothing, no blood on screen.` |
| `Nobody looks at the camera.` | `Every gaze stays inside the scene, nobody looks at the camera.` |
| `No text.` | `Clean picture with no graphics, no captions, no subtitles, no on-screen text.` |

**Sobre maiúsculas:** os dois filmes usam caixa alta para **nomear seções e o elemento crítico**
(`CRITICAL`, `ZAY = NEON BEANIE`), e isso funciona. Frase inteira de proibição em caixa alta
(`NO SWORDS`) não: a importância se diz pela ordem da lista e pela seção CRITICAL.

### RECAP — a última coisa que o modelo lê
A sequência inteira em setas, com os segundos, e os marcadores de identidade e de estado. Cane Men
fecha todos os prompts assim. Repetir o essencial no fim é o que segura o modelo nos 30 s inteiros.
```
RECAP
00:00 last punch, Johansen runs → 00:08 kneels, Collins dies in his arms, camera stays on
Johansen's face → 00:18 the cap leaves Collins's head, insert → 00:24 Johansen stands, points to
the horizon → 00:28 puts the cap on → END on his face, the cult ship small behind him.
JOHANSEN = black oilskin jacket. COLLINS = grey beard, navy coat, wet patch on the LEFT side.
THE CAP = the same peaked wool cap in every shot.
```

---

## 3. Antes de entregar — a autoavaliação

Responder nas OBSERVAÇÕES, uma linha cada; corrigir antes de entregar o que falhar:
1. Qual a intenção, e cada beat serve a ela?
2. Quem é o dono do olhar, e os ângulos obedecem? Os personagens aparecem prioritariamente de
   frente ou em três quartos, com rosto legível e olhos, cabeça e corpo orientados ao alvo da
   cena? Cada vista de costas tem motivo narrativo declarado, conforme `direcao.md`, “Prioridade
   frontal e direção do olhar”?
3. Toda ação tem antecipação, consequência e conectores de causa (`only after`, `as`, `until`)?
4. Todo beat tem posição na tela, foco com gatilho, profundidade e `END`?
5. O risco principal tem um bloco CRITICAL com descrição positiva antes das proibições?
6. Marcadores de identidade e estados (com lado) aparecem em CAST, nos beats e no RECAP?
7. O que está escondido, até quando, e a câmera não denuncia antes?
8. A luz diz de onde vem, o que toca e o que fica no escuro?
9. 3 a 4 cortes? (nunca mais de 4)
10. Negativa solta, frase de proibição em caixa alta ou adjetivo vazio ("epic", "cinematic")?
11. Efeito físico em excesso? O perigo vem da situação?
12. Emenda com o bloco anterior escrita? Algum `@` sem status `cadastrado`?
13. **Densidade: cada beat cabe no tempo dele?** Contar as ações físicas principais de cada beat
    (andar até, ajoelhar, tirar o chapéu, entregar, morrer…). Referência: **uma ação principal a
    cada 3 segundos, no máximo**. Passou disso, tirar ação do beat, dar mais segundos a ele ou
    passar a ação para a imagem de referência (a pose já pronta no primeiro quadro).
14. **Nenhuma instrução anula outra?** Exemplos do que conferir: câmera travada × personagem que
    entra correndo e precisa ser acompanhado; foco no rosto × foco no objeto no mesmo instante;
    "o rosto dele nunca aparece" × um plano que precisa do rosto; um horário em CRITICAL diferente do
    horário no beat e no RECAP.
15. O `EXECUTAR.md` do bloco foi escrito, este arquivo diz no topo que é o passo 4, e o pacote
    (`montar_pacote.py`) monta sem erro?

## 4. Plano B — quando um trecho é arriscado

A observação já diz **qual beat isolar**. Se o take vier com aquele trecho ruim e o resto bom, não
se regera o bloco: gera-se só o trecho num clipe curto (a partir de 4 s, custo proporcional), que
entra por cima na montagem. Ordem completa em `rubrica-aceitacao-take.md` §7.

---

## 5. Exemplo completo — Bloco 8 do Cthulhu no formato

> Exemplo de forma. Os labels seguem o padrão novo; o projeto Cthulhu real usa labels anteriores
> ao padrão (ver o `registro.json` dele).

````markdown
# Bloco 08 — O chapéu passa de mão
> ⚠️ **PROMPT DE CENA (VÍDEO) — colar no Higgsfield Cinema Studio 4.0, modo Video.**
> **Não é prompt de imagem: não vai para o GPT.**
PRÉVIA (PT-BR, não colar): Johansen vence a última luta, corre até o capitão Collins, que morre
nos braços dele, e recebe o chapéu. Ele aponta o navio do culto: a caçada começa.
CONTINUA DE: nenhuma (o último quadro do bloco 7 não está disponível)
EFEITO PEDIDO: nenhum
CUSTO: 75 créditos

## 1. SETTINGS — Cinema Studio 4.0, modo Video
Resolução: 480p · Proporção: 16:9 · Duração: 30s · Áudio: On · Quantidade: 1 · Enhancer: Off
Genre: Drama · Era: Auto · Tempo: Calm
Camera: Modern · Lens: Clean Sharp · Aperture: f/4 Moderate
Color palette: A Hotel for One · Lighting: Practicals
Emoção: Johansen (00:00–00:30): luto contido, depois decisão · Collins (00:08–00:18): entrega
Por quê: luto pede Drama/Calm; as lanternas e as brasas são as únicas luzes do convés.

## 2. UPLOAD — imagens, nesta ordem
PASTA DAS IMAGENS: C:\Ai-Project\Criaturas\Cthulhu\blocos\bloco-08\
| @Image | Arquivo | Papel |
|---|---|---|
| 1 | ref_01_conves-pos-luta.png | estado do convés; só fundo |
| 2 | ref_02_collins-morrendo.png | pose do Collins caído, com o chapéu |
| 3 | ref_03_johansen-luto.png | pose e rosto de luto do Johansen |
| 4 | ref_04_chapeu-molhado.png | o chapéu nas mãos dele |
| 5 | ref_05_tripulantes-amurada.png | os dois na amurada |
| 6 | ref_06_navio-culto-horizonte.png | o navio do culto ao longe |
| 7 | ref_07_chegada-johansen-horizonte.png | quadro de chegada do último beat |
Vídeo de referência: nenhum
SALVAR O VÍDEO GERADO EM: C:\Ai-Project\Criaturas\Cthulhu\blocos\bloco-08\takes\take-<n>.mp4

## 3. ELEMENTS
@per_johansen · @per_collins · @per_tripulante-1 · @per_tripulante-2 · @obj_chapeu-collins · @amb_alert-conves

## 4. CONFERÊNCIA ANTES DE GERAR
- [ ] 480p · [ ] ordem das imagens · [ ] @ verdes · [ ] OK do Samuel

## 5. PROMPT
DESTINO: Higgsfield Cinema Studio 4.0 → modo Video → campo de prompt (NÃO é para o GPT)
```
THE CAP CHANGES HANDS — LAST PUNCH / THE CAPTAIN DIES / THE CAP / THE ORDER

TONE AND PACE
Restrained, tragic, then resolute. Four shots. The first moves with him; the second holds long on
his face; the third is a still insert; the fourth turns grief into a decision.

LOOK
Photographic naturalism, grounded real-life appearance, shot as if by a real cinematographer
documenting an actual event, on a cinema camera with a 35mm lens and visible fine film grain.
Cold grey-green night after the storm. Restrained contrast and restrained atmosphere: the battle
is over and the deck is quiet, with large calm dark areas and visual breathing room.

LIGHT
The only light comes from two lanterns swinging from a snapped line at camera-right and from
fires burning down to embers near the stern. It catches only fragments: rain falling in front of
the lanterns, the wet brim and brass button of the cap, the edge of Johansen's cheek, the beaded
wool of Collins's coat. Most of the deck stays in deep shadow; do not expose the whole ship.

SCENE
The mid-deck of the schooner @amb_alert-conves, minutes after the battle. The ship is wrecked,
rain falls steadily on the planks. Captain Collins has been stabbed and is dying on the wet deck.
His first mate, Johansen, is still finishing the last fight and has not reached him yet. When
Collins dies, the command of what is left of the crew passes to Johansen.

CAST AND REFERENCES
@per_johansen — JOHANSEN = the broad sailor in the black oilskin jacket.
@per_collins — COLLINS = the grey-bearded captain in the navy double-breasted coat, wearing the
peaked wool cap @obj_chapeu-collins.
@per_tripulante-1 and @per_tripulante-2 — THE CREWMEN = two exhausted sailors at the rail.
@Image 1: the deck after the battle — match its state, colour and light; background only, never a
subject.
@Image 2: Collins lying on his side on the wet planks, cap on his head — match pose and wardrobe.
@Image 3: Johansen kneeling, face wet with rain — match pose and expression.
@Image 4: the cap in Johansen's hands — match exactly.
@Image 5: the two crewmen at the rail — match pose and wardrobe.
@Image 6: the cult ship on the horizon — layout and scale only; it stays far away.
@Image 7: the final frame of the scene.
Identity comes only from the Elements: face, build and outfit. Use each element image for
reference only and never include the scene, backdrop or layout of that image. Do not recast, do
not beautify.

CRITICAL — THE CAP
The cap is a navy peaked wool captain's cap with a short black leather visor, a thin black braid
above the visor and one brass button on each side. It is soaked: the wool is dark and heavy, water
runs off the visor edge. It is the same single cap in every shot, identical to @obj_chapeu-collins
and @Image 4. It is on Collins's head until 00:20, then in Johansen's hands, then on Johansen's
head from 00:28. Not a sailor's knit hat, not a different cap, never two caps in the scene.

CRITICAL — COLLINS'S DEATH
The death is quiet and is read through Johansen, not through Collins's face. Collins's breathing
under Johansen's hand stops at 00:14; his hand slides off Johansen's wrist and lands on the planks.
His wound is implied only by a dark wet patch on the LEFT side of his coat that never moves or
spreads. No blood on screen, no visible wound, no convulsion.

CONTINUITY
First frame: Johansen at camera-left, 6 m from Collins, mid-stride, his fist landing on a hooded
cultist. Collins already down at camera-right, on his side, head toward the bow. The two crewmen
deep at frame-right by the rail. 180-degree axis held for the whole scene: Johansen moves left to
right, Collins stays on camera-right, the cult ship is always on the right horizon; screen
direction never flips. Johansen's jacket is soaked from the first frame. Each character exists
exactly once. The cult ship is small and far, about a fifth of the frame width at most.

REVEAL
Collins's death is never shown on his own face: the camera holds on Johansen and learns it from
him. The cult ship is not seen until 00:27, and only because the crewmen turn to look; the camera
turns after them, never before.

BEATS
THE RUN — 00:00–00:08 — medium close-up, camera at 1.6 m, running beside him
CAMERA: handheld tracking alongside Johansen · matches his running pace · his face and shoulders,
the deck sliding past behind · ends as he drops out of the bottom of frame        (@Image 1, @Image 3)
Johansen's fist lands and the hooded cultist folds out of frame-left; Johansen does not slow down.
Only after the body is gone does he turn his head toward Collins at frame-right, and from that
moment he runs straight at him, breath loud and ragged, jaw set, eyes fixed on one point ahead.
Rain throws off his jacket with every stride. A lantern swings across the foreground once; behind
him, blurred figures stumble in the dark. Focus stays on his face the whole time.
END: Johansen's knees hit the planks beside Collins, at frame-right.
CUT TO
THE DYING — 00:08–00:18 — close two-shot from 0.8 m, Johansen sharp, Collins soft in the foreground
CAMERA: slow push-in · about 10 cm per second · ends on Johansen's face alone · holds still for
the last 3 s                                                                      (@Image 2, @Image 3)
Johansen slides one hand behind Collins's shoulders and lifts him 20 cm off the wet wood. Collins's
right hand rises slowly and rests on Johansen's wrist. As the push-in continues, Collins's shoulder
leaves the frame and only Johansen's face remains. At 00:14 Johansen feels the breathing stop under
his hand: Collins's hand slides off his wrist and drops out of frame onto the planks. Johansen holds
completely still for a full beat. Grief is building under the surface, but he holds it back: his
jaw stays set, his eyes fill and do not blink, rain runs down his face. Hold long enough for the
moment to register.
END: Johansen's face alone in frame, eyes lowered toward Collins.
CUT TO
THE CAP — 00:18–00:24 — insert, extreme close-up from 1.0 m
CAMERA: locked-off camera, no pan, no tilt, no push · still · the cap and two hands only · the cap
held at chest height                                                              (@Image 4)
Johansen's left hand enters frame and stops a few centimetres above the cap, trembling. Only after
that hesitation does he lift it from Collins's head, slowly, the way you take something that belongs
to someone else. Water runs off the visor; the brass button catches the lantern light once. His
second hand joins the first. Focus stays on the cap; the hands are sharp at the edges, the deck
behind is black.
END: the cap held in both of his hands at chest height.
CUT TO
THE ORDER — 00:24–00:30 — medium shot, low angle from 1.2 m, Johansen standing
CAMERA: slow pan right following his arm · the pan takes 3 s · Johansen at frame-left, the crewmen
and the horizon at frame-right · settles on Johansen's profile with the ship behind  (@Image 5, @Image 6, @Image 7)
Johansen stands with the cap in his left hand and looks at the two crewmen at the rail. He does not
shout. He lifts his right arm and points toward the horizon at frame-right. Only after he points do
the crewmen turn their heads and look; as they turn, the camera pans with them and the cult ship
appears, small and far through the rain. At 00:28 Johansen puts the cap on his own head with one
hand, without looking at it.
END: Johansen's profile in focus at frame-left, the cap on his head, eyes on the horizon; the cult
ship small at frame-right (= @Image 7).

BACKGROUND
Midground: the two crewmen at the rail, still until they turn at 00:27. Deep background: two last
struggles end out of focus; one figure falls and does not rise; embers drift low. Let these happen
inside the composition; do not cut to them. The background never becomes a shot of its own.

PHYSICS AND RESTRAINT
Rain falls steadily and is carried by the surfaces: dark wet planks, beaded wool, water running off
the visor, Johansen's jacket hanging heavy. Collins is limp when lifted: his head follows his chest
with a short delay, his arm hangs. The rail is splintered but stays attached; the deck is tilted
slightly and stays stable. Smoke is thin and rises only from the stern fires, with clear air between
the figures. The fires light only the wet wood near them. Weight, not force. Do not make every
visible element dramatic at the same time.

SPEED
Real-time 24 fps throughout, natural speed, no slow motion.

SOUND
Diegetic sound only, recorded on location: Johansen's ragged breathing, his boots on wet planks,
rain on the deck, water dripping off the cap, embers crackling, the hull creaking, distant waves.
One dull punch impact at 00:01. One beat of silence after 00:14, when the breathing stops. No
music, no score, no dialogue, no voices, no narration.

POSITIVE LOCKS
1. The camera stays on the characters or on the cap; the deck, the rail and the ship are
   background only, never a close-up or a hold of their own.
2. One single cap, identical in every shot, moving from Collins's head to Johansen's hands to
   Johansen's head.
3. Wounds are implied by the dark wet patch on the LEFT side of Collins's coat, no blood on screen.
4. Every fight is bare-handed, no swords; no new fight starts after 00:08.
5. Every gaze stays inside the scene, nobody looks at the camera.
6. Clean picture with no graphics, no captions, no subtitles, no on-screen text.

RECAP
00:00 last punch, Johansen runs to Collins → 00:08 kneels, lifts him; 00:14 Collins dies, the
camera stays on Johansen's face → 00:18 insert: the cap leaves Collins's head → 00:24 Johansen
stands and points; the crewmen turn; the ship appears → 00:28 he puts the cap on → END on his
profile, the ship small behind him.
JOHANSEN = black oilskin jacket. COLLINS = grey beard, navy coat, wet patch on the LEFT side.
THE CAP = the same single peaked wool cap in every shot.
```

## 6. OBSERVAÇÕES
- Cortes: 4 — corrida (8 s), morte (10 s), chapéu (6 s), ordem (6 s).
- Última pose: Johansen de pé, perfil para a direita, chapéu na cabeça, olhando o horizonte;
  tripulantes na amurada, de costas para a câmera.
- Risco principal: o chapéu mudar de modelo entre beats → CRITICAL — THE CAP.
- Plano B: se o beat 3 sair com chapéu diferente, isolar 00:18–00:24 num clipe de 6 s com
  @Image 4 como start_image.
- Câmera na mão no beat 1: motivo, o pânico de chegar a tempo.
````
