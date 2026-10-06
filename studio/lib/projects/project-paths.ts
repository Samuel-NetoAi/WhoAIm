import path from "node:path";
import { AI_PROJECT_ROOT } from "./constants";
import { decodeProjectId } from "./project-id";

export type ProjectPaths = {
  projectPath: string;
  videosDir: string;
  audioDir: string;
  sourceDir: string;
  editPlanFile: string;
  analysisDir: string;
  probeFile: string;
  silencesFile: string;
  rendersDir: string;
};

export const getProjectPaths = (projectId: string): ProjectPaths => {
  const relative = decodeProjectId(projectId);
  const segments = relative.split("/").filter(Boolean);

  const root = path.resolve(AI_PROJECT_ROOT);
  const projectPath = path.resolve(root, ...segments);

  // Guard against a malformed/tampered id escaping the project root.
  if (projectPath !== root && !projectPath.startsWith(root + path.sep)) {
    throw new Error("Invalid project id");
  }

  return {
    projectPath,
    videosDir: path.join(projectPath, "public", "videos"),
    audioDir: path.join(projectPath, "public", "audio"),
    // Where a full-episode upload is kept after being split into numbered
    // clips (see split-video.ts) — not read by the render pipeline itself,
    // just a durable copy so the project can be re-split at a different
    // clip length later without re-uploading.
    sourceDir: path.join(projectPath, "source"),
    editPlanFile: path.join(projectPath, "edit-plan.json"),
    analysisDir: path.join(projectPath, "analysis"),
    probeFile: path.join(projectPath, "analysis", "probe.json"),
    silencesFile: path.join(projectPath, "analysis", "silences.json"),
    rendersDir: path.join(projectPath, "renders"),
  };
};
