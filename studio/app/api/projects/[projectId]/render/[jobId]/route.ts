import { NextResponse } from "next/server";
import { getJob } from "@/lib/render/job-store";

export async function GET(
  request: Request,
  context: { params: Promise<{ projectId: string; jobId: string }> },
) {
  const { jobId } = await context.params;
  const job = getJob(jobId);

  if (!job) {
    return NextResponse.json({ error: "Job not found" }, { status: 404 });
  }

  return NextResponse.json({ job });
}
