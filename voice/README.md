# ALPHA — assistente de voz do canal WhoIAm

Interface herdada do Mark-XXXIX, retematizada em violeta; ferramentas
focadas no pipeline do canal; dois motores de voz (um deles de custo zero).

## Rodar

Clique duplo em **`run.bat`** (ou `python main.py`). A janela abre com o
núcleo 3D ao centro; fale normalmente — em português.

## Dois motores de voz

O app escolhe sozinho ao abrir (`"engine": "auto"` no `config/api_keys.json`;
force com `"free"` ou `"realtime"`):

| | **GRATUITO** (padrão hoje) | **REALTIME** (OpenAI) |
|---|---|---|
| ouvir | Vosk offline, `models/pt-br` | OpenAI Realtime |
| pensar | Gemini (camada gratuita) | mesmo modelo da voz |
| falar | Maria pt-BR (SAPI do Windows) | voz neural |
| custo | **zero** | pago por minuto |
| exige | nada (Gemini só p/ frase livre) | saldo na OpenAI |

No modo gratuito **comece a frase com "Alpha"** ("Alpha, pesquisa a Quimera").
Sem a palavra de ativação ele ignora — senão transcreveria conversa do
ambiente e responderia sozinho. A conversa é por turnos, não fluida como a
Realtime: fale, espere a resposta, fale de novo.

O `auto` sonda o saldo da OpenAI com uma requisição de 1 token; sem saldo cai
no gratuito sem travar. Testar as três peças: `python test_free.py`.

## Visual

**Centro = núcleo 3D** (`scene/neural.html`): a rede neural bioelétrica em
Three.js do `style.txt` do canal, deslocada para violeta e sem o HUD próprio
(quem desenha HUD é a janela Qt em volta). Ela reage aos estados: quando o
ALPHA fala, o núcleo dispara impulsos; pensando, gira mais rápido; mudo,
o brilho cai. A ponte é `window.alphaState(modo, mudo)`, chamada pelo Python.

> Precisa de internet na primeira carga (o three.js vem de CDN); depois o
> QtWebEngine mantém em cache. Sem conexão e sem cache a cena mostra
> "NÚCLEO OFFLINE" em vez de ficar preta.
>
> A página é `file://`, e o QtWebEngine **bloqueia conteúdo remoto em página
> local por padrão** — por isso `NeuralScene` liga
> `LocalContentCanAccessRemoteUrls`. Sem esse atributo a cena não carrega.
> Para conferir se o núcleo está vivo: `python test_nucleo.py` (checa também
> se o canvas acompanha o redimensionamento — o widget Qt só ganha o tamanho
> final depois da carga, então a cena usa `ResizeObserver`, e `setSize` tem
> que atualizar o CSS do canvas: passar `false` ali prende a cena no tamanho
> inicial e ela fica num quadrado no canto).

A régua de comandos fica sempre visível no painel esquerdo (`_COMANDOS` em
`ui.py`) — ao mexer em `tools/local_commands.py`, atualize essa lista junto.

Painéis e textos usam a paleta violeta de `class C` (topo de `ui.py`), com
dourado e magenta de acento, mais scanlines e vinheta.

O `HudCanvas` clássico (rosto do canal em duotone violeta) continua no código
como reserva — `make_face.py` regenera esse rosto se você trocar o ícone.
Para fechar: feche a janela, ou diga "encerrar".

**A voz** precisa de saldo na conta OpenAI (platform.openai.com → Billing).
Sem saldo, a UI avisa e segue tentando reconectar a cada 60s — mas os
**comandos digitados abaixo continuam funcionando**, porque são 100% locais.

## Modo local — funciona sem créditos e sem internet

Digite no campo "COMMAND INPUT". `ajuda` lista tudo.

| Comando | O que faz |
|---|---|
| `projetos` | lista os projetos na tela |
| `dossie <criatura>` | exibe a pesquisa no centro da tela |
| `roteiro <criatura>` | exibe o roteiro de narração |
| `prompts <criatura>` | exibe os prompts (model sheets, storyboards, Seedance) |
| `video <criatura>` | toca o último render, dentro da própria janela |
| `analisar <criatura>` | monta o plano de edição |
| `renderizar <criatura>` / `short <criatura>` | dispara o render |
| `status` | progresso dos renders |
| `hud` | volta ao rosto do Alpha |

Qualquer texto que **não** seja um desses comandos é enviado ao modelo de voz
(e aí sim precisa de créditos).

## O que dá pra pedir por voz

- "Liste os projetos do estúdio"
- "Analisa o projeto da Medusa"
- "Renderiza o vídeo completo da Medusa" / "Faz um Short de 40 segundos"
- "Como está o render?"
- "Abre o projeto da Medusa no navegador"
- "Pesquisa a criatura Quimera" (dispara o Claude Code com a skill
  pesquisa-seres — CLI já instalado; falta apenas **fazer login uma vez**:
  abra um terminal, rode `claude`, e autentique com sua conta)
- "Gera o roteiro e os prompts da Quimera" (skill whoiam, fase producao)

Também dá pra digitar no campo de texto da janela em vez de falar.

## Testes

```
python test_local.py      # comandos locais — roda sem créditos
python test_headless.py   # voz + ferramentas — precisa de saldo na OpenAI
```

## Arquivos

- `main.py` — persona (INSTRUCTIONS), ferramentas, roteamento local→voz, boot
- `realtime_engine.py` — WebSocket Realtime GA, áudio 24kHz, barge-in
- `tools/local_commands.py` — comandos digitados, 100% offline
- `tools/studio.py` — ponte HTTP com o Alpha Studio (auto-inicia se offline)
- `tools/pipeline.py` — dispara Claude Code CLI (fases 0–2 do canal)
- `ui.py` — HUD PyQt6 do Mark + `ViewerPanel` (documentos e vídeo no centro)
- `config/api_keys.json` — chave OpenAI (local, não versionar)
