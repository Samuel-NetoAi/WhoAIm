import { spawn } from "node:child_process";
import path from "node:path";

export const DEV_NULL = process.platform === "win32" ? "NUL" : "/dev/null";

// The Remotion CLI run by node itself, not through `npx`. Windows can NOT
// spawn `npx.cmd` without a shell: since Node 18.20.2/20.12.2 (CVE-2024-27980)
// that throws EINVAL on the spot — measured on this machine's Node 22.16.
// Pointing node at the CLI's own entry file needs no shell and no .cmd, so
// paths with spaces survive as single argv entries. Exported for
// postprocess.ts's fallback, which needs the same fix.
const REMOTION_CLI = path.join(
  process.cwd(),
  "node_modules",
  "@remotion",
  "cli",
  "remotion-cli.js",
);
export const spawnRemotion = (args: string[]) =>
  spawn(process.execPath, [REMOTION_CLI, ...args], { cwd: process.cwd() });

// Runs `npx remotion ffmpeg`, which uses Remotion's bundled ffmpeg binary —
// nothing needs to be installed on the machine.
//
// Deliberately spawned WITHOUT shell:true: that option concatenates the
// command and its args into ONE string with no escaping (Node's own
// deprecation warning says as much), which silently breaks on the first
// space in any argument — and every path here can have one, since a project
// is named after a creature ("Teste Episodio Pomfy", ...). Confirmed by
// reproduction: the same call that works with an argv array fails with
// "No such file or directory" under shell:true the moment the path contains
// a space, because the shell splits it into multiple arguments.
//
// ffmpeg writes filter output to stderr regardless of exit code, so stdout
// is discarded and stderr is what callers parse — but a non-zero exit code
// now rejects instead of resolving, so a real failure surfaces as an error
// instead of silently looking like "ran fine, found nothing" (which is
// exactly what caused the space-in-path failures above to go unnoticed).
export const runRemotionFfmpeg = (args: string[]): Promise<string> => {
  return new Promise((resolve, reject) => {
    const child = spawnRemotion(["ffmpeg", ...args]);
    let stderr = "";
    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });
    child.on("error", reject);
    child.on("close", (code) => {
      if (code === 0) {
        resolve(stderr);
      } else {
        reject(new Error(`ffmpeg exited with code ${code}: ${stderr.slice(-800)}`));
      }
    });
  });
};
