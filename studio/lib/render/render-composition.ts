import path from "node:path";
import { bundle } from "@remotion/bundler";
import { renderMedia, renderStill, selectComposition } from "@remotion/renderer";
import type { EditPlan } from "@/lib/edit-plan/schema";

const ENTRY_POINT = path.join(process.cwd(), "remotion", "index.ts");

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
  });

  await renderMedia({
    composition,
    serveUrl,
    codec: "h264",
    outputLocation,
    inputProps,
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
  });

  await renderStill({
    composition,
    serveUrl,
    output: outputLocation,
    inputProps,
    frame,
  });
};
