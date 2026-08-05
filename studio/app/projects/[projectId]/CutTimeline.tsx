"use client";

import { useCallback, useRef, useState } from "react";

const MIN_GAP_SECONDS = 3;

export type Silence = { start: number; end: number };

const formatTime = (seconds: number): string => {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
};

// Horizontal timeline: one block per clip, draggable handles at each
// internal cut point, silence ticks along the bottom for context on where
// natural pauses are. Fully controlled — the parent owns `cutPoints` and
// recomputes the edit plan (and Player preview) on every change.
export function CutTimeline({
  totalSeconds,
  cutPoints,
  silences,
  onChange,
}: {
  totalSeconds: number;
  cutPoints: number[];
  silences: Silence[];
  onChange: (next: number[]) => void;
}) {
  const trackRef = useRef<HTMLDivElement>(null);
  const [draggingIndex, setDraggingIndex] = useState<number | null>(null);

  const pixelToSeconds = useCallback(
    (clientX: number) => {
      const track = trackRef.current;
      if (!track) return 0;
      const rect = track.getBoundingClientRect();
      const ratio = Math.min(
        1,
        Math.max(0, (clientX - rect.left) / rect.width),
      );
      return ratio * totalSeconds;
    },
    [totalSeconds],
  );

  const startDrag = (index: number) => (event: React.MouseEvent) => {
    event.preventDefault();
    setDraggingIndex(index);
    const snapWindow = Math.max(0.3, totalSeconds * 0.01);

    const handleMove = (moveEvent: MouseEvent) => {
      const raw = pixelToSeconds(moveEvent.clientX);
      const lowerBound = cutPoints[index - 1] + MIN_GAP_SECONDS;
      const upperBound = cutPoints[index + 1] - MIN_GAP_SECONDS;
      let value = Math.min(upperBound, Math.max(lowerBound, raw));

      for (const silence of silences) {
        const midpoint = (silence.start + silence.end) / 2;
        if (Math.abs(midpoint - value) < snapWindow) {
          value = midpoint;
          break;
        }
      }

      const updated = [...cutPoints];
      updated[index] = value;
      onChange(updated);
    };

    const handleUp = () => {
      setDraggingIndex(null);
      window.removeEventListener("mousemove", handleMove);
      window.removeEventListener("mouseup", handleUp);
    };

    window.addEventListener("mousemove", handleMove);
    window.addEventListener("mouseup", handleUp);
  };

  return (
    <div>
      <div
        ref={trackRef}
        style={{
          position: "relative",
          height: 58,
          background: "var(--surface-2)",
          border: "1px solid var(--border)",
          borderRadius: "var(--radius-sm)",
          overflow: "hidden",
          userSelect: "none",
        }}
      >
        {cutPoints.slice(0, -1).map((start, i) => {
          const end = cutPoints[i + 1];
          const left = (start / totalSeconds) * 100;
          const width = ((end - start) / totalSeconds) * 100;
          return (
            <div
              key={i}
              style={{
                position: "absolute",
                left: `${left}%`,
                width: `${width}%`,
                top: 0,
                bottom: 0,
                borderRight: "1px solid var(--bg)",
                background:
                  i % 2 === 0 ? "var(--surface-3)" : "var(--surface-2)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 11,
                fontWeight: 600,
                color: "var(--text-dim)",
              }}
            >
              {i + 1}
            </div>
          );
        })}

        {silences.map((s, i) => (
          <div
            key={i}
            title={`pausa em ${s.start.toFixed(1)}s`}
            style={{
              position: "absolute",
              left: `${(((s.start + s.end) / 2) / totalSeconds) * 100}%`,
              bottom: 0,
              width: 2,
              height: 7,
              background: "var(--success)",
              opacity: 0.85,
              pointerEvents: "none",
            }}
          />
        ))}

        {cutPoints.slice(1, -1).map((cp, i) => {
          const index = i + 1;
          const left = (cp / totalSeconds) * 100;
          return (
            <div
              key={index}
              onMouseDown={startDrag(index)}
              style={{
                position: "absolute",
                left: `calc(${left}% - 4px)`,
                top: 0,
                bottom: 0,
                width: 8,
                cursor: "ew-resize",
                background:
                  draggingIndex === index ? "#ffffff" : "var(--accent)",
                zIndex: 2,
              }}
            />
          );
        })}
      </div>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          fontSize: 11,
          color: "var(--text-faint)",
          marginTop: 4,
        }}
      >
        <span>0:00</span>
        <span>{formatTime(totalSeconds)}</span>
      </div>
    </div>
  );
}
