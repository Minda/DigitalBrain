import { db } from "@/modules/audio/db";
import { audioFiles, playbackSessions } from "@/modules/audio/schema";
import { desc, eq } from "drizzle-orm";
import { AudioPlayer } from "./audio-player";
import Link from "next/link";

export const dynamic = "force-dynamic";

export default async function AudioPage() {
  // Get all audio files with their playback sessions
  const allAudioFiles = await db
    .select()
    .from(audioFiles)
    .orderBy(desc(audioFiles.generatedAt));

  const audioFilesWithSessions = await Promise.all(
    allAudioFiles.map(async (file) => {
      const [session] = await db
        .select()
        .from(playbackSessions)
        .where(eq(playbackSessions.audioFileId, file.id))
        .orderBy(desc(playbackSessions.lastPlayedAt))
        .limit(1);

      return { file, session: session || null };
    })
  );

  // Get most recently played
  const mostRecentlyPlayed = audioFilesWithSessions
    .filter((item) => item.session)
    .sort((a, b) => {
      const timeA = new Date(a.session!.lastPlayedAt).getTime();
      const timeB = new Date(b.session!.lastPlayedAt).getTime();
      return timeB - timeA;
    })[0];

  return (
    <div className="min-h-screen bg-zinc-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-zinc-900">
                Audio Library
              </h1>
              <p className="text-zinc-600 mt-2">
                Listen to your articles and notes with text-to-speech
              </p>
            </div>
            <Link
              href="/"
              className="px-4 py-2 text-sm font-medium text-zinc-700 hover:text-zinc-900"
            >
              ← Back to Portal
            </Link>
          </div>
        </div>

        {allAudioFiles.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-zinc-600 mb-4">
              No audio files yet. Generate your first one from the API.
            </p>
            <div className="bg-zinc-100 rounded-lg p-6 max-w-2xl mx-auto text-left">
              <p className="text-sm text-zinc-700 font-mono mb-2">
                POST /api/audio/generate
              </p>
              <pre className="text-xs text-zinc-600 overflow-x-auto">
                {JSON.stringify(
                  {
                    contentPath: "downloads/articles/some-article.md",
                    title: "My Article",
                    voiceId: "21m00Tcm4TlvDq8ikWAM",
                  },
                  null,
                  2
                )}
              </pre>
            </div>
          </div>
        ) : (
          <>
            {/* Currently Playing / Resume */}
            {mostRecentlyPlayed && !mostRecentlyPlayed.session?.completed && (
              <div className="mb-8">
                <h2 className="text-xl font-semibold text-zinc-900 mb-4">
                  Continue Listening
                </h2>
                <AudioPlayerWrapper
                  audioFile={mostRecentlyPlayed.file}
                  session={mostRecentlyPlayed.session}
                />
              </div>
            )}

            {/* Library */}
            <div>
              <h2 className="text-xl font-semibold text-zinc-900 mb-4">
                All Audio Files ({allAudioFiles.length})
              </h2>
              <div className="space-y-4">
                {audioFilesWithSessions.map(({ file, session }) => (
                  <div
                    key={file.id}
                    className="rounded-lg border border-zinc-200 bg-white p-4"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-zinc-900">
                          {file.title}
                        </h3>
                        <p className="text-sm text-zinc-500 mt-1">
                          {file.contentPath}
                        </p>
                        <div className="flex gap-4 mt-2 text-xs text-zinc-600">
                          <span>
                            Duration: {formatDuration(file.duration ?? 0)}
                          </span>
                          <span>Voice: {file.voiceName ?? "Unknown"}</span>
                          {session && (
                            <span>
                              Progress:{" "}
                              {Math.floor(
                                ((session.currentPosition ?? 0) /
                                  (file.duration ?? 1)) *
                                  100
                              )}
                              %
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="ml-4">
                        {session?.completed ? (
                          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
                            ✓ Completed
                          </span>
                        ) : session ? (
                          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                            In Progress
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-zinc-100 text-zinc-700">
                            Not Started
                          </span>
                        )}
                      </div>
                    </div>

                    {/* CLI playback instruction */}
                    <div className="mt-3 pt-3 border-t border-zinc-100">
                      <p className="text-xs text-zinc-500 font-mono">
                        CLI: node src/node/audio-player.js {file.id}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function AudioPlayerWrapper({
  audioFile,
  session,
}: {
  audioFile: any;
  session: any;
}) {
  const handlePositionUpdate = async (position: number) => {
    await fetch(`/api/audio/${audioFile.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ currentPosition: position }),
    });
  };

  const handleComplete = async () => {
    await fetch(`/api/audio/${audioFile.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ completed: 1, currentPosition: audioFile.duration }),
    });
  };

  return (
    <AudioPlayer
      audioFile={audioFile}
      session={session}
      onPositionUpdate={handlePositionUpdate}
      onComplete={handleComplete}
    />
  );
}

function formatDuration(seconds: number) {
  const hours = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  if (hours > 0) {
    return `${hours}:${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  }
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}
