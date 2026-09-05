# ~~Pendente~~ RESOLVIDO em 04/09/2026: Remotion travava ao renderizar clipes melhorados

> ✅ **RESOLVIDO.** A causa era o **decodificador**, não o timeout, não o
> bitrate, não o perfil do H.264. O `remotion/Clip.tsx` usava `<Video>` do
> `@remotion/media`, que decodifica por **WebCodecs** dentro do Chromium
> headless e **não dá conta do encode que o `enhance-clips.ts` produz**.
> Trocado pelo `<OffthreadVideo>` do `remotion` puro, que decodifica por
> **FFmpeg**.
>
> **Medido no mesmo dia, mesma máquina, mesmos clipes, só trocando o
> componente:**
>
> | clipes | `<Video>` (WebCodecs) | `<OffthreadVideo>` (FFmpeg) |
> |---|---|---|
> | **melhorados** (1882×1080, 60 fps, High L4.2, 19 MB) | 290 s a 0%, depois `Timeout while extracting frame at 0.13sec` | **60 s, done** |
> | **crus** (864×496, 24 fps, 5 MB) | 36 s | 40 s |
>
> Ou seja: o WebCodecs é ~11% mais rápido no material que ele consegue
> decodificar, e trava sem erro nenhum no que não consegue — o erro só
> aparece cinco minutos depois, quando o timeout de montagem estoura. Um
> caminho que sempre funciona vale mais que um mais rápido que trava calado.
>
> Áudio conferido no resultado (aac estéreo, mean_volume −17,8 dB) e quadro
> extraído e olhado: imagem íntegra em 1882×1080.
>
> **O que isto DESTRAVA:** o painel "1.5. Melhorar clipes" do Studio agora
> funciona de ponta a ponta, e a fase 4 do OMEGA pode passar a chamar o
> `enhance-clips` — mas **isso continua sendo decisão do Samuel, não minha**,
> porque a interpolação para 60 fps custa ~79 s por clipe de 15 s (~26 min de
> CPU num vídeo de 10 min) e o §C7 do `ESTUDO-STUDIO` registra que ainda não
> foi respondido se queremos 60 fps. O que mudou é que agora é uma ESCOLHA, e
> não um bug. O upscale sozinho (Lanczos, rápido) não tem essa dúvida.

---

## Registro original (19-21/08/2026)

**19-20/08/2026, durante o PLANO B (upscale + interpolação local no Studio).** Depois de melhorar
clipes de teste (480p → 1882×1080, 24fps → 60fps), o render final do Studio **trava** —
`@remotion/media` (o componente `<Video>` em `remotion/Clip.tsx`) não consegue extrair o primeiro
frame do clipe melhorado, e o job fica preso em progresso 0% até estourar o timeout.

**Reproduzido duas vezes, com timeouts diferentes (120s e depois 300s) — os dois deram exatamente
o mesmo erro, sem nenhum progresso no meio: "Timeout while extracting frame at time 0.1sec from
/public/videos/1.mp4".** Isso é sinal de trava mesmo, não de lentidão — se fosse só devagar,
esperaria progresso subindo aos poucos, ou sucesso com timeout maior.

## O que já foi testado e NÃO resolveu

1. **Levantar `MOUNT_TIMEOUT_MS`** (120s → 300s, em `lib/render/render-composition.ts`) — mesmo
   erro, só que estourando 180s depois. Confirma que não é questão de tempo.
2. **Remover B-frames do encode** (`-bf 0` no ffmpeg) — mesma hipótese de incompatibilidade de
   decodificação, testada re-encodando o clipe 1 isoladamente e rodando de novo — mesmo erro.

## O que NÃO foi testado ainda (próximos passos sugeridos)

- **Tamanho do arquivo isolado da resolução.** O clipe melhorado ficou em ~14,8 MB contra ~4 MB do
  original — nunca isolei se é o TAMANHO em si (não a resolução/fps) que trava a extração. Teste:
  um clipe 480p comprimido para o MESMO tamanho de arquivo (bitrate mais alto, mesma resolução) —
  se travar do mesmo jeito, é tamanho; se não, é resolução/fps.
- **Abrir o devtools do Chromium headless durante o render.** `@remotion/renderer` tem flags para
  isso (`chromiumOptions` já é usado em `render-composition.ts` para `gl: "angle"`; existe também
  a opção de log verboso/`dumpBrowserLogs`). Sem ver o console real do Chrome, estou testando às
  cegas — ver a mensagem de erro real do WebCodecs seria o atalho para a causa.
- **Testar SÓ upscale (sem interpolação) e SÓ interpolação (sem upscale) separadamente contra o
  render**, não os dois juntos — não isolei qual dos dois filtros (ou a combinação) é o gatilho.
- **Perfil/nível do H.264.** O clipe melhorado saiu com `profile=High, level=42` — o original
  (gerado pelo Kairogen) pode estar num perfil mais simples. Testar forçar
  `-profile:v baseline -level 3.0` no `postProcess` e ver se muda alguma coisa.
- **Verificar se é um problema conhecido do `@remotion/media`** (pacote relativamente novo, baseado
  em WebCodecs) — vale procurar issues abertas no GitHub do Remotion antes de continuar testando
  às cegas.

## Impacto prático, por enquanto

A Fase 4 do Omega (destravada em 21/08/2026, ver `voice/tools/pipeline.py:_run_edicao`) **não chama
`enhance-clips` por padrão** — renderiza os clipes brutos da fase 3 direto. Testado de verdade,
funciona bem (vídeo real de 45s, 1882×1080, áudio e vídeo alinhados com 32ms de diferença). A
melhoria de clipes (upscale para Full HD + interpolação 60fps) continua disponível como passo
manual opcional na interface do Studio (painel "1.5. Melhorar clipes"), mas não entra no fluxo
automático até este bug ser resolvido — senão a Fase 4 travaria silenciosamente sempre que alguém
pedisse a melhoria antes de montar.

---

## Atualização — 04/09/2026

**Uma contradição foi resolvida, o bug não.** O comentário de
`MOUNT_TIMEOUT_MS` em `studio/lib/render/render-composition.ts` afirmava que
subir 120s → 300s era *"the right fix"* — contra a evidência que já estava
escrita neste documento (300s dá o mesmo erro, só que 180s depois). O
comentário foi corrigido para registrar o que se sabe de fato; o valor
continua em 300s, porque folga de montagem é legítima, e nada mais.

**Duas coisas a mais, apuradas hoje:**

1. **Não existe "outro botão de timeout".** O `timeoutInMilliseconds` passado
   ao `selectComposition`/`renderMedia` **é** o timeout do `delayRender` que
   cobre a extração de frame. A última frase do comentário antigo ("rather
   than a renderMedia-specific knob") estava errada: não há knob separado.
   O que existe é a prop `delayRenderTimeoutInMilliseconds` por componente —
   mesmo relógio, escopo menor. Nenhum dos dois conserta travamento.

2. **A pista mais forte, e a mais barata de testar:** `remotion/Clip.tsx` usa
   `<Video>` do `@remotion/media`, que decodifica por **WebCodecs** dentro do
   Chromium headless. O `<OffthreadVideo>` do `remotion` puro decodifica por
   **FFmpeg**. Trocar um pelo outro no caminho do clipe melhorado tira o
   WebCodecs da jogada inteira e responde em UM render se o decodificador é o
   culpado — sem precisar entender o erro dele primeiro. É o teste que eu
   faria antes de qualquer um dos cinco da lista acima.
   📚 Fonte: documentação do Remotion sobre extração de frame lenta e sobre a
   diferença `<Video>` (WebCodecs) × `<OffthreadVideo>` (FFmpeg), lida em
   04/09/2026 — https://www.remotion.dev/docs/slow-method-to-extract-frame e
   https://www.remotion.dev/docs/media/support

**O que NÃO mudou:** a fase 4 automática continua renderizando os clipes
brutos da fase 3, sem melhoria. Isso segue certo até o teste acima acontecer.
