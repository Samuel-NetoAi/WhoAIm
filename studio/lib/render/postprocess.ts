import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import path from "node:path";

export type PostProcessOptions = {
  inputPath: string;
  // 30fps -> 60fps motion-compensated interpolation (minterpolate). CPU-bound
  // and slow (several minutes for a 5-minute video) but needs no extra
  // install. RIFE (AI) is the planned upgrade — see PLANO-ALPHA.md.
  interpolateTo60: boolean;
  // 2x lanczos upscale. Fast and sharp; Real-ESRGAN (AI) is the planned
  // upgrade for detail synthesis.
  upscale2x: boolean;
};

export const postProcessOutputPath = (inputPath: string): string => {
  const parsed = path.parse(inputPath);
  return path.join(parsed.dir, `${parsed.name}-post${parsed.ext}`);
};

// Full ffmpeg build shipped in studio\bin (the Remotion-bundled ffmpeg is a
// slim build without minterpolate/framerate filters). Falls back to
// `npx remotion ffmpeg` for upscale-only jobs if bin\ffmpeg.exe is missing.
const FULL_FFMPEG = path.join(process.cwd(), "bin", "ffmpeg.exe");

// Progress callback receives 0..1 estimated from ffmpeg's time= stderr lines.
export const postProcess = (
  options: PostProcessOptions,
  durationInSeconds: number,
  onProgress?: (progress: number) => void,
): Promise<string> => {
  const { inputPath, interpolateTo60, upscale2x } = options;
  if (!existsSync(inputPath)) {
    throw new Error(`Input not found: ${inputPath}`);
  }
  if (!interpolateTo60 && !upscale2x) {
    throw new Error("Nothing to do: enable interpolation and/or upscale");
  }

  const filters: string[] = [];
  if (interpolateTo60) {
    filters.push(
      "minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1",
    );
  }
  if (upscale2x) {
    filters.push("scale=iw*2:ih*2:flags=lanczos");
  }

  const useFullBinary = existsSync(FULL_FFMPEG);
  if (interpolateTo60 && !useFullBinary) {
    throw new Error(
      "Interpolação requer bin\\ffmpeg.exe (build completo) — ver PLANO-ALPHA.md",
    );
  }

  const outputPath = postProcessOutputPath(inputPath);
  const args = [
    ...(useFullBinary ? [] : ["remotion", "ffmpeg"]),
    "-y",
    "-i",
    inputPath,
    "-vf",
    filters.join(","),
    "-c:v",
    "libx264",
    "-crf",
    "18",
    "-preset",
    "medium",
    "-c:a",
    "copy",
    outputPath,
  ];

  return new Promise((resolve, reject) => {
    const child = useFullBinary
      ? spawn(FULL_FFMPEG, args, { cwd: process.cwd() })
      : spawn("npx", args, { cwd: process.cwd(), shell: true });
    let stderr = "";
    child.stderr.on("data", (chunk) => {
      const text = chunk.toString();
      stderr += text;
      const match = text.match(/time=(\d+):(\d+):(\d+(?:\.\d+)?)/);
      if (match && onProgress && durationInSeconds > 0) {
        const seconds =
          parseInt(match[1], 10) * 3600 +
          parseInt(match[2], 10) * 60 +
          parseFloat(match[3]);
        onProgress(Math.min(1, seconds / durationInSeconds));
      }
    });
    child.on("error", reject);
    child.on("close", (code) => {
      if (code === 0 && existsSync(outputPath)) {
        resolve(outputPath);
      } else {
        reject(new Error(`ffmpeg exited with ${code}: ${stderr.slice(-800)}`));
      }
    });
  });
};
