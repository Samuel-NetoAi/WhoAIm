import { NextResponse } from "next/server";
import { listProjects } from "@/lib/projects/list-projects";
import { createProject } from "@/lib/projects/create-project";

export async function GET() {
  return NextResponse.json({ projects: listProjects() });
}

export async function POST(request: Request) {
  const body = await request.json().catch(() => null);
  const creatureName =
    typeof body?.creatureName === "string" ? body.creatureName : "";

  try {
    const { id } = createProject(creatureName);
    return NextResponse.json({ id }, { status: 201 });
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Unknown error" },
      { status: 400 },
    );
  }
}
