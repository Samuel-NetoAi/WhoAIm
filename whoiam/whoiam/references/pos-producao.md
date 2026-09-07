# PÓS-PRODUÇÃO — Narração, Trilha (Biblioteca do YouTube + Suno), SFX e Edição (CapCut)

Complemento do SKILL.md para a fase pós-montagem. Mesma disciplina do receituário Seedance:
o que está marcado como PONTO DE PARTIDA não foi testado no canal — vira regra só após
veredito real do usuário, e o veredito deve ser registrado aqui.

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

## 2b. SFX — camada nova, criada pelo áudio desligado no gerador (ago/2026)

Enquanto o vídeo saía do Leonardo com `[AUDIO]` diegético, os SFX vinham junto com o clipe. No
Higgsfield o áudio é parâmetro (`generate_audio: false` / `sound: off`) e a decisão do canal é
desligar — porque com o áudio ligado o modelo insere trilha por conta própria, que é exatamente o que
o Documento 7 existe para evitar. **Consequência: os clipes chegam mudos e os SFX passam a ser uma
camada de pós-produção.**

Fontes, em ordem:
1. **Efeitos sonoros da Biblioteca de áudio do YouTube** — centenas, gratuitos, sem Content ID. Piso.
2. **Gerados** (Higgsfield `mirelo_text_to_audio` para SFX, ou equivalente) quando o efeito é
   específico demais para a Biblioteca.

O `[AUDIO]` do prompt de vídeo **continua sendo escrito**, mas muda de função: deixa de ser instrução
para o gerador e passa a ser a **lista de compras de SFX** daquele bloco, que alimenta a coluna de SFX
do Documento 8. Manter a exigência de específico e diegético ("madeira do cais rangendo", "páginas
viradas"), nunca "efeito de tensão".

**Alternativa não descartada, a testar:** deixar `generate_audio: true` e simplesmente descartar a
faixa de áudio do clipe na montagem, aproveitando só os SFX que vieram bons. Custa a mesma coisa e
pode economizar a camada manual. Não foi testado — testar num bloco e registrar na seção 4.

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

**Regra de mixagem (PONTO DE PARTIDA):** trilha sob narração com ducking de −8 a −12 dB; subir a trilha
nos trechos SEM voz (transições, clímax visual). A narração nunca disputa com a música — é a regra nº 1.

---

## 3. EDIÇÃO — O STUDIO PRÓPRIO DO USUÁRIO (Documento 8: MAPA DE EDIÇÃO)

**Correção de premissa (19/08/2026).** Esta seção foi escrita presumindo CapCut. O editor do canal é
**"o Studio"** — `github.com/Samuel-NetoAi/WhoAIm`, pasta `studio/`: aplicação **Next.js 16 +
Remotion 4.0.495** que o próprio usuário desenvolveu, com render server-side e pós-processo por ffmpeg
local. **Código auditado em 19/08/2026** (ver `recursos-higgsfield-quando-usar.md` §1b para o veredito
do upscale). O que ele faz:

| Função do Studio | O que muda nesta referência |
|---|---|
| **Legendas sobrepostas ao vídeo**, para ver onde a narração encaixa | É o **Documento 1a (rascunho de legendas com placement)** executado de verdade, em cima do vídeo real, em vez de estimado por constante. Quando o Studio estiver rodando, ele **substitui** a estimativa: o rascunho da skill vira insumo de texto, e o encaixe se lê na tela. |
| Filtros | Camada de grading; conversa com o Mood Sheet e com o "Manual Style" do Cinema Studio — cuidado para não gradear duas vezes. |
| Biblioteca de músicas | **Resolvido (19/08/2026): são faixas licenciadas do YouTube, sem risco de strike** — coerente com a hierarquia da seção 2, onde a Biblioteca do YouTube é a fonte primária. Duas ressalvas que continuam valendo: (a) faixa marcada `CC BY 4.0` exige crédito ao artista + link na descrição, e isso é termo de licença, não regra de curso; (b) **Biblioteca de áudio do YouTube Studio ≠ YouTube Music.** A Biblioteca (em Studio → Áudio) é livre para uso em vídeo; o YouTube Music é serviço de streaming e as faixas dele NÃO são licenciadas para trilha. Se alguma faixa do acervo do Studio veio do segundo, ela sai. |
| **Interpolação de frames** | `minterpolate` do ffmpeg (não é RIFE). **Manter DESLIGADA**: o YouTube não precisa de 60fps aqui, o próprio projeto registra que borra movimento rápido, e interpolar material de IA acrescenta morphing. |
| **Upscale** | `scale=lanczos` 2x — reamostragem, **não sintetiza textura**. Custo marginal zero, mas não recupera detalhe. Por isso o ECU da revelação sai em 1080p nativo. Detalhe em `recursos-higgsfield-quando-usar.md` §1b. |
| **Resolução de saída** | Composição sempre com ≥1080p no lado curto, desacoplada dos clipes — decisão acertada: legenda e overlay ficam nítidos em vez de rasterizados a 480p. |

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
- [ ] SFX: camada manual (Biblioteca/gerado) × aproveitar o áudio nativo do gerador e descartar a
      música — qual dá menos trabalho e melhor resultado
- [ ] Orçamento de narração em bloco de 30s: a constante de 33/15s escala linearmente para 66/30s?
      (hipótese, nunca medida — medir no primeiro vídeo com blocos de 30s)
- [ ] Paleta musical: quais cues funcionaram/falharam por tipo de cena
- [ ] Ducking e mixagem: valores reais usados
- [ ] Formato do Documento 8: colunas mantidas/removidas
- [ ] Rascunho de legendas com placement (1a, jul/2026): pendente de primeiro uso real — validar se
      a constante do orçamento de duração estima o encaixe com precisão suficiente para ser útil no
      planejamento, ou se precisa de ajuste depois do primeiro vídeo por esse fluxo.
