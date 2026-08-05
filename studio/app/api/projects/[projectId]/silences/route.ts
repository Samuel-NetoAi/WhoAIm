import { existsSync, readFileSync } from "node:fs";
import { NextResponse } from "next/server";
import { getProjectPaths } from "@/lib/projects/project-paths";

export async function GET(
  request: Request,
  context: { params: Promise<{ projectId: string }> },
) {
  const { projectId } = await context.params;
  const { silencesFile } = getProjectPaths(projectId);

  if (!existsSync(silencesFile)) {
    return NextResponse.json({ silences: [] });
  }

  const silences = JSON.parse(readFileSync(silencesFile, "utf8"));
  return NextResponse.json({ silences });
}
