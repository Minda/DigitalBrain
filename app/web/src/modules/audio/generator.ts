import fs from "fs";
import path from "path";
import { db } from "./db";
import { audioFiles, generationRuns } from "./schema";
import { eq } from "drizzle-orm";

// ElevenLabs API configuration
const ELEVENLABS_API_KEY = process.env.ELEVENLABS_API_KEY;
const ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1";

// Default voice settings
const DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"; // Rachel (default ElevenLabs voice)
const DEFAULT_MODEL = "eleven_monolingual_v1";

export interface GenerateAudioOptions {
  contentPath: string;
  title?: string;
  voiceId?: string;
  voiceName?: string;
  model?: string;
}

export interface GenerateAudioResult {
  audioFileId: number;
  audioPath: string;
  duration: number;
  fileSize: number;
}

/**
 * Generate audio from markdown content using ElevenLabs API
 */
export async function generateAudio(
  options: GenerateAudioOptions
): Promise<GenerateAudioResult> {
  if (!ELEVENLABS_API_KEY) {
    throw new Error("ELEVENLABS_API_KEY environment variable is not set");
  }

  const {
    contentPath,
    title,
    voiceId = DEFAULT_VOICE_ID,
    voiceName = "Rachel",
    model = DEFAULT_MODEL,
  } = options;

  // Start generation run tracking
  const now = new Date().toISOString();
  const [runRecord] = await db
    .insert(generationRuns)
    .values({
      startedAt: now,
      status: "running",
    })
    .returning();

  try {
    // Read and process markdown content
    const content = fs.readFileSync(contentPath, "utf-8");
    const textContent = stripMarkdown(content);
    const charactersProcessed = textContent.length;

    // Generate output filename
    const baseName = path.basename(contentPath, path.extname(contentPath));
    const audioFileName = `${baseName}-${Date.now()}.mp3`;
    const audioPath = path.join(
      process.cwd(),
      "../../downloads/audio",
      audioFileName
    );

    // Ensure output directory exists
    const audioDir = path.dirname(audioPath);
    if (!fs.existsSync(audioDir)) {
      fs.mkdirSync(audioDir, { recursive: true });
    }

    // Call ElevenLabs text-to-speech API
    const response = await fetch(
      `${ELEVENLABS_API_URL}/text-to-speech/${voiceId}`,
      {
        method: "POST",
        headers: {
          "xi-api-key": ELEVENLABS_API_KEY,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: textContent,
          model_id: model,
          voice_settings: {
            stability: 0.5,
            similarity_boost: 0.75,
          },
        }),
      }
    );

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`ElevenLabs API error: ${response.status} - ${error}`);
    }

    // Save audio file
    const audioBuffer = await response.arrayBuffer();
    fs.writeFileSync(audioPath, Buffer.from(audioBuffer));

    // Get file stats
    const stats = fs.statSync(audioPath);
    const fileSize = stats.size;

    // Get audio duration (approximate: MP3 bitrate ~128kbps)
    const duration = estimateAudioDuration(fileSize);

    // Save to database
    const [audioFile] = await db
      .insert(audioFiles)
      .values({
        title: title || baseName,
        contentPath,
        audioPath,
        duration,
        fileSize,
        voiceId,
        voiceName,
        model,
        generatedAt: now,
        updatedAt: now,
      })
      .returning();

    // Update generation run
    await db
      .update(generationRuns)
      .set({
        audioFileId: audioFile.id,
        charactersProcessed,
        completedAt: new Date().toISOString(),
        status: "completed",
      })
      .where(eq(generationRuns.id, runRecord.id));

    return {
      audioFileId: audioFile.id,
      audioPath,
      duration,
      fileSize,
    };
  } catch (error) {
    // Mark run as failed
    await db
      .update(generationRuns)
      .set({
        completedAt: new Date().toISOString(),
        status: "failed",
        error: error instanceof Error ? error.message : String(error),
      })
      .where(eq(generationRuns.id, runRecord.id));

    throw error;
  }
}

/**
 * Strip markdown formatting to get plain text for TTS
 */
function stripMarkdown(markdown: string): string {
  let text = markdown;

  // Remove code blocks
  text = text.replace(/```[\s\S]*?```/g, "");
  text = text.replace(/`[^`]+`/g, "");

  // Remove images
  text = text.replace(/!\[.*?\]\(.*?\)/g, "");

  // Remove links but keep text
  text = text.replace(/\[([^\]]+)\]\([^\)]+\)/g, "$1");

  // Remove headings markers
  text = text.replace(/^#{1,6}\s+/gm, "");

  // Remove bold/italic
  text = text.replace(/(\*\*|__)(.*?)\1/g, "$2");
  text = text.replace(/(\*|_)(.*?)\1/g, "$2");

  // Remove horizontal rules
  text = text.replace(/^(-{3,}|\*{3,}|_{3,})$/gm, "");

  // Remove list markers
  text = text.replace(/^[\s]*[-*+]\s+/gm, "");
  text = text.replace(/^[\s]*\d+\.\s+/gm, "");

  // Clean up extra whitespace
  text = text.replace(/\n{3,}/g, "\n\n");
  text = text.trim();

  return text;
}

/**
 * Estimate audio duration based on file size (approximate)
 * Assumes ~128kbps MP3 encoding
 */
function estimateAudioDuration(fileSize: number): number {
  const BITRATE = 128000; // 128 kbps in bits per second
  const BYTES_PER_SECOND = BITRATE / 8;
  return fileSize / BYTES_PER_SECOND;
}

/**
 * Get available ElevenLabs voices
 */
export async function getVoices() {
  if (!ELEVENLABS_API_KEY) {
    throw new Error("ELEVENLABS_API_KEY environment variable is not set");
  }

  const response = await fetch(`${ELEVENLABS_API_URL}/voices`, {
    headers: {
      "xi-api-key": ELEVENLABS_API_KEY,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch voices: ${response.status}`);
  }

  const data = await response.json();
  return data.voices;
}
