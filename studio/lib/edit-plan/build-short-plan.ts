import type { EditPlan } from "./schema";
import { applyBoundaries } from "./apply-boundaries";
import { SHORT_RESOLUTION } from "./output-resolution";

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

  // The short is a prefix of the full edit, so a cue carries over when it
  // starts inside the kept scenes — trimmed to them if it ran past the cutoff.
  // Without this the Short would render silent while the full video had music.
  const lastKeptScene = includedClips.length - 1;
  const music = (fullPlan.music ?? [])
    .filter((cue) => Math.min(...cue.scenes) <= lastKeptScene)
    .map((cue) => ({
      ...cue,
      scenes: cue.scenes.filter((scene) => scene <= lastKeptScene),
    }));

  // Same prefix logic as the music, minus the re-stretching: a caption is a
  // measured moment in the narration, and the narration is the same file
  // simply truncated at `cutoff`. A caption that straddles the cutoff is kept
  // and clipped — cutting a subtitle's tail is better than dropping a line
  // that is half-spoken on screen.
  const captions = (fullPlan.captions ?? [])
    .filter((caption) => caption.t0 < cutoff)
    .map((caption) => ({ ...caption, t1: Math.min(caption.t1, cutoff) }));

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
    })),
    { file: fullPlan.narration.file, durationInSeconds: cutoff },
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
      narrationPauses: fullPlan.narrationPauses,
      captions,
      // The Short is the one cut that burns them in: it autoplays muted in
      // the feed, so an un-captioned Short is a silent Short. This is what
      // align/README.md meant by "para o Studio/Remotion queimar no Short".
      burnCaptions: captions.length > 0,
    },
  );
};
