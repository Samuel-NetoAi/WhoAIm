#!/usr/bin/env node
/**
 * Cria e mantém a biblioteca de trilha do canal.
 *
 *   node scripts/trilhas.mjs              cria as pastas e sincroniza o catálogo
 *   node scripts/trilhas.mjs --verificar  só relata, não escreve nada
 *   node scripts/trilhas.mjs --raiz D:\Ai-Project
 *
 * O catálogo é GERADO a partir das pastas, não escrito à mão: você joga o mp3
 * na seção certa e roda. A duração é medida do arquivo — se ela estivesse
 * errada, o Studio repetiria (ou cortaria) a faixa na hora errada, e esse é o
 * tipo de erro que só aparece no vídeo pronto.
 *
 * O que é seu para preencher: `fonte`, `licenca`, `intensidade`, `tags`. O
 * script nunca sobrescreve esses campos numa faixa que já existe.
 */

import { existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { ALL_FORMATS, FilePathSource, Input } from "mediabunny";

// Seções por FUNÇÃO EMOCIONAL, não por gênero — é assim que se acha o cue certo
// em dez segundos no meio da edição. Ver Alpha/docs/TRILHA-SONORA.md.
const SECOES = [
  ["01-misterio", "drones graves, cordas sustentadas, piano esparso, pulso lento"],
  ["02-tragedia", "violoncelo solo, piano menor, cordas lentas, melancolia contida"],
  ["03-terror", "sub-bass, clusters dissonantes de metais, crescendo glacial"],
  ["04-acao", "ostinato de cordas, percussão acelerada, sforzandos nos impactos"],
  ["05-epico", "metais nobres, cordas amplas, percussão orquestral"],
  ["06-nordico-folk", "taiko/bombo, trompas, cordas friccionadas, instrumentos étnicos"],
  ["07-contemplativo", "pads amplos, harpa/piano, dinâmica baixa"],
  ["08-folclore-br", "viola/violão atmosférico, percussão orgânica, texturas de mata"],
  ["09-stingers", "acentos curtos, hits, risers, impactos"],
  ["10-drones", "texturas puras sem pulso, para ficar sob qualquer cena"],
];

const EXTENSOES = new Set([".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac"]);

const argumento = (nome) => {
  const i = process.argv.indexOf(nome);
  return i >= 0 ? process.argv[i + 1] : undefined;
};

const RAIZ = argumento("--raiz") ?? process.env.AI_PROJECT_ROOT ?? "C:\\Ai-Project";
const TRILHAS = path.join(RAIZ, "Trilhas");
const CATALOGO = path.join(TRILHAS, "catalogo.json");
const SOMENTE_LER = process.argv.includes("--verificar");

const slug = (valor) =>
  valor
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "");

// "01-misterio" -> "misterio", para o id não carregar o número da pasta (que
// existe só para ordenar no explorador de arquivos).
const nomeDaSecao = (pasta) => pasta.replace(/^\d+-/, "");

const duracaoDe = async (arquivo) => {
  const input = new Input({ formats: ALL_FORMATS, source: new FilePathSource(arquivo) });
  return Math.round((await input.computeDuration()) * 10) / 10;
};

const lerCatalogo = () => {
  if (!existsSync(CATALOGO)) return [];
  try {
    const conteudo = JSON.parse(readFileSync(CATALOGO, "utf8"));
    return Array.isArray(conteudo) ? conteudo : conteudo.faixas ?? [];
  } catch {
    console.error(`! ${CATALOGO} não é um JSON válido — corrija antes de sincronizar.`);
    process.exit(1);
  }
};

const LEIA_ME = `# Trilhas — biblioteca de música do canal

Organizada por FUNÇÃO EMOCIONAL, não por gênero: na edição você procura
"o que essa cena precisa sentir", não "que estilo é esse".

Reutilizar as mesmas faixas entre vídeos é DE PROPÓSITO — é o que faz o
espectador reconhecer o tema de "revelação do monstro". Não é preguiça.

## Como adicionar uma faixa

1. Baixe o arquivo e coloque na pasta da emoção correspondente.
2. Rode: \`node scripts/trilhas.mjs\` (da pasta Alpha\\studio)
3. Abra o \`catalogo.json\` e preencha **fonte** e **licenca** da faixa nova.
4. No \`scenes.json\` do projeto, use o \`id\` da faixa no campo \`cue\`.

O script mede a duração sozinho e nunca sobrescreve o que você preencheu.

> **Não renomeie um arquivo depois de usá-lo.** O \`id\` é derivado do nome do
> arquivo na primeira vez que a faixa entra no catálogo — e é esse \`id\` que os
> \`scenes.json\` dos projetos guardam no campo \`cue\`. Renomear gera um id novo
> e os projetos antigos ficam sem música. O Studio avisa ("cue sem faixa no
> catálogo"), mas o conserto é manual. Para mudar o nome de exibição, edite o
> \`id\` no catálogo à mão — o script preserva o que já existe.

## De onde tirar música — veredito por fonte

| Fonte | Risco de reivindicação | Veredito |
|---|---|---|
| **YouTube Audio Library** | **nenhum** — o próprio YouTube garante que não há Content ID | **Base da biblioteca** |
| Pixabay Music | baixo, mas há relatos de reivindicação para contestar na mão | Complemento |
| Uppbeat | baixo (versão grátis exige crédito) | Complemento |
| Free Music Archive | **alto** — licença faixa a faixa, e a FMA não detém os direitos | Evitar para uso comercial |
| Artlist / Epidemic | baixo (pago) | Quando houver verba |
| ElevenLabs Music | baixo — direitos comerciais completos | Momentos-assinatura |
| **Música do CapCut** | **PROIBIDA** | Licença cobre CapCut/TikTok, NÃO o YouTube: o Content ID do detentor fica com a receita do vídeo |

Preencha o campo \`licenca\` sempre. Quando vier uma reivindicação, a defesa
precisa estar a um clique — não na sua memória.

## Regra de duração

Gere/baixe a música **maior** que a sequência que ela vai cobrir, e deixe o
Studio cortar. Faixa mais curta que o trecho é repetida em loop, e loop de
trilha se ouve.
`;

const main = async () => {
  if (!existsSync(TRILHAS) && SOMENTE_LER) {
    console.log(`Nada para verificar: ${TRILHAS} não existe.`);
    return;
  }

  if (!SOMENTE_LER) {
    for (const [pasta] of SECOES) {
      mkdirSync(path.join(TRILHAS, pasta), { recursive: true });
    }
    const leiaMe = path.join(TRILHAS, "LEIA-ME.md");
    if (!existsSync(leiaMe)) writeFileSync(leiaMe, LEIA_ME, "utf8");
  }

  const existentes = new Map(lerCatalogo().map((faixa) => [faixa.arquivo, faixa]));
  const faixas = [];
  const novas = [];
  const semLicenca = [];

  for (const [pasta] of SECOES) {
    const dir = path.join(TRILHAS, pasta);
    if (!existsSync(dir)) continue;

    const arquivos = readdirSync(dir)
      .filter((f) => EXTENSOES.has(path.extname(f).toLowerCase()))
      .sort();

    for (const arquivo of arquivos) {
      const relativo = `${pasta}/${arquivo}`;
      const anterior = existentes.get(relativo);
      const base = path.parse(arquivo).name;

      let duracao;
      try {
        duracao = await duracaoDe(path.join(dir, arquivo));
      } catch {
        console.error(`! não consegui ler a duração de ${relativo} — arquivo corrompido?`);
        continue;
      }

      // Campos editoriais são seus; os medidos são do script.
      const faixa = {
        id: anterior?.id ?? `${nomeDaSecao(pasta)}-${slug(base)}`,
        arquivo: relativo,
        secao: nomeDaSecao(pasta),
        duracao,
        bpm: anterior?.bpm,
        loopavel: anterior?.loopavel ?? false,
        intensidade: anterior?.intensidade,
        // Sem palpite: preencher com o texto genérico da seção criaria dado
        // que PARECE informação e está errado para a faixa específica.
        instrumentacao: anterior?.instrumentacao,
        tags: anterior?.tags ?? [],
        fonte: anterior?.fonte ?? "",
        licenca: anterior?.licenca ?? "",
      };
      for (const chave of Object.keys(faixa)) {
        if (faixa[chave] === undefined) delete faixa[chave];
      }

      faixas.push(faixa);
      if (!anterior) novas.push(faixa);
      if (!faixa.licenca) semLicenca.push(faixa.id);
      existentes.delete(relativo);
    }
  }

  const orfas = Array.from(existentes.values());

  console.log(`Biblioteca: ${TRILHAS}`);
  console.log(`  ${faixas.length} faixa(s) em ${SECOES.length} seções`);
  if (novas.length) console.log(`  ${novas.length} nova(s): ${novas.map((f) => f.id).join(", ")}`);
  if (orfas.length) {
    console.log(`  ${orfas.length} no catálogo sem arquivo (removida(s)): ${orfas.map((f) => f.id).join(", ")}`);
  }
  if (semLicenca.length) {
    console.log(`  ⚠ sem licença registrada: ${semLicenca.join(", ")}`);
    console.log(`    Preencha "fonte" e "licenca" — é a defesa contra reivindicação.`);
  }

  if (SOMENTE_LER) {
    console.log("\n(--verificar: nada foi escrito)");
    return;
  }

  writeFileSync(
    CATALOGO,
    JSON.stringify({ version: 1, faixas }, null, 2) + "\n",
    "utf8",
  );
  console.log(`\nGravado ${CATALOGO}`);
  if (faixas.length === 0) {
    console.log("Coloque os arquivos nas pastas por emoção e rode de novo.");
  }
};

main().catch((erro) => {
  console.error(erro);
  process.exit(1);
});
