import { sqliteTable, text, integer, real } from "drizzle-orm/sqlite-core";
import { type InferSelectModel, type InferInsertModel } from "drizzle-orm";

// ---------------------------------------------------------------------------
// audio_files - Generated audio files from markdown content
// ---------------------------------------------------------------------------
export const audioFiles = sqliteTable("audio_files", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  title: text("title").notNull(),
  contentPath: text("content_path").notNull(), // Original .md file path
  audioPath: text("audio_path").notNull(),     // Generated .mp3 file path
  duration: real("duration"),                   // Duration in seconds
  fileSize: integer("file_size"),               // File size in bytes
  voiceId: text("voice_id"),                    // ElevenLabs voice ID
  voiceName: text("voice_name"),                // Human-readable voice name
  model: text("model"),                         // ElevenLabs model used
  generatedAt: text("generated_at").notNull(),  // ISO timestamp
  updatedAt: text("updated_at").notNull(),      // ISO timestamp
});

// ---------------------------------------------------------------------------
// playback_sessions - Tracks playback state for resume functionality
// ---------------------------------------------------------------------------
export const playbackSessions = sqliteTable("playback_sessions", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  audioFileId: integer("audio_file_id")
    .notNull()
    .references(() => audioFiles.id),
  currentPosition: real("current_position").default(0),  // Position in seconds
  playbackRate: real("playback_rate").default(1.0),      // Speed: 0.5x - 2.0x
  completed: integer("completed").default(0),             // Boolean: finished listening
  lastPlayedAt: text("last_played_at").notNull(),        // ISO timestamp
  lastPlayedFrom: text("last_played_from"),              // "web" | "cli"
  updatedAt: text("updated_at").notNull(),               // ISO timestamp
});

// ---------------------------------------------------------------------------
// generation_runs - Tracks ElevenLabs API usage and generation history
// ---------------------------------------------------------------------------
export const generationRuns = sqliteTable("generation_runs", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  audioFileId: integer("audio_file_id").references(() => audioFiles.id),
  startedAt: text("started_at").notNull(),
  completedAt: text("completed_at"),
  charactersProcessed: integer("characters_processed").default(0),
  status: text("status").default("running"),  // running | completed | failed
  error: text("error"),
});

// ---------------------------------------------------------------------------
// Type helpers
// ---------------------------------------------------------------------------
export type AudioFile = InferSelectModel<typeof audioFiles>;
export type NewAudioFile = InferInsertModel<typeof audioFiles>;

export type PlaybackSession = InferSelectModel<typeof playbackSessions>;
export type NewPlaybackSession = InferInsertModel<typeof playbackSessions>;

export type GenerationRun = InferSelectModel<typeof generationRuns>;
export type NewGenerationRun = InferInsertModel<typeof generationRuns>;
