# PROPOSTAS — pesquisa e análise dos 6 pontos (2026-08-05)

> Resposta ao pedido de "pesquisar o que dá para fazer" antes de implementar.
> Nada aqui foi codificado ainda. Cada item diz: o que existe hoje, o que a
> pesquisa mostrou, o que eu recomendo, e o custo aproximado.
> Referências criadas junto: `EDICAO-MONTAGEM.md` e `TRILHA-SONORA.md`.

---

## A IDEIA CENTRAL — uma coisa destrava as outras cinco

Todos os seis pedidos esbarram na mesma pergunta: **em que segundo do vídeo
começa e termina cada bloco do roteiro?**

- filtro e trilha por cena → precisam saber onde a cena começa
- transição por cena → precisa saber onde é o limite
- legenda sincronizada → precisa saber onde cada frase é dita
- corte no lugar certo → precisa saber onde a ideia termina

Hoje o Studio **adivinha**: divide a narração em partes iguais e imanta o corte
na pausa mais próxima. Funciona, mas é um chute educado.

Nós temos o roteiro exato (`notes/roteiro.md`) e o áudio exato da narração.
Com **alinhamento forçado** (forced alignment: dá-se o texto conhecido + o
áudio, e o modelo devolve o tempo de cada palavra), obtém-se o tempo real de
cada bloco e de cada palavra — não é transcrição, é sincronização, e por isso é
muito mais preciso.

Um único passo de alinhamento gera, de uma vez:

1. `blocos.json` → limites reais de cena → **cortes certos** (substitui o chute)
2. `captions.json` → legendas em sincronia de palavra (itens 3 e 6 resolvidos)
3. os pontos de entrada/saída dos **cues musicais** (item 1)
4. os pontos onde a **transição** faz sentido (item 2)

**É por aqui que eu começaria.** Uma peça, quatro problemas.

Ferramenta: WhisperX (faster-whisper + wav2vec2 para alinhamento) ou Montreal
Forced Aligner. Roda local, de graça, com GPU NVIDIA. Ressalva honesta: há
relatos de que a precisão do WhisperX fica atrás do MFA em casos difíceis —
vale testar os dois com uma narração real antes de fixar.

---

## 1. FILTROS

**Hoje:** 6 presets de filtro CSS (`none`, `cinematic`, `warm`, `cold`, `noir`,
`vintage`), aplicados por clipe, iguais no preview e no render.

**O limite real:** filtro CSS não faz curvas, nem ajuste por canal, nem LUT.
E, mais importante, ele **estiliza** — não **iguala**. O problema de clipes
gerados em sessões diferentes não é falta de estilo, é falta de coerência.

### Recomendações, em ordem de valor

**1.1 — Grade em duas camadas (o que mais resolve).**
Uma **grade base do canal**, aplicada a TODOS os clipes de TODOS os vídeos
(contraste, saturação, leve dominante fria, vinheta suave) — é o que faz o
canal ter cara própria e o que mais disfarça a variação entre clipes. Por cima
dela, o **filtro de cena** atual, como acento. Custo: baixo (um campo novo no
`edit-plan.json` + um wrapper no Remotion).

**1.2 — Igualação automática de cor (color match).**
Medir a luminância/temperatura média de cada clipe (uma amostra de frames via
o ffprobe/ffmpeg que já vem embutido no Remotion, filtro `signalstats`) e
calcular a correção que puxa cada clipe para a média do vídeo. É o passo que
elimina o "clipe 7 está visivelmente mais amarelo". Custo: médio. **Alto valor
para o problema específico do canal.**

**1.3 — Filtros novos que valem a pena** (todos possíveis já com CSS + camadas):
- **vinheta** (foco de atenção; ótimo para terror)
- **grão de filme** (unifica clipes de origens diferentes — o grão cobre
  diferença de textura entre gerações)
- **halation/bloom** (brilho sangrando nas altas luzes — sonho, divino, fogo)
- **letterbox 2.39:1** (barras pretas; muda a percepção para "cinema" sem
  custo nenhum)
- **dessaturação seletiva** (mundo cinza, um elemento colorido)
- **aberração cromática sutil** (desconforto, alucinação)
- **light leaks** — o Remotion tem pacote próprio (`@remotion/light-leaks`)

**1.4 — O teto: LUTs e shaders.**
Para grade de verdade (LUT `.cube`, curvas, correção por canal), o caminho é o
sistema de efeitos WebGL do Remotion (`createEffect()`), que aceita shader
customizado. Isso abre grade profissional e efeitos que CSS não alcança.
Custo: alto. Recomendo só depois de 1.1 e 1.2 provarem valor.

**1.5 — Filtro por sequência, não por clipe.**
A mesma segmentação emocional que define os cues musicais deve definir o
filtro. Cena de tragédia inteira em `cold`, sequência de ação inteira em
`cinematic` quente. Vem de graça com o `scenes.json`.

---

## 1B. ÁUDIO E MÚSICA

Está tudo detalhado em **`TRILHA-SONORA.md`**. O resumo:

- Já existe um bom modelo dentro da skill `whoiam` (Documento 7 — mapa de
  trilha por sequência emocional, com paleta por tipo de cena e regra de
  ducking). O que falta é **transformar isso em dado que o Studio lê**, em vez
  de uma tabela para colar no CapCut.
- **Biblioteca local organizada por função emocional** (10 seções), com
  `catalogo.json` descrevendo cada faixa (duração, BPM, intensidade 0–5,
  instrumentação, fonte, licença). É isso que dá ao Alpha "noção do tipo de
  música que deve estar acontecendo".
- **Fonte mais segura para a base: YouTube Audio Library** — o próprio YouTube
  garante que não haverá reivindicação de Content ID. Pixabay como complemento.
  Evitar Free Music Archive para uso comercial. Para os 2–3 momentos-assinatura
  de cada vídeo, música gerada sob medida (ElevenLabs Music tem direitos
  comerciais completos e já será fornecedor da narração).
- **Silêncio é um tipo de cue.** O caso da transformação da Medusa está
  analisado no documento: cortar a música ~1s antes e deixar só o SFX é
  normalmente mais forte; a versão com música só ganha se a intenção for o
  desespero DELA em vez do horror do espectador.
- **Ducking sai de graça**: o `silences.json` que o Studio já gera permite
  calcular a curva de volume da música por frame dentro do Remotion — a música
  sobe nas pausas e desce quando a voz volta, igual no preview e no render.
- Fechar com `loudnorm` em −14 LUFS para todo vídeo do canal sair no mesmo volume.

---

## 2. TRANSIÇÕES

**Hoje:** um único tipo (`fade`) com a mesma duração em todos os limites.

**Estudo salvo em `EDICAO-MONTAGEM.md`** — Regra dos Seis do Walter Murch,
significado de cada transição, J/L-cut, ritmo por ato, e o que dá para
consertar na montagem quando os clipes não casam.

**A descoberta mais útil para o canal:** pela hierarquia de Murch, continuidade
espacial vale 4% e planaridade 5% — emoção, história e ritmo valem 84%. Ou
seja, **a inconsistência entre clipes gerados em sessões diferentes é um
problema de 16%**, e a montagem tem licença explícita para ignorá-la desde que
o ritmo esteja certo. Isso muda a prioridade: gastar esforço em ritmo e
igualação de cor, não em disfarçar corte.

**Proposta técnica:** transição por limite no `edit-plan.json`
(`{ tipo, duracaoEmFrames }`), escolhida a partir da relação de continuidade
declarada no `scenes.json`:

| Relação entre os clipes | Transição |
|---|---|
| ação contínua / mesma cena | corte seco (padrão) |
| salto de tempo curto | dissolve 12–20 frames |
| nova sequência ou capítulo | fade through black 20–30 frames |
| transformação/sobrenatural | `film-burn`, `dreamy-zoom`, `ripple`, `linear-blur` |
| formas parecidas nos dois clipes | match cut (corte seco alinhado) |

Boa notícia: o `@remotion/transitions` já instalado traz 18 apresentações
prontas (fade, slide, wipe, flip, iris, clock-wipe, dissolve, cross-zoom,
crosswarp, film-burn, linear-blur, zoom-blur, dreamy-zoom, book-flip, ripple,
swap, zoom-in-out, none). Não precisa escrever nenhuma — só expor.

**Extra barato e eficaz:** J/L-cut de SFX — deixar o som do clipe seguinte
entrar ~10 frames antes da imagem, ou o do anterior atravessar o corte. Amarra
clipes que visualmente não combinam.

---

## 3 e 6. LEGENDAS E SINCRONIZAÇÃO

São duas coisas diferentes, e a distinção importa:

| | **Vídeo longo (YouTube)** | **Shorts / Reels / TikTok** |
|---|---|---|
| Formato | faixa CC (.srt) enviada ao YouTube | legenda **queimada** no vídeo |
| Por quê | acessibilidade, SEO, o espectador liga/desliga, e permite tradução | assistido no mudo, autoplay; a plataforma renderiza UI própria e faixa CC não aparece de forma confiável |
| Onde entra | **na publicação**, não na edição | **na edição** (render do Short) |

Respondendo diretamente à sua dúvida: para o vídeo longo, a legenda **não é
feita na edição** — é um arquivo `.srt` enviado junto na publicação. Para os
Shorts, é o contrário: tem que estar dentro do vídeo.

**Sincronização (item 6):** resolvida pelo alinhamento forçado descrito no topo.
Como temos o roteiro exato, a sincronia fica de nível profissional, palavra a
palavra — e "bloco a bloco" vem de brinde. Detalhe importante: o YouTube
**descontinuou o parâmetro `sync` do `captions.insert`** em março/2024, ou seja,
se formos automatizar o envio, os tempos têm que vir prontos e corretos. O
auto-sync só existe na interface do Studio, na mão. Mais uma razão para o
alinhamento local.

**Regras de estilo de legenda (padrão de legendagem):** 32–42 caracteres por
linha, máximo 2 linhas, mínimo ~1s e máximo ~7s por bloco, velocidade de
leitura ~15–17 caracteres/segundo.

### Sobre os 3 canais (PT / EN / ES europeu) — uma sugestão que muda a estratégia

A pesquisa trouxe algo que vale considerar antes de abrir três canais: desde
2025 o YouTube liberou **faixas de áudio multi-idioma** (até 6 idiomas no
mesmo vídeo, o espectador troca no player), e criadores que sobem faixas
próprias relatam **25%+ do tempo de exibição vindo de idiomas não primários**,
sem republicar nada. A recomendação de mercado em 2026 virou "um canal, vários
idiomas" — **exceto** quando se quer marca localizada, thumbnail e texto na
tela traduzidos, e comunidade separada, que é justamente o caso de canais de
entretenimento.

Como você vai dublar com ElevenLabs de qualquer jeito, o mesmo ativo de áudio
serve às duas estratégias. Minha sugestão: **testar primeiro multi-áudio no
canal PT** (custo quase zero, mede a demanda real por idioma) e abrir canal
separado só para o idioma que provar audiência. Evita manter três canais
vazios. A decisão é sua — só não vale decidir sem saber que a opção existe.

Sobre tradução: traduzir o **roteiro**, não o `.srt` (qualidade muito melhor),
e depois realinhar cada idioma contra a narração dublada correspondente — os
tempos mudam entre idiomas, e o mesmo pipeline de alinhamento resolve.

---

## 4. O QUANTO O ALPHA ENTENDE HOJE (resposta honesta)

Fui ao código verificar em vez de estimar.

**O que ele tem hoje:** exatamente 3 ferramentas — `studio_control` (listar /
analisar / renderizar / status / abrir), `exibir` (mostrar dossiê, roteiro,
prompts ou vídeo na tela) e `pipeline_criatura` (disparar o Claude Code).

**O que ele consegue:** "Alpha, pesquisa a Quimera" e "gera o roteiro e os
prompts da Quimera" funcionam — mas apenas como dois botões grandes. A fase 0
e a fase 1–2 são chamadas fixas.

**O que ele NÃO consegue, e por quê:** "o storyboard 7 está com a mão errada,
refaz" é impossível hoje. O `pipeline.py` dispara `claude -p "<prompt fixo>"`,
espera até 30 minutos, e a sessão morre. Não há continuidade de conversa, não
há noção de bloco individual, não há como pedir correção. Cada disparo começa
do zero.

**O caminho para o que você quer** (3 mudanças, em ordem):

1. **Sessão persistente do Claude Code por criatura.** O CLI aceita retomar uma
   sessão. Com isso o Alpha deixa de ser "botão que dispara" e passa a ser a
   frente de conversa de uma sessão que já tem todo o contexto do projeto —
   e aí "refaz o painel 3 do bloco 7, a mão está errada" é só mais um turno.
   *Isto é o item que mais muda a experiência.*
2. **Um `projeto.json` de estado por criatura** — fase atual, blocos aprovados,
   pendências. A skill `whoiam` já trabalha em 4 fases com portões de aprovação;
   falta o Alpha saber em qual portão o projeto está. Sem isso ele não tem como
   responder "onde nós paramos?".
3. **Ferramentas mais finas** — hoje `pipeline_criatura` só aceita
   `pesquisa|producao`. Precisa de granularidade: model sheet de um personagem,
   storyboard de um bloco, revisão de um painel.

**Ponto prático:** como este computador não tem áudio, toda essa camada
conversacional pode ser construída e testada aqui **pelo campo de texto** da
janela do Alpha (o `COMMAND INPUT` já existe e já roteia texto → comando local
→ modelo). A voz é a mesma lógica com outro transporte. Ou seja: **o item 4 é
perfeitamente trabalhável nesta máquina**, e só a validação por voz fica para o
Windows.

---

## 5. ACESSOS E PUBLICAÇÃO — o que a pesquisa mostrou

| Plataforma | Situação real em 2026 | Custo | Veredito |
|---|---|---|---|
| **YouTube** | Data API v3, OAuth2 de app "computador". Upload custa 1600 de 10.000 unidades/dia → ~6 uploads/dia. Também cobre envio de legendas | grátis | **Comece por aqui.** Só falta o JSON de credenciais (passo a passo já está no `SUGESTOES.md`) |
| **Instagram** | Só conta **Business** ligada a Página do Facebook. Exige revisão de app da Meta (`instagram_business_content_publish`), com vídeo demonstrando o fluxo — **2 a 4 semanas**. Reels via API: **máx. 90s**. Limite de 25 posts/24h | grátis | Viável, mas com burocracia e o teto de 90s (Shorts maiores não passam) |
| **X (Twitter)** | **Não há mais tier gratuito para novos desenvolvedores** (desde fev/2026). Modelo pay-per-use: ~US$0,015 por post, **US$0,20 se o post tiver link**. Upload de mídia em 3 etapas (INIT/APPEND/FINALIZE) | pago, mas barato no nosso volume | Deixar por último; o custo por link é o detalhe que pega |
| **TikTok** | Já existe conector MCP com publicação direta no seu ambiente Claude | — | Caminho mais curto de todos, se quiser TikTok |

**Regras de segurança que eu recomendo fixar desde já:**

- Publicação **sempre** como privado/não listado primeiro; tornar público é
  ação sua, nunca do Alpha.
- Um log de auditoria (`publicacoes.json`) com o que foi enviado, quando e para
  onde — publicação é irreversível na prática.
- Uma confirmação explícita por publicação. "Alpha, publica" deve responder
  "subo como não listado, confirma?".

**Sobre acesso ao navegador:** priorizar API sempre que existir; navegador só
onde não há API. No Windows, o caminho realista para o Alpha é Playwright
(controle programático); a extensão Claude in Chrome serve para você e eu
trabalharmos, não para o Alpha rodar sozinho.

---

## PRIORIDADE SUGERIDA

| # | O quê | Por que primeiro | Custo |
|---|---|---|---|
| 1 | **Alinhamento forçado roteiro↔narração** (`blocos.json` + `captions.json`) | destrava cortes certos, legendas, cues e transições de uma vez | médio |
| 2 | **`scenes.json`** como contrato entre a skill `whoiam` e o Studio | é o "arquivo de orientação de cenas" que você pediu; sem ele, tudo continua manual | baixo |
| 3 | **Trilha no Studio**: biblioteca + catálogo + cue por cena + ducking automático | a música é o buraco maior do produto hoje | médio |
| 4 | **Grade base + igualação de cor** | resolve a inconsistência entre clipes melhor que qualquer transição | médio |
| 5 | **Transição por limite** (tipos já disponíveis no Remotion) | barato, e o estudo já está escrito | baixo |
| 6 | **Legendas queimadas no Short** + `.srt` para o longo | vem quase de graça depois do item 1 | baixo |
| 7 | **Sessão persistente do Claude Code no Alpha** | é o que transforma o Alpha em interlocutor de verdade | médio |
| 8 | **Publicação no YouTube** (não listado + confirmação) | depende só do OAuth JSON, que é ação sua | médio |

Itens 1, 2, 4, 5 e 6 são todos trabalháveis nesta máquina Linux. O item 7 dá
para construir e testar por texto aqui, e validar por voz no Windows.

---

## Fontes

- [Captions | YouTube Data API (Google for Developers)](https://developers.google.com/youtube/v3/docs/captions)
- [Add Multi-language features to your videos (YouTube Help)](https://support.google.com/youtube/answer/13338784?hl=en)
- [Multi-Language Audio Tracks or Separate Channels? (Linguana)](https://www.linguana.com/insights/the-smart-way-to-localize-on-youtube)
- [YouTube Shorts Caption & Subtitle Best Practices in 2026 (OpusClip)](https://www.opus.pro/blog/youtube-shorts-caption-subtitle-best-practices)
- [Open Captions vs. Closed Captions (BIGVU)](https://bigvu.tv/blog/open-captions-vs-closed-captions)
- [WhisperX — Whisper with Word-Level Timestamps (VexaScribe)](https://vexascribe.com/whisperx)
- [Word-level timestamps from WhisperX vs Montreal Forced Aligner (GitHub issue)](https://github.com/m-bain/whisperX/issues/1247)
- [Instagram Reels API: Complete Developer Guide 2026 (Phyllo)](https://www.getphyllo.com/post/a-complete-guide-to-the-instagram-reels-api)
- [Instagram Reels API Publishing Guide 2026 (Postproxy)](https://postproxy.dev/blog/instagram-reels-api-publishing-guide/)
- [X (Twitter) API Pricing in 2026: All Tiers (Postproxy)](https://postproxy.dev/blog/x-api-pricing-2026/)
- [X API Pricing in 2026: the new Pay-As-You-Go option (We Are Founders)](https://www.wearefounders.uk/the-x-api-price-hike-a-blow-to-indie-hackers/)
