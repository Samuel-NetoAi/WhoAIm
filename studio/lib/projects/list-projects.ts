import { existsSync, readdirSync, statSync } from "node:fs";
import path from "node:path";
import { SCAN_ROOTS } from "./constants";
import { encodeProjectId } from "./project-id";
import type { ProjectSummary } from "./types";

const VIDEO_EXTENSIONS = new Set([".mp4", ".mov", ".webm"]);

const isDirectory = (candidate: string): boolean => {
  try {
    return statSync(candidate).isDirectory();
  } catch {
    return false;
  }
};

const countVideoFiles = (dir: string): number => {
  if (!existsSync(dir)) return 0;
  return readdirSync(dir).filter((f) =>
    VIDEO_EXTENSIONS.has(path.extname(f).toLowerCase()),
  ).length;
};

// A "project" is any <scanRoot>\<Creature>\<name>\ folder that has a
// public/videos or public/audio subfolder — the same shape medusa-video
// already has. Scan roots are Criaturas\ and Animes\ under C:\Ai-Project.
export const listProjects = (): ProjectSummary[] => {
  const projects: ProjectSummary[] = [];

  for (const root of SCAN_ROOTS) {
    if (!existsSync(root.absolutePath)) continue;

    for (const creatureName of readdirSync(root.absolutePath)) {
      const creaturePath = path.join(root.absolutePath, creatureName);
      if (!isDirectory(creaturePath)) continue;

      for (const projectDirName of readdirSync(creaturePath)) {
        const projectPath = path.join(creaturePath, projectDirName);
        if (!isDirectory(projectPath)) continue;

        const videosDir = path.join(projectPath, "public", "videos");
        const audioDir = path.join(projectPath, "public", "audio");
        const hasVideosDir = existsSync(videosDir);
        const hasAudioDir = existsSync(audioDir);
        if (!hasVideosDir && !hasAudioDir) continue;

        projects.push({
          id: encodeProjectId(
            `${root.label}/${creatureName}/${projectDirName}`,
          ),
          creatureName: `${root.label} / ${creatureName}`,
          projectDirName,
          clipCount: countVideoFiles(videosDir),
          hasAudio: hasAudioDir && readdirSync(audioDir).length > 0,
          hasEditPlan: existsSync(path.join(projectPath, "edit-plan.json")),
        });
      }
    }
  }

  return projects;
};
