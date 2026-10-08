# Higgsfield — tradução genérica (intenção da `whoiam` → botão real do Higgsfield)

> Reescrito em 15/08/2026 pra parar de ser específico de uma criatura. Antes desta versão, a
> tradução estava amarrada a números de bloco do Cthulhu — inútil pra qualquer produção nova. A
> partir daqui, toda linha desta tabela deriva das tabelas GENÉRICAS que a `whoiam` já usa
> (`direcao.md`, `vendor-visual-skills/`), nunca do conteúdo de um vídeo
> específico. O Cthulhu vira só um EXEMPLO aplicado — ver `higgsfield-presets-exemplo-cthulhu.md`.
>
> **Papel deste arquivo:** é o CATÁLOGO dos presets do Cinema Studio 4.0 — nomes reais de botão,
> confirmados por print, e as tabelas de derivação (ângulo→Movement, lente-como-psicologia→
> Lens/Aperture, fraseado de movimento→preset). Ele preenche a parte 1 (SETTINGS) do `cena.md`
> (`etapa-4-cena.md`). Custo, parâmetros fixos e Elements: `plataforma-e-custo.md`.
>
> **Continua incompleto de propósito.** Minha única fonte de verdade sobre o Higgsfield são prints
> que o Samuel manda — não existe ferramenta de API/MCP que exponha esses campos aqui, e tentativas
> de ler as páginas do Higgsfield por link deram em app vazio (React/Next.js renderizado só por
> JavaScript, sem conteúdo no HTML puro). Ver "LACUNAS" no fim antes de confiar cegamente nisto.
> Atualização 24/08/2026: Genre, Era, Tempo, Lighting e Color palette já foram todos confirmados e
> fechados — não há mais lacuna conhecida de catálogo. Também confirmado: a Camada 1 inteira
> (Genre/Era/Tempo/paleta) trava por GERAÇÃO/BLOCO do Seedance, não pro vídeo inteiro — ver "Por
> que duas camadas" abaixo.
> **Lacuna nova, descoberta na fusão de 28/08/2026: a Emoção do personagem (roda de emoção da UI,
> linha "Emoção" do SETTINGS) nunca foi fotografada — não sei
> quantas opções tem nem os nomes reais. Pendente de print.** Também continua em aberto o
> workaround de Era pra período pré-1960s.

## Por que duas camadas

O Film Setup do Higgsfield mistura duas granularidades diferentes, e tratá-las como uma coisa só
foi o erro da primeira versão deste arquivo:

- **Camada 1 — nível da GERAÇÃO/CENA** (Genre, Era, Tempo, família de paleta de cor). Confirmado
  pelo Samuel (24/08/2026): o Film Setup do Higgsfield trava por geração do Seedance — uma cena de
  ~30s inteira sai no mesmo Genre/Era/Tempo, sem trocar NO MEIO dela, mas a cena seguinte já pode
  vir com um Film Setup diferente. Ou seja, essa camada é decidida **uma vez por bloco**
  (cada bloco = uma geração no Seedance), não uma vez só pro vídeo inteiro como a
  primeira versão deste arquivo supunha.
- **Camada 2 — nível do PLANO/SHOT dentro da cena** (Camera, Lens, Aperture, Movement, Lighting).
  Decidida a cada beat do `cena.md`, a partir da intenção que o algoritmo de `direcao.md` JÁ
  classificou pra aquele plano específico.

Isso significa que a troca de clima no meio do vídeo (começa calmo, vira terror) se resolve em
DOIS níveis que já existem: entre blocos, a Camada 1 inteira pode mudar (Genre Noir → Horror, por
exemplo); dentro do mesmo bloco, só a Camada 2 varia por shot. Nenhum mecanismo novo precisa
existir pra isso — só esta tabela de tradução em cima do que já existe.

---

## CAMADA 1 — decidida uma vez por bloco/geração (não pro vídeo inteiro)

### Genre — confirmado (24/08/2026)

Lista completa vista no seletor (ciclo com `< >`, "Story conventions the model should follow"):
**General, Epic, Drama, Noir, Comedy, Horror, Action.**

Mapeamento pro canal (mito/horror/dread, quase nunca comédia):

| Genre do Higgsfield | Quando usar | Por quê |
|---|---|---|
| **Horror** | Padrão pra blocos de revelação/ameaça direta da criatura | Bate literal com o registro do canal |
| **Noir** | Blocos de investigação, lore, mistério, cidade noturna | Sombra dura, contraluz, mesmo espírito da tabela de paleta "névoa fria/urbana noturna" |
| **Epic** | Blocos de escala colossal, clímax, revelação de algo "maior que humano" | Bate com blocos tipo a emergência de Cthulhu — grandiosidade, céu, escala |
| **Drama** | Blocos de interioridade humana (medo, decisão, colapso emocional de um personagem) | Foco no rosto/reação, sem estilização de gênero |
| **Action** | Blocos de confronto físico, fuga, perseguição | Cortes de impacto, clareza espacial |
| **General** | Blocos de transição/estabelecimento sem carga de gênero | Neutro — não força nenhuma convenção |
| **Comedy** | Descartado pra este canal | Nunca serve ao registro documental-sombrio |

Confirmado: Genre trava por geração/bloco (não dá pra trocar no meio de uma cena de ~30s do
Seedance), mas a próxima geração já pode vir com Genre diferente. Então, ao montar o `cena.md`,
escolher o Genre bloco a bloco — junto de Era/Tempo/paleta — usando a MESMA intenção dominante que
o passo 1 do algoritmo de `direcao.md` já classifica pra aquele bloco (ex.: bloco
de investigação/lore → Noir; bloco de emergência da criatura → Horror ou Epic).

### Era — confirmado (24/08/2026) — LACUNA CRÍTICA: não cobre períodos antigos

Lista completa vista no seletor (ciclo com `< >`, "The period the film belongs to"):
**Auto, 1960s, 1980s, 1990s, 2000s, 2020s.**

Achado importante: **não existe nenhuma opção antes de 1960s.** Isso significa que Era não serve
pra nenhuma criatura ambientada antes da década de 60 — inclusive o próprio Cthulhu (1925), que
ficaria sem preset de época correspondente. Pra esses casos:
- Usar **Auto** em Era (não force um "1960s" que é 35 anos adiante demais) e continuar resolvendo
  o período pelo texto do prompt (seção `LOOK`, referências de vestuário/tecnologia/grão de filme já
  descritas manualmente) como a `whoiam` já faz hoje.
- Reservar o preset de Era real pra criaturas com história ambientada em 1960 ou depois — aí sim
  escolher a década mais próxima do período real.

### Tempo — confirmado (24/08/2026)

Lista vista no seletor (ciclo com `< >`, "Pacing of the montage"): **Auto, Calm, Single shot,
Dynamic, Chaotic** (ordem exata de ciclo entre os 3 últimos não confirmada — não vi a régua com
os dois vizinhos como vi em Era; a suspeita de "régua lenta↔rápida" se confirma pelo nome e pelas
miniaturas: a barra de progresso embaixo do preview mostra mais segmentos preenchidos quanto mais
"cortado"/rápido é o preset, ex.: Single shot = 1 segmento contínuo, Chaotic = vários segmentos
picotados).

| Tempo | Quando usar |
|---|---|
| **Single shot** | Bloco contemplativo, sem corte — plano-sequência, silêncio, dread lento |
| **Calm** | Bloco narrativo tranquilo, ritmo de conversa/observação |
| **Dynamic** | Bloco narrativo com energia — transição, revelação progressiva |
| **Chaotic** | Bloco de ação/clímax/pânico — cortes rápidos e picotados |
| **Auto** | Deixar o sistema decidir quando o bloco não tem um ritmo dominante claro |

Mapear pelo RITMO do bloco (contemplativo → Single shot/Calm; narrativo → Calm/Dynamic; ação/clímax →
Dynamic). ⚠️ **Chaotic só se o Samuel pedir:** ele empurra para cortes rápidos e picotados, e a regra
do canal é 3 a 4 cortes por bloco (oito cortes já geraram câmera lenta).

### Color palette — família de clima → paleta (genérico, não por criatura)

Baseado nos ~40 nomes já catalogados (7 prints, 15/08/2026). Cada família abaixo é um arquétipo de
ambiente que se repete em QUALQUER produção do canal, não um bloco específico:

| Família de clima | 1ª opção | 2ª opção | Quando se aplica |
|---|---|---|---|
| Névoa fria / urbana noturna | **Industrial Fog** | Twilight Fable (ou The Investigation pra variante mais "observação/investigação à distância" — cais, navio visto de longe) | Cidade, cais, ruas à noite, qualquer estabelecimento de mundo sombrio |
| Interior quente a luz de lamparina/vela | **Oil & Ochre** | The Mountain Convent (variante fria/austera) | Biblioteca, cabine, qualquer interior iluminado por fonte prática quente |
| Tempestade / caos neutro | **Breakfast on Schedule** | Home Is the Next Gas Station | Blocos de ação física sem cor dominante — tempestade, luta, fuga |
| Interior ritualístico / cerimonial | **The Circus** | Crimson Vigil | Culto, ritual, qualquer cena com vermelho/dourado entalhado |
| Natureza doentia / cósmico-horror | **The Emerald Ambush** | The Morning After Rain | Ambiente alienígena, floresta/ruína tomada, o "lugar errado" da criatura |
| Corredor escuro com brilho sobrenatural | **Stairs Go Up** | Ghost in the Code / Bioluminescent Night | Portão, passagem, qualquer coisa que brilha onde não deveria haver luz |
| Confronto / clímax tenso | **A Hotel for One** | After Dark | Pico de ação, revelação da criatura, ápice do vídeo |
| Figuras encapuzadas / cerimonial ao ar livre | **The Grey Channel** | — | Culto visto de fora, epílogo, qualquer cena de figuras encapuzadas num ambiente aberto |

Ver `higgsfield-presets-exemplo-cthulhu.md` pra ver essa tabela aplicada bloco a bloco num vídeo
real. **Recomendo sempre**: gerar 1 frame de teste com a 1ª opção antes de fixar como padrão do
vídeo — miniatura pequena engana, render real não.

**Lista de paletas fechada em 24/08/2026: exatamente 50 nomes**, batendo com o "50+ color
palettes" do próprio metadado da página do Higgsfield. Todas as 50 já estão catalogadas (nas
tabelas de família acima ou na lista de descartadas abaixo) — não há mais cauda pendente.

**Descartadas de cara** (tom quente/diurno/vibrante, fora do registro documental-sombrio do
canal, qualquer criatura): Static Noon, Back Row Kissing Seats, On the Other Side of the Port,
Highway Standoff, The Faded Fresco, Pink Velvet, Two Days to the Horizon, Field Post, Glossy
Flesh, The Crimson Ballet, Neon Rain at Midnight, The Iron Borough, The Ground, Turquoise Mirage,
A Dream in Color, Favela Gold, The Neighbors Saw Everything, Mirage at Noon, Bubblegum Boulevard,
Yellow Room, The Earth Keeps Things, Tropic Fever Dream, The Butterfly, Wallpaper Romance, The Way
Home Is Longer, Runaway Summer, Amber Wasteland, Gasoline Sunset, Don't Turn It Off I'm Watching,
The Silk Curtain Falls, Playtime, Overtime, Everyone Speaks in Whispers.

---

## CAMADA 2 — decidida por beat, a partir da intenção já classificada

### De `Gramática — ângulo e movimento pelo efeito` (direcao.md) → Higgsfield

| Recurso (já escolhido pelo algoritmo, pelo EFEITO) | Movement / Camera-Lens-Aperture do Higgsfield |
|---|---|
| Low angle (contra-plongée) — poder, ameaça, divindade | Tilt up ou Crane up (câmera sobe olhando de baixo) |
| High angle (plongée) — vulnerabilidade | Crane down ou Aerial pullback |
| Dutch/canted — mundo errado, instabilidade | Nenhum botão de Movement cobre ângulo canted diretamente — descrever no texto do prompt; Movement fica em Static shot ou Handheld conforme o resto da cena |
| Extreme close-up — detalhe como presságio | Crush zoom, ou Static shot + Aperture f/1.4 Wide Open |
| Close-up — interioridade | Static shot ou Slow zoom in + f/1.4 Wide Open |
| Wide/establishing — solidão, escala, geografia | Static shot, Aerial pullback, ou Helicopter shot + f/11 Deep Focus |
| Over-the-shoulder — perseguição, ponto de vista | POV ou Side tracking |
| Silhueta/contraluz — mito, não pessoa | Lighting = Silhouette (câmera geralmente Static shot ou Slow zoom in) |
| Push-in lento — tensão que aperta | Slow zoom in ou Dolly in |
| Pull-back — revelação de contexto, abandono | Slow zoom out, Dolly out, ou Aerial pullback |
| Câmera estática, movimento interno — observação fria, documental | Static shot |
| Handheld sutil — pânico humano (nunca na criatura) | Handheld |
| Foreground occlusion — espreita, ameaça latente | Static shot ou Tracking, com o objeto de primeiro plano descrito no texto (Higgsfield não tem botão pra oclusão) |

### De `LENTE COMO PSICOLOGIA` → Lens/Aperture do Higgsfield

| Lente (já escolhida pelo algoritmo) | Aperture/Lens do Higgsfield |
|---|---|
| 24–35mm (ampla) — espaço engole o humano | Lens: Clean Sharp ou 35mm Film · Aperture: f/11 Deep Focus (se o fundo precisa ameaçar junto) ou f/4 Moderate (neutro) |
| 50mm — neutra, olho humano, blocos documentais | Lens: Clean Sharp · Aperture: f/4 Moderate |
| 85–135mm (longa) — compressão, claustrofobia | Lens: Anamorphic (comprime e alarga) · Aperture: f/1.4 Wide Open |
| Shallow DOF — isolar, só isto importa | Aperture: **f/1.4 Wide Open** |
| Deep focus — a ameaça mora no ambiente inteiro | Aperture: **f/11 Deep Focus** |

Casos especiais de Lens (fora da tabela de psicologia, usar com intenção clara):
- **Halation Vintage / Warm Vintage** — registro de lenda/memória (bate com afirmação classificada
  "Mediana"/"Reza a lenda" pela `pesquisa-seres"); nunca em blocos de ação ou revelação direta da
  criatura, porque o halo conflita com a âncora de realismo (`estilo-e-contencao.md`).
- **Anamorphic / Vintage Anamorphic** — quando o bloco pede peso de "cinema", não documental — bom
  candidato pro clímax/confronto do vídeo.
- **8mm Film** (Camera, não Lens) — só se o canal um dia quiser um registro "encontrado"/amador
  deliberado (found footage); não é o padrão.
- **DV Camcorder** — mesma lógica do 8mm Film, mais próximo de vídeo doméstico que cinema; evitar
  como padrão.
- **Modern** (Camera) — padrão geral pra quase todo bloco: bate com a âncora de realismo
  "ultra-realista, cinema camera" que todo prompt já carrega.

### De `FRASEADO DE MOVIMENTO` → Movement do Higgsfield

| Fraseado já usado no beat | Botão de Movement |
|---|---|
| `slow dolly forward` | Dolly in |
| `slow push-in on [alvo]` | Slow zoom in |
| `pull back to reveal [contexto]` | Slow zoom out ou Aerial pullback |
| `orbit slowly around [sujeito]` | Drone orbit, Arc left, ou Arc right |
| `handheld, slight shake` | Handheld |
| `whip pan to [alvo]` | Whip pan |
| `snap zoom on [detalhe]` | Crush zoom |
| `rack focus from [primeiro plano] to [fundo]` | Rack focus |
| `tilt up from [base] to [topo]` | Tilt up |
| `crane up, revealing [escala]` | Crane up |
| `static camera, locked off` | Static shot |

Botões de Movement vistos que ainda não têm fraseado equivalente no nosso vocabulário (guardar
pra quando fizer sentido usar): Snorricam, Robot arm, Bullet time, Dolly zoom (Hitchcock zoom —
zoom+dolly opostos, ótimo pra vertigem/revelação de escala colossal), Truck left/right, Slider
left/right, Pedestal up/down, Side tracking.

### Lighting — princípio, não bloco específico

| Botão visto | Princípio genérico de quando usar |
|---|---|
| **Practicals** | Sempre que a cena tem fonte de luz visível no próprio ambiente (lampião, vela, lamparina, tela) — é a aplicação direta da regra "luz sempre motivada por fonte do mundo da cena" que a `whoiam` já segue em todo prompt. Vai ser o mais usado em qualquer produção do canal. |
| **Silhouette** | Sempre que o algoritmo escolheu "silhueta/contraluz" na gramática de ângulos — revelar a criatura como forma antes de corpo. |
| **Window** | Interior com uma fonte direcional forte vinda de uma abertura — usar quando o Environment Sheet do bloco declarar uma janela/vão como fonte de luz do lugar. |
| **Overhead fall** | Revelação vertical dramática — algo caindo, um brilho vindo de cima, luz que desce de uma abertura no teto. |
| **Contre jour** | Fonte de luz forte atrás do sujeito, de frente pra câmera (não é a mesma coisa que Silhouette: aqui a luz "vaza" ao redor da figura, mais halo do que forma preta total) — bom pra revelações onde a criatura ainda precisa mostrar um pouco de detalhe/textura mesmo em contraluz. |
| **Soft cross** | Duas fontes suaves cruzando o sujeito (visto num quarto rosa, luz difusa e uniforme) — cenas íntimas/humanas sem tensão de sombra, o oposto do registro do canal; candidato fraco pra qualquer bloco de horror/dread. |
| **Auto** | Névoa densa dominando a cena, sem fonte pontual clara identificável no ambiente. |

Lista fechada em 24/08/2026 (7 presets reais + "New lighting preset", que é o botão de criar luz
customizada, não uma opção pronta): Auto, Silhouette, Practicals, Window, Overhead fall, Contre
jour, Soft cross.

---

## LACUNAS — o que ainda falta pra esta tabela ser confiável de ponta a ponta

- ~~**Genre**~~ — confirmado 24/08/2026 (7 valores: General, Epic, Drama, Noir, Comedy, Horror,
  Action). Troca por bloco, não por vídeo.
- **Emoção do personagem (roda de emoção da UI)** — nunca fotografada; não sei quantas opções tem nem os nomes reais.
  Pendente de print.
- ~~**Era**~~ — confirmado 24/08/2026 (Auto, 1960s, 1980s, 1990s, 2000s, 2020s). **Lacuna nova
  descoberta**: não cobre nada antes de 1960s — sem uso real pra criaturas de período antigo
  (Cthulhu incluso). Ver seção Era acima pro workaround.
- ~~**Tempo**~~ — confirmado 24/08/2026 (Auto, Calm, Single shot, Dynamic, Chaotic). Falta só a
  ordem exata do ciclo entre os 3 do meio.
- ~~**Lighting**~~ — confirmado 24/08/2026, lista fechada (7 presets: Auto, Silhouette, Practicals,
  Window, Overhead fall, Contre jour, Soft cross).
- ~~**Color palette**~~ — confirmado 24/08/2026, lista fechada em exatamente 50 nomes (bate com o
  "50+" do metadado da página). Único nome que não estava na tabela genérica ainda (só no exemplo
  do Cthulhu) era "The Investigation" — já incorporado na família "névoa fria/urbana noturna".
- Tentativa de ler o conteúdo por link falhou duas vezes (15/08/2026): `higgsfield.ai/generate?
  projectId=...` e `higgsfield.ai/community` são apps React/Next.js renderizados só por
  JavaScript — o HTML puro não carrega nada real, então WebFetch não serve pra isso. Só print
  funciona.

Confirmado por metadado da própria página do Higgsfield: "30+ camera movement presets and 50+
color palettes" — a lista de Movement acima (~32 nomes) provavelmente já está quase completa; a
de Color Palette (~40 nomes) ainda deve ter uns 10 nomes não vistos.
