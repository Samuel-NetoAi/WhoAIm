import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { NextResponse } from "next/server";
import { getProjectPaths } from "@/lib/projects/project-paths";

// Persists the pre-production phases next to the project itself:
// dossie (fase 0 / pesquisa-seres), roteiro (fase 1 / whoiam),
// prompts (fase 2 / model sheets + storyboards + SeeDance).
const ALLOWED_NOTES = new Set(["dossie", "roteiro", "prompts"]);

const notePath = (projectId: string, noteName: string): string | null => {
  if (!ALLOWED_NOTES.has(noteName)) return null;
  const { projectPath } = getProjectPaths(projectId);
  return path.join(projectPath, "notes", `${noteName}.md`);
};

export async function GET(
  request: Request,
  context: { params: Promise<{ projectId: string; noteName: string }> },
) {
  const { projectId, noteName } = await context.params;
  const filePath = notePath(projectId, noteName);
  if (!filePath) {
    return NextResponse.json({ error: "Nota inválida" }, { status: 400 });
  }
  const content = existsSync(filePath) ? readFileSync(filePath, "utf8") : "";
  return NextResponse.json({ content });
}

export async function PUT(
  request: Request,
  context: { params: Promise<{ projectId: string; noteName: string }> },
) {
  const { projectId, noteName } = await context.params;
  const filePath = notePath(projectId, noteName);
  if (!filePath) {
    return NextResponse.json({ error: "Nota inválida" }, { status: 400 });
  }
  const body = await request.json().catch(() => ({}));
  const content = typeof body?.content === "string" ? body.content : null;
  if (content === null) {
    return NextResponse.json({ error: "content obrigatório" }, { status: 400 });
  }
  mkdirSync(path.dirname(filePath), { recursive: true });
  writeFileSync(filePath, content, "utf8");
  return NextResponse.json({ saved: true });
}
