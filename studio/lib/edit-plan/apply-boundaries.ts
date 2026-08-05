import type { AudioMode, EditPlan, FilterPreset } from "./schema";

export type BoundaryClip = {
  id: string;
  file: string;
  durationInSeconds: number;
  audioMode?: AudioMode;
  filter?: FilterPreset;
};

export type BoundaryNarration = {
  file: string;
  durationInSeconds: number;
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
): EditPlan => {
  const totalSeconds = narration.durationInSeconds;
  const durationInFrames = Math.ceil(totalSeconds * fps);

  const boundaryFrames = [
    0,
    ...internalBoundarySeconds.map((s) => Math.round(s * fps)),
    durationInFrames,
  ];

  const planClips = clips.map((clip, i) => {
    const isLast = i === clips.length - 1;
    const desiredFrames = boundaryFrames[i + 1] - boundaryFrames[i];
    const slotDurationInFrames =
      desiredFrames + (isLast ? 0 : transitionFrames);

    return {
      id: clip.id,
      file: clip.file,
      naturalDurationInSeconds: clip.durationInSeconds,
      slotDurationInFrames,
      startInNarrationSeconds: boundaryFrames[i] / fps,
      audioMode: clip.audioMode ?? "mix",
      filter: clip.filter ?? "none",
    };
  });

  return {
    version: 1,
    fps,
    width,
    height,
    narration: { file: narration.file, durationInSeconds: totalSeconds },
    transitionFrames,
    clips: planClips,
    cutPoints: boundaryFrames.map((f) => f / fps),
  };
};
