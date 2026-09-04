# Modificações nas skills — 19/08/2026 (migração Leonardo → Higgsfield)

Arquivo de transferência de contexto. Lista tudo o que mudou, onde, e por qual motivo. Serve para
colar numa conversa nova e o modelo saber o que já foi decidido.

**Decisões do usuário nesta sessão:**
1. Repertório musical = **Biblioteca de áudio do YouTube Studio**.
2. Modo de produção = **híbrido** (imagens por MCP, vídeo no Cinema Studio na web).
3. Plano = **Higgsfield Ultra**. Base do tier é 3.000 créditos/mês, mas o Ultra **tem uma função
   para escalar até 9.000 créditos/mês** (Samuel confirmou em 19/08/2026, depois desta sessão
   original ter registrado "o 9.000 não existe na oferta" — correção). **Print da página de preços
   confirmou o mecanismo: é um slider dentro do próprio Ultra (3.000/6.000/9.000), não um top-up
   separado.** Falta só comparar a razão cr/US$ do 9.000 contra o 3.000 na mesma condição de
   cobrança antes de recalcular qualquer tabela de vídeos/mês (ver `planejamento-fluxo-higgsfield.md`,
   seções 1.2/1.3/8).
4. Storyboard de bloco de 30s = **uma folha de 12–15 painéis** (recusadas: 2 folhas de 8–10; 30 painéis).

**Entregáveis desta sessão:** `whoiam.skill`, `postagem.skill`, `planejamento-fluxo-higgsfield.md`,
este arquivo.

> Nota: os arquivos de skill em disco nesta sessão são cache somente-leitura — editar lá não muda a
> skill da sua conta. As mudanças abaixo foram aplicadas em cópias e empacotadas nos dois `.skill`.

---

## A. ARQUIVOS NOVOS

### `whoiam/references/higgsfield-cinema-studio.md` — NOVO (~16 KB)
Base factual da migração. Contém:
- **Seção 1 — fronteira web × MCP:** tabela do que existe em cada porta; registro de que os controles
  de direção do Cinema Studio 4.0 e os benefícios "Unlimited/Free Gens" do plano **não** funcionam via
  MCP (nota de compliance do próprio Higgsfield); definição do modo híbrido como padrão do canal.
- **Seção 2 — tabela de custos [MEDIDA via `get_cost` em 19/08/2026]:** créditos e créditos/segundo de
  Seedance 2.5 (480p/720p/1080p, 15s/30s), Seedance 2.0 std, Seedance 2.0 Mini, Cinema Studio Video
  (std/pro) e imagem. Registro de que os "75 créditos" observados eram 480p. Custo por vídeo de 10 min
  e vídeos/mês em Ultra. Fator de retrabalho ×1,4 (orçado, não medido). **PORTÃO DE CRÉDITO** obrigatório
  no checkpoint da Fase 1.
- **Seção 3 — roteamento de modelo por bloco:** absorve a classificação AÇÃO/SIMPLES da skill `teste`
  (que fica obsoleta como fork). Exemplo numérico de economia (~38%). Teto de 12s do Cinema Studio Video.
- **Seção 4 — prompt × controles:** tabela do que vai no texto e do que vai nos controles; formato da
  FICHA DE CONTROLES; mapeamento dos passos da `direcao-cinematografica.md` para os controles;
  recomendação de manter o **enhancer de prompt desligado** (marcada como leitura, não medição) + teste
  para refutá-la.
- **Seção 5 — Elements:** model/environment sheet aprovado → Element → `<<<element_id>>>` no prompt.
  Ressalva: documentação não lista Seedance 2.5 como compatível (a confirmar).
- **Seção 6 — ganhos técnicos:** `generate_audio:false`, `end_image` (H4 nativa), `video_extension`,
  `multi_shots` sem custo extra, fim do limite de 1.494 chars.
- **Seção 7 — registro empírico** com 10 itens abertos.

### `whoiam/scripts/orcamento.py` — NOVO
Calculadora de créditos por vídeo. Modo simples, modo misto (AÇÃO/SIMPLES) e modo `--tabela`
(vídeos/mês por modelo). Bloqueia duração acima do teto do modelo, alerta se o vídeo cair abaixo de
8 min (anúncio intermediário) e se o custo não couber no saldo, listando as quatro saídas. Preços
embutidos como constantes com data de medição.

---

## B. `whoiam/SKILL.md`

| Onde | Antes | Depois |
|---|---|---|
| Front matter (description) | "prompts de vídeo Seedance" | inclui orçamento de créditos, ficha de controles do Cinema Studio, "Seedance 2.5 / Cinema Studio Video no Higgsfield" |
| Bloco novo no topo: **PLATAFORMA** | não existia | 4 fatos que mudam decisão: modo híbrido; vídeo é o gargalo (6,5 cr/s vs 3.000 cr/mês); duração de bloco deixou de ser constante; direção migra do texto para os controles |
| "Roda aqui, no chat" | só entregava texto | ganhou parágrafo **"Roda aqui de verdade, executando (MCP)"**: gera imagens (1–2 cr), registra Elements, consulta `balance`/`get_cost`. Vídeo explicitamente NÃO |
| Fase 1 — portão de saída | roteiro + sheets | + **classificação de modelo por bloco** (AÇÃO/SIMPLES) + **portão de crédito** + registro dos sheets como Elements |
| Fase 3 | "Prompts Seedance" | "Prompts de vídeo": dialeto por modelo + **ficha de controles obrigatória** |
| Heurística, passo 2 | tabela fixa de 6/6–8/8–10 painéis para blocos de 15s | tabela por **duração**: 30s → 12/12–15/15 painéis (grid 4x3, 5x3); ≤12s → 6–8. Decisão de 1 folha registrada com as mitigações, o tripwire de reversão e o motivo do descarte de "1 painel/segundo" |
| Heurística, passo 3 | "1 cena = 1 bloco de ~15s" | duração do bloco vem do modelo; teto por modelo |
| Heurística, **passo 4 (novo)** | — | portão de custo com o comando do `orcamento.py` e as quatro saídas |
| Documento 1 | "~4–5 linhas por bloco de 15s" | ~4–5 (15s) / ~8–10 (30s) / ~3–4 (12s); constante 33/15s marcada como **não verificada em 30s** |
| Documento 2b | "PISO DE 6, teto 10" | painéis vêm da tabela por duração; painel crítico avulso **por padrão** no bloco de 30s |
| Documento 3 | "PROMPTS SEEDANCE", regras do Leonardo | "PROMPTS DE VÍDEO (Higgsfield)": duas partes (prompt + ficha); `generate_audio:false`/`sound:off` como parâmetro; limite de 1.494 chars **revogado**; **Dialeto A** (Seedance 2.5, multi-shot em texto) e **Dialeto B** (Cinema Studio Video, multi-shot em parâmetro); aviso de que o padrão "metade ótima/metade mediana" não foi medido em 30s |
| Template do prompt | `[IMAGE 1 as first frame]` | cabeçalho ganhou MODELO e CUSTO; referência aceita `<<<element_id>>>` |
| Documento 5 (nota de fronteira) | "~32 a 48 blocos de 15s" | 16–24 blocos de 30s / 40–60 de 12s / mistura + **nota nova**: a duração-alvo virou decisão de dinheiro, e o parâmetro de frequência da `postagem` não é financiável como estava |
| Anti-strike, trilha | "Suno; fallback: YouTube Audio Library" | **hierarquia invertida**: Biblioteca do YouTube é primária (grátis, monetizável, sem Content ID; CC BY exige crédito; cuidado com "somente YouTube"); Suno é complemento, com a ressalva do acervo fraco no que a paleta pede e a nota de que música 100% IA não tem copyright |

---

## C. `whoiam/references/pos-producao.md`

- Título passou a citar Biblioteca do YouTube + Suno + SFX.
- **Seção 2 reescrita:** Biblioteca do YouTube como fonte primária, Suno como complemento, com o motivo
  técnico (o acervo é forte em jazz/rock/pop/folk e fraco em drone/cluster/percussão de guerra).
  Regras de licença explícitas (padrão / CC BY / "somente YouTube"). Regra do cue por sequência
  emocional **mantida e reforçada** ("três blocos de suspense recebem UMA música"). Tabela do
  Documento 7 ganhou colunas **Fonte** e **Licença · crédito?**, que alimentam o bloco de créditos da
  descrição na `postagem`. Ordem de busca: Biblioteca primeiro, Suno só quando falhar, registrando qual
  clima faltou.
- **Seção 2b — SFX: NOVA.** Camada criada pelo áudio desligado no gerador. Fontes em ordem (efeitos da
  Biblioteca → gerados). O `[AUDIO]` do prompt muda de função: deixa de ser instrução ao gerador e passa
  a ser **lista de compras de SFX** que alimenta o Documento 8. Alternativa a testar: deixar o áudio
  ligado e descartar só a música.
- Seção 4 (vereditos) ganhou 3 itens: cobertura real da Biblioteca por clima; SFX manual vs. nativo;
  calibração da constante de narração em bloco de 30s.

## D. `whoiam/references/model-sheet-storyboard.md`

- **Geometria do grid:** layouts 12 = 4x3 e 15 = 5x3 adicionados. Bloco novo sobre o bloco de 30s: o
  painel num 5x3 tem ~40% da área de um 3x2, painel crítico avulso **por padrão**, auditoria painel por
  painel, tripwire de reversão em 4 degraus (a alternativa de 2 folhas de 8 fica registrada como degrau,
  não como ideia morta).
- **Model sheet:** depois de aprovado, registrar como **Element** e citar por placeholder; o texto
  "use IMAGE 1 as strict character reference" continua como fallback (web, ou modelo incompatível), com
  o motivo explicitado.

## E. `whoiam/references/seedance-receituario.md`

- **AVISO DE ESCOPO no topo:** tudo no arquivo foi observado em Seedance 2.0 / 15s / Leonardo. Nada está
  automaticamente válido no 2.5. Três padrões marcados para reavaliação prioritária (metade ótima/metade
  mediana; perda de dinamismo no start frame; referência sobrescrevendo atmosfera). Os padrões de
  densidade/composição são apontados como os mais prováveis de permanecer válidos.
- **Hipótese do bloco curto reaberta:** no Leonardo encurtar era desperdício (4 prompts/crédito); no
  Higgsfield o preço é por segundo, a objeção econômica caiu, e dois blocos de 15s custam igual a um de
  30s.
- **"Registrado e descartado"**: o item que descartava features do Higgsfield foi marcado como
  **REVOGADO** (a plataforma agora é o Higgsfield); `end_image`, `video_extension` e `multi_shots`
  passaram de "features de outra plataforma" a recursos disponíveis, com H4 nativa.

## F. `whoiam/references/direcao-cinematografica.md`

- Bloco no topo: o algoritmo continua inteiro (ele decide *o que* filmar e *por quê*), mas a execução
  migrou para os controles do Cinema Studio. Mapeamento passo-a-controle. Reforço: **a justificativa
  dramática por shot continua obrigatória**, agora escrita na ficha de controles — "controle escolhido
  sem porquê é o mesmo default de antes, com outra roupa".

---

## G. `postagem/SKILL.md`

| Onde | Mudança |
|---|---|
| Front matter | acrescenta thumbnail gerada, frequência **sustentável** dada o orçamento, e o **Produto D** (identidade do canal); novos gatilhos: "o que escrevo no Sobre", "quantos vídeos consigo fazer por mês" |
| "O que roda / não roda" | passa a gerar a imagem da thumb por MCP (2 opções reais, 1–2 cr) e a rodar identidade do canal; "não roda" ganhou: escrever o texto final do Sobre no lugar do Samuel (o curso manda ser ele) e pôr texto dentro da arte |
| Tabela de parâmetros | Lote de estreia e Frequência marcados **EM REVISÃO**; linha nova **Orçamento de créditos: Ultra 3.000/mês** |
| **Seção nova: "O parâmetro que faltava: o custo de produção"** | tabela de créditos/vídeo e vídeos/mês por modelo; constatação de que 2/semana não é financiável em nenhuma combinação e que o teto real é ~2/mês; o argumento do curso (nunca baixar frequência, 3 aulas) usado para justificar estrear devagar; a citação que legitima **quinzenal** (aula 1 [04:03]; start [03:51]); 4 obrigações da skill ao montar calendário; conta da gaveta de estreia (80–120 min = 4–5 meses de plano) e proposta de gaveta de 4–5 com desvio registrado |
| Produto A · item 2 (Thumbnail) | parágrafo novo: geração da arte por MCP + workflow `youtube-thumbnail-generator` do Higgsfield, com as regras desta skill vencendo em conflito; as "duas opções" do curso passam a ser duas imagens reais |
| Produto A · item 3 (Descrição) | ganhou **CRÉDITOS DE TRILHA** (CC BY obrigatório, insumo do Documento 7 da `whoiam`), template fixo citado (aula 17 [11:08]) e link do próximo vídeo (aula 3 [13:56]) |
| **PRODUTO D — IDENTIDADE DO CANAL: NOVO** | descrição do "Sobre" (aula 7 [26:11]; escrita pelo Samuel — a skill propõe rascunho, aula 7 [14:24]/[17:34], aula 17 [04:25] média), template fixo de descrição, nome/avatar/banner, playlists, checklist de "canal pronto para estrear". Aviso de não inventar "SEO de canal" |

## H. `postagem/references/calendario-e-fila.md`

- `canal-estado.md` ganhou seção **"Orçamento de produção"**: plataforma e modo, plano/créditos por mês,
  gasto do mês, custo médio por vídeo, fator de retrabalho observado, **frequência sustentável** e a
  regra de que sustentável < atual é alerta de primeira linha.
- "O que o calendário deve mostrar" ganhou item 5: **o mês em que o orçamento estoura**.
- Seção nova: **`--producao-por-semana` mudou de natureza** — deixou de ser só disciplina e passou a ter
  teto financeiro; usar o número do orçamento, não o da vontade.

---

## I. O QUE **NÃO** FOI MEXIDO (e por quê)

- **`pesquisa-seres`** — a Fase 0 não foi afetada pela migração. Nota: o script
  `transcrever_youtube.py` não funciona neste ambiente (YouTube bloqueado); roda na máquina do usuário.
- **`teste`** — fica **obsoleta como fork** (existia para comparar Seedance × Magnific; a ferramenta
  barata agora está dentro do Higgsfield). A parte útil dela (classificação AÇÃO/SIMPLES) migrou para a
  `whoiam`. **Recomendação: aposentar a skill `teste`**, ou reescrevê-la como skill de teste A/B
  genérica. Não foi tocada nesta sessão para não misturar decisão de arquitetura com execução.
- `narracao-elevenlabs-v3.md` — não editado; a calibração da constante para 30s está apontada na
  `SKILL.md` e na lista de vereditos do `pos-producao.md`, mas o número real só pode entrar depois de
  medido.
- `regras-postagem.md`, `titulo-e-thumbnail.md`, `auditoria-ctr.md` — as regras de título e thumbnail já
  cobriam o que foi perguntado (fórmula, power words, subtítulo que complementa, prompt de imagem,
  legibilidade a 120px, padrão mantido 3–4 vídeos). Nada a corrigir; só a via de execução da arte mudou,
  e isso entrou na `SKILL.md`. As 10 aulas travadas na Kiwify continuam pendentes de processamento.
- `scripts/calendario.py` — não alterado. Ele projeta gaveta por tempo, não por crédito; a conta de
  crédito ficou na `orcamento.py` da `whoiam` e na leitura do calendário. Se virar incômodo, o próximo
  passo é um `--creditos-mes` no `calendario.py`.

---

## J. LISTA DE PENDÊNCIAS (o que ainda é hipótese)

1. Fator de retrabalho real do canal (orçado ×1,4, sem dado).
2. Seedance 2.5 sustenta 30s de dinamismo, ou repete "metade ótima / metade mediana"?
3. Seedance 2.5 respeita `[SHOT n]` em texto, ou precisa de multi-shot como parâmetro?
4. Element funciona com Seedance 2.5?
5. Qualidade do Cinema Studio Video vs. Seedance 2.5 no MESMO bloco contemplativo (a decisão que vale
   mais dinheiro).
6. Custo em créditos dos modelos exclusivos do Cinema Studio na web (não mensurável via MCP).
7. Duração máxima real na web (30s no blog de lançamento; a página de produto fala de até 1 min e 4K).
8. Enhancer de prompt: nome, comportamento e efeito real (recomendação atual de desligado é opinião).
9. ~~Limite de caracteres do prompt no Higgsfield (~3.500 é fonte de terceiro).~~ **FECHADO em
   02/09/2026: não existe teto conhecido.** 🟢 Nenhum modelo declara `maxLength`; o ~3.500 não tem
   lastro; o 5.000 era sobre o modo de 180 s. 🎓 8 dos 10 prompts oficiais passam de 5.000 (faixa
   1.020–7.084). Ver `PESQUISA-2026-09-02-limite-prosa-json-direcao.md` §1.
10. Constante do orçamento de narração em bloco de 30s.
11. `video_extension` costura dois blocos sem emenda visível?
12. Piso de resolução aceitável para o canal (480p/720p/1080p) na TV e no celular.
13. Folha de 12–15 painéis: o tripwire de alucinação aguenta?
14. Quais climas da paleta a Biblioteca de áudio do YouTube realmente cobre.
