import { NextResponse } from "next/server";
import { getProjectPaths } from "@/lib/projects/project-paths";
import { enhanceProjectClips } from "@/lib/media/enhance-clips";
import { createJob, updateJob } from "@/lib/render/job-store";
import { MINIMUM_SHORT_SIDE } from "@/lib/edit-plan/output-resolution";

// Enhances every raw clip in the project (upscale to Full HD and/or
// interpolate to 60fps) BEFORE analyze runs, so the EditPlan's clip
// durations are measured from the final, already-enhanced files — never
// stale (see PLANO B / lib/media/enhance-clips.ts for why placement here,
// not on the final render, matters). Fire-and-forget like the render route:
// returns a jobId the client polls at .../render/[jobId].
export async function POST(
  request: Request,
  context: { params: Promise<{ projectId: string }> },
) {
  const { projectId } = await context.params;
  const { videosDir } = getProjectPaths(projectId);

  const body = await request.json().catch(() => ({}));
  const interpolateTo60 = body?.interpolateTo60 === true;
  const upscale = body?.upscale === true;

  if (!interpolateTo60 && !upscale) {
    return NextResponse.json(
      { error: "ao menos uma opção (interpolateTo60/upscale)" },
      { status: 400 },
    );
  }

  const jobId = crypto.randomUUID();
  createJob({
    id: jobId,
    projectId,
    target: "enhance",
    status: "rendering",
    progress: 0,
    startedAt: Date.now(),
  });

  enhanceProjectClips(
    videosDir,
    { interpolateTo60, upscaleTargetShortSide: upscale ? MINIMUM_SHORT_SIDE : undefined },
    ({ clipsDone, totalClips }) =>
      updateJob(jobId, {
        progress: totalClips > 0 ? clipsDone / totalClips : 0,
        currentClip: clipsDone,
        totalClips,
      }),
  )
    .then(({ enhanced, skipped, totalClips }) =>
      updateJob(jobId, {
        status: "done",
        progress: 1,
        currentClip: totalClips,
        totalClips,
        // Reused as a human-readable summary; the render/[jobId] client
        // already only reads outputPath as an opaque string.
        outputPath: `${enhanced} melhorado(s), ${skipped} já estava(m) no padrão`,
      }),
    )
    .catch((error) =>
      updateJob(jobId, {
        status: "error",
        error: error instanceof Error ? error.message : "Unknown error",
      }),
    );

  return NextResponse.json({ jobId }, { status: 202 });
}
