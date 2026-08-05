import { mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import { NextResponse } from "next/server";
import AdmZip from "adm-zip";
import { getProjectPaths } from "@/lib/projects/project-paths";

const VIDEO_EXTENSIONS = new Set([".mp4", ".mov", ".webm"]);

export async function POST(
  request: Request,
  context: { params: Promise<{ projectId: string }> },
) {
  const { projectId } = await context.params;
  const { videosDir, audioDir } = getProjectPaths(projectId);

  const formData = await request.formData();

  let clipsAdded = 0;
  const zipFile = formData.get("videosZip");
  if (zipFile instanceof File) {
    const buffer = Buffer.from(await zipFile.arrayBuffer());
    const zip = new AdmZip(buffer);
    mkdirSync(videosDir, { recursive: true });
    for (const entry of zip.getEntries()) {
      if (entry.isDirectory) continue;
      const ext = path.extname(entry.entryName).toLowerCase();
      if (!VIDEO_EXTENSIONS.has(ext)) continue;
      // Flatten any folder structure inside the zip — we only care about
      // the numbered filenames, not where they sat inside the archive.
      const fileName = path.basename(entry.entryName);
      writeFileSync(path.join(videosDir, fileName), entry.getData());
      clipsAdded += 1;
    }
  }

  let narrationSaved = false;
  const narrationFile = formData.get("narration");
  if (narrationFile instanceof File) {
    mkdirSync(audioDir, { recursive: true });
    const buffer = Buffer.from(await narrationFile.arrayBuffer());
    writeFileSync(path.join(audioDir, narrationFile.name), buffer);
    narrationSaved = true;
  }

  return NextResponse.json({ clipsAdded, narrationSaved });
}
