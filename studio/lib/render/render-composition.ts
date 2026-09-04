import path from "node:path";
import { bundle } from "@remotion/bundler";
import { renderMedia, renderStill, selectComposition } from "@remotion/renderer";
import type { EditPlan } from "@/lib/edit-plan/schema";

const ENTRY_POINT = path.join(process.cwd(), "remotion", "index.ts");

// The shader-backed transitions (film-burn, ripple, dreamy-zoom, linear-blur)
// draw through WebGL2, which headless Chrome does not provide with its default
// renderer: the render hung and died on "Timeout exceeded rendering the
// component initially". ANGLE is Chrome's normal GL backend and fixes it —
// measured here, it also made those transitions render faster than the plain
// crossfade. "swiftshader" is NOT a substitute: it fails outright with
// "Failed to create WebGL2 context".
const CHROMIUM_OPTIONS = { gl: "angle" } as const;

// Mounting a 1080p composition with many clips takes longer than Remotion's
// 30s default, and that default was already within seconds of failing on a
// three-clip test project. 300s is generous headroom for that legitimate
// mount cost, and that is the ONLY thing this constant buys.
//
// CORRECTED 04/09/2026 — this comment used to claim that raising it from
// 120s to 300s was "the right fix" for the enhanced-clip hang. It is not,
// and the evidence was already written down in
// PENDENTE-FASE4-render-hang.md before the claim was made: with 300s the
// render fails with the SAME "Timeout while extracting frame at time
// 0.1sec" error, just 180s later, and with zero progress in between. A
// slow mount shows progress and then finishes; this one hangs. Raising a
// timeout never fixes a hang, it only postpones the message.
//
// What is actually known:
//   - Trigger: SOURCE clips produced by lib/media/enhance-clips.ts
//     (upscaled to 1080p and/or interpolated to 60fps). Raw 480p clips from
//     phase 3 render fine — that is why the automatic phase 4
//     (pipeline.py:_run_edicao) deliberately skips enhancement.
//   - Already ruled out: the timeout itself (120s and 300s, same error) and
//     B-frames (`-bf 0` re-encode, same error).
//   - `timeoutInMilliseconds` here IS the delayRender timeout that covers
//     frame extraction, so there is no separate renderMedia knob to reach
//     for — the old comment's last clause was wrong about that too.
//
// Strongest untested lead: remotion/Clip.tsx uses <Video> from
// @remotion/media, which decodes through WebCodecs in headless Chromium.
// Swapping to core Remotion's <OffthreadVideo> (FFmpeg-based) for the
// enhanced path would sidestep WebCodecs entirely and would say in one
// render whether the decoder is the culprit. Not done here because it needs
// a real render to validate, and shipping an unverified swap is how the
// wrong claim above got written in the first place.
const MOUNT_TIMEOUT_MS = 300_000;

// bundle() copies the given publicDir's contents into the output bundle, so
// a fresh bundle is needed whenever the project (and therefore its public
// dir) changes. Renders of the same project back-to-back reuse the bundle.
//
// The cache is keyed ONLY on publicDir, which means it does not notice the
// composition's own SOURCE changing. In production that is right — the code
// cannot change without the process restarting. In development it is a trap
// that cost a real debugging detour on 04/09/2026: a fix to remotion/
// Captions.tsx was rendered twice, produced a byte-for-byte identical frame
// both times, and looked like a broken fix when it was a stale bundle. Next's
// hot reload swaps the API route's module and leaves this module-level cache
// untouched, so nothing visible says the render is running old code.
const IS_DEV = process.env.NODE_ENV !== "production";
let cachedServeUrl: string | null = null;
let cachedPublicDir: string | null = null;

const getServeUrl = async (publicDir: string): Promise<string> => {
  if (!IS_DEV && cachedServeUrl && cachedPublicDir === publicDir) {
    return cachedServeUrl;
  }
  cachedServeUrl = await bundle({ entryPoint: ENTRY_POINT, publicDir });
  cachedPublicDir = publicDir;
  return cachedServeUrl;
};

export const renderEditPlan = async ({
  editPlan,
  publicDir,
  outputLocation,
  onProgress,
}: {
  editPlan: EditPlan;
  publicDir: string;
  outputLocation: string;
  onProgress?: (progress: number) => void;
}): Promise<void> => {
  const serveUrl = await getServeUrl(publicDir);
  const inputProps = { editPlan };

  const composition = await selectComposition({
    serveUrl,
    id: "EditedVideo",
    inputProps,
    chromiumOptions: CHROMIUM_OPTIONS,
    timeoutInMilliseconds: MOUNT_TIMEOUT_MS,
  });

  await renderMedia({
    composition,
    serveUrl,
    codec: "h264",
    outputLocation,
    inputProps,
    chromiumOptions: CHROMIUM_OPTIONS,
    timeoutInMilliseconds: MOUNT_TIMEOUT_MS,
    onProgress: ({ progress }) => onProgress?.(progress),
  });
};

// Used by verification scripts to spot-check a specific frame without a
// full render (the same technique used manually for the Medusa edit).
export const renderEditPlanStill = async ({
  editPlan,
  publicDir,
  outputLocation,
  frame,
}: {
  editPlan: EditPlan;
  publicDir: string;
  outputLocation: string;
  frame: number;
}): Promise<void> => {
  const serveUrl = await getServeUrl(publicDir);
  const inputProps = { editPlan };

  const composition = await selectComposition({
    serveUrl,
    id: "EditedVideo",
    inputProps,
    chromiumOptions: CHROMIUM_OPTIONS,
    timeoutInMilliseconds: MOUNT_TIMEOUT_MS,
  });

  await renderStill({
    composition,
    serveUrl,
    output: outputLocation,
    inputProps,
    frame,
    chromiumOptions: CHROMIUM_OPTIONS,
    timeoutInMilliseconds: MOUNT_TIMEOUT_MS,
  });
};
