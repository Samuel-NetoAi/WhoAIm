# Calendário, fila e o arquivo de estado

## Por que existe um arquivo de estado

Você começa cada conversa sem memória do canal. Não sabe o que foi publicado, qual thumb está
rodando, se o vídeo de terça tinha tags, quantos vídeos sobraram na gaveta. Se você adivinhar, o
Samuel recebe um calendário errado com cara de calendário certo — e vai descobrir isso tarde.

Por isso: **o estado do canal vive num arquivo, não na sua cabeça.** A skill `whoiam` já diz a
mesma coisa ("estado do projeto vive FORA da skill — perguntar ao usuário ou consultar o arquivo
que ele indicar; nunca presumir"). Aqui esse arquivo tem nome e formato.

## `canal-estado.md` — formato

```markdown
# Estado do canal WhoIAm
Atualizado em: 2026-08-14

## Configuração
- Idioma: pt-BR
- Duração-alvo: 8–12 min
- Dias de postagem: quarta e sábado
- Horário: 19:00 (America/Sao_Paulo)
- Frequência atual: <n>/semana ou /mês
- Gaveta mínima: 6
- Estreia: <data, ou "não estreou">

## Orçamento de produção (novo, ago/2026)
- Plataforma de vídeo: Higgsfield (modo híbrido — imagens por MCP, vídeo no Cinema Studio web)
- Plano / créditos por mês: Ultra — 3.000
- Créditos gastos no mês corrente: <n>
- Custo médio observado por vídeo: <n> créditos  (a `whoiam` informa por vídeo)
- Fator de retrabalho observado: <n>  (orçado em ×1,4 até haver medição real)
- **Frequência sustentável = créditos/mês ÷ custo médio por vídeo** → <n> vídeos/mês
- Frequência sustentável < frequência atual? → é alerta de primeira linha no calendário, não nota
  de rodapé. Quebrar o padrão de frequência é o erro que o curso repete em três aulas.

## Canais de referência
| Canal | Por que é referência | Duração média | Frequência | Padrão de título observado |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

## Padrão de thumbnail em teste
- Padrão atual: <descrição em uma linha>
- Vídeos já publicados com esse padrão: <n> (troca só depois de 3–4)
- Prints de referência salvos em: <caminho>

## Teste de tags (lote dividido)
| Vídeo | Com tags? | CTR | Impressões | Observação |
|---|---|---|---|---|

## Gaveta (prontos, ainda não publicados)
| # | Criatura | Duração | Pacote pronto? | Slot previsto |
|---|---|---|---|---|

## Publicados
| Data | Criatura | Título | Com tags? | CTR | Impressões | Retenção | Trocas feitas |
|---|---|---|---|---|---|---|---|

## Desvios registrados
- <data> — <o que foi contra o curso, qual regra, e a justificativa do Samuel>
```

Se o arquivo não existir, ofereça criar. Se o Samuel disser para tocar sem ele, toque — mas avise
uma vez que o calendário e a auditoria vão sair cegos, e não repita o aviso a cada mensagem.

---

## Como montar o calendário

Use `scripts/calendario.py`. Data feita de cabeça é onde erro entra sem aviso, e o script já aplica
os dias e o horário fixos, projeta quando a gaveta acaba e marca as semanas em risco.

```bash
python3 scripts/calendario.py --inicio 2026-09-02 --dias qua,sab --hora 19:00 \
  --prontos 9 --producao-por-semana 2 --semanas 16
```

O `--producao-por-semana` é o número **honesto** de vídeos que o Samuel consegue terminar por
semana, não a meta. É esse número que decide se o padrão sobrevive: publicando 2 e produzindo 1,5,
a gaveta de 9 dura 18 semanas e depois quebra. Publicando 2 e produzindo 2, ela nunca quebra nem
cresce. Mostre isso, não esconda numa nota de rodapé.

## As regras que o calendário tem que respeitar

**Antes de estrear:**
- Ter o lote pronto (8–10 vídeos). O curso manda montar a gaveta de adiantados exatamente para
  não falhar o padrão em dia de imprevisto (aula 10, [09:20]–[09:56]).
- Não publicar vários de uma vez na estreia (aula 7, [22:01] — confiança média). Os vídeos prontos
  entram na fila, não no ar.
- "Aquecer" a conta antes: assistir, curtir e comentar vídeos do nicho por 1–2 dias (aula 7,
  [20:31] — confiança média). Vale lembrar uma vez ao montar a estreia; não é para repetir sempre.

**Durante:**
- Dias e horário fixos (aula 10, [10:24]–[11:45]). A única exceção é gaveta vazia com vídeo pronto
  fora da janela.
- Subir sempre como **"não listado"** primeiro, depois publicar ou programar (aula 17, [11:51] e
  [32:17]). Isso dá a última checagem antes do vídeo existir para o público.
- Nunca quebrar o padrão (aula 10, [08:23]) e **nunca postar com menos frequência do que já vinha**
  (aula 12, [02:20]; aula 10, [08:49]; aula 13, [19:56] — três aulas diferentes).

**Para subir a frequência:**
- Só para cima, e por degrau: 2 → 3 → 4 por semana. Critério combinado com o Samuel: três semanas
  seguidas com a gaveta em 6 ou mais. Esse critério é nosso; o curso só diz "aumente conforme o
  canal esquenta" (aula 9, [28:44]) sem dar número.
- O teto útil para canal atemporal é 3–4/semana (aula 10, [06:56]); o curso sugere evoluir para
  1 por dia se der (aula 10, [07:52]), mas isso é 7/semana e ele mesmo condiciona à qualidade
  (aula 1, [20:56]).

**O que NÃO é regra de frequência, apesar de parecer:**
- Os números de 1 a 3 vídeos por dia são para **canal hype** (notícias, pautas quentes) — aula 10,
  [02:07]. O WhoIAm é atemporal. Não misture as duas tabelas; é o erro mais fácil de cometer lendo
  a seção `quando-postar` das regras.

## Datas com CPM alto

O curso menciona que o CPM sobe em picos de anunciante — Black Friday e final de ano (aula 14,
[12:41]). Se houver escolha sobre onde alocar os vídeos mais fortes do lote, essas janelas são
onde a mesma view paga mais. Não é motivo para segurar vídeo nem para quebrar o padrão.

## O que o calendário deve mostrar

Não é uma lista de datas. É um instrumento de aviso. Sempre inclua:

1. A tabela de slots com data, hora, criatura e se o pacote já está pronto.
2. **A semana em que a gaveta chega a zero** com o ritmo de produção informado — em destaque.
3. Quantas semanas faltam para o critério de subir um degrau de frequência ser atingido.
4. Qualquer slot sem vídeo alocado, como pergunta ao Samuel, não como buraco silencioso.
5. **O mês em que o orçamento de créditos estoura**, se o ritmo de produção informado for maior que a
   frequência sustentável. É o mesmo tipo de aviso do item 2, mas a restrição é dinheiro, não tempo —
   e o `--producao-por-semana` do script não sabe nada sobre créditos, então essa conta é sua.

## O `--producao-por-semana` mudou de natureza

Antes ele era só uma pergunta de disciplina: quantos vídeos você consegue TERMINAR por semana. Agora
ele tem um teto que não depende de esforço: **os créditos do mês.** Se o Samuel disser "consigo fazer
2 por semana" e o orçamento financiar 0,5 por semana, o número honesto é 0,5 — e é esse que vai para o
script. Usar o número da vontade em vez do número do orçamento produz um calendário que erra sozinho.
