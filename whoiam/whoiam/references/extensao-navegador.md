# A extensão do Claude no navegador — o executor no ChatGPT e no Higgsfield

> ⚫ **Reescrito em 2026-10-06, depois que a extensão parou no Bloco 8 do Cthulhu — com razão.**
> A versão anterior deste arquivo supunha que a extensão abria arquivos do disco, anexava por
> caminho (`C:\...`) e conferia se o download tinha sido salvo. **Ela não faz nenhuma das três
> coisas.** A sessão dela não está ligada ao computador do Samuel: ela só vê o que é **anexado no
> chat dela** e o que está **na tela do navegador**.

---

## 1. O que cada um faz

| Quem | Faz | Não faz |
|---|---|---|
| **Claude Code** (esta skill) | escreve `referencias.md` / `cena`; monta o **pacote** de cada passo (`montar_pacote.py`); **recebe** os downloads (`receber_pacote.py`): renomeia, move e confere; atualiza o `registro.json` | não clica no navegador |
| **Samuel** | arrasta a pasta do pacote para o chat da extensão; aprova cada download e cada imagem; dá o OK de crédito; diz "pronto" ao Claude Code | não renomeia nem move arquivo à mão |
| **Extensão** | lê o `PACOTE.md` anexado; gera no ChatGPT; anexa no GPT **só** o que foi anexado no chat dela; baixa em ordem; no Higgsfield, preenche settings, sobe imagens, cria Elements; **para** nos pontos marcados | não abre caminho do disco; não usa a Biblioteca do ChatGPT; não renomeia nem confere arquivo salvo; não gera vídeo sem OK |

## 2. O pacote — a única coisa que vai para a extensão

Para cada passo que a extensão executa, o Claude Code monta uma pasta **`_pacote_passoN`** na pasta
do bloco:

```bash
python scripts/montar_pacote.py --referencias "<bloco>\referencias.md"   # passo 1: imagens no GPT
python scripts/montar_pacote.py --cena "<bloco>\cena.txt"                # passo 4: vídeo
```

Dentro dela:
- **`PACOTE.md` autocontido**: as regras do passo, os prompts inteiros, o que anexar em cada item,
  a ordem, os pontos de parada e a lista `ARQUIVOS ESPERADOS, NA ORDEM`. Nenhum caminho para abrir.
- **os anexos copiados** (`anexo_01_collins.png`, … / `imagem_01_ref_01_….png`, …), com nomes que o
  `PACOTE.md` cita.

O Samuel seleciona **todos os arquivos da pasta** e arrasta para o chat da extensão. O pacote é
gerado **a partir** da `referencias.md` / `cena`, nunca escrito à mão: não há como os dois
divergirem. Mudou o prompt → montar o pacote de novo.

**Imagem gerada num item e usada como anexo de outro** ainda não existe no disco: o pacote a cita como
*"a imagem número N que você gerou nesta conversa"*, e o prompt começa com uma linha em inglês
apontando para ela. Por isso todas as imagens de um passo se geram **na mesma conversa nova**.

**Biblioteca do ChatGPT ("Add from library"): nunca.** Ela guarda as saídas de tentativas
anteriores; anexar de lá traz de volta o estilo errado.

## 3. Gerar imagens no ChatGPT (passo 1)

1. Conversa **nova** em chatgpt.com, sem imagem anterior. Uma conversa por pacote; criatura
   (ultra-realista) e o resto (naturalista) em conversas separadas.
2. Para cada item do `PACOTE.md`, em ordem: anexar o que ele indica, colar o prompt inteiro sem
   editar, esperar, **baixar só a versão aceita**. O download pede o OK do Samuel a cada vez.
3. O nome que o Chrome dá ao arquivo **não importa**: a **ordem dos downloads** é o que identifica
   cada imagem. Não pular item, não baixar nada fora da lista.
4. Recusa do filtro: no máximo 2 reescritas da parte recusada; se não passar, registrar e seguir.
5. **Parar no fim** com o relatório numerado: `N. <nome esperado> — baixada como <nome do Chrome>`
   (ou "não baixada: motivo").

## 4. Receber o que foi baixado (Claude Code)

Quando o Samuel disser "pronto":

```bash
python scripts/receber_pacote.py --pacote "<bloco>\_pacote_passo1\PACOTE.md" --simular
python scripts/receber_pacote.py --pacote "<bloco>\_pacote_passo1\PACOTE.md"
```

Ele pega os arquivos que chegaram em Downloads **depois da criação do pacote**, em ordem de chegada,
casa com a lista esperada, renomeia, move para o destino e confere. **Quantidade diferente: não move
nada** — conferir com o relatório da extensão (item recusado → `--pular N`; download a mais → tirar
de Downloads) e rodar de novo. Depois, mostrar as imagens ao Samuel para a aprovação.

## 5. Elements no Higgsfield (passo 3)

O Samuel arrasta para o chat da extensão o arquivo aprovado (ex.: `obj_chapeu-collins.png`) com a
instrução: Elements → criar novo · categoria (`cri_`/`per_` Character · `amb_` Location · `obj_`
Prop/Object) · nome **exato** = nome do arquivo sem `.png` · conferir que o `@nome` fica **verde** no
Cinema Studio · não gerar nada. Nome recusado pela plataforma: parar e relatar.

## 6. O vídeo no Cinema Studio (passo 4)

Pacote do passo 4 (só monta com as `ref_` já no lugar): settings, as imagens numeradas na ordem do
`@Image`, o prompt inteiro e a lista dos `@`. A extensão preenche, confere **480p**, sobe as imagens em
ordem, cola o prompt, confere os `@` verdes e **para pedindo o OK do Samuel com o custo da tela**. Com
o OK, gera e baixa; o Claude Code recebe com `receber_pacote.py` (vai para `takes\take-N.mp4`).

Status `nsfw` sem motivo já aconteceu (doca de 1925, todos vestidos); uma tentativa idêntica passou e
o crédito voltou sozinho em ~8 min. Relatar e perguntar antes de tentar de novo.
