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
