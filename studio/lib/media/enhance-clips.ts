import { copyFileSync, existsSync, mkdirSync, renameSync } from "node:fs";
import path from "node:path";
import { listVideoFiles } from "./probe-project";
import {
  getMediaDuration,
  getVideoDimensions,
  getVideoFrameRate,
} from "./get-media-duration";
import {
  hasEnhancementWork,
  planEnhancement,
  postProcess,
  type EnhancementPlan,
} from "@/lib/render/postprocess";

export type EnhanceProgress = {
  clipsDone: number;
  totalClips: number;
  currentFile?: string;
};

export type EnhanceResult = {
  enhanced: number;
  skipped: number;
  totalClips: number;
};

// Small hand-rolled concurrency pool — no new dependency, consistent with
// this codebase's preference elsewhere (job-store.ts is a plain Map, not a
// queue library). Start at 2: minterpolate is itself CPU/memory-bandwidth
// heavy per process, so this is unlikely to scale linearly with core count —
// measure with a real batch before raising it (see PLANO B verification).
const CONCURRENCY = 2;

const runPool = async <T>(
  items: T[],
  worker: (item: T) => Promise<void>,
): Promise<void> => {
  let index = 0;
  const next = async (): Promise<void> => {
    while (index < items.length) {
      const item = items[index++];
      await worker(item);
    }
  };
  await Promise.all(
    Array.from({ length: Math.min(CONCURRENCY, items.length) }, () => next()),
  );
};

const sleep = (ms: number): Promise<void> =>
  new Promise((resolve) => setTimeout(resolve, ms));

// Windows can refuse to rename OVER an existing file if something else
// (Next dev's file watcher on public/, a browser tab still holding a
// connection to it, antivirus) has it open at that exact instant —
// confirmed for real running this against the dev server (EPERM on
// "rename ... -> 3.mp4"). The lock is transient in practice; a short retry
// clears it without needing to identify the holder. POSIX systems don't
// have this failure mode (rename succeeds even over an open file), so this
// only ever loops on Windows in the first place.
const renameWithRetry = async (
  from: string,
  to: string,
  attempts = 5,
): Promise<void> => {
  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    try {
      renameSync(from, to);
      return;
    } catch (error) {
      const isLastAttempt = attempt === attempts;
      const isPermissionIssue =
        error instanceof Error && "code" in error && error.code === "EPERM";
      if (isLastAttempt || !isPermissionIssue) throw error;
      await sleep(300 * attempt);
    }
  }
};

// Enhances every raw clip in videosDir IN PLACE, before it ever enters the
// EditPlan. This is the whole point (see PLANO B): probeProject()/analyze
// measures real on-disk duration/dimensions AFTER this runs, so the
// EditPlan's timing is correct from the moment it's written — narration and
// music (both timed as global tracks against EditPlan cutPoints, not against
// any one clip's own duration) never see a stale number. Doing this earlier
// than analyze, rather than post-render, structurally eliminates the
// audio/video desync class of bug instead of patching it after the fact.
export const enhanceProjectClips = async (
  videosDir: string,
  requested: EnhancementPlan,
  onProgress?: (progress: EnhanceProgress) => void,
): Promise<EnhanceResult> => {
  const files = listVideoFiles(videosDir);
  if (files.length === 0) {
    throw new Error(`No video clips found in ${videosDir}`);
  }

  // Sibling of videosDir (public/videos), not inside it — keeps the
  // preserved originals out of anything that scans videosDir for clips.
  const backupDir = path.join(path.dirname(videosDir), "videos-original");
  mkdirSync(backupDir, { recursive: true });

  let clipsDone = 0;
  let enhanced = 0;
  let skipped = 0;

  await runPool(files, async (file) => {
    const absolutePath = path.join(videosDir, file);
    const [duration, dimensions, fps] = await Promise.all([
      getMediaDuration(absolutePath),
      getVideoDimensions(absolutePath),
      getVideoFrameRate(absolutePath),
    ]);

    const plan = planEnhancement(requested, { ...dimensions, fps });

    if (hasEnhancementWork(plan)) {
      // Preserve the true original once, before the first modification.
      // Re-running enhancement later (e.g. clip regenerated under the same
      // filename) must never let an already-enhanced file masquerade as the
      // original.
      const backupPath = path.join(backupDir, file);
      if (!existsSync(backupPath)) {
        copyFileSync(absolutePath, backupPath);
      }

      const outputPath = await postProcess(
        {
          inputPath: absolutePath,
          ...plan,
          currentWidth: dimensions.width,
          currentHeight: dimensions.height,
        },
        duration,
      );
      // Same directory, different filename (postProcessOutputPath appends
      // "-post") — a plain rename is atomic on the same volume and safe to
      // run concurrently across different clips. Retries because Windows
      // can transiently lock the destination (see renameWithRetry).
      await renameWithRetry(outputPath, absolutePath);
      enhanced += 1;
    } else {
      skipped += 1;
    }

    clipsDone += 1;
    onProgress?.({ clipsDone, totalClips: files.length, currentFile: file });
  });

  return { enhanced, skipped, totalClips: files.length };
};
