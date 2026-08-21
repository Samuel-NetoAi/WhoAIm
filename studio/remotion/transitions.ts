import { isHtmlInCanvasSupported } from "remotion";
import type { TransitionPresentation } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { filmBurn } from "@remotion/transitions/film-burn";
import { dreamyZoom } from "@remotion/transitions/dreamy-zoom";
import { ripple } from "@remotion/transitions/ripple";
import { linearBlur } from "@remotion/transitions/linear-blur";
import type { TransitionPreset } from "../lib/edit-plan/schema";

// These four composite their WebGL shader through <HtmlInCanvas>, which
// needs a very recent Canvas API (Chrome 148+, or its chrome://flags dev
// toggle) — present in the headless Chromium the actual render runs in
// (verified with a real render), but often missing in whatever browser is
// running the live editor Preview. There it throws a fatal "HTML in Canvas
// is not supported" error instead of drawing a frame.
const SHADER_BACKED_PRESETS = new Set<TransitionPreset>([
  "film-burn",
  "dreamy-zoom",
  "ripple",
  "linear-blur",
]);

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
  // Falls back to a plain crossfade wherever HtmlInCanvas isn't available —
  // just for THIS render pass, so the Preview stays usable instead of
  // crashing. The real render (where the capability check passes) still gets
  // the actual shader effect.
  if (SHADER_BACKED_PRESETS.has(preset) && !isHtmlInCanvasSupported()) {
    return fade();
  }

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
