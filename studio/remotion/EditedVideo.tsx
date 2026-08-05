import React from "react";
import { AbsoluteFill, staticFile } from "remotion";
import { Audio } from "@remotion/media";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { isHardCut, type EditPlan } from "../lib/edit-plan/schema";
import { Clip } from "./Clip";
import { presentationFor } from "./transitions";
import { MusicTrack } from "./MusicTrack";

export const EditedVideo: React.FC<{
  editPlan: EditPlan;
  mediaBaseUrl?: string;
}> = ({ editPlan, mediaBaseUrl }) => {
  const { clips, transitionFrames, narration, width, height, fps } = editPlan;
  const numClips = clips.length;
  const narrationSrc = mediaBaseUrl
    ? `${mediaBaseUrl}/${narration.file}`
    : staticFile(narration.file);

  // Boundaries between clips, in frames — cutPoints if the plan has them
  // (it always does once analyzed), else derived from each clip's own start.
  const boundarySeconds =
    editPlan.cutPoints ??
    [
      0,
      ...clips.slice(1).map((c) => c.startInNarrationSeconds),
      narration.durationInSeconds,
    ];
  const replaceRanges = clips
    .map((clip, i) => ({
      audioMode: clip.audioMode ?? "mix",
      startFrame: Math.round(boundarySeconds[i] * fps),
      endFrame: Math.round(boundarySeconds[i + 1] * fps),
    }))
    .filter((range) => range.audioMode === "replace");

  // Ducks the narration to silence during clips set to "replace" mode, so
  // the clip's own audio (played at full volume in Clip.tsx) is what's
  // heard instead of the voiceover for those specific scenes.
  const narrationVolume = (frame: number): number => {
    for (const range of replaceRanges) {
      if (frame >= range.startFrame && frame < range.endFrame) return 0;
    }
    return 1;
  };

  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <TransitionSeries>
        {clips.flatMap((clip, i) => {
          const sequence = (
            <TransitionSeries.Sequence
              key={`seq-${clip.id}`}
              durationInFrames={clip.slotDurationInFrames}
            >
              <Clip
                file={clip.file}
                mediaBaseUrl={mediaBaseUrl}
                naturalDurationInSeconds={clip.naturalDurationInSeconds}
                slotFrames={clip.slotDurationInFrames}
                width={width}
                height={height}
                audioMode={clip.audioMode}
                filter={clip.filter}
              />
            </TransitionSeries.Sequence>
          );

          const next = clips[i + 1];
          if (i === numClips - 1) {
            return [sequence];
          }

          // The boundary's transition is declared on the clip that ENTERS it.
          // A hard cut emits no Transition at all: that keeps both slots whole
          // and avoids Remotion's "shorter than both neighbours" constraint.
          const preset = next.transitionFromPrevious ?? "dissolve";
          if (isHardCut(preset)) {
            return [sequence];
          }

          const transition = (
            <TransitionSeries.Transition
              key={`transition-${clip.id}`}
              presentation={presentationFor(preset)}
              timing={linearTiming({
                durationInFrames: next.transitionFrames ?? transitionFrames,
              })}
            />
          );

          return [sequence, transition];
        })}
      </TransitionSeries>
      <Audio src={narrationSrc} volume={narrationVolume} />
      <MusicTrack
        music={editPlan.music ?? []}
        ducking={editPlan.ducking}
        pauses={editPlan.narrationPauses ?? []}
        mediaBaseUrl={mediaBaseUrl}
      />
    </AbsoluteFill>
  );
};
