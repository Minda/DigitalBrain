import { NextRequest, NextResponse } from "next/server";
import { db } from "@/modules/audio/db";
import { playbackSessions, audioFiles } from "@/modules/audio/schema";
import { eq, and, desc } from "drizzle-orm";

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const audioFileId = parseInt(id, 10);

    if (isNaN(audioFileId)) {
      return NextResponse.json(
        { success: false, error: "Invalid audio file ID" },
        { status: 400 }
      );
    }

    const body = await request.json();
    const { currentPosition, playbackRate, completed } = body;

    // Validate inputs
    if (currentPosition !== undefined && typeof currentPosition !== "number") {
      return NextResponse.json(
        { success: false, error: "currentPosition must be a number" },
        { status: 400 }
      );
    }

    if (playbackRate !== undefined && typeof playbackRate !== "number") {
      return NextResponse.json(
        { success: false, error: "playbackRate must be a number" },
        { status: 400 }
      );
    }

    const now = new Date().toISOString();

    // Check if session exists
    const [existingSession] = await db
      .select()
      .from(playbackSessions)
      .where(eq(playbackSessions.audioFileId, audioFileId))
      .orderBy(desc(playbackSessions.lastPlayedAt))
      .limit(1);

    if (existingSession) {
      // Update existing session
      const [updated] = await db
        .update(playbackSessions)
        .set({
          currentPosition:
            currentPosition ?? existingSession.currentPosition,
          playbackRate: playbackRate ?? existingSession.playbackRate,
          completed: completed ?? existingSession.completed,
          lastPlayedAt: now,
          lastPlayedFrom: "web",
          updatedAt: now,
        })
        .where(eq(playbackSessions.id, existingSession.id))
        .returning();

      return NextResponse.json({ success: true, session: updated });
    } else {
      // Create new session
      const [created] = await db
        .insert(playbackSessions)
        .values({
          audioFileId,
          currentPosition: currentPosition ?? 0,
          playbackRate: playbackRate ?? 1.0,
          completed: completed ?? 0,
          lastPlayedAt: now,
          lastPlayedFrom: "web",
          updatedAt: now,
        })
        .returning();

      return NextResponse.json({ success: true, session: created });
    }
  } catch (error) {
    console.error("Playback session update error:", error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const audioFileId = parseInt(id, 10);

    if (isNaN(audioFileId)) {
      return NextResponse.json(
        { success: false, error: "Invalid audio file ID" },
        { status: 400 }
      );
    }

    // Get audio file with playback session
    const [audioFile] = await db
      .select()
      .from(audioFiles)
      .where(eq(audioFiles.id, audioFileId));

    if (!audioFile) {
      return NextResponse.json(
        { success: false, error: "Audio file not found" },
        { status: 404 }
      );
    }

    // Get latest playback session
    const [session] = await db
      .select()
      .from(playbackSessions)
      .where(eq(playbackSessions.audioFileId, audioFileId))
      .orderBy(desc(playbackSessions.lastPlayedAt))
      .limit(1);

    return NextResponse.json({
      success: true,
      audioFile,
      session: session || null,
    });
  } catch (error) {
    console.error("Audio file fetch error:", error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}
