import type { ProjectProbe } from "../media/probe-project";
import type { EditPlan } from "./schema";

export const DEFAULT_FPS = 30;
export const DEFAULT_TRANSITION_FRAMES = 20;

// Divides the narration into N equal slots (N = number of available clips),
// inflated to account for TransitionSeries crossfade overlap so the
// post-transition total exactly equals the narration duration. This is the
// same math used manually for the Medusa edit, generalized to N clips.
// It's the Phase A baseline — Phase B replaces this with silence-snapped
// boundaries, kept available as a fallback toggle.
export const buildNaivePlan = (
  probe: ProjectProbe,
  fps: number = DEFAULT_FPS,
  transitionFrames: number = DEFAULT_TRANSITION_FRAMES,
): EditPlan => {
  const { clips, narration } = probe;
  const numClips = clips.length;
  const numTransitions = numClips - 1;

  const durationInFrames = Math.ceil(narration.durationInSeconds * fps);
  const sumOfSequenceDurations =
    durationInFrames + numTransitions * transitionFrames;
  const baseSlot = Math.floor(sumOfSequenceDurations / numClips);
  const remainder = sumOfSequenceDurations - baseSlot * numClips;

  let cursorFrames = 0;
  const planClips = clips.map((clip, i) => {
    const isLast = i === numClips - 1;
    const slotDurationInFrames = isLast ? baseSlot + remainder : baseSlot;
    const startInNarrationSeconds = cursorFrames / fps;
    cursorFrames += slotDurationInFrames - (isLast ? 0 : transitionFrames);

    return {
      id: clip.id,
      file: clip.file,
      naturalDurationInSeconds: clip.durationInSeconds,
      slotDurationInFrames,
      startInNarrationSeconds,
      audioMode: "mix" as const,
      filter: "none" as const,
    };
  });

  const firstClip = clips[0];

  return {
    version: 1,
    fps,
    width: firstClip.width,
    height: firstClip.height,
    narration: {
      file: narration.file,
      durationInSeconds: narration.durationInSeconds,
    },
    transitionFrames,
    clips: planClips,
  };
};
