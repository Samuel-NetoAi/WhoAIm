# PLANO ALPHA — Central de Produção do Canal (o "Jarvis" do canal)

> Documento-mestre. Se os créditos acabarem no meio da execução, qualquer sessão
> futura do Claude (ou você mesmo) consegue continuar daqui. Cada fase diz o que
> é, por que, como fazer, e como verificar que ficou pronto.
> Última atualização: 2026-08-03.

## Visão geral

O canal opera em 5 fases:

| Fase | O quê | Ferramenta hoje | Onde fica |
|------|-------|-----------------|-----------|
| 0 — Pesquisa | Dossiê da criatura/personagem | skill `pesquisa-seres` | conversa do Claude (não persistido) → **centralizar em `notes/dossie.md` do projeto** |
| 1 — Cenas | Descrição cinematográfica das cenas | skill `whoiam` | conversa → **centralizar em `notes/roteiro.md`** |
| 2 — Prompts | Model sheets → storyboards → prompts SeeDance | skill `whoiam` | conversa → **centralizar em `notes/prompts.md`** |
| Final — Narração | ElevenLabs v3 com tags de entonação | manual | `public/audio/` do projeto |
| **Nova: Edição** | Sincronizar clipes + narração, Shorts, filtros, pós-processamento | **Alpha Studio** (`C:\Ai-Project\Alpha\studio`) | esta pasta |

## Documentos de referência (2026-08-05)

- `docs/EDICAO-MONTAGEM.md` — gramática de edição do canal: quando cortar,
  quando dissolver, ritmo por ato, o que fazer quando os clipes não casam.
- `docs/TRILHA-SONORA.md` — como a música de cada cena é decidida: cue por
  sequência emocional, silêncio como escolha, biblioteca por função,
  níveis de mixagem.
- `docs/PROPOSTAS-2026-08-05.md` — pesquisa dos 6 pedidos (filtros, transições,
  legendas, conversa do Alpha, publicação) com prioridade e custo.
- `DIARIO/` — o que mudou em cada dia de trabalho, para sincronizar as duas
  máquinas.

## Layout de pastas (alvo)

```
C:\Ai-Project\
├── Alpha\                        ← CENTRO DE TUDO
│   ├── PLANO-ALPHA.md            ← este documento
│   ├── SUGESTOES.md              ← caminhos não tomados, para você decidir depois
│   ├── studio\                   ← o app web (Next.js + Remotion), movido de Criaturas\RemotionSkill
│   ├── align\                    ← alinhamento roteiro↔narração (cortes, cues, legendas)
│   ├── docs\                     ← referências de edição, trilha e propostas
│   └── Mark-XXXIX-OR-main\       ← referência de agente Python (fase futura, NÃO integrado ainda)
├── Criaturas\<Nome>\             ← um projeto por criatura
│   └── <nome>-video\             ← projeto reconhecido pelo Studio
│       ├── public\videos\        ← clipes numerados (1.mp4, 2.mp4, …)
│       ├── public\audio\         ← narração
│       ├── notes\                ← dossiê/roteiro/prompts (Fases 0–2 persistidas)
│       ├── edit-plan.json        ← plano de edição (gerado/editado no Studio)
│       ├── analysis\             ← probe.json, silences.json
│       └── renders\              ← saídas (full-*.mp4, short-*.mp4, *-post.mp4)
└── Animes\<Nome>\                ← mesmo formato para personagens de anime
```

O Studio escaneia `Criaturas\` e `Animes\` automaticamente. Uma pasta vira
"projeto" quando tem `public\videos\` ou `public\audio\`. Para criaturas
antigas com estrutura solta (ex.: Sobek com PNGs soltos, Cthullhu com
`VideoSeeDance1\`), basta criar `<Nome>\<nome>-video\public\videos\` e copiar
os clipes numerados pra lá.

## Status das fases de implementação

### ✅ FEITO (sessões anteriores + esta)
- [x] Studio: upload de zip + narração, análise de durações (mediabunny)
- [x] Detecção de silêncio adaptativa (ffmpeg loudnorm + silencedetect, embutido no Remotion — nada pra instalar)
- [x] Cortes "imantados" nas pausas da narração (smart plan) com fallback pra divisão igual
- [x] Timeline visual com cortes arrastáveis + marcadores de pausa
- [x] Áudio por cena: mix (som do clipe baixo sob narração) / substitui / mudo
- [x] Render completo + Short com alvo de duração configurável (corta só em pausas)
- [x] Congelar-último-frame + zoom Ken Burns quando o clipe é mais curto que a fatia (nunca repetir clipe)
- [x] Mover Studio para `Alpha\studio` e escanear `Criaturas\` + `Animes\`
- [x] Filtros visuais por cena (cinematográfico, quente, frio, noir, vintage) — ver seção Filtros
- [x] Pós-processamento: interpolação de frames (30→60fps) e upscale 2x — ver seção Pós-processamento
- [x] Botão de download dos renders
- [x] Aba Notas (dossiê/roteiro/prompts) por projeto — Fases 0–2 persistidas junto do projeto
- [x] **Alinhamento forçado roteiro↔narração** (`Alpha\align`) — os cortes passam a ser medidos, não estimados; sai também legenda sincronizada
- [x] **Resolução de saída desacoplada dos clipes** — clipes 480p renderizam em 1080p (mínimo 1080 no lado curto, nunca reduz)
- [x] **`scenes.json` lido pelo Studio** — filtro e transição por cena vindos da skill `whoiam`
- [x] **Transição por limite** — 7 presets, todos verificados em render real
- [x] **Trilha musical** — biblioteca em `Trilhas\` com `catalogo.json`, cue por sequência emocional vindo do `scenes.json`, ducking por frame calculado das pausas da narração, `SILENCIO` como cue de verdade

## Identidade visual do assistente (2026-08-04)

O assistente se chama **ALPHA** (não mais "Jarvis") — renomeado em todo o
código, título da janela (`A.L.P.H.A — WhoIAm`), badges e rodapé.
Tema violeta baseado no `Alpha\style.txt` do Samuel: primário `#b57bff`,
dourado `#ffaa00` para atividade, magenta `#ff00aa` para alerta/mudo, fundo
`#050208`, mais scanlines + vinheta (`_draw_crt_overlay` em `ui.py`).
**Centro da janela = núcleo 3D real** (`voice\scene\neural.html`): a cena
Three.js do `style.txt` (rede neural bioelétrica, shaders + bloom), em
violeta e sem o HUD próprio dela. Embutida via `QWebEngineView`
(`NeuralScene` em `ui.py`); reage aos estados por
`window.alphaState(modo, mudo)` — falando dispara impulsos, pensando acelera
a rotação, mudo baixa o bloom. Carrega three.js de CDN: sem internet mostra
"NÚCLEO OFFLINE" (fallback já tratado). Requer `PyQt6-WebEngine`.
O `HudCanvas` (rosto do canal em duotone violeta, `voice\make_face.py`)
continua como reserva no stack.
**Toda a paleta vive em `class C` no topo de `voice\ui.py`** — mexer só ali.

## FASE VOZ (em execução 2026-08-03) — "Alpha Voice"

Decisão aprovada pelo Samuel: motor de voz = **OpenAI Realtime API** (rota 2), porque
a conta Gemini dele não tem acesso ao Live API (testado) e a chave OpenAI tem
`gpt-realtime` disponível (testado). Arquitetura:
- `Alpha\voice\` — app novo. `ui.py` copiado do Mark (rosto/HUD PyQt6, intacto);
  `main.py` novo: WebSocket direto na Realtime API (`wss://api.openai.com/v1/realtime`),
  áudio PCM16 24kHz via sounddevice, server VAD, barge-in (limpar fila ao detectar fala).
- Ferramentas por voz focadas no canal: `studio_control` (listar projetos, analisar,
  renderizar full/short, status, pós-processar — chama a API HTTP do Studio na porta 3001,
  iniciando o Studio via npm se estiver offline) e `pipeline_criatura` (dispara
  Claude Code CLI com as skills pesquisa-seres/whoiam; se o CLI não estiver no PATH,
  responde explicando como instalar: `npm install -g @anthropic-ai/claude-code`).
- Config: `voice\config\api_keys.json` (openai_api_key; gemini fica pro Mark).
- Teste sem microfone: `voice\test_headless.py` valida conexão, sessão, tool-call
  round-trip com o Studio real e resposta — dá pra rodar sempre que algo mudar.
- O Mark original continua intocado como referência.

**Convenção crítica de caminhos:** as notas (dossiê/roteiro/prompts) vivem em
`Criaturas\<Nome>\<slug>-video\notes\` — o `-video` no meio é obrigatório,
é onde o Studio procura. `pipeline.py` replica o `slugify` do
`create-project.ts` para os dois lados baterem (verificado com round-trip:
grava pelo pipeline, lê pela API do Studio).

**Claude Code CLI:** instalado globalmente em 2026-08-03 (v2.1.221, em
`%APPDATA%\npm\claude.CMD`). Falta apenas o **login interativo** (rodar
`claude` num terminal uma vez) — `pipeline.py` já detecta esse estado e
avisa em português por voz em vez de dar erro cru.

**Painel de exibição + modo local (2026-08-03):** o centro da janela virou um
`QStackedWidget` (HUD ↔ `ViewerPanel`). O ViewerPanel exibe markdown
(`QTextEdit.setMarkdown`) e reproduz vídeo (`QtMultimedia`, disponível no
PyQt6 instalado) — dossiê, roteiro, prompts e o render final aparecem dentro
do Jarvis, sem ir ao navegador. `tools/local_commands.py` dá comandos
digitados que rodam **sem OpenAI** (ler notas, listar projetos, tocar vídeo,
disparar render via Studio local): `main.py` tenta o comando local primeiro e
só repassa ao modelo de voz o que não reconhecer. Testado com
`test_local.py` (8 casos, 0 falhas, dados reais) e construção da UI em
`QT_QPA_PLATFORM=offscreen`.

**MOTOR GRATUITO (2026-08-04) — o ALPHA já funciona sem gastar nada.**
`voice\free_engine.py`: ouvidos = **Vosk** offline (modelo pt-BR de 52MB em
`voice\models\pt-br`), cérebro = **Gemini** (chave do Samuel, camada
gratuita, só para frases que não são comando local), voz = **Maria pt-BR**
do SAPI do Windows via pyttsx3 (offline). Palavra de ativação: "Alpha".
`main.py` escolhe o motor (`engine: auto|free|realtime` no config) sondando o
saldo da OpenAI com uma requisição de 1 token. Testar: `python test_free.py`.
Limitação: conversa por turnos, sem interrupção, qualidade abaixo da
Realtime — é a ponte até haver saldo na OpenAI.

**STATUS (2026-08-03, fim da sessão):** app construído e de pé — janela abre,
protocolo GA aceito pelo servidor (o shape beta foi rejeitado com
`beta_api_shape_disabled` e o código já usa GA), reconexão resiliente.
**BLOQUEIO EXTERNO:** a conta OpenAI do Samuel está `insufficient_quota`
(sem saldo — confirmado até em chat de 3 tokens). Ao adicionar créditos em
platform.openai.com → Billing, rodar `python voice\test_headless.py`; se
passar, `run.bat` e falar. Pode haver 1-2 ajustes finos pós-quota (ex.: nome
da voz "cedar", nomes de eventos de transcrição) — o teste headless aponta.

## Design da interface (2026-08-03)

Tema escuro **deliberado** (fixo, não segue o SO) em `app/globals.css`, com
tokens CSS. Antes o app herdava o dark automático do navegador e usava
controles sem estilo — os botões ficavam ilegíveis (queixa do Samuel).
Contrastes medidos no navegador após a mudança: primário 9.5:1, normal
14.2:1, select 12.6:1, títulos/hints 7.7:1, desabilitado 5.3:1 — todos acima
do mínimo AA (4.5:1). Acento dourado `#e8b84b` (temática do canal).
Ao mexer em cor, **medir de novo** (script de contraste no histórico) em vez
de confiar no olho.

## Regra de ouro do material: quantos clipes por vídeo

O congelamento de frame só existe para cobrir **falta de material**. Fórmula:
`clipes necessários = duração da narração ÷ duração de cada clipe`.
Medusa (protótipo): 305s de narração ÷ ~15s por clipe = **21 clipes** para
zero congelamento. Com 14 clipes, 107.8s (35% do vídeo) são frame congelado.
Repassar isso ao Samuel sempre que ele for gerar material novo.

### ⏳ PRÓXIMOS PASSOS (em ordem de valor; qualquer sessão pode pegar daqui)
1. **Migrar criaturas antigas pro formato padrão** — criar `<nome>-video\public\videos\` em BabaYaga, Cthullhu, Sobek etc. e copiar/renomear clipes pra `1.mp4, 2.mp4…`. Mecânico; dá pra pedir pro Claude fazer em lote ("padroniza as pastas de Criaturas pro formato do Studio").
2. **Upscale com IA (Real-ESRGAN)** — o upscale atual é lanczos (nítido, mas não "inventa" detalhe). Real-ESRGAN roda local com binário pronto: baixar release `realesrgan-ncnn-vulkan` (Windows), colocar em `Alpha\studio\bin\`, e no `postprocess/route.ts` trocar o passo de scale por chamada ao binário quando `upscaleMode === "ai"`. GPU NVIDIA presente → viável.
3. **Interpolação com IA (RIFE)** — mesmo padrão: binário `rife-ncnn-vulkan` em `bin\`, passo alternativo ao minterpolate. Muito melhor em cenas de ação.
4. **Legendas automáticas** — skill `transcribe-captions` (Whisper.cpp) já existe no ambiente; gerar `captions.json` na análise e desenhar legendas TikTok-style no Short (skill `display-captions`). Alto valor pra Shorts.
5. **Página "Nova criatura"** — formulário que cria a pasta inteira (`Criaturas\<Nome>\<nome>-video\{public\videos,public\audio,notes}`) e já abre as Notas pra colar o dossiê.
6. **Fila de renders** — hoje 1 render por vez por alvo; trocar job-store por fila simples (p-queue) pra enfileirar full+short+post de vários projetos.
7. **Integração Mark-XXXIX (voz/desktop)** — fase à parte. O Mark é Python+OpenRouter (voz, controle de desktop). Caminho realista: expor o Studio via API local (já é HTTP) e o Mark chamar essas rotas por voz ("Mark, renderiza o short da Medusa"). NÃO misturar os códigos; integrar por HTTP.

## Como rodar o Studio

```bash
npm --prefix C:\Ai-Project\Alpha\studio run dev -- -p 3001
```
Abrir http://localhost:3001. (O `.claude\launch.json` da pasta Alpha já tem a
entrada `alpha-studio` pra preview integrado.)

## Decisões técnicas já tomadas (e por quê)

- **Remotion como motor** — edição = código React parametrizado por `edit-plan.json`; preview no navegador é o mesmo código do render final.
- **ffmpeg via `npx remotion ffmpeg`** — binário embutido do Remotion; zero instalação no sistema.
- **Cortes por silêncio, não por transcrição** — os clipes não têm fala própria; a narração manda. Transcrição (Whisper) só será necessária pra legendas.
- **Nunca repetir clipe (loop)** — parece vídeo duplicado. Clipe curto → congela último frame + zoom lento.
- **`edit-plan.json` é a fonte de verdade** — todo ajuste manual vive nele; o render lê ele; regenerar análise sobrescreve (botão "Resetar").
- **IDs de projeto** = base64(caminho relativo a `C:\Ai-Project`), ex. `Criaturas/Medusa/medusa-video`. Compatível com caminhos de 2 ou 3 níveis.

## Filtros (implementado)

Por cena, no `edit-plan.json` (`clips[].filter`) e na UI. Presets (CSS filters
aplicados no Remotion, valem no preview e no render):
`none` · `cinematic` (contraste+saturação leve) · `warm` (dourado) ·
`cold` (azulado) · `noir` (P&B contrastado) · `vintage` (sépia suave).
Adicionar preset novo = 1 linha em `remotion/filters.ts`.

## Pós-processamento (implementado)

Depois de um render pronto, a UI oferece:
- **60 fps** — `minterpolate` (interpolação por movimento, CPU; ~lento: minutos para vídeo de 5min)
- **Upscale 2x** — `scale=iw*2:ih*2:flags=lanczos` (rápido, nítido)
- Os dois combinados. Sai como `renders\<original>-post.mp4`, com botão de download.
Upgrade futuro: RIFE/Real-ESRGAN (ver Próximos passos 2–3).

## O que NÃO foi feito de propósito (ver SUGESTOES.md)

Resumo: banco de dados (JSON em disco basta), autenticação (app local),
publicação automática TikTok/YouTube (existe MCP pra isso — decisão sua),
geração de vídeo/imagem dentro do Studio (APIs pagas — melhor decidir com calma),
integração de voz do Mark (fase própria).
