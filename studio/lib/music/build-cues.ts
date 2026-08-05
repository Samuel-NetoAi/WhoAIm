import type { MusicCue } from "../edit-plan/schema";
import type { Scene } from "../scenes/schema";
import type { Track } from "./catalog";

// The cue that means "no music here". Silence is a deliberate musical choice,
// not a missing value: cutting the score just before a transformation is
// usually stronger than scoring it. See Alpha/docs/TRILHA-SONORA.md.
export const SILENCE_CUE = "SILENCIO";

// Cue types that are not tracks from the catalogue. STINGER and DRONE are in
// the vocabulary of the skill but have no rendering of their own yet, so they
// are reported rather than silently dropped.
const NON_TRACK_CUES = new Set(["STINGER", "DRONE"]);

// Where a library track lands inside the project. Kept next to the cue builder
// because the plan's `file` and the copy destination must never disagree.
export const publicPathForTrack = (track: Track): string =>
  `music/${track.arquivo.split(/[\\/]/).pop()}`;

export type BuiltCues = {
  cues: MusicCue[];
  // Tracks the caller must copy into the project's public dir. Copying (rather
  // than referencing the library in place) is what lets the render bundle reach
  // the audio and keeps the project self-contained when it moves between the
  // Windows machine and this one.
  tracksUsed: Track[];
  notes: string[];
};

type SceneSpan = { cue: string; firstScene: number; lastScene: number };

// Consecutive scenes sharing a cue collapse into ONE span. This is the rule
// that matters musically: the cue follows the emotional sequence, so a single
// piece plays across several blocks and only changes when the atmosphere turns.
const groupConsecutive = (scenes: Scene[]): SceneSpan[] => {
  const spans: SceneSpan[] = [];
  scenes.forEach((scene, index) => {
    const cue = scene.cue?.trim();
    if (!cue) return;
    const open = spans[spans.length - 1];
    if (open && open.cue === cue && open.lastScene === index - 1) {
      open.lastScene = index;
      return;
    }
    spans.push({ cue, firstScene: index, lastScene: index });
  });
  return spans;
};

export const buildMusicCues = (
  scenes: Scene[],
  // Scene boundaries in seconds — cutPoints from the edit plan, so the music
  // changes exactly where the scene does.
  cutPoints: number[],
  catalog: Map<string, Track>,
): BuiltCues => {
  const cues: MusicCue[] = [];
  const tracksUsed = new Map<string, Track>();
  const notes: string[] = [];
  const missing = new Set<string>();

  for (const span of groupConsecutive(scenes)) {
    if (span.cue === SILENCE_CUE) continue;

    if (NON_TRACK_CUES.has(span.cue)) {
      notes.push(
        `cue "${span.cue}" (cena ${span.firstScene + 1}) ainda não é renderizado`,
      );
      continue;
    }

    const track = catalog.get(span.cue);
    if (!track) {
      missing.add(span.cue);
      continue;
    }

    const startInSeconds = cutPoints[span.firstScene];
    const endInSeconds = cutPoints[span.lastScene + 1];
    if (
      startInSeconds === undefined ||
      endInSeconds === undefined ||
      endInSeconds <= startInSeconds
    ) {
      notes.push(`cue "${span.cue}" caiu fora da linha do tempo e foi ignorado`);
      continue;
    }

    const spanSeconds = endInSeconds - startInSeconds;
    const loop = track.duracao < spanSeconds;
    if (loop) {
      notes.push(
        `faixa "${track.id}" tem ${track.duracao.toFixed(0)}s para cobrir ` +
          `${spanSeconds.toFixed(0)}s e será repetida — gere a música maior que a sequência`,
      );
    }

    cues.push({
      id: `${span.cue}-${span.firstScene}`,
      file: publicPathForTrack(track),
      startInSeconds,
      endInSeconds,
      gain: 1,
      fadeInSeconds: 1.5,
      fadeOutSeconds: 2,
      loop,
      scenes: Array.from(
        { length: span.lastScene - span.firstScene + 1 },
        (_, i) => span.firstScene + i,
      ),
    });
    tracksUsed.set(track.id, track);
  }

  if (missing.size > 0) {
    notes.push(
      `cue(s) sem faixa no catálogo: ${Array.from(missing).join(", ")}`,
    );
  }

  return { cues, tracksUsed: Array.from(tracksUsed.values()), notes };
};
