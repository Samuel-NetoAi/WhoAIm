import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { z } from "zod";

// analysis/alignment.json is written by Alpha/align — it measures where each
// script block actually falls in the narration, instead of the Studio guessing
// with an equal split snapped to the nearest pause. See align/README.md.

const blockSchema = z.object({
  indice: z.number().int().nonnegative(),
  texto: z.string(),
  t0: z.number().nonnegative(),
  t1: z.number().nonnegative(),
  confianca: z.number().min(0).max(1),
  rotulo: z.string().default(""),
  // How many production blocks (and therefore clips) this group of lines
  // covers: a "[Blocos 2-3]" heading is one group for two 15s clips.
  abrange: z.number().int().positive().default(1),
});

export const alignmentSchema = z.object({
  version: z.literal(1),
  duracaoAudio: z.number().positive(),
  confianca: z.number().min(0).max(1),
  blocos: z.array(blockSchema).min(1),
});

export type Alignment = z.infer<typeof alignmentSchema>;

export type AlignmentLoadResult = {
  alignment: Alignment | null;
  problem: string | null;
};

export const loadAlignment = (projectPath: string): AlignmentLoadResult => {
  const file = path.join(projectPath, "analysis", "alignment.json");
  if (!existsSync(file)) {
    return { alignment: null, problem: null };
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(readFileSync(file, "utf8"));
  } catch {
    return { alignment: null, problem: "alignment.json não é um JSON válido" };
  }

  const result = alignmentSchema.safeParse(parsed);
  if (!result.success) {
    return {
      alignment: null,
      problem: "alignment.json não tem o formato esperado — regere com Alpha/align",
    };
  }

  return { alignment: result.data, problem: null };
};

// A heading that covers several blocks is one measured span for several clips.
// Splitting it evenly is an approximation, but a far better one than ignoring
// the measurement entirely: the span itself was measured, only its internal
// division is estimated.
const expandGroups = (alignment: Alignment): number[] => {
  const ends: number[] = [];
  for (const block of alignment.blocos) {
    const step = (block.t1 - block.t0) / block.abrange;
    for (let i = 1; i <= block.abrange; i++) {
      ends.push(block.t0 + step * i);
    }
  }
  return ends;
};

export type BoundaryResult = {
  internalBoundarySeconds: number[] | null;
  problem: string | null;
};

// Returns the cut points between clips, or explains why the alignment could
// not be used. Never throws: a mismatch falls back to silence-snapping.
export const boundariesForClips = (
  alignment: Alignment,
  clipCount: number,
): BoundaryResult => {
  const ends = expandGroups(alignment);

  if (ends.length !== clipCount) {
    return {
      internalBoundarySeconds: null,
      problem:
        `o roteiro alinhado tem ${ends.length} bloco(s) e o projeto tem ` +
        `${clipCount} clipe(s) — gere um clipe por bloco, ou ajuste o roteiro`,
    };
  }

  // The last block's end is the end of the narration, not a cut between clips.
  return { internalBoundarySeconds: ends.slice(0, -1), problem: null };
};
