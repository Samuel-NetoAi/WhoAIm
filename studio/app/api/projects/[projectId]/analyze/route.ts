import { mkdirSync, writeFileSync } from "node:fs";
import { NextResponse } from "next/server";
import { getProjectPaths } from "@/lib/projects/project-paths";
import { probeProject } from "@/lib/media/probe-project";
import { buildNaivePlan } from "@/lib/edit-plan/build-naive-plan";
import { buildSmartPlan } from "@/lib/edit-plan/build-smart-plan";
import { detectSilences } from "@/lib/media/detect-silences";

export async function POST(
  request: Request,
  context: { params: Promise<{ projectId: string }> },
) {
  const { projectId } = await context.params;
  const paths = getProjectPaths(projectId);

  let probe;
  try {
    probe = await probeProject(paths.videosDir, paths.audioDir);
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Unknown error" },
      { status: 400 },
    );
  }

  // Silence-snapped cuts are strictly better than a hard equal split, but
  // ffmpeg is an external process — if it's unavailable or the audio is
  // unparseable, fall back to the naive plan rather than failing analysis.
  let editPlan;
  let alignment: "smart" | "naive" = "smart";
  let silences: Awaited<ReturnType<typeof detectSilences>> = [];
  try {
    silences = await detectSilences(
      probe.narration.absolutePath,
      probe.narration.durationInSeconds,
    );
    editPlan = buildSmartPlan(probe, silences);
  } catch (error) {
    console.warn(
      "Silence detection failed, falling back to equal-split plan:",
      error,
    );
    editPlan = buildNaivePlan(probe);
    alignment = "naive";
  }

  mkdirSync(paths.analysisDir, { recursive: true });
  writeFileSync(paths.silencesFile, JSON.stringify(silences, null, 2));
  writeFileSync(
    paths.probeFile,
    JSON.stringify(
      {
        clips: probe.clips.map(({ absolutePath: _absolutePath, ...rest }) => rest),
        narration: (({ absolutePath: _absolutePath, ...rest }) => rest)(
          probe.narration,
        ),
      },
      null,
      2,
    ),
  );
  writeFileSync(paths.editPlanFile, JSON.stringify(editPlan, null, 2));

  return NextResponse.json({ editPlan, alignment });
}
