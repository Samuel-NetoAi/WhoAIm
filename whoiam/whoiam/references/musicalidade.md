# Musicalidade e trilha — gramática de cena e a Biblioteca do YouTube na prática

> Criado em **2026-09-03**, a pedido do Samuel. Duas apurações do Salomão nesta data
> (`D:\Agentes\SALOMAO\missoes\2026-09-03-*`). Marcadores: 🟢 fonte primária ·
> 🔎 apurado (secundária) · ⚫ decisão do Samuel · ❌ não encontrado.
>
> **Fronteira:** mixagem (dB, ducking, LUFS) fica em `pos-producao.md` §2c. Aqui é
> **escolha** de trilha e **operação** da Biblioteca.

---

## 0. ⚠️ A LIMITAÇÃO QUE GOVERNA ESTE ARQUIVO — o agente NÃO ESCUTA

> ⚫ **Levantado pelo Samuel em 03/09/2026:** *"minha maior preocupação é que você pesquisa muito
> por transcrição; se você não escuta áudio, não sei como pode entender a tonalidade das músicas."*

**Ele está certo, e a verificação foi feita.** Não há entrada de áudio em lugar nenhum do
ferramental: o agente lê texto, imagem e PDF. O `salomao_video` é **Whisper — fala para texto**;
em faixa instrumental ele devolve vazio ou lixo. Não existe via de escuta.

### O que isso proíbe

> **O agente NUNCA decide que uma faixa "soa certo".** Julgamento de timbre, tonalidade,
> andamento percebido, mixagem da faixa ou "combina com a cena" **é ouvido do Samuel, sempre.**
> Agente que opina sobre som que não ouviu está inventando.

### O que isso permite, e é bastante

A Biblioteca do YouTube expõe **metadado verificável** — gênero, clima, duração, atribuição — e é
exatamente aí que o agente é útil. A divisão de trabalho:

| Quem | Faz o quê |
|---|---|
| **Agente** | escreve a **receita de busca** (qual gênero, qual clima, que duração, filtro de atribuição) a partir da intenção dramática do bloco; monta a shortlist; guarda o veredito |
| **Samuel** | **ouve** e escolhe dentro da shortlist |
| **Agente** | registra o que foi escolhido e por quê, para a próxima busca começar mais perto |

**O gargalo real não é o ouvido do agente — é o tamanho da lista que chega ao ouvido do Samuel.**
Reduzir 200 faixas a 6 é trabalho de metadado, e isso o agente faz.

> ⚠️ **Pendência que destrava tudo:** o vocabulário exato do filtro **"clima" (mood)** da Biblioteca
> não foi apurado — nenhuma fonte lista os valores possíveis, e a Biblioteca exige login (o
> `dissecar` de 03/09 bateu em tela de sign-in). **Pedir ao Samuel uma vez a lista de gêneros e
> climas que a interface mostra, e registrar aqui.** Com ela, a receita de busca passa a ser escrita
> no vocabulário exato da ferramenta em vez de em adjetivo aproximado.

---

## 1. A BIBLIOTECA DE ÁUDIO — 🟢 fonte primária (documentação da própria Google)

### 1.1. Os filtros, e a assimetria que importa

| Aba | Busca | Filtros |
|---|---|---|
| **Músicas** | título, artista ou palavra-chave | **seis** — título · gênero · clima · artista · **atribuição** · duração (em segundos) |
| **Efeitos sonoros** | título ou palavra-chave | **dois** — categoria · duração |

> **A assimetria é a informação.** SFX **não tem** filtro de gênero, clima nem artista. Quem
> planejar buscar efeito com a granularidade da música bate na parede. Planejar a busca de SFX por
> **palavra-chave concreta** ("door creak", "wet footstep"), que é o que resta.

**Duas barras de filtro nomeadas, e elas são o atalho mais útil da interface:**

- **"Atribuição não é necessária"** = licença padrão da Biblioteca. **⚫ Estado padrão do nosso fluxo.**
- **"Atribuição necessária"** = Creative Commons. Exige crédito na descrição.

**Filtro por clique contextual:** achou uma faixa que serve → clicar no gênero/clima/artista **dela**
refina a busca para aquilo. É o "mais como esta", e é o jeito mais rápido de transformar um acerto
em shortlist.

**Ordenação por coluna** (título, artista, duração, **data**) — clicando no nome da coluna.
⚠️ A documentação **em pt-BR traduz isso errado**, como "filtrar". É **ordenar**. E a ordenação por
data é o **único** jeito que a documentação oferece de achar as faixas novas do acervo.

**Operação:** o download sai em **MP3**, e o botão aparece **ao passar o cursor sobre a data**.
A estrela joga a faixa na aba **"Com estrela"**. Quem está no YPP **pode monetizar** vídeo com
música e SFX da Biblioteca.

### 1.2. As duas licenças, e o gerador de crédito

São **duas**: a **padrão** (sem atribuição) e **Creative Commons** (crédito obrigatório na descrição).

> 🟢 **O Studio GERA o texto de atribuição pronto.** Coluna "Tipo de licença" → ícone Creative
> Commons → botão **Copiar** → colar na descrição. **Ninguém escreve crédito à mão.** Isso é o que a
> skill `postagem` consome — e derruba metade das "regras de crédito" que circulam em blog.

🔎 A versão da CC é **CC-BY 4.0** segundo fonte secundária (licenseorg, 2026-03-02) — **a Google não
nomeia a versão em lugar nenhum.** Se a decisão depender da versão, conferir na faixa.

### 1.3. ⚠️ O VÁCUO QUE NOS AFETA DE VERDADE — uso FORA do YouTube

> 🟢 **A Google não diz se a licença padrão vale fora do YouTube.** Ela só declara que não dá
> orientação jurídica *"incluindo orientação sobre problemas com música que podem ocorrer fora da
> plataforma"*. **Ela não autoriza nem proíbe — ela se exime.**

Três fontes secundárias preenchem o silêncio de três formas **incompatíveis**: "é restrita ao
YouTube" (licenseorg, 2026-03-02) · "geralmente pode, cheque faixa a faixa" (Thematic, 2025-05-12) ·
"você TEM que contatar o artista" (Lickd, 2021-02-11 — deriva de uma lista já classificada como
lenda). **Nenhuma é primária. Não há vencedor.**

**O único ponto em que as três concordam: faixa Creative Commons PODE sair do YouTube, com crédito.**

> ### ⚫ CONSEQUÊNCIA DIRETA PARA O CANAL — e ela toca o Documento 6
>
> **Short que atravessa para TikTok/Reels não pode carregar faixa de licença padrão** — é terreno
> que o fabricante explicitamente não cobre. Duas saídas, e a escolha é do Samuel:
>
> 1. **Short fica só no YouTube** → licença padrão serve, nada muda.
> 2. **Short atravessa** → a trilha daquele corte sai **exclusivamente** de faixa **Creative
>    Commons** (com o crédito da §1.2 em toda descrição, em toda rede).
>
> **O mapa de trilha (Documento 7) precisa saber disso ANTES de escolher o cue**, porque a sequência
> que vai virar Short é decidida no Documento 6 — e trocar a faixa depois significa remixar o corte.

### 1.4. O que a Google promete, e como a promessa é redigida

🟢 *"Música e efeitos sonoros **baixados da Biblioteca de áudio** não serão reivindicados por um
detentor de direitos **através do sistema Content ID**."*

**Duas cautelas, ambas dentro da própria frase:** ela cobre o que foi **baixado da Biblioteca** (não
faixa obtida por outro caminho), e cobre o **Content ID** (não reivindicação manual nem takedown).
🔎 Uma secundária (licenseorg, 2026-03-02) afirma que algumas faixas **ainda** disparam match de
terceiro. A primária pesa mais — o Content ID é sistema da própria Google — mas **a promessa não é
blindagem absoluta.**

### 1.5. 🪤 A ARMADILHA DE TRADUÇÃO — específica de quem lê em português

| Inglês (redação original) | pt-BR (tradução oficial) |
|---|---|
| **"copyright-safe"** (seguro quanto a direitos autorais) | **"sem restrições de direitos autorais"** |

**Não é a mesma coisa.** O original nunca escreve "copyright-free" — escreve *royalty-free* e
*copyright-safe*. **A tradução oficial da Google alimenta o mito que o original evita**, e nós
operamos em pt-BR. **Ler a página em inglês quando a decisão for de licença.**

### 1.6. ❌ QUANTAS FAIXAS EXISTEM — apurado em 03/09/2026, e a resposta é "ninguém sabe"

> ⚫ **Pergunta do Samuel.** Apuração dedicada rodada no mesmo dia. **A Google nunca publicou
> contagem nenhuma** — nem de música, nem de efeito. A documentação descreve interface, filtros,
> licença e download, e **em nenhum ponto diz quantos arquivos existem.**

Os dois números que circulam **discordam por quase o dobro**, e nenhum tem lastro:

| Número | Fonte | Por que não se sustenta |
|---|---|---|
| **~1.600 no total** | Influencer Marketing Hub, 2022-04-12 | **A própria página se contradiz:** diz "milhares" de músicas + "centenas" de efeitos em outro trecho — não cabe em 1.600. E tem 4 anos. |
| **2.000 músicas + 1.000 efeitos** | vmia.com.br, 2025-05-21 | Números redondos, sem metodologia, blog de assistência técnica que fecha em anúncio. Única a separar por categoria. |

**O que três fontes independentes sustentam, e só isso:** **milhares de faixas de música e centenas
de efeitos sonoros**, com o acervo crescendo. Ordem de grandeza, não contagem.

> ⚫ **Regra: nunca citar 1.600, 2.000 ou 1.000 como fato.** Dizer "milhares de músicas, centenas de
> efeitos" — e, se o número exato importar, **contar na interface**, que é o único dado de hoje.
> O agente não tem acesso (a Biblioteca exige login); o Samuel tem, e leva minutos.

> ### 📐 E o total é a MÉTRICA ERRADA — o que decide é outra coisa
>
> **Um acervo de 3.000 faixas com 12 que servem para vídeo narrativo de mitologia é, na prática, um
> acervo de 12.** O número que decide produção é **quantas sobram depois dos SEUS filtros** — gênero
> + clima + duração + "atribuição não é necessária" — e quantas dessas já estão **saturadas**.
>
> 🔎 A saturação é o único indício de uso real que a apuração achou: as faixas populares da
> Biblioteca são reconhecíveis a ponto de o público comentar. Para um canal que quer identidade
> sonora, isso pesa mais que o tamanho do acervo.
>
> **Contagem que ninguém tem e seria a mais útil de todas:** quantas faixas são licença padrão e
> quantas são Creative Commons. Nenhuma fonte toca nisso. **Dá para ler na interface aplicando as
> duas barras de filtro** (§1.1) — vale medir junto com o resto.

### 1.7. ❌ O resto do que não se sabe sobre o acervo

A cadência real de atualização ("duas vezes por mês" é fonte única, comercial, sem origem) · **se
uma faixa pode ser removida do acervo depois de você usar**, e o que acontece com o vídeo já
publicado · restrição geográfica · se existe filtro por instrumento · formato além de MP3 (todas as
fontes param no MP3; uma secundária especifica 320 kbps).

E a crítica de que "o acervo é velho e genérico" vem de **três empresas que vendem a alternativa**,
a mais enfática de **2021**. Não é base de decisão.

---

## 2. GRAMÁTICA DE CENA — 🔎 o que apurou, e o buraco que ficou

> ⚠️ **Aviso de base estreita.** As fontes são três blogs corporativos, todos vendendo o que
> recomendam. **Nenhuma fonte primária** — nenhum compositor, nenhum livro de trilha, nenhum estudo.
> E **"mitologia" não aparece uma única vez em nenhuma das três.**

### 2.1. ✅ O que CONFIRMA regra nossa que já existia

🔎 *"Pense em termos de **atos** — em vez de usar apenas uma faixa, use temas musicais diferentes
para dar suporte emocional a cada capítulo."*

**É a nossa regra do cue por sequência emocional**, dita por fonte externa. `pos-producao.md` §2 já
manda o cue seguir a sequência, não o bloco. Segunda fonte, mesma conclusão.

### 2.2. A atmosfera vem antes do susto — e o stinger é LIBERAÇÃO, não a cena

🔎 O medo se constrói no **chão atmosférico** (ambiências, drones, texturas, respirações). O impacto
é o **ponto de liberação de uma tensão já construída** — *"não deve ser a cena inteira"*. Usado
errado soa *"barato e previsível"*.

**Casa direto com a nossa revelação por partes** (`bibliotecas-camera-emocao.md` §4.2): a revelação
parcial é a construção, a total é a liberação. **A trilha obedece à mesma curva que a câmera.**

### 2.3. O erro nomeado pela fonte — e é o "exagero" que o Samuel apontou

> 🔎 *"Usar um tipo só de som de terror para toda cena. **Se tudo é alto, nada se destaca.** Se todo
> susto usa o mesmo golpe áspero, a plateia se adapta."*

⚫ **É a formulação técnica do "nada de muito exagerado".** O exagero não cansa por ser intenso —
cansa por ser **uniforme**. Trilha alta o vídeo inteiro destrói o pico que ela deveria servir.

🔎 **E o corolário:** *"sons minúsculos frequentemente fazem mais do que os grandes"* — rangido leve,
mudança no ar, textura instável atrás da fala, respiração perto demais. **O silêncio faz parte do
desenho:** *"o objetivo não é ruído constante, é tensão com propósito"*.

### 2.4. Por subgênero — a única classificação que as fontes oferecem

🔎 Fonte única, e é sobre **SFX**, não música — mas transporta:

| Subgênero | O que o som faz |
|---|---|
| **Psicológico** | contenção, movimento sutil, atmosfera instável |
| **Paranormal** | respirações, sussurros, deslocamentos tonais, texturas distantes e não naturais |
| **Criatura** | mais agressão, stingers mais afiados, sons com **presença física** |

⚫ **O canal é majoritariamente "criatura", com blocos de "paranormal" na aproximação.** A revelação
da criatura — que é justamente onde o Samuel tira a voz — é o único momento que pede a linha de cima.

### 2.5. 🟢 Recursos musicais concretos, verificáveis nas obras

Estes são **Firmes** quanto a existirem na obra (fatos musicais checáveis, não opinião):

| Recurso | Obra |
|---|---|
| **Segunda menor** (um semitom) alternada com a fundamental | *Jaws* — John Williams |
| **Trítono** (E e B♭) | tema de *The Twilight Zone* |
| **Modulações repetidas + compasso 5/4** (Dó m → Lá m → Fá m → Ré m → Dó m) | *Halloween* (1978) — Carpenter |
| **Atonalidade / ruído no lugar de música** | *The Texas Chain Saw Massacre* (1974) |
| **Citação do "Dies Irae"** (canto gregoriano do séc. XIII) | *The Shining* |
| **Sintetizador como instrumento de terror** | *Suspiria* (1977) — Goblin |

> **Como isto se usa aqui, e a ressalva é séria:** é **vocabulário para escrever prompt de Suno**
> ("dissonant minor second drone", "tritone motif", "5/4 ostinato") e para **nomear** o que o Samuel
> ouviu. **Não é licença para usar os temas** — a fonte fala de compor inspirado, e nunca levanta a
> questão de licenciamento. Nada disso entra em busca da Biblioteca por nome de obra.

🔎 **Grave é a ferramenta de presença ameaçadora** — e o risco técnico declarado é o grave
"enlameado". Conversa direto com o EQ carving de `pos-producao.md` §2c.

### 2.6. ⚠️ O conflito que cai EXATAMENTE em cima do nosso caso

| Para | A fonte recomenda |
|---|---|
| Vídeo de **narração/informação** | esparsa · **sem vocal** · volume mais baixo que em outros formatos · **evitar composição dramática ou melódica demais**, porque compete com a voz |
| Vídeo **narrativo/cinematográfico** | expressiva · **não baseada em loop** · que muda quando a emoção muda |

**O nosso vídeo é as duas coisas ao mesmo tempo** — narração contínua **e** história. **A fonte não
resolve**; ela nunca considera um formato que seja os dois.

> ### ⚫ COMO RESOLVEMOS — hierarquia, não meio-termo
>
> **A narração é a espinha. A música muda por ATO, não por segundo.**
>
> - **"Pense em atos"** (§2.1) governa a **estrutura** — um cue por sequência emocional.
> - **"esparsa, sem vocal, contida"** governa o **piso técnico dentro de cada ato**.
> - **Os momentos expressivos ficam nos trechos SEM fala** — as transições, o clímax visual, e o
>   bloco de revelação onde o Samuel tira a voz de propósito.
>
> **Textura vence melodia enquanto a voz fala. Melodia é permitida onde a voz não está.**
> Isso reconcilia as duas recomendações sem escolher uma — e é exatamente onde a decisão do Samuel
> de tirar a narração na revelação passa a ter função musical, não só dramática.

### 2.7. ❌ MITOLOGIA — nada, e é a maior lacuna

**Zero menções em zero fontes.** Nenhuma orientação sobre instrumentação de época, coral, percussão
ritual, escalas modais, world music para evocar mundo mítico. A única pista é indireta e fraca
(instrumentação específica da cultura para dar "senso de lugar") — e foi dita para **vídeo de
viagem**. Falar de um lugar real não é evocar um mundo mítico. **Não trato como resposta.**

**Também não apurado:** taxonomia cena→música para terror narrativo (não se confirmou que exista uma
canônica) · BPM, tonalidade ou duração por tipo de cena · qualquer evidência empírica de que essas
técnicas funcionem com público (nenhum estudo, nenhum A/B, nenhum dado de retenção).

---

## 4. ⚫ ARQUITETURA DO CUE — desenho do Samuel, 2026-09-03

> *"As 3 primeiras cenas são calmas, então escolheríamos uma música que caia nesse quesito durante
> esse 1 min e 30. Caso a próxima cena começasse a ser uma tensão, a música calma vai abaixando e é
> substituída pela trilha de tensão pela quantidade de cenas que se enquadrem nesse tema."*

**Isto CONFIRMA a regra do cue por sequência emocional** (`pos-producao.md` §2) e acrescenta duas
coisas que não estavam escritas: a **cross-fade como mecanismo de troca** (a anterior abaixa enquanto
a nova entra — não é corte seco) e o fato de que **o cue tem duração de MINUTOS, não de bloco**.

### 4.1. 🔴 A CONSEQUÊNCIA QUE NINGUÉM TINHA VISTO — duração vira o PRIMEIRO filtro

Cue de 3 blocos = **1min30**. E a regra desta casa é dura:

> **NUNCA usar loop para preencher tempo.** (`licoes-edicao-video.md` lição 1 — o Samuel reclamou
> quando aconteceu com vídeo.) `pos-producao.md` §2 diz o mesmo para trilha: **baixar a música MAIOR
> que a sequência e cortar. Nunca menor.**

**Somando as duas: uma faixa de 1min só não serve para um cue de 1min30. Ponto.** Não há "estica",
não há "repete o refrão".

> ### Portanto: **o filtro de DURAÇÃO entra ANTES do de clima.**
>
> A Biblioteca filtra duração **em segundos** (§1.1). Para um cue de 1min30, o piso é
> **~100 s** (90 s + margem de fade dos dois lados). **É o filtro que mais elimina candidatas** —
> aplicá-lo por último é procurar faixa que já estava descartada.
>
> **Ordem de busca:** `duração ≥ (cue + 10s)` → `atribuição` → `gênero/clima` → ouvir.

**E é aqui que o Suno deixa de ser luxo e vira necessidade estrutural.** Se nenhuma faixa do clima
certo alcança a duração do cue, o Suno resolve por desenho — você especifica o tamanho. **Registrar
toda vez que isso acontecer**, porque é o dado que diz onde a Biblioteca não cobre o canal.

### 4.2. A cross-fade, e por que ela é a operação mais defensável

Trocar cue por **cross-fade** (a calma descendo enquanto a tensão sobe) sobrepõe duas faixas por
alguns segundos. **Nenhuma das duas é alterada** — são camadas, não remix. É a operação de edição
menos agressiva que existe, e vale registrar isso porque é o que sustenta a §5.

⚫ **O ponto de troca é a virada da cena, não o corte de bloco.** A emenda narração → diálogo →
narração já é ponto de corte natural; a virada de clima é outro.
Quando os dois coincidem, é ali que a troca de cue fica invisível.

---

## 5. ⚠️ EDITAR A FAIXA — o caminho seguro, apurado em 2026-09-03

> ⚫ **Pergunta do Samuel:** *"verifique o caminho mais seguro para podermos usar isso sem problema."*
> A arquitetura da §4 exige **cortar** (faixa maior que o cue), **aplicar fade** (entrada e saída) e
> **sobrepor** (cross-fade). A pergunta é se a licença permite.

### 5.1. 🟢 A Google NÃO DIZ — nem sim, nem não

**A documentação não contém as palavras editar, cortar, remixar, modificar, fade ou mixagem.** Em
nenhum dos dois idiomas. Ela descreve interface, licença, download e monetização, e **para**.

E isso não vai mudar: a própria página declara que *"não podemos oferecer orientação jurídica"*.
**Esperar que ela um dia responda é esperar sentado.**

### 5.2. 🟢 A CC BY 4.0 DIZ SIM, por escrito, e é irrevogável

Fonte primária — o texto da própria licença:

> *"**Adapt** — remix, transform, and build upon the material **for any purpose, even
> commercially**."* · *"The licensor **cannot revoke** these freedoms as long as you follow the
> license terms."*

**Cortar, aplicar fade e fazer cross-fade cabem inteiramente dentro de "adapt/transform".** Não
existe operação de edição de vídeo comum que caia fora desse guarda-chuva.

> ### ⚠️ E A CLÁUSULA QUE TODO MUNDO ESQUECE
>
> A CC BY 4.0 exige **três** coisas, não duas: crédito · link da licença · **"indicate if changes
> were made"**.
>
> **O botão "Copiar" do Studio gera o crédito do autor — ele NÃO sabe que você cortou e aplicou
> fade.** Assim que a faixa é editada, o texto colado fica **incompleto**. Acrescentar algo como
> *"faixa editada (corte e fade)"* custa cinco palavras e é o que a fonte primária pede.
>
> ⚫ **Isso entra no template de descrição da skill `postagem`.** Cue CC editado sem essa linha é
> descumprimento de licença — e o nosso fluxo edita **todos** os cues, por desenho.

### 5.3. ❌ A licença padrão — vazio documental, nos dois sentidos

**O texto da licença padrão não foi localizado em fonte nenhuma.** Nem a Google o descreve, nem
secundária alguma o cita literalmente. Portanto, para a fatia "Atribuição não é necessária":
**não confirmei que pode, e não confirmei que não pode.**

**A "regra" de que não se pode remixar é 🪤 LENDA, e a origem foi rastreada.** Duas fontes (Lickd
2021, Voicy 2024) publicam a mesma lista de oito regras, quase palavra por palavra, e **as duas
dizem que a origem é "o canal da YouTube Audio Library"** — um canal do YouTube, **não** a
documentação. Quatro motivos para rebaixar: origem não-primária · duas fontes copiando a mesma
origem não são duas fontes · **contradiz frontalmente a CC BY 4.0**, que é primária · e ambas vendem
o catálogo concorrente.

⚠️ **O que isso NÃO autoriza:** a lenda ser fraca não transforma o vazio em permissão.

### 5.4. ⚫ A DECISÃO — e ela INVERTE a recomendação de 02/09

> **Ontem a recomendação foi "Atribuição não é necessária" como estado padrão**, pela lógica de não
> criar dívida de crédito na descrição. **Aquilo valia para faixa usada inteira. Não vale para o
> nosso fluxo**, que corta e sobrepõe TODOS os cues por desenho (§4).

**O risco é assimétrico, e é isso que decide:**

| | Permissão de editar | Preço |
|---|---|---|
| **Creative Commons** | **escrita, primária, irrevogável** | uma linha na descrição, com a menção à alteração |
| **Licença padrão** | **nenhuma — vazio documental** | zero |

> ### A regra
>
> **Cue que vai ser trabalhado (cortado, com fade, em cross-fade) → preferir faixa CREATIVE
> COMMONS.** É o único caminho em que a permissão está escrita, e ela não depende da boa vontade de
> ninguém.
>
> **Faixa de licença padrão → usar inteira ou quase inteira** (fade de entrada e saída, corte de
> duração para caber). Não porque a proibição esteja provada — **porque a permissão não está.**
>
> **Escolher a faixa pela LICENÇA antes de escolher pela vibe.** É um clique de filtro, e inverte a
> ordem de trabalho de um jeito que economiza retrabalho.

**A honestidade que acompanha a regra:** não existe **um único caso documentado** de alguém
penalizado por cortar faixa da Biblioteca — zero exemplos em seis fontes. Cortar e dar fade em
música de biblioteca é o que o mundo inteiro faz, e uma licença que entrega MP3 "para usar nos seus
vídeos" e proibisse ajustar duração seria inutilizável para a própria finalidade que declara.
**Mas isso é argumento de razoabilidade, não é fonte** — e "todo mundo faz" não é apoio documental.

### 5.5. O que fica em aberto, e a ação de melhor retorno

- ❌ **O texto da licença padrão** — nunca localizado. É o que fecharia a questão.
- ❌ **Se editar quebra a promessa de não-reivindicação do Content ID.** A Google promete para faixa
  da Biblioteca; ninguém fala de faixa **editada**.
- ❌ **Se a monetização sobrevive à edição.** As fontes dizem que se pode monetizar vídeo que **usa**
  a faixa. Nenhuma diz "usa editada".
- ❌ **A versão da CC nas faixas do YouTube.** Foi aplicado o texto da **4.0**; a Google não nomeia
  versão. Conferir na faixa antes de contar com a cláusula de adaptação.
- 🔎 **A ação de melhor retorno:** a fonte on-topic mais recente (LicenseOrg, 2026-03-02) tem uma
  tabela "All License Details" cujos **nomes de campo não sobreviveram à captura** — onze linhas de
  ✓/✗ sem rótulo. **Uma delas pode ser literalmente "modification allowed".** Abrir a página num
  navegador e passar o mouse nos rótulos é um minuto de trabalho.

---

## 6. O QUE FAZER NO PRÓXIMO VÍDEO

1. **Pedir ao Samuel a lista de gêneros e climas da Biblioteca** (§0) — destrava a receita de busca.
2. **Decidir se os Shorts atravessam** para fora do YouTube (§1.3) — muda a licença do cue.
3. **Filtro "Atribuição não é necessária" ligado por padrão**, salvo a decisão acima.
4. **Registrar cada cue escolhido**: gênero + clima + duração + veredito do Samuel. Em três vídeos
   isso vira a tabela cena→música que a pesquisa não achou pronta — **medida na nossa produção,
   que é fonte melhor que os três blogs.**
5. **Preencher a paleta de `pos-producao.md` §2** com o que a Biblioteca de fato cobriu, e registrar
   qual clima obrigou a cair no Suno.

6. **Cue de 1min30 → filtrar duração ≥ ~100 s ANTES de tudo** (§4.1). Faixa curta não vira cue longo:
   loop é proibido nesta casa.
7. **Cue que vai ser cortado e cross-fadeado → preferir Creative Commons** (§5.4), e o crédito
   precisa dizer que a faixa foi **alterada**.
