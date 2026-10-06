import React from "react";
import {
  AbsoluteFill,
  Freeze,
  interpolate,
  OffthreadVideo,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import type { AudioMode, FilterPreset } from "../lib/edit-plan/schema";
import { FILTER_PRESETS } from "./filters";

const ZOOM_AMOUNT = 0.12;

// "mix" plays the clip's own sound as a low ambient bed under the
// narration — audible presence without competing with the voiceover.
const MIX_VOLUME = 0.3;

const volumeForAudioMode = (audioMode: AudioMode): number => {
  if (audioMode === "muted") return 0;
  if (audioMode === "replace") return 1;
  return MIX_VOLUME;
};

// Plays a clip once at natural speed, then holds its last frame with a slow
// zoom for the rest of its slot — instead of restarting the clip from frame
// 0, which reads as a visibly repeated/duplicated clip (this is the fix
// applied to the Medusa edit after the loop-based version looked like
// duplicated footage).
export const Clip: React.FC<{
  file: string;
  mediaBaseUrl?: string;
  naturalDurationInSeconds: number;
  slotFrames: number;
  width: number;
  height: number;
  audioMode?: AudioMode;
  filter?: FilterPreset;
  cropX?: number;
}> = ({
  file,
  mediaBaseUrl,
  naturalDurationInSeconds,
  slotFrames,
  width,
  height,
  audioMode = "mix",
  filter = "none",
  cropX = 0.5,
}) => {
  const { fps } = useVideoConfig();
  const frame = useCurrentFrame();
  const naturalFrames = Math.round(naturalDurationInSeconds * fps);
  const playFrames = Math.min(naturalFrames, slotFrames);
  const scale = interpolate(frame, [0, slotFrames], [1, 1 + ZOOM_AMOUNT], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  // During a real render, staticFile() resolves against the bundle's
  // publicDir (set to this project's public/ folder at bundle time). In the
  // browser-side Player preview there is no such bundle, so mediaBaseUrl
  // points at the media-serving API route instead.
  const src = mediaBaseUrl ? `${mediaBaseUrl}/${file}` : staticFile(file);

  const cssFilter = FILTER_PRESETS[filter];

  return (
    <AbsoluteFill
      style={{
        transform: `scale(${scale})`,
        ...(cssFilter ? { filter: cssFilter } : {}),
      }}
    >
      <Freeze frame={playFrames - 1} active={(f) => f >= playFrames}>
        {/* OffthreadVideo (core Remotion, decodes with FFmpeg), NOT <Video>
            from @remotion/media (decodes with WebCodecs in headless Chromium).
            That choice is the fix for the render hang that blocked the clip
            enhancement pipeline from 19/08 to 04/09/2026, and it was settled
            by measurement, not by preference — same clips, same plan, same
            machine, only the decoder swapped:

              enhanced clips (1882x1080, 60fps, High L4.2, 19 MB)
                <Video>          0% progress for 290s, then
                                 "Timeout while extracting frame at 0.13sec"
                <OffthreadVideo> done in ~60s, progress climbing normally

              raw clips (864x496, 24fps, 5 MB) — the case that already worked
                <Video>          36s
                <OffthreadVideo> 40s

            So WebCodecs costs ~11% less on footage it can decode, and hangs
            outright on footage it cannot — with no error until the mount
            timeout fires, five minutes later. One path that always works beats
            a faster one that silently stalls; the 11% is the premium paid for
            that, knowingly.

            @remotion/media was never a documented decision here — it arrived
            in a bulk snapshot commit — and Remotion's own docs describe the
            WebCodecs packages as being phased out in favour of Mediabunny. */}
        <OffthreadVideo
          src={src}
          volume={volumeForAudioMode(audioMode)}
          trimAfter={playFrames}
          // `cover` already fills a frame of a different aspect by cropping;
          // objectPosition is what decides WHICH part survives the crop. It
          // only has any effect when the aspects differ (the 9:16 Short out of
          // 16:9 footage) — on a matching aspect there is nothing to crop and
          // the value is inert.
          style={{
            width,
            height,
            objectFit: "cover",
            objectPosition: `${cropX * 100}% 50%`,
          }}
        />
      </Freeze>
    </AbsoluteFill>
  );
};
