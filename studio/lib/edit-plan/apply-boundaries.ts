import {
  DEFAULT_DUCKING,
  isHardCut,
  type AudioMode,
  type Ducking,
  type EditPlan,
  type FilterPreset,
  type MusicCue,
  type TransitionPreset,
} from "./schema";

export type BoundaryClip = {
  id: string;
  file: string;
  durationInSeconds: number;
  audioMode?: AudioMode;
  filter?: FilterPreset;
  transitionFromPrevious?: TransitionPreset;
  transitionFrames?: number;
  energyScore?: number;
};

export type BoundaryNarration = {
  file: string;
  durationInSeconds: number;
  startInSeconds?: number;
};

// Everything the plan carries that is not derived from the boundaries. It has
// to travel through, because applyBoundaries runs again every time a cut is
// dragged in the timeline — dropping it there would silently delete the music
// the moment the user nudged a single cut.
export type BoundaryExtras = {
  music?: MusicCue[];
  ducking?: Ducking;
  narrationPauses?: { start: number; end: number }[];
};

// A cue knows which scenes it covers, so moving a cut moves the music with it:
// the cue keeps spanning the same scenes, at their new times.
const restretchCues = (
  music: MusicCue[],
  boundarySeconds: number[],
): MusicCue[] =>
  music.map((cue) => {
    if (cue.scenes.length === 0) return cue;
    const first = Math.min(...cue.scenes);
    const last = Math.max(...cue.scenes);
    const startInSeconds = boundarySeconds[first] ?? cue.startInSeconds;
    const endInSeconds = boundarySeconds[last + 1] ?? cue.endInSeconds;
    if (endInSeconds <= startInSeconds) return cue;
    return { ...cue, startInSeconds, endInSeconds };
  });

// Remotion refuses a transition that is not shorter than both sequences it
// joins, and a crash at render time is a terrible way to find that out. Two
// short scenes in a row simply get a shorter transition.
const clampTransition = (
  requestedFrames: number,
  previousDesiredFrames: number,
  nextDesiredFrames: number,
): number => {
  const longestAllowed =
    Math.min(previousDesiredFrames, nextDesiredFrames) - 1;
  return Math.max(0, Math.min(requestedFrames, longestAllowed));
};

// Pure, isomorphic (no Node APIs) — used both server-side by buildSmartPlan
// and client-side while dragging the cut timeline, so the preview and the
// persisted plan are always computed by the exact same math.
//
// `internalBoundarySeconds` must have exactly `clips.length - 1` entries,
// strictly ascending, each strictly between 0 and narration.durationInSeconds.
export const applyBoundaries = (
  clips: BoundaryClip[],
  narration: BoundaryNarration,
  internalBoundarySeconds: number[],
  fps: number,
  transitionFrames: number,
  width: number,
  height: number,
  extras: BoundaryExtras = {},
): EditPlan => {
  const totalSeconds = narration.durationInSeconds;
  const durationInFrames = Math.ceil(totalSeconds * fps);

  const boundaryFrames = [
    0,
    ...internalBoundarySeconds.map((s) => Math.round(s * fps)),
    durationInFrames,
  ];

  const desiredFrames = clips.map(
    (_, i) => boundaryFrames[i + 1] - boundaryFrames[i],
  );

  // The transition that FOLLOWS clip i is declared on clip i+1, because
  // scenes.json describes each scene by how it enters. A hard cut costs
  // nothing; anything else overlaps the two slots and has to be paid for by
  // inflating the earlier one.
  const transitionAfter = clips.map((_, i) => {
    const next = clips[i + 1];
    if (!next) return 0;
    const preset = next.transitionFromPrevious ?? "dissolve";
    if (isHardCut(preset)) return 0;
    return clampTransition(
      next.transitionFrames ?? transitionFrames,
      desiredFrames[i],
      desiredFrames[i + 1],
    );
  });

  const planClips = clips.map((clip, i) => ({
    id: clip.id,
    file: clip.file,
    naturalDurationInSeconds: clip.durationInSeconds,
    slotDurationInFrames: desiredFrames[i] + transitionAfter[i],
    startInNarrationSeconds: boundaryFrames[i] / fps,
    audioMode: clip.audioMode ?? "mix",
    filter: clip.filter ?? "none",
    transitionFromPrevious: clip.transitionFromPrevious ?? "dissolve",
    // Persist the clamped value, so what the plan says is what renders.
    transitionFrames: i === 0 ? 0 : transitionAfter[i - 1],
    energyScore: clip.energyScore ?? 0,
  }));

  const cutPoints = boundaryFrames.map((f) => f / fps);

  return {
    version: 1,
    fps,
    width,
    height,
    narration: {
      file: narration.file,
      durationInSeconds: totalSeconds,
      startInSeconds: narration.startInSeconds ?? 0,
    },
    transitionFrames,
    clips: planClips,
    cutPoints,
    music: restretchCues(extras.music ?? [], cutPoints),
    ducking: extras.ducking ?? DEFAULT_DUCKING,
    narrationPauses: extras.narrationPauses ?? [],
  };
};
