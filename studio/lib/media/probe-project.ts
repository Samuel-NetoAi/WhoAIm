import { readdirSync } from "node:fs";
import path from "node:path";
import { getMediaDuration, getVideoDimensions } from "./get-media-duration";
import { measureClipLoudness } from "./measure-loudness";

const VIDEO_EXTENSIONS = new Set([".mp4", ".mov", ".webm"]);
const AUDIO_EXTENSIONS = new Set([
  ".mp3",
  ".wav",
  ".m4a",
  ".mpeg",
  ".mpga",
  ".aac",
  ".ogg",
]);

export type ClipProbe = {
  id: string;
  file: string;
  absolutePath: string;
  durationInSeconds: number;
  width: number;
  height: number;
  // Integrated loudness (LUFS) of the clip's own audio track, from ffmpeg's
  // loudnorm filter — see measure-loudness.ts.
  loudnessLufs: number;
  // loudnessLufs min-max normalized against this project's OWN clips (0..1)
  // — "loud" is relative to what this footage actually contains, not an
  // absolute broadcast standard. Used by build-short-plan.ts to pick which
  // stretch of footage is the "best moment" for a Short.
  energyScore: number;
};

export type NarrationProbe = {
  file: string;
  absolutePath: string;
  durationInSeconds: number;
};

export type ProjectProbe = {
  clips: ClipProbe[];
  narration: NarrationProbe;
};

// Clips are named "1.mp4", "2.mp4", ... — sort numerically, not lexically
// ("10.mp4" must come after "9.mp4", not after "1.mp4"). Gaps (missing
// numbers) are expected and simply mean fewer clips than intended scenes.
const numericThenAlpha = (a: string, b: string): number => {
  const na = parseInt(a, 10);
  const nb = parseInt(b, 10);
  if (!Number.isNaN(na) && !Number.isNaN(nb)) return na - nb;
  return a.localeCompare(b);
};

export const probeProject = async (
  videosDir: string,
  audioDir: string,
): Promise<ProjectProbe> => {
  const videoFiles = readdirSync(videosDir)
    .filter((f) => VIDEO_EXTENSIONS.has(path.extname(f).toLowerCase()))
    .sort((a, b) => numericThenAlpha(path.parse(a).name, path.parse(b).name));

  if (videoFiles.length === 0) {
    throw new Error(`No video clips found in ${videosDir}`);
  }

  const clips: ClipProbe[] = [];
  for (const file of videoFiles) {
    const absolutePath = path.join(videosDir, file);
    const [durationInSeconds, dimensions, loudnessLufs] = await Promise.all([
      getMediaDuration(absolutePath),
      getVideoDimensions(absolutePath),
      measureClipLoudness(absolutePath),
    ]);
    clips.push({
      id: path.parse(file).name,
      file: `videos/${file}`,
      absolutePath,
      durationInSeconds,
      ...dimensions,
      loudnessLufs,
      energyScore: 0, // filled in below, once every clip's loudness is known
    });
  }

  const loudnessValues = clips.map((clip) => clip.loudnessLufs);
  const minDb = Math.min(...loudnessValues);
  const maxDb = Math.max(...loudnessValues);
  const spreadDb = maxDb - minDb;
  for (const clip of clips) {
    // All clips equally loud (or a single clip) carries no signal either
    // way — 0.5 keeps every window's average energy tied, so selection
    // falls back to picking by duration fit alone.
    clip.energyScore =
      spreadDb > 0.01 ? (clip.loudnessLufs - minDb) / spreadDb : 0.5;
  }

  const audioFiles = readdirSync(audioDir).filter((f) =>
    AUDIO_EXTENSIONS.has(path.extname(f).toLowerCase()),
  );
  if (audioFiles.length === 0) {
    throw new Error(`No narration audio file found in ${audioDir}`);
  }
  const narrationFile = audioFiles[0];
  const narrationAbsolutePath = path.join(audioDir, narrationFile);

  return {
    clips,
    narration: {
      file: `audio/${narrationFile}`,
      absolutePath: narrationAbsolutePath,
      durationInSeconds: await getMediaDuration(narrationAbsolutePath),
    },
  };
};
