---
name: pesquisa-seres
description: >
  Pesquisa e dossiê de fontes sobre SERES/PERSONAGENS de qualquer natureza e QUALQUER NICHO, sem
  restrição — mitológicos, folclore, lendas urbanas, criptídeos, figuras históricas, anime/mangá,
  HQs/super-heróis (mesmo com IP protegido), domínio público — cruzando WEB e TRANSCRIÇÕES DE
  YOUTUBE (nunca só web). Use SEMPRE que o usuário disser "pesquisa sobre [X]", "levanta a lore de
  [X]", "o que se sabe sobre [X]", "monta o dossiê de [X]", quiser material antes do roteiro, ou
  usar vídeo do YouTube como fonte. Entrega TRÊS produtos: (1) DOSSIÊ com cada afirmação
  classificada por camada de fonte e veredito em três níveis (Firme/Mediana/Reza a lenda), fontes
  creditadas; (2) NARRATIVA LINEAR RICA para visualizar cenas; (3) SUGESTÃO DE HISTÓRIA — 3
  histórias famosas paralelas, sem número fixo de blocos (o usuário decide o tamanho a cada vídeo).
  Alimenta a skill whoiam. NÃO produz roteiro/prompts.
---

# Pesquisa de Seres — Dossiê de Fontes

Reúne o material de um ser/personagem ANTES do roteiro. O produto não é "um resumo": é um dossiê
onde cada afirmação vem com a origem rastreada, para o usuário decidir o que é lore firme e o que é
"reza a lenda". A geração de roteiro fica com a skill `whoiam`; esta skill só entrega o material julgado.

## PRINCÍPIO CENTRAL — leia antes de qualquer coisa

**Rastreabilidade até a origem vence contagem de repetição.** O erro que arruína um canal deste tipo
é confundir "aparece em todo lugar" com "é verdade". Mito e lenda viralizam justamente por serem
repetíveis; o detalhe correto costuma estar na fonte primária, que quase ninguém leu e por isso
aparece POUCO.

Consequências práticas, que valem como regra:
- NUNCA ordenar ou priorizar informação por "quantas vezes apareceu". Isso coloca o boato viral no topo
  e enterra o fato original. Ordenar SEMPRE por camada da fonte (primária no topo).
- Dez canais dizendo o mesmo quase nunca são dez confirmações — normalmente é uma fonte copiada dez vezes.
  Só conta como várias fontes se forem INDEPENDENTES entre si (ver "Regra da independência").
- Uma afirmação sem nenhuma fonte primária ou secundária NÃO é falsa — é "reza a lenda". Não descartar;
  reclassificar. O canal opera no registro do mito, então "reza a lenda" é uso legítimo, desde que MARCADO.

## O QUE ESTA SKILL FAZ vs. NÃO FAZ

**SEM RESTRIÇÃO DE NICHO (decisão jul/2026 — vale para toda pesquisa, sempre):** mitologia,
folclore, criptídeo, figura histórica, personagem de anime/mangá, super-herói de HQ, ou qualquer
outro tipo de ser/personagem — a pesquisa roda igual, sem perguntar se está "dentro do escopo".
Status de IP (domínio público ou protegido) NÃO impede a pesquisa: reunir e classificar informação
factual sobre um personagem é pesquisa, não reprodução — mesma lógica de um verbete de
enciclopédia. Restrição de reprodução de IP protegido (se houver) é assunto da PRODUÇÃO
(`whoiam`), nunca desta skill.

**Faz:** busca na web + coleta de conteúdo de vídeos do YouTube; classifica cada afirmação por camada
de fonte; emite veredito em três níveis; detecta cópias entre fontes; monta o dossiê com links para
crédito; sinaliza divergências entre fontes.

**Não faz:** decidir sozinha o que entra no roteiro (entrega classificado, o usuário decide);
afirmar que algo é fato histórico (o registro do canal é o mito); inventar lore não encontrada nas
fontes; transcrever vídeo "magicamente" — a coleta de YouTube segue a escada da seção COLETA, e a
transcrição automática depende do ambiente — SONDAR antes de prometer (ver Frente 2; roda sozinha
no Cowork com allowlist de rede, não roda no chat do Claude.ai).

---

## COLETA — a pesquisa NUNCA é só web

Toda pesquisa cobre, no mínimo, duas frentes. Buscar só na web é considerado incompleto.

### Frente 1 — Web
Priorizar, nesta ordem: edições/traduções de textos primários e registros de época, enciclopédias
e artigos de pesquisadores, e só então material de divulgação. Registrar a URL de cada afirmação usada.

### PESQUISA NATIVA — criaturas de culturas de outro idioma

Fonte no idioma nativo está estruturalmente mais perto da camada primária (material em PT sobre
yokai é quase todo tradução de tradução = terciário). Para ser de cultura não-lusófona/anglófona:

1. **PASSO ZERO — resolver o nome nativo ANTES de buscar:** grafia original (kanji/cirílico/etc.),
   romanizações, variantes e nomes regionais. Buscar "Kappa" acha pouco; buscar 河童 acha o acervo.
2. **Buscar nos dois idiomas em paralelo** (nativo + PT/EN), formulando as queries nativas
   diretamente no idioma. Fontes nativas têm prioridade para as camadas primária/secundária.
3. **YouTube nativo:** buscar vídeos no idioma e transcrever a legenda ORIGINAL
   (`--langs ja` etc.) — nunca a legenda auto-traduzida do YouTube (tradução sobre ASR degrada
   duas vezes). Claude lê o original e traduz uma vez só.
4. **Auditabilidade da tradução (obrigatório):** o usuário não confere o idioma original, então
   erro de tradução é invisível. Para afirmações FIRMES vindas de fonte nativa, incluir no dossiê
   um trecho curtíssimo no idioma original ao lado da tradução; lista de fontes com título
   original + título traduzido.
5. **Nativo ≠ confiável:** site pop nativo é terciário igual. As camadas e a regra da independência
   se aplicam sem desconto.
6. **Escopo honesto:** para idiomas de poucos recursos (línguas indígenas, dialetos pequenos), a
   leitura nativa é fraca — apoiar-se em fontes acadêmicas (geralmente em inglês) sobre aquela
   cultura e DECLARAR no dossiê que a cobertura nativa não foi possível.

Todo o dossiê e a narrativa saem em PT-BR, independentemente dos idiomas pesquisados.

### Frente 2 — YouTube (coleta com sondagem de ambiente)

**PASSO 0 — SONDAR O AMBIENTE, nunca assumir.** O acesso a youtube.com varia por ambiente
(bloqueado no chat do Claude.ai; liberado no Cowork/Claude Code se o usuário adicionou
`youtube.com` e `*.youtube.com` à allowlist de rede). Antes de escolher o caminho, testar com
uma requisição barata:
```bash
curl -sI --max-time 10 https://www.youtube.com/ | head -3
```
- Resposta HTTP normal → **MODO AUTÔNOMO** (abaixo).
- `403` + `x-deny-reason: host_not_allowed` (ou timeout) → **MODO ASSISTIDO** (abaixo).
  Nesse caso, avisar o usuário em uma linha que a rede está bloqueada neste ambiente e que
  no Cowork (com os domínios na allowlist) a coleta roda sozinha.

**Identificação dos vídeos (ambos os modos).** Buscar na web 2–4 vídeos sobre o ser. Registrar
título + canal + URL. Vídeo indicado pelo usuário tem prioridade absoluta. **Regra dura contra o
viés de seleção:** os primeiros resultados de busca são os mais virais, ou seja, o topo da câmara
de eco. Ao menos UM vídeo transcrito deve ser de canal com cara de pesquisa (cita fontes,
distingue versões). O dossiê declara QUAIS vídeos foram escolhidos e POR QUÊ, para o usuário
auditar a seleção, não só o conteúdo.

**MODO AUTÔNOMO (rede liberada):** rodar o script embutido em cada vídeo:
```bash
pip install youtube-transcript-api  # uma vez
python scripts/transcrever_youtube.py "<URL>" --langs pt en --out transcricao_<slug>.txt
```
Vídeo sem legenda → o script avisa e sai; não insistir, buscar outro vídeo.

**MODO ASSISTIDO (rede bloqueada):** em ordem:
1. Pedir a transcrição ao usuário (~20s por vídeo): abrir o vídeo → descrição → "...mais" →
   **"Mostrar transcrição"** → selecionar tudo → copiar → colar no chat.
2. Fallback oportunista: buscar "[título do vídeo] transcript" e tentar web_fetch em páginas que
   indexam transcrições. Se o texto parecer truncado/corrompido, descartar e voltar ao passo 1.

**HIGIENE DE TOKENS (ambos os modos):**
- Transcrição SEMPRE vai para arquivo (`--out`), nunca despejada inteira na resposta ao usuário.
- Citar no dossiê apenas trechos curtos, com atribuição (título + canal + URL).
- Vídeo longo (>20 min): não ler a transcrição inteira — localizar o nome do ser e termos-chave
  dentro do arquivo (grep) e ler os trechos ao redor.
- O usuário não precisa ver a transcrição; precisa ver o que foi EXTRAÍDO dela e de onde veio.

**REGRA ABSOLUTA: não inventar transcrição.** Se nenhum caminho trouxe o texto, o vídeo entra no
dossiê apenas como "fonte identificada, não transcrita" — sem afirmações extraídas dele. Nunca
travar a pesquisa num vídeo só.

A transcrição entra como QUALQUER outra fonte: passa pela mesma classificação, não ganha peso por ser vídeo.

---

## PERGUNTAS DO USUÁRIO (opcional) — decisão ago/2026

Junto do pedido de pesquisa, o usuário pode listar dúvidas específicas ("pesquisa sobre Cthulhu, mas
quero saber se ele é imortal e o que é R'lyeh"). Isso não é um pedido à parte — é prioridade de
investigação dentro da MESMA pesquisa, com a mesma régua de camada/veredito de sempre. Nenhuma
pergunta autoriza atalho na classificação; só muda o que se busca primeiro e onde a resposta aparece.

- Cada pergunta vira, no mínimo, uma busca dedicada (não esperar que ela apareça de bônus na busca geral).
- A resposta entra classificada como qualquer afirmação (camada + veredito + origem) — "não sei" com
  fonte primária ausente é resposta válida, não falha.
- As respostas abrem o dossiê, na seção **"RESPOSTAS ÀS PERGUNTAS"** (ver FORMATO DO DOSSIÊ), para o
  usuário achar sem caçar no meio do resto. O resto do dossiê continua sendo produzido por completo —
  perguntar sobre um ponto não reduz a cobertura geral.
- Sem perguntas no pedido → a seção não aparece; nada muda no restante do fluxo.

---

## CENSO DE VERSÕES — obrigatório ANTES da classificação

Muitos seres têm mais de uma versão — regional, temporal, ou moral (a doce e a sombria) — e a
busca ingênua devolve só a mais famosa, sem nenhum conflito que denuncie a mutilação. Caso
registrado (jul/2026): o Saci voltou apenas na versão travessa infantil; a versão sombria das
raízes (o redemoinho, as ligações com Yaci-Yaterê/Matinta-Pereira) ficou de fora — e o dossiê
parecia completo. Divergência só é detectável quando as fontes conflitam sobre a MESMA afirmação;
versão paralela não conflita — ela simplesmente não aparece se não for procurada.

Portanto, para TODO ser, antes de classificar:
1. Buscar ativamente por variantes: "[ser] versão original", "[ser] versão sombria/maligna",
   "[ser] variantes regionais", "[ser] folclore origem", nomes alternativos e seres aparentados
   — nos idiomas da pesquisa (incl. nativo, quando aplicável).
2. O dossiê ganha a seção **"VERSÕES DO SER"** logo após o cabeçalho: cada versão encontrada com
   uma linha de identidade, sua camada de fonte e veredito próprios, e a marcação explícita de
   qual é a MAIS POPULAR e qual a MAIS ANTIGA rastreável (frequentemente não são a mesma —
   a popular costuma ser a suavizada).
3. NUNCA presumir versão canônica única. Se só uma versão foi encontrada após busca ativa,
   declarar no dossiê: "busquei variantes e não encontrei" — ausência verificada é diferente de
   ausência por não procurar.
4. O usuário escolhe qual versão (ou mistura) vai para a produção; a pesquisa entrega todas.
5. **SER-CATEGORIA (caso Long, jul/2026):** se o ser pesquisado for uma FAMÍLIA/categoria e não um
   indivíduo (Long chinês, yokai como classe, fadas, djinn como povo), o dossiê NUNCA entrega uma
   lista plana de "tipos" — cada classificação encontrada recebe o rótulo do seu EIXO:
   - **espécie/tipo** = seres distintos dentro da família (Tianlong ≠ Dilong ≠ Jiaolong);
   - **indivíduo nomeado** = membros específicos (os Reis-Dragões dos quatro mares);
   - **patente/status** = o mesmo ser em hierarquia (nº de garras do Long = posto imperial, não biologia);
   - **estágio de vida** = o mesmo ser amadurecendo (jiao → long → yinglong em certas tradições);
   - **papel cosmológico** = o ser como função (Qinglong entre os Quatro Símbolos);
   - **prole/aparentados** = criaturas-filhas ou associadas (os Nove Filhos do Dragão).
   Quando as fontes divergem sobre se algo é espécie ou estágio (acontece), registrar a divergência —
   é lore valiosa, não ruído. E perguntar ao usuário o ESCOPO do vídeo: um membro específico da
   família, ou a família inteira como história.

## CLASSIFICAÇÃO — as três camadas

Para CADA afirmação recolhida, atribuir a camada da fonte mais forte que a sustenta:

- **PRIMÁRIA** — a origem em si, não alguém falando sobre ela. O que conta como primária DEPENDE do
  tipo de ser (ver tabela abaixo).
- **SECUNDÁRIA SÉRIA** — pesquisador, enciclopédia, obra acadêmica, museu, canal de YouTube claramente
  de pesquisa (cita fontes, distingue versões). Fala SOBRE o ser com rigor.
- **TERCIÁRIA** — canal de conteúdo/viral, fan wiki, post de SEO, agregador. Repete sem rastrear origem.
  Não é lixo — é onde vive o embelezamento popular — mas não sustenta afirmação como fato.

### O que conta como PRIMÁRIA, por tipo de ser

| Tipo de ser | Fonte primária é... |
|---|---|
| Mitologia clássica/religiosa | O texto mítico original ou tradução direta (Hesíodo, Ovídio, Eddas, Gilgamesh, texto bíblico) |
| Folclore tradicional | Coletânea com registro de campo (ex.: Croker, Grimm, Câmara Cascudo), datada e localizada |
| Lenda urbana | O registro mais antigo rastreável: jornal de época, post/thread original, estudo folclorístico que documenta a primeira aparição |
| Criptídeo | Relato de testemunha documentado, boletim/registro oficial, reportagem de época sobre o avistamento original |
| Figura histórica lendária | Documento de época (crônica, registro paroquial, correspondência) — separando o que é registro do que é lenda posterior |
| Personagem literário (domínio público) | O texto original da obra |
| Personagem de mídia moderna (anime/mangá, HQ/super-herói, mesmo com IP protegido) | A obra original (o mangá/anime/HQ em si — episódio, capítulo, edição específica), nunca wiki de fã ou resumo de terceiro |

Quando a mesma afirmação aparece em várias camadas, vale a mais forte. Quando uma afirmação vistosa só
existe na camada terciária, marcar como **"reza a lenda"** — utilizável no roteiro, mas nunca como fato.

## REGRA DA INDEPENDÊNCIA — contra a câmara de eco

Antes de contar "N fontes dizem X", verificar se são independentes:
- Se duas fontes usam a mesma frase, o mesmo detalhe específico e incomum, ou uma cita/repete a outra,
  contam como UMA só. Sinalizar: "aparece em 6 páginas, mas ~1 origem repetida".
- Independência real = chegaram à afirmação por caminhos diferentes (ex.: uma tradução da Edda + um
  artigo acadêmico que discorda em parte). Divergência entre fontes independentes é SINAL VALIOSO,
  não ruído a suavizar — mostrar as duas versões ao usuário.

## VEREDITO — os três níveis de leitura

Cada afirmação recebe, além da camada, um veredito único, derivado da camada + independência
(NUNCA da frequência de aparição):

- **FIRME** — sustentada por fonte primária, ou por secundária séria com ≥2 fontes independentes.
  Pode ser narrada com firmeza.
- **MEDIANA** — uma única fonte secundária, ou fontes independentes que divergem entre si.
  Usável com marcador leve ("segundo alguns registros...").
- **REZA A LENDA** — só camada terciária, independente de quantas vezes apareceu.
  Usável apenas com marcador de transmissão ("dizem que...", "conta-se que...").

---

## FORMATO DO DOSSIÊ (o entregável)

Duas coisas ficam SEPARADAS de propósito: **crédito** (quem usei, a creditar no "sobre" do vídeo) é
diferente de **peso** (quão confiável é). Creditar um canal não valida a informação dele.

### 0. Respostas às perguntas do usuário (só se ele fez alguma — ver seção acima)
Uma resposta direta por pergunta, no formato normal de afirmação (camada + veredito + origem).
Abre o dossiê, antes de qualquer outra seção.

### 1. Afirmações da lore (ordenadas por camada — primária primeiro)
Uma linha por afirmação:
> **[afirmação, em uma frase]** — Veredito: `FIRME` / `MEDIANA` / `REZA A LENDA` ·
> Camada: `PRIMÁRIA`/`SECUNDÁRIA`/`TERCIÁRIA` · Fontes independentes: `N` · Origem: [nome/link]

Divergências marcadas explicitamente:
> ⚠️ **Divergência:** a versão A (fonte primária X) diz [...]; a versão B (terciária, popular) diz [...].

### 2. Fontes usadas — a creditar no "sobre" do vídeo
Lista simples de tudo que foi consultado e aproveitado, com link. Inclui vídeos de YouTube
(título + canal + URL), inclusive os "identificados, não transcritos" se algo deles foi usado
indiretamente. Esta lista é sobre DAR CRÉDITO, não sobre confiabilidade.

### 3. Recomendação de uso (curta)
2–3 linhas: o que dá para narrar como lore firme e o que só entra como "reza a lenda".
Sem decidir pelo usuário — recomendar e deixar ele escolher.

---

## NARRATIVA LINEAR RICA (rascunho de compreensão de cena)

Segundo produto, entregue JUNTO do dossiê. Não substitui o dossiê — o dossiê é para JULGAR, esta
narrativa é para o usuário VISUALIZAR as cenas. Prosa corrida, sensorial, na ordem que o usuário
pensa o vídeo.

**Não confundir com o Documento 1 da `whoiam`.** O Documento 1 segue a narração dissociada (a voz narra
só o mito, nunca a ação humana da tela). Esta narrativa é o OPOSTO: é a história inteira contada para o
usuário entender e imaginar. É insumo de planejamento, não texto de locução.

**ORDENAÇÃO — origem primeiro, depois características.** Regra do usuário. Mas com uma trava de
honestidade, porque pôr a origem em primeiro lugar pressiona a inflá-la:
- Se o ser TEM origem sólida (veredito FIRME) → abrir contando a origem com firmeza.
- Se a origem é INCERTA (MEDIANA ou REZA A LENDA) → **abrir pelo próprio mistério**: "ninguém sabe ao
  certo de onde ele veio; a versão mais contada diz que...". O mistério vira o gancho. NUNCA transformar
  origem especulativa em origem aparentemente certa só porque vem primeiro.
- "Mais repetida" nunca vira "mais forte". Se a origem é popular mas frágil, dizer isso na própria narrativa.

**DETALHE — o que é livre e o que é proibido.**
- LIVRE: detalhe sensorial, atmosférico e cinematográfico (luz, textura, som, movimento, enquadramento,
  clima). É a matéria-prima das cenas e é cor legítima de mito.
- PROIBIDO: inventar FATO de lore que não está nas fontes só para encher. Enfeite de câmera, sim;
  fato falso, não.

**MARCAÇÃO INLINE.** Dentro do fluxo, sinalizar em itálico entre parênteses a procedência dos blocos.
Ex.: *(firme — Croker, 1825)* / *(reza a lenda — só terciária)*.

O comprimento acompanha a densidade do ser e o número de cenas que o usuário planeja — passagens
cobrindo origem → natureza/poderes → característica marcante → fechamento perturbador, sem
duração-alvo de vídeo.

---

## SUGESTÃO DE HISTÓRIA PARA PRODUÇÃO (terceiro produto, decisão jul/2026 — sem teto de blocos)

A narração de fundo conta a CRIATURA (lore, natureza, poderes — a narração dissociada de sempre,
ver Documento 1 da `whoiam`); as CENAS recriam uma história famosa dela. Este produto
existe para dar ao usuário a matéria-prima dessa fusão, com mais nuance do que uma leitura corrida
entrega — sem decidir por ele, e SEM presumir quantos blocos o vídeo vai ter (o usuário varia isso
por produção — às vezes ~10, às vezes ~20+, conforme o fôlego daquele vídeo específico; nenhum
número é o padrão do canal). Ver Passo 3 na `whoiam`: nº de blocos = nº de cenas que o
usuário descrever, sem teto embutido em skill nenhuma.

**Entregar sempre, junto do dossiê e da narrativa linear: TRÊS histórias candidatas, paralelas**
(não uma principal + alternativas secundárias — três opções de peso equivalente, para o usuário
escolher ou misturar). Para CADA uma das três:

1. **Identificação e veredito próprio** — nome/situação da história, com seu PRÓPRIO veredito
   (Firme/Mediana/Reza a lenda — a história pode ser mais ou menos firme que os fatos básicos da
   criatura; frequentemente é mais lendária que a natureza dela).
2. **Resumo em beats** — início → complicação → virada → clímax → desfecho (nem toda história tem
   os cinco; mesma lógica de "estados do arco" da direção cinematográfica).
3. **Contagem de beats naturais** — quantos momentos distintos a história realmente tem, sem
   encaixar em nenhum número-alvo de blocos. Informar isso como dado bruto; se o usuário quiser um
   vídeo mais longo, cada beat pode se desdobrar em várias cenas (2, 3, o quanto ele quiser); se
   quiser mais enxuto, apontar quais beats são o núcleo inegociável do arco e quais são opcionais
   de cortar. A decisão de tamanho é do usuário a cada vídeo, não uma calibragem fixa desta skill.
4. **Pitch de uma linha** — por que essa versão em particular rende cena boa (visual, dramática,
   ou por ser a mais reconhecível do público).

Ao final das três, uma nota curta de **PONTE COM A LORE**: quais afirmações FIRMES do dossiê
(natureza, poderes, características) se encaixam bem como narração durante os momentos-chave das
histórias apresentadas — sugestão de onde lore e cena se cruzam, não obrigação.

**Isso é sugestão, não decisão.** O usuário lê as três, escolhe uma, mistura, ou ajusta como quiser,
e descreve as cenas do jeito que preferir — a `whoiam` continuam gerando pelo número de
cenas que ELE descrever, nunca um total fixo imposto por aqui.

---

## ENTREGA E ENCAIXE COM A `whoiam`

- Salvar o dossiê em `output/` e entregar via present_files quando disponível.
- O dossiê é o INSUMO da `whoiam`: as afirmações FIRMES entram como lore firme; as MEDIANAS com
  marcador leve; as REZA A LENDA no registro mítico (marcadores de transmissão + registro de lenda
  na imagem, como a `whoiam` já opera).
- Não duplicar trabalho: esta skill NÃO escreve roteiro nem prompts, e a sugestão de história
  (produto 3) não decide cenas — só entrega material julgado e opções para o usuário decidir.

## MODOS DE FALHA A EVITAR

- Ordenar por popularidade "porque é mais fácil de ler" → reintroduz o boato no topo. NÃO fazer.
- Contar cópias como confirmações → inflar a confiança de um boato. Aplicar a regra da independência.
- Tratar YouTube como mais fraco por padrão, ou mais forte por ser vídeo → errado nos dois sentidos;
  vídeo é classificado pelo conteúdo da fonte, igual a qualquer outra.
- Descartar a lenda vistosa por "não ser verdade" → o canal é de mito; reclassificar como "reza a
  lenda", não jogar fora.
- Pesquisar só na web sem nem tentar a escada do YouTube → viola o princípio da skill.
- **Inventar ou "reconstruir" transcrição de vídeo que não foi obtida** → falha grave; se não há
  texto, não há texto.
- Aplicar a régua mitológica de "primária" a um criptídeo ou lenda urbana → usar a tabela por tipo de ser.
- Devolver só a versão mais famosa do ser sem censo de versões → mutilação invisível (caso Saci);
  o censo é obrigatório e ausência de variantes só se declara após busca ativa.
- Entregar ser-categoria como lista plana de "tipos" sem rotular o eixo de cada classificação
  (espécie × patente × estágio × papel × prole) → confusão garantida (caso Long).
