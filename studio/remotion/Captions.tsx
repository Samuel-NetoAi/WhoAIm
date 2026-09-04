import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import type { Caption } from "../lib/edit-plan/schema";

// Type size is a fraction of the frame, never fixed pixels: the same plan
// renders a 1920x1080 full cut and a 1080x1920 Short, and a 48px caption that
// reads well on one is either a whisper or a wall on the other.
//
// The two are keyed to DIFFERENT dimensions on purpose. On a wide frame the
// limit is vertical real estate, so height decides. On a vertical frame the
// limit is the measure — how many characters fit across 1080px — so width
// decides, and keying it to height there produced an 86px caption on a frame
// only 1080 wide.
const FONT_HEIGHT_FRACTION_WIDE = 0.045;
const FONT_WIDTH_FRACTION_VERTICAL = 0.058;
const LINE_HEIGHT = 1.25;
// Bottom margin. Deliberately generous on the Short: YouTube's own UI (title,
// channel handle, buttons) sits over the lower fifth of a vertical video, and
// a caption under it is a caption nobody reads.
const BOTTOM_FRACTION_WIDE = 0.08;
const BOTTOM_FRACTION_VERTICAL = 0.2;
// Never let a line run the full frame width — long measures are what make
// burned-in captions tiring to read.
const MAX_WIDTH_FRACTION = 0.85;

const isVertical = (width: number, height: number): boolean => height > width;

// The caption on screen at this instant, or none. Linear scan because a
// 10-minute narration is a few hundred captions — an index would be more code
// than the search it saves.
const captionAt = (captions: Caption[], seconds: number): Caption | null => {
  for (const caption of captions) {
    if (seconds >= caption.t0 && seconds < caption.t1) return caption;
    // Sorted ascending by loadCaptions, so once a caption starts in the
    // future, none of the remaining ones can be active.
    if (caption.t0 > seconds) break;
  }
  return null;
};

export const Captions: React.FC<{ captions: Caption[] }> = ({ captions }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const caption = captionAt(captions, frame / fps);
  if (!caption) return null;

  const vertical = isVertical(width, height);

  // `linhas` comes from align/alpha_align/legendas.py, which owns the
  // line-breaking rule: 42 characters per line, at most 2 lines, balanced,
  // never splitting a word — the Netflix/BBC convention.
  //
  // That measure was written for a WIDE frame, and on a 9:16 Short it does not
  // fit: at a size worth reading, 42 characters overflow 1080px, so each
  // authored line wrapped AGAIN and a two-line caption rendered as three, with
  // the last word of line one orphaned onto its own line (seen in the first
  // real render, 04/09/2026). So on a vertical frame the authored breaks are
  // deliberately dropped and the text is re-flowed as one paragraph — CSS
  // wraps greedily without splitting words, which is exactly the job, and
  // needs no second copy of the breaking algorithm in TypeScript.
  //
  // On a wide frame the authored breaks are honoured, because there the
  // measure fits and a balanced two-line split reads better than a greedy one.
  const lines =
    vertical || !caption.linhas?.length
      ? [caption.linhas?.join(" ") ?? caption.texto]
      : caption.linhas;

  const fontSize = vertical
    ? width * FONT_WIDTH_FRACTION_VERTICAL
    : height * FONT_HEIGHT_FRACTION_WIDE;
  const bottom =
    height * (vertical ? BOTTOM_FRACTION_VERTICAL : BOTTOM_FRACTION_WIDE);

  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-end",
        alignItems: "center",
        paddingBottom: bottom,
        // The caption layer must never eat a click in the Player preview.
        pointerEvents: "none",
      }}
    >
      <div
        style={{
          maxWidth: width * MAX_WIDTH_FRACTION,
          textAlign: "center",
          fontFamily:
            '"Inter", "Segoe UI", "Helvetica Neue", Arial, sans-serif',
          fontSize,
          fontWeight: 700,
          lineHeight: LINE_HEIGHT,
          color: "white",
          // Outline plus a soft drop shadow, rather than a solid box: the box
          // reads as broadcast subtitles and covers the image, and this
          // footage is the product. The stroke is what keeps white text legible
          // over a white-ish frame; the shadow is what keeps it legible over a
          // busy one.
          WebkitTextStroke: `${Math.max(1, fontSize * 0.045)}px rgba(0,0,0,0.9)`,
          paintOrder: "stroke fill",
          textShadow: `0 ${fontSize * 0.06}px ${fontSize * 0.14}px rgba(0,0,0,0.65)`,
          // Balanced wrapping when the browser supports it: it is what keeps a
          // re-flowed vertical caption from ending on a single orphan word.
          textWrap: "balance",
        }}
      >
        {lines.map((line, i) => (
          <div key={i}>{line}</div>
        ))}
      </div>
    </AbsoluteFill>
  );
};
