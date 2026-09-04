import { spawn } from "node:child_process";
import { existsSync, renameSync, unlinkSync } from "node:fs";
import path from "node:path";
import { getMediaDuration } from "@/lib/media/get-media-duration";

export type EnhancementPlan = {
  // 24/30fps -> 60fps motion-compensated interpolation (minterpolate). CPU-bound
  // and slow (measured ~79s for a 15s/480p clip) but needs no extra install.
  // RIFE (AI) is the planned upgrade — see PLANO-ALPHA.md.
  interpolateTo60: boolean;
  // Target SHORT side in pixels (e.g. 1080 for Full HD), aspect-preserving.
  // Undefined/omitted = no upscale. Replaces the old fixed-2x multiplier,
  // which landed a real 480p clip (864x496) at 1728x992 — short of true
  // Full HD. Fast and sharp (Lanczos); Real-ESRGAN (AI) is the planned
  // upgrade for real detail synthesis (this never invents detail).
  upscaleTargetShortSide?: number;
};

export type ClipState = {
  width: number;
  height: number;
  fps: number;
};

export type PostProcessOptions = EnhancementPlan & {
  inputPath: string;
  // Required when upscaleTargetShortSide is set (picks scale orientation).
  // Irrelevant/omittable otherwise.
  currentWidth?: number;
  currentHeight?: number;
};

// A clip counts as "already smooth" a hair under 60 to tolerate 59.94-style
// NTSC-ish rates without triggering a pointless re-interpolation pass.
const FPS_ALREADY_SMOOTH = 58.5;

// Given what the caller WANTS and what the clip ALREADY IS (from a real
// probe — see lib/media/get-media-duration.ts), returns only the work still
// actually needed: never upscales a clip already at/above the target, never
// re-interpolates a clip already near 60fps (running minterpolate twice
// doesn't add detail — it compounds motion-interpolation artifacts on
// already-synthetic frames). Pure function, no I/O, so both callers (the
// manual whole-render /postprocess route and the per-clip enhancement
// pipeline) share the exact same skip decision instead of each
// implementing — and possibly disagreeing on — their own.
export const planEnhancement = (
  requested: EnhancementPlan,
  current: ClipState,
): EnhancementPlan => {
  const shortSide = Math.min(current.width, current.height);
  return {
    interpolateTo60: requested.interpolateTo60 && current.fps < FPS_ALREADY_SMOOTH,
    upscaleTargetShortSide:
      requested.upscaleTargetShortSide != null &&
      shortSide < requested.upscaleTargetShortSide
        ? requested.upscaleTargetShortSide
        : undefined,
  };
};

export const hasEnhancementWork = (plan: EnhancementPlan): boolean =>
  plan.interpolateTo60 || plan.upscaleTargetShortSide != null;

export const postProcessOutputPath = (inputPath: string): string => {
  const parsed = path.parse(inputPath);
  return path.join(parsed.dir, `${parsed.name}-post${parsed.ext}`);
};

// Full ffmpeg build shipped in studio\bin (the Remotion-bundled ffmpeg is a
// slim build without minterpolate/framerate filters). Falls back to
// `npx remotion ffmpeg` for upscale-only jobs if bin\ffmpeg.exe is missing.
const FULL_FFMPEG = path.join(process.cwd(), "bin", "ffmpeg.exe");

// A single ffmpeg invocation. Progress callback receives 0..1 estimated from
// ffmpeg's time= stderr lines.
const runFfmpeg = (
  args: string[],
  useFullBinary: boolean,
  outputPath: string,
  durationInSeconds: number,
  onProgress?: (progress: number) => void,
): Promise<string> =>
  new Promise((resolve, reject) => {
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

// How close is "close enough" before spending a second encode pass to fix it
// — one output frame at 60fps.
const DURATION_TOLERANCE_SECONDS = 1 / 60;

// Callers MUST run `planEnhancement` first and skip calling this entirely
// when `hasEnhancementWork` is false for the reduced plan — this function
// does not re-check current clip state itself (it has no I/O), so calling it
// with a plan that's already satisfied just wastes an ffmpeg pass.
export const postProcess = async (
  options: PostProcessOptions,
  durationInSeconds: number,
  onProgress?: (progress: number) => void,
): Promise<string> => {
  const { inputPath, interpolateTo60, upscaleTargetShortSide } = options;
  if (!existsSync(inputPath)) {
    throw new Error(`Input not found: ${inputPath}`);
  }
  if (!hasEnhancementWork(options)) {
    throw new Error("Nothing to do: enable interpolation and/or upscale");
  }

  const filters: string[] = [];
  if (interpolateTo60) {
    filters.push(
      "minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1",
    );
  }
  if (upscaleTargetShortSide != null) {
    if (options.currentWidth == null || options.currentHeight == null) {
      throw new Error(
        "upscaleTargetShortSide requires currentWidth/currentHeight (from a real probe)",
      );
    }
    const target = upscaleTargetShortSide;
    const isLandscape = options.currentWidth >= options.currentHeight;
    // "-2" (not "-1") keeps the computed dimension even — h264 rejects odd
    // dimensions outright.
    filters.push(
      isLandscape ? `scale=-2:${target}:flags=lanczos` : `scale=${target}:-2:flags=lanczos`,
    );
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

  await runFfmpeg(args, useFullBinary, outputPath, durationInSeconds, onProgress);

  // Upscale-only never touches timing (confirmed empirically — a spatial
  // resize doesn't change frame count). Nothing left to correct.
  if (!interpolateTo60) {
    return outputPath;
  }

  // minterpolate's fps conversion does NOT reliably reproduce the source
  // duration — measured drift of ~75-90ms on a real 15s clip, from internal
  // frame-count rounding (not a fixed constant; varies with content/length,
  // so this is measured per-run, never assumed). Audio is `-c:a copy` above
  // and therefore never moves — an uncorrected drift here silently desyncs
  // audio from video. Tried and REJECTED first: `tpad` tail-padding +
  // `-t <duration>` trim — empirically the `-t` output flag discarded the
  // padded frames instead of trimming down to them (reproduced twice; not a
  // fluke). `-frames:v <N>` hits the requested frame count exactly but the
  // container-level duration still didn't match nb_frames/fps cleanly
  // (encoder start-time/delay artifact), so frame-count targeting doesn't
  // solve it either. What DOES work, verified: measure the real output
  // duration, then run a second, fast, encode-only pass that rescales
  // presentation timestamps by the exact ratio needed
  // (`setpts=(target/actual)*PTS`, forcing `-r 60` to resample onto the new
  // timeline) — this closed a 75ms drift down to 8ms in testing. It's a
  // sub-1% speed change, imperceptible, and doesn't depend on understanding
  // *why* minterpolate drifted in the first place.
  const actualDuration = await getMediaDuration(outputPath);
  const drift = Math.abs(actualDuration - durationInSeconds);
  if (drift <= DURATION_TOLERANCE_SECONDS) {
    return outputPath;
  }

  const scale = durationInSeconds / actualDuration;
  const retimedPath = path.join(
    path.dirname(outputPath),
    `${path.parse(outputPath).name}-retimed${path.extname(outputPath)}`,
  );
  const retimeArgs = [
    ...(useFullBinary ? [] : ["remotion", "ffmpeg"]),
    "-y",
    "-i",
    outputPath,
    "-vf",
    `setpts=${scale}*PTS`,
    "-r",
    "60",
    "-c:v",
    "libx264",
    "-crf",
    "18",
    "-preset",
    "medium",
    "-c:a",
    "copy",
    retimedPath,
  ];
  await runFfmpeg(retimeArgs, useFullBinary, retimedPath, durationInSeconds);
  unlinkSync(outputPath);
  renameSync(retimedPath, outputPath);
  return outputPath;
};
