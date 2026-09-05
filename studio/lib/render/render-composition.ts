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
// This constant is NOT what fixed the enhanced-clip render hang, and an
// earlier version of this comment claiming it was is the reason the bug
// stayed open from 19/08 to 04/09/2026. Reproduced on 04/09 with the exact
// conditions: 300s of ZERO progress, then "Timeout while extracting frame at
// time 0.13sec". A slow mount climbs and finishes; that one never moved.
// Raising a timeout never fixes a hang, it only postpones the message.
//
// The actual cause was the DECODER: remotion/Clip.tsx used <Video> from
// @remotion/media (WebCodecs in headless Chromium), which cannot decode the
// encode that lib/media/enhance-clips.ts produces. Switching to core
// Remotion's <OffthreadVideo> (FFmpeg) renders the same clips in ~60s. The
// measurements are in Clip.tsx, next to the decision they justify.
//
// Also ruled out along the way: B-frames (`-bf 0` re-encode, same error) and
// the idea that some other renderMedia knob was the right place to raise —
// `timeoutInMilliseconds` here IS the delayRender timeout covering frame
// extraction, so there was never a second knob to find.
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
