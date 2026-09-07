# Estudo — Blender para construção de cenas do WhoIAm

> Apurado pelo Salomão e **medido nesta máquina** em **2026-09-06**. Blender instalado no mesmo dia.
>
> **Marcação de origem** (mesma convenção de `REGRAS-PRODUCAO-VIDEO.md`):
> 🔵 **medido nesta máquina hoje** — o mais forte que existe aqui ·
> 📗 dossiê do Salomão, veredito **Firme** · 📙 dossiê do Salomão, veredito **Mediana**
> (fonte secundária, ou fornecedor vendendo o próprio fluxo) ·
> ⚪ conclusão minha, sem fonte — marcada como tal, não tratar como achado ·
> ⛔ **o Salomão tentou e não conseguiu confirmar** — buraco declarado, não silêncio.
>
> Dossiês brutos:
> `D:\Agentes\SALOMAO\missoes\2026-09-06-como-usar-o-blender-versao-atual-em-2026-para-ajud\dossie.md`
> `D:\Agentes\SALOMAO\missoes\2026-09-06-segunda-coleta-dirigida-sobre-blender-apontando-pa\dossie.md`

---

> ## ⚫ REGRA DE OPERAÇÃO — os dois portões (Samuel, 2026-09-06)
>
> **Este estudo é leitura. A regra de uso está acima dele e não se negocia:**
>
> 1. **Avisar SEMPRE antes de abrir o Blender** — dizendo qual plano, qual gatilho disparou e o
>    que vai ser blocado. Nem sendo grátis o agente abre sozinho.
> 2. **Entregar o greybox (primeiro frame + `driver.mp4`) e PARAR.** O Samuel averigua.
>    **Só com a palavra dele o plano vai para a geração paga.**
>
> Gatilhos e não-gatilhos (lista fechada): §0 de `D:\Agentes\_registros\BLENDER.md`.
> O ranking que justifica a lista: §12 deste documento.

---

## 0. O que foi instalado

🔵 **Blender 5.2.1 LTS**, build de 2026-08-25, via `winget install BlenderFoundation.Blender`.
Caminho: `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`. Python interno: **3.13.13**.

🔵 GPU desta máquina, confirmada por `nvidia-smi`: **RTX 3050, 8192 MiB, driver 591.44**.

⛔ **Não está confirmado que 5.2.1 é a versão mais recente do Blender.** O binário se declara LTS —
isso é o próprio fabricante falando e vale. Mas o winget é repositório de pacote, não é a Blender
Foundation, e a coleta que iria a `blender.org/download` falhou nas duas tentativas.
**"Instalou" não é "é a atual".**

---

## 1. A resposta curta

📙 Blocar o plano no Blender antes de gerar **não virou obsoleto** — é descrito como a forma mais
confiável de dirigir um modelo de vídeo por IA em 2026, e a justificativa é técnica:

> *"AI video models like Seedance, Kling, and Veo are exceptional renders but very poor directors.
> They have no persistent understanding of 3D space — no fixed camera, no stable geometry, no
> memory of where different aspects of a scene move across different generations."*
> — *Blender for AI Filmmaking: The 2026 Guide*, Jaime Yao,
> https://flick.art/blog/blender-ai-filmmaking, 2026-06-29

📗 Um paper independente sustenta o mesmo princípio — *"rough 3D scenes in combination with
generative image and video models"* — em estudo feito junto a cineastas
(*PrevizWhiz*, https://arxiv.org/abs/2602.03838, 2026-02-03). É a **única fonte não-comercial** do
levantamento, e por isso a única marcada Firme neste eixo.

📙 E o contraintuitivo que mais importa: **menos detalhe é melhor.**

> *"Rough shapes, even cubes as stand ins for characters, are all the model needs to retain spatial
> choreography, camera movement, and timing. Too much detail can confuse the model. (...) the
> blockout is for spatial reference, not for beauty."* — mesma fonte, 2026-06-29

**Ressalva honesta:** as duas fontes que descrevem o fluxo em detalhe são de empresas que vendem
exatamente esse fluxo. A que não vende nada (o paper) sustenta o princípio, mas só o abstract foi
coletado — não tem número, nem tempo de tarefa, nem tamanho de amostra.

---

## 2. Os cinco métodos, e quais são os nossos

📙 Tabela publicada pela fonte de 2026-06-29. **"Esforço" e "Controle" são julgamento editorial
dela, não medição** — não há metodologia declarada.

| Método | O que faz | Esforço | Controle | Serve aqui? |
|---|---|---|---|---|
| **Motion reference** (vídeo → vídeo) | clipe de blockout do Blender como referência de movimento | Baixo–médio | Alto | ✅ **é o nosso** |
| **Start-frame control** | renderiza 1 frame, restiliza, usa como primeiro frame | Baixo | Médio–alto | ✅ **é o nosso** |
| **Greybox + rig de personagem** | posa personagem tosco pra travar proporção e ângulo | Médio | Alto | ✅ subestimado |
| **Cena 3D como set virtual** | ambiente estável e reutilizável entre cortes | Médio–alto | Alto | ✅ subestimado |
| Passes → ControlNet (ComfyUI local) | depth/pose/edge frame a frame | Alto | Muito alto | ❌ **hardware não dá** |

### Por que a rota de ControlNet local está fora

📙 O piso declarado pela fonte: *"16GB of VRAM is the practical floor for image work, and video
models like Wan generally want 24GB or a cloud GPU."*

🔵 Esta máquina tem **8 GB**. É metade do piso — não é distância que se resolve com configuração.

⚪ Conclusão minha: isso **reduz a decisão de cinco métodos para quatro**, e os quatro que sobram
rodam com Blender local leve + a geração em nuvem que já pagamos. Nenhuma fonte fez essa conta.

---

## 3. O fluxo concreto, com o prompt literal

📙 Publicado passo a passo pela fonte de 2026-06-29. É o material mais concreto do levantamento, e o
único com praticante nomeado.

**Etapa 1 — Blender.** Fazer a ação e o movimento de câmera com formas básicas. Exportar **o vídeo**
e **o primeiro frame** como imagem.

**Etapa 2 — renderizar o primeiro frame** (lá foi com Nano Banana), com este prompt literal:

> *"Use the provided image as the composition and pose reference. Keep composition a 100% exactly
> match of the provided sketch. Keep camera position 100% unchanged. Keep framing 100% unchanged.
> Make sure character pose stays a 100% match to the provided sketch."*

**Etapa 3 — gerar o vídeo:** frame renderizado como *start frame*, vídeo do Blender como *video
reference*. Prompt curto de propósito:

> *"Reference the character's actions and camera language from @Video."*

📙 A fonte explica por que o prompt é curto: *"Most of the information you're giving the model lives
in your two references."*

**O que eu NÃO vi:** a fonte escreve *"Here's the final result:"* e **o vídeo não foi capturado no
texto extraído**. Tenho o método, não tenho a prova. É por isso que isto é 📙 e não 📗.

### Duas armadilhas de nome, para não errarmos a chamada

⛔ **Nenhuma fonte do levantamento menciona Seedance 2.5.** Elas dizem "Seedance" e "Seedance 2.0".
Nós rodamos 2.5. O *fluxo* provavelmente atravessa; o *nome da versão* não é garantia.

⛔ A mesma página escreve **"Kling 3.0"** no corpo e **"Kling O3"** no FAQ — é a fonte se
contradizendo. **Não use este documento para afirmar nome de versão de modelo.**

---

## 4. Automação headless — medido aqui, não apurado

⛔ Os dois dossiês voltaram com **zero linhas** sobre `bpy`, `blender -b`, EEVEE, Cycles e requisitos
do Blender. A via que alcançaria `docs.blender.org` não respondeu nas duas tentativas.
**Então medi na máquina.** Tudo desta seção é 🔵, reproduzível por `Omega\blender\blockout.py`.

### O que funciona

```
blender.exe -b -P script.py
```

🔵 Roda sem interface no Windows, sem display, sem erro. Foi assim que tudo abaixo foi medido.

🔵 **`pip install bpy` existe de verdade:** versão **5.2.1** no PyPI, publicado pela **Blender
Foundation**, `requires_python == 3.13.*` — bate exatamente com a versão instalada e com o Python
interno do Blender. Releases recentes: 5.0.1, 5.1.0, 5.1.1, 5.1.2, 5.2.0, 5.2.1.

### As quatro armadilhas que quebram script escrito para Blender 4.x

Estas custaram três execuções falhadas hoje. Todas 🔵, todas reproduzíveis:

1. **`BLENDER_EEVEE_NEXT` não existe mais.** Em 5.2 o identificador voltou a ser **`BLENDER_EEVEE`**.
   Setar `'BLENDER_EEVEE_NEXT'` levanta erro. `'CYCLES'` e `'BLENDER_WORKBENCH'` funcionam.
2. **`action.fcurves` não existe mais.** Actions viraram *slotted*; o caminho agora é
   `action.layers[].strips[].channelbags[].fcurves`. `AttributeError` seco, sem aviso de migração.
3. **`scene.view_layer` não existe** — é `bpy.context.view_layer` ou `scene.view_layers[0]`.
4. **`OPEN_EXR_MULTILAYER` sumiu do enum de `file_format`.** Existe agora
   **`image_settings.media_type`**, com três valores: `IMAGE`, `MULTI_LAYER_IMAGE`, `VIDEO`.
   Ao setar `media_type='MULTI_LAYER_IMAGE'`, o `file_format` **vira `OPEN_EXR_MULTILAYER` sozinho**
   e o enum passa a aceitar só ele. **Ordem importa: `media_type` primeiro — ou nem setar
   `file_format`.**

### Passes disponíveis

🔵 Confirmados no `view_layer` desta build, entre outros: **`use_pass_z`** (profundidade — o nome não
é "depth"), **`use_pass_normal`**, `use_pass_mist`, `use_pass_position`, `use_pass_vector`,
`use_pass_object_index`, `use_pass_material_index`, e a família cryptomatte.

🔵 **EXR multilayer com z + normal + mist saiu de verdade:** `passes_0001.exr`, 383 KB,
1 frame em **0,3 s** no Workbench.

🔵 **Freestyle existe e é ligável** (`render.use_freestyle`, vem `False`). A fonte de 2026-06-29 não
menciona Freestyle — é acréscimo nosso, e é o caminho óbvio para gerar contorno tipo Canny direto do
Blender, sem passar por ComfyUI.

🔵 Saída de vídeo direta: containers `MPEG4`, `MKV`, `WEBM`, `AVI`, `MPEG1/2`, `QUICKTIME`, `OGG`,
`FLASH`, `DV`. **O MP4 driver sai do Blender sem passar pelo ffmpeg** — confirmado,
`driver0001-0024.mp4` gerado.

🔵 `bpy.ops.import_scene.gltf` disponível — **importar `.glb` de gerador de 3D funciona nativamente.**

🔵 `preferences.system.gpu_backend` = **`OPENGL`** nesta instalação (o backend Vulkan não está ativo).

⛔ `compute_device_type` do Cycles voltou **lista vazia** em modo background. Não concluo nada disso —
pode exigir `get_devices()` antes. **Fica em aberto: não sei se o Cycles usa a GPU aqui.** Como o
nosso caminho é EEVEE e Workbench, isso não bloqueia nada hoje.

---

## 5. Custo em tempo — medido, e com uma surpresa

🔵 Cena greybox (chão, humano de 1,75 m, criatura de 4 m, duas colunas), câmera 35 mm com dolly
animado por 24 frames, **854×480** (a resolução da regra do canal):

| Execução | 24 frames | Por frame |
|---|---|---|
| EEVEE, **sem world** (cena vazia de fábrica) | **30,9 s** | ~0,5 s |
| EEVEE, **com world + sol rotacionado** | **234,1 s** | ~9,8 s |
| Mesmos 24 frames de novo, saída MP4 | **183,6 s** | ~7,7 s |
| **Workbench + passes z/normal/mist** | — | **0,3 s** |

**A diferença de 7,6× entre as duas linhas de EEVEE é real e foi medida, mas eu não isolei a causa.**
A única diferença conhecida entre as duas execuções é a presença do world com nó de Background. Pode
ser o custo de iluminação de mundo do EEVEE, pode ser outra coisa. **Não afirmo o motivo — registro
o número e o que mudou.**

⚪ Conclusão minha, e é a que muda o fluxo: **o Workbench a 0,3 s/frame é praticamente de graça.**
Um clipe driver de 5 s a 24 fps = 120 frames ≈ **36 s de máquina** em Workbench, contra vários
minutos no EEVEE com world. E o Workbench é justamente o que a fonte de 2026-06-29 indica para
gerar passes de controle (*"using EEVEE or the Workbench engine"*). **Para blockout, Workbench
primeiro; EEVEE só quando precisar de sombra e volume.**

⚪ Para comparação: uma geração Seedance 2.5 a 480p custa **75 créditos** e pode sair torta. Mesmo
na linha mais cara medida, **o blockout é barato o suficiente para não precisar de justificativa por
plano.** O custo real não é a máquina — é o seu tempo montando a cena, e esse ninguém mediu.

---

## 6. Onde isto se paga — e onde não

⚪ **Esta seção é conclusão minha. Nenhuma fonte fez esta divisão.**

O levantamento vende "controle de câmera" como manchete. Para um canal de criaturas, **eu inverto a
prioridade**: o problema estrutural não é a câmera, é que **a mesma criatura precisa ter o mesmo
tamanho em relação ao humano, na mesma caverna, em cinco planos diferentes.** As duas linhas da
tabela que atacam isso — *set virtual* e *proxy de escala* — são justamente as que a fonte não
destaca.

**Vale a pena quando há continuidade:**
- mesma criatura em três ângulos diferentes
- mesma locação em cinco cortes
- eixo de olhar que precisa bater entre planos
- escala da criatura contra referência humana

**Não vale a pena:**
- plano de estabelecimento genérico
- textura e atmosfera
- close sem movimento
- qualquer plano que você aceite refazer duas vezes

📙 O trade-off, dito pela própria fonte que vende o fluxo — e é honesto:

> *"More Blender control means more predictability of the output. This translates to less of the
> model's generative magic."*

---

## 7. O add-on de Blender da Higgsfield — a recomendação é NÃO, por enquanto

📙 Anunciado em 2026-08-25 (~215 mil views no X em um dia). Descrito como *"a previz copilot rather
than a mesh generator"*: você descreve a cena, ele devolve o blockout dentro do Blender; descreve a
câmera, ele anima; e reblocla o plano em segundos quando o layout muda. Acesso por **Higgsfield MCP**
ou pelo agente em nuvem deles. *"Do I need a Higgsfield plan? Yes for the first-party path."*
— https://www.explainx.ai/blog/higgsfield-blender-mcp-ai-blockout-august-2026, Yash Thakker,
2026-08-25

**A própria fonte é a mais autocrítica do levantamento:**
- *"No public benchmark yet."*
- *"until independent builders publish .blend files and iteration logs, treat marketing velocity as unverified"*
- *"the demo's hand-edit step is not optional polish, it is the job"*
- não se sabe se o reblock preserva rig, material e luz — *"The demo does not answer that."*

⚪ **Minha recomendação: não adotar agora**, por três motivos:
1. É anúncio de 12 dias atrás **sem um único uso independente verificado**. Adotar hoje é virar
   beta-tester pagando.
2. Ele acelera *fazer* o blockout. **Esse não é o nosso gargalo** — desenhar cinco caixas é barato
   (§5). O gargalo é a geração final acertar.
3. Troca uma dependência que controlamos (Blender local, grátis, offline) por uma que não
   controlamos (nuvem, crédito, uptime alheio).

📙 E o alerta que esta casa já registrou em 2026-09-02: **o trial do Higgsfield MCP pede cartão e
converte sozinho em plano pago se não for cancelado.** Cadastrar cartão é decisão sua, não de agente.

**Isso se inverte se** aparecer relato independente com `.blend` e log de iteração publicados.

---

## 8. Text-to-3D para proxy de criatura — o que sabemos e o que não

📗 **TRELLIS** (Microsoft, MIT, https://github.com/microsoft/TRELLIS) — fonte primária:
- *"An NVIDIA GPU with at least 16GB of memory is necessary."* Verificado em A100 e A6000.
- *"The code is currently tested only on Linux."* Windows remetido a uma issue, *"not fully tested"*.
- Instalação compila submódulos CUDA com conda. Não é `pip install`.
- Exporta GLB com `simplify=0.95` (remove 95% dos triângulos) e `texture_size=1024`.
- **Os próprios autores desaconselham text-to-3D direto:** *"It is always recommended to do text to
  3D generation by first generating images using text-to-image models and then using TRELLIS-image
  models. Text-conditioned models are less creative and detailed due to data limitations."*

⚪ Duas conclusões minhas:
- **8 GB contra piso de 16 GB, em Windows não testado: rodar TRELLIS aqui não é caminho.** E é o
  mesmo número 16 GB que apareceu, independentemente, no eixo do ControlNet — duas apurações que não
  conversam entre si convergindo na mesma barreira sobre esta máquina.
- O `simplify=0.95` que incomodaria quem quer asset final **serve ao nosso caso**: proxy de escala
  quer malha leve.

⛔ **Hunyuan3D, Tripo, Meshy e Rodin: zero linhas nos dois dossiês.** Não sei se são grátis, se rodam
local, quanta VRAM pedem, nem — o que mais importa por regra desta casa — **se o tier grátis pede
cartão.** Não deduzo.

---

## 9. O que ficou sem resposta (e por quê)

Isto não é lacuna por preguiça — é resultado declarado. A segunda coleta, feita justamente para
fechar estes buracos, **voltou pior que a primeira**: uma única fonte externa, de 2024.

⛔ **Não confirmado:**
- Se 5.2.1 é a versão atual do Blender; qual é a LTS vigente. (O binário se declara LTS. 🔵)
- Requisitos de hardware oficiais da Blender Foundation. **O número 16 GB dos dossiês é dos modelos
  de IA, não do Blender — não transportar de um para o outro.**
- Se a RTX 3050 dá conta de Cycles. (De EEVEE e Workbench dá — §5 é medida. 🔵)
- **Poly Haven, BlenderKit, Mixamo, Rigify, Geometry Nodes, add-ons de storyboard, Grease Pencil:**
  zero ocorrências nos dois dossiês.
- Os quatro nomes que a primeira coleta trouxe **sem URL e sem confirmação**: o rig do **toyxyz**
  *"Character bones that look like OpenPose for Blender"*, o **AIGODLIKE ComfyUI-BlenderAI-node**, o
  **fSpy** (que casaria a câmera do Blender com um frame já gerado), e o add-on da Higgsfield.
  **Trate como lista de nomes a investigar, não como recomendação.**
- Quanto tempo leva para ter resultado útil. **Nenhuma fonte dá número de tempo** — só os adjetivos
  "Baixo/Médio/Alto". (O tempo de máquina está medido em §5; o tempo humano, não.)
- Zero relatos de terceiros independentes. Nenhum Reddit, nenhum criador sem vínculo comercial.

**Por que falhou:** a via de busca `tavily` — a única que alcançaria `docs.blender.org`,
`projects.blender.org` e `blender.org/download` — **não respondeu nas duas coletas**. Na segunda, o
buscador ainda fatiou o enunciado da missão em palavras soltas e saiu procurando por "PRIMARIAS" e
"ZERO", o que explica os 15 resultados fora do tema. **"Não respondeu" não é "não existe".**

---

## 10. O que existe hoje, pronto para usar

`Omega\blender\blockout.py` — roda como está:

```
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b -P C:\Ai-Project\Omega\blender\blockout.py
```

Monta a cena greybox com escala humana de referência, anima a câmera 35 mm, e cospe:
`gb_*.png` (frames greybox) · `driver0001-0024.mp4` (o clipe driver de movimento) ·
`passes_0001.exr` (z + normal + mist) · `cena.blend`.

🔵 Todos os quatro foram gerados e verificados hoje. **É o esqueleto, não a ferramenta** — os
caminhos de saída estão fixos no scratchpad e as medidas da cena são de teste.

---

## 11. Próximo passo proposto

⚪ Proposta minha, não decidida:

1. **Um teste real de ponta a ponta quando a API do Higgsfield chegar**: pegar UM plano de um vídeo
   que já existe, blocar no Blender, gerar pelos dois caminhos (só prompt × start frame + motion
   reference) e comparar. **É a única forma de trocar 📙 por 🔵 neste assunto.** Custo: 2 gerações
   de 480p = 150 créditos.
2. **Terceira coleta dirigida** só para `docs.blender.org` e para os add-ons — mas só depois de
   entender por que o `tavily` cai. Repetir a mesma coleta sem consertar a via é gastar tempo.
3. Promover o `blockout.py` a ferramenta de verdade (parâmetros por linha de comando, saída dentro
   da pasta do projeto do vídeo) — **só se o teste do item 1 confirmar que o fluxo vale.**

---

## 12. QUAL TIPO DE PLANO — a resposta, e ela é incômoda para este canal

> Segunda rodada de coleta, **2026-09-06**, com pergunta curta (a lição do vault sobre buscador de
> palavra-chave — foi o conserto e funcionou). **10 fontes**, contra 5 da primeira.
> Dossiê: `D:\Agentes\SALOMAO\missoes\2026-09-06-blender-blockout-para-video-gerado-por-ia-em-que-ti\dossie.md`

### 12.1. A regra que responde tudo

📗 **Seis fontes independentes** dizem a mesma coisa em 2026: o blockout é referência **espacial**,
não visual, e carrega **quatro coisas — composição, movimento de câmera, profundidade e posição**.
A aparência fica com o modelo. (Flick 2026-06-29, invideo 2026-08-10, Toonkit 2026-09-06,
Mixar 2026-08-07, Tesseract 2026-07-25, explainx.ai 2026-08-25.)

⚪ Disso o Salomão tirou uma regra que **nenhuma fonte enuncia**, e ela responde a pergunta inteira:

> **O blockout funciona na proporção em que a carga dramática do plano está na GEOMETRIA, e falha na
> proporção em que ela está na FORMA e no ROSTO.**

Geometria = onde as coisas estão, para onde a câmera vai, que tamanho tem cada coisa, quando cada uma
chega. Forma e rosto = como a criatura é, que textura tem a pele, que cara o ator faz.

### 12.2. O ranking, do que mais ganha para o que menos ganha

| # | Tipo de plano | Ganho | Por quê |
|---|---|---|---|
| **1º** | **Plano de escala** | **Máximo** | Escala é função de três números — tamanho, distância, focal — e são exatamente os que o blockout transfere sem ambiguidade. **Um cubo do tamanho de um prédio é inequívoco em qualquer nível de detalhe.** |
| **2º** | **Cena de ação** | **Alto, com teto** | Único tipo que duas fontes nomeiam como beneficiado. Coreografia de várias figuras é o que o texto descreve mal e o espaço 3D descreve bem. |
| **3º** | **Cena de diálogo** | **Só com cobertura** | O valor está no rosto e no microtiming — nada disso o blockout entrega. O que sobra é **eyeline e eixo de 180°** entre cortes, e isso não é pouco. |
| **4º** | **Revelação de criatura** | **Mínimo** | A carga está na silhueta e na superfície — a parte que todo o material manda deixar para o modelo. |

⚪ Onde cada um quebra — conclusão do Salomão, sem fonte:

- **Escala:** o modelo não tem obrigação de manter escala *relativa entre duas gerações*. O blockout
  garante cada plano isoladamente; **nada garante a coerência entre eles.**
- **Ação:** o blockout acerta quem está onde e por onde a câmera passa, e **erra o timing fino do
  contato** — porque a trajetória "não é cópia frame a frame" (§12.4) e ação é feita de impactos.
  **Corolário prático: planeje para o instante do impacto não ser o ponto do plano.** Corte no antes
  e no depois, ou deixe o impacto fora de quadro. É o que o cinema já faz, por outros motivos.
- **Diálogo:** para um plano **isolado**, não vale — vale start frame + prompt. Para uma cena com
  **dois ou mais ângulos que vão ser cortados juntos**, vale, e o valor é inteiramente continuidade.
- **Revelação:** ver §12.3.

### 12.3. O problema deste canal, dito sem rodeio

⛔ **Nenhuma das dez fontes menciona criatura, monstro, revelação ou anatomia não-humana.** Zero.

⚪ Mas duas afirmações apuradas, encadeadas, dão a resposta:

1. 📙 *"Explain in sentences what each grey shape actually is. That minimises misread objects"* —
   exemplo literal da fonte: *"the cylinder in the centre is a robot"* (Toonkit, 2026-09-06).
2. 📗 "Menos detalhe é melhor" — seis fontes.

**A forma cinza não comunica o que ela é: ela precisa ser NOMEADA em texto.** O modelo não deduz
"isto é um robô" do cilindro — ele é informado, e então usa o *prior* que já tem de "robô".
**Uma revelação de criatura é exatamente o caso em que não existe esse prior para invocar:** se a
criatura fosse nomeável em duas palavras com resultado previsível, ela não seria a nossa criatura —
seria um dragão genérico.

> **Numa revelação, o blockout dá o TEMPO da revelação, o TAMANHO, a TRAJETÓRIA e a CÂMERA.
> Não dá a criatura.**

📗 **E a saída já é nossa.** Três fontes independentes mandam incluir **sempre** character sheet +
imagem de referência de estilo (Toonkit 2026-09-06, invideo 2026-08-10, Flick 2026-06-29) — que é
exatamente o que a skill `whoiam` já faz com model sheets → storyboards. **Numa revelação o blockout
é coadjuvante e a imagem de referência é protagonista.** A inversão exata do que vale numa ação.

### 12.4. Achado de plataforma — o Seedance 2.5 aceita whitebox como referência FORMAL

📗 **Três fontes independentes**, uma delas com números de API:

- *"in Seedance 2.5 the 3D whitebox is included as a formal reference input"* e *"a single generation
  stretches to about 30 seconds"* — Toonkit, https://toonkit.io/en/models/seedance-blender, 2026-09-06
- *"up to nine stills and three clips per generation, 4 to 30 seconds at 480p or 720p"* —
  Mixar, https://www.mixar.app/blog/ai-video-generator-blender, 2026-08-07
- *"Seedance 2.5 was built with exactly this kind of workflow in mind, offering direct support for
  white-model, or blockout-style, references"* — Tesseract Academy, 2026-07-25

⚪ **Isto muda o enquadramento da decisão:** não estamos improvisando um uso lateral — o whitebox é
entrada declarada do modelo que já usamos. E o limite de **480p ou 720p** declarado pela Mixar é o
dado mais duro do conjunto justamente por ser o menos conveniente para quem vende. **Bate com a §1 do
`REGRAS-PRODUCAO-VIDEO.md`.**

### ⚠️ Conflito aberto sobre duração — e ele decide o tamanho do plano

📙 **Toonkit (2026-09-06):** *"The trajectory is followed well, but **it is not a frame-exact copy**.
Short, simple **3–5 second** moves come out most reliably; long or highly complex paths are better
split into several generations."*

📙 **Flick (2026-06-29) e invideo (2026-08-10)** vendem o oposto: *"The model follows your camera
movement and character action **exactly**"* e *"pixel-accurate to the Blender camera"*.

⚪ **A do Toonkit pesa mais** — é a única que declara um limite contra o próprio interesse, e é a mais
nova. Mas ela contradiz **a si mesma** na mesma página, ao dizer que one-take longo "deveria" sair
melhor. **Planejar para 3–5 s por geração até termos medida nossa.**

### 12.5. Duas ferramentas que apareceram, e nenhuma foi testada aqui

📗 **`wassermanproductions/blockout`** — https://github.com/wassermanproductions/blockout, 2026-07-07,
**Apache-2.0**, fonte primária (README do autor). App livre feito *especificamente* para blocar ação:
194 movimentos de personagem, 39 movimentos clássicos de câmera, multidão de 2 a 60 em um clique,
manequins e veículos **em escala do mundo real com matemática de lente real** (sensores Super 16 / 35
/ Full Frame / 65mm), e aviso de sanidade *"when a walk implies 6 m/s"*. Exporta pacote com
`reference.mp4` + `depth.mp4` + `normal.mp4` + `prompt.txt` + `comfyui-workflow.json`, **com perfis
para Seedance 2.0, Veo 3.1, Kling, LTX 2.3 e Wan 2.2**. Tem **servidor MCP com 33 ferramentas**,
registrável em uma linha:
`claude mcp add blockout -- node /CAMINHO/blockout/mcp/blockout-mcp.mjs`

📗 E ele **falha alto, não em silêncio** — o que importa por lição desta casa: traz tabela de
sintoma→correção e declara, para dado de ação inválido, *"Current builds reject it before the
timeline can fail."* Também declara exports determinísticos (*"byte-identical frames on every run"*).

⚠️ **Armadilha declarada para Windows, que é a nossa:** *"Current release artifacts are unsigned"* —
o SmartScreen avisa no primeiro uso, e a orientação do próprio autor é conferir o **SHA-256** na
página de release antes de rodar. **Não instalar sem conferir o hash.**

📙 **Regras operacionais de depth map** (mindstudio.ai, Luis Chavez-Mattos, 2026-07-22) — as três são
baratas de seguir: **nunca JPEG** (*"compression introduces artifacts in depth maps that can mislead
the model"*), sempre PNG ou EXR; **escolher uma convenção** claro-perto ou escuro-perto e **manter no
projeto inteiro**; bordas mal definidas geram artefato de halo. Peso de condicionamento sugerido:
**0,5–0,75, começando em 0,6** — sem metodologia declarada, é experiência do autor.

⚠️ A mesma fonte descreve extrair o passe pelo Compositor (Render Layers → **Normalize** → PNG/EXR)
mas **não declara em que versão do Blender testou.** Vale a lição da §4: sondar o runtime antes de
escrever automação em cima disso.

### 12.6. "O que o pessoal mais usa" — sem resposta, e o porquê importa

⛔ **Não foi respondido.** A coleta sobre tutoriais de YouTube não trouxe amostragem nenhuma — nem
contagem, nem lista de canais, nem títulos, nem visualizações.

📗 E trouxe um **achado negativo verificável**: os dois acervos de tutorial de Blender que entraram na
coleta — *Blender Tutorials Channel* (3,21 mil inscritos, 293 vídeos) e a playlist *Blender 3D
Tutorials* do Nafay 3D (39 vídeos, 169 mil views) — **não têm UM único vídeo sobre previz para IA**.
São modelagem clássica, visualização de produto e cursos completos, com conteúdo de 1 a 7 anos.

📙 E a própria Blender Foundation declara que **não centraliza tutoriais**: *"The most up-to-date
tutorials can be found on social media. Look out for the hashtag #b3d."*

📙 O **único** vídeo de YouTube transcrito no lote (`xBLGsYLwgks`) é sobre **o inverso** do nosso
fluxo — a IA operando o Blender por MCP, não o Blender alimentando a IA. O balanço que o próprio
criador faz na tela: *"for texturing, it worked out very well. For creating models was a little bit
basic. Creating add-ons, very powerful. File organization, super powerful. For following tutorials,
it's not entirely there yet."* **Sem data, sem autor identificado, legenda automática, e o criador
vende um curso dentro do próprio vídeo.** As afirmações dele sobre versão ("Blender 5.1+") e sobre
"Claude investiu na Blender como patrocinadora corporativa" ficaram em **Reza a lenda** — a mesma
transcrição escreve "model contact protocol" e "five coded", então o ruído da legenda é alto.

⚪ Conclusão: **"o que os criadores mais fazem" não tem fonte central para consultar** — teria que ser
levantado por amostragem, e não foi. Não confundir com "ninguém faz": o material que descreve o fluxo
existe, é de 2026, e só não vem de tutorial de YouTube.

### 12.7. O viés do lote — leia antes de usar isto

⚪ **Nove das dez fontes vendem o fluxo.** Todo modo de falha registrado aqui veio de fonte admitindo
limite do próprio produto — não é frame-exato, física (pano, cabelo, fluido) exige várias gerações,
sem benchmark público. **São admissões, não medições. Trate a lista de falhas como piso, nunca como
teto.**
