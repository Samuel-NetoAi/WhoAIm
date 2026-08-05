import { z } from "zod";
import {
  filterPresetSchema,
  transitionPresetSchema,
  type FilterPreset,
  type TransitionPreset,
} from "../edit-plan/schema";

// scenes.json is the "orientação de cenas" file the `whoiam` skill writes next
// to the clips: what each scene IS, so filter, transition and music cue are
// pre-filled instead of decided by hand in the Studio. Its field names are in
// Portuguese because that is the contract documented in the skill
// (references/pos-producao.md §3-A) and the file is written by an LLM reading
// that document.
//
// It is validated forgivingly on purpose: the author is a language model, so a
// typo in one enum must degrade to the default rather than throw away the
// whole file. Unknown fields are ignored, not rejected.

export const EMOTIONS = [
  "misterio",
  "tragedia",
  "terror",
  "acao",
  "epico",
  "nordico-folk",
  "contemplativo",
  "folclore-br",
] as const;

export const sceneSchema = z.object({
  bloco: z.number().int().positive().optional(),
  clipe: z.string().optional(),
  intencao: z.string().optional(),
  emocao: z.enum(EMOTIONS).optional().catch(undefined),
  energia: z.number().min(0).max(5).optional().catch(undefined),
  // Track id from the music catalogue, or a cue type. Not rendered yet — the
  // music layer is not built — but validated and carried through so the
  // information is not lost between the skill and the Studio.
  cue: z.string().optional(),
  sfx: z.array(z.string()).optional().catch(undefined),
  transicao_da_anterior: transitionPresetSchema.catch("corte"),
  filtro: filterPresetSchema.catch("none"),
  nota: z.string().optional(),
});

export const scenesFileSchema = z.object({
  version: z.literal(1),
  criatura: z.string().optional(),
  cenas: z.array(sceneSchema).min(1),
});

export type Scene = z.infer<typeof sceneSchema>;
export type ScenesFile = z.infer<typeof scenesFileSchema>;

export type SceneDirection = {
  filter: FilterPreset;
  transitionFromPrevious: TransitionPreset;
};

export type DirectionMatch = {
  directions: (SceneDirection | null)[];
  matched: number;
  strategy: "arquivo" | "posição";
};

const toDirection = (scene: Scene): SceneDirection => ({
  filter: scene.filtro,
  transitionFromPrevious: scene.transicao_da_anterior,
});

// Compared by basename on both sides: the skill writes "7.mp4" while the probe
// reports "videos/7.mp4". Matching the raw strings silently matched nothing —
// the file loaded, validated, and did absolutely nothing.
const basename = (filePath: string): string =>
  filePath.split(/[\\/]/).pop() ?? filePath;

// Scenes are matched to clips by filename first, because clip numbering can
// have gaps (a scene whose clip was never generated). Falling back to position
// is only safe when the filenames matched nothing at all — a partial match
// means the numbering is meaningful and the gaps are real.
export const directionsForClips = (
  scenes: Scene[],
  clipFiles: string[],
): DirectionMatch => {
  const byFile = new Map<string, Scene>();
  for (const scene of scenes) {
    if (scene.clipe) byFile.set(basename(scene.clipe), scene);
  }

  const byName = clipFiles.map((file) => {
    const scene = byFile.get(basename(file));
    return scene ? toDirection(scene) : null;
  });
  const matched = byName.filter(Boolean).length;

  if (matched > 0) {
    return { directions: byName, matched, strategy: "arquivo" };
  }

  const byPosition = clipFiles.map((_, index) =>
    scenes[index] ? toDirection(scenes[index]) : null,
  );
  return {
    directions: byPosition,
    matched: byPosition.filter(Boolean).length,
    strategy: "posição",
  };
};
