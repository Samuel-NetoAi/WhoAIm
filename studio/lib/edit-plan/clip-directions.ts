import type { BoundaryClip } from "./apply-boundaries";
import type { SceneDirection } from "../scenes/schema";

// Per-clip editorial choices coming from scenes.json, aligned positionally
// with the project's clips. `null` for a clip the scenes file says nothing
// about — that clip keeps the defaults.
export type ClipDirections = (SceneDirection | null)[];

type ProbedClip = { id: string; file: string; durationInSeconds: number };

// Single place where "what the skill decided" meets "what the plan builds".
// Without a scenes.json every clip falls back to no filter and a dissolve,
// which is exactly how the Studio behaved before the file existed.
export const toBoundaryClips = (
  clips: ProbedClip[],
  directions?: ClipDirections,
): BoundaryClip[] =>
  clips.map((clip, i) => {
    const direction = directions?.[i] ?? null;
    return {
      id: clip.id,
      file: clip.file,
      durationInSeconds: clip.durationInSeconds,
      filter: direction?.filter,
      transitionFromPrevious: direction?.transitionFromPrevious,
    };
  });
