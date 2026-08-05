// Output resolution is deliberately DECOUPLED from the source clips.
//
// The clips are currently generated at 480p (cost constraint), and taking the
// first clip's dimensions as the composition size meant the whole video —
// including captions and any overlay drawn by Remotion — rendered at 480p.
// Upscaling that afterwards can never recover the text: it was rasterized
// small. Rendering the composition at 1080p instead costs encode time and
// gives crisp overlays for free, while the footage itself is scaled by the
// compositor exactly once.
//
// This does NOT invent detail in the footage. Real detail requires either
// generating clips at a higher resolution or running an upscaler (Real-ESRGAN)
// over public/videos before analysis — see PLANO-ALPHA.md.

export type Resolution = { width: number; height: number };

// Short side of the target frame. 1080 is the lowest resolution YouTube still
// treats as "HD" for bitrate/codec purposes.
const MINIMUM_SHORT_SIDE = 1080;

// h264 requires even dimensions; an odd width fails the encode outright.
const toEven = (value: number): number => Math.round(value / 2) * 2;

// Encoders round frame sizes to even (often multiple-of-16) dimensions, so a
// clip's stored aspect is already an approximation of the intended one:
// 854x480 is "16:9" but computes to 1.7792. Scaling that up amplifies the
// error into a non-standard 1922x1080. Snapping to the intended aspect when
// we're within a fraction of a percent keeps the frame on standard sizes.
const STANDARD_ASPECTS = [16 / 9, 9 / 16, 4 / 3, 3 / 4, 1, 21 / 9, 2 / 3, 3 / 2];
const ASPECT_TOLERANCE = 0.01;

const snapAspect = (aspect: number): number =>
  STANDARD_ASPECTS.find(
    (standard) => Math.abs(aspect - standard) / standard <= ASPECT_TOLERANCE,
  ) ?? aspect;

const largestByArea = (clips: Resolution[]): Resolution =>
  clips.reduce((biggest, clip) =>
    clip.width * clip.height > biggest.width * biggest.height ? clip : biggest,
  );

// Never downscales: a project that already has 4K clips keeps 4K.
export const resolveOutputResolution = (
  clips: Resolution[],
  override?: Partial<Resolution>,
): Resolution => {
  if (clips.length === 0) {
    throw new Error("Cannot resolve output resolution without clips");
  }

  if (override?.width && override?.height) {
    return { width: toEven(override.width), height: toEven(override.height) };
  }

  const reference = largestByArea(clips);
  const aspect = snapAspect(reference.width / reference.height);

  if (aspect >= 1) {
    const height = Math.max(MINIMUM_SHORT_SIDE, reference.height);
    return { width: toEven(height * aspect), height: toEven(height) };
  }

  const width = Math.max(MINIMUM_SHORT_SIDE, reference.width);
  return { width: toEven(width), height: toEven(width / aspect) };
};
