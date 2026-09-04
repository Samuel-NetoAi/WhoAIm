import { existsSync } from "node:fs";
import path from "node:path";
import { NextResponse } from "next/server";
import { getProjectPaths } from "@/lib/projects/project-paths";
import {
  getMediaDuration,
  getVideoDimensions,
  getVideoFrameRate,
} from "@/lib/media/get-media-duration";
import {
  hasEnhancementWork,
  planEnhancement,
  postProcess,
} from "@/lib/render/postprocess";
import { createJob, updateJob } from "@/lib/render/job-store";
import { MINIMUM_SHORT_SIDE } from "@/lib/edit-plan/output-resolution";

// Post-processes an existing render (frame interpolation to 60fps and/or
// upscale to Full HD). Fire-and-forget like the render route: returns a
// jobId the client polls at .../render/[jobId]. Manual escape hatch — the
// primary path is per-clip enhancement before analyze
// (see app/api/projects/[projectId]/enhance-clips/route.ts). Protected by
// the same planEnhancement() idempotency check as that pipeline, so running
// this on a render whose clips were already enhanced degrades to a no-op
// instead of double-processing.
export async function POST(
  request: Request,
  context: { params: Promise<{ projectId: string }> },
) {
  const { projectId } = await context.params;
  const { rendersDir } = getProjectPaths(projectId);

  const body = await request.json().catch(() => ({}));
  const filename = typeof body?.filename === "string" ? body.filename : "";
  const interpolateTo60 = body?.interpolateTo60 === true;
  const upscale = body?.upscale === true;

  if (!filename || (!interpolateTo60 && !upscale)) {
    return NextResponse.json(
      { error: "filename e ao menos uma opção (interpolateTo60/upscale)" },
      { status: 400 },
    );
  }

  const inputPath = path.join(rendersDir, path.basename(filename));
  if (!existsSync(inputPath)) {
    return NextResponse.json({ error: "Render não encontrado" }, { status: 404 });
  }

  const [durationInSeconds, dimensions, fps] = await Promise.all([
    getMediaDuration(inputPath),
    getVideoDimensions(inputPath),
    getVideoFrameRate(inputPath),
  ]);

  const plan = planEnhancement(
    {
      interpolateTo60,
      upscaleTargetShortSide: upscale ? MINIMUM_SHORT_SIDE : undefined,
    },
    { ...dimensions, fps },
  );

  const jobId = crypto.randomUUID();
  createJob({
    id: jobId,
    projectId,
    target: "post",
    status: "rendering",
    progress: 0,
    startedAt: Date.now(),
  });

  if (!hasEnhancementWork(plan)) {
    updateJob(jobId, { status: "done", progress: 1, outputPath: inputPath });
    return NextResponse.json({ jobId }, { status: 202 });
  }

  postProcess(
    {
      inputPath,
      ...plan,
      currentWidth: dimensions.width,
      currentHeight: dimensions.height,
    },
    durationInSeconds,
    (progress) => updateJob(jobId, { progress }),
  )
    .then((outputPath) =>
      updateJob(jobId, { status: "done", progress: 1, outputPath }),
    )
    .catch((error) =>
      updateJob(jobId, {
        status: "error",
        error: error instanceof Error ? error.message : "Unknown error",
      }),
    );

  return NextResponse.json({ jobId }, { status: 202 });
}
