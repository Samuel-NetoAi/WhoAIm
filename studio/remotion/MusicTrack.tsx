import React from "react";
import { Sequence, staticFile, useVideoConfig } from "remotion";
import { Audio } from "@remotion/media";
import type { Ducking, MusicCue } from "../lib/edit-plan/schema";
import { musicVolumeAt, qualifyingPauses, type Pause } from "../lib/audio/ducking";

// One <Audio> per cue, wrapped in a Sequence so the track only exists during
// its own stretch of timeline. A scene marked SILENCIO simply has no cue
// covering it — silence is the absence of a cue, not a muted one.
export const MusicTrack: React.FC<{
  music: MusicCue[];
  ducking: Ducking;
  pauses: Pause[];
  mediaBaseUrl?: string;
}> = ({ music, ducking, pauses, mediaBaseUrl }) => {
  const { fps } = useVideoConfig();
  const gaps = qualifyingPauses(pauses, ducking.minimumPauseSeconds);

  return (
    <>
      {music.map((cue) => {
        const from = Math.round(cue.startInSeconds * fps);
        const durationInFrames = Math.max(
          1,
          Math.round((cue.endInSeconds - cue.startInSeconds) * fps),
        );
        const src = mediaBaseUrl
          ? `${mediaBaseUrl}/${cue.file}`
          : staticFile(cue.file);

        return (
          <Sequence key={cue.id} from={from} durationInFrames={durationInFrames}>
            <Audio
              src={src}
              loop={cue.loop}
              // The frame is local to the Sequence, so it has to be shifted
              // back onto the timeline before asking for the volume — the
              // ducking curve is expressed in absolute narration time.
              volume={(frame) =>
                musicVolumeAt(
                  (frame + from) / fps,
                  cue,
                  gaps,
                  ducking,
                )
              }
            />
          </Sequence>
        );
      })}
    </>
  );
};
