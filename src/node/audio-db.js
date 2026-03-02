/**
 * Shared database access for audio playback state
 * Works with SQLite database created by the Next.js app
 */

import { createClient } from "@libsql/client";
import { fileURLToPath } from "url";
import { dirname, join } from "path";
import fs from "fs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Path to the audio database (shared with Next.js app)
const DB_PATH = join(__dirname, "../../data/audio.db");

// Initialize database client
let db;

function getDB() {
  if (!db) {
    // Ensure database exists
    if (!fs.existsSync(DB_PATH)) {
      throw new Error(
        `Database not found at ${DB_PATH}. Run 'pnpm db:push' in app/web first.`
      );
    }

    db = createClient({
      url: `file:${DB_PATH}`,
    });
  }
  return db;
}

/**
 * Get audio file by ID
 */
export async function getAudioFile(id) {
  const db = getDB();
  const result = await db.execute({
    sql: "SELECT * FROM audio_files WHERE id = ?",
    args: [id],
  });
  return result.rows[0] || null;
}

/**
 * Get all audio files
 */
export async function getAllAudioFiles() {
  const db = getDB();
  const result = await db.execute(
    "SELECT * FROM audio_files ORDER BY generated_at DESC"
  );
  return result.rows;
}

/**
 * Get playback session for an audio file
 */
export async function getPlaybackSession(audioFileId) {
  const db = getDB();
  const result = await db.execute({
    sql: `
      SELECT * FROM playback_sessions
      WHERE audio_file_id = ?
      ORDER BY last_played_at DESC
      LIMIT 1
    `,
    args: [audioFileId],
  });
  return result.rows[0] || null;
}

/**
 * Create or update playback session
 */
export async function upsertPlaybackSession(audioFileId, data) {
  const db = getDB();
  const now = new Date().toISOString();

  const existing = await getPlaybackSession(audioFileId);

  if (existing) {
    // Update existing session
    await db.execute({
      sql: `
        UPDATE playback_sessions
        SET current_position = ?,
            playback_rate = ?,
            completed = ?,
            last_played_at = ?,
            last_played_from = ?,
            updated_at = ?
        WHERE id = ?
      `,
      args: [
        data.currentPosition ?? existing.current_position,
        data.playbackRate ?? existing.playback_rate,
        data.completed ?? existing.completed,
        now,
        data.lastPlayedFrom ?? "cli",
        now,
        existing.id,
      ],
    });
    return existing.id;
  } else {
    // Create new session
    const result = await db.execute({
      sql: `
        INSERT INTO playback_sessions
        (audio_file_id, current_position, playback_rate, completed, last_played_at, last_played_from, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
      `,
      args: [
        audioFileId,
        data.currentPosition ?? 0,
        data.playbackRate ?? 1.0,
        data.completed ?? 0,
        now,
        data.lastPlayedFrom ?? "cli",
        now,
      ],
    });
    return result.lastInsertRowid;
  }
}

/**
 * Get the most recently played audio file
 */
export async function getLastPlayedAudio() {
  const db = getDB();
  const result = await db.execute(`
    SELECT af.*, ps.current_position, ps.playback_rate, ps.completed
    FROM audio_files af
    JOIN playback_sessions ps ON af.id = ps.audio_file_id
    ORDER BY ps.last_played_at DESC
    LIMIT 1
  `);
  return result.rows[0] || null;
}

/**
 * Search audio files by title
 */
export async function searchAudioFiles(query) {
  const db = getDB();
  const result = await db.execute({
    sql: `
      SELECT * FROM audio_files
      WHERE title LIKE ? OR content_path LIKE ?
      ORDER BY generated_at DESC
    `,
    args: [`%${query}%`, `%${query}%`],
  });
  return result.rows;
}
