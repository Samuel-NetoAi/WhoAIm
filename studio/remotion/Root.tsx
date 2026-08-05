import React from "react";
import { CalculateMetadataFunction, Composition } from "remotion";
import { EditedVideo } from "./EditedVideo";
import { DEFAULT_DUCKING, type EditPlan } from "../lib/edit-plan/schema";
import { calculateTotalFrames } from "../lib/edit-plan/calculate-total-frames";

type Props = { editPlan: EditPlan };

// The whole edit plan (slot durations, transitions, dimensions) is computed
// upstream by the analysis step, so this is pure arithmetic — no I/O, unlike
// medusa-video's calculateMetadata which fetched the narration duration live.
const calculateMetadata: CalculateMetadataFunction<Props> = ({ props }) => {
  return {
    durationInFrames: calculateTotalFrames(props.editPlan),
    fps: props.editPlan.fps,
    width: props.editPlan.width,
    height: props.editPlan.height,
  };
};

// Placeholder so the Composition has a structurally valid default — real
// renders and previews always pass a real editPlan via inputProps.
const DEFAULT_PLAN: EditPlan = {
  version: 1,
  fps: 30,
  width: 1920,
  height: 1080,
  narration: { file: "audio/placeholder.mp3", durationInSeconds: 1 },
  transitionFrames: 0,
  clips: [
    {
      id: "placeholder",
      file: "videos/placeholder.mp4",
      naturalDurationInSeconds: 1,
      slotDurationInFrames: 30,
      startInNarrationSeconds: 0,
      audioMode: "mix",
      filter: "none",
      transitionFromPrevious: "dissolve",
    },
  ],
  music: [],
  ducking: DEFAULT_DUCKING,
  narrationPauses: [],
};

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="EditedVideo"
      component={EditedVideo}
      durationInFrames={30}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{ editPlan: DEFAULT_PLAN }}
      calculateMetadata={calculateMetadata}
    />
  );
};
