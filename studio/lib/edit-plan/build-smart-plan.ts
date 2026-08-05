import type { ProjectProbe } from "../media/probe-project";
import type { Silence } from "../media/detect-silences";
import type { EditPlan } from "./schema";
import { DEFAULT_FPS, DEFAULT_TRANSITION_FRAMES } from "./build-naive-plan";
import { applyBoundaries } from "./apply-boundaries";
import { resolveOutputResolution, type Resolution } from "./output-resolution";
import { toBoundaryClips, type ClipDirections } from "./clip-directions";

// How far (in seconds) from an equal-split point we'll look for a nearby
// pause to snap to. Wide enough to usually find one of the frequent
// mid-sentence breaths in narration audio, narrow enough that a snap never
// drags a cut point into a neighboring scene's "territory".
const SNAP_SEARCH_WINDOW_SECONDS = 3;

// Never let a snap (or its absence) leave a clip with less than this much
// screen time — guards against two nearby silences collapsing a slot.
const MIN_SLOT_SECONDS = 3;

const findNearestSilenceMidpoint = (
  silences: Silence[],
  target: number,
  maxDistance: number,
): number | null => {
  let best: number | null = null;
  let bestDistance = Infinity;
  for (const silence of silences) {
    const midpoint = (silence.start + silence.end) / 2;
    const distance = Math.abs(midpoint - target);
    if (distance <= maxDistance && distance < bestDistance) {
      bestDistance = distance;
      best = midpoint;
    }
  }
  return best;
};

// Same overall shape as buildNaivePlan (equal split, inflated for transition
// overlap), except each internal cut point is snapped to the nearest silence
// in the narration when one is close enough — so cuts land in natural pauses
// instead of mid-word, without needing a transcript (the source clips have
// no dialogue/text to align against, only b-roll + narration).
export const buildSmartPlan = (
  probe: ProjectProbe,
  silences: Silence[],
  fps: number = DEFAULT_FPS,
  transitionFrames: number = DEFAULT_TRANSITION_FRAMES,
  resolutionOverride?: Partial<Resolution>,
  directions?: ClipDirections,
): EditPlan => {
  const { clips, narration } = probe;
  const numClips = clips.length;
  const totalSeconds = narration.durationInSeconds;

  const naiveBoundarySeconds = Array.from(
    { length: numClips - 1 },
    (_, i) => (totalSeconds * (i + 1)) / numClips,
  );

  const snappedBoundarySeconds = naiveBoundarySeconds.map((target) => {
    const snapped = findNearestSilenceMidpoint(
      silences,
      target,
      SNAP_SEARCH_WINDOW_SECONDS,
    );
    return snapped ?? target;
  });

  // Reject a snap if it collapses the slot before or after it below the
  // minimum, falling back to the naive equal-split point for that boundary.
  for (let i = 0; i < snappedBoundarySeconds.length; i++) {
    const prev = i === 0 ? 0 : snappedBoundarySeconds[i - 1];
    const next =
      i === snappedBoundarySeconds.length - 1
        ? totalSeconds
        : snappedBoundarySeconds[i + 1];
    const tooCloseToPrev = snappedBoundarySeconds[i] - prev < MIN_SLOT_SECONDS;
    const tooCloseToNext = next - snappedBoundarySeconds[i] < MIN_SLOT_SECONDS;
    if (tooCloseToPrev || tooCloseToNext) {
      snappedBoundarySeconds[i] = naiveBoundarySeconds[i];
    }
  }

  const { width, height } = resolveOutputResolution(clips, resolutionOverride);

  return applyBoundaries(
    toBoundaryClips(clips, directions),
    { file: narration.file, durationInSeconds: totalSeconds },
    snappedBoundarySeconds,
    fps,
    transitionFrames,
    width,
    height,
  );
};
