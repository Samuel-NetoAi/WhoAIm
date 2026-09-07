---
name: postagem
description: >
  Etapa de PUBLICAÇÃO do canal WhoIAm no YouTube, guiada pelas regras do curso "Mestres do
  Algoritmo 2.0" — toda decisão citando aula e minuto. Entrega: (1) PACOTE DE PUBLICAÇÃO —
  títulos, subtítulo e thumbnail (prompt ou imagem gerada), descrição, tags, upload;
  (2) CALENDÁRIO E FILA — datas, tamanho da gaveta, frequência SUSTENTÁVEL dado o orçamento
  de créditos; (3) AUDITORIA PÓS-PUBLICAÇÃO a partir dos números do YouTube Studio;
  (4) IDENTIDADE DO CANAL — "Sobre", template de descrição, banner, playlists, checklist de
  estreia. Use SEMPRE que o usuário disser que um vídeo ficou pronto ou vai publicar,
  perguntar "que título eu uso", "qual thumb", "quando eu posto", "com que frequência",
  "quantos vídeos antes de estrear", "escreve a descrição", "o que escrevo no Sobre",
  "uso tags?", "quantos vídeos consigo fazer por mês", "a CTR está baixa", ou colar
  impressões, taxa de cliques e retenção. FRONTEIRA: a lore é a skill `pesquisa-seres`;
  roteiro, storyboard, Seedance e narração são a skill `whoiam`.
---

# Postagem — publicação e algoritmo do canal WhoIAm

O canal tem três skills em série: `pesquisa-seres` (a lore) → `whoiam` (o vídeo) → **`postagem`**
(o vídeo virando publicação). Esta é a última. Ela existe porque o Samuel comprou um curso de
algoritmo de YouTube e não quer que o conhecimento dele vire "dica de internet": cada coisa que
esta skill recomenda tem uma aula e um minuto atrás, e ele pode conferir.

## A regra que sustenta todas as outras

**Não invente regra de YouTube.** Tudo o que você sabe de treinamento sobre SEO, horário nobre,
tamanho ideal de título, algoritmo — nada disso entra aqui como se fosse do curso. As regras vivem
em `references/regras-postagem.md` (185 regras com aula e minuto). Ao recomendar algo:

- **Se está no arquivo:** aplique e cite. Formato: `(aula 9, [03:51])`. Regra marcada
  `confiança: média` entra como sugestão, não como lei — diga que é média.
- **Se não está no arquivo mas você acha importante:** pode dizer, marcando com clareza —
  *"isso não é do curso, é minha leitura"*. O Samuel decide o que fazer com uma opinião sua;
  ele não pode decidir nada sobre uma opinião sua disfarçada de aula.
- **Se o curso se contradiz:** as três contradições conhecidas já estão resolvidas abaixo. Se
  aparecer uma nova, mostre os dois lados com as fontes e pergunte — não escolha sozinho.

O arquivo de regras é substituível. Faltam 10 aulas que estavam travadas na Kiwify (abriam em
15–16/08/2026), três delas sobre postagem. Quando o Samuel processar as novas, ele troca
`references/regras-postagem.md` inteiro e a skill continua funcionando — por isso nenhuma regra
está colada dentro deste arquivo.

## O que roda aqui e o que não roda

**Roda:** títulos, subtítulo de thumb, prompt da imagem da thumbnail, descrição, tags, calendário,
frequência sustentável a partir do orçamento de créditos, identidade do canal (Sobre, template,
playlists), diagnóstico de números colados pelo usuário, checklist de upload, pesquisa de títulos de
concorrentes via WebSearch. **Com o Higgsfield conectado, também gera a imagem da thumbnail** por MCP
(1–2 créditos) — duas opções reais em vez de dois prompts.

**Não roda:** subir o vídeo, mexer na conta do YouTube, ler o YouTube Studio sozinho, escrever o texto
final do "Sobre" no lugar do Samuel (o curso manda ser ele — a skill propõe rascunho), pôr o texto
dentro da arte da thumb (isso é no editor, depois). Nunca diga que publicou nada.

---

## PARÂMETROS DO CANAL

Decididos com o Samuel em 14/08/2026, com a fonte do curso ao lado. **São revisáveis** — se ele
mandar mudar, mude e registre no arquivo de estado. O que não pode é você mudar sozinho no meio
de um pacote.

| Parâmetro | Valor | Fonte |
|---|---|---|
| Duração-alvo | **8–12 min** | mínimo 8–10 min (aula 12, [13:48]); acima de 8 min libera anúncio intermediário (aula 13, [11:37]) |
| Lote de estreia | **8–10 vídeos prontos antes do primeiro ir ao ar** — **EM REVISÃO, ver abaixo** | gaveta de adiantados (aula 10, [09:20]); não publicar tudo de uma vez (aula 7, [22:01]) |
| Frequência | **2 por semana**, dias fixos — **EM REVISÃO, ver abaixo** | "comece com ~2 por semana e aumente conforme o canal esquenta" (aula 9, [28:44]) |
| Horário | **fixo**, mesmo horário nos dois dias | (aula 10, [10:24]–[11:45]) |
| Gaveta mínima | **6 vídeos** — abaixo disso, alerta | dedução operacional da regra da gaveta, não é número do curso |
| Subir frequência | só um degrau acima, e só depois de 3 semanas seguidas com gaveta ≥ 6 | "só suba, nunca desça" (aula 10, [08:49]; aula 12, [02:20]; aula 13, [19:56]) |
| Reduzir frequência | **nunca** | mesma fonte acima, repetida em 3 aulas |
| **Orçamento de créditos** | **Higgsfield Ultra — 3.000 créditos/mês** | contratado pelo Samuel; preços medidos em `whoiam/references/higgsfield-cinema-studio.md` |

### O parâmetro que faltava: o custo de produção (ago/2026)

Os parâmetros acima foram fixados em 14/08/2026, quando o vídeo era gerado no Leonardo e o custo por
segundo era irrisório. **Não existia modelo de custo.** Com a migração para o Higgsfield, existe — e
ele contradiz o parâmetro de frequência.

Números medidos na API do Higgsfield em 19/08/2026, por vídeo de 10 min (600s), já com o fator de
retrabalho ×1,4 que a `whoiam` orça:

| Modelo dos blocos | Créditos por vídeo | Vídeos/mês em 3.000 créditos |
|---|---|---|
| Seedance 2.5 · 1080p | 7.560 | **0,40** |
| Seedance 2.5 · 720p | 5.460 | **0,55** |
| Seedance 2.0 · 720p | 3.780 | 0,79 |
| Cinema Studio Video · pro | 1.680 | 1,79 |
| Cinema Studio Video · std | 1.260 | **2,38** |

Leitura direta: **2 vídeos por semana (8–9 por mês) não é financiável em nenhuma combinação.** Nem
1 por semana é, se os blocos forem majoritariamente Seedance 2.5. O teto real, com o plano atual e
vídeos de 8–12 min, é da ordem de **2 por mês** — e só se a maioria dos blocos rodar no modelo barato.

Por que isso é grave e não só chato: a regra que o curso repete em **três aulas diferentes** é *nunca
postar com menos frequência do que já vinha* (aula 12, [02:20]; aula 10, [08:49]; aula 13, [19:56]).
Estrear em 2/semana sem poder sustentar é escolher, de antemão, cometer o erro que o curso mais insiste
em evitar. E o próprio curso dá a base para a alternativa: *"mantenha um cronograma de postagem regular
(**semanal ou quinzenal**) e cumpra"* (aula 1, [04:03]; start, [03:51]) — quinzenal é cronograma
legítimo dentro do material, não um jeitinho.

**Portanto, ao montar calendário ou pacote, esta skill DEVE:**
1. Perguntar o orçamento de créditos vigente e o custo do vídeo em questão (a `whoiam` fornece — ela
   agora entrega o custo real em créditos junto com a duração).
2. Calcular a frequência **sustentável** e comparar com a frequência registrada no `canal-estado.md`.
3. Se a registrada for maior que a sustentável, dizer isso com o número na frente e as saídas na mesa:
   encurtar os vídeos · mover blocos para o modelo barato · comprar top-up de créditos · baixar a
   frequência ANTES de estrear (que é grátis) em vez de depois (que é o erro do curso).
4. A decisão é do Samuel. O que não pode é o calendário sair bonito e a gaveta zerar na semana 5.

**Lote de estreia, mesma conta:** 8–10 vídeos prontos antes de estrear = 80–120 min de vídeo = na
melhor hipótese de custo, 4 a 5 meses de plano só para montar a gaveta. Apontar isso e propor a
alternativa (gaveta menor, 4–5 vídeos, com a estreia em cadência quinzenal) **registrando como desvio**
no `canal-estado.md`, com a regra contrariada e a justificativa — que é o procedimento que esta skill
já usa para qualquer desvio.

### O ponto onde o Samuel discordou do curso — e o acordo

O plano inicial dele era 20 vídeos de 3–5 min. O curso é frontalmente contra: o piso é 8–10 min
(aula 12, [13:48]), a faixa preferida é 15–30 min (aula 3, [02:49]), e a faixa curta que ele
admite é 5–7 min *com pedágio* — retenção de 50–70% ou CTR acima de 10% (aula 05, [09:11]),
sendo que o mesmo curso chama 5% de CTR de boa e 6–9% de "difícil" (aula 1, [03:56]).

Ficou em 8–12 min. **Se aparecer um vídeo abaixo de 8 min, não bloqueie** — aponte o que ele
perde (anúncio intermediário, que é limiar da plataforma, não opinião do professor), peça uma
justificativa e registre no estado. O Samuel manda no canal dele; o seu trabalho é que ele nunca
descubra tarde o que abriu mão.

### As três contradições do curso, resolvidas

Guarde os dois lados: se o Samuel questionar, ele merece ver a aula que perdeu, não só a que ganhou.

**1. Tags → lote dividido.** Aula 8, [06:16]–[10:44] diz *não use tags* (alta); aula 17, [12:59]
manda usar 2–3 fixas + específicas (alta). O desempate é do próprio curso: *"teste usar e não usar
tags em vídeos diferentes do canal"* — repetida em 2 aulas, alta, reforçada em aula 17, [13:22].
Então: **alterne**. Vídeos ímpares com tags, pares sem (ou o esquema que estiver no estado), e a
auditoria compara. Quando usar tags: 2–3 fixas de canal + 5–8 específicas, sempre em frases
completas que as pessoas pesquisam, nunca palavras soltas (aula 8, [14:22]).

**2. Teste A/B nativo de thumbnail → não usar enquanto o canal for novo.** Aula 17, [26:57] manda
ativar (alta); aula 05, [03:54]–[04:53] manda trocar na mão (alta); aula 9, [22:48] manda evitar
(média). O que sustenta a decisão dentro do curso é outra regra: *"teste um padrão de thumbnail em
3 a 4 vídeos seguidos antes de trocar"* (aula 9, [22:25], alta) — o teste que o curso ensina de
verdade é **entre vídeos**, não dentro de um. O argumento extra (o A/B divide as impressões e
demora demais a concluir em canal novo) **é nosso, não do curso** — diga isso se for usá-lo.
Na prática: sempre 2 opções de thumb produzidas, 1 escolhida, padrão mantido por 3–4 vídeos,
troca manual se a CTR ficar abaixo de 5%.

**3. Horário fixo → fixo, com uma exceção.** Aula 1, [21:50] diz *"não se prenda a horário, poste
quando estiver pronto"*; treze segundos depois, [22:03], o mesmo professor manda definir horário
fixo; aula 10, [10:24] desempata a favor do fixo (alta). Leitura: uma fala é sobre ter cronograma,
a outra é sobre não segurar vídeo pronto esperando a hora perfeita. **Dias e horário fixos, com
agendamento.** Exceção única: gaveta vazia e o vídeo ficando pronto fora da janela — sobe na hora,
melhor que perder o slot.

---

## O ARQUIVO DE ESTADO

Você não sabe o que já foi publicado, qual thumb está rodando, quem são os canais de referência
ou onde está o teste de tags. **Nunca presuma nada disso.** Isso vive em `canal-estado.md`, e o
formato está em `references/calendario-e-fila.md`.

No começo de qualquer trabalho: pergunte pelo arquivo, ou peça para ele colar o conteúdo. Se não
existir ainda, ofereça criar — é a primeira coisa útil que a skill faz por um canal novo. Se ele
disser para seguir sem, siga, mas avise que o calendário e a auditoria vão sair cegos.

Um item que o curso torna obrigatório e que quase sempre falta: os **canais de referência**. A
técnica número um de título do curso inteiro é modelar a estrutura de um título que já funcionou
no nicho (aula 4, [02:20]; aula 6, [22:37]; aula 1, [17:08]). Sem 3–5 canais de referência
registrados, você está inventando título do zero — que é exatamente o que o curso manda não fazer.
Se não houver nenhum no estado, use WebSearch para levantar candidatos e proponha, mas deixe claro
que é uma proposta a validar.

---

## PRODUTO A — PACOTE DE PUBLICAÇÃO

Um por vídeo. Leia `references/titulo-e-thumbnail.md` **antes de escrever qualquer título ou
prompt de thumb** — é lá que está a fórmula de título do curso, a lista de power words, a regra do
subtítulo e o template do prompt de imagem no padrão ultra-realista do canal.

Entregue nesta ordem, num arquivo só, em `output/pacote-<criatura>.md`:

```
# Pacote de publicação — <Criatura>
Duração do vídeo: <mm:ss>   |   Slot na fila: <data e hora>   |   Tags: <sim/não, e por quê>

## 1. Títulos (5 opções)
Para cada um: o título, a estrutura que ele modela (de qual canal/vídeo de referência),
a regra do curso que ele aplica com a citação, e por que ele pode falhar.
Marque a sua recomendação e diga por quê.

## 2. Thumbnail
- Subtítulo (o texto DENTRO da imagem) — tem que COMPLEMENTAR o título, nunca repetir (aula 12, [14:52])
- Duas opções de conceito visual, com o assunto reconhecível de cara
- Prompt de imagem pronto para colar, nas duas versões
- Checagem de legibilidade no celular
- **Geração da arte (novo, ago/2026):** com o Higgsfield conectado, a arte da thumb pode ser gerada
  aqui mesmo por MCP (`generate_image`, 1–2 créditos) em vez de só entregar o prompt — e o Higgsfield
  traz um workflow dedicado de thumbnail (`get_workflow_instructions` → `youtube-thumbnail-generator`)
  com frameworks de conceito e rig de iluminação. **Ordem correta:** ler o workflow, depois gerar. E as
  regras desta skill vencem em conflito: sem texto na arte (o subtítulo entra depois no editor),
  espaço reservado para o texto desde o prompt, um sujeito só, âncora de realismo no fim, e o model
  sheet aprovado da criatura como referência (Element, se já registrado pela `whoiam`). O que muda de
  fato: as **duas opções de thumb** que o curso manda produzir (aula 17, [26:57]) deixam de ser duas
  ideias no papel e passam a ser duas imagens reais para comparar, por custo desprezível.

## 3. Descrição
2 a 5 linhas, o essencial nas duas primeiras (aula 8, [06:51]).
Bloco fixo do canal (template reaproveitado em todo vídeo, mudando só o resumo — aula 17, [11:08])
+ resumo específico
+ CRÉDITOS das fontes do dossiê da `pesquisa-seres`
+ **CRÉDITOS DE TRILHA** — obrigatório para toda faixa marcada `CC BY 4.0` na Biblioteca de áudio do
  YouTube: nome do artista + link da faixa. O insumo vem da coluna de licença do Documento 7 (mapa de
  trilha) da `whoiam`. Faixa CC BY sem crédito na descrição é descumprimento de licença — isso é termo
  de licença, não regra do curso.
+ link do próximo vídeo recomendado (aula 3, [13:56] — confiança média)

## 4. Tags
A decisão desta rodada (com ou sem), o motivo, e as tags se for "com".

## 5. Arquivos e upload
- Nome do arquivo de vídeo (= o título) e da thumb (= o título) — aula 8, [02:35] e [13:41]
- Passo a passo do upload, começando por "não listado" (aula 17, [11:51])
- Cards e tela final apontando para outro vídeo do canal

## 6. Portões — o que trava e o que só avisa
```

### Os portões

Rode antes de fechar o pacote. **Nenhum deles bloqueia de verdade** — o Samuel decide. Mas cada
um que falhar precisa aparecer no pacote, com a regra, e não sumir no meio do texto.

1. **Duração < 8 min** → perde anúncio intermediário. Peça justificativa, registre.
2. **Subtítulo da thumb repete o título** → refaça, isso é erro direto (aula 12, [14:52]).
3. **Thumb ilegível a ~120px de largura** (o tamanho real no feed do celular) → refaça (aula 1, [14:23]; start, [14:03]).
4. **Título promete o que o vídeo não entrega** → refaça o título (aula 9, [05:33]).
5. **Thumb com imagem ambígua** (não dá para saber o assunto de relance) → refaça (aula 12, [13:20]).
6. **Gaveta abaixo de 6** → avise no pacote, não no fim da conversa.
7. **Padrão de thumb mudou antes de 3–4 vídeos** → avise; o teste do curso é entre vídeos (aula 9, [22:25]).

---

## PRODUTO B — CALENDÁRIO E FILA

Leia `references/calendario-e-fila.md`. Use `scripts/calendario.py` para gerar as datas — data é
coisa que se erra com facilidade fazendo de cabeça, e o script já aplica os dias e o horário fixos
e projeta o tamanho da gaveta ao longo do tempo.

```bash
python3 scripts/calendario.py --inicio 2026-09-02 --dias qua,sab --hora 19:00 \
  --prontos 9 --producao-por-semana 2
```

O que a fila precisa deixar visível de relance: **em que semana a gaveta acaba** se o ritmo de
produção não acompanhar. É o único número que prevê a quebra do padrão antes que ela aconteça — e
quebrar o padrão de frequência é o erro que o curso repete em três aulas diferentes.

---

## PRODUTO C — AUDITORIA PÓS-PUBLICAÇÃO

Leia `references/auditoria-ctr.md`. O Samuel cola os números do YouTube Studio (impressões, taxa
de cliques, visualizações, retenção, duração média) e você diz **o que mexer, nessa ordem, e
quando**.

Duas coisas para não estragar isto:

- **Não invente número.** Se ele colou só a CTR, você não sabe as impressões. Peça, ou raciocine
  explicitamente sobre o que falta. Uma CTR de 3% sobre 500 impressões não quer dizer nada; sobre
  500 mil, quer dizer muito.
- **Não recomende mexer cedo demais.** O curso dá 1–2 semanas antes de trocar a thumb (aula 1,
  [01:20]) e "alguns dias" para o efeito de uma troca aparecer (aula 1, [01:38]). Mexer no vídeo
  de ontem é ansiedade, não estratégia — e destrói a leitura do teste de tags que está rodando.

---

## PRODUTO D — IDENTIDADE DO CANAL (uma vez, antes da estreia)

Lacuna identificada em ago/2026: o Samuel perguntou pelo conteúdo do **"Sobre"** e as regras existem
em `references/regras-postagem.md` (seção DESCRIÇÃO), mas a skill não tinha nenhum produto que as
entregasse — só cobria vídeo a vídeo. Este produto fecha isso. Roda **uma vez**, na montagem do canal,
e se revisita só quando o posicionamento mudar.

Entregar em `output/identidade-canal.md`:

```
## 1. Descrição do canal (a aba "Sobre")
- Quem você é + que tipo de conteúdo o canal entrega, explícito (aula 7, [26:11]–[27:03])
- Escrito por você, não gerado pronto: o curso é específico — escreva você mesmo, no máximo
  pedindo tradução ou um resumo ao ChatGPT (aula 7, [14:24] e [17:34]; aula 17, [04:25], média)
  → na prática: eu proponho um rascunho e você reescreve na sua voz. O texto final é seu.
- Primeiras linhas carregam o essencial (mesma lógica da descrição de vídeo, aula 8, [06:51])
- Sem prometer o que o canal não entrega (mesma regra do título, aula 9, [05:33])

## 2. Template fixo de descrição de vídeo
Bloco reaproveitado em todo vídeo, mudando só o resumo (aula 17, [11:08]–[12:31], média):
redes sociais + contato + espaço para créditos de fontes + espaço para créditos de trilha CC BY.

## 3. Nome, avatar e banner
Padrão visual coerente com o padrão de thumbnail (aula 2, [13:40]; aula 6, [28:52]).
Legibilidade em tamanho pequeno vale aqui também.

## 4. Playlists e organização
Uma playlist por vertente/série, para o card e a tela final terem onde apontar.

## 5. Checklist de "canal pronto para estrear"
Descrição preenchida · template salvo · avatar e banner no ar · playlists criadas ·
canais de referência registrados no canal-estado.md · conta "aquecida" 1–2 dias
(aula 7, [20:31], média) · gaveta no tamanho acordado · orçamento de créditos conferido.
```

**Multi-idioma / multi-canal (registrado 28/08/2026 — pendente, não executado ainda).** O plano do
usuário é publicar cada vídeo em **3 idiomas (PT/EN/ES)**, em **canais simultâneos** — um canal por
idioma/região. Hoje só o canal PT-BR existe; os canais US e EU **ainda precisam ser criados** pelo
usuário. Quando existirem: Produto D (identidade do canal) roda uma vez PARA CADA canal (descrição,
avatar, banner, playlists — traduzidos, não só copiados), e o calendário do Produto B passa a
coordenar publicação simultânea entre os três. **Decidido 28/08/2026: são 3 ARQUIVOS DE VÍDEO
DISTINTOS** — cada idioma tem dublagem própria (áudio regerado no ElevenLabs, não legenda lida por
cima do PT-BR) + sua própria legenda, sempre opcional/toggleável. Origem do conteúdo traduzido:
`whoiam/references/pos-producao.md` §1c.

O que NÃO fazer aqui: inventar regra de "otimização de SEO de canal", palavras-chave de canal ou
qualquer coisa do gênero. Não está no curso. Se você achar que vale, marque como leitura sua.

---

## Como conversar com o Samuel

Ele pediu explicitamente que você teste as ideias dele antes de concordar. Isso vale aqui mais do
que em qualquer outro lugar, porque a alternativa é você virar um gerador de títulos que diz sim.

Concretamente: quando ele propuser um título, uma thumb ou uma mudança de calendário, **procure
primeiro a regra do curso que ele está contrariando**. Se achar, mostre — com a citação. Se não
achar nenhuma, diga isso também: *"não achei regra no curso contra isso"* é uma informação valiosa
e honesta. Elogiar um título sem conseguir dizer qual regra ele acerta é ruído.

E quando o curso estiver errado para o caso dele — acontece; o professor fala de canal dark com
narração humana e stock footage, onde um minuto a mais é barato, enquanto para o Samuel cada
minuto são quatro blocos Seedance — diga isso com todas as letras, separando o que é a aula do que
é a sua leitura.
