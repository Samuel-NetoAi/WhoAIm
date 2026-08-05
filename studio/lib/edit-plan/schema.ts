import { z } from "zod";

// "mix" (default): the clip's own audio plays at a low level under the
// narration, like ambient bed in a documentary. "replace": the clip's own
// audio becomes the primary sound and the narration is ducked to silence
// for that clip's slot — for the specific scenes where the clip's own sound
// is what should be heard instead of the voiceover. "muted": no clip audio.
export const audioModeSchema = z
  .enum(["mix", "replace", "muted"])
  .default("mix");

// Visual filter preset applied to the clip (see remotion/filters.ts).
export const filterPresetSchema = z
  .enum(["none", "cinematic", "warm", "cold", "noir", "vintage"])
  .default("none");

export const clipPlanSchema = z.object({
  id: z.string(),
  file: z.string(),
  naturalDurationInSeconds: z.number().positive(),
  slotDurationInFrames: z.number().int().positive(),
  startInNarrationSeconds: z.number().nonnegative(),
  audioMode: audioModeSchema,
  filter: filterPresetSchema,
});

export const editPlanSchema = z.object({
  version: z.literal(1),
  fps: z.number().int().positive(),
  width: z.number().int().positive(),
  height: z.number().int().positive(),
  narration: z.object({
    file: z.string(),
    durationInSeconds: z.number().positive(),
  }),
  transitionFrames: z.number().int().nonnegative(),
  clips: z.array(clipPlanSchema).min(1),
  cutPoints: z.array(z.number()).optional(),
});

export type AudioMode = z.infer<typeof audioModeSchema>;
export type FilterPreset = z.infer<typeof filterPresetSchema>;
export type ClipPlan = z.infer<typeof clipPlanSchema>;
export type EditPlan = z.infer<typeof editPlanSchema>;
