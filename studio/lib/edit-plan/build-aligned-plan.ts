import type { ProjectProbe } from "../media/probe-project";
import type { EditPlan } from "./schema";
import { applyBoundaries } from "./apply-boundaries";
import { DEFAULT_FPS, DEFAULT_TRANSITION_FRAMES } from "./build-naive-plan";
import { resolveOutputResolution, type Resolution } from "./output-resolution";
import { toBoundaryClips, type ClipDirections } from "./clip-directions";

// The best of the three strategies: the cut points were MEASURED against the
// narration (Alpha/align aligns the script to the audio), so each clip changes
// exactly where its block of narration ends — not at an equal-split point that
// happened to land near a pause.
export const buildAlignedPlan = (
  probe: ProjectProbe,
  internalBoundarySeconds: number[],
  fps: number = DEFAULT_FPS,
  transitionFrames: number = DEFAULT_TRANSITION_FRAMES,
  resolutionOverride?: Partial<Resolution>,
  directions?: ClipDirections,
): EditPlan => {
  const { clips, narration } = probe;
  const { width, height } = resolveOutputResolution(clips, resolutionOverride);

  return applyBoundaries(
    toBoundaryClips(clips, directions),
    { file: narration.file, durationInSeconds: narration.durationInSeconds },
    internalBoundarySeconds,
    fps,
    transitionFrames,
    width,
    height,
  );
};
