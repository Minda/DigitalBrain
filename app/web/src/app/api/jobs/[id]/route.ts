import { NextResponse } from "next/server";
import { db } from "@/modules/jobs/db";
import { jobs, events } from "@/modules/jobs/schema";
import { eq } from "drizzle-orm";

const VALID_STAGES = ["inbox", "viewed", "applied", "dismissed"] as const;

export async function PATCH(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const jobId = parseInt(id, 10);
    if (isNaN(jobId)) {
      return NextResponse.json(
        { success: false, error: "Invalid job ID" },
        { status: 400 }
      );
    }

    const body = await request.json();
    const { stage, relevance, starred } = body;

    // --- Validation ---
    if (stage !== undefined && !VALID_STAGES.includes(stage)) {
      return NextResponse.json(
        {
          success: false,
          error: `Invalid stage. Must be one of: ${VALID_STAGES.join(", ")}`,
        },
        { status: 400 }
      );
    }

    if (
      relevance !== undefined &&
      (!Number.isInteger(relevance) || relevance < 0 || relevance > 3)
    ) {
      return NextResponse.json(
        { success: false, error: "Relevance must be an integer from 0 to 3" },
        { status: 400 }
      );
    }

    if (starred !== undefined && starred !== 0 && starred !== 1) {
      return NextResponse.json(
        { success: false, error: "Starred must be 0 or 1" },
        { status: 400 }
      );
    }

    // --- Fetch existing job ---
    const existing = await db
      .select()
      .from(jobs)
      .where(eq(jobs.id, jobId))
      .get();

    if (!existing) {
      return NextResponse.json(
        { success: false, error: "Job not found" },
        { status: 404 }
      );
    }

    // --- Build update payload & event log ---
    const now = new Date().toISOString();
    const updateFields: Record<string, unknown> = { updatedAt: now };
    const eventInserts: {
      eventType: string;
      jobId: number;
      payload: string;
      createdAt: string;
    }[] = [];

    if (stage !== undefined && stage !== existing.stage) {
      updateFields.stage = stage;
      eventInserts.push({
        eventType: "stage_changed",
        jobId,
        payload: JSON.stringify({
          fromStage: existing.stage,
          toStage: stage,
        }),
        createdAt: now,
      });
    }

    if (relevance !== undefined && relevance !== existing.relevance) {
      updateFields.relevance = relevance;
      eventInserts.push({
        eventType: "relevance_corrected",
        jobId,
        payload: JSON.stringify({
          oldRelevance: existing.relevance,
          newRelevance: relevance,
        }),
        createdAt: now,
      });
    }

    if (starred !== undefined && starred !== existing.starred) {
      updateFields.starred = starred;
      eventInserts.push({
        eventType: "job_starred",
        jobId,
        payload: JSON.stringify({ starred: starred === 1 }),
        createdAt: now,
      });
    }

    // --- Apply update ---
    await db.update(jobs).set(updateFields).where(eq(jobs.id, jobId));

    // --- Insert events ---
    for (const evt of eventInserts) {
      await db.insert(events).values(evt);
    }

    // --- Return updated job ---
    const updatedJob = await db
      .select()
      .from(jobs)
      .where(eq(jobs.id, jobId))
      .get();

    return NextResponse.json({ success: true, job: updatedJob });
  } catch (error) {
    console.error("PATCH /api/jobs/[id] failed:", error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}
