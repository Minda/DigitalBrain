"use client";

import { useEffect, useRef, useState } from "react";
import { AudioFile, PlaybackSession } from "@/modules/audio/schema";

interface AudioPlayerProps {
  audioFile: AudioFile;
  session: PlaybackSession | null;
  onPositionUpdate: (position: number) => void;
  onComplete: () => void;
}

export function AudioPlayer({
  audioFile,
  session,
  onPositionUpdate,
  onComplete,
}: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(session?.currentPosition ?? 0);
  const [duration, setDuration] = useState(audioFile.duration ?? 0);
  const [playbackRate, setPlaybackRate] = useState(session?.playbackRate ?? 1.0);

  // Restore playback position on mount
  useEffect(() => {
    if (audioRef.current && session?.currentPosition) {
      audioRef.current.currentTime = session.currentPosition;
    }
  }, [session]);

  // Update playback rate
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.playbackRate = playbackRate;
    }
  }, [playbackRate]);

  // Save position periodically
  useEffect(() => {
    const interval = setInterval(() => {
      if (audioRef.current && isPlaying) {
        onPositionUpdate(audioRef.current.currentTime);
      }
    }, 5000); // Save every 5 seconds

    return () => clearInterval(interval);
  }, [isPlaying, onPositionUpdate]);

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  };

  const handleEnded = () => {
    setIsPlaying(false);
    onComplete();
  };

  const handlePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleSeek = (seconds: number) => {
    if (audioRef.current) {
      audioRef.current.currentTime = Math.max(
        0,
        Math.min(audioRef.current.currentTime + seconds, duration)
      );
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const progressPercent = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <div className="rounded-lg border border-zinc-200 bg-white p-6">
      <div className="mb-4">
        <h2 className="text-xl font-semibold text-zinc-900">
          {audioFile.title}
        </h2>
        <p className="text-sm text-zinc-500 mt-1">{audioFile.contentPath}</p>
      </div>

      <audio
        ref={audioRef}
        src={audioFile.audioPath}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={handleEnded}
        className="hidden"
      />

      {/* Progress bar */}
      <div className="mb-4">
        <div className="h-2 bg-zinc-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-blue-600 transition-all"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
        <div className="flex justify-between text-sm text-zinc-600 mt-2">
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(duration)}</span>
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center justify-center gap-4 mb-4">
        <button
          onClick={() => handleSeek(-30)}
          className="p-2 rounded-lg hover:bg-zinc-100 text-zinc-700"
          title="Rewind 30s"
        >
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0019 16V8a1 1 0 00-1.6-.8l-5.333 4zM4.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0011 16V8a1 1 0 00-1.6-.8l-5.334 4z"
            />
          </svg>
        </button>

        <button
          onClick={() => handleSeek(-10)}
          className="p-2 rounded-lg hover:bg-zinc-100 text-zinc-700"
          title="Rewind 10s"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0019 16V8a1 1 0 00-1.6-.8l-5.333 4z"
            />
          </svg>
        </button>

        <button
          onClick={handlePlayPause}
          className="p-4 rounded-full bg-blue-600 hover:bg-blue-700 text-white shadow-lg"
        >
          {isPlaying ? (
            <svg
              className="w-8 h-8"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
            </svg>
          ) : (
            <svg
              className="w-8 h-8"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M8 5v14l11-7z" />
            </svg>
          )}
        </button>

        <button
          onClick={() => handleSeek(10)}
          className="p-2 rounded-lg hover:bg-zinc-100 text-zinc-700"
          title="Forward 10s"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M11.933 12.8a1 1 0 000-1.6L6.6 7.2A1 1 0 005 8v8a1 1 0 001.6.8l5.333-4z"
            />
          </svg>
        </button>

        <button
          onClick={() => handleSeek(30)}
          className="p-2 rounded-lg hover:bg-zinc-100 text-zinc-700"
          title="Forward 30s"
        >
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M11.933 12.8a1 1 0 000-1.6L6.6 7.2A1 1 0 005 8v8a1 1 0 001.6.8l5.333 4zM19.933 12.8a1 1 0 000-1.6l-5.333-4A1 1 0 0013 8v8a1 1 0 001.6.8l5.333-4z"
            />
          </svg>
        </button>
      </div>

      {/* Playback speed */}
      <div className="flex items-center justify-center gap-2">
        <span className="text-sm text-zinc-600">Speed:</span>
        {[0.5, 0.75, 1.0, 1.25, 1.5, 2.0].map((speed) => (
          <button
            key={speed}
            onClick={() => setPlaybackRate(speed)}
            className={`px-3 py-1 text-sm rounded ${
              playbackRate === speed
                ? "bg-blue-600 text-white"
                : "bg-zinc-100 text-zinc-700 hover:bg-zinc-200"
            }`}
          >
            {speed}x
          </button>
        ))}
      </div>

      {/* Keyboard shortcuts hint */}
      <div className="mt-4 pt-4 border-t border-zinc-200">
        <p className="text-xs text-zinc-500 text-center">
          Tip: Use arrow keys (← →) to skip, spacebar to play/pause
        </p>
      </div>
    </div>
  );
}
