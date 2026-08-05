"use client";

import {
  Fragment,
  useEffect,
  useMemo,
  useRef,
  useState,
  type FormEvent,
} from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { Player } from "@remotion/player";
import { EditedVideo } from "@/remotion/EditedVideo";
import { calculateTotalFrames } from "@/lib/edit-plan/calculate-total-frames";
import { applyBoundaries } from "@/lib/edit-plan/apply-boundaries";
import type {
  AudioMode,
  EditPlan,
  FilterPreset,
  TransitionPreset,
} from "@/lib/edit-plan/schema";
import { FILTER_LABELS } from "@/remotion/filters";
import { TRANSITION_LABELS } from "@/remotion/transitions";
import { CutTimeline, type Silence } from "./CutTimeline";
import { NotesPanel } from "./NotesPanel";

type RenderTarget = "full" | "short";

const AUDIO_MODE_LABELS: Record<AudioMode, string> = {
  mix: "Som do clipe baixo (sob a narração)",
  replace: "Som do clipe substitui a narração",
  muted: "Sem som do clipe",
};

const audioModesFromPlan = (plan: EditPlan): Record<string, AudioMode> =>
  Object.fromEntries(plan.clips.map((c) => [c.id, c.audioMode ?? "mix"]));

const filtersFromPlan = (plan: EditPlan): Record<string, FilterPreset> =>
  Object.fromEntries(plan.clips.map((c) => [c.id, c.filter ?? "none"]));

// Which cue covers each scene, for the label in the scene grid. A scene with
// no cue is silent by design (SILENCIO), which is a musical decision worth
// seeing at a glance rather than mistaking for a missing track.
const cueByScene = (plan: EditPlan): (string | null)[] =>
  plan.clips.map((_, index) => {
    const cue = (plan.music ?? []).find((c) => c.scenes.includes(index));
    return cue ? cue.id.replace(/-\d+$/, "") : null;
  });

const transitionsFromPlan = (
  plan: EditPlan,
): Record<string, TransitionPreset> =>
  Object.fromEntries(
    plan.clips.map((c) => [c.id, c.transitionFromPrevious ?? "dissolve"]),
  );

type RenderJob = {
  id: string;
  target: RenderTarget;
  status: "rendering" | "done" | "error";
  progress: number;
  outputPath?: string;
  error?: string;
};

const filenameFromOutputPath = (outputPath: string): string =>
  encodeURIComponent(outputPath.split(/[\\/]/).pop() ?? "");

export default function ProjectPage() {
  const { projectId } = useParams<{ projectId: string }>();

  const [editPlan, setEditPlan] = useState<EditPlan | null>(null);
  const [planError, setPlanError] = useState<string | null>(null);
  const [silences, setSilences] = useState<Silence[]>([]);
  const [cutPoints, setCutPoints] = useState<number[] | null>(null);
  const [audioModes, setAudioModes] = useState<Record<string, AudioMode>>({});
  const [filters, setFilters] = useState<Record<string, FilterPreset>>({});
  const [transitions, setTransitions] = useState<
    Record<string, TransitionPreset>
  >({});
  const [postJob, setPostJob] = useState<RenderJob | null>(null);
  const [postSource, setPostSource] = useState<string | null>(null);
  const [post60, setPost60] = useState(false);
  const [postUpscale, setPostUpscale] = useState(true);
  const [dirty, setDirty] = useState(false);
  const [busy, setBusy] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [analysisNotes, setAnalysisNotes] = useState<string[]>([]);
  const [shortTargetSeconds, setShortTargetSeconds] = useState(30);
  const [jobs, setJobs] = useState<Record<RenderTarget, RenderJob | null>>({
    full: null,
    short: null,
  });

  const zipInputRef = useRef<HTMLInputElement>(null);
  const audioInputRef = useRef<HTMLInputElement>(null);

  const loadEditPlan = async () => {
    const res = await fetch(`/api/projects/${projectId}/edit-plan`);
    if (res.ok) {
      const data = await res.json();
      setEditPlan(data.editPlan);
      setCutPoints(data.editPlan.cutPoints ?? null);
      setAudioModes(audioModesFromPlan(data.editPlan));
      setFilters(filtersFromPlan(data.editPlan));
      setTransitions(transitionsFromPlan(data.editPlan));
      setDirty(false);
      setPlanError(null);
    } else {
      const data = await res.json().catch(() => ({}));
      setEditPlan(null);
      setPlanError(data.error ?? "Sem plano ainda");
    }
  };

  const loadSilences = async () => {
    const res = await fetch(`/api/projects/${projectId}/silences`);
    if (res.ok) {
      const data = await res.json();
      setSilences(data.silences ?? []);
    }
  };

  useEffect(() => {
    // One-time fetch on mount, reusing the same loaders the buttons below call.
    if (!projectId) return;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadEditPlan();
    loadSilences();
  }, [projectId]);

  // The plan actually shown in the Player / sent to the server: the saved
  // editPlan with cut points swapped for whatever's currently on the
  // timeline (identical to editPlan when nothing has been dragged yet).
  const previewPlan = useMemo(() => {
    if (!editPlan || !cutPoints) return editPlan;
    return applyBoundaries(
      editPlan.clips.map((clip) => ({
        id: clip.id,
        file: clip.file,
        durationInSeconds: clip.naturalDurationInSeconds,
        audioMode: audioModes[clip.id] ?? clip.audioMode,
        filter: filters[clip.id] ?? clip.filter,
        transitionFromPrevious:
          transitions[clip.id] ?? clip.transitionFromPrevious,
      })),
      editPlan.narration,
      cutPoints.slice(1, -1),
      editPlan.fps,
      editPlan.transitionFrames,
      editPlan.width,
      editPlan.height,
      {
        music: editPlan.music,
        ducking: editPlan.ducking,
        narrationPauses: editPlan.narrationPauses,
      },
    );
  }, [editPlan, cutPoints, audioModes, filters, transitions]);

  const cues = useMemo(
    () => (previewPlan ? cueByScene(previewPlan) : []),
    [previewPlan],
  );

  const handleUpload = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setStatusMessage("Enviando arquivos...");
    try {
      const formData = new FormData();
      if (zipInputRef.current?.files?.[0]) {
        formData.append("videosZip", zipInputRef.current.files[0]);
      }
      if (audioInputRef.current?.files?.[0]) {
        formData.append("narration", audioInputRef.current.files[0]);
      }
      const uploadRes = await fetch(`/api/projects/${projectId}/upload`, {
        method: "POST",
        body: formData,
      });
      if (!uploadRes.ok) throw new Error("Falha no upload");

      await runAnalyze();
    } catch (err) {
      setStatusMessage(
        err instanceof Error ? err.message : "Erro desconhecido",
      );
    } finally {
      setBusy(false);
    }
  };

  const runAnalyze = async () => {
    setStatusMessage("Analisando (durações + pausas na narração)...");
    const analyzeRes = await fetch(`/api/projects/${projectId}/analyze`, {
      method: "POST",
    });
    const analyzeData = await analyzeRes.json();
    if (!analyzeRes.ok)
      throw new Error(analyzeData.error ?? "Falha na análise");

    setEditPlan(analyzeData.editPlan);
    setCutPoints(analyzeData.editPlan.cutPoints ?? null);
    setAudioModes(audioModesFromPlan(analyzeData.editPlan));
    setFilters(filtersFromPlan(analyzeData.editPlan));
    setTransitions(transitionsFromPlan(analyzeData.editPlan));
    setDirty(false);
    setPlanError(null);
    await loadSilences();
    const origem: Record<string, string> = {
      aligned: "cortes medidos no roteiro alinhado",
      smart: "cortes encaixados nas pausas da narração",
      naive: "divisão igual — sem pausas detectadas",
    };
    setStatusMessage(
      `Plano gerado (${origem[analyzeData.alignment] ?? analyzeData.alignment}).`,
    );
    // The analysis reports what it could and could not use — a scenes.json that
    // matched nothing, a cue with no track, an alignment that did not fit the
    // clip count. Hiding that would make "loaded" and "worked" look the same.
    setAnalysisNotes(analyzeData.notes ?? []);
  };

  const handleResetCuts = async () => {
    setBusy(true);
    try {
      await runAnalyze();
    } catch (err) {
      setStatusMessage(
        err instanceof Error ? err.message : "Erro ao resetar cortes",
      );
    } finally {
      setBusy(false);
    }
  };

  const handleSaveCuts = async () => {
    if (!previewPlan) return;
    setBusy(true);
    setStatusMessage("Salvando cortes...");
    try {
      const res = await fetch(`/api/projects/${projectId}/edit-plan`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(previewPlan),
      });
      const data = await res.json();
      if (!res.ok) throw new Error("Falha ao salvar cortes");
      setEditPlan(data.editPlan);
      setCutPoints(data.editPlan.cutPoints ?? null);
      setAudioModes(audioModesFromPlan(data.editPlan));
      setFilters(filtersFromPlan(data.editPlan));
      setTransitions(transitionsFromPlan(data.editPlan));
      setDirty(false);
      setStatusMessage("Cortes salvos.");
    } catch (err) {
      setStatusMessage(
        err instanceof Error ? err.message : "Erro ao salvar cortes",
      );
    } finally {
      setBusy(false);
    }
  };

  const handleRender = async (target: RenderTarget) => {
    setJobs((prev) => ({ ...prev, [target]: null }));
    const res = await fetch(`/api/projects/${projectId}/render`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        target,
        ...(target === "short" ? { targetSeconds: shortTargetSeconds } : {}),
      }),
    });
    const data = await res.json();
    if (!res.ok) {
      setStatusMessage(data.error ?? "Falha ao iniciar render");
      return;
    }
    setJobs((prev) => ({
      ...prev,
      [target]: { id: data.jobId, target, status: "rendering", progress: 0 },
    }));
  };

  const handlePostProcess = async () => {
    if (!postSource) return;
    setPostJob(null);
    const res = await fetch(`/api/projects/${projectId}/postprocess`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        filename: postSource,
        interpolateTo60: post60,
        upscale2x: postUpscale,
      }),
    });
    const data = await res.json();
    if (!res.ok) {
      setStatusMessage(data.error ?? "Falha no pós-processamento");
      return;
    }
    setPostJob({
      id: data.jobId,
      target: "full",
      status: "rendering",
      progress: 0,
    });
  };

  useEffect(() => {
    if (postJob?.status !== "rendering") return;
    const interval = setInterval(async () => {
      const res = await fetch(
        `/api/projects/${projectId}/render/${postJob.id}`,
      );
      const data = await res.json();
      if (res.ok) setPostJob(data.job);
    }, 1500);
    return () => clearInterval(interval);
  }, [postJob, projectId]);

  useEffect(() => {
    const pending = (Object.values(jobs) as (RenderJob | null)[]).filter(
      (job) => job?.status === "rendering",
    );
    if (pending.length === 0) return;

    const interval = setInterval(async () => {
      for (const job of pending) {
        if (!job) continue;
        const res = await fetch(
          `/api/projects/${projectId}/render/${job.id}`,
        );
        const data = await res.json();
        if (res.ok) {
          setJobs((prev) => ({ ...prev, [job.target]: data.job }));
        }
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [jobs, projectId]);

  return (
    <main className="page">
      <header className="page-header">
        <h1>{editPlan ? "Projeto" : "Projeto (sem plano ainda)"}</h1>
        <p className="subtitle">
          <Link href="/">← todos os projetos</Link>
        </p>
      </header>

      <section className="card">
        <h2>1. Enviar material</h2>
        <div className="stack">
          <form onSubmit={handleUpload} className="stack">
            <label>
              Zip com os clipes numerados{" "}
              <input ref={zipInputRef} type="file" accept=".zip" />
            </label>
            <label>
              Narração{" "}
              <input ref={audioInputRef} type="file" accept="audio/*" />
            </label>
            <div className="row">
              <button type="submit" className="primary" disabled={busy}>
                {busy ? "Processando..." : "Enviar e analisar"}
              </button>
              {statusMessage && <span className="status">{statusMessage}</span>}
            </div>
            {analysisNotes.length > 0 && (
              <ul className="analysis-notes">
                {analysisNotes.map((note) => (
                  <li key={note}>{note}</li>
                ))}
              </ul>
            )}
          </form>
        </div>
      </section>

      <section className="card">
        <h2>2. Prévia</h2>
        {planError && !editPlan && <p className="hint">{planError}</p>}
        {previewPlan && (
          <>
            <Player
              component={EditedVideo}
              inputProps={{
                editPlan: previewPlan,
                mediaBaseUrl: `/api/projects/${projectId}/media`,
              }}
              durationInFrames={calculateTotalFrames(previewPlan)}
              compositionWidth={previewPlan.width}
              compositionHeight={previewPlan.height}
              fps={previewPlan.fps}
              controls
              style={{ width: "100%", maxWidth: 640 }}
            />

            <div style={{ marginTop: "1.5rem" }}>
              <h3>
                Cortes — {previewPlan.clips.length} cenas
                <span className="hint" style={{ fontWeight: 400 }}>
                  {" "}
                  · arraste as divisórias para ajustar
                </span>
              </h3>
              {cutPoints && (
                <CutTimeline
                  totalSeconds={previewPlan.narration.durationInSeconds}
                  cutPoints={cutPoints}
                  silences={silences}
                  onChange={(next) => {
                    setCutPoints(next);
                    setDirty(true);
                  }}
                />
              )}
              <div className="row" style={{ marginTop: "0.7rem" }}>
                <button
                  className={dirty ? "primary" : ""}
                  onClick={handleSaveCuts}
                  disabled={!dirty || busy}
                >
                  Salvar cortes
                </button>
                <button onClick={handleResetCuts} disabled={busy}>
                  Resetar para automático
                </button>
              </div>
            </div>

            <div style={{ marginTop: "1.75rem" }}>
              <h3>
                Áudio, filtro e transição por cena
                <span className="hint" style={{ fontWeight: 400 }}>
                  {" "}
                  · o som do clipe fica baixo sob a narração por padrão;
                  &quot;substitui&quot; troca a narração pelo som original. A
                  transição é a ENTRADA da cena — a primeira não tem.
                </span>
              </h3>
              <div style={{ marginBottom: "0.7rem" }}>
                <label>
                  Filtro em todas as cenas:{" "}
                  <select
                    value=""
                    onChange={(e) => {
                      const preset = e.target.value as FilterPreset;
                      if (!preset) return;
                      setFilters(
                        Object.fromEntries(
                          previewPlan.clips.map((c) => [c.id, preset]),
                        ),
                      );
                      setDirty(true);
                    }}
                  >
                    <option value="">— aplicar a todas —</option>
                    {(Object.keys(FILTER_LABELS) as FilterPreset[]).map(
                      (preset) => (
                        <option key={preset} value={preset}>
                          {FILTER_LABELS[preset]}
                        </option>
                      ),
                    )}
                  </select>
                </label>
              </div>
              <div className="scene-grid">
                {previewPlan.clips.map((clip, i) => (
                  <Fragment key={clip.id}>
                    <span className="scene-label">
                      Cena {i + 1}
                      <br />
                      <span className="scene-cue">
                        {cues[i] ? `♪ ${cues[i]}` : "sem música"}
                      </span>
                    </span>
                    <select
                      value={audioModes[clip.id] ?? clip.audioMode ?? "mix"}
                      onChange={(e) => {
                        setAudioModes((prev) => ({
                          ...prev,
                          [clip.id]: e.target.value as AudioMode,
                        }));
                        setDirty(true);
                      }}
                    >
                      {(Object.keys(AUDIO_MODE_LABELS) as AudioMode[]).map(
                        (mode) => (
                          <option key={mode} value={mode}>
                            {AUDIO_MODE_LABELS[mode]}
                          </option>
                        ),
                      )}
                    </select>
                    <select
                      value={filters[clip.id] ?? clip.filter ?? "none"}
                      onChange={(e) => {
                        setFilters((prev) => ({
                          ...prev,
                          [clip.id]: e.target.value as FilterPreset,
                        }));
                        setDirty(true);
                      }}
                    >
                      {(Object.keys(FILTER_LABELS) as FilterPreset[]).map(
                        (preset) => (
                          <option key={preset} value={preset}>
                            {FILTER_LABELS[preset]}
                          </option>
                        ),
                      )}
                    </select>
                    {i === 0 ? (
                      <span className="hint">— (abre o vídeo)</span>
                    ) : (
                      <select
                        value={
                          transitions[clip.id] ??
                          clip.transitionFromPrevious ??
                          "dissolve"
                        }
                        onChange={(e) => {
                          setTransitions((prev) => ({
                            ...prev,
                            [clip.id]: e.target.value as TransitionPreset,
                          }));
                          setDirty(true);
                        }}
                      >
                        {(
                          Object.keys(TRANSITION_LABELS) as TransitionPreset[]
                        ).map((preset) => (
                          <option key={preset} value={preset}>
                            {TRANSITION_LABELS[preset]}
                          </option>
                        ))}
                      </select>
                    )}
                  </Fragment>
                ))}
              </div>
            </div>
          </>
        )}
      </section>

      <section className="card">
        <h2>3. Renderizar</h2>
        <div className="row" style={{ marginBottom: "0.5rem" }}>
          <button
            className="primary"
            onClick={() => handleRender("full")}
            disabled={!editPlan || jobs.full?.status === "rendering"}
          >
            Renderizar vídeo completo
          </button>
          <span className="hint">ou</span>
          <label className="row" style={{ gap: "0.4rem" }}>
            Short de
            <input
              type="number"
              min={5}
              max={120}
              value={shortTargetSeconds}
              onChange={(e) =>
                setShortTargetSeconds(Number(e.target.value) || 30)
              }
              style={{ width: 62 }}
            />
            segundos
          </label>
          <button
            onClick={() => handleRender("short")}
            disabled={!editPlan || jobs.short?.status === "rendering"}
          >
            Renderizar Short
          </button>
        </div>

        {(["full", "short"] as const).map((target) => {
          const job = jobs[target];
          if (!job) return null;
          const rotulo = target === "full" ? "Vídeo completo" : "Short";
          return (
            <div key={target} style={{ marginTop: "1rem" }}>
              {job.status === "rendering" && (
                <>
                  <span className="status">
                    {rotulo} — renderizando ({Math.round(job.progress * 100)}%)
                  </span>
                  <div className="progress-track">
                    <div
                      className="progress-fill"
                      style={{ width: `${job.progress * 100}%` }}
                    />
                  </div>
                </>
              )}
              {job.status === "error" && (
                <span className="status error">
                  {rotulo} — erro: {job.error}
                </span>
              )}
              {job.status === "done" && job.outputPath && (
                <>
                  <p className="status done" style={{ marginBottom: "0.5rem" }}>
                    {rotulo} — pronto
                  </p>
                  <video
                    controls
                    style={{ width: "100%", maxWidth: 640 }}
                    src={`/api/projects/${projectId}/renders/${filenameFromOutputPath(
                      job.outputPath,
                    )}`}
                  />
                  <div className="row" style={{ marginTop: "0.6rem" }}>
                    <a
                      className="button"
                      href={`/api/projects/${projectId}/renders/${filenameFromOutputPath(
                        job.outputPath,
                      )}`}
                      download
                    >
                      ⬇ Baixar
                    </a>
                    <button
                      onClick={() =>
                        setPostSource(
                          job.outputPath!.split(/[\\/]/).pop() ?? null,
                        )
                      }
                    >
                      Pós-processar…
                    </button>
                  </div>
                </>
              )}
            </div>
          );
        })}

        {postSource && (
          <div
            style={{
              marginTop: "1.25rem",
              paddingTop: "1.25rem",
              borderTop: "1px solid var(--border)",
            }}
          >
            <h3>Pós-processamento — {postSource}</h3>
            <div className="stack" style={{ gap: "0.4rem" }}>
              <label>
                <input
                  type="checkbox"
                  checked={post60}
                  onChange={(e) => setPost60(e.target.checked)}
                />{" "}
                Interpolar para 60 fps{" "}
                <span className="hint">(lento — vários minutos)</span>
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={postUpscale}
                  onChange={(e) => setPostUpscale(e.target.checked)}
                />{" "}
                Upscale 2x <span className="hint">(rápido)</span>
              </label>
            </div>
            <div className="row" style={{ marginTop: "0.75rem" }}>
              <button
                className="primary"
                disabled={
                  (!post60 && !postUpscale) || postJob?.status === "rendering"
                }
                onClick={handlePostProcess}
              >
                Processar
              </button>
              {postJob?.status === "rendering" && (
                <span className="status">
                  processando ({Math.round(postJob.progress * 100)}%)
                </span>
              )}
              {postJob?.status === "error" && (
                <span className="status error">{postJob.error}</span>
              )}
              {postJob?.status === "done" && postJob.outputPath && (
                <a
                  className="button"
                  href={`/api/projects/${projectId}/renders/${filenameFromOutputPath(
                    postJob.outputPath,
                  )}`}
                  download
                >
                  ⬇ Baixar resultado
                </a>
              )}
            </div>
            {postJob?.status === "rendering" && (
              <div className="progress-track">
                <div
                  className="progress-fill"
                  style={{ width: `${postJob.progress * 100}%` }}
                />
              </div>
            )}
          </div>
        )}
      </section>

      <section className="card">
        <h2>4. Notas do projeto</h2>
        <NotesPanel projectId={projectId} />
      </section>
    </main>
  );
}
