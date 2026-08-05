import path from "node:path";

// All project ids are paths relative to this root (e.g.
// "Criaturas/Medusa/medusa-video"), so moving the studio itself never
// invalidates ids.
export const AI_PROJECT_ROOT = process.env.AI_PROJECT_ROOT ?? "C:\\Ai-Project";

// Folders scanned for projects, each two levels deep:
// <root>\<criatura|anime>\<projeto>\public\{videos,audio}
export const SCAN_ROOTS = ["Criaturas", "Animes"].map((name) => ({
  label: name,
  absolutePath: path.join(AI_PROJECT_ROOT, name),
}));
