import { DEV_NULL, runRemotionFfmpeg } from "./run-ffmpeg";

// Remotion bundles a stripped-down ffmpeg (see postprocess.ts) that does NOT
// include `volumedetect` — confirmed by running it directly ("No such
// filter: 'volumedetect'"). `loudnorm` IS in that build (detect-silences.ts
// already relies on it for its own single-pass measurement), so integrated
// loudness (EBU R128, LUFS) from loudnorm's JSON report is used instead —
// arguably a better "how loud is this" number than a plain mean anyway.
const SILENT_FLOOR_LUFS = -70;

const parseIntegratedLoudness = (output: string): number => {
  const match = output.match(/\{[\s\S]*?"input_i"[\s\S]*?\}/);
  if (!match) return SILENT_FLOOR_LUFS;
  try {
    const parsed = JSON.parse(match[0]) as { input_i: string };
    const value = parseFloat(parsed.input_i);
    // input_i is the literal string "-inf" for a track that never produced
    // sound at all.
    return Number.isFinite(value) ? value : SILENT_FLOOR_LUFS;
  } catch {
    return SILENT_FLOOR_LUFS;
  }
};

// Integrated loudness (LUFS) of a clip's OWN audio track — a cheap, content-
// agnostic stand-in for "how eventful is this moment" when a Short has to
// pick which stretch of footage to feature. A shouted fight or a musical
// sting reads louder than a quiet establishing shot, even on projects where
// the clip's own audio never plays in the final mix (see build-short-plan.ts,
// which is the only reader of this score).
//
// Never throws: one clip's probe failing must not abort analysis of the
// whole project, matching how the analyze route already treats every other
// optional signal (scenes.json, alignment, silence detection).
export const measureClipLoudness = async (
  absolutePath: string,
): Promise<number> => {
  try {
    const output = await runRemotionFfmpeg([
      "-i",
      absolutePath,
      "-map",
      "0:a?",
      "-af",
      "loudnorm=print_format=json",
      "-f",
      "null",
      DEV_NULL,
    ]);
    return parseIntegratedLoudness(output);
  } catch {
    return SILENT_FLOOR_LUFS;
  }
};
