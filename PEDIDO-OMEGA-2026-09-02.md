# Ordem de serviço para o Omega — 2026-09-02 (versão final)

> **Substitui a versão anterior deste arquivo.** A anterior foi escrita antes das
> 75 aulas serem transcritas e antes de você ter feito a primeira rodada de
> limpeza. Esta considera as duas coisas.
>
> **Documento irmão:** `ESTUDO-ACADEMY-HIGGSFIELD-completo.md` — o conteúdo das
> 75 aulas, organizado por tema, com citação literal e aula de origem. **Leia-o
> antes desta ordem.** Transcrição bruta em
> `D:\Agentes\SALOMAO\estudos\academy-higgsfield\`.
>
> ⚠️ **Instrução do Samuel que vale acima de tudo: em dúvida de comportamento,
> PERGUNTE A ELE.** Não decida sozinho o que for escolha, e não apague o que você
> não tem certeza de que morreu.

---

## 0. O que já está feito — não refaça

Confirmado por varredura hoje. **Nada abaixo precisa ser tocado de novo:**

- ✅ Marcador **🎓** e aviso de calibragem no cabeçalho do `REGRAS-PRODUCAO-VIDEO.md`.
- ✅ **Limite de caracteres, morto nos três números**, nas duas cópias do corpus:
  `direcao-cinematografica.md`, `higgsfield-cinema-studio.md`,
  `seedance-2-5-e-regras-2026-08.md`, `seedance-receituario.md`, `SKILL.md` e a
  §3 do REGRAS. A medição está certa lá (1.020–7.084, mediana ~6.300, 8 de 10
  acima de 5.000).
- ✅ ⚫ Decisão do Samuel sobre tamanho de prompt, registrada.
- ✅ As duas cópias do corpus aparentemente foram sincronizadas.

**Uma pergunta que ficou sem resposta e continua valendo (§6.1):** qual das duas
cópias é a fonte de verdade daqui pra frente?

---

## 1. O QUE ENTRA — técnicas novas, com fonte

Cada item abaixo tem citação literal e aula de origem no documento irmão. Isto é
o grosso do trabalho: **são capacidades que não existem em documento nosso
nenhum.**

### 1.1. PRIORIDADE MÁXIMA — o trio que conserta cena de diálogo

Isto ataca exatamente o problema que o Samuel corrigiu à mão (duas pessoas
conversando saindo artificiais), e **nenhuma das três está no nosso corpus**:

1. **Referência de ângulo reverso do AMBIENTE.** Para cena de diálogo com
   contracampo, gerar imagens dos **dois lados da sala** e alimentar o modelo com
   as duas. Sem isso o fundo pula entre os cortes e *"the scene will never piece
   together in the edit"*. O mesmo princípio vale para ação: locação com vista de
   frente **e** vista de costas trava o batch.
2. **Plano aberto de estabelecimento no início trava a marcação.** *"start the
   video with a wide establishing shot. That way Seedance places everyone exactly
   where they need to be and they stay locked for the entire video."*
3. **Eixo de 180° escrito no prompt**: câmera estática, personagem A sempre do
   mesmo ângulo nas falas dela, corte para B **por cima do ombro esquerdo dela**
   nas falas dele.

> **E aqui entra a linha que o Samuel pediu explicitamente:** escrever a distinção
> entre **3/4 de LOCAÇÃO** (legítimo — a Academy manda usar sempre, dá volume e
> profundidade) e **3/4 de PESSOA** (proibido — é o padrão velho que ele matou).
> O termo é ambíguo em português e já vazou uma vez (porta da cabana, jul/2026).

### 1.2. Régua de diagnóstico — 4/4 versus sorte

**Sempre gerar 4 de uma vez, e isso é diagnóstico, não luxo.**

- **Os 4 saíram errados → o problema é o PROMPT.**
- **1 ou 2 saíram errados → foi sorte; regere.**

*"Knowing the difference between a broken prompt and a bad roll is how you save
credits."* Nós não temos nenhuma régua desse tipo. **Isto deveria entrar na §5 do
`REGRAS-PRODUCAO-VIDEO.md`, antes da ordem de tentativa que já está lá.**

### 1.3. Números no lugar de adjetivos

- Comparação em vez de adjetivo: **não "rápido", e sim "três vezes mais rápido que
  um dolly cinematográfico típico"**. *"AI models don't really get big
  descriptions, but they understand direct comparisons."*
- Câmera em números crus: órbita de 8 m para 4 m, altura de 3 m para 2 m.
  *"video models prefer arithmetic over vague words like 'dramatically'."*
- Ação em passos de meio segundo: mão em 0,5 s, elmo em 1,5 s, de pé em 3 s.
  *"When the timing is locked, the model can't rush it or skip stages."*

### 1.4. Desenho no lugar de descrição para GEOMETRIA

*"Instead of explaining the geometry in words, I give Claude a picture. I
literally draw where the cannonball should hit and where everyone stands. One
drawing tells the model what 10 sentences can't."*

Isto é um método de entrada que não temos e é barato — e imagem custa 1–2
créditos.

### 1.5. Escada de simplificação, ampliada

A nossa §5 tem "partir o plano em dois". As aulas dão a escada inteira:

1. multi-shot falhou → **cair para UM plano contínuo**;
2. cena apertada → **partir em duas**;
3. cena grande → Claude escreve o prompt todo e **depois divide** (8A, 8B, 8C);
4. plano chapado → **aumentar a cobertura** (2 planos viram 3, com ângulos).

### 1.6. Continuidade entre cenas — a receita completa

Três entradas, não uma. A nossa §4 só tem a terceira:

- **prompt da cena anterior → para o Claude** (para ele saber o que aconteceu);
- **keyframe → referência de estilo**;
- **vídeo anterior → para o Seedance**.

E a trava de pose no corte: *"The poses at the end of shot one exactly match the
start of shot two. If you don't spell this out, the AI treats the cut as a brand
new scene and throws away the poses."*

### 1.7. Transformação de criatura — serve direto ao canal

*"We gave it a hard number, 0.4 seconds. (...) this is a weapon deploying, not a
magic sequence, because if you let a transformation take its time, you get a
glowing anime power up. Every single time. The instant snap is what keeps it
real."*

**Número duro + enquadrar como mecânica, não como magia.** É a diferença entre
metamorfose com peso e brilho de anime — e o canal é de criatura.

### 1.8. Mudança de estado resolve-se com ASSET, não com texto

Roupa rasgada que "se remendava" no plano seguinte → **gerar nova folha de
personagem já com a roupa rasgada**. Vale para ferimento, sujeira, transformação
parcial, envelhecimento (flashback usa o mesmo truque).

### 1.9. Escala e multidão

- **Nunca pedir número.** Três camadas: um sujeito nítido à frente, multidão densa
  atrás, silhuetas sumindo na bruma. *"You only see about 40 soldiers clearly, but
  your brain fills in the rest."*
- **Figurante não se pede como multidão** — construir **classes** distintas (dois
  ou três arquétipos) dá variedade de silhueta e mantém consistência.
- **Névoa é limpeza barata**: limitar visibilidade a ~20 m esconde o que o modelo
  quebra ao fundo.

### 1.10. A cura do "cara de videogame"

*"one long, unbroken take is exactly how video games look. Real movies cut."*
A cura é **cobertura variada dentro do plano gerado**: quatro cortes secos, cada
um com sua ótica (órbita 50mm, contra-plongée 24mm, close 85mm, aberto 35mm). E o
sintoma a evitar: **câmera flutuando atrás do personagem** é enquadramento de
jogo em terceira pessoa.

### 1.11. Rubrica de aceitação de take — o buraco que a gente sabia ter

O documento irmão traz a checklist inteira (§8). O sinal mais importante:

> **Corte rápido é esconderijo, não estilo.** *"Quick cuts are what this model
> does when it can't animate the motion underneath."* Se a geração começa a picotar
> sozinha, ela está escondendo movimento que não conseguiu animar.

E a regra de acúmulo: *"Each one is pretty minor, but together, they're the
difference between an ad and an AI ad."*

### 1.12. Detalhes de ferramenta

- **Cor em 10 bits** — existe, e depende de **pôr o bit rate em alto**. Não
  conhecíamos.
- **Roteamento de modelo de imagem:** Soul Cinema para personagem/locação/keyframe
  (8 imagens por 1 crédito, mais cinematográfico por padrão) · **GPT Image 2 para
  TEXTO, movimento e storyboard** · Nano Banana Pro para consertar personagem sem
  regerar.
- **`turbo: true` no Seedance 2.5 restringe a resolução a 720p/1080p** — quem ligar
  turbo perde o 480p sem aviso e paga 2,6×. **Isto tem que virar aviso escrito ao
  lado da §1**, é o modo de falhar que a §1 existe para impedir.
- **Seedance 2.0 aceita só 4 imagens de referência** (o 2.5 aceita 30) e para em
  15 s. **Rotear bloco para o 2.0 por preço custa 26 âncoras** — recalcular a §3 do
  `planejamento-fluxo-higgsfield.md`.
- **50 referências = 30 imagens + 10 vídeos + 10 áudios**, com teto de 30 s no
  total para vídeo e para áudio.
- **4K no Seedance 2.5 é upscale** — o guia oficial diz que o modelo gera
  nativamente até 1080p. Reforça a nossa arquitetura.

---

## 2. O QUE PRECISA SER REVISTO — e não é apagar

### 2.1. ⚠️ A doutrina das negativas — o item mais delicado desta ordem

**Três aulas independentes dizem que negação não funciona no Seedance**, e a
terceira dá nome ao fenômeno: *"the negation trap"* — *"AI models completely
ignore the word 'not'. It just sees 'game' a dozen times and goes with it."*

**Mas o guia oficial de prompt do mesmo Higgsfield usa negativas o tempo todo**
(*"No logos, no readable text"*, *"no music, no discernible dialogue"*), e o
prompt bank público escreve movimento de câmera inteiramente por negação.

**São duas fontes oficiais da mesma empresa em desacordo. NÃO RESOLVA ISSO
SOZINHO.** Registre o conflito com as duas citações.

O que **pode** entrar já, porque os dois lados sustentam: **descrever o que se
quer é o mecanismo; negar é, no máximo, cinto de segurança.** O que **não** pode
é apagar as nossas regras negativas testadas com base num palpite.

**Isto toca:** as "regras negativas testadas" do `seedance-receituario.md`, o
bloco `NEGATIVES` da §3 do REGRAS e a frase *"No music. No score."*
**Traga ao Samuel antes de mexer.**

### 2.2. A folha de personagem — um modo de falhar que a nossa expõe

A Academy é enfática: **um rosto por folha**. *"Our character sheet has multiple
faces in one image. (...) Seedance doesn't understand which face to grab. So it
drifts, a little in every scene. And by scene 5, our hero is a stranger."* Eles
chegam a **apagar o rosto do painel de corpo inteiro**.

A nossa `model-sheet-storyboard.md` prescreve turnaround com **cinco vistas de
corpo inteiro**. **Não estou dizendo que o nosso está errado** — estou dizendo que
existe um modo de falhar nomeado pelo fabricante e a nossa folha se expõe a ele.
**Decisão do Samuel**, com o custo dos dois lados na mesa.

### 2.3. O enhancer — nuance, não contradição

A Academy manda **ligar** o enhancer no Soul Cinema para **explorar estilo em
imagem** com prompt curto. A nossa recomendação de desligar é sobre o **prompt de
vídeo hiperespecificado**, onde o reescritor apagaria a âncora de realismo.
**São usos diferentes.** Registre a distinção em vez de tratar como conflito.

---

## 3. O QUE CONFIRMA O QUE JÁ TÍNHAMOS

Não gera trabalho, mas vale carimbar como 🎓 porque agora tem fonte independente:

- pipeline em estágios (roteiro → assets → geração);
- folha de personagem de três painéis, fundo cinza, luz suave;
- âncora de realismo (o prompt oficial abre com *8K IMAX, Lubezki/Deakins,
  contre-jour, pore-level*);
- geração ruim é matéria-prima — *"Not writing one genius prompt, but reading what
  broke and fixing only that"*;
- combinar pedaços de gerações diferentes é o padrão, não o remendo;
- imagem é quase de graça, então regerar é o comportamento certo;
- **⚫ a decisão de não fazer storyboard como entregável** — eles usam asset sheets
  + shotlist + prompt com stages, exatamente como o Samuel escolheu.

---

## 4. ⚫ O CONTRATO DE DIREÇÃO — agora com respaldo do fabricante

> **O Samuel dita a CENA. Você dirige.**

Ele entrega: o que acontece, quem está lá, onde, e a emoção. Você decide:
enquadramento, ângulo, altura de câmera, lente, movimento, posicionamento,
cobertura, ritmo e onde corta.

**E isto não é mais só preferência dele.** A skill oficial do Higgsfield faz
exatamente isso: *"It splits the scene into shots automatically and **picks the
framing, close-ups, medium shots, all of it**. That way you get real camera angle
changes in your generations, just like an actual movie."* O usuário só *"tells
what happens in the first scene"*.

**Corolário operacional:** nunca devolva pergunta de técnica. *"Qual lente você
quer?"* é pergunta errada. Dúvida é sobre **intenção** (*"essa cena é de ameaça ou
de tristeza?"*). Decisão técnica cara ou arriscada: **decida e declare** o que
decidiu e por quê.

⚠️ Isto **convive** com a ordem de perguntar em caso de dúvida: a dúvida que se
pergunta é de **intenção e de comportamento**, nunca de ofício de câmera.

---

## 5. GUARDA-CORPOS

1. **Não apague decisão ⚫ do Samuel** sem perguntar. Em particular a §2 do REGRAS
   (storyboard) — a Academy **reforça**, não derruba.
2. **Não apague P2–P7** da §6 do REGRAS. A Academy não respondeu P2 nem P3.
3. **Contradição não resolvida não é entulho.** Marque, não apague. Duas vivas
   hoje: as negativas (§2.1) e a duração máxima do Cinema Studio 4.0 (30 s × 1 min,
   duas fontes oficiais discordando).
4. **Não trate marketing 4K da Academy como evidência contra os 480p.** A §1 é
   decisão de orçamento (⚫ + 🔵 medido).
5. **Não adote a skill oficial sem comparar campo a campo.** Ver §6.
6. **Método atravessa, número não atravessa.** Eles rodam 4K/15s ou 30s; nós
   rodamos 480p.

---

## 6. O QUE PERGUNTAR AO SAMUEL

Junte numa pergunta só quando puder.

1. **Qual cópia do corpus é a fonte de verdade?** (repo `C:\Ai-Project\Omega\whoiam\`
   × instalada `~/.claude/skills/whoiam\`). Sem isso elas divergem de novo.
2. **As negativas (§2.1)** — como tratar o conflito entre as aulas e o guia oficial?
3. **A folha de personagem (§2.2)** — manter o turnaround de cinco vistas de corpo
   inteiro, ou migrar para o formato de um rosto só?
4. **Baixar a skill oficial `higgsfield-seedance-prompt.skill`?** Ela é citada em
   quatro cursos e é baixável no post de cada um. É o item de maior valor ainda em
   aberto — as aulas descrevem o que ela faz (tags, coordenadas em metros,
   movimento com segundos, regras anti-alucinação) mas não mostram o interior.
5. **Os posts de blog dos cursos** trazem *"the full script, every single prompt,
   the asset sheets"*. Vale colher?
6. **video-to-video sobre footage real** — serve ao WhoIAm ou é ruído?
7. **Os 9 cursos das outras duas categorias**, incluindo dois sobre **canal
   faceless com Claude + Higgsfield**, que é a nossa arquitetura exata. Levantar?

---

## 7. O QUE ESTA ORDEM NÃO COBRE

- A skill oficial do fabricante **não foi baixada**.
- Os posts de blog de cada curso **não foram lidos**.
- Os 9 cursos das outras duas categorias **não foram levantados**.
- O conflito das negativas **não tem resolução com fonte**.
