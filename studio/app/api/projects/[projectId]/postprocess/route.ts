import { existsSync } from "node:fs";
import path from "node:path";
import { NextResponse } from "next/server";
import { getProjectPaths } from "@/lib/projects/project-paths";
import { getMediaDuration } from "@/lib/media/get-media-duration";
import { postProcess } from "@/lib/render/postprocess";
import { createJob, updateJob } from "@/lib/render/job-store";

// Post-processes an existing render (frame interpolation to 60fps and/or
// 2x upscale). Fire-and-forget like the render route: returns a jobId the
// client polls at .../render/[jobId].
export async function POST(
  request: Request,
  context: { params: Promise<{ projectId: string }> },
) {
  const { projectId } = await context.params;
  const { rendersDir } = getProjectPaths(projectId);

  const body = await request.json().catch(() => ({}));
  const filename = typeof body?.filename === "string" ? body.filename : "";
  const interpolateTo60 = body?.interpolateTo60 === true;
  const upscale2x = body?.upscale2x === true;

  if (!filename || (!interpolateTo60 && !upscale2x)) {
    return NextResponse.json(
      { error: "filename e ao menos uma opção (interpolateTo60/upscale2x)" },
      { status: 400 },
    );
  }

  const inputPath = path.join(rendersDir, path.basename(filename));
  if (!existsSync(inputPath)) {
    return NextResponse.json({ error: "Render não encontrado" }, { status: 404 });
  }

  const durationInSeconds = await getMediaDuration(inputPath);

  const jobId = crypto.randomUUID();
  createJob({
    id: jobId,
    projectId,
    target: "post",
    status: "rendering",
    progress: 0,
    startedAt: Date.now(),
  });

  postProcess(
    { inputPath, interpolateTo60, upscale2x },
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
