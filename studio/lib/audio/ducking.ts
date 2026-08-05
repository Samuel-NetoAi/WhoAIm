import type { Ducking, MusicCue } from "../edit-plan/schema";

export type Pause = { start: number; end: number };

// Pure and isomorphic: the browser Player and the headless render call this
// same function, so what you hear in the preview is what exports.
//
// The narration is never touched — it always plays at full level. It is the
// music that moves out of its way and swells back in the gaps, which is the
// rule of the channel: the voice never competes with the music.

const clamp01 = (value: number): number => Math.min(1, Math.max(0, value));

// A pause only counts if it is long enough to be a gap rather than a breath.
// Swelling into every inter-word breath makes the music pump audibly.
export const qualifyingPauses = (
  pauses: Pause[],
  minimumPauseSeconds: number,
): Pause[] =>
  pauses.filter((pause) => pause.end - pause.start >= minimumPauseSeconds);

// Ducking envelope: `underVoice` while the narration speaks, rising towards
// `inPauses` inside a gap.
//
// The rise takes `releaseSeconds` from the start of the gap and the fall takes
// `attackSeconds` ending exactly when the voice returns — taking the minimum of
// the two ramps means a gap shorter than release+attack simply peaks lower
// instead of being cut off mid-swell, and the music is always back down before
// the first syllable.
export const duckingLevelAt = (
  seconds: number,
  pauses: Pause[],
  ducking: Ducking,
): number => {
  for (const pause of pauses) {
    if (seconds < pause.start || seconds > pause.end) continue;
    const rising = clamp01((seconds - pause.start) / ducking.releaseSeconds);
    const falling = clamp01((pause.end - seconds) / ducking.attackSeconds);
    const openness = Math.min(rising, falling);
    return ducking.underVoice + (ducking.inPauses - ducking.underVoice) * openness;
  }
  return ducking.underVoice;
};

// Fade in/out at the edges of the cue itself, so a cue never starts or stops
// abruptly — and so a cue that ends before a SILENCIO scene has time to
// disappear before the silence is supposed to land.
export const cueFadeAt = (seconds: number, cue: MusicCue): number => {
  const sinceStart = seconds - cue.startInSeconds;
  const untilEnd = cue.endInSeconds - seconds;
  if (sinceStart < 0 || untilEnd < 0) return 0;

  const fadingIn =
    cue.fadeInSeconds > 0 ? clamp01(sinceStart / cue.fadeInSeconds) : 1;
  const fadingOut =
    cue.fadeOutSeconds > 0 ? clamp01(untilEnd / cue.fadeOutSeconds) : 1;
  return Math.min(fadingIn, fadingOut);
};

export const musicVolumeAt = (
  seconds: number,
  cue: MusicCue,
  pauses: Pause[],
  ducking: Ducking,
): number =>
  cue.gain * cueFadeAt(seconds, cue) * duckingLevelAt(seconds, pauses, ducking);
