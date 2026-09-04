import React from "react";
import {
  AbsoluteFill,
  Freeze,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Video } from "@remotion/media";
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
        <Video
          src={src}
          volume={volumeForAudioMode(audioMode)}
          trimAfter={playFrames}
          objectFit="cover"
          // `cover` already fills a frame of a different aspect by cropping;
          // objectPosition is what decides WHICH part survives the crop. It
          // only has any effect when the aspects differ (the 9:16 Short out of
          // 16:9 footage) — on a matching aspect there is nothing to crop and
          // the value is inert.
          style={{
            width,
            height,
            objectPosition: `${cropX * 100}% 50%`,
          }}
        />
      </Freeze>
    </AbsoluteFill>
  );
};
