import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { scenesFileSchema, type ScenesFile } from "./schema";

export type ScenesLoadResult = {
  scenes: ScenesFile | null;
  // Why there are no scenes, in Portuguese, for the analysis response. `null`
  // when the file loaded fine.
  problem: string | null;
};

// Absent scenes.json is the normal case, not an error: projects created before
// the file existed, or edited entirely by hand, simply keep the defaults.
export const loadScenes = (projectPath: string): ScenesLoadResult => {
  const file = path.join(projectPath, "scenes.json");
  if (!existsSync(file)) {
    return { scenes: null, problem: null };
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(readFileSync(file, "utf8"));
  } catch {
    return { scenes: null, problem: "scenes.json não é um JSON válido" };
  }

  const result = scenesFileSchema.safeParse(parsed);
  if (!result.success) {
    const first = result.error.issues[0];
    return {
      scenes: null,
      problem: `scenes.json inválido em "${first.path.join(".")}": ${first.message}`,
    };
  }

  return { scenes: result.data, problem: null };
};
