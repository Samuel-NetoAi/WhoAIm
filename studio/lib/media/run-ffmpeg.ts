import { spawn } from "node:child_process";

export const DEV_NULL = process.platform === "win32" ? "NUL" : "/dev/null";

// `npx`/`npx.cmd` spawned by their exact platform name, which Windows can
// invoke directly (despite being a .cmd file) without going through a shell.
// Exported for postprocess.ts's own npx fallback, which needs the same fix.
export const NPX_COMMAND = process.platform === "win32" ? "npx.cmd" : "npx";

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
    const child = spawn(NPX_COMMAND, ["remotion", "ffmpeg", ...args], {
      cwd: process.cwd(),
    });
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
