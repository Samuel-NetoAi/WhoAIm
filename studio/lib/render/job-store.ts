export type RenderJob = {
  id: string;
  projectId: string;
  target: "full" | "short" | "post";
  status: "rendering" | "done" | "error";
  progress: number;
  outputPath?: string;
  error?: string;
  startedAt: number;
};

// In-memory only — fine for a single local user with no restart-resilience
// requirement. Skips SSE/websockets; the UI polls the job status endpoint.
const jobs = new Map<string, RenderJob>();

export const createJob = (job: RenderJob): RenderJob => {
  jobs.set(job.id, job);
  return job;
};

export const updateJob = (id: string, patch: Partial<RenderJob>): void => {
  const existing = jobs.get(id);
  if (!existing) return;
  jobs.set(id, { ...existing, ...patch });
};

export const getJob = (id: string): RenderJob | undefined => jobs.get(id);
