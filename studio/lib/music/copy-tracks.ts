import { copyFileSync, existsSync, mkdirSync, statSync } from "node:fs";
import path from "node:path";
import { publicPathForTrack } from "./build-cues";
import { trackAbsolutePath, type Track } from "./catalog";

export type CopyResult = {
  // Public-relative paths that could NOT be made available, so the caller can
  // drop the cues pointing at them instead of rendering silence and calling it
  // music.
  failed: Set<string>;
  problems: string[];
};

// Library tracks are copied into the project rather than referenced in place.
// Remotion's bundle exposes exactly one public dir, so a file outside it is
// unreachable at render time — and copying has the side benefit of making the
// project self-contained when it travels between the two machines.
export const copyTracksIntoProject = (
  tracks: Track[],
  projectPath: string,
): CopyResult => {
  const failed = new Set<string>();
  const problems: string[] = [];
  if (tracks.length === 0) return { failed, problems };

  const musicDir = path.join(projectPath, "public", "music");
  mkdirSync(musicDir, { recursive: true });

  for (const track of tracks) {
    const publicRelativePath = publicPathForTrack(track);
    const source = trackAbsolutePath(track);
    const destination = path.join(projectPath, "public", publicRelativePath);

    if (!existsSync(source)) {
      failed.add(publicRelativePath);
      problems.push(
        `faixa "${track.id}": arquivo não encontrado em ${track.arquivo}`,
      );
      continue;
    }

    // Re-analysing a project is routine; re-copying megabytes of audio that
    // did not change is not.
    if (
      existsSync(destination) &&
      statSync(destination).size === statSync(source).size
    ) {
      continue;
    }

    try {
      copyFileSync(source, destination);
    } catch (error) {
      failed.add(publicRelativePath);
      problems.push(
        `faixa "${track.id}": falha ao copiar — ${
          error instanceof Error ? error.message : "erro desconhecido"
        }`,
      );
    }
  }

  return { failed, problems };
};
