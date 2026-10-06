# Referências por cena — o que o exemplo do Samuel revelou (2026-09-11)

> Achado de produção, não doutrina de plataforma. Nasceu de um prompt real que o Samuel trouxe
> (um vídeo de perseguição de scooter/demônio/pizza) e da comparação com o que a gente vinha
> fazendo — poucas imagens genéricas por bloco, um único plano contínuo. Este arquivo existe pra
> próxima sessão não redescobrir isso do zero.

## O sintoma que motivou isto

Bloco 5 do Cthulhu ("O porto") saiu com o navio Alert **pequeno demais**, **sem tripulação de
fundo**, e **dentro do navio em vez do cais**. O Samuel notou que produções que conseguem "cortar"
de personagem pra personagem dentro de um vídeo usam **muito mais imagem de referência do que a
gente estava usando** — não 1 ou 2, um conjunto inteiro por cena.

## O que o prompt de exemplo realmente tinha (contagem literal)

Não foram 4 imagens. Foram pelo menos **13 referências distintas** num vídeo de ~14s:

| Tipo | Exemplos no prompt do Samuel | O que resolve |
|---|---|---|
| **Ambiente, DOIS ângulos** | `<<<world>>>` (frente) + `<<<world_reverso>>>` (reverso) | continuidade de cenário entre cortes que olham em direções opostas |
| **Personagem** | o menino, a menina, o demônio (3 refs) | rosto/figurino — o que a gente já fazia |
| **Veículo/objeto de cada personagem** | scooter do menino, scooter da menina, triciclo do demônio (3 refs) | identidade do objeto que o personagem usa a cena toda |
| **Detalhe DENTRO de um objeto** | o velocímetro da scooter, o celular no suporte (2 refs) | closes específicos que precisam bater com o objeto principal |
| **Imagem de ESCALA/RELAÇÃO** | "use `<<<image_2>>>` pra relação de tamanho entre o demônio e os personagens" | exatamente o problema que a gente teve com o Alert — sem essa imagem, o modelo não sabe o tamanho relativo |
| **Objeto de enredo, reaparece** | o "power-up" flutuante (usado 2× no prompt) | prop que a câmera precisa reconhecer de novo mais tarde |
| **Prancha de composição por CORTE** | `<<<image_1>>>` no corte de 00:00–00:03, `<<<image_4>>>` no corte de 00:06–00:10 | cada CUT TO tem sua própria imagem-chave, não uma imagem genérica pro vídeo inteiro |

**A lição não é "usar mais imagens por usar"** — é que cada categoria acima resolve um problema
que um prompt só de texto não resolve. Contar quantas categorias a cena PRECISA, não travar num
número fixo (nem 4, nem 13 — o que a cena pedir).

## A pegadinha técnica: isso é Elements, e Elements não cobre todo modelo

O `<<<uuid>>>` do exemplo é o sistema de **Elements** do Higgsfield (`show_reference_elements`).
Ele precisa que o modelo aceite Elements — e o **Seedance 2.5 não está confirmado na lista** (só
Nano Banana Pro/2, GPT Image 2, Seedream 4.5/5 lite, Cinema Studio Image 2.5, Cinema Studio Video
2.0/3.0, Seedance 2.0, Kling 3.0 — ver `higgsfield-cinema-studio.md` §5). O `multi_shots`/CUT TO
também é recurso do Cinema Studio Video, que trava em **12s totais** — incompatível com a regra do
canal de "sempre 30s por bloco".

⚫ **Decisão do Samuel, 2026-09-11:** seguir no **Seedance 2.5**, sem Elements. Em vez de
`<<<uuid>>>`, as imagens entram como `image_references`/`video_references` normais (upload direto),
e o texto do prompt descreve explicitamente qual imagem vale pra qual trecho/corte — sem a garantia
de amarração que o Elements dá. **Isto é teste, não certeza** — registrar o veredito depois de
usar em blocos de verdade (seção de registro empírico do `higgsfield-cinema-studio.md`).

## O processo novo, por bloco

1. Antes de gerar, o agente escreve um **documento de referências da cena**: lista cada imagem
   necessária, categorizada pela tabela acima (ambiente ×ângulos, personagem, objeto do
   personagem, detalhe, escala/relação, prop de enredo, prancha por corte), com um prompt pronto
   pra gerar cada uma.
2. As imagens são geradas — pelo Samuel no GPT, ou pelo agente direto no Higgsfield
   (`nano_banana_pro`, ~2 créditos cada, `count:4` de graça — ver `higgsfield-cinema-studio.md`
   §1b). Imagem é barata; **não é onde o orçamento se decide**.
3. O agente sobe tudo (arquivo local ou link) via `media_upload`/`media_import_url` e monta o
   prompt do Seedance com todas as referências relevantes + descrição explícita, por trecho de
   tempo, de qual imagem rege qual momento.
4. **Nunca poupar imagem por poupar** — a pergunta certa é "quantas categorias da tabela essa cena
   toca", não um teto arbitrário.

## Registro empírico (preencher depois de usar)

- [x] **Seedance 2.5 amarra imagem por corte — confirmado no bloco 5 (2026-09-11).** Com 7
      referências (escala, ambiente ×2 ângulos, navio ×2 ângulos, prop, grupo), o resultado usou
      cortes diferentes puxando de referências diferentes, parecido com o exemplo do Samuel. Não é
      Elements de verdade (sem `<<<uuid>>>`), mas descrever explicitamente qual imagem rege qual
      trecho no texto **funciona na prática**. Vale continuar sem poupar imagem — **o teto real do
      Seedance é ~50 referências**, bem longe do que a gente vinha usando.
- [x] Imagem de escala/relação resolveu o problema do navio pequeno do take anterior.
- [x] Ambiente em dois ângulos deu continuidade.
- ⚠️ **Achado novo, não esperado:** a mesma geração voltou com `status: "nsfw"` (bloqueada pelo
      filtro de moderação) **sem nenhum motivo aparente** — cena de doca de 1925, todo mundo
      vestido. Cobrou os 75 créditos mesmo bloqueando. Uma segunda tentativa idêntica passou normal
      e completou. **Higgsfield estornou o crédito da tentativa bloqueada sozinho, sem precisar
      contato com suporte** — em ~8 min. Se acontecer de novo e não estornar sozinho, aí sim vale
      contato com o suporte.
