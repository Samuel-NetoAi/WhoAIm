# Receituário — o que o modelo faz de verdade

> Comportamentos observados em produção. Não é teoria: é o que o Seedance faz com cada tipo de
> instrução. **Atualizar quando o Samuel relatar algo novo**, com data e bloco. O que não foi
> testado no 2.5 está marcado como tal.
>
> Até ago/2026 a produção era Seedance 2.0 em 15 s; os itens marcados **(2.0)** vêm de lá e valem
> como hipótese no 2.5 até um bloco real confirmar.

---

## Confirmado no Seedance 2.5 (Cinema Studio)

- **Imagem por corte funciona** (bloco 5 do Cthulhu, 11/09): com o texto dizendo qual `@Image` rege
  qual trecho, cortes diferentes puxam referências diferentes.
- **Imagem de escala resolve tamanho relativo** (o Alert pequeno demais sumiu com ela).
- **Ambiente nos dois ângulos dá continuidade** entre cortes que olham em direções opostas.
- **Oito cortes num bloco de 30 s geraram câmera lenta.** Daí a regra: 3 a 4 cortes, nunca mais de 4.
- **Âncora ultra-realista funciona na criatura e exagera humano e paisagem** (out/2026): espuma em
  toda onda, gotícula em tudo, nuvem hiperdetalhada. Daí o estilo em duas camadas e a contenção
  (`estilo-e-contencao.md`).

## Observado no 2.0, a confirmar no 2.5

- **(2.0) O primeiro quadro freia o movimento.** Com start frame, o modelo desacelera para não se
  afastar dele: tentáculos chegam violentos e depois seguram os personagens parados "como bonecos".
  Mitigação: referência não é start frame por padrão; movimento violento leva aceleração declarada
  em cada beat (`velocity increases throughout, no settling`); arrasto se escreve `yanked violently
  out of frame`, não `pulled` (sai lento).
- **(2.0) Pico no começo.** O bloco tendia a sair metade excelente, metade mediana, com o fim mais
  fraco. Mitigação: em bloco de impacto, o pico vai nos primeiros segundos e o fim fica para a
  consequência.
- **(2.0) Referência de personagem apaga a atmosfera pedida no texto** ("Cthulhu sobre névoa densa"
  veio limpo, sem névoa). Mitigação: atmosfera que precisa estar lá vai **na imagem de referência**
  do bloco, não só no texto.
- **(2.0) Quadro denso duplica personagem.** Composição com vários sujeitos e ações ao mesmo tempo
  faz o modelo repetir gente. Mitigação: cada imagem de referência mostra um sujeito e uma ação;
  figurante que não precisa de consistência não recebe referência.
- **(2.0) Primeiro quadro no meio da ação** faz o vídeo começar do meio: o início da ação não existe
  para ele reconstruir. Mitigação: a referência mostra **o instante antes** do gesto.
- **(2.0) Música aparece sozinha** sob a imagem (caso Medusa/águia). Mitigação: a regra de som do
  prompt (`no music, no score`, sempre acompanhada da lista de sons diegéticos).

## Comportamento de composição (vale para referência e para vídeo)

- **Viés de retrato:** sem geometria declarada, dois sujeitos saem lado a lado e de frente para a
  câmera, mesmo em confronto. "Encarando de frente" vira "facing front". Escrever posição no quadro,
  olhar e distância de cada um.
- **Simetria vazando:** a correção acima, aplicada a tudo, transforma encontro comum em duelo.
  Confronto usa simetria; encontro cotidiano usa assimetria.
- **Co-presença total:** com dois personagens importantes, os dois aparecem em todo plano, de
  frente, sem reação. Exigir plano de reação de cada um e corpo virado para a ameaça.
- **Mudança sutil não se vê:** pupila contraindo ou peito respirando não diferenciam dois momentos.
  Mudança entre momentos precisa ser **binária** (olho aberto/fechado) ou **ambiental** (algo entra
  ou sai do quadro).
- **"Ao fundo" migra para a frente** se não for comandado por tamanho, foco e luz.

## Hipóteses abertas — testar quando aparecer a ocasião

- Luta entre criaturas ou com poderes (energia, voo, escala gigante): nunca testada. A regra de
  plano-sequência vale só para luta humana corpo a corpo.
- Teste da negativa (Samuel, set/2026): negativa solta × negativa acompanhada × só positivo, em
  cenas sem ação, 2 takes por braço. Até rodar, vale a regra das travas (`etapa-4-cena.md`).
- Retrabalho real em vídeo: primeiro número a medir.

## Registro (preencher a cada bloco que ensinar algo)

| Data | Criatura / bloco | O que se viu | O que mudou |
|---|---|---|---|
| 2026-10-06 | Cthulhu / bloco 8 (referências) | Pedidas na mesma conversa do GPT das referências antigas, as imagens novas saíram no estilo ultra-realista anterior, ignorando a âncora naturalista | Conversa nova por lote e por estilo (`extensao-navegador.md` §3) |
| 2026-10-06 | Cthulhu / bloco 8 (referências) | Duas referências do mesmo momento (capitão caído; Johansen ajoelhado) saíram quase idênticas — mesmo enquadramento, só um personagem a mais | Cada referência de um bloco precisa de ponto de vista diferente; referência que repete composição de outra não entra |
| | | | |
