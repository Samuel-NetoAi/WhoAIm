# Estado do corpus — 2026-09-02, fim do dia

> **Nota:** este arquivo nasceu como "repasse para o Omega". O Omega é a própria sessão que o
> escreveu (`omega-d2`) — era um bilhete para si mesmo. **As pendências de prioridade alta foram
> executadas na mesma sessão** (§6). O que sobrou é o que continua realmente aberto.
>
> Diz o que já está feito (para não refazer), o que o Samuel decidiu (para não redecidir), e o que
> falta (com prioridade).
>
> **Fonte de verdade do corpus:** `C:\Users\Samuel\.claude\skills\{whoiam,postagem,pesquisa-seres}\`.
> As pastas do repo são **cópia gerada** — editar só a instalada e sincronizar depois. Os `.skill`
> na raiz são zips de 19/ago, **desatualizados**, não usar como referência.

---

## 1. NÃO REFAZER — já está feito e verificado

- ✅ **Limite de caracteres.** Os três números estão mortos e enterrados com lápide em todos os
  arquivos: 1.494 (Leonardo), ~3.500 (terceiro sem lastro), 5.000 (lido errado — era sobre o modo
  de vídeo longo de 180 s). Não existe teto conhecido. Faixa oficial medida: 1.020–7.084, mediana
  ~6.300, 8 de 10 acima de 5.000.
- ✅ **Marcador 🎓 e aviso de calibragem** no cabeçalho do `REGRAS-PRODUCAO-VIDEO.md`.
- ✅ **Distinção dos três sentidos de "3/4"** escrita em `model-sheet-storyboard.md`. Não é o que o
  briefing dizia: **3/4 de pessoa assimétrico está VIVO** (é o instrumento anti-espelho);
  o que morreu é o 3/4 **espelhado** (as duas figuras no mesmo ângulo, de corpo inteiro).
- ✅ **Resíduo da regra velha de duas pessoas a 45°:** varrido, **não existe**. O corpus já
  refletia a correção inteira.
- ✅ **Skill `teste`:** já não existe em disco; referências textuais limpas.
- ✅ **Duas cópias do corpus sincronizadas** (`diff -r` limpo nas três skills).
- ✅ **`direcao-bloco-acao.md`** e **`rubrica-aceitacao-take.md`** criados e ligados no `SKILL.md`.
- ✅ **Comparação campo a campo** com a skill da comunidade — ver §4.

---

## 2. DECISÕES DO SAMUEL — ⚫ não redecidir, não perguntar de novo

| # | Decisão | Onde está escrita |
|---|---|---|
| 1 | **Fonte de verdade é a cópia instalada**; repo é cópia gerada | memória + este doc |
| 2 | **Prompt é tão detalhado quanto a cena precisar** — nem teto nem piso. Nem o chat nem a skill comprimem prompt para caber em número | `REGRAS` §3, `SKILL.md` |
| 3 | **O Samuel dita a CENA, o agente dirige.** Nunca devolver pergunta de técnica ("qual lente?"); dúvida é de INTENÇÃO | `REGRAS` §7.4 |
| 4 | **4/4 não é padrão. Começar com 2 takes em bloco de AÇÃO**, subir para 4 só no bloco que resistir. Bloco simples: 1 take | `direcao-bloco-acao.md` §4.2 |
| 5 | **Blueprint só em cena de ação** — portão explícito, classificação declarada na ficha do bloco. Errar para o lado caro também é erro | `direcao-bloco-acao.md` §1.1 |
| 6 | **Régua de aceitação: aprova o BOM, não regera atrás de excelente.** Rejeita abaixo de mediano ou item da lista de reprovação automática | `rubrica-aceitacao-take.md` §1 |
| 7 | **Fundo e figurantes:** comportamento coerente em UMA linha, por atividade e por classe. Nem abandonado, nem detalhado | `rubrica-aceitacao-take.md` §5 |
| 8 | **Blur de pós antes de refazer cena.** Refazer custa 75 cr; desfoque custa zero | `rubrica-aceitacao-take.md` §5.1 |
| 9 | **Imagens saem do orçamento de crédito.** O Samuel gera fora (GPT Plus, Nano Banana Pro). A skill entrega o PROMPT, nunca a imagem | `direcao-bloco-acao.md` §4, `model-sheet-storyboard.md` |
| 10 | **Roteamento de modelo por bloco: descontinuado** (28/08). Tudo em Seedance 2.5, 30 s, 480p | `SKILL.md`, `higgsfield-cinema-studio.md` §3 |
| 11 | **video-to-video entra nos canais FUTUROS** (HQ/anime), ciente do risco de strike. Não é para o canal de criaturas agora | este doc |

---

## 3. A CONTA, fechada — para não ser refeita de cabeça

🔵 Base: Seedance 2.5 · 480p · 30 s = **75 créditos**. Plano 9.000/mês. Vídeo = 20 blocos = 10 min.

| Regime nos blocos de AÇÃO | cr/vídeo | vídeos/mês |
|---|---|---|
| 1 take + retrabalho ×1,4 | 2.100 | 4,3 |
| **2 takes** ← padrão | 2.235 | **4,0** |
| 4/4 | 2.685 | 3,3 |
| 4/4 em tudo (não fazer) | 6.000 | 1,5 |

**O blueprint custa ZERO.** É papel. O que custa é o número de takes de vídeo.

**A alavanca mais forte é de direção:** desfocar multidão de fundo + névoa tira o gatilho caro
("3+ corpos coordenados"). Batalha naval: 5 blocos de multidão nítida a 4/4 = **1.500 cr**;
3 blocos focados nos principais com fundo desfocado a 2 takes = **450 cr**.

---

## 4. A SKILL DE PROMPT — item ENCERRADO, e a conclusão mudou

**Não existe prova de que exista uma skill de prompt do fabricante.**

- 🟢 O MCP do Higgsfield serve **16 workflows** e nenhum é construtor de prompt do Seedance.
- A aula Stage 3 não expõe download no HTML servido.
- O que existe é `OSideMedia/higgsfield-ai-prompt-skill` (GitHub, MIT), e o **README se declara
  community-made**: *"This is community-made, not official Higgsfield material."* É o autor
  dizendo. **Ela é 🟡, não 🎓.**

**Comparação feita. Os três formatos são compatíveis — o nosso formato NÃO precisa ser reescrito.**

**O que a skill 🟡 acrescenta e vale testar** (tudo em `REGRAS` §7.2):
1. ⚠️ **Folha de personagem exige exclusão do fundo** — *"Do not take the gray backdrop"*. **Nós
   pegaríamos essa armadilha:** nosso model sheet usa fundo de estúdio cinza liso.
2. **Grau de fidelidade por referência** — `full-preserve` / `partial-preserve` /
   `attribute-transfer` / `loose-guide`.
3. **Nomear personagem por marcador visível**, nunca pelo handle (`@Image 1`).
4. **Nunca escrever idade em palavra** — usar papel, porte, roupa, ação.
5. **Timestamp é orçamento de tempo**, não ponto de corte exato.

✅ **A skill `character-sheet` do FABRICANTE (essa sim, 🎓) já foi lida via MCP e incorporada** em
`model-sheet-storyboard.md`: motor anti-IA/anti-retoque, cláusula anti-brilho no olho, estrutura
facial adulta, negativa contra figura duplicada, ordem dos slots. **A arquitetura bateu com a
nossa** — nosso model sheet ganhou respaldo, não foi desmentido.

---

## 5. CONTRADIÇÕES VIVAS — marcar, nunca apagar

1. **A armadilha da negação** (`REGRAS` §7.4b). Três aulas da Academy dizem que negativa não
   funciona; o guia oficial da mesma empresa usa negativa o tempo todo. **Duas fontes oficiais em
   desacordo.** A regra que sobrevive: descrever o que se quer é obrigatório, negar é cinto de
   segurança, nunca o mecanismo — e **nunca negar estilo ou estado** ("not a game" entrega jogo).
2. **Duração máxima do Cinema Studio 4.0** — 30 s no blog de lançamento × "até 1 min" na página de
   produto. Duas fontes oficiais discordando.
3. **P2 e P3** da §6 do `REGRAS` (descrição minuciosa × personagem constante; storyboard rígido
   ajuda ou atrapalha) **continuam abertas**. A Academy **reforça** a decisão ⚫ de não produzir
   storyboard como artefato, mas **não responde** P2 nem P3.
4. **P4–P7** também continuam abertas.

---

## 6. O QUE FALTA — em ordem de valor

### ✅ Alta — FEITO em 2026-09-02, com o diagnóstico do erro antigo junto

1. ✅ **Exclusão de folha** — `model-sheet-storyboard.md`. **O erro era maior do que a fonte
   dizia:** nossas folhas carregam fundo de estúdio **+ rótulos de seção + tira de paleta**, e
   passávamos tudo como *"strict reference"* sem dizer o que não ler. Bloco de exclusão obrigatório
   escrito, com os sintomas de quando ele faltou.
2. ✅ **Ângulo reverso do ambiente** — `model-sheet-storyboard.md`. **O erro:** o Environment Sheet
   tinha WIDE + DETAIL + planta, tudo olhando para o mesmo lado; no contracampo o modelo inventava
   o que estava atrás, diferente a cada geração — e nós culpávamos o prompt.
3. ✅ **Eixo de 180° escrito DENTRO do prompt** — `direcao-cinematografica.md`. **O erro:** o eixo
   era regra nossa, aplicada ao escolher painéis. O modelo nunca era informado dele.
4. ✅ **Plano aberto trava a marcação** + **receita de continuidade completa** + **trava de pose no
   corte** — `REGRAS` §4. **O erro:** usávamos 1 das 3 entradas. O vídeo anterior ia para o
   Seedance, mas quem escrevia o bloco seguinte não recebia nem o prompt nem o keyframe anterior.
5. ✅ **Número e comparação no lugar do adjetivo** — `direcao-cinematografica.md`. **O erro:**
   baníamos o adjetivo vazio ("épico") mas aceitávamos o adjetivo de grau ("dramaticamente"), que
   também não renderiza. Junto: nunca escrever idade em palavra; nomear personagem por marcador
   visível, nunca pelo handle.
6. ✅ **Referência com papel + exclusão + grau de fidelidade** e **timestamp é orçamento de tempo** —
   `REGRAS` §3. **O erro:** o bloco REFERENCES dizia o que cada referência *é*, nunca o que tomar,
   o que não tomar, nem com que força — então tudo virava full-preserve e as âncoras brigavam.

### Média — ainda aberto

5. **Movimento de câmera por negação exaustiva** — 46 exemplos do prompt bank público. ⚠️ **Cruzar
   com a §5.1 desta lista antes de adotar**: escrever movimento por negação é exatamente o que as
   aulas dizem que não funciona. Contradição a resolver com teste, não com escolha.
6. **Ótica em graus de campo de visão** (`84° wide`, `47° medium`) ao lado dos mm.
7. **Notação de áudio na prosa:** `( )` música · `< >` efeito · `{ }` diálogo · `【 】` legenda.
8. **Cor em 10 bits** — existe e depende de pôr o bit rate em alto. Não conhecíamos.
9. **`turbo` mata o 480p** — já escrito no `REGRAS` §1, mas **é do Kairogen, não do Higgsfield**
   (o schema do Higgsfield não expõe `turbo`). Conferir a superfície antes de assumir proteção.

### Baixa / fila

10. **Os 9 cursos das outras categorias da Academy**, incluindo **dois sobre canal faceless com
    Claude + Higgsfield** — que é a nossa arquitetura exata.
11. **Os posts de blog de cada curso** trazem *"the full script, every single prompt, the asset
    sheets"*. Nenhum foi lido.
12. **`.skill` da raiz desatualizados** — decidir se são regerados ou apagados.

---

## 7. O QUE NÃO SE APLICA A NÓS — não trazer de volta

- Todo número de resolução e duração da Academy (eles rodam 4K; nós 480p + upscale local).
- "4K resolve slop" — verdade deles, irrelevante para o nosso orçamento.
- Cinema Studio como lugar de trabalho (interface web com Canvas e Elements).
- **video-to-video precisa de vídeo de origem.** Serve para anime (tem footage); **não serve para
  HQ e mangá** (página é imagem estática — ali o caminho é image-to-video).
