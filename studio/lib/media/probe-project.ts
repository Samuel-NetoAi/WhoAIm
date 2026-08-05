import { readdirSync } from "node:fs";
import path from "node:path";
import { getMediaDuration, getVideoDimensions } from "./get-media-duration";

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
    const [durationInSeconds, dimensions] = await Promise.all([
      getMediaDuration(absolutePath),
      getVideoDimensions(absolutePath),
    ]);
    clips.push({
      id: path.parse(file).name,
      file: `videos/${file}`,
      absolutePath,
      durationInSeconds,
      ...dimensions,
    });
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
