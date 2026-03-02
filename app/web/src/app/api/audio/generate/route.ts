import { NextRequest, NextResponse } from "next/server";
import { generateAudio } from "@/modules/audio/generator";
import fs from "fs";
import path from "path";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { contentPath, title, voiceId, voiceName, model } = body;

    if (!contentPath) {
      return NextResponse.json(
        { success: false, error: "contentPath is required" },
        { status: 400 }
      );
    }

    // Resolve full path
    const fullPath = path.resolve(process.cwd(), "../../", contentPath);

    // Check if file exists
    if (!fs.existsSync(fullPath)) {
      return NextResponse.json(
        { success: false, error: `File not found: ${contentPath}` },
        { status: 404 }
      );
    }

    // Generate audio
    const result = await generateAudio({
      contentPath: fullPath,
      title,
      voiceId,
      voiceName,
      model,
    });

    return NextResponse.json({
      success: true,
      audioFileId: result.audioFileId,
      audioPath: result.audioPath,
      duration: result.duration,
      fileSize: result.fileSize,
    });
  } catch (error) {
    console.error("Audio generation error:", error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}
