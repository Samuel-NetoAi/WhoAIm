import { mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import { NextResponse } from "next/server";
import AdmZip from "adm-zip";
import { getProjectPaths } from "@/lib/projects/project-paths";
import { extractAudioTrack, splitVideoIntoClips } from "@/lib/media/split-video";
import { DEFAULT_SHORT_TARGET_SECONDS } from "@/lib/edit-plan/build-short-plan";

const VIDEO_EXTENSIONS = new Set([".mp4", ".mov", ".webm"]);

export async function POST(
  request: Request,
  context: { params: Promise<{ projectId: string }> },
) {
  const { projectId } = await context.params;
  const { videosDir, audioDir, sourceDir } = getProjectPaths(projectId);

  const formData = await request.formData();

  const zipFile = formData.get("videosZip");
  const videoFile = formData.get("video");
  if (zipFile instanceof File && videoFile instanceof File) {
    return NextResponse.json(
      {
        error:
          "Envie um zip de clipes numerados OU um vídeo completo, não os dois",
      },
      { status: 400 },
    );
  }

  let clipsAdded = 0;
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

  // A single already-edited episode instead of pre-cut clips: split it into
  // the same numbered-clip shape the rest of the Studio expects (see
  // split-video.ts), and — when no separate narration was uploaded — use the
  // video's own audio track as the narration, since there is no other voice
  // to align cuts against.
  if (videoFile instanceof File) {
    mkdirSync(sourceDir, { recursive: true });
    const ext = path.extname(videoFile.name) || ".mp4";
    const sourcePath = path.join(sourceDir, `episode${ext}`);
    writeFileSync(sourcePath, Buffer.from(await videoFile.arrayBuffer()));

    const segmentSecondsRaw = formData.get("segmentSeconds");
    const segmentSeconds =
      typeof segmentSecondsRaw === "string" && Number(segmentSecondsRaw) > 0
        ? Number(segmentSecondsRaw)
        : DEFAULT_SHORT_TARGET_SECONDS;

    try {
      clipsAdded = await splitVideoIntoClips(sourcePath, videosDir, segmentSeconds);
      if (!narrationSaved) {
        await extractAudioTrack(sourcePath, audioDir, "episode.m4a");
        narrationSaved = true;
      }
    } catch (error) {
      return NextResponse.json(
        {
          error:
            error instanceof Error
              ? `Falha ao processar o vídeo: ${error.message}`
              : "Falha ao processar o vídeo completo",
        },
        { status: 500 },
      );
    }
  }

  return NextResponse.json({ clipsAdded, narrationSaved });
}
