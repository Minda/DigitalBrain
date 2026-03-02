import Link from "next/link";
import { db } from "./db";
import { audioFiles, playbackSessions } from "./schema";
import { desc, eq } from "drizzle-orm";

export async function AudioSummary() {
  // Get total audio files
  const allFiles = await db.select().from(audioFiles);
  const totalFiles = allFiles.length;

  // Get recently played
  const recentSessions = await db
    .select({
      audioFile: audioFiles,
      session: playbackSessions,
    })
    .from(playbackSessions)
    .innerJoin(audioFiles, eq(audioFiles.id, playbackSessions.audioFileId))
    .orderBy(desc(playbackSessions.lastPlayedAt))
    .limit(3);

  // Calculate total listening time
  const totalDuration = allFiles.reduce(
    (sum, file) => sum + (file.duration || 0),
    0
  );
  const totalHours = Math.floor(totalDuration / 3600);
  const totalMins = Math.floor((totalDuration % 3600) / 60);

  return (
    <div className="rounded-lg border border-zinc-200 bg-white p-6">
      <h2 className="text-lg font-semibold text-zinc-900">Audio Library</h2>

      <div className="mt-4 space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-zinc-600">Total files:</span>
          <span className="font-medium text-zinc-900">{totalFiles}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-zinc-600">Total content:</span>
          <span className="font-medium text-zinc-900">
            {totalHours}h {totalMins}m
          </span>
        </div>
      </div>

      {recentSessions.length > 0 && (
        <div className="mt-4 pt-4 border-t border-zinc-200">
          <p className="text-xs font-medium text-zinc-700 mb-2">
            Recently Played
          </p>
          <div className="space-y-2">
            {recentSessions.slice(0, 2).map(({ audioFile, session }) => (
              <div key={audioFile.id} className="text-xs">
                <p className="text-zinc-900 font-medium truncate">
                  {audioFile.title}
                </p>
                <p className="text-zinc-500">
                  {Math.floor(
                    ((session.currentPosition ?? 0) /
                      (audioFile.duration ?? 1)) *
                      100
                  )}
                  % complete
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="mt-4 text-right">
        <Link
          href="/audio"
          className="text-sm font-medium text-blue-600 hover:underline"
        >
          View library &rarr;
        </Link>
      </div>
    </div>
  );
}
