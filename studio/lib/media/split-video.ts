import { mkdirSync, readdirSync } from "node:fs";
import path from "node:path";
import { runRemotionFfmpeg } from "./run-ffmpeg";
import { getMediaDuration } from "./get-media-duration";

const VIDEO_EXTENSIONS = new Set([".mp4", ".mov", ".webm"]);

// Splits one continuous video (a full episode, already edited together)
// into fixed-length numbered clips inside videosDir — "000.mp4", "001.mp4",
// ... — the exact shape probeProject and every plan builder already expect,
// so the rest of the Studio needs no changes to handle a single-file upload.
//
// One ffmpeg call PER segment (-ss/-t/-c copy), not the `segment` muxer:
// Remotion's bundled ffmpeg is a stripped build (see run-ffmpeg.ts) that
// doesn't have it compiled in — confirmed by running it directly
// ("Unrecognized option 'segment_time'. Error splitting the argument list").
// Plain seek + trim + stream-copy is core functionality every ffmpeg build
// has, so this needs nothing more than that.
//
// Stream-copied, so no re-encode and no quality loss, but each cut lands on
// the nearest keyframe rather than exactly on segmentSeconds — probeProject
// reads every clip's real duration afterwards, so the plan builders already
// handle that variance (they always have).
export const splitVideoIntoClips = async (
  sourcePath: string,
  videosDir: string,
  segmentSeconds: number,
): Promise<number> => {
  mkdirSync(videosDir, { recursive: true });
  const totalSeconds = await getMediaDuration(sourcePath);
  const segmentCount = Math.max(1, Math.ceil(totalSeconds / segmentSeconds));

  for (let i = 0; i < segmentCount; i++) {
    const outputPath = path.join(videosDir, `${String(i).padStart(3, "0")}.mp4`);
    await runRemotionFfmpeg([
      "-ss",
      String(i * segmentSeconds),
      "-i",
      sourcePath,
      "-t",
      String(segmentSeconds),
      "-map",
      "0",
      "-c",
      "copy",
      outputPath,
    ]);
  }

  return readdirSync(videosDir).filter((f) =>
    VIDEO_EXTENSIONS.has(path.extname(f).toLowerCase()),
  ).length;
};

// Extracts the source video's own audio track to stand in as the narration
// — for a full-episode upload with no separately recorded voiceover, the
// dialogue baked into the video IS the only narration there is. Re-encoded
// (not stream-copied) because the source's audio codec can be anything a
// browser/editor exports (opus, ac3, ...) and the rest of the Studio only
// ever reads aac/m4a narration files.
//
// `-f mp4` forces the container explicitly: Remotion's stripped ffmpeg
// build failed to infer it from the .m4a extension on its own ("Unable to
// choose an output format ... use a standard extension"), even though m4a
// IS an mp4 container holding just an audio track — confirmed by running it
// directly.
export const extractAudioTrack = async (
  sourcePath: string,
  audioDir: string,
  outputFileName: string,
): Promise<void> => {
  mkdirSync(audioDir, { recursive: true });
  await runRemotionFfmpeg([
    "-i",
    sourcePath,
    "-vn",
    "-c:a",
    "aac",
    "-b:a",
    "192k",
    "-f",
    "mp4",
    path.join(audioDir, outputFileName),
  ]);
};
