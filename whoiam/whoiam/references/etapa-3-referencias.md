# Etapa 3 — Referências do bloco

> Para cada bloco, antes do prompt de cena: o documento que diz **quais componentes entram** e
> **quais imagens de referência precisam ser geradas** para aquele momento específico (o convés
> já em chamas, o Collins caído, a vista do que o personagem vê). As imagens são geradas no GPT
> pela extensão, a partir dos componentes. No vídeo, cada uma entra como `@Image N`.

---

## 1. Por que imagem e não só texto

O texto não fixa o que é geométrico ou de estado: o tamanho do navio ao lado do cais, o que está
atrás do personagem no contracampo, o estado do fogo, a pose de chegada de um corte. No Bloco 5 do
Cthulhu o Alert saiu pequeno, sem tripulação e no lugar errado; com 7 referências (escala, ambiente
nos dois ângulos, navio nos dois ângulos, prop, grupo) o problema sumiu, e o Seedance passou a
puxar referências diferentes em cortes diferentes. Teto da plataforma: **30 imagens**. Imagem não
é onde o orçamento se decide.

**A pergunta certa é "quantas categorias abaixo esta cena toca", não um número fixo.**

## 2. As categorias

| Categoria | Quando | O que resolve |
|---|---|---|
| **Ambiente do bloco** (frente e, se houver contracampo, reverso) | sempre que o lugar está num estado específico deste bloco | geografia e estado do lugar travados entre cortes |
| **Personagem no estado do bloco** | ferido, molhado, ajoelhado, transformado, com outra roupa | o estado; a identidade continua vindo do Element |
| **Escala / relação** | dois corpos ou objetos de tamanhos muito diferentes; posição de grupo | o modelo não sabe tamanho relativo sem ver |
| **Objeto ou detalhe** | o prop que a câmera vai fechar; o detalhe dentro de um objeto | close que tem que bater com o objeto principal |
| **Quadro de chegada de um corte** | corte que termina numa composição exata (a revelação, o último quadro do bloco) | o corte tem destino, não só começo |
| **POV** | o que um personagem vê | o contraplano sem inventar |
| **Último quadro do take anterior** | bloco que continua o anterior | luz, paleta e pose da emenda. **Não se gera: copia-se** de `bloco-(N-1)\takes\ultimo-quadro.png` |

**Referência de expressão é close-up** (`direcao.md`, regras de enquadramento): se a imagem existe
para fixar o que o personagem sente, o rosto ocupa a maior parte do quadro. **Over the shoulder do X**
é sempre a câmera atrás do ombro de X, vendo o que X vê.

**Todo personagem importante do momento aparece na imagem.** Antes de entregar, conferir a lista de
quem o roteiro põe naquele momento contra quem o prompt descreve — no Bloco 8, o último quadro saiu
sem o William.

**Nenhuma referência repete a composição de outra.** Duas imagens do mesmo momento com o mesmo
enquadramento (o capitão caído; o mesmo capitão caído com o Johansen ao lado) não dão informação nova
ao modelo e empurram dois cortes para o mesmo plano. Cada referência traz um ponto de vista próprio:
chão, plano médio, sobre o ombro, de cima.

Uma imagem por categoria e por momento. Cada imagem mostra **um sujeito e uma ação**, com composição
simples: quadro denso faz o modelo duplicar personagem.

**🔴 Nunca usar manequim, boneco ou figura sem rosto como marcador de personagem em referência**
(Samuel, 2026-10-09). Foi testado no Bloco 8 do Cthulhu e o vídeo copiou os bonecos: um vermelho no lugar
do rosto do Collins e um verde "vivo" no fundo. O modelo trata tudo o que está na imagem como conteúdo da
cena. Personagem em referência aparece com o rosto e o figurino da folha dele (`per_*.png`, anexada),
como nos blocos anteriores. O bloqueio de "pessoa real" visto antes tinha como causa provável a folha
antiga, já trocada; se voltar, avisar o Samuel antes de tentar outra solução. Vale também para cores
de marcação e qualquer outro tag visual dentro da imagem.


**Referência é momento de passagem, não quadro parado** (Samuel, 2026-10-07): ela fixa como a cena
está num instante; o vídeo passa por ela em movimento, com ação antes e depois
(`etapa-4-cena.md`, BEATS). Por isso a imagem mostra o meio de um movimento sempre que possível.

**Referência não é primeiro quadro, por padrão.** Ela informa aparência, estado e geometria. Só vira
`start_image` quando o `cena.md` disser isso explicitamente, com motivo. O modelo trata o primeiro
quadro como âncora e desacelera para não se afastar dele.

## 3. O formato de `referencias.md`

Arquivo: `C:\Ai-Project\Criaturas\<Nome>\blocos\bloco-NN\referencias.md`

```markdown
# Bloco NN — <título> · referências

> 🟢 **PASSO 1 de 4 do bloco** (ordem completa no `EXECUTAR.md` da pasta). Depois dele, PARAR para a
> aprovação do Samuel; o `cena.md` só entra no passo 4.
>
> ⚠️ **PROMPT DE IMAGEM DE REFERÊNCIA — gerar no ChatGPT, com a geração de imagem nativa do GPT.**
> **NÃO usar o MCP do Higgsfield nem o site do Higgsfield para gerar estas imagens.**

PARTE DO ROTEIRO: <a parte N, colada como o Samuel escreveu>
INTENÇÃO: <uma linha: pavor crescente / luto / ameaça latente…>
EFEITO PEDIDO: <se houver>  |  nenhum
CONTINUA DE: bloco-(N-1)  |  nenhum

## Componentes deste bloco (Elements)
| Element | Em quais beats | Observação |
|---|---|---|
| @per_johansen | 1–4 | identidade |
| @obj_chapeu-collins | 3–4 | passa para a cabeça do Johansen no beat 4 |

## Imagens de referência (geradas no GPT, nesta ordem)

### ref_01_conves-pos-luta  →  @Image 1
DESTINO: ChatGPT — geração de imagem nativa do GPT (NÃO usar o MCP do Higgsfield)
CATEGORIA: ambiente do bloco (frente)
RESOLVE: estado do convés depois da luta, mantido em todos os cortes
ANEXAR NO GPT: componentes\amb_alert-conves.png
SALVAR COMO: C:\Ai-Project\Criaturas\Cthulhu\blocos\bloco-08\ref_01_conves-pos-luta.png
PROMPT:
```
<inglês, uma imagem, um momento, terminando com as âncoras da tabela de estilo>
```

### ref_02_…  →  @Image 2
…
```

**O aviso de destino é obrigatório** no topo do arquivo e em cada item.

**O número do arquivo é o `@Image` do upload.** `ref_01` sobe primeiro e é `@Image 1`. A ordem de
geração e a de upload são a mesma, e o prompt de cena usa esses números. Não reordenar depois de
escrito o `cena.md`.

**Gerar a imagem-base primeiro.** A referência de ambiente do bloco (o estado do lugar) é a `ref_01`
e ancora as outras: toda referência seguinte do mesmo lugar anexa `ref_01` para o estado do fogo,
da chuva e do dano não mudar de uma imagem para outra.

## 4. Como escrever cada prompt de referência

- Abrir dizendo **o que tomar de cada anexo**:
  `Using the attached character sheet only for his face, build and costume — not its grey
  background or layout — and the attached image 1 for the exact deck and fire state, …`
- Depois **o momento**: pose, ação congelada, para onde olha, tamanho de plano e altura de câmera
  em metros.
- Profundidade: o que está em primeiro plano, o sujeito, o fundo (comandar o fundo por tamanho,
  foco e luz: `small in frame, far background, out of focus`).
- **Estado declarado:** ferimento, sujeira, molhado, o que segura. É o que mais quebra a continuidade.
- **Momento antes, não durante**, quando a ação é a cena: referência do instante anterior ao gesto,
  para o vídeo ter de onde partir.
- Âncoras no fim, conforme `estilo-e-contencao.md` §1 (com criatura: **E + C**; sem: **B + C**, mais
  **D** se houver rosto em close).
- Gore implícito: ferimento sugerido (mancha escura molhada no casaco), nunca sangue em cena.

## 5. Portão

A extensão gera e salva; o Samuel aprova o conjunto. Referência ruim refaz no GPT (sem custo de
crédito). Só com o conjunto aprovado se escreve o `cena.md`.
