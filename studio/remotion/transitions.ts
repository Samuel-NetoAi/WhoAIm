import type { TransitionPresentation } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { filmBurn } from "@remotion/transitions/film-burn";
import { dreamyZoom } from "@remotion/transitions/dreamy-zoom";
import { ripple } from "@remotion/transitions/ripple";
import { linearBlur } from "@remotion/transitions/linear-blur";
import type { TransitionPreset } from "../lib/edit-plan/schema";

// Editorial vocabulary -> Remotion presentation.
//
// Note that our "dissolve" is Remotion's `fade()` (a plain crossfade, what an
// editor calls a dissolve) — NOT Remotion's `dissolve` presentation, which is
// a shader burn effect. Our "fade" is the fade THROUGH BLACK: the outgoing
// scene fades to the composition's black background before the next one
// arrives, which is what marks the end of a chapter.
// The return type is widened deliberately: each presentation carries its own
// props type, and TransitionSeries.Transition cannot infer a single generic
// from a union of them.
export const presentationFor = (
  preset: TransitionPreset,
): TransitionPresentation<Record<string, unknown>> => {
  switch (preset) {
    case "fade":
      return fade({ shouldFadeOutExitingScene: true });
    case "film-burn":
      return filmBurn({});
    case "dreamy-zoom":
      return dreamyZoom({});
    case "ripple":
      return ripple({});
    case "linear-blur":
      return linearBlur({});
    // "corte" and "match" never reach here — a hard cut renders no Transition
    // element at all (see EditedVideo).
    case "dissolve":
    default:
      return fade();
  }
};

export const TRANSITION_LABELS: Record<TransitionPreset, string> = {
  corte: "Corte seco",
  match: "Match cut (corte)",
  dissolve: "Dissolve (crossfade)",
  fade: "Fade pelo preto",
  "film-burn": "Queima de filme",
  "dreamy-zoom": "Zoom onírico",
  ripple: "Ondulação",
  "linear-blur": "Desfoque linear",
};
