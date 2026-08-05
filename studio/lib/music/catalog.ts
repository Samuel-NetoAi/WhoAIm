import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { z } from "zod";
import { AI_PROJECT_ROOT } from "../projects/constants";

// The music library lives OUTSIDE the projects, at <root>/Trilhas, organised by
// emotional function rather than genre — that is how a cue gets found in ten
// seconds while editing. Reusing the same tracks across videos is deliberate:
// it is what gives the channel a recognisable sound.
// Full rationale in Alpha/docs/TRILHA-SONORA.md.

export const MUSIC_ROOT = path.join(AI_PROJECT_ROOT, "Trilhas");
export const CATALOG_FILE = path.join(MUSIC_ROOT, "catalogo.json");

const trackSchema = z.object({
  id: z.string(),
  // Relative to the Trilhas folder, e.g. "01-misterio/veil-of-dust.mp3".
  arquivo: z.string(),
  secao: z.string().optional(),
  duracao: z.number().positive(),
  bpm: z.number().positive().optional(),
  loopavel: z.boolean().default(false),
  intensidade: z.number().min(0).max(5).optional(),
  instrumentacao: z.array(z.string()).optional().catch(undefined),
  tags: z.array(z.string()).optional().catch(undefined),
  fonte: z.string().optional(),
  // Kept because a Content ID claim has to be answerable in one click.
  licenca: z.string().optional(),
});

// Accepts either { version, faixas: [...] } or a bare array, because the
// catalogue is maintained by hand and both shapes are the obvious guess.
const catalogSchema = z.union([
  z.object({ version: z.literal(1).optional(), faixas: z.array(trackSchema) }),
  z.array(trackSchema),
]);

export type Track = z.infer<typeof trackSchema>;

export type CatalogLoadResult = {
  tracks: Map<string, Track>;
  problem: string | null;
};

const EMPTY = new Map<string, Track>();

export const loadCatalog = (): CatalogLoadResult => {
  if (!existsSync(CATALOG_FILE)) {
    return { tracks: EMPTY, problem: null };
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(readFileSync(CATALOG_FILE, "utf8"));
  } catch {
    return { tracks: EMPTY, problem: "catalogo.json não é um JSON válido" };
  }

  const result = catalogSchema.safeParse(parsed);
  if (!result.success) {
    const first = result.error.issues[0];
    return {
      tracks: EMPTY,
      problem: `catalogo.json inválido em "${first.path.join(".")}": ${first.message}`,
    };
  }

  const list = Array.isArray(result.data) ? result.data : result.data.faixas;
  return { tracks: new Map(list.map((track) => [track.id, track])), problem: null };
};

export const trackAbsolutePath = (track: Track): string =>
  path.join(MUSIC_ROOT, track.arquivo);
