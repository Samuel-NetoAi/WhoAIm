import { ALL_FORMATS, FilePathSource, Input } from "mediabunny";

export const getMediaDuration = async (filePath: string): Promise<number> => {
  const input = new Input({
    formats: ALL_FORMATS,
    source: new FilePathSource(filePath),
  });
  return input.computeDuration();
};

export const getVideoDimensions = async (
  filePath: string,
): Promise<{ width: number; height: number }> => {
  const input = new Input({
    formats: ALL_FORMATS,
    source: new FilePathSource(filePath),
  });
  const track = await input.getPrimaryVideoTrack();
  if (!track) {
    throw new Error(`No video track found in ${filePath}`);
  }
  return { width: track.displayWidth, height: track.displayHeight };
};

// Average frames-per-second of a clip's primary video track. Used by the
// clip-enhancement pipeline to decide whether interpolation is still needed
// (skip if the clip is already at/near the 60fps target) — measured from the
// real packet timing, not assumed from a container tag.
export const getVideoFrameRate = async (filePath: string): Promise<number> => {
  const input = new Input({
    formats: ALL_FORMATS,
    source: new FilePathSource(filePath),
  });
  const track = await input.getPrimaryVideoTrack();
  if (!track) {
    throw new Error(`No video track found in ${filePath}`);
  }
  const stats = await track.computePacketStats();
  return stats.averagePacketRate;
};
