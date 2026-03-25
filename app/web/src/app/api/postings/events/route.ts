import { NextResponse } from "next/server";
import { db } from "@/modules/jobs/db";
import { events } from "@/modules/jobs/schema";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { eventType, jobId, payload } = body;

    if (!eventType || typeof eventType !== "string") {
      return NextResponse.json(
        { success: false, error: "eventType is required and must be a string" },
        { status: 400 }
      );
    }

    const now = new Date().toISOString();

    const result = await db
      .insert(events)
      .values({
        eventType,
        jobId: jobId ?? null,
        payload: payload ? JSON.stringify(payload) : null,
        createdAt: now,
      })
      .returning({ id: events.id });

    return NextResponse.json({ success: true, eventId: result[0].id });
  } catch (error) {
    console.error("POST /api/jobs/events failed:", error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}
