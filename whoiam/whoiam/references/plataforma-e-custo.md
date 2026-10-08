# Plataforma e custo — o que vale hoje

> Substitui `higgsfield-cinema-studio.md`, `recursos-higgsfield-quando-usar.md` e
> `seedance-2-5-e-regras-2026-08.md`, que tinham camadas de decisões revogadas (Leonardo,
> Kairogen, roteamento de modelo, `generate_audio: false`, storyboard). O registro dessas
> decisões está no histórico do git, não aqui.
>
> Marcas: 🟢 catálogo/plataforma · 🔵 medido por nós · ⚫ decisão do Samuel.

---

## 1. Onde o vídeo é gerado

⚫ **Cinema Studio 4.0, no site do Higgsfield, modo Video.** Por baixo ele roda o **Seedance 2.5**;
o que o Cinema Studio acrescenta são presets escolhidos antes de gerar (gênero, era, tempo, corpo
de câmera, lente, abertura, paleta, luz, emoção por personagem) e os **Elements** chamados por `@`.
Catálogo dos presets: `higgsfield-presets.md`.

🔵 O Cinema Studio 4.0 **não existe no MCP** do Higgsfield (`models_explore` não conhece o ID). O
vídeo é feito no site, pela extensão do navegador ou pelo Samuel. O MCP serve para consultar saldo
(`balance`) e preço (`get_cost`), não para gerar.

⚫ **Imagem não se gera no Higgsfield:** componentes e referências saem do GPT
(`extensao-navegador.md`).

## 2. Os parâmetros fixos de todo bloco

| Parâmetro | Valor | Por quê |
|---|---|---|
| Resolução | **480p**, conferida no seletor | 🟢 o padrão da tela é **720p** e cobra 720p sem avisar |
| Duração | **30 s** | ⚫ um bloco = uma parte do roteiro; não se parte o bloco em dois de 15 s |
| Proporção | 16:9 | 21:9 custa o mesmo crédito, mas encolhe a imagem útil no YouTube |
| Áudio | **On** | ⚫ (10/09) é o único jeito de ter o som da cena sincronizado; música se barra no texto do prompt |
| Enhancer de prompt | **Off** | os prompts já são específicos; o reescritor tende a apagar travas e geometria |
| Quantidade | 1 · **4 só em bloco de ação** | ⚫ 4/4 em tudo derruba o canal de 4,3 para 1,5 vídeos/mês |
| Modo de vídeo longo (180 s) | **nunca** | são seis gerações de 30 s presas a um prompt só, sem detalhe suficiente |

**Upscale** para entregar acima de 480p roda na pós, de graça, na RTX 3050 da casa (Studio).

**Bloco-vitrine (exceção, só com decisão do Samuel naquele vídeo):** um plano único da revelação da
criatura em 720p (195 cr), upscalado depois. Nunca multi-corte.

## 3. Custo

🔵 Seedance 2.5, medido em 19/08/2026, linear por segundo:

| 30 s | Créditos |
|---|---|
| **480p** | **75** |
| 720p | 195 (2,6×) |
| 1080p | 270 (3,6×) |

Vídeo padrão: **20 blocos × 75 = 1.500**, × 1,4 de retrabalho (estimado, nunca medido em vídeo) =
**2.100 créditos** por vídeo de 10 min. No degrau de 9.000/mês, o envelope para 4 vídeos/mês é
**2.250 por vídeo**: cabe, com folga curta. Blocos de ação em 4 takes saem do envelope; a conta é
do script:

```bash
python scripts/orcamento.py --blocos 20 --acao-4takes <n> --saldo <saldo> --meta-videos 4
```

**Antes do primeiro bloco**, a skill mostra o orçamento do vídeo inteiro com o saldo ao lado. Se não
couber, as saídas (menos blocos de ação em 4 takes, top-up, adiar) vão ao Samuel **antes** de
gastar. Descobrir que o mês acabou no bloco 14 é o que isso impede.

## 4. Referências e Elements

🟢 **Teto do Seedance 2.5:** 50 referências — até **30 imagens**, 10 vídeos e 10 áudios (vídeos e
áudios somando até 30 s por categoria). Uso típico do canal: 4 a 10 imagens por bloco.

🔵 **Elements funcionam no Cinema Studio 4.0:** o `@label` fica verde no prompt quando o Element
existe e foi reconhecido (usado nos blocos 7 e 8 do Cthulhu). Element não reconhecido = não gerar.

🔵 **Imagem por corte funciona:** dizer no texto qual `@Image` rege qual trecho faz o Seedance puxar
referências diferentes em cortes diferentes (bloco 5 do Cthulhu, 11/09).

## 5. Tamanho do prompt

🟢 Nenhum modelo do Higgsfield declara limite de caracteres. Os prompts publicados pelo fabricante
medem de 1.000 a 7.000 caracteres, a maioria entre 5.000 e 7.000. ⚫ **Nem teto nem piso:** o
prompt é tão detalhado quanto a cena pedir. Prompt longo e vago continua pior que curto e preciso;
o espaço vai para ofício (ação no corpo, geometria, profundidade, travas), não para adjetivo.
Um prompt de cena com 600 caracteres quase certamente está com falta de ofício.

## 6. Comportamentos da plataforma já vistos

- 🔵 **`nsfw` sem motivo:** uma cena de doca de 1925, todos vestidos, voltou bloqueada e cobrou os
  75 créditos; uma tentativa idêntica passou. O crédito voltou sozinho em ~8 min. Se não voltar,
  suporte.
- 🟢 Geração que falha por erro de plataforma devolve o crédito automaticamente.
- 🔵 Retrabalho em **imagem** medido no Cthulhu: ~×1,2, concentrado em cenas de colisão. Em vídeo,
  ainda não medido: é o primeiro número a registrar no próximo vídeo.
