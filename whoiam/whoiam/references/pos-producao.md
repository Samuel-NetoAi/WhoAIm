# PÓS-PRODUÇÃO — Narração, Trilha (Biblioteca do YouTube + Suno), SFX e Edição (CapCut)

Complemento do SKILL.md para a fase pós-montagem. Mesma disciplina do receituário Seedance:
o que está marcado como PONTO DE PARTIDA não foi testado no canal — vira regra só após
veredito real do usuário, e o veredito deve ser registrado aqui.

> **Nomes usados aqui (todos da etapa 6, pós-produção):** Documento 1/1a = legenda-base (o texto
> da narração encaixado na montagem travada) · Documento 4 = narração marcada para o ElevenLabs v3 ·
> Documento 6 = cortes para Shorts · Documento 7 = mapa de trilha · Documento 8 = mapa de edição.
> Nenhum deles é gerado antes de os 20 takes estarem aprovados e montados no Studio.

---

## 1. NARRAÇÃO — ElevenLabs v3 (A/B ENCERRADO)

Status: DECIDIDO (jul/2026) — vencedor: **ElevenLabs v3 com audio tags**. O formato Suno de
narração está aposentado (Suno continua só na trilha, seção 2). Todo o procedimento de narração —
tags, configurações, perfil de voz por criatura, formato de entrega, registro empírico — está em
`references/narracao-elevenlabs-v3.md`. Não duplicar aqui.

**Duas etapas, nesta ordem (decisão jul/2026 — inverteu a ordem antiga):**

**1a. RASCUNHO DE LEGENDAS COM PLACEMENT (antes de qualquer geração no ElevenLabs).** Assim que
`cenas-travadas-<criatura>.md` existir (durações reais travadas), gerar um rascunho: o roteiro
reescrito (Fase de sincronização, acima) dividido por SEQUÊNCIA, com o texto de cada uma mapeado
contra a duração real daquela sequência, usando o ORÇAMENTO DE DURAÇÃO já existente (custo =
palavras + 1,5×reticências + 2×[pause]; ver `narracao-elevenlabs-v3.md`) para estimar se o texto
cabe. Formato:
```
SEQUÊNCIA 3 (trava: 12s real) — custo estimado do texto: 27 (~12,3s pela constante calibrada)
[texto da narração desta sequência, sem tags ainda — só o texto e a pontuação de ritmo]
```
O usuário lê o rascunho inteiro, vê onde o texto aperta ou sobra em cada sequência, e AJUSTA A
PALAVRA antes de qualquer áudio existir — sem gastar geração nenhuma no ElevenLabs. **Nada aqui é
fixo:** é estimativa de planejamento (a mesma constante calibrada usada no orçamento de duração,
que já carrega sua própria margem de erro); o texto pode mudar de novo depois, inclusive depois do
áudio real existir. O valor deste passo é dar visibilidade de encaixe ANTES de comprometer geração,
não travar nada.

**1b. GERAÇÃO FINAL.** Só com o rascunho aprovado pelo usuário: aplicar a passada de marcação
(audio tags do vocabulário do canal, ver `narracao-elevenlabs-v3.md`) em cima do texto já ajustado
— não remarcar do zero — e gerar 2–3 takes por sequência no ElevenLabs. A partir daqui, qualquer
sincronia (Documento 8) usa a duração do ÁUDIO REAL gerado, nunca a estimativa do rascunho 1a —
o rascunho só serve para planejar o texto, não substitui medir o áudio de verdade depois.

**1c. LOCALIZAÇÃO — PT/EN/ES (decidido 28/08/2026, ainda não testado).** Depois do vídeo montado com
a legenda do 1a/1b travada como guia de timing, a legenda vira **opcional** no vídeo final (overlay
que pode ser ligado/desligado) — sempre, nas 3 versões. **É AMBOS: dublagem E legenda**, não um ou
outro:
- **Dublagem:** o mesmo texto marcado (audio tags, `narracao-elevenlabs-v3.md`) é traduzido e
  reenviado ao ElevenLabs trocando só o idioma da voz — gera o áudio EN e ES do zero, não é
  "legenda lida por cima do áudio PT-BR".
- **Legenda:** cada idioma ganha sua própria legenda (o mesmo texto traduzido, sincronizado ao
  áudio daquele idioma), sempre como overlay opcional — nunca queimada/obrigatória no vídeo.
- **Entrega:** o texto traduzido das 3 versões (PT/EN/ES) sai da skill (eu) ou é entregue pelo
  próprio usuário depois de gerar no ElevenLabs — os dois caminhos são válidos.

**Constraint real que isso cria, e que precisa entrar no checkpoint:** a tradução não é troca livre
de palavra — o áudio EN/ES tem que caber na MESMA janela de tempo de cada sequência/bloco que o
vídeo já tem travada (o vídeo é o mesmo, só a narração muda). Inglês e espanhol raramente têm a
mesma contagem de sílabas/palavras que o português para dizer a mesma coisa. **Rodar o rascunho do
1a de novo para EN e ES antes de gerar** (mesma lógica, texto traduzido em vez de original), ajustar
a tradução pelo encaixe — não só pelo sentido — e só então gerar. Primeira execução real vai revelar
se a constante de custo/duração precisa de um fator por idioma; registrar aqui quando acontecer.

**Aviso permanente:** narração 100% sintética em canal faceless carrega risco real de desmonetização
(política de conteúdo inautêntico do YouTube). Conteúdo original e edição pesada mitigam, não eliminam.
Relembrar o usuário disso uma vez por projeto, sem repetir em todo documento.

---

## 2. TRILHA MUSICAL — Documento 7: MAPA DE TRILHA

> 📖 **Antes de montar um mapa de trilha, ler `musicalidade.md`** (criado em 03/09/2026): a gramática
> de cena apurada, a operação real da Biblioteca (6 filtros na aba Músicas, 2 na de efeitos), as duas
> licenças, o vácuo sobre uso FORA do YouTube que afeta os Shorts — e **a regra de que o agente não
> escuta**, com a divisão de trabalho que ela impõe.


**Fonte primária: Biblioteca de áudio do YouTube Studio. Complemento: Suno.** (Decisão ago/2026 —
inverteu a hierarquia anterior, em que o Suno era a fonte e a Biblioteca era "fallback".)

Por que a Biblioteca vem primeiro: as faixas são gratuitas, monetizáveis dentro do YPP e **não são
reclamadas pelo Content ID** — some a categoria inteira de risco de reclamação. Reclamação indevida
acontece raramente e se contesta linkando a página da faixa. Não há divisão de receita.

Por que ela não resolve tudo, e isso precisa estar dito: o acervo é forte em jazz, rock, reggae, pop,
folk e country, e **fraco exatamente no que a paleta deste canal pede** — drone grave, cluster
dissonante de metais, percussão de guerra, crescendo glacial. Então o mapa de trilha é MISTO por
desenho, não por preguiça.

**Regras fixas (mantidas):**
- SEMPRE instrumental. Todo prompt Suno de trilha termina com: "instrumental, no vocals, no lyrics".
- **O cue segue a SEQUÊNCIA EMOCIONAL, não o bloco.** Uma música cobre vários blocos consecutivos do
  mesmo clima e só troca quando a cena/atmosfera vira (ex. Cthulhu: toda a sequência do arqueólogo
  no cais/navio/biblioteca = 1 cue; a virada para a revelação cósmica = novo cue). Três blocos de
  suspense recebem UMA música de suspense, nunca três diferentes — trocar melodia dentro do mesmo
  intento é o erro que esta regra existe para impedir.

**Regras novas de licença — precisam sair daqui e entrar na descrição do vídeo:**
- Faixa da Biblioteca com licença padrão: nenhuma obrigação.
- Faixa marcada **`Creative Commons — Attribution (CC BY 4.0)`**: crédito ao artista + link da faixa
  na descrição, obrigatório. A coluna "Tipo de licença" no YouTube Studio é onde isso se lê.
- Faixa marcada **"somente YouTube"**: não pode sair da plataforma (nada de reaproveitar em Shorts de
  outra rede, TikTok, etc.).
- Suno: exige plano pago (Pro ou Premier — Studio é só no Premier) para uso comercial. O direito vale
  para as faixas geradas enquanto a assinatura estava ativa, e continua valendo depois de cancelar.
  Música 100% gerada por IA não tem proteção de copyright — ou seja, você também não consegue
  registrar no Content ID nem impedir que outro canal use a mesma faixa. Isso não é risco de strike;
  é só uma expectativa que não deve existir.

**Formato do Documento 7 — gerar só após a montagem travar as durações:**

| Cue | Sequência emocional | Blocos cobertos | Duração-alvo | Fonte | Faixa / Prompt | Licença · crédito? |
|-----|--------------------|-----------------|--------------|-------|----------------|--------------------|
| 1 | Mistério/investigação | 1–4 | ~1m10s | Biblioteca YT | `<nome da faixa + artista>` | padrão · não |
| 2 | Revelação/terror | 5–7 | ~50s | Suno | `<prompt>` | Pro · não |
| 3 | Luto/desfecho | 8–9 | ~40s | Biblioteca YT | `<faixa>` | CC BY · **SIM** |

- A coluna de licença/crédito não é decoração: ela é o insumo que a skill `postagem` usa para montar o
  bloco de créditos da descrição. Cue CC BY sem crédito na descrição é descumprimento de licença.
- Duração-alvo = soma dos blocos + 5–10s de respiro para fade. Gerar/baixar a música MAIOR que a
  sequência e cortar no CapCut — nunca menor.
- Prompt Suno de trilha: gênero/atmosfera + instrumentação + andamento + dinâmica (e.g. "slow build") +
  "instrumental, no vocals, no lyrics". Não usar nomes de artistas ou obras reais.
- **Ordem de busca ao montar o mapa:** primeiro procurar o clima na Biblioteca; só cair no Suno quando
  a busca falhar — e registrar aqui QUAL clima a Biblioteca não cobriu, para o mapa do próximo vídeo
  já começar sabendo.

---

**Paleta por tipo de cena — PONTO DE PARTIDA (não testado; refinar com vereditos):**
- Mistério/investigação: drones graves, cordas sustentadas, piano esparso, pulso lento, tensão contida.
- Horror cósmico/revelação: sub-bass, brass clusters dissonantes, coros NÃO (instrumental) → usar pads
  vocálicos sintéticos apenas se o usuário liberar; crescendo glacial.
- Trágico (Medusa, Sereia): violoncelo solo, piano menor, cordas lentas, melancolia contida.
- Nórdico (Jormungandr): percussão de guerra (taiko/bombo), trompas, cordas friccionadas, frio e épico.
- Olímpico (Zeus): metais nobres, cordas amplas, percussão orquestral, majestade.
- Folclore BR (Boi Tatá): viola/violão atmosférico, percussão orgânica, texturas de mata, mística.
- Ação/perseguição: ostinato de cordas, percussão acelerada, sforzandos nos impactos.
- Contemplativo/abertura: pads amplos, harpa/piano, dinâmica baixa — deixar espaço para a narração.

> ⚫ **Calibragem do Samuel (03/09/2026): "nada de muito exagerado."** A paleta acima descreve
> instrumentação, não intensidade. **Textura vence melodia** neste canal: melodia forte disputa a
> mesma atenção que a narração, e drone/pedal grave/ostinato sustentam sem competir. Trilha que
> "atua" — que tenta produzir a emoção em vez de sustentar a cena — é o erro a evitar.
>
> ⚠️ **Isto ainda NÃO está apurado.** A busca de 03/09 sobre escolha de trilha por tipo de cena e
> sobre o erro do exagero **não achou fonte utilizável** (o Salomão recusou responder de cabeça, e
> foi o certo). Só o eixo de MIXAGEM apurou. **Refazer a pesquisa em perguntas curtas e separadas**
> — uma por eixo, não uma pergunta composta, que foi o que fragmentou a busca.

---

## 2b. SOM DIEGÉTICO E SFX — ⚫ REVERTIDO em 2026-09-03 (decisão do Samuel)

> ### O áudio nativo do Seedance volta a ser LIGADO. `generate_audio: true`.
>
> **O que estava errado, nas palavras dele:** *"não é porque não tem música que significa que não
> vai ter som. Se nós gerarmos uma cena do personagem quebrando um vidro e não tiver som, nós vamos
> adicionar isso na pós? Não ia ser natural."*

**O erro, e ele é de raciocínio, não de gosto.** A regra anterior desligava o áudio inteiro para
impedir que o modelo inventasse trilha. Mas o parâmetro não separa música de efeito — ele é um
interruptor da faixa toda. Desligar para matar a música matava junto **todo o som diegético**: o
vidro que quebra, o passo na madeira, a respiração, a água. Os clipes chegavam **mudos**.

E o custo disso não era neutro: a seção de som do prompt virava lista de compras, e a pós tinha que
**remontar à mão** um som que o modelo já sabia fazer — e sincronizar na unha um estilhaço com o
frame do impacto. 🎥 O material de setembro mostra o nível que o modelo entrega quando se pede
direito (*"cada passo produz um guincho de sola de borracha seguido imediatamente de um pequeno
splash molhado sob o pé correspondente"*). Jogar isso fora para não ganhar música é troca ruim.

### A correção é a MESMA regra da negativa acompanhada (`REGRAS` §7.4b)

Não se resolve com interruptor, resolve-se com **trava positiva**. A seção `SOUND` passa a
terminar sempre com a trava, e ela segue a forma do guia oficial — afirmação positiva primeiro, a
negação aparando o que sobrou:

```
diegetic sound only, recorded on location: <sons específicos da cena>
— no music, no score, no soundtrack, no ambient pads
```

**Isto não é o mesmo "cinto e suspensório" de antes.** Antes a frase negativa era redundante (o
parâmetro já matava tudo); agora ela é a **única** coisa segurando a música, e por isso tem que
carregar a afirmação positiva ao lado. Negativa órfã aqui é defeito de prompt.

### O que muda em cada etapa

| Etapa | Antes (mudo) | Agora |
|---|---|---|
| **Parâmetro** | `generate_audio: false` / `sound: off` | **`generate_audio: true`** |
| **Seção `SOUND` do prompt** | lista de compras para a pós | **instrução de verdade para o gerador**, com a trava positiva no fim |
| **Nível de detalhe** | genérico bastava | **específico e microscópico** — é o que o modelo executa bem |
| **SFX na pós** | camada obrigatória, montada do zero | **camada de REFORÇO** — só o que o take não entregou |
| **Trilha** | Documento 7 | Documento 7, **sem mudança** — a música continua entrando só na pós |

### A régua de aceitação da faixa de áudio, por bloco

O take agora tem duas coisas para julgar. Na ordem:

1. **O vídeo passou pela `rubrica-aceitacao-take.md`?** Se não, a faixa de áudio é irrelevante.
2. **A faixa veio limpa (só diegético)?** → aproveitar.
3. **A faixa veio com música por baixo?** → **descartar a faixa inteira daquele bloco** e montar o
   SFX na pós, como no regime antigo. **Não regerar o bloco por causa do áudio** — o vídeo custa
   75 créditos, a camada manual custa zero.
4. **Registrar a frequência disso.** Se a música vazar em muitos blocos apesar da trava positiva,
   a trava não está funcionando e a decisão volta à mesa.

> 🔵 **Custo — evidência coletada em 2026-09-03, e ela é tranquilizadora.** No catálogo ao vivo do
> **Kairogen**, o `conditionalPricing` do Seedance 2.5 condiciona preço **só a `resolution` e
> `turbo`**. `audio` existe no `param_schema` e **não aparece em nenhuma condição de preço** — o
> provedor cobra por segundo, por resolução. Isso é forte indício de que o modelo-base não cobra
> pelo áudio, e sustenta a linha antiga de que "custa a mesma coisa".
>
> ⚠️ **Mas é outra plataforma (Kairogen, em BRL), não o Higgsfield.** O `get_cost` do Higgsfield
> **não pôde ser rodado** — o MCP estava desconectado na sessão de 03/09. **Confirmar no primeiro
> bloco real antes de fechar o orçamento de um vídeo inteiro.** A conta de 75 cr/bloco foi medida
> com áudio desligado e continua sendo a base até essa medição existir.

**O que NÃO mudou:** nenhuma música sai do gerador, em hipótese nenhuma. A trilha é decidida
holisticamente no Documento 7, depois da montagem, e nunca bloco a bloco.

---

## 2c. MIXAGEM narração × trilha — 🔎 apurado em 2026-09-03 (dossiê Salomão)

> Dossiê em `D:/Agentes/SALOMAO/missoes/2026-09-03-como-mixar-ma-sica-de-fundo-com-narraa-a-o-em-voz/dossie.md`.
> **6 fontes, 4 comerciais, nenhuma primária, nenhuma medição independente.** Tudo aqui é ponto de
> partida — e um dos eixos está em conflito aberto de 4×.

⚠️ **O conflito: quanto abaixar a música sob a voz?**

| Fonte | Data | Valor |
|---|---|---|
| Record, Mix and Master (Simon Duggal — credencial acadêmica, **não** vende ducking) | 2024-05-06 | **3 a 6 dB** abaixo da voz |
| Zella (blog de produto — **vende** auto-duck) | 2026-07-19 | **18 a 25 dB** abaixo, ~20 dB de bolso |

**Hipótese do Salomão para reconciliar** (é leitura dele, nenhuma fonte diz isso): os dois medem
coisas diferentes — 3–6 dB é **balanço estático de fader**, 18–25 dB é **profundidade do duck
enquanto a voz fala**. **Adotamos as duas em cadeia**, e medimos no primeiro vídeo:

```
1. fader: música 3–6 dB abaixo da narração  (balanço de base)
2. sidechain na trilha da música, com a VOZ como key input
3. ataque < 300 ms · release mais lento  (assimetria = respiração, não bombeamento)
4. nos silêncios a música sobe — é ali que a trilha justifica existir
```

**Critério de ouvido — duas fontes independentes concordam:** *se você percebe a música enquanto a
pessoa fala, está alta; se não percebe nunca, está baixa. As pausas é que são o lugar dela.*

**EQ carving NA MÚSICA** (fonte única): a voz mora em **250 Hz–5 kHz**; corte de **2 a 4 dB com Q
estreito** na trilha da música dentro dessa faixa. ⚠️ A fonte **não diz onde centrar**, e 4 oitavas
é largo demais para ser receita. Indício para fechar: a inteligibilidade mora em **1,5–2,5 kHz**.

**LUFS:** quatro fontes repetem **−14 LUFS integrado** para YouTube — **nenhuma é do YouTube**, e a
mais recente chama de *"ponto de partida, não regra universal"*. O −14 vale para **a mistura
inteira** (voz + música), não para a voz sozinha. True peak tem três valores conflitantes
(−0,1 / −1 / **−2 dBTP**); o **−2 dBTP** é o único declarado para YouTube por quem não vende o
limitador.

> 🔵 **A ação que vale mais que todos os números, e é de graça:** publicar, abrir **"Stats for
> nerds"** e ler `Volume / Normalized`. `100% / 60% (content loudness 4.4dB)` = o áudio estava
> 4,4 dB alto e o YouTube baixou. **Corrigir o PRÓXIMO vídeo por esse número.** Duas fontes que não
> se conhecem chegam à mesma postura: não acredite no alvo publicado, meça a saída.
>
> **Assimetria que decide para que lado errar:** o YouTube **abaixa** o que veio alto, mas em geral
> **não levanta** o que veio baixo.

**Lacunas que o dossiê NÃO fechou:** threshold/ratio/release do sidechain · onde centrar o corte de
EQ · high-pass na música · qual LUFS a música sozinha deve ter · **nada sobre voz sintética** — e a
nossa narração é ElevenLabs, então o comportamento dela sob gate e compressão pode não ser o de voz
gravada em cabine.

**Regra nº 1, que número nenhum substitui:** a narração nunca disputa com a música.

---

## 3. EDIÇÃO — O STUDIO PRÓPRIO DO USUÁRIO (Documento 8: MAPA DE EDIÇÃO)

**Correção de premissa (19/08/2026).** Esta seção foi escrita presumindo CapCut. O editor do canal é
**"o Studio"** — `github.com/Samuel-NetoAi/WhoAIm`, pasta `studio/`: aplicação **Next.js 16 +
Remotion 4.0.495** que o próprio usuário desenvolveu, com render server-side e pós-processo por ffmpeg
local. **Código auditado em 19/08/2026** (veredito do upscale abaixo, na linha "Upscale"). O que ele faz:

| Função do Studio | O que muda nesta referência |
|---|---|
| **Legendas sobrepostas ao vídeo**, para ver onde a narração encaixa | É o **Documento 1a (rascunho de legendas com placement)** executado de verdade, em cima do vídeo real, em vez de estimado por constante. Quando o Studio estiver rodando, ele **substitui** a estimativa: o rascunho da skill vira insumo de texto, e o encaixe se lê na tela. |
| Filtros | Camada de grading; conversa com o Mood Sheet e com o "Manual Style" do Cinema Studio — cuidado para não gradear duas vezes. |
| Biblioteca de músicas | **Resolvido (19/08/2026): são faixas licenciadas do YouTube, sem risco de strike** — coerente com a hierarquia da seção 2, onde a Biblioteca do YouTube é a fonte primária. Duas ressalvas que continuam valendo: (a) faixa marcada `CC BY 4.0` exige crédito ao artista + link na descrição, e isso é termo de licença, não regra de curso; (b) **Biblioteca de áudio do YouTube Studio ≠ YouTube Music.** A Biblioteca (em Studio → Áudio) é livre para uso em vídeo; o YouTube Music é serviço de streaming e as faixas dele NÃO são licenciadas para trilha. Se alguma faixa do acervo do Studio veio do segundo, ela sai. |
| **Interpolação de frames** | ⚫ **REVERTIDO em 2026-09-03 — passa a ser LIGADA por padrão, no fim da edição, com exceção por cena.** Ver §3b abaixo. |
| **Upscale** | `scale=lanczos` 2x — reamostragem, **não sintetiza textura**. Custo marginal zero, mas não recupera detalhe. Por isso o bloco-vitrine, quando existir, sai em 720p (`plataforma-e-custo.md` §2). |
| **Resolução de saída** | Composição sempre com ≥1080p no lado curto, desacoplada dos clipes — decisão acertada: legenda e overlay ficam nítidos em vez de rasterizados a 480p. |

### 3b. ⚫ INTERPOLAÇÃO PARA 60fps — revertido em 2026-09-03 (decisão do Samuel)

> **Motivo, dele:** *"eu tinha feito uma interpolação de um vídeo no Kairogen como teste, e o
> resultado foi um vídeo incrivelmente fluido, mais fluido que o padrão dos vídeos do YT. Não
> podemos descartar uma característica tão boa assim."* A cena de teste era **de ação**, que é
> justamente o caso que a regra antiga alegava que quebraria.

**Por que a regra antiga não fica simplesmente errada — ela mirava em outro alvo.** A rejeição foi
escrita sobre o **`minterpolate` do ffmpeg**, que é fluxo óptico clássico, e o próprio comentário do
código já dizia isso: *"RIFE (AI) is the planned upgrade"* (`studio/lib/render/postprocess.ts`). O
teste do Samuel rodou no **Kairogen**, que é outro motor. Então o teste **não valida o
`minterpolate`** — valida a interpolação neural. As duas coisas não são intercambiáveis.

> ⚠️ **Não foi possível confirmar qual motor o Kairogen usa.** Varredura no catálogo do MCP em
> 03/09: `list_models` não retorna nada para "topaz" nem "upscale" em vídeo — a página de upscale de
> vídeo não está exposta como modelo. **Perguntar ao Samuel o que a interface mostra**, ou testar
> lado a lado com o `minterpolate` no mesmo clipe.

### A arquitetura que ele pediu JÁ EXISTE no Studio

Auditado em 03/09 — não precisa ser construída, precisa ser exposta na interface:

| Rota | O que faz | Serve para |
|---|---|---|
| `app/api/projects/[id]/enhance-clips` | interpola/upscala **clipe a clipe** antes do analyze | **a exceção por cena** — é aqui que uma cena fica de fora |
| `app/api/projects/[id]/postprocess` | interpola/upscala **o render inteiro** | **o passe final** que ele descreveu |
| `planEnhancement()` em `lib/render/postprocess.ts` | pula clipe já ≥58,5fps ou já no tamanho | impede processar duas vezes — rodar as duas rotas **não** compõe artefato |

**O regime decidido:**

1. Editar normalmente, com os clipes crus.
2. **Ao fechar a edição, interpolar para 60fps.**
3. **Cena que ficar ruim volta ao normal, sozinha** — o resto continua interpolado. A granularidade
   por clipe é o que a rota `enhance-clips` já dá.
4. **Registrar quais cenas foram excluídas e por quê.** É assim que a gente descobre o padrão (se é
   sempre movimento rápido, se é sempre criatura, se é sempre corte seco dentro do bloco).

**Duas coisas para vigiar, e nenhuma é motivo para não fazer:**

- 🔵 **Tempo, não crédito.** ~79s medidos para um clipe de 15s/480p com `minterpolate`, e o pool roda
  com concorrência 2. Para 20 blocos de 30s isso é ordem de **uma hora de CPU**. Não custa crédito,
  custa relógio — planejar como passe noturno, não como último clique antes de publicar.
- **Interação com "cortar o slow-motion" (`rubrica-aceitacao-take.md` §7).** As duas mexem na
  sensação de movimento em direções opostas: uma tira lentidão falsa, a outra suaviza. **Cortar o
  slow-motion PRIMEIRO, interpolar depois** — interpolar um trecho lento demais só deixa o defeito
  mais visível e mais fluido.

**Portão de saída:** depois do primeiro vídeo, registrar aqui quantas cenas precisaram ficar de fora.
Se for quase nenhuma, a interpolação vira automática. Se for muita, o motor é que está errado — e aí
a conversa é trocar o `minterpolate` por RIFE/neural, não desligar de novo.

---

**Ponte técnica que vale registrar:** o Studio é Remotion. O ambiente desta skill tem as skills
Remotion instaladas (`remotion-markup`, `transitions`, `display-captions`, `transcribe-captions`,
`silence-detection`, `remotion-render`, `video-editing`…). Quando o trabalho for mexer no Studio, elas
são a referência certa — não improvisar API de Remotion de memória.

Enquanto o Studio não tiver veredito real, o mapa de edição continua sendo entregue como documento de
orientação, agnóstico de ferramenta. Depois do primeiro vídeo montado nele, **reescrever as colunas
para casar com a interface real do Studio** — e, se fizer sentido, propor ao usuário que o Studio leia
o Documento 8 direto (ele é o dono do código; um formato JSON acordado entre a skill e o Studio
elimina a transcrição manual do mapa).

### Formato do Documento 8 (mantido até o Studio ser conhecido)

Entregável de orientação (a execução é manual, do usuário). Formato — uma linha por trecho:

| Tempo aprox. | Bloco/cena | Linha(s) de narração | Cue de trilha | SFX sugeridos | Nota |
|--------------|-----------|----------------------|---------------|---------------|------|

- A coluna de narração referencia as linhas do Documento 4 FINAL (pós-áudio real), não o rascunho
  1a — o rascunho serviu só para ajustar o texto antes de gerar; a partir daqui vale o áudio real.
- Como a narração é DISSOCIADA da imagem, o mapa só precisa de âncoras grossas (a voz não precisa
  bater em corte específico) — exceto: o nome da criatura dito pela 1ª vez deve coincidir com uma
  imagem forte da criatura (ou da sua iminência). Essa é a única sincronia obrigatória.
- SFX: específicos e diegéticos (madeira do cais rangendo, páginas viradas), nunca "efeito de tensão" genérico.
- O formato deste documento ainda NÃO foi validado pelo usuário — após o primeiro uso real, ajustar
  colunas conforme o que ele de fato usou no CapCut.

---

## 4. REGISTRO DE VEREDITOS (preencher conforme os testes)

- [x] Narração: Suno × ElevenLabs → vencedor: **ElevenLabs v3** (jul/2026, decisão do usuário;
      motivação: controle de entonação via audio tags, compatível com a marcação do Documento 1)
- [ ] Biblioteca de áudio do YouTube: quais climas da paleta do canal ela COBRE de fato, e quais
      obrigam a cair no Suno (preencher a cada mapa de trilha montado)
- [x] SFX: camada manual × áudio nativo → **DECIDIDO 03/09/2026: áudio nativo LIGADO** com trava
      positiva na seção `SOUND`; a camada manual vira reforço, não base (§2b)
- [ ] A trava positiva SEGURA a música? Contar em quantos blocos do 1º vídeo a música vazou mesmo
      com `no music, no score` acompanhado da afirmação positiva. Muito vazamento → decisão volta à mesa
- [ ] `generate_audio: true` encarece no HIGGSFIELD? (indício do Kairogen diz que não — confirmar)
- [ ] Interpolação 60fps: quantas cenas precisaram ficar de fora, e qual o padrão delas (§3b)
- [ ] Qual motor o Kairogen usa na interpolação — não localizado no catálogo do MCP
- [ ] Pesquisa de musicalidade por TIPO DE CENA e o "erro do exagero": **não apurou em 03/09**,
      refazer em perguntas curtas e separadas (a pergunta composta fragmentou a busca)
- [ ] Orçamento de narração em bloco de 30s: a constante de 33/15s escala linearmente para 66/30s?
      (hipótese, nunca medida — medir no primeiro vídeo com blocos de 30s)
- [ ] Paleta musical: quais cues funcionaram/falharam por tipo de cena
- [ ] Ducking e mixagem: valores reais usados
- [ ] Formato do Documento 8: colunas mantidas/removidas
- [ ] Rascunho de legendas com placement (1a, jul/2026): pendente de primeiro uso real — validar se
      a constante do orçamento de duração estima o encaixe com precisão suficiente para ser útil no
      planejamento, ou se precisa de ajuste depois do primeiro vídeo por esse fluxo.
