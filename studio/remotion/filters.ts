// CSS filter presets applied to each clip's wrapper. CSS filters render
// identically in the browser Player preview and in the headless render, so
// what you see is exactly what exports. Add a preset = add one entry here.
export const FILTER_PRESETS = {
  none: "",
  cinematic: "contrast(1.12) saturate(1.15) brightness(0.97)",
  warm: "sepia(0.18) saturate(1.25) hue-rotate(-8deg) brightness(1.02)",
  cold: "saturate(1.05) hue-rotate(10deg) brightness(1.02) contrast(1.08)",
  noir: "grayscale(1) contrast(1.3) brightness(0.95)",
  vintage: "sepia(0.35) saturate(0.85) contrast(0.95) brightness(1.05)",
} as const;

export type FilterPreset = keyof typeof FILTER_PRESETS;

export const FILTER_LABELS: Record<FilterPreset, string> = {
  none: "Sem filtro",
  cinematic: "Cinematográfico",
  warm: "Quente (dourado)",
  cold: "Frio (azulado)",
  noir: "Noir (P&B)",
  vintage: "Vintage (sépia)",
};
