# OMEGA — assistente de voz do canal WhoIAm

Interface herdada do Mark-XXXIX, retematizada em violeta; ferramentas
focadas no pipeline do canal; dois motores de voz (um deles de custo zero).

## Rodar

**Windows:** clique duplo em **`run.bat`** (ou `python main.py`). A janela abre
com o núcleo 3D ao centro; fale normalmente — em português.

**Linux:** `export AI_PROJECT_ROOT=~/Ai-Project && ./run.sh`. Sem microfone a
janela abre em **MODO DIGITADO** e o campo de comando funciona igual — digite
`diagnostico` para ver o que esta máquina tem e o que falta.

## Dois motores de voz

O app escolhe sozinho ao abrir (`"engine": "auto"` no `config/api_keys.json`;
force com `"free"` ou `"realtime"`):

| | **GRATUITO** (padrão hoje) | **REALTIME** (OpenAI) |
|---|---|---|
| ouvir | Vosk offline, `models/pt-br` | OpenAI Realtime |
| pensar | Gemini (camada gratuita) | mesmo modelo da voz |
| falar | Maria pt-BR (SAPI do Windows) | voz neural |
| ferramentas | **sim** (function calling do Gemini) | sim |
| custo | **zero** | pago por minuto |
| exige | nada (Gemini só p/ frase livre) | saldo na OpenAI |

> As duas rotas usam a MESMA lista de ferramentas (`TOOLS` em `main.py`). Até
> ago/2026 o motor gratuito recebia o executor e nunca o chamava: o Gemini
> conversava e respondia como se tivesse executado. Corrigido — agora ele chama
> a ferramenta de verdade e o resultado volta para ele antes da resposta final.

No modo gratuito **comece a frase com "Omega"** ("Omega, pesquisa a Quimera").
Sem a palavra de ativação ele ignora — senão transcreveria conversa do
ambiente e responderia sozinho. A conversa é por turnos, não fluida como a
Realtime: fale, espere a resposta, fale de novo.

O `auto` sonda o saldo da OpenAI com uma requisição de 1 token; sem saldo cai
no gratuito sem travar. Testar as três peças: `python test_free.py`.

## Visual

**Centro = núcleo 3D** (`scene/neural.html`): a rede neural bioelétrica em
Three.js do `style.txt` do canal, deslocada para violeta e sem o HUD próprio
(quem desenha HUD é a janela Qt em volta). Ela reage aos estados: quando o
OMEGA fala, o núcleo dispara impulsos; pensando, gira mais rápido; mudo,
o brilho cai. A ponte é `window.omegaState(modo, mudo)`, chamada pelo Python.

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

## Duas palmas trazem a janela de volta

Com o OMEGA rodando, bata **duas palmas** (intervalo de 0,12 s a 0,7 s): ele
desminimiza, entra em tela cheia e ganha o foco.

**O que ele NÃO faz — e não tem como fazer:** abrir o app fechado. Alguém
precisa estar ouvindo o microfone para escutar a palma, e esse alguém é o
próprio OMEGA. Nos vídeos em que isso aparece, o assistente já estava rodando.
Para ele estar sempre disponível, deixe-o aberto e minimizado (ou no início
automático do sistema).

Detalhes que importam:

- escuta o **mesmo fluxo** do Vosk — nenhuma segunda captura do microfone;
- funciona **mesmo com o microfone mudo**, que é o ponto: o OMEGA não fica
  transcrevendo a sala, mas continua atendendo ao chamado;
- é DSP puro em `clap.py`, sem numpy (que não está no venv) e sem `audioop`
  (removido no Python 3.13). Custa ~0,03 s por 10 s de áudio;
- o que separa palma de voz alta é o **decaimento**, não o volume: a palma
  desaba abaixo de 35% do pico em 120 ms, um grito não.

Se disparar sozinho (porta batendo) ou não disparar (microfone fraco), o ajuste
é `FATOR_DE_PICO` e `PISO_ABSOLUTO` no topo de `clap.py`. Os testes usam áudio
sintético — `python -m unittest test_palmas` — mas a calibração fina só sai com
o seu microfone e a sua sala.

## Modo local — funciona sem créditos e sem internet

Digite no campo "COMMAND INPUT". `ajuda` lista tudo.

| Comando | O que faz |
|---|---|
| `diagnostico` | o que esta máquina tem e o que falta (CLI, Studio, modelo, trilhas) |
| `projetos` | lista os projetos na tela |
| `dossie <criatura>` | exibe a pesquisa no centro da tela |
| `roteiro <criatura>` | exibe o roteiro de narração |
| `prompts <criatura>` | exibe os prompts (model sheets, storyboards, Seedance) |
| `video <criatura>` | toca o último render, dentro da própria janela |
| `analisar <criatura>` | monta o plano de edição |
| `renderizar <criatura>` / `short <criatura>` | dispara o render |
| `status` | progresso dos renders |
| `pesquisar <criatura>` | **dispara o Claude Code** com a skill `pesquisa-seres` (fase 0) |
| `produzir <criatura>` | **dispara o Claude Code** com a skill `whoiam` (fases 1–2) |
| `pipeline` | andamento da pesquisa/produção em curso |
| `hud` | volta ao rosto do Omega |

**Substantivo lê, verbo age:** `dossie X` mostra a pesquisa que já existe;
`pesquisar X` produz uma nova. Confundir os dois fazia parecer que a pesquisa
tinha falhado quando ela nunca havia começado.

`pesquisar` e `produzir` levam minutos e exigem o **Claude Code instalado e
logado** nesta máquina — sem isso, o OMEGA diz exatamente o que falta.

## Avisos ativos — o OMEGA fala sem ser perguntado

Tarefas longas não ficam mais em silêncio esperando um "status":

| Quando | O que acontece |
|---|---|
| a cada 2 min de pesquisa/produção | linha no log: "ainda trabalhando na pesquisa de X — 4 minutos até agora" |
| pesquisa/produção termina | **fala**: o que gravou, em qual arquivo, e que já aparece no Studio |
| a cada 25% de um render | linha no log: "vídeo completo de X: 50 por cento" |
| render termina | **fala**: nome do arquivo + "diga 'video X' para assistir aqui" |
| qualquer um falha | **fala** o erro |

Batimento de progresso fica só no log de propósito: ouvir "ainda pesquisando" a
cada dois minutos cansa mais do que informa.

**Detalhe que evita mentira:** se o Claude terminar com código de sucesso mas
não gravar os arquivos esperados, o OMEGA diz isso — não "concluído". Esse caso
só se descobriria abrindo a aba Notas e achando-a vazia.

O canal vive em `tools/notify.py`; o `main.py` o liga na janela
(`ligar_avisos`). Sem notificador registrado — testes, headless — as mensagens
somem em silêncio e nunca derrubam a tarefa que avisa.

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
python test_local.py                     # comandos locais — roda sem créditos
python -m unittest test_pesquisa -v      # pesquisa/produção: comando e ferramenta
python -m unittest test_avisos -v        # avisos de progresso e conclusão
python -m unittest test_palmas -v        # gesto de palmas, com áudio sintético
python test_headless.py                  # voz Realtime — precisa de saldo na OpenAI
```

`test_pesquisa.py` roda sem áudio, sem crédito e sem internet: ele simula as
respostas do Gemini para provar que a ferramenta é de fato executada e que o
resultado dela volta ao modelo.

## Arquivos

- `main.py` — persona (INSTRUCTIONS), ferramentas, roteamento local→voz, boot
- `realtime_engine.py` — WebSocket Realtime GA, áudio 24kHz, barge-in
- `tools/local_commands.py` — comandos digitados, 100% offline
- `tools/studio.py` — ponte HTTP com o Alpha Studio (auto-inicia se offline)
- `tools/pipeline.py` — dispara Claude Code CLI (fases 0–2 do canal)
- `tools/notify.py` — canal de aviso ativo (progresso e conclusão)
- `clap.py` — detector de palmas sobre o fluxo de áudio existente
- `ui.py` — HUD PyQt6 do Mark + `ViewerPanel` (documentos e vídeo no centro)
- `config/api_keys.json` — chave OpenAI (local, não versionar)

## Reconhecimento de fala (Whisper)

O Vosk foi substituído: mesmo com o modelo grande ele errava demais em
português — "Ômega" virava "amiga", "IT A Coisa" virava "e tinha coice",
"e a colonizar", "doente". Nenhuma camada de correção conserta isso.

Hoje usa **faster-whisper** local, `small`, na GPU (RTX 3050): ~0,05 s por
frase contra ~1,6 s na CPU. Cai para CPU sozinho se a GPU não estiver
disponível.

- As DLLs de CUDA vêm dos pacotes pip `nvidia-cublas-cu12` / `nvidia-cudnn-cu12`
  e **precisam entrar no PATH antes** do ctranslate2 carregar — é o que
  `tools/transcritor.py::_preparar_cuda` faz. Sem isso: `cublas64_12.dll not found`.
- O Whisper é por trecho, não contínuo: `DetectorDeFala` acumula áudio
  enquanto há voz e transcreve quando o silêncio fecha a frase.
- Ajustes finos em `tools/transcritor.py`: `LIMIAR_VOZ` (sobe se disparar
  com ruído), `SILENCIO_FIM` (sobe se cortar no meio da frase).

O modelo Vosk continua em `models/pt-br` como reserva, mas não é mais usado.
