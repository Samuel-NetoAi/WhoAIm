# Alpha Align — alinhamento forçado roteiro ↔ narração

Descobre **em que segundo cada bloco, fala e palavra do roteiro acontece na
narração**. Um passo só, quatro respostas: cortes de cena, entrada/saída dos
cues de trilha, limites de transição e legendas sincronizadas.

Antes disso o Studio dividia a narração em partes iguais e imantava o corte na
pausa mais próxima — chute educado. Aqui o tempo é medido.

## Rodar

```bash
# Windows (a máquina principal)
C:\Ai-Project\Alpha\voice\.venv\Scripts\python C:\Ai-Project\Alpha\align\alinhar.py ^
    --audio C:\Ai-Project\Criaturas\Medusa\medusa-video\public\audio\narracao.mp3 ^
    --roteiro C:\Ai-Project\Criaturas\Medusa\medusa-video\notes\roteiro.md ^
    --saida C:\Ai-Project\Criaturas\Medusa\medusa-video\analysis

# Linux
voice/.venv/bin/python align/alinhar.py --audio narracao.mp3 --roteiro roteiro.md
```

Usa o venv do Alpha porque o `vosk` já está instalado lá, junto com o modelo
pt-BR em `voice/models/pt-br` — nada novo para instalar em nenhuma das duas
máquinas. O ffmpeg é achado sozinho (sistema → `studio/bin` → binário embutido
do Remotion).

Depois da primeira execução, `--usar-cache` re-roda o alinhamento inteiro em
menos de um segundo, sem tocar no áudio. É assim que se ajusta o resultado.

## O que sai

| Arquivo | Para quê |
|---|---|
| `alignment.json` | palavras, falas e blocos com tempo e confiança; `cortes` = limites de cena para o Studio |
| `captions.pt.srt` | legendas prontas para subir no YouTube |
| `captions.json` | as mesmas legendas para o Studio/Remotion queimar no Short |
| `asr.json` | transcrição bruta (cache) |

E um relatório na tela: duração de cada bloco, confiança, e **quanto falta ou
sobra de clipe** — com clipes de 15s, um bloco de 22s de narração significa 7s
de frame congelado, e isso aparece antes de renderizar.

## Como funciona (e por que aguenta ASR ruim)

O texto final vem SEMPRE do roteiro. O reconhecimento de fala só empresta o
relógio — por isso um erro de transcrição nunca vira erro de legenda.

1. Roteiro e transcrição viram palavras normalizadas.
2. `SequenceMatcher` acha onde os dois concordam: cada palavra dessas é uma
   **âncora**, com tempo medido no áudio.
3. Âncoras incoerentes são descartadas — palavra curta e isolada ("de", "que")
   ou palavra que caiu longe da posição esperada no áudio.
4. O que sobra entre âncoras é interpolado por tamanho de palavra.
5. Cada fala e cada bloco recebem uma **confiança** = proporção de palavras
   ancoradas. É o número que diz onde olhar.

## Precisão medida

`python testes/simular_precisao.py <roteiro.md>` constrói uma narração
sintética a partir de um roteiro real (tempos conhecidos), simula um ASR com
taxa de acerto controlada e mede o erro. Com o roteiro do Dullahan (428
palavras):

| ASR acerta | erro mediano | p95 |
|---|---|---|
| 10% | 0,87s | 5,8s |
| 25% | 0,20s | 6,9s |
| 40% | 0,10s | 4,6s |
| 60% | 0,04s | 0,6s |
| 80% | 0,03s | 0,3s |

Acima de ~0,5s de erro a legenda começa a parecer fora de sincronia. Ou seja: a
partir de ~40% de acerto do ASR, a mediana já está muito abaixo do perceptível
— e o Vosk sobre narração neural do ElevenLabs deve ficar bem acima disso (no
teste com voz sintética ruim de propósito, ele fez 29%).

O filtro de coerência de posição (passo 3) é o que segura a cauda: sem ele, uma
única âncora casada com a ocorrência errada de uma palavra repetida levava o
erro mediano a **29 segundos** com transcrição ruim. Há teste de regressão.

## Quando a confiança está baixa

Confiança global abaixo de ~30% quer dizer que a maior parte do tempo foi
estimada, não medida. O que fazer, em ordem:

1. Conferir se o `roteiro.md` é mesmo o texto que foi narrado (bloco cortado na
   gravação é a causa mais comum).
2. Conferir os blocos marcados com ⚠ no relatório — o erro se concentra neles.
3. Trocar o motor de ASR (ver abaixo).

## Trocar o Vosk por algo melhor

O ASR está isolado em `alpha_align/asr.py`: qualquer motor serve, desde que
devolva uma lista de `PalavraASR`. O upgrade natural é **WhisperX**
(faster-whisper + wav2vec2), muito mais preciso e com GPU NVIDIA disponível na
máquina Windows. Depois de trocar, rodar `simular_precisao.py` de novo e
comparar a tabela acima — a decisão deve ser por número, não por impressão.

## Testes

```bash
voice/.venv/bin/python -m unittest discover -s testes -t .   # 40 testes, sem áudio
```

Os testes de alinhamento simulam o ASR de propósito: é o que permite reproduzir
transcrição incompleta, palavra trocada e âncora deslocada de forma
determinística.
