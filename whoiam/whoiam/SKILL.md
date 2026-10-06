---
name: whoiam
description: >
  Pipeline completo de PRODUÇÃO para o canal WhoIAm (YouTube de mitologia/criaturas com IA).
  Use SEMPRE que o usuário pedir para "gerar o vídeo de [X]", "criar os prompts para [X]",
  planejar storyboard, gerar narração (ElevenLabs v3), sugerir cortes/melhores momentos,
  converter mídia (frames, GIF, cortes), orçar créditos do Higgsfield, montar a ficha de
  controles do Cinema Studio, ou organizar o processo de um vídeo do canal. Também dispara
  quando o usuário descreve cenas ou opina sobre momentos de um vídeo em produção. Entrega um
  pacote de produção: roteiro, prompts de imagem, prompts de vídeo (Seedance 2.5 / Cinema
  Studio Video no Higgsfield) com ficha de controles e orçamento em créditos, roteiro marcado
  para ElevenLabs v3, plano de cortes para Shorts. SEO/thumbnail/calendário de postagem NÃO
  são desta skill — é a skill `postagem`. FRONTEIRA: se o pedido é PESQUISAR/levantar a lore
  de um ser (antes de produzir), isso é a skill `pesquisa-seres`. Esta skill começa quando a
  produção começa.
---

# WhoIAm — Pipeline de Produção

Canal de YouTube sobre mitologia e criaturas, produzido com IA. A partir de um tópico (criatura + ideia de cenas),
esta skill conduz a produção de um vídeo inteiro, do roteiro à publicação assistida.

## PLATAFORMA — leia antes de qualquer coisa (migração ago/2026)

A geração de vídeo saiu do **Leonardo** e foi para o **Higgsfield**. Isso não é troca de fornecedor:
muda o preço por segundo, o limite de duração, onde mora a direção de câmera e o que a skill pode
executar sozinha. **Antes de gerar ou orçar qualquer coisa, ler `references/higgsfield-cinema-studio.md`.**

Os quatro fatos que mudam decisão:

1. **Modo HÍBRIDO** (decisão do usuário): imagens pelo MCP (1–2 créditos, praticamente grátis);
   **vídeo no Cinema Studio na web**, onde ficam os controles de direção e os benefícios do plano —
   que, por regra do próprio Higgsfield, **não valem via MCP**.
2. **Vídeo é caro e é o gargalo do canal.** Seedance 2.5 em 720p custa 6,5 créditos/segundo; o plano
   Ultra dá 3.000 créditos/mês. Um vídeo de 10 min todo em Seedance 2.5 custa mais que um mês inteiro
   de plano. O número de blocos deixou de ser só decisão editorial e passou a ter portão de custo.
3. **DECISÃO DO USUÁRIO (28/08/2026): sempre Seedance 2.5, sempre 30s.** O roteamento AÇÃO→Seedance
   2.5 / SIMPLES→Cinema Studio Video que existia até aqui foi **descontinuado por decisão explícita**
   — todo bloco, ação ou contemplativo, sai em Seedance 2.5 a 30s. Duração de bloco volta a ser
   **constante** (30s), o que simplifica orçamento de narração, edição e o cálculo de custo.
   **Por que isso não é desperdício de crédito:** a comparação que justificava o roteamento (seção 3
   de `higgsfield-cinema-studio.md`) usava Seedance 2.5 a 720p (6,5 cr/s) contra Cinema Studio Video —
   mas a regra permanente do canal é **sempre 480p** (seção 1b de `recursos-higgsfield-quando-usar.md`),
   e a 480p o Seedance 2.5 custa **2,5 cr/s**, muito perto do Cinema Studio Video. A economia que a
   antiga tabela media não existe mais na prática porque o denominador mudou. `references/higgsfield-
   cinema-studio.md` seção 3 fica **como registro histórico**, não como regra ativa — ver nota lá.
4. **A direção de câmera migra do texto para os controles.** Gênero, era, tempo de montagem, câmera,
   lente, abertura, movimento e emoção são parâmetros do Cinema Studio, não frases do prompt. Todo
   bloco entrega **prompt + ficha de controles**. A âncora de realismo é a única coisa técnica que
   permanece obrigatoriamente no texto.
5. **A ESCOLHA DOS RECURSOS É TRABALHO DESTA SKILL, NÃO DO USUÁRIO** (pedido explícito, ago/2026).
   Ele descreve o que acontece na cena e não é diretor de cinema — não vai pedir `speedramp: impact`
   num soco, nem `end_image` numa metamorfose, nem lembrar que reenquadrar Short no Higgsfield custa
   145 créditos e no ffmpeg custa zero. **A skill propõe, com justificativa dramática e custo; o
   usuário aprova.** Tabela de decisão: `references/recursos-higgsfield-quando-usar.md` — ler junto
   com a referência de plataforma, antes de qualquer bloco.

> ⚠️ **ANTES DE TUDO, ler também `references/seedance-2-5-e-regras-2026-08.md`.** É mais recente
> que este bloco PLATAFORMA e que `higgsfield-cinema-studio.md` — **vence em conflito.** Ele corrige
> três coisas: (1) **resolução é SEMPRE 480p** (`resolution: "480p"` escrito por extenso em toda
> chamada de vídeo — o padrão da plataforma é 720p e omitir o parâmetro cobra 720p sem avisar; o
> upscale roda depois, na pós, de graça na RTX 3050 da casa — não 720p/1080p "nativo por vitrine"
> como uma leitura anterior desta skill chegou a supor); (2) confirma a decisão do Samuel de **não
> produzir storyboard como artefato separado**, com a ressalva de que as perguntas P2/P3 do estudo
> ainda não foram respondidas; (3) traz o **formato de prompt do Seedance 2.5** direto de uma aula
> transcrita pelo Salomão — goal · references · continuity · stages · look · camera+performance ·
> negatives — e o que fazer **quando um bloco sai errado** (recortar o quadro bom e reusar como
> referência, antes de reescrever texto). Estudo do Salomão ainda tem 6 perguntas em aberto (P2–P7,
> listadas no arquivo) — não decidir por conta própria nenhuma delas.

## O QUE ESTA SKILL FAZ vs. NÃO FAZ — leia antes de prometer qualquer coisa

**Roda aqui, no chat (entrego pronto):** roteiro, prompts de imagem, prompts de vídeo + ficha de
controles do Cinema Studio, orçamento em créditos, roteiro de narração marcado para ElevenLabs v3
(ver `references/narracao-elevenlabs-v3.md`), mapa de trilha, mapa de edição CapCut, plano de
cortes/Shorts, planejamento de storyboard. SEO/thumbnail/publicação: skill `postagem` (ver Documento 5,
abaixo, para o que a whoiam fornece como insumo a ela). Pós-produção: ver `references/pos-producao.md`.

**Roda aqui de verdade, executando (MCP do Higgsfield):** gerar as IMAGENS (model sheets, environment
sheets, clean plates, mood sheet, folhas de storyboard, painel avulso) via `generate_image` — 0,12 a
2 créditos cada, **sempre com `count: 4`** (quatro variações custam o mesmo que uma — [MEDIDO]);
registrar sheets aprovados como Elements; consultar saldo (`balance`) e preço (`get_cost`). **Vídeo,
não** — no modo híbrido escolhido pelo usuário o vídeo é gerado por ele no Cinema Studio na web, onde
estão os controles de direção e os benefícios do plano. Nunca afirmar que gerou um vídeo.

**Roda aqui SE o arquivo estiver enviado no chat (ffmpeg no container):** extração de frames, cortes,
conversão vídeo→GIF, reenquadramento 9:16, transcrição de áudio local via Whisper —
ver `references/conversao-midia.md`. Sem o arquivo enviado, essas etapas não acontecem.

**Fora do alcance — diga isso com clareza, não prometa:** publicar no YouTube, fazer upload,
disparar o ChatGPT ou o ElevenLabs sozinho. Os prompts são feitos para o usuário COLAR nas
ferramentas; a publicação é feita pelo usuário. Nunca afirme que executou um upload.
Pesquisa de lore/fontes e transcrição de vídeos do YouTube: skill `pesquisa-seres`.

---

## FLUXO EM FASES — sequencial, sem sobreposição (decisão jul/2026; Fase 2 tornada opcional em 29/08/2026)

Problema observado em produção: Documentos 2 e 3 saindo ora simultâneos, ora em lotes de tamanho
aleatório (3 cenas de uma vez, depois todas de uma vez, depois separadas) — sem padrão, forçando o
usuário a caçar cena por cena. Correção: **fases estanques, cada uma 100% completa e entregue
como um lote único e íntegro antes da fase seguinte começar.** Nunca abrir a fase seguinte com a
anterior parcial; nunca intercalar documentos de fases diferentes bloco a bloco.

**Mudança de 29/08/2026: a Fase 2 (Storyboard) deixou de ser obrigatória no fluxo padrão.** Decisão
do usuário: "não vamos mais usar sempre o sistema de Storyboard... pelo menos não sempre, talvez uma
vez ou outra usemos." **Caminho padrão agora: Fase 0 → Fase 1 → Fase 3, direto**, sem storyboard
intermediário — o roteiro descrito pelo usuário vira prompt de vídeo (Documento 3) apoiado nos model
sheets/Elements da Fase 1, sem passar pelo ChatGPT/Kairogen no meio. A Fase 2 continua existindo e
disponível pra quando o usuário pedir explicitamente (bloco complexo demais pra confiar sem
pré-visualizar, ou qualquer motivo que ele declare) — mas não é mais o padrão nem um portão que
bloqueia a Fase 3. Isso já vinha sinalizado desde `seedance-2-5-e-regras-2026-08.md` ("decisão de
não produzir storyboard como artefato separado"); esta atualização só corrige o `SKILL.md`, que
ainda tratava a Fase 2 como portão obrigatório — inconsistência encontrada e fechada agora.

**FASE 0 — Pesquisa.** Skill `pesquisa-seres` (fora desta skill). Entrega: dossiê da criatura.
Portão de saída: dossiê aprovado pelo usuário (ou fornecido por ele).

**FASE 1 — Personagens + Ambiente + Mood.** Ler o input (cenas, detalhes, preferências) + o dossiê
da Fase 0 como insumo de lore (FIRME = narrar com firmeza; MEDIANA = marcador leve; REZA A LENDA =
registro de lenda). Decidir nº de blocos e painéis (heurística abaixo), gerar o Documento 1
(Roteiro) + a BÍBLIA DE PERSONAGENS, o MODEL SHEET ultra-realista de CADA personagem recorrente,
o ENVIRONMENT SHEET de cada ambiente recorrente (2+ blocos no mesmo lugar — não obrigatório se
todo cenário é de uso único), e o MOOD/STYLE SHEET do vídeo (opcional, recomendado; templates dos
três em `references/model-sheet-storyboard.md`) — tudo num lote só, nunca um de cada vez em
mensagens separadas. Estado do projeto (calendário, o que está publicado) vive FORA da skill —
perguntar ao usuário ou consultar o arquivo que ele indicar; nunca presumir.
Além disso, a Fase 1 agora fecha com duas coisas que não existiam no fluxo Leonardo:

- ~~CLASSIFICAÇÃO DE MODELO POR BLOCO~~ **DESCONTINUADA (decisão do usuário, 28/08/2026).** Todo
  bloco sai em **Seedance 2.5, sempre 30s, sempre 480p** — não existe mais classificação AÇÃO/SIMPLES
  nem roteamento pro Cinema Studio Video. `references/higgsfield-cinema-studio.md` seção 3 documenta
  a lógica antiga como histórico; não aplicar.
- **PORTÃO DE CRÉDITO** — o orçamento do vídeo inteiro, em créditos, com o saldo do mês ao lado
  (`python3 scripts/orcamento.py`). Se não couber, as saídas vão na mesa ANTES do primeiro bloco.
  Descobrir que o mês acabou no bloco 14 é o modo de falhar que este portão existe para impedir.
- **LINHA `RECURSOS:` POR BLOCO** — qual recurso do Higgsfield aquele bloco vai usar (end_image,
  video_extension, speedramp, motion_control, upscale, preset…) e por quê. **Pedido explícito do
  usuário (ago/2026): a escolha do recurso é trabalho da skill, não dele.** Ele descreve o que
  acontece na cena; a skill decide o que usar, PROPÕE com o motivo dramático e o custo ao lado, e
  espera aprovação. Tabela de decisão em `references/recursos-higgsfield-quando-usar.md`. Bloco sem
  essa linha — mesmo que seja `RECURSOS: nenhum` — está incompleto.

**Portão de saída:** usuário aprova roteiro + TODOS os model sheets + environment sheet(s) (se
houver) + mood sheet (se gerado) + a classificação de modelo + o orçamento. Só então abre a Fase 2
(se o usuário pedir) ou a Fase 3 direto (padrão, ver nota acima). Com os sheets aprovados,
**registrar cada um como Element no Higgsfield** (`show_reference_elements` action=create) — dali
para frente os prompts citam o Element por placeholder em vez de depender de o usuário anexar a
imagem certa em cada geração (seção 5 da referência de plataforma).

**FASE 2 — Storyboards (Documento 2, para o ChatGPT). OPCIONAL — só roda se o usuário pedir
explicitamente para aquele vídeo/bloco (não é mais o padrão, ver nota no topo desta seção).** Quando
usada: só começa com a Fase 1 inteira aprovada. Gerar os prompts de storyboard de TODOS os blocos do
vídeo, na íntegra, entregues juntos (um arquivo por bloco está OK; lote parcial ou ordem embaralhada
não está). Nenhum prompt de vídeo nesta fase. **Portão de saída:** todos os storyboards do vídeo
entregues. **Portão de entrada pra Fase 3, quando a 2 foi usada:** usuário confirma que já gerou as
imagens no ChatGPT (ou pede para seguir mesmo sem confirmar — registrar essa opção).

**FASE 3 — Prompts de vídeo (Documento 3).** Padrão: começa direto depois da Fase 1 (sem Fase 2).
Se a Fase 2 foi usada para este vídeo, só começa com ela inteira entregue, mesmo lote/ordem (bloco 1
de storyboard casa com bloco 1 de vídeo — não reordenar). Nenhum prompt de storyboard nesta fase.
Cada bloco sai em **Seedance 2.5, sempre 30s, sempre 480p** (dialeto único — ver PLATAFORMA) e
**acompanhado da ficha de controles do Cinema Studio** — bloco sem ficha de controles está incompleto.

**Documentos fora das 4 fases (não bloqueiam nem são bloqueados por elas):**
- Documento 5 (SEO/publicação): não é mais gerado aqui — é a skill `postagem` (ver detalhe abaixo).
- Documentos 4 (narração), 6 (cortes), 7 (trilha) e 8 (edição): só DEPOIS do vídeo montado
  (ver "Sincronização" e `references/pos-producao.md`) — nunca durante as Fases 1–3.

Sempre que possível, salvar cada documento como arquivo separado em `output/` e entregar via
present_files. Se o usuário pedir explicitamente para pular fase ou gerar tudo de uma vez, seguir
o pedido dele — as fases são o padrão, não uma prisão.

---

## HEURÍSTICA DE STORYBOARD DINÂMICO (substitui o "sempre 4 painéis")

Nunca fixe a quantidade de cenas. Calcule por bloco assim:

**Passo 1 — classificar o ritmo do bloco:**
- CONTEMPLATIVO (estabelecimento de mundo, revelação estática, a criatura simplesmente ESTÁ lá) → poucas cenas
- NARRATIVO (apresentação, origem, deslocamento) → ritmo médio
- AÇÃO/CLÍMAX (confronto, convergência, perseguição, destruição) → muitas cenas

**Passo 2 — aplicar a regra. A duração do bloco agora vem do MODELO (ago/2026): `AÇÃO` = Seedance 2.5,
até 30s; `SIMPLES` = Cinema Studio Video, até 12s. A densidade de painéis escala com a duração.**

DECISÃO DE PRODUÇÃO (jul/2026, empírica do usuário, mantida): storyboards DENSOS — o gerador não
preenche o "entre-cenas" de painéis esparsos; folhas de 3 painéis saíram quase estáticas.

| Bloco | Ritmo | Painéis | Grid | Organização |
|---|---|---|---|---|
| **30s** (Seedance 2.5) | Contemplativo/transformação | 12 | 4x3 | 2–3 shots; painéis = intermediários do MESMO enquadramento |
| **30s** | Narrativo | 12–15 | 4x3 / 5x3 | 3–5 shots; 3–4 intermediários por shot |
| **30s** | Ação/Clímax | 15 | 5x3 | 4–6 shots; intermediários em progressão rápida |
| ~~≤12s (Cinema Studio)~~ | — | — | — | descontinuado (28/08/2026) — todo bloco agora é 30s Seedance 2.5, ver linhas acima |

**Decisão do usuário (ago/2026): bloco de 30s = UMA folha de 12–15 painéis.** A alternativa
considerada e recusada foram duas folhas de 8–10. O ganho é manuseio (uma folha por bloco, como
sempre foi); o risco é conhecido e está registrado: **painel pequeno alucina**, e um painel num grid
5x3 é ~40% menor que num 3x2. Mitigações que passam a ser obrigatórias, não opcionais:

- Composição simples por painel deixa de ser "lei" e passa a ser **auditada**: um sujeito, uma ação,
  fundo sem carga, em TODOS os 12–15.
- **Painel crítico sai avulso, em resolução cheia** (rosto, revelação, insert que decide o bloco).
  Imagem custa 1–2 créditos — não existe mais motivo econômico para economizar geração de imagem.
- Intermediários do mesmo enquadramento são o que salva a resolução: repetir o quadro reduz o que o
  gerador precisa acertar em cada painel pequeno. Ângulo novo só na fronteira de shot.
- **Tripwire de reversão:** se a folha de 12–15 começar a alucinar ou perder fidelidade de
  personagem, a escada é — simplificar composições → painel crítico avulso → **quebrar em duas
  folhas de 8** → só então rediscutir a densidade. Registrar o que aconteceu no receituário.

**Nota sobre "1 painel por segundo":** a ideia era 30 painéis por bloco de 30s, para amarrar o
modelo a cada segundo. Foi descartada porque colide de frente com a causa raiz nº 1 de alucinação já
registrada em produção (densidade de painel) — 30 painéis numa imagem deixam cada quadro na faixa em
que o gerador inventa. O objetivo por trás dela (amarrar os acontecimentos) é atendido por outra via:
mais INTERMEDIÁRIOS por shot, que é amarração temporal sem miniaturizar o painel.

**REGRA DOS INTERMEDIÁRIOS (o que impede a densidade de virar picote):** os painéis se agrupam em
2–4 SHOTS; dentro do mesmo shot, os painéis intermediários mantêm o MESMO enquadramento/ângulo com
a ação avançada (como frames consecutivos de um filme) — o enquadramento só muda na fronteira de
shot, e essas fronteiras são as mesmas dos [SHOT] do Documento 3. 6–10 painéis com 6–10 ângulos
diferentes = 10 cortes em 15s = picote; NÃO fazer.

**Exceções ao rótulo (intenção emocional > categoria):**
- TRANSFORMAÇÃO/METAMORFOSE: a exceção rege o RITMO (lento, pesado, sem cortes rápidos), não o
  tamanho de plano — a mudança se cobre com 2–3 shots calmos incluindo o INSERT (extreme close-up
  do detalhe transformando), conforme o plano de cobertura da direção. Eixo único do início ao fim
  só se o usuário pedir plano-sequência.
- LUTA HUMANA (corpo a corpo): plano-sequência — 1–2 shots no máximo, painéis todos como
  intermediários da coreografia (ver receituário; confirmado em teste).
- Composição complexa (múltiplos elementos): usar as fronteiras de shot para ISOLAR cada elemento,
  mantendo cada painel simples.

**Passo 3 — nº de blocos = nº de CENAS DESCRITAS PELO USUÁRIO (decisão jul/2026, mantida):** as cenas
que o usuário descrever são as cenas do vídeo, na quantidade que ele descrever. 1 cena = 1 bloco;
cena que não couber no teto de duração do modelo dela se desdobra em blocos consecutivos, avisado no
checkpoint.

**O SLOT FIXO MORREU (ago/2026).** No Leonardo o bloco era de 15s porque o crédito comprava um slot:
usar 9 segundos desperdiçava os outros 6. **No Higgsfield o preço é por SEGUNDO** — 2,5 cr/s em 480p —,
então bloco de 18s custa exatamente 18 segundos. Consequências:
- **A duração do bloco é o que a cena pede**, entre 4 e 30s (Seedance 2.5). Não existe mais motivo para
  esticar cena até fechar um slot, nem para picotar cena que pede 25s.
- **Fundir duas cenas de 15s numa de 30s é NEUTRO em custo** — a duração total não muda, o preço
  tampouco. O que muda é outra coisa (ver abaixo).
- Falar em "20 prompts de 30s" é raciocínio herdado do slot. O certo é falar em **minutos de vídeo
  dentro do envelope**.

**QUANDO FUNDIR DUAS CENAS NUM BLOCO DE 30s — e quando não:**
- **FUNDIR** quando as duas são contíguas em espaço e tempo (mesmo lugar, ação que continua). É onde o
  multi-shot nativo do Seedance 2.5 ganha de verdade: a transição interna acontece dentro da geração,
  sem corte de montagem, com continuidade de luz e de posição que dois blocos separados não garantem.
- **NÃO FUNDIR** cenas em lugares ou tempos diferentes só para "aproveitar os 30s". O modelo teria que
  saltar, o ganho de continuidade evapora, e sobra só o risco.
- **Custo: fundir é NEUTRO no mesmo modelo** [MEDIDO 19/08]. Seedance 2.5 em 480p é estritamente
  linear a 2,5 cr/s (4s = 10 · 14s = 35 · 15s = 37,5 · 30s = 75). Dois blocos de 15s custam 75; um de
  30s custa 75. Não há desconto por bloco longo nem penalidade por bloco curto. **Fundir só economiza
  contra o Seedance 2.0**, que em 480p/15s custa 45 (3,0 cr/s) — se a comparação mental for com preço
  de 2.0, a fusão parece render, mas o ganho é a troca de modelo, não a fusão.
- **O custo real da fusão é a GRANULARIDADE DE RETRABALHO.** Um bloco de 30s errado no segundo 22 custa
  75 créditos para refazer; um de 15s custa 37,5. Fundir concentra risco.
  **A resposta certa para isso NÃO é evitar blocos longos — é storyboard denso.** Se o medo de errar
  ditasse a decisão, não se usaria o Seedance 2.5 em primeiro lugar. Os 12–15 painéis do bloco de 30s
  existem exatamente para isso: quanto mais keyframes amarram os 30 segundos, menos espaço o modelo tem
  para derivar no meio. Fundir onde há continuidade real + storyboard denso é a combinação; fundir por
  conveniência aritmética continua sendo erro. A duração total é CONSEQUÊNCIA (soma dos blocos) e deve ser informada no checkpoint para
o usuário decidir — nunca usada para cortar ou inflar cenas. Se a lista de cenas não cobrir algum
beat estrutural (abertura, clímax, desfecho), APONTAR a lacuna no checkpoint como pergunta — o
usuário decide se adiciona; a skill não acrescenta cenas por conta própria.

**Passo 4 — o portão que o Leonardo não exigia: CUSTO.** O canal trabalha com **ENVELOPE POR VÍDEO**,
não com custo livre: a meta mensal define quanto cada vídeo pode gastar, e a alocação acontece dentro
disso. Com 9.000 créditos e meta de 4 vídeos/mês, o envelope é **2.250 créditos (~US$ 68)**.

**Recalculado (28/08/2026) pra decisão de "sempre Seedance 2.5, sempre 30s, sempre 480p" — sem
classificação AÇÃO/SIMPLES.** Cada bloco de 30s custa **75 créditos fixos** (2,5 cr/s). Um vídeo de
8 min (16 blocos) sem retrabalho = 1.200 créditos, ×1,4 de retrabalho = **1.680** — folga confortável
dentro do envelope de 2.250. Um de 9 min (18 blocos) = 1.350, ×1,4 = **1.890** — ainda cabe. Isso é
MELHOR do que a conta antiga achava, porque a tabela de roteamento comparava Seedance 2.5 a 720p
(6,5 cr/s) contra Cinema Studio Video — a 480p a diferença encolhe quase toda.

```bash
python3 scripts/orcamento.py --envelope --saldo 9000 --meta-videos 4 --duracao-video 480
```

> ⚠️ `scripts/orcamento.py` ainda tem as flags `--acao`/`--simples` do modelo antigo de roteamento —
> **precisam ser atualizadas** pra um modo único (`--blocos N --duracao 30 --saldo <saldo>`) na
> próxima vez que o script for tocado. Não usar as flags antigas pra decidir orçamento até lá; fazer
> a conta manual (nº de blocos × 75 × 1,4) enquanto isso.

**Bloco-vitrine — resolvido (29/08/2026).** Continua sendo a única exceção à regra de 480p, mas em
**720p** (não 1080p nativo) — o usuário decidiu fazer upscale nela também no Studio, um meio-termo
entre custo (195 cr os 30s, contra 270 do 1080p) e detalhe. **Sempre plano único, um só prompt de
cena** — normalmente a revelação da criatura; nunca multi-shot, ao contrário do resto do vídeo.
Detalhe em `references/recursos-higgsfield-quando-usar.md` §1b.

**Por que 8–9 min e não 10:** a 8 min o vídeo tolera 61% de retrabalho e ainda fecha 4/mês; a 10 min,
só 33%. Como o retrabalho real do canal nunca foi medido, a duração é o que compra margem. Detalhe e
tabela em `references/recursos-higgsfield-quando-usar.md` §1b.

O saldo real vem do `balance` do Higgsfield. Se não couber no mês, a skill **não escolhe sozinha** o
que sacrificar: apresenta as saídas possíveis (menos blocos · comprar top-up) e espera a decisão. E se
o vídeo ficar abaixo de 8 min,
avisar o que se perde (anúncio intermediário — regra da `postagem`), sem bloquear.

**Princípio:** mais ação = mais cortes = mais cenas curtas. Mais peso/tensão = menos cenas, mais longas.
Justifique a escolha por bloco no checkpoint para o usuário poder ajustar.

---

## DOCUMENTO 1 — ROTEIRO DE NARRAÇÃO

- PT-BR, frases curtas (5–12 palavras). Comprimento proporcional à DURAÇÃO REAL de cada bloco — desde
  28/08/2026 o bloco é sempre **30s** (decisão do usuário: sempre Seedance 2.5, sem variação por
  modelo): **~8–10 linhas por bloco** (coerente com o orçamento de narração — custo ≈ 33 por 15s,
  logo ≈ 66 por 30s, tolerância ±4). Sem meta fixa de total — o total segue os blocos definidos pelas
  cenas do usuário. (~4–5 linhas/15s e ~3–4/12s ficam como referência histórica do fluxo com
  roteamento de modelo, descontinuado — ver PLATAFORMA.)
  **A constante de 33/15s foi calibrada no fluxo antigo e nunca foi verificada em bloco de 30s:**
  escalar linearmente é hipótese, não medição. **Além disso, a calibração fina de verdade é a
  "legenda prévia" (Documento 1a, `pos-producao.md`)** — depois que a montagem trava as durações
  reais, a legenda é ajustada olhando o encaixe, palavra por palavra, antes de acionar o ElevenLabs.
  Medir no primeiro vídeo com blocos de 30s e corrigir em `references/narracao-elevenlabs-v3.md`.
- Reticências (...) para pausa dramática; MAIÚSCULO para ênfase; vírgulas onde a voz respira.
  (Estas convenções são também a sintaxe nativa do ElevenLabs v3 — o roteiro transfere direto.)
- Tom épico + documental, adaptado ao personagem.
- Estrutura: abertura (contexto/mundo) → desenvolvimento (criatura, origem, poderes) → clímax (confronto/revelação) → desfecho (legado, fechamento perturbador).

**Regras absolutas:**
- NUNCA mencionar criadores, datas reais ou referências ao mundo moderno.
- **NARRAÇÃO DISSOCIADA (regra central):** a voz narra EXCLUSIVAMENTE a lore da criatura — origem, natureza,
  poderes, legado. NUNCA descrever a ação humana que está na tela ("um arqueólogo caminha pelo cais" é PROIBIDO
  no roteiro de voz, mesmo que seja exatamente o que o vídeo mostra). Humanos só entram como papéis da lore,
  sem nomes ("aqueles que leem o livro", "os que ousam navegar até lá") — o espectador conecta sozinho a figura
  da tela ao papel citado. A imagem conta a história humana; a voz conta o mito. Benefício prático: a narração
  não depende do timing de nenhum corte.
- O nome da criatura PODE e DEVE aparecer.
- Basear-se no que o usuário forneceu; não inventar lore não mencionada.
- **ORIGEM ESPECULATIVA (registro de lenda):** quando a origem da criatura NÃO é fato estabelecido — usar o
  veredito da skill `pesquisa-seres`: origem com veredito MEDIANA ou REZA A LENDA é especulativa — tratá-la
  como LENDA CONTADA, não como registro histórico:
  - Na NARRAÇÃO: usar marcadores de transmissão ("reza a lenda", "dizem que", "conta-se que") no trecho de
    origem. Nunca afirmar origem especulativa como fato consumado.
  - Na IMAGEM (Documento 2): a sequência de origem usa registro de lenda — névoa, bordas oníricas, fragmento,
    como memória sendo contada — em vez de parecer um documentário do que "aconteceu". Atmosfera no start frame.
  - CUIDADO REDOBRADO com povos/religiões reais: se a origem especulativa envolve um povo, culto ou divindade
    que EXISTIU de fato, não encenar como fato histórico comprovado — a criatura é ficção do canal, mas o povo
    real não é. Registro de lenda protege disso.
  - Origem SÓLIDA (veredito FIRME) não precisa disso — contar com firmeza. A regra vale só para o incerto.
  - NÃO forçar cena de transformação quando a lenda não a tem (ex.: Dullahan não tem maldição direta como a Medusa).

---

## DOCUMENTO 2 — MODEL SHEETS (2a, FASE 1) + STORYBOARDS (2b, FASE 2) — ambos para o ChatGPT

**Documento 2 tem duas metades que pertencem a fases DIFERENTES — não gerar juntas:**
- **2a MODEL SHEETS → FASE 1.** Um por personagem recorrente, todos no mesmo lote, junto com o
  Documento 1. É o portão de saída da Fase 1: sem model sheet aprovado, a Fase 2 não abre.
- **2b STORYBOARDS → FASE 2.** Só depois que TODOS os model sheets da Fase 1 estiverem aprovados.
  Todos os blocos do vídeo, na íntegra, no mesmo lote/entrega — nunca 3 blocos agora e o resto
  depois, nunca misturado com prompts Seedance (esses são Documento 3, Fase 3).

**ANTES de escrever qualquer prompt deste documento, ler `references/model-sheet-storyboard.md`
E `references/direcao-cinematografica.md`** — a segunda contém o algoritmo diretorial (intenção
dramática → dono do olhar → anatomia do movimento → três planos de profundidade → gramática de
ângulos com justificativa obrigatória por shot → luz motivada → lente) e a autoavaliação
anti-default. A direção ADICIONA sobre os elementos descritos pelo usuário, nunca os substitui.
A biblioteca profissional de padrões de montagem, módulos de gênero e dramaturgia vive em
`references/vendor-visual-skills/` (MIT, atribuição no ATRIBUICAO.md) — o passo 5a do algoritmo
escolhe o padrão de cena por lá; em conflito com o receituário Seedance próprio, o receituário vence.

> ⚠️ **Se o bloco for de AÇÃO, ler também `references/direcao-bloco-acao.md` ANTES de escrever.**
> Lá está o teste do que conta como ação (contato entre corpos · transformação · 3+ corpos
> coordenados · câmera e sujeito rápidos juntos), o blueprint que se faz **antes** de gerar (que
> custa zero crédito), as três camadas de multidão, a névoa como limpeza barata, e a régua **4/4**
> com o custo dela em créditos. ⚫ **4/4 só em bloco de AÇÃO** — aplicar em tudo derruba o canal de
> 4,3 para 1,5 vídeos/mês.
>
> ⚠️ **Vocabulário pronto em `references/bibliotecas-camera-emocao.md`:** 45 movimentos de câmera
> na forma de quatro campos (**Movement · Speed · Framing · End**), 25 emoções escritas como
> **descrição anatômica sem nomear a emoção**, a conversão de **altura de câmera em metros** para
> ângulo nomeado, e o **orçamento de detalhe por tamanho de plano** (close pede poro e olho nítido;
> wide pede foco profundo). Consultar antes de escrever movimento ou atuação à mão.
>
> 📖 **E a §4 do mesmo arquivo é a TABELA MESTRA do canal** — vai do nosso tipo de cena (abertura ·
> ameaça latente · presságio · aproximação · revelação parcial · revelação total · reação · fuga ·
> perseguição · confronto · maldição · consequência · luto) direto para movimento, altura, tamanho
> e emoção, em uma consulta. **Começar por ela em todo bloco.** Ela é ponto de partida, não
> substituto do algoritmo de `direcao-cinematografica.md`: a justificativa dramática por shot
> continua obrigatória.
>
> ⚠️ **Para atuação, diálogo, sotaque e som, `references/atuacao-dialogo-som.md`.** Traz a tese de
> que **realismo é imperfeição** (o polido demais é o que sai falso), a estrutura de diálogo em três
> tempos (**stage → primary event → end state**), a receita de sotaque em cinco campos, as palavras
> de atuação batida a batida, foco com gatilho, a sequência de ângulos de cena de ação, a notação
> de som `( ) < > { } 【 】`, e os quatro ajustes de pós que custam zero crédito — sendo o **ruído**
> o que mais entrega realismo.
>
> ⚠️ **Para julgar o take que voltou, `references/rubrica-aceitacao-take.md`.** ⚫ A régua do Samuel
> (set/2026): **aprova o bom, não regera atrás de excelente**; rejeita o que está abaixo de mediano
> ou que quebre um item da lista de reprovação automática. Lá também estão a regra ⚫ de fundo e
> figurantes (comportamento coerente em uma linha — nem abandonado, nem detalhado) e o uso do
> desfoque de pós como alternativa barata a refazer a cena.
**Todo bloco abre declarando REFERÊNCIAS DESTE BLOCO** — quais model sheets aprovados entram,
mais environment sheet e mood sheet quando existirem, mapeados a painéis/shots (formato na
referência); bloco sem essa declaração está incompleto.
Ele contém a ÂNCORA DE REALISMO obrigatória (o bloco que impede o gerador de derivar para concept
art — causa nº 1 de resultado "ilustrado"), o template completo do model sheet e o template de
storyboard em duas partes. Regras-síntese:

- **Padrão do canal: ultra-realista "vida real".** Estrutura de model sheet/storyboard profissional
  + acabamento de fotografia cinematográfica. Criatura tratada como criatura física filmada, nunca
  "fantasy art". A âncora de realismo entra no final de TODO prompt de imagem, sem exceção.
- **Model sheet primeiro:** um por personagem recorrente (a "bíblia" do checkpoint), com corpo
  inteiro frente/costas, turnaround, expressões, close-ups de detalhe e paleta. A aparência se
  descreve exaustivamente NELE e em nenhum outro lugar — storyboards e Seedance referenciam a
  imagem ("use IMAGE 1 as strict character reference"), não redescrevem. Aprovação do usuário
  antes de qualquer storyboard.
- **Storyboard por bloco, em duas partes:** (A) o prompt da imagem — grid EXPLÍCITO (colunas x
  linhas, painéis iguais, calhas pretas grossas, cada painel autocontido; nenhum elemento cruza
  calha — sangramento entre painéis é causa direta de alucinação no Seedance), painéis LIMPOS sem
  nenhum texto renderizado (testado em produção), um tipo de shot declarado por painel, variando
  o enquadramento entre painéis; folha com painéis sangrados se regenera, nunca vai ao Seedance; (B) a ficha do
  bloco para o usuário (SHOT/ACTION/SFX por painel) — que alimenta o [AUDIO] e os [SHOT] do
  Documento 3 e NUNCA vai dentro da imagem.
- Quantidade de painéis: vem da tabela da heurística, que agora escala com a duração do bloco —
  **6–8 para bloco de ≤12s, 12–15 para bloco de 30s** (decisão de produção — o gerador não preenche
  entre-cenas esparsos). Método: listar os ESTADOS do arco (antes → primeiro contato → pico →
  consequência) como keyframes, agrupá-los em shots, e preencher com INTERMEDIÁRIOS — painéis
  do MESMO enquadramento com a ação avançada; ângulo só muda na fronteira de shot (senão vira
  picote). REGRA DURA mantida: painel 1 é pré-ação (sem o verbo da ação; tableau intacto, "the
  instant BEFORE"); último painel = estado final; elemento de fundo se comanda por
  tamanho/foco/luz, não por "ao fundo". Composição simples por painel é LEI (painéis pequenos
  alucinam) e no bloco de 30s o painel crítico (rosto/revelação) **sai avulso em resolução cheia,
  por padrão** — imagem custa 1–2 créditos, a economia de geração de imagem deixou de existir.
  Detalhe e frases-modelo na referência.

**REGRA DE DENSIDADE — a mais importante deste documento (causa raiz da alucinação/duplicação):**
Cada painel mostra UM sujeito e UMA ação, em composição limpa e legível. NUNCA amontoar múltiplas
ações no mesmo quadro. Ação complexa se resolve com MAIS painéis simples, não com painéis densos.
Incluir no prompt: "Each panel must show ONE clear subject and ONE clear action — simple, focused,
legible compositions. Do NOT crowd multiple actions into a single panel."

Manter paleta/estilo/iluminação consistentes entre todos os storyboards do vídeo (declarar a
lógica de luz da sequência em cada prompt).

---

## DOCUMENTO 3 — PROMPTS DE VÍDEO (Higgsfield) — FASE 3

**Padrão (29/08/2026): começa direto depois da Fase 1, sem storyboard intermediário.** Só se a Fase 2
tiver sido usada pra este vídeo (exceção, não regra — ver FLUXO EM FASES) é que este documento espera
o Documento 2b inteiro entregue, mesmo lote e mesma ordem de blocos — bloco 1 de storyboard casa com
bloco 1 de vídeo.

Cada bloco sai em **duas partes inseparáveis**: (A) o prompt, em Seedance 2.5/30s/480p (dialeto
único — ver PLATAFORMA); (B) a **FICHA DE CONTROLES DO CINEMA STUDIO** (formato em
`references/higgsfield-cinema-studio.md`, seção 4). Bloco sem a ficha está incompleto — no fluxo
híbrido é a ficha que carrega gênero, era, tempo de montagem, câmera, lente, abertura, movimento e
emoção, que antes moravam no texto do prompt.

**Regras comuns aos dois modelos:**
- NUNCA descrever aparência da criatura — o Element / a imagem de referência cuida disso. Descrever
  só comportamento/ação/movimento.
- NUNCA usar bloco [QUALITY AND RESTRICTIONS]. Gerar SEM legendas: "No captions. No text. No subtitles."
- **SEM MÚSICA.** No Higgsfield isso deixou de ser pedido e passou a ser parâmetro: **`generate_audio: false`**
  (Seedance) / **`sound: off`** (Cinema Studio Video). Manter a frase negativa no texto de qualquer
  jeito, como cinto e suspensório para geração feita na web. Consequência que precisa estar clara: com
  o áudio desligado o clipe vem MUDO — o `[AUDIO]` do prompt não produz nada, e a camada de SFX passa
  a ser montada na pós (ver `pos-producao.md`). A trilha continua sendo decidida holisticamente no
  Documento 7, nunca bloco a bloco.
- **Timing:** não dividir o tempo igualmente. Dar mais segundos a shots que precisam respirar
  (impacto, revelação, convergência). Usar a heurística de storyboard.
- **Câmera estilo trailer:** cada shot foca UM elemento fechado (rosto, mãos, olhos, objeto). Um
  movimento por shot no máximo. Cortes secos entre subjects > câmera acompanhando ação contínua — o
  gerador executa fragmentação melhor que continuidade.
- **Limite de caracteres: não existe teto conhecido.** 🟢 Catálogo ao vivo (02/09/2026): nenhum
  modelo do Higgsfield declara `maxLength`. Os três números que circulavam morreram — o 1.494 era do
  Leonardo, o ~3.500 nunca teve lastro (10 fontes varridas, 4 oficiais, não aparece em nenhuma), e o
  5.000 **nós lemos errado**: a frase da aula era sobre o modo de vídeo longo de 180 s, não sobre o
  prompt normal. 🎓 **8 dos 10 prompts do guia oficial do Higgsfield passam de 5.000** (faixa medida
  1.020–7.084, mediana ~6.300). Decisão do usuário (ago/2026, reafirmada set/2026): **detalhar muito
  mais as cenas, e incluir a INTENÇÃO no prompt** quando ela for relevante. Como fazer isso sem
  estragar o prompt está na seção logo abaixo — não é só escrever mais.

### PROMPT LONGO — o tamanho é o que a cena pedir (decisão do usuário, ago/2026 · reafirmada set/2026)

> ⚫ **Nem teto, nem piso.** O prompt de cena é tão detalhado quanto o modelo e a cena exigirem. Não
> há cota a cumprir nem cota a respeitar — nem o chat do Omega nem a skill devem encurtar um prompt
> para caber em número nenhum, e nenhum dos dois deve inflar um prompt que já está completo.
>
> 🎓 **Faixa observada no material oficial do fabricante: 1.000 a 7.000 caracteres, massa entre 5.000
> e 7.000.** Serve para calibrar intuição, não como meta. Se um prompt de cena está saindo com 600
> caracteres, quase certamente falta ofício nele — é sinal de alerta, **não** um mínimo a bater.
>
> ⚠️ **A ressalva que continua viva:** prompt longo e *vago* continua pior que curto e preciso. Os
> prompts oficiais são longos porque são **densos** — medidas, segundos, negativas coladas no sujeito
> —, não porque são prolixos. O ganho é poder detalhar, não encher linguiça.

A compressão telegráfica existia por restrição de plataforma e mutilava justamente o que a
`direcao-cinematografica.md` pede: antecipação, follow-through, reação do ambiente, três planos de
profundidade, geometria de relação sujeito a sujeito. Tudo isso volta. Onde gastar o espaço, em ordem
de retorno:

1. **`[ACTION]` — os três tempos, escritos.** `ANTECIPAÇÃO → AÇÃO → CONSEQUÊNCIA`, cada um com verbo,
   velocidade, peso e o que o ambiente faz em resposta. Era a primeira coisa a ser cortada no fluxo
   antigo e é a que mais separa vídeo com física de vídeo com boneco.
2. **Profundidade declarada por shot:** primeiro plano / sujeito / fundo, os três nomeados. Quadro sem
   primeiro plano é quadro chapado, e "ao fundo" continua não funcionando — comandar por
   tamanho-no-quadro, foco e luz.
3. **Geometria de relação**, quando há 2+ sujeitos: posição no quadro, direção do olhar e do corpo,
   distância. É a mitigação testada contra o viés de retrato.
4. **Textura e matéria específicas:** o que a luz faz na escama molhada, como o tecido pesa, o que o
   pé afunda. Isto é o que sustenta a âncora de realismo dentro do movimento.

**Campo novo — `[INTENT]`.** Uma linha, em inglês, com o trabalho emocional do bloco (a mesma frase do
passo 1 do algoritmo diretorial: pavor crescente / assombro / tragédia / ameaça latente / revelação /
luto). Vai logo depois do `[SUBJECT]`.

**A regra que impede o `[INTENT]` de virar enfeite:** intenção não se renderiza. O modelo não desenha
"tragédia"; ele desenha um corpo, uma luz e um movimento. Então toda intenção declarada tem que estar
**paga em coisa filmável** dentro do mesmo prompt — se o `[INTENT]` diz *dread*, alguma coisa no
`[ACTION]`, no `[SCENE]` ou no `[LIGHTING]` tem que ser a razão física daquele pavor. `[INTENT]` sem
contrapartida concreta é linha decorativa e sai. Vale também o inverso, que é a hipótese H5 do
receituário: descrever a SITUAÇÃO ("ele percebe que a porta está trancada") costuma render mais que
descrever a expressão ("rosto de pavor").

**Tripwire, porque isto é uma aposta e não uma certeza:** o modo de falhar de prompt longo é diluição
— o modelo perde o comando principal no meio da prosa. Se um bloco sair pior depois da expansão do que
saía no formato telegráfico, **cortar pela metade, manter só `[ACTION]` + geometria, e registrar no
`seedance-receituario.md`**. Mais caractere é permissão, não obrigação: prompt longo e vago continua
pior que prompt curto e preciso.

**Dialeto único (decisão de 28/08/2026: sempre Seedance 2.5, sempre 30s)** — estrutura multi-shot
`[SHOT 1]`, `[SHOT 2]`…
com timestamps somando a duração do bloco. `[STYLE]` e `[LIGHTING]` continuam presentes (a luz
diegética específica da cena é do prompt; o preset de iluminação e o grading são da ficha de
controles — não repetir a mesma informação nos dois lugares).
**Aviso empírico ainda em aberto:** o padrão "metade ótima, metade mediana" do Seedance 2.0 em 15s
nunca foi medido em 30s. Se ele se repetir, dois blocos de 15s custam o mesmo que um de 30s e dão
duas aberturas fortes em vez de uma — vale testar mesmo já tendo padronizado 30s.
(O antigo "Dialeto B", bloco `SIMPLES` via Cinema Studio Video/12s, fica descontinuado junto com o
roteamento de modelo — ver PLATAFORMA.)

TÍTULO + PRÉVIA PT-BR obrigatórios antes do prompt (formato universal em
`references/model-sheet-storyboard.md`), mesmo TÍTULO do bloco correspondente no Documento 2b:

```
TÍTULO: Bloco [N] — [nome do bloco]   |   MODELO: Seedance 2.5, 30s, 480p
PRÉVIA (PT-BR — não copiar): [1–2 frases do que acontece nesta cena]
CUSTO: [créditos deste bloco]

[IMAGE 1 as first frame  —  ou  <<<element_id>>> quando o sheet estiver registrado como Element]
[SUBJECT] quem/o que aparece — sem descrever aparência
[INTENT] o trabalho emocional do bloco, uma linha — e pago em coisa filmável abaixo
[ACTION] ANTECIPAÇÃO → AÇÃO → CONSEQUÊNCIA, cada tempo com verbo, velocidade, peso e reação
         do ambiente; micro-movimento e textura à vontade (não há mais teto de caracteres)
[SCENE] primeiro plano / sujeito / fundo declarados; chão, objetos, atmosfera, foco/desfoque
[LIGHTING] fonte, direção, intensidade, cor, sombras, reflexos, contraste
[STYLE] "photorealistic, real-life, cinematic camera, [tom emocional da cena]"
[AUDIO] sons específicos e microscópicos da cena, diegéticos (não "efeitos sonoros" genérico) — NUNCA música/trilha
[SHOT 1] 00:00-00:0X ação + movimento de câmera + o que entra/sai de quadro
[SHOT 2] ...
```

Nº de shots por bloco vem da HEURÍSTICA — não é fixo. Depois do prompt, a FICHA DE CONTROLES, que
inclui obrigatoriamente `speedramp`, `cfg_scale`, `genre`, `multi_shots`, resolução e a linha
`RECURSOS:` — todos decididos pela skill, com o porquê escrito. Padrões e gatilhos em
`references/recursos-higgsfield-quando-usar.md`.

**ANTES de escrever qualquer prompt de imagem ou de vídeo, ler `references/higgsfield-cinema-studio.md`,
`references/recursos-higgsfield-quando-usar.md`, `references/higgsfield-presets.md`,
`references/seedance-receituario.md` e `references/direcao-cinematografica.md`** (algoritmo diretorial
+ REFERÊNCIAS DESTE BLOCO com os model sheets mapeados aos [SHOT] — obrigatório também aqui).**
`higgsfield-presets.md` é o CATÁLOGO de botão real por trás da ficha de controles (seção 4 de
`higgsfield-cinema-studio.md`): nomes confirmados por print de Genre/Era/Tempo/Câmera/Lente/
Abertura/Lighting/Paleta, e as tabelas de derivação (ângulo→Movement, lente-como-psicologia→
Lens/Aperture, fraseado de movimento→preset). `higgsfield-presets-exemplo-cthulhu.md` mostra essa
tabela já aplicada bloco a bloco — útil de consultar, não é a fonte da regra.
Ele contém os padrões empíricos do modelo (perda de dinamismo ao seguir o start frame, duplicação de
personagem, atmosfera ignorada quando há referência, posição do pico nos 15s). Aplicar as mitigações de lá —
elas vêm de teste real, não de teoria. Atualizar o arquivo quando o usuário relatar novo padrão observado.

---

## DOCUMENTO 4 — NARRAÇÃO (ElevenLabs v3) — só após vídeo montado

**Decisão do usuário (jul/2026): narração é ElevenLabs v3.** O teste A/B Suno × ElevenLabs foi
encerrado; o formato Suno de narração está aposentado. O Suno continua APENAS para trilha musical
(Documento 7).

O Documento 4 é o roteiro final (Documento 1 já reescrito para casar com o vídeo montado — ver
Sincronização) com a **passada de marcação de audio tags do v3**, dividido por sequência e pronto
para colar no ElevenLabs.

**ANTES de gerar o Documento 4, ler `references/narracao-elevenlabs-v3.md`.** Ele contém:
como as tags funcionam, as configurações (stability, escolha de voz), o vocabulário de tags do
canal (documental sombrio — tags alegres são proibidas), a tabela de perfil de voz por tipo de
criatura, o formato de entrega por sequência, e o registro empírico vivo (atualizar quando o
usuário relatar comportamento observado do v3).

Regras-resumo (detalhe na referência):
- Insumo obrigatório: `cenas-travadas-<criatura>.md` (sequências finais + duração real de cada uma);
  se não existir, criar com o usuário e salvar em output/ antes de marcar.
- Orçamento de duração por bloco de ~15s: custo = palavras + 1,5×reticências + 2×[pause] ≈ 33,
  tolerância ±4. CALIBRAR a constante na primeira geração real de cada voz (medir o áudio) e
  registrar na referência.
- 1 narrador por padrão. Multi-narrador (ex.: personagem em 1ª pessoa → narrador mítico) só quando
  o usuário pedir, via MAPA DE NARRADORES — e o MODO PERSONAGEM é exceção sancionada à narração
  dissociada, restrita às sequências designadas (1ª pessoa narra estado interno/descoberta, nunca
  a própria ação shot-a-shot).
- Bloco pronto-para-colar contém SÓ narração + tags válidas: marcação de cena entre colchetes e
  textos de tempo ("15 segundos") DENTRO do bloco são defeito grave (o v3 performa ou lê em voz alta).
- Preservação absoluta do texto: marcar não é reescrever nem expandir.
- Gerar por SEQUÊNCIA (blocos > 250 caracteres); 2–3 takes por sequência (1 versão marcada, não
  3 variações tonais — o canal tem um registro só).
- Stability: Natural por padrão; Creative para picos emocionais; nunca Robust com direção emocional.
- Se o usuário pedir outra voz, usar a preferência dele.

---

## DOCUMENTO 5 — SEO E PUBLICAÇÃO → skill `postagem`

**Este documento saiu da `whoiam`.** Título, thumbnail, descrição, tags, calendário de
postagem e análise de CTR agora são a skill `postagem`, que aplica as regras extraídas do
curso "Mestres do Algoritmo 2.0" citando aula e minuto em cada decisão.

Quando o usuário pedir SEO, título, thumb, descrição, "quando eu posto" ou colar números do
YouTube Studio: acione a `postagem`. Não gere um pacote de SEO aqui — um SEO improvisado que
contradiz uma regra que o usuário aprovou é pior que nenhum.

O que a `whoiam` continua fornecendo como INSUMO para a `postagem`:
- o roteiro final (o curso manda tirar o título do roteiro já escrito, não do nada);
- a duração real do vídeo montado, de `cenas-travadas-<criatura>.md`;
- os model sheets aprovados, que a thumbnail referencia para ser a mesma criatura do vídeo;
- os CRÉDITOS de fontes vindos do dossiê da `pesquisa-seres`.

Uma nota de fronteira que vale registrar: a `postagem` trabalha com duração-alvo de 8–12 min,
porque abaixo de 8 min o vídeo não tem anúncio intermediário (aula 13, [11:37]). Isso afeta o
número de blocos decidido na Fase 1 desta skill — **16 a 24 blocos de 30s, ou 40 a 60 de 12s, ou a
mistura das duas coisas**. Se a lista de cenas do usuário render menos que isso, aponte no
checkpoint; a decisão continua sendo dele.

**E a nota nova, ago/2026 — a duração-alvo virou uma decisão de dinheiro.** 8–12 min por vídeo custa,
no Higgsfield, entre ~900 e ~5.400 créditos dependendo do modelo (tabela em
`references/higgsfield-cinema-studio.md`), contra um plano Ultra de 3.000 créditos/mês. Isso significa
que o parâmetro de FREQUÊNCIA da `postagem` (2/semana, fixado em 14/08/2026, antes de existir modelo
de custo) não é financiável como está. Quando a `postagem` for acionada, ela precisa receber desta
skill o **custo real em créditos do vídeo montado**, não só a duração — e o calendário dela tem que
caber no orçamento, não só no cronograma.

---

## DOCUMENTO 6 — PLANO DE CORTES / MELHORES MOMENTOS (Shorts) — após vídeo montado

A partir do roteiro + descrição de como o vídeo ficou:
- Identificar 2–4 trechos de maior impacto (revelação de poder, clímax, frase marcante).
- Para cada corte: timestamp aproximado, por que funciona como Short, gancho de abertura sugerido (texto on-screen), e título/legenda do Short.
- Marcar quais precisam de reenquadramento vertical (9:16).

**Execução técnica:** se o arquivo do vídeo estiver enviado no chat, os cortes e o reenquadramento
rodam aqui com ffmpeg (`references/conversao-midia.md`). Se não estiver, fornecer os comandos para
o usuário rodar localmente. Não simular o corte.

---

## SINCRONIZAÇÃO DE ÁUDIO (regra herdada — atualizada com rascunho de legendas)

Documentos 1 e 4 são rascunhos durante a produção. Fluxo pós-produção completo (decisão jul/2026 —
legendas rascunhadas com placement ANTES da geração final no ElevenLabs, não depois):
produzir blocos Seedance → montar no CapCut e TRAVAR a duração das sequências → usuário descreve
como o vídeo ficou de fato → REGISTRAR isso em `cenas-travadas-<criatura>.md` (sequências finais,
duração real, o que aparece na tela) e salvar em output/ → reescrever roteiro para casar com o
vídeo real → **gerar o RASCUNHO DE LEGENDAS COM PLACEMENT** (mapeia o texto de cada sequência
contra a duração real travada, usando o orçamento de duração já existente para estimar o encaixe;
o usuário lê, ajusta o texto vendo como cabe em cada trecho, ANTES de gastar qualquer geração no
ElevenLabs — nada fixo, o placement é estimativa de planejamento, não trava nada) → só então gerar
o Documento 4 FINAL (marcação ElevenLabs v3, a partir do rascunho já aprovado, 2–3 takes por
sequência) → gerar o áudio real → gerar Documento 7 (mapa de trilha Suno, com duração-alvo por
sequência) → Documento 8 (mapa de edição — a partir daqui, a sincronia de legenda usa o ÁUDIO REAL,
nunca a estimativa do rascunho) → mixagem final. Documento 6 (cortes) também só depois do vídeo
real existir. Detalhes do rascunho de legendas e do fluxo completo: `references/pos-producao.md`.

---

## REGRAS ANTI-STRIKE YOUTUBE (por vertente do canal — decisão jul/2026)

Esta skill serve múltiplas vertentes/canais com a mesma metodologia (mitologia/folclore,
anime/mangá, super-heróis de HQ). O status de IP do personagem muda o que se aplica:

- **Vertente mitologia/folclore (domínio público):** só criaturas de domínio público; nunca IP
  registrado. Regra original, inalterada.
- **Vertentes anime/mangá e super-heróis de HQ:** reprodução de personagem com IP protegido é
  escolha consciente e já avaliada pelo usuário — a skill NÃO bloqueia, NÃO questiona e NÃO repete
  aviso de risco a cada bloco/geração. Gerar normalmente.
- Regras abaixo valem para QUALQUER vertente, sem exceção:
  - Gore: implicar, nunca mostrar. Violência no tom, ausente nos detalhes gráficos.
  - **Trilha (decisão ago/2026 — inverteu a hierarquia):** a fonte PRIMÁRIA passa a ser a
    **Biblioteca de áudio do YouTube Studio** — as faixas de lá são gratuitas, monetizáveis dentro do
    YPP e **não são reclamadas pelo Content ID**, o que remove a categoria de risco inteira. Faixas
    marcadas `Creative Commons — Attribution (CC BY 4.0)` exigem crédito ao artista na descrição
    (obrigação que a `postagem` tem de carregar no template de descrição); as de licença padrão da
    Biblioteca não exigem nada. Cuidado com faixas marcadas "somente YouTube": não podem sair da
    plataforma. **O Suno passa a ser o COMPLEMENTO**, para os cues que a Biblioteca não cobre — e a
    limitação dela é real: o acervo é forte em jazz/rock/pop/folk e fraco justamente no que a paleta
    do canal pede (drones graves, clusters de metais, percussão de guerra, crescendo glacial). Suno em
    vídeo monetizado exige plano pago (Pro ou Premier; Studio só no Premier), e o direito comercial
    vale para as faixas geradas enquanto a assinatura estava ativa, mesmo após cancelar. Detalhe
    operacional em `references/pos-producao.md`.
  - Nunca música de terceiros sem licença.
  - Narração ElevenLabs: verificar que o plano do usuário cobre uso comercial antes de publicar
    vídeo monetizado.
