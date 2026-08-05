import type { EditPlan } from "./schema";

// TransitionSeries overlaps adjacent slots by `transitionFrames`, so the
// rendered timeline is shorter than the sum of the individual slots.
export const calculateTotalFrames = (plan: EditPlan): number => {
  const sumOfSlots = plan.clips.reduce(
    (sum, clip) => sum + clip.slotDurationInFrames,
    0,
  );
  const numTransitions = plan.clips.length - 1;
  return sumOfSlots - numTransitions * plan.transitionFrames;
};
