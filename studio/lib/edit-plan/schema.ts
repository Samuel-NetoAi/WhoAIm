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

// How this clip enters, i.e. the transition on the boundary with the clip
// BEFORE it (the first clip's value is meaningless and ignored). The
// vocabulary mirrors the one the `whoiam` skill writes into scenes.json, so
// the editorial decision travels from the script to the render unchanged.
//
// "corte" and "match" are both hard cuts — a match cut is a hard cut chosen
// for the visual rhyme, not a different render operation. See
// Alpha/docs/EDICAO-MONTAGEM.md for when each one is the right call.
//
// Default is "dissolve" for backward compatibility: plans written before this
// field existed had a crossfade on every boundary, and parsing them must not
// silently re-cut the video.
export const transitionPresetSchema = z
  .enum([
    "corte",
    "match",
    "dissolve",
    "fade",
    "film-burn",
    "dreamy-zoom",
    "ripple",
    "linear-blur",
  ])
  .default("dissolve");

export const clipPlanSchema = z.object({
  id: z.string(),
  file: z.string(),
  naturalDurationInSeconds: z.number().positive(),
  slotDurationInFrames: z.number().int().positive(),
  startInNarrationSeconds: z.number().nonnegative(),
  audioMode: audioModeSchema,
  filter: filterPresetSchema,
  transitionFromPrevious: transitionPresetSchema,
  // Duration of that transition; falls back to the plan-wide transitionFrames.
  // Coupled to slotDurationInFrames: a transition overlaps the two slots it
  // joins, so the earlier slot is inflated to pay for it. Change one by hand
  // and the video drifts away from the narration — always go through
  // applyBoundaries, which is what the UI and every plan builder do.
  transitionFrames: z.number().int().nonnegative().optional(),
});

// One continuous stretch of music. A cue follows the EMOTIONAL SEQUENCE, not
// the block: consecutive scenes sharing the same cue become one span, and a
// new cue only starts when the atmosphere turns. See Alpha/docs/TRILHA-SONORA.md.
export const musicCueSchema = z.object({
  id: z.string(),
  // Relative to the project's public dir, e.g. "music/veil-of-dust.mp3". The
  // track is copied into the project so the render bundle can reach it and the
  // project stays self-contained when it moves between machines.
  file: z.string(),
  startInSeconds: z.number().nonnegative(),
  endInSeconds: z.number().positive(),
  // Ceiling for this cue, before ducking. Lets a quiet drone and a loud action
  // cue coexist without re-mastering the files.
  gain: z.number().min(0).max(1).default(1),
  fadeInSeconds: z.number().nonnegative().default(1.5),
  fadeOutSeconds: z.number().nonnegative().default(2),
  // Set when the track is shorter than the span it has to cover. The doc says
  // to generate music LONGER than the sequence; looping is the fallback, and
  // flagging it keeps the compromise visible instead of silent.
  loop: z.boolean().default(false),
  scenes: z.array(z.number().int().nonnegative()).default([]),
});

// Levels are relative to the narration, which always sits at 1.0 — the rule of
// the channel is that the voice never competes with the music.
export const DEFAULT_DUCKING = {
  // ≈ −18 dB. The measured practice is 18–25 dB below the voice.
  underVoice: 0.12,
  // Music swells in the gaps between sentences (≈ −11 dB).
  inPauses: 0.28,
  // Duck fast so the first syllable is never buried...
  attackSeconds: 0.25,
  // ...and come back slowly, or the mix pumps audibly.
  releaseSeconds: 1,
  // A pause shorter than this is a breath, not a gap: swelling into it makes
  // the music surge between words.
  minimumPauseSeconds: 0.9,
} as const;

export const duckingSchema = z.object({
  underVoice: z.number().min(0).max(1).default(DEFAULT_DUCKING.underVoice),
  inPauses: z.number().min(0).max(1).default(DEFAULT_DUCKING.inPauses),
  attackSeconds: z.number().positive().default(DEFAULT_DUCKING.attackSeconds),
  releaseSeconds: z.number().positive().default(DEFAULT_DUCKING.releaseSeconds),
  minimumPauseSeconds: z
    .number()
    .positive()
    .default(DEFAULT_DUCKING.minimumPauseSeconds),
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
  music: z.array(musicCueSchema).default([]),
  ducking: duckingSchema.default(DEFAULT_DUCKING),
  // Narration pauses, carried in the plan so the ducking curve is identical in
  // the browser preview and in the headless render without re-reading
  // analysis/silences.json from two different places.
  narrationPauses: z
    .array(z.object({ start: z.number(), end: z.number() }))
    .default([]),
});

export type AudioMode = z.infer<typeof audioModeSchema>;
export type FilterPreset = z.infer<typeof filterPresetSchema>;
export type TransitionPreset = z.infer<typeof transitionPresetSchema>;

// Hard cuts render as no Transition element at all, which sidesteps
// Remotion's "transition must be shorter than both neighbours" constraint and
// gives the clips their full slot back.
export const isHardCut = (preset: TransitionPreset): boolean =>
  preset === "corte" || preset === "match";
export type ClipPlan = z.infer<typeof clipPlanSchema>;
export type MusicCue = z.infer<typeof musicCueSchema>;
export type Ducking = z.infer<typeof duckingSchema>;
export type EditPlan = z.infer<typeof editPlanSchema>;
