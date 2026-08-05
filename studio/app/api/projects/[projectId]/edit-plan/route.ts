import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { NextResponse } from "next/server";
import { getProjectPaths } from "@/lib/projects/project-paths";
import { editPlanSchema } from "@/lib/edit-plan/schema";

export async function GET(
  request: Request,
  context: { params: Promise<{ projectId: string }> },
) {
  const { projectId } = await context.params;
  const { editPlanFile } = getProjectPaths(projectId);

  if (!existsSync(editPlanFile)) {
    return NextResponse.json(
      { error: "No edit plan yet — run analyze first" },
      { status: 404 },
    );
  }

  const editPlan = JSON.parse(readFileSync(editPlanFile, "utf8"));
  return NextResponse.json({ editPlan });
}

export async function PUT(
  request: Request,
  context: { params: Promise<{ projectId: string }> },
) {
  const { projectId } = await context.params;
  const { editPlanFile } = getProjectPaths(projectId);

  const body = await request.json();
  const parsed = editPlanSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json(
      { error: parsed.error.flatten() },
      { status: 400 },
    );
  }

  writeFileSync(editPlanFile, JSON.stringify(parsed.data, null, 2));
  return NextResponse.json({ editPlan: parsed.data });
}
