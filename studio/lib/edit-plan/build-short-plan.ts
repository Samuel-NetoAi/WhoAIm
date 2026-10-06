import type { EditPlan } from "./schema";
import { applyBoundaries } from "./apply-boundaries";
import { SHORT_RESOLUTION } from "./output-resolution";

export const DEFAULT_SHORT_TARGET_SECONDS = 30;

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

  // Same windowing as the pauses: a caption is a measured moment in the
  // narration, and the Short plays the narration trimmed to this window, so
  // each caption shifts into window-relative time. One that straddles either
  // edge is kept and clipped — cutting a subtitle's head or tail is better
  // than dropping a line that is half-spoken on screen.
  const captions = (fullPlan.captions ?? [])
    .map((caption) => ({
      ...caption,
      t0: caption.t0 - windowStartSeconds,
      t1: caption.t1 - windowStartSeconds,
    }))
    .filter((caption) => caption.t1 > 0 && caption.t0 < windowDurationSeconds)
    .map((caption) => ({
      ...caption,
      t0: Math.max(0, caption.t0),
      t1: Math.min(windowDurationSeconds, caption.t1),
    }));

  return applyBoundaries(
    includedClips.map((clip) => ({
      id: clip.id,
      file: clip.file,
      durationInSeconds: clip.naturalDurationInSeconds,
      audioMode: clip.audioMode,
      filter: clip.filter,
      // Centred crop today. This is the single number a reframing analyser
      // would fill in per scene to follow the subject instead — see
      // ESTUDO-STUDIO-melhorias §C3 for why that analyser must write a crop
      // track rather than re-encode the video.
      cropX: clip.cropX,
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
    // NOT fullPlan.width/height. The Short is a different FRAME, not just a
    // shorter one: 1080x1920, with the 16:9 footage cropped into it by
    // Clip.tsx's object-fit:cover + cropX. Inheriting the full plan's
    // dimensions is what made every Short so far a 16:9 video in a vertical
    // feed.
    SHORT_RESOLUTION.width,
    SHORT_RESOLUTION.height,
    {
      music,
      ducking: fullPlan.ducking,
      narrationPauses,
      captions,
      // The Short is the one cut that burns them in: it autoplays muted in
      // the feed, so an un-captioned Short is a silent Short. This is what
      // align/README.md meant by "para o Studio/Remotion queimar no Short".
      burnCaptions: captions.length > 0,
    },
  );
};
