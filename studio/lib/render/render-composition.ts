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
// three-clip test project.
const MOUNT_TIMEOUT_MS = 120_000;

// bundle() copies the given publicDir's contents into the output bundle, so
// a fresh bundle is needed whenever the project (and therefore its public
// dir) changes. Renders of the same project back-to-back reuse the bundle.
let cachedServeUrl: string | null = null;
let cachedPublicDir: string | null = null;

const getServeUrl = async (publicDir: string): Promise<string> => {
  if (cachedServeUrl && cachedPublicDir === publicDir) {
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
