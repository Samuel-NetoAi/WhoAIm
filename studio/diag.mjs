// ../../../../../tmp/claude-1000/-home-sami-Downloads-Alpha/8e6a9949-5c30-420d-a587-fc0cd7912689/scratchpad/diag.mts
import { readFileSync, mkdirSync } from "node:fs";
import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";
var P = "/tmp/claude-1000/-home-sami-Downloads-Alpha/8e6a9949-5c30-420d-a587-fc0cd7912689/scratchpad/proj/Criaturas/Teste/teste-video";
var base = JSON.parse(readFileSync(`${P}/edit-plan.json`, "utf8"));
mkdirSync(`${P}/renders`, { recursive: true });
var serveUrl = await bundle({
  entryPoint: "/home/sami/Downloads/Alpha/studio/remotion/index.ts",
  publicDir: `${P}/public`
});
console.log("bundle ok");
var preset = process.argv[2];
var editPlan = structuredClone(base);
for (const c of editPlan.clips) c.transitionFromPrevious = preset;
var t0 = Date.now();
try {
  const composition = await selectComposition({
    serveUrl,
    id: "EditedVideo",
    inputProps: { editPlan },
    timeoutInMilliseconds: 12e4
  });
  await renderMedia({
    composition,
    serveUrl,
    codec: "h264",
    outputLocation: `${P}/renders/${preset}.mp4`,
    inputProps: { editPlan },
    timeoutInMilliseconds: 12e4,
    onProgress: () => {
    }
  });
  console.log(`${preset}: OK em ${((Date.now() - t0) / 1e3).toFixed(1)}s`);
} catch (e) {
  console.log(`${preset}: FALHOU em ${((Date.now() - t0) / 1e3).toFixed(1)}s \u2014 ${String(e).split("\n")[0].slice(0, 160)}`);
}
