import type { EditPlan } from "./schema";
import { applyBoundaries } from "./apply-boundaries";

export const DEFAULT_SHORT_TARGET_SECONDS = 30;

// Builds a short cut from the front of the full edit: takes as many whole
// scenes as fit closest to the target length, ending exactly on one of the
// full plan's existing cut points (already silence-snapped) rather than
// introducing a new mid-sentence cut. The narration audio is simply the same
// file truncated to that point — Remotion stops rendering it there, no
// re-encoding needed.
export const buildShortPlan = (
  fullPlan: EditPlan,
  targetSeconds: number = DEFAULT_SHORT_TARGET_SECONDS,
): EditPlan => {
  const allBoundaries =
    fullPlan.cutPoints ??
    [
      0,
      ...fullPlan.clips.map((c) => c.startInNarrationSeconds).slice(1),
      fullPlan.narration.durationInSeconds,
    ];

  const interiorAndEnd = allBoundaries.filter((b) => b > 0);
  if (interiorAndEnd.length === 0) {
    throw new Error("Not enough scenes to build a short cut");
  }

  const cutoff = interiorAndEnd.reduce((best, candidate) =>
    Math.abs(candidate - targetSeconds) < Math.abs(best - targetSeconds)
      ? candidate
      : best,
  );

  const includedClips = fullPlan.clips.filter(
    (clip) => clip.startInNarrationSeconds < cutoff,
  );
  const internalBoundarySeconds = includedClips
    .slice(1)
    .map((clip) => clip.startInNarrationSeconds);

  return applyBoundaries(
    includedClips.map((clip) => ({
      id: clip.id,
      file: clip.file,
      durationInSeconds: clip.naturalDurationInSeconds,
      audioMode: clip.audioMode,
      filter: clip.filter,
    })),
    { file: fullPlan.narration.file, durationInSeconds: cutoff },
    internalBoundarySeconds,
    fullPlan.fps,
    fullPlan.transitionFrames,
    fullPlan.width,
    fullPlan.height,
  );
};
