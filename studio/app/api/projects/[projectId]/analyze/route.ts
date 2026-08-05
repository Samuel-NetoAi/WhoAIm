import { mkdirSync, writeFileSync } from "node:fs";
import { NextResponse } from "next/server";
import { getProjectPaths } from "@/lib/projects/project-paths";
import { probeProject } from "@/lib/media/probe-project";
import { buildNaivePlan } from "@/lib/edit-plan/build-naive-plan";
import { buildSmartPlan } from "@/lib/edit-plan/build-smart-plan";
import { buildAlignedPlan } from "@/lib/edit-plan/build-aligned-plan";
import { detectSilences } from "@/lib/media/detect-silences";
import { loadScenes } from "@/lib/scenes/load-scenes";
import { directionsForClips } from "@/lib/scenes/schema";
import { boundariesForClips, loadAlignment } from "@/lib/alignment/load-alignment";
import { loadCatalog } from "@/lib/music/catalog";
import { buildMusicCues } from "@/lib/music/build-cues";
import { copyTracksIntoProject } from "@/lib/music/copy-tracks";

export async function POST(
  request: Request,
  context: { params: Promise<{ projectId: string }> },
) {
  const { projectId } = await context.params;
  const paths = getProjectPaths(projectId);

  // Optional { width, height } to force the output resolution; omitted, the
  // plan targets at least 1080p regardless of how small the clips are.
  const body = await request.json().catch(() => ({}));
  const resolutionOverride =
    typeof body?.width === "number" && typeof body?.height === "number"
      ? { width: body.width, height: body.height }
      : undefined;

  let probe;
  try {
    probe = await probeProject(paths.videosDir, paths.audioDir);
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Unknown error" },
      { status: 400 },
    );
  }

  // Editorial choices (filter, transition) written by the `whoiam` skill.
  // Their absence is normal and simply means "keep the defaults".
  const { scenes, problem: scenesProblem } = loadScenes(paths.projectPath);
  const sceneMatch = scenes
    ? directionsForClips(
        scenes.cenas,
        probe.clips.map((clip) => clip.file),
      )
    : null;
  const directions = sceneMatch?.directions;

  // Three strategies, best first:
  //   aligned — cut points MEASURED against the narration (Alpha/align)
  //   smart   — equal split snapped to the nearest pause
  //   naive   — plain equal split
  // Each falls through to the next, so analysis never fails because an
  // optional input is missing or an external process is unavailable.
  let editPlan;
  let alignmentMode: "aligned" | "smart" | "naive" = "smart";
  const notes: string[] = [];
  if (scenesProblem) notes.push(scenesProblem);
  if (sceneMatch) {
    // Surfaced on purpose: a scenes.json that matches nothing used to load
    // cleanly and change nothing, which is indistinguishable from working.
    notes.push(
      `scenes.json: ${sceneMatch.matched} de ${probe.clips.length} clipe(s) ` +
        `com direção, por ${sceneMatch.strategy}`,
    );
  }

  const { alignment, problem: alignmentProblem } = loadAlignment(
    paths.projectPath,
  );
  if (alignmentProblem) notes.push(alignmentProblem);

  let alignedBoundaries: number[] | null = null;
  if (alignment) {
    const result = boundariesForClips(alignment, probe.clips.length);
    alignedBoundaries = result.internalBoundarySeconds;
    if (result.problem) notes.push(`Alinhamento não usado: ${result.problem}`);
  }

  // The pauses are needed for the music ducking curve regardless of which
  // strategy sets the cut points, so detection runs on its own now instead of
  // only inside the "smart" branch.
  let silences: Awaited<ReturnType<typeof detectSilences>> = [];
  let silenceDetectionFailed = false;
  try {
    silences = await detectSilences(
      probe.narration.absolutePath,
      probe.narration.durationInSeconds,
    );
  } catch (error) {
    console.warn("Silence detection failed:", error);
    silenceDetectionFailed = true;
    notes.push("Detecção de pausas falhou — a trilha não vai respirar nas pausas");
  }

  if (alignedBoundaries) {
    editPlan = buildAlignedPlan(
      probe,
      alignedBoundaries,
      undefined,
      undefined,
      resolutionOverride,
      directions,
    );
    alignmentMode = "aligned";
  } else {
    // Silence-snapped cuts are strictly better than a hard equal split, but
    // without pauses there is nothing to snap to.
    if (silenceDetectionFailed) {
      editPlan = buildNaivePlan(
        probe,
        undefined,
        undefined,
        resolutionOverride,
        directions,
      );
      alignmentMode = "naive";
    } else {
      editPlan = buildSmartPlan(
        probe,
        silences,
        undefined,
        undefined,
        resolutionOverride,
        directions,
      );
    }
  }

  // Music last: the cues are laid out against the plan's own cut points, so
  // they can only be built once the boundaries are settled.
  editPlan.narrationPauses = silences;
  if (scenes) {
    const { tracks, problem: catalogProblem } = loadCatalog();
    if (catalogProblem) notes.push(catalogProblem);

    const built = buildMusicCues(
      scenes.cenas,
      editPlan.cutPoints ?? [],
      tracks,
    );
    notes.push(...built.notes);

    if (built.cues.length > 0) {
      const copied = copyTracksIntoProject(built.tracksUsed, paths.projectPath);
      notes.push(...copied.problems);
      editPlan.music = built.cues.filter((cue) => !copied.failed.has(cue.file));
      notes.push(
        `trilha: ${editPlan.music.length} cue(s) em ${scenes.cenas.length} cena(s)`,
      );
    }
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

  return NextResponse.json({
    editPlan,
    alignment: alignmentMode,
    musicCues: editPlan.music.length,
    scenesApplied: sceneMatch ? sceneMatch.matched : 0,
    alignmentConfidence: alignment?.confianca ?? null,
    notes,
  });
}
