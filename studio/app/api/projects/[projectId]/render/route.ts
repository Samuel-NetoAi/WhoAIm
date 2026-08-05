import { existsSync, mkdirSync, readFileSync } from "node:fs";
import path from "node:path";
import { NextResponse } from "next/server";
import { getProjectPaths } from "@/lib/projects/project-paths";
import { editPlanSchema } from "@/lib/edit-plan/schema";
import { buildShortPlan } from "@/lib/edit-plan/build-short-plan";
import { renderEditPlan } from "@/lib/render/render-composition";
import { createJob, updateJob } from "@/lib/render/job-store";

export async function POST(
  request: Request,
  context: { params: Promise<{ projectId: string }> },
) {
  const { projectId } = await context.params;
  const paths = getProjectPaths(projectId);

  if (!existsSync(paths.editPlanFile)) {
    return NextResponse.json(
      { error: "No edit plan yet — run analyze first" },
      { status: 404 },
    );
  }

  const body = await request.json().catch(() => ({}));
  const target: "full" | "short" = body?.target === "short" ? "short" : "full";
  const targetSeconds =
    typeof body?.targetSeconds === "number" && body.targetSeconds > 0
      ? body.targetSeconds
      : undefined;

  const fullPlan = editPlanSchema.parse(
    JSON.parse(readFileSync(paths.editPlanFile, "utf8")),
  );
  const editPlan =
    target === "short" ? buildShortPlan(fullPlan, targetSeconds) : fullPlan;

  mkdirSync(paths.rendersDir, { recursive: true });
  const jobId = crypto.randomUUID();
  const outputPath = path.join(
    paths.rendersDir,
    `${target}-${Date.now()}.mp4`,
  );

  createJob({
    id: jobId,
    projectId,
    target,
    status: "rendering",
    progress: 0,
    startedAt: Date.now(),
  });

  // Fire-and-forget: respond immediately with the job id, the client polls
  // GET .../render/[jobId] for progress instead of waiting on this request.
  renderEditPlan({
    editPlan,
    publicDir: path.join(paths.projectPath, "public"),
    outputLocation: outputPath,
    onProgress: (progress) => updateJob(jobId, { progress }),
  })
    .then(() => updateJob(jobId, { status: "done", progress: 1, outputPath }))
    .catch((error) =>
      updateJob(jobId, {
        status: "error",
        error: error instanceof Error ? error.message : "Unknown error",
      }),
    );

  return NextResponse.json({ jobId }, { status: 202 });
}
