import type { ProjectProbe } from "../media/probe-project";
import type { EditPlan } from "./schema";
import { applyBoundaries } from "./apply-boundaries";
import { resolveOutputResolution, type Resolution } from "./output-resolution";
import { toBoundaryClips, type ClipDirections } from "./clip-directions";

export const DEFAULT_FPS = 30;
export const DEFAULT_TRANSITION_FRAMES = 20;

// Divides the narration into N equal slots (N = number of available clips).
// Last-resort fallback: used only when neither the alignment (measured block
// timings) nor silence detection is available. Delegates the slot/transition
// arithmetic to applyBoundaries so all three strategies share one implementation
// — per-boundary transitions must be honoured here too.
export const buildNaivePlan = (
  probe: ProjectProbe,
  fps: number = DEFAULT_FPS,
  transitionFrames: number = DEFAULT_TRANSITION_FRAMES,
  resolutionOverride?: Partial<Resolution>,
  directions?: ClipDirections,
): EditPlan => {
  const { clips, narration } = probe;
  const totalSeconds = narration.durationInSeconds;

  const equalBoundaries = Array.from(
    { length: clips.length - 1 },
    (_, i) => (totalSeconds * (i + 1)) / clips.length,
  );

  const { width, height } = resolveOutputResolution(clips, resolutionOverride);

  return applyBoundaries(
    toBoundaryClips(clips, directions),
    { file: narration.file, durationInSeconds: totalSeconds },
    equalBoundaries,
    fps,
    transitionFrames,
    width,
    height,
  );
};
