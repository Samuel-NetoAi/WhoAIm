import { existsSync, mkdirSync } from "node:fs";
import path from "node:path";
import { AI_PROJECT_ROOT } from "./constants";
import { encodeProjectId } from "./project-id";

const slugify = (value: string): string =>
  value
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "");

export const createProject = (creatureName: string): { id: string } => {
  const cleanCreatureName = creatureName.trim();
  if (!cleanCreatureName) {
    throw new Error("creatureName is required");
  }

  // New projects go under Criaturas\ by default; anime projects can be
  // created by prefixing the name with "Animes/" (e.g. "Animes/Bestas De Nen").
  const [rootLabel, folderName] = cleanCreatureName.includes("/")
    ? cleanCreatureName.split("/", 2).map((s) => s.trim())
    : ["Criaturas", cleanCreatureName];
  const projectDirName = `${slugify(folderName)}-video`;
  const projectPath = path.join(
    AI_PROJECT_ROOT,
    rootLabel,
    folderName,
    projectDirName,
  );

  if (existsSync(projectPath)) {
    throw new Error(`Project already exists: ${projectPath}`);
  }

  mkdirSync(path.join(projectPath, "public", "videos"), { recursive: true });
  mkdirSync(path.join(projectPath, "public", "audio"), { recursive: true });
  mkdirSync(path.join(projectPath, "notes"), { recursive: true });

  return {
    id: encodeProjectId(`${rootLabel}/${folderName}/${projectDirName}`),
  };
};
