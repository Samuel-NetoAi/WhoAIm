import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { z } from "zod";
import { captionSchema, type Caption } from "@/lib/edit-plan/schema";

// analysis/captions.json is written by Alpha/align, from the same forced
// alignment that produces the cut points — the text comes from the script,
// never from the ASR, so a transcription error can never become a subtitle
// error (see align/README.md, "Como funciona").
//
// This loader exists because that file was being written and never read: the
// align README declared it as "as mesmas legendas para o Studio/Remotion
// queimar no Short", and nothing in studio/ opened it. Meanwhile
// output-resolution.ts justified rendering at 1080p because it "gives crisp
// overlays for free, including captions" — overlays that did not exist.

const captionsFileSchema = z.object({
  version: z.literal(1),
  idioma: z.string().default("pt"),
  legendas: z.array(captionSchema),
});

export type CaptionsLoadResult = {
  captions: Caption[];
  problem: string | null;
};

// Never throws and never blocks analysis: subtitles are an optional input, so
// a missing or malformed file means "render without them", with a note the
// caller can surface — the same contract as loadAlignment and loadScenes.
export const loadCaptions = (projectPath: string): CaptionsLoadResult => {
  const file = path.join(projectPath, "analysis", "captions.json");
  if (!existsSync(file)) {
    return { captions: [], problem: null };
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(readFileSync(file, "utf8"));
  } catch {
    return { captions: [], problem: "captions.json não é um JSON válido" };
  }

  const result = captionsFileSchema.safeParse(parsed);
  if (!result.success) {
    return {
      captions: [],
      problem:
        "captions.json não tem o formato esperado — regere com Alpha/align",
    };
  }

  // Ascending by time, because the renderer picks the active caption by
  // scanning forward and a file written out of order would flicker.
  const captions = [...result.data.legendas].sort((a, b) => a.t0 - b.t0);
  return { captions, problem: null };
};
