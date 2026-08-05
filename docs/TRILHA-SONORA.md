# TRILHA SONORA — como o Alpha decide a música de cada cena

> Base de referência para a camada musical do WhoIAm. Os clipes do SeeDance
> saem **sem música, só com efeitos sonoros diegéticos** (decisão jul/2026,
> registrada na skill `whoiam`) justamente para que a trilha seja decidida
> aqui, de forma holística, olhando o vídeo inteiro.
> Criado 2026-08-05. Itens marcados **PONTO DE PARTIDA** ainda não foram
> validados em vídeo publicado.

---

## 1. O modelo: cue por sequência emocional, não por bloco

Na indústria isso se chama **spotting session**: antes de compor, diretor e
compositor assistem ao filme e decidem, cena a cena, onde a música entra, onde
sai, e — o mais importante — **onde ela não deve existir**. Cada trecho com
música é um **cue**, com ponto de entrada, ponto de saída e uma função.

A pergunta de cada cue é sempre a mesma:

> **"O que esta música está fazendo pela história?"**

Se a resposta for "preenchendo silêncio", o cue não deveria existir.

Duas regras estruturais que já são decisão do canal e continuam valendo:

- **A música segue a SEQUÊNCIA EMOCIONAL, não o bloco.** Um cue cobre vários
  blocos consecutivos do mesmo clima e só troca quando a atmosfera vira.
- **Sempre instrumental.** Se houver voz, que seja vocalise/textura (sem
  palavras concretas) — reduz risco de reivindicação e não briga com a narração.

### Os quatro tipos de cue

| Tipo | O que é | Quando |
|---|---|---|
| `MUSICA` | cue normal, música sob a narração | maioria das sequências |
| `SILENCIO` | ausência deliberada de música (só SFX + narração) | quando a imagem ou a narração já carregam a emoção sozinhas |
| `STINGER` | acento curto (2–4s), sem cue contínuo | impacto, revelação, susto |
| `DRONE` | textura sem melodia nem pulso | tensão latente, lore, ambientação longa |

**O silêncio é uma escolha musical, não a falta de uma.** No exemplo da
transformação da Medusa: cortar a música exatamente no início da transformação
e deixar só o som da carne/escamas/serpentes é quase sempre mais forte do que
um cue de terror — a queda súbita de densidade sonora faz o espectador se
inclinar para a tela. A versão com música funciona se a intenção for o
DESESPERO DELA (subjetivo, cordas agudas em fricção) em vez do HORROR DO
ESPECTADOR (objetivo, silêncio + SFX).
Regra prática: **corte a música um pouco antes do momento, não no momento** —
a ausência precisa de ~1s para ser percebida como escolha.

E o oposto também vale: música que **atravessa** um corte de imagem amarra dois
clipes que não combinam visualmente (ver `EDICAO-MONTAGEM.md`, seção 3). Nunca
faça o cue começar e terminar exatamente no mesmo frame de um corte de imagem —
isso denuncia a montagem.

---

## 2. Paleta emocional — as seções da biblioteca

A biblioteca deve ser organizada **por função emocional**, não por gênero. É
assim que se acha a música certa em 10 segundos durante a edição.

| Seção | Instrumentação/caráter | Cenas típicas |
|---|---|---|
| `01-misterio` | drones graves, cordas sustentadas, piano esparso, pulso lento | investigação, abertura de lore, "ninguém sabe de onde veio" |
| `02-tragedia` | violoncelo solo, piano menor, cordas lentas | Medusa, Sereia — vítima, injustiça, luto |
| `03-terror` | sub-bass, clusters dissonantes de metais, texturas metálicas, crescendo glacial | revelação do monstro, horror cósmico |
| `04-acao` | ostinato de cordas, percussão acelerada, sforzandos nos impactos, guitarra/rock híbrido | Minotauro × Teseu, perseguição, luta |
| `05-epico` | metais nobres, cordas amplas, percussão orquestral | Zeus, entrada de divindade, escala colossal |
| `06-nordico-folk` | taiko/bombo, trompas, cordas friccionadas, instrumentos étnicos | Jormungandr, mitologias regionais |
| `07-contemplativo` | pads amplos, harpa/piano, dinâmica baixa | abertura, encerramento, respiro entre atos |
| `08-folclore-br` | viola/violão atmosférico, percussão orgânica, texturas de mata | Boi Tatá, Curupira, folclore |
| `09-stingers` | acentos curtos, hits, risers, impactos | pontuação, revelações |
| `10-drones` | texturas puras sem pulso | camada de base sob qualquer cena |

Sobre o exemplo do Minotauro: a luta final pede `04-acao` com batida marcada
(percussão + guitarra grave), e o vídeo inteiro **não** deve ter sido esse
clima — é exatamente o contraste com `01-misterio`/`03-terror` do labirinto que
faz a luta explodir. Cue novo, não continuação. E a entrada do cue de ação deve
cair no primeiro golpe, não antes.

### Estrutura de pastas

```
C:\Ai-Project\Trilhas\
├── catalogo.json           ← GERADO pelo script; índice lido pelo Studio
├── LEIA-ME.md              ← as regras, onde você vai estar trabalhando
├── 01-misterio\
│   ├── veil-of-dust.mp3
│   └── ...
├── 02-tragedia\
└── ...
```

**Criar e manter — não escreva o catálogo à mão:**

```bash
npm --prefix C:\Ai-Project\Alpha\studio run trilhas             # cria e sincroniza
npm --prefix C:\Ai-Project\Alpha\studio run trilhas -- --verificar  # só relata
```

O script cria as 10 pastas, varre os arquivos, **mede a duração de cada faixa**
e escreve o `catalogo.json`. Campos editoriais (`fonte`, `licenca`,
`intensidade`, `tags`, `bpm`) nunca são sobrescritos numa faixa que já existe —
esses são seus. Faixa sem `licenca` preenchida aparece como aviso, porque é ela
a defesa contra uma reivindicação.

A duração é medida, e não digitada, porque ela decide se o Studio repete a
faixa em loop: um número errado ali só aparece no vídeo pronto.

> **Não renomeie um arquivo depois de usá-lo num projeto.** O `id` nasce do nome
> do arquivo, e é o `id` que os `scenes.json` guardam. Renomear cria um id novo
> e os projetos antigos ficam sem música — o Studio avisa, mas o conserto é
> manual. Para mudar o nome de exibição, edite o `id` no catálogo.

E o `catalogo.json`, uma entrada por faixa — é isso que permite ao Alpha
"saber que música existe" em vez de chutar. **É o formato que o Studio lê**
(`lib/music/catalog.ts`); só `id`, `arquivo` e `duracao` são obrigatórios:

```json
{
  "version": 1,
  "faixas": [
    {
      "id": "misterio-veil-of-dust",
      "arquivo": "01-misterio/veil-of-dust__120s__loop.mp3",
      "secao": "misterio",
      "duracao": 120,
      "bpm": 62,
      "loopavel": true,
      "intensidade": 2,
      "instrumentacao": ["drone", "cordas", "piano"],
      "tags": ["investigacao", "abertura", "frio"],
      "fonte": "YouTube Audio Library",
      "licenca": "YT-AL — livre, sem atribuição, sem Content ID"
    }
  ]
}
```

O `id` é o que vai no campo `cue` do `scenes.json`. O `duracao` não é enfeite:
se a faixa for mais curta que a sequência que ela cobre, o Studio repete a
faixa e avisa — o certo é gerar a música maior que a sequência.

`intensidade` de 0 a 5 é o campo mais útil na prática: permite subir e descer a
energia dentro da mesma seção emocional sem trocar de clima.

---

## 3. De onde tirar a música — veredito por fonte

| Fonte | Custo | Risco de reivindicação | Veredito |
|---|---|---|---|
| **YouTube Audio Library** | grátis | **nenhum** — o próprio YouTube garante que faixas da biblioteca não são reivindicadas por Content ID; maioria sem exigência de atribuição | **Base da biblioteca.** Mais seguro que existe para YouTube. |
| **Pixabay Music** | grátis | baixo, mas há relatos de reivindicações que o criador tem que contestar manualmente (não há whitelisting) | Bom complemento; evitar em vídeo monetizado crítico |
| **Uppbeat** | grátis com crédito / pago | baixo | Complemento |
| **Free Music Archive** | grátis | **alto** — exige checar a licença CC faixa a faixa, e a FMA avisa que não detém os direitos originais | Evitar para uso comercial |
| **Artlist** (~US$15/mês) | pago | baixo, licença perpétua (mantém o direito mesmo cancelando) | Melhor custo-benefício pago para cinematográfico |
| **Epidemic Sound** (~US$13/mês) | pago | baixo, com whitelisting de Content ID | Alternativa a Artlist |
| **ElevenLabs Music** | pago (API/plano) | baixo — direitos comerciais completos, com acordos de licenciamento (Merlin, Kobalt) | **Melhor caminho para música sob medida**, ainda mais porque o ElevenLabs já é o fornecedor de narração |
| **Suno** | pago = uso comercial | médio — sem indenização: se houver reivindicação de terceiro, o risco jurídico é seu | Já usado no canal; manter só onde já funciona |
| **Stable Audio** | grátis/pago | baixo — treinado com dados licenciados, criador é dono da saída | Ótimo para SFX e texturas instrumentais |

**Estratégia recomendada — híbrida:**

1. Uma **biblioteca fixa local** (YouTube Audio Library + Pixabay, curada por
   seção emocional) para os climas recorrentes. Reutilizar as mesmas faixas
   entre vídeos não é preguiça: é **identidade sonora do canal** — o espectador
   passa a reconhecer o tema de "revelação do monstro".
2. **Música gerada sob medida** (ElevenLabs Music) só nos momentos-assinatura:
   o clímax, a transformação, a luta. São 2–3 cues por vídeo, não 10.
3. Registrar em `catalogo.json` a fonte e a licença de cada faixa — quando vier
   uma reivindicação, a defesa tem que estar a um clique.

---

## 4. Mixagem — números concretos

A regra nº 1 é imutável: **a narração nunca disputa com a música.**

| Parâmetro | Valor | Fonte |
|---|---|---|
| Alvo de loudness do vídeo final | **−14 LUFS** integrado | é para onde o YouTube normaliza |
| Música sob narração | **−18 a −25 dB** abaixo da voz | prática de mixagem para locução |
| Ducking do canal (já registrado na skill) | −8 a −12 dB | PONTO DE PARTIDA do canal |
| Música em trecho sem voz | pode subir até ~−12 a −14 dB pico | respiro/clímax visual |
| Ataque do ducking | **< 300 ms** | descer rápido quando a voz entra |
| Release do ducking | lento (~800 ms–1,5 s) | subir devagar, senão "bombeia" |
| SFX do clipe sob narração | ~30% (o `mix` atual do Studio) | já implementado |

**Implementado assim (2026-08-05):** o Studio já detecta as pausas da narração,
então a curva de ducking é calculada **por frame** dentro do próprio Remotion
(`lib/audio/ducking.ts`, usado igual no preview e no render) — sem compressor
sidechain e sem passo de ffmpeg. A música sobe sozinha nas pausas e desce
quando a voz volta.

Dois detalhes que só aparecem ao ouvir:
- A descida termina **exatamente** quando a voz volta, não quando começa a
  descer — por isso a primeira sílaba nunca fica enterrada.
- Pausa curta demais (< `minimumPauseSeconds`, 0,9s por padrão) é respiro, não
  intervalo: se a música subisse em cada respiro, ela pulsaria entre as
  palavras. Pausa mais curta que subida+descida simplesmente sobe menos, em vez
  de ser cortada no meio do movimento.

No fim do render, uma passada de `loudnorm=I=-14:TP=-1.5:LRA=11` garante que
todo vídeo do canal saia no mesmo volume — o espectador nunca precisa mexer no
controle entre um vídeo e outro.

---

## 5. O contrato: `scenes.json`

Hoje a informação emocional das cenas existe (a skill `whoiam` produz o
Documento 7 — Mapa de Trilha, e o Documento 8 — Mapa de Edição), mas em forma
de tabela para colar no CapCut. A proposta é que essa mesma informação viaje
junto com os clipes, como dado estruturado, e o Studio a leia:

```json
{
  "version": 1,
  "criatura": "Medusa",
  "cenas": [
    {
      "bloco": 7,
      "clipe": "7.mp4",
      "intencao": "horror da transformação",
      "emocao": "terror",
      "energia": 4,
      "cue": "SILENCIO",
      "sfx": ["escamas surgindo", "ossos estalando", "sibilo"],
      "transicao_da_anterior": "corte",
      "filtro": "cold",
      "nota": "cortar a música 1s antes do bloco começar"
    },
    {
      "bloco": 8,
      "clipe": "8.mp4",
      "emocao": "tragedia",
      "energia": 2,
      "cue": "tragedia-lament-cello",
      "transicao_da_anterior": "dissolve",
      "filtro": "cinematic"
    }
  ]
}
```

Com esse arquivo dentro da pasta do projeto, o Studio pré-preenche filtro,
transição, cue musical e ducking de cada cena automaticamente — e a edição
manual vira ajuste fino, não montagem do zero. É o "arquivo de orientação de
cenas" que deve ser enviado junto com os vídeos.

**Estado (2026-08-05):** `filtro`, `transicao_da_anterior` e `cue` são lidos e
aplicados no render. `emocao`, `energia`, `intencao`, `sfx` e `nota` são
validados e preservados, mas nada os consome ainda. Dos tipos de cue,
`SILENCIO` e id de faixa funcionam; `STINGER` e `DRONE` são reportados como
ainda não renderizados em vez de sumirem em silêncio.

Cenas seguidas com o mesmo `cue` viram **um** trecho de música só — é a regra
da sequência emocional, aplicada automaticamente. As faixas usadas são copiadas
para `public/music/` do projeto, o que também deixa o projeto autossuficiente
ao viajar entre as duas máquinas.

---

## Fontes

- [Use music and sound effects from the Audio Library (YouTube Help)](https://support.google.com/youtube/answer/3376882?hl=en)
- [YouTube Audio Library: Free Music and Attribution Rules in 2026 (vidIQ)](https://vidiq.com/blog/post/royalty-free-music-youtube-audio-library/)
- [12 Best Free Royalty-Free Music Sites for Video (Swarmify)](https://swarmify.com/blog/free-music-for-your-videos-the-importance-and-where-to-find/)
- [Best Royalty-Free Music Libraries for YouTube Creators in 2026 (UxerWave)](https://uxerwave.com/video-audio/best-royalty-free-music-youtube-creators/)
- [ElevenLabs Music — royalty-free commercial music](https://elevenlabs.io/music/commercial)
- [Can You Sell Suno AI Music? 2026 Commercial Rights Guide (Terms.law)](https://terms.law/ai-output-rights/suno/)
- [Suno vs Stable Audio: Commercial Rights Compared (Dynamoi)](https://dynamoi.com/learn/comparisons/suno-vs-stable-audio-commercial-rights)
- [The Spotting Session: Mapping Your Film's Score (Ken Joseph Music)](https://kenjosephmusic.com/what-is-a-spotting-session-and-how-does-the-workflow-work/)
- [Spotting Sessions Demystified (Adrian Walther)](https://www.adrianwalther.com/post/spotting-sessions-demystified-collaborating-with-directors-to-find-the-perfect-musical-moments)
- [Audio Ducking: How to Lower Music Under a Voiceover (Zella)](https://zellahq.com/blog/music-ducking-explained/)
- [The Right Audio Levels for YouTube (Kevin Muldoon)](https://www.kevinmuldoon.com/audio-levels-youtube/)
