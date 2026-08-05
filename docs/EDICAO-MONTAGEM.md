# EDIÇÃO E MONTAGEM — base de referência do canal

> Estudo de gramática de edição para o WhoIAm, escrito para ser consultado
> ANTES de decidir um corte, uma transição ou o ritmo de uma sequência —
> para que a edição não venha "do nada".
> Complementa `whoiam/references/direcao-cinematografica.md` (que resolve o
> quadro, dentro do plano) — aqui é o que acontece ENTRE os planos.
> Criado 2026-08-05. O que estiver marcado como **PONTO DE PARTIDA** ainda
> não foi validado em vídeo publicado; vira regra depois do veredito real.

---

## 0. A pergunta que abre qualquer decisão

> "Este corte serve à emoção do momento?"

Walter Murch (editor de *Apocalypse Now*, *O Paciente Inglês*) organiza toda
decisão de corte numa hierarquia de prioridades, a **Regra dos Seis**, com os
pesos que ele mesmo atribui:

| # | Critério | Peso | O que é |
|---|----------|------|---------|
| 1 | **Emoção** | 51% | O corte preserva o que o espectador deve SENTIR? |
| 2 | **História** | 23% | O corte faz a narrativa avançar? |
| 3 | **Ritmo** | 10% | O corte acontece no momento certo, é "musical"? |
| 4 | Eye-trace | 7% | O olho do espectador está onde o próximo plano precisa que esteja? |
| 5 | Planaridade (regra dos 180°) | 5% | O eixo da cena foi respeitado? |
| 6 | Continuidade espacial | 4% | A geografia bate exatamente? |

A regra prática: **se for preciso sacrificar algo, sacrifique de baixo para
cima — nunca abra mão de emoção por continuidade.** Emoção + história + ritmo
somam 84%; os três últimos, 16%. É uma licença explícita para cortar "errado"
tecnicamente quando o resultado emocional é melhor.

Por que isso importa MUITO neste canal: nossos clipes são gerados em sessões
diferentes, então a continuidade espacial perfeita é impossível. A Regra dos
Seis diz que tudo bem — desde que emoção, história e ritmo estejam certos, os
itens 4–6 são os que devem ceder. **A inconsistência entre clipes é um problema
de 16%, não de 100%.**

---

## 1. Transições como pontuação

Toda transição é um sinal de pontuação. Usar a errada é escrever com vírgula
onde precisava de ponto final.

| Transição | Significa | Usar quando |
|---|---|---|
| **Corte seco (hard cut)** | vírgula / nada | 90% dos casos. Continuidade dentro da mesma cena, mudança de ângulo, ação contínua. Aumenta tensão e ritmo. |
| **Dissolve (crossfade)** | ponto e vírgula: passagem de tempo, ligação entre ideias | Elipse temporal curta dentro da mesma sequência; memória, sonho, devaneio; ligar dois lugares que "conversam". |
| **Fade to/from black** | ponto final / início de capítulo | Fim de ato, salto grande de tempo, morte, fim do vídeo. Nunca no meio de uma sequência. |
| **Match cut** | rima visual | Duas formas/movimentos/cores parecidos em planos diferentes — o corte "invisível" mais elegante que existe. |
| **Whip/blur/zoom** | energia, agressão | Ação, luta, perseguição. Barato em excesso: no máximo 2–3 por vídeo. |
| **Corte no impacto** | pontuação musical | Cortar exatamente no golpe, no trovão, no acorde. |

Regra dura: **transição é motivada, nunca decorativa.** Se você não consegue
dizer numa frase o que a transição está comunicando, use corte seco.

### O caso específico do canal: clipes de IA de sessões diferentes

A escolha depende da **relação de continuidade entre o clipe A e o B**:

| Relação entre A e B | Transição correta |
|---|---|
| Mesma cena, mesma ação continuando (você tentou manter consistência) | **corte seco** — e se o clipe B continua o movimento de A, corte no meio do movimento, não na pausa |
| Mesma cena, ângulo/enquadramento diferente | **corte seco** (aceite a variação de cor/luz; corrija na correção de cor, não com transição) |
| Mesma sequência, salto de tempo pequeno | **dissolve curto** (12–20 frames) |
| Nova sequência / mudança de local ou de época | **fade through black** (20–30 frames) ou dissolve longo |
| Transformação, magia, delírio, sobrenatural | transições de textura: `film-burn`, `dreamy-zoom`, `ripple`, `linear-blur` (disponíveis em `@remotion/transitions`) |
| Dois clipes com forma/movimento parecidos | **match cut** — corte seco, alinhando o ponto de forma |

**No Studio (implementado em 2026-08-05):** a transição é por limite, declarada
como `transicao_da_anterior` no `scenes.json` e ajustável na aba de cenas. Os
sete presets foram renderizados de ponta a ponta e todos funcionam:
`corte` · `match` · `dissolve` (crossfade) · `fade` (pelo preto) ·
`film-burn` · `dreamy-zoom` · `ripple` · `linear-blur`.
Corte e match cut não geram elemento de transição nenhum — o corte seco é
ausência de transição, e por isso as duas cenas ficam com o tempo de tela
inteiro.

### Cortes de áudio: J-cut e L-cut

Split edits — o áudio e a imagem trocam em momentos diferentes:

- **J-cut**: o áudio do próximo plano entra ANTES da imagem. Cria expectativa
  ("o que é esse som?"), puxa o espectador para a cena seguinte.
- **L-cut**: o áudio do plano anterior continua DEPOIS da imagem trocar.
  Suaviza o corte, mantém o clima.

No WhoIAm a narração é uma faixa contínua por cima de tudo — ela já funciona
como uma cola permanente entre os planos, que é por si só a razão de a
montagem tolerar tanta troca de clipe. O J/L-cut aqui se aplica ao **SFX dos
clipes**: fazer o som do clipe seguinte entrar ~10 frames antes da imagem
(J-cut) ou o som do anterior atravessar o corte (L-cut) amarra dois clipes
que visualmente não combinam. É barato de implementar e o ganho de coesão é
alto. **PONTO DE PARTIDA.**

---

## 2. Ritmo, duração de plano e retenção

Números que servem de piso e teto, não de fórmula:

- O espectador precisa de **~3 segundos** para absorver um plano novo; passando
  de ~5s sem que nada mude (movimento, informação, revelação), a atenção cai.
- B-roll típico: **2 a 10 segundos** por clipe. Documentário/narrativo permite
  planos mais longos — o que segura não é a frequência de cortes, é a clareza
  narrativa.
- Canais de documentário longo (Kurzgesagt, Johnny Harris, Real Engineering)
  mantêm 50%+ de retenção em vídeos de 20 min com ritmo deliberado, não com
  corte rápido.
- **Uma ideia nova por cena.** Cada corte deve entregar exatamente um elemento
  conceitual novo. Cena que não acrescenta nada deve sair, não ficar mais curta.

Como isso conversa com a regra de material do canal
(`clipes = duração da narração ÷ duração de cada clipe`): a fórmula dá o piso
para não haver frame congelado, mas o ritmo diz onde gastar. Sequência de
tensão crescente pede planos progressivamente MAIS CURTOS; sequência
contemplativa pede planos longos com movimento interno lento (o zoom lento que
o Studio já aplica).

**Curva de ritmo por ato (PONTO DE PARTIDA):**

| Trecho | Duração média de plano | Por quê |
|---|---|---|
| Gancho (0–30s) | 3–5s | Precisa de movimento, mas sem confundir |
| Exposição/lore | 6–10s | Deixar a narração respirar; o texto carrega |
| Escalada | 4–6s, encurtando | O ritmo faz o trabalho da tensão |
| Clímax | 2–4s | Corte curto = adrenalina |
| Desfecho | 8–15s | Deixar o espectador assentar |

---

## 3. Continuidade: o que dá para consertar na edição

Nossos clipes variam em exposição, temperatura de cor e escala de personagem
entre gerações. Ordem de ataque, do mais eficaz ao menos:

1. **Correção de cor de igualação (color match)** — antes de qualquer estilo,
   puxar todos os clipes para uma mesma base de luminância/temperatura. É o
   que mais elimina a sensação de "colagem". Um "look do canal" aplicado por
   cima de todos os clipes (grade base) faz mais pela coesão do que qualquer
   transição.
2. **Cortar no movimento**, não na pausa — o olho perde a diferença de cor
   quando há movimento atravessando o corte.
3. **Insert de detalhe entre dois clipes que brigam** — um extreme close-up
   (mão, olho, chama, objeto) entre dois planos incompatíveis quebra a
   comparação direta. É a solução clássica de montagem para material que não
   casa; vale gerar clipes de insert de propósito para isso.
4. **Transição de textura** apenas se 1–3 não resolverem.

Regra dos 180°: mantê-la quando dá, mas ela é o item 5 da Regra dos Seis —
não vale sacrificar um clipe bom por causa dela.

---

## 4. Onde o corte deve cair

Três âncoras possíveis, em ordem de qualidade:

1. **Fim de bloco do roteiro** (melhor) — o corte cai onde a narração termina
   uma ideia. Exige saber o tempo real de cada bloco na narração; consegue-se
   por alinhamento forçado do roteiro contra o áudio.
2. **Pausa de respiração da narração** (o que o Studio faz hoje, imantando o
   corte no silêncio mais próximo) — bom, mas escolhe a pausa por proximidade
   de um ponto matemático, não por sentido.
3. **Divisão igual do tempo** (fallback) — nunca por escolha.

A única sincronia obrigatória do canal continua valendo: **o nome da criatura
dito pela primeira vez tem que coincidir com uma imagem forte dela** (ou da
sua iminência).

Sincronia narração↔imagem: quando a narração cita algo concreto, a imagem
correspondente deve aparecer em até ~0,5s da palavra. Fora esses momentos, a
narração é dissociada e não precisa bater em corte nenhum.

---

## 5. Checklist antes de renderizar

- [ ] Cada corte tem uma razão emocional ou narrativa (não é só "acabou o clipe")
- [ ] A transição de cada limite está motivada (ou é corte seco por padrão)
- [ ] Nenhum fade to black no meio de uma sequência
- [ ] A curva de ritmo acompanha o arco (não é uniforme do início ao fim)
- [ ] Todos os clipes passaram pela grade base do canal antes do filtro de cena
- [ ] O nome da criatura bate com a imagem dela
- [ ] Nenhum clipe repetido/em loop; congelamento só onde é inevitável
- [ ] O áudio final foi normalizado (ver `TRILHA-SONORA.md`)

---

## Fontes

- [The Rule of Six — Walter Murch's In the Blink of an Eye (StudioBinder)](https://www.studiobinder.com/blog/walter-murch-rule-of-six/)
- [Editing Secrets from Legendary Editor Walter Murch (Musicbed)](https://www.musicbed.com/articles/filmmaking/editing/editing-secrets-from-legendary-editor-walter-murch/)
- [Eye trace and the rule of six (Artlist)](https://artlist.io/blog/eye-trace-and-rule-of-six-editing/)
- [L cut and J cut in film (Adobe)](https://www.adobe.com/creativecloud/video/post-production/cuts-in-film/l-and-j-cut.html)
- [Cuts in film: types of cuts (Adobe)](https://www.adobe.com/creativecloud/video/post-production/cuts-in-film.html)
- [Video Transitions in Film Editing: A Full Guide (Backstage)](https://www.backstage.com/magazine/article/video-transitions-75727/)
- [The Difference Between Dissolves and Cuts (FILMPAC)](https://filmpac.com/the-difference-between-dissolves-and-cuts-in-video-edit/)
- [Video Clip Length: Ultimate Guide (VidPros)](https://vidpros.com/video-clip-length/)
- [Advanced retention editing (AIR Media-Tech)](https://air.io/en/youtube-hacks/advanced-retention-editing-cutting-patterns-that-keep-viewers-past-minute-8)
- [B-Roll Guide (Riverside)](https://riverside.com/blog/b-roll)
