import { DEV_NULL, runRemotionFfmpeg } from "./run-ffmpeg";

export type Silence = { start: number; end: number };

const parseLoudnormThreshold = (output: string): number => {
  const match = output.match(/\{[\s\S]*?"input_thresh"[\s\S]*?\}/);
  if (!match) {
    throw new Error("Could not parse loudnorm output for input_thresh");
  }
  const parsed = JSON.parse(match[0]) as { input_thresh: string };
  return parseFloat(parsed.input_thresh);
};

const parseSilences = (output: string, totalDurationSeconds: number): Silence[] => {
  const silences: Silence[] = [];
  let pendingStart: number | null = null;

  for (const line of output.split("\n")) {
    const startMatch = line.match(/silence_start:\s*(-?[\d.]+)/);
    if (startMatch) {
      pendingStart = parseFloat(startMatch[1]);
      continue;
    }
    const endMatch = line.match(/silence_end:\s*(-?[\d.]+)/);
    if (endMatch && pendingStart !== null) {
      silences.push({ start: pendingStart, end: parseFloat(endMatch[1]) });
      pendingStart = null;
    }
  }

  // Trailing silence that runs to EOF sometimes has no silence_end line.
  if (pendingStart !== null) {
    silences.push({ start: pendingStart, end: totalDurationSeconds });
  }

  return silences;
};

// Adaptive silence detection (see the `silence-detection` skill): measure
// integrated loudness first, then use its gating threshold for silencedetect
// instead of a fixed dB guess, since narration recordings vary a lot in gain.
export const detectSilences = async (
  audioAbsolutePath: string,
  totalDurationSeconds: number,
  minSilenceDuration = 0.5,
): Promise<Silence[]> => {
  const loudnormOutput = await runRemotionFfmpeg([
    "-i",
    audioAbsolutePath,
    "-map",
    "0:a",
    "-af",
    "loudnorm=print_format=json",
    "-f",
    "null",
    DEV_NULL,
  ]);
  const threshold = parseLoudnormThreshold(loudnormOutput);

  const silenceOutput = await runRemotionFfmpeg([
    "-i",
    audioAbsolutePath,
    "-map",
    "0:a",
    "-af",
    `silencedetect=noise=${threshold}dB:d=${minSilenceDuration}`,
    "-f",
    "null",
    DEV_NULL,
  ]);

  return parseSilences(silenceOutput, totalDurationSeconds);
};
