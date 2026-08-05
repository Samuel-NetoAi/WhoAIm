import { isHardCut, type EditPlan } from "./schema";

// The frames each transition overlaps away, boundary by boundary. A hard cut
// overlaps nothing; the rest borrow from the slot before them.
export const transitionOverlaps = (plan: EditPlan): number[] =>
  plan.clips.slice(1).map((clip) => {
    const preset = clip.transitionFromPrevious ?? "dissolve";
    if (isHardCut(preset)) return 0;
    return clip.transitionFrames ?? plan.transitionFrames;
  });

// TransitionSeries overlaps adjacent slots, so the rendered timeline is
// shorter than the sum of the individual slots — by exactly the sum of the
// transitions actually rendered.
export const calculateTotalFrames = (plan: EditPlan): number => {
  const sumOfSlots = plan.clips.reduce(
    (sum, clip) => sum + clip.slotDurationInFrames,
    0,
  );
  const sumOfOverlaps = transitionOverlaps(plan).reduce((a, b) => a + b, 0);
  return sumOfSlots - sumOfOverlaps;
};
