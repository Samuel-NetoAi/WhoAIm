import { createReadStream, existsSync, statSync } from "node:fs";
import path from "node:path";
import { Readable } from "node:stream";
import { NextResponse } from "next/server";
import { getProjectPaths } from "@/lib/projects/project-paths";

const CONTENT_TYPES: Record<string, string> = {
  ".mp4": "video/mp4",
  ".mov": "video/quicktime",
  ".webm": "video/webm",
  ".mp3": "audio/mpeg",
  ".wav": "audio/wav",
  ".m4a": "audio/mp4",
  ".mpeg": "audio/mpeg",
  ".mpga": "audio/mpeg",
  ".aac": "audio/aac",
  ".ogg": "audio/ogg",
};

// Serves a project's public/ folder (videos + audio) so the browser-side
// @remotion/player preview can load media that lives outside this app's own
// public/ dir (which is where staticFile() resolves during a real render,
// via the bundler's per-project publicDir override).
export async function GET(
  request: Request,
  context: { params: Promise<{ projectId: string; filePath: string[] }> },
) {
  const { projectId, filePath } = await context.params;
  const { projectPath } = getProjectPaths(projectId);
  const publicDir = path.resolve(path.join(projectPath, "public"));

  const relative = filePath.map((segment) => decodeURIComponent(segment));
  const resolved = path.resolve(path.join(publicDir, ...relative));
  if (!resolved.startsWith(publicDir + path.sep)) {
    return NextResponse.json({ error: "Invalid path" }, { status: 400 });
  }

  if (!existsSync(resolved)) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }

  const stat = statSync(resolved);
  const contentType =
    CONTENT_TYPES[path.extname(resolved).toLowerCase()] ??
    "application/octet-stream";
  const webStream = Readable.toWeb(
    createReadStream(resolved),
  ) as ReadableStream;

  return new NextResponse(webStream, {
    headers: {
      "Content-Type": contentType,
      "Content-Length": String(stat.size),
    },
  });
}
