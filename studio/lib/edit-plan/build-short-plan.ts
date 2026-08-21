import type { EditPlan } from "./schema";
import { applyBoundaries } from "./apply-boundaries";

export const DEFAULT_SHORT_TARGET_SECONDS = 30;

// Vertical is the platform standard for a "Short" (YouTube Shorts, TikTok,
// Reels) regardless of the source footage's own aspect. Clip.tsx already
// renders with objectFit="cover", so pointing the composition at this frame
// is enough: the usually-16:9 footage gets center-cropped to fill it, no
// distortion, no letterboxing — the same "decouple output from source"
// approach output-resolution.ts already uses for the full render.
const SHORT_WIDTH = 1080;
const SHORT_HEIGHT = 1920;

// How far a candidate window's duration may drift from the target and still
// be considered — as a fraction of the target. Wide enough that, on a
// project cut into ~30s clips with a 30s target, every single-clip window
// qualifies (so energy actually gets to pick among them); narrow enough that
// a much longer or shorter stretch can't out-score a well-sized one just for
// being louder.
const DURATION_TOLERANCE_FRACTION = 0.4;

type Candidate = {
  startIdx: number;
  endIdx: number;
  durationSeconds: number;
  avgEnergy: number;
};

// Builds a short cut by searching every contiguous window of clips (not just
// the front of the edit) for the one that best matches the target length AND
// is, on average, the LOUDEST — a cheap, content-agnostic stand-in for "the
// best moment" that needs no manual scene tagging (see measure-loudness.ts /
// probe-project.ts for where energyScore comes from). Falls back to the
// closest-length window overall when nothing clears the loudness bar, so a
// short always renders even for legacy plans with no energy signal — and, in
// that case, ties resolve to the earliest window, i.e. the old front-of-edit
// behavior.
//
// The window always starts and ends on one of the full plan's existing cut
// points (already silence-snapped for the narration), never a new mid-
// sentence cut.
export const buildShortPlan = (
  fullPlan: EditPlan,
  targetSeconds: number = DEFAULT_SHORT_TARGET_SECONDS,
): EditPlan => {
  const numClips = fullPlan.clips.length;
  const boundaries =
    fullPlan.cutPoints ??
    [
      0,
      ...fullPlan.clips.map((c) => c.startInNarrationSeconds).slice(1),
      fullPlan.narration.durationInSeconds,
    ];

  if (numClips === 0 || boundaries.length !== numClips + 1) {
    throw new Error("Not enough scenes to build a short cut");
  }

  // Prefix sums turn a window's average energy into an O(1) lookup instead
  // of re-summing its clips for every candidate below.
  const energyPrefix = [0];
  for (const clip of fullPlan.clips) {
    energyPrefix.push(
      energyPrefix[energyPrefix.length - 1] + (clip.energyScore ?? 0),
    );
  }

  const tolerance = targetSeconds * DURATION_TOLERANCE_FRACTION;
  let bestOverall: Candidate | null = null;
  let bestInTolerance: Candidate | null = null;

  for (let startIdx = 0; startIdx < numClips; startIdx++) {
    for (let endIdx = startIdx + 1; endIdx <= numClips; endIdx++) {
      const durationSeconds = boundaries[endIdx] - boundaries[startIdx];
      const avgEnergy =
        (energyPrefix[endIdx] - energyPrefix[startIdx]) / (endIdx - startIdx);
      const distance = Math.abs(durationSeconds - targetSeconds);

      if (
        !bestOverall ||
        distance < Math.abs(bestOverall.durationSeconds - targetSeconds)
      ) {
        bestOverall = { startIdx, endIdx, durationSeconds, avgEnergy };
      }

      if (distance > tolerance) continue;

      if (
        !bestInTolerance ||
        avgEnergy > bestInTolerance.avgEnergy ||
        (avgEnergy === bestInTolerance.avgEnergy &&
          distance < Math.abs(bestInTolerance.durationSeconds - targetSeconds))
      ) {
        bestInTolerance = { startIdx, endIdx, durationSeconds, avgEnergy };
      }
    }
  }

  const chosen = bestInTolerance ?? bestOverall;
  if (!chosen) {
    throw new Error("Not enough scenes to build a short cut");
  }

  const { startIdx, endIdx } = chosen;
  const windowStartSeconds = boundaries[startIdx];
  const windowEndSeconds = boundaries[endIdx];
  const lastKeptIdx = endIdx - 1;

  const includedClips = fullPlan.clips.slice(startIdx, endIdx);
  const internalBoundarySeconds = includedClips
    .slice(1)
    .map((clip) => clip.startInNarrationSeconds - windowStartSeconds);

  // A cue/pause carries over when it overlaps the kept window, remapped from
  // absolute clip/time indices to window-relative ones — applyBoundaries (and
  // the ducking curve in MusicTrack.tsx) only understand time relative to
  // THIS render's own timeline, which now may start mid-episode.
  const music = (fullPlan.music ?? [])
    .filter((cue) => cue.scenes.some((s) => s >= startIdx && s <= lastKeptIdx))
    .map((cue) => ({
      ...cue,
      scenes: cue.scenes
        .filter((s) => s >= startIdx && s <= lastKeptIdx)
        .map((s) => s - startIdx),
    }));

  const windowDurationSeconds = windowEndSeconds - windowStartSeconds;
  const narrationPauses = (fullPlan.narrationPauses ?? [])
    .map((pause) => ({
      start: pause.start - windowStartSeconds,
      end: pause.end - windowStartSeconds,
    }))
    .filter((pause) => pause.end > 0 && pause.start < windowDurationSeconds)
    .map((pause) => ({
      start: Math.max(0, pause.start),
      end: Math.min(windowDurationSeconds, pause.end),
    }));

  return applyBoundaries(
    includedClips.map((clip) => ({
      id: clip.id,
      file: clip.file,
      durationInSeconds: clip.naturalDurationInSeconds,
      audioMode: clip.audioMode,
      filter: clip.filter,
      energyScore: clip.energyScore,
    })),
    {
      file: fullPlan.narration.file,
      durationInSeconds: windowDurationSeconds,
      startInSeconds: windowStartSeconds,
    },
    internalBoundarySeconds,
    fullPlan.fps,
    fullPlan.transitionFrames,
    SHORT_WIDTH,
    SHORT_HEIGHT,
    {
      music,
      ducking: fullPlan.ducking,
      narrationPauses,
    },
  );
};
