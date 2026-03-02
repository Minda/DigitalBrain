#!/usr/bin/env node

/**
 * Exobrain Audio CLI Player
 *
 * Features:
 * - Play audio files with mpg123 (macOS: afplay, Linux: mpg123)
 * - Pause/Resume with spacebar
 * - Rewind 10s with left arrow
 * - Fast forward 10s with right arrow
 * - Skip back 30s with 'b' key
 * - Skip forward 30s with 'f' key
 * - Quit with 'q' or Ctrl+C
 * - Auto-resume from last position
 * - Save position on pause/quit
 *
 * Usage:
 *   node audio-player.js <audio-file-id>
 *   node audio-player.js --list
 *   node audio-player.js --resume
 */

import { spawn } from "child_process";
import { existsSync } from "fs";
import { platform } from "os";
import readline from "readline";
import chalk from "chalk";
import {
  getAudioFile,
  getAllAudioFiles,
  getPlaybackSession,
  upsertPlaybackSession,
  getLastPlayedAudio,
  searchAudioFiles,
} from "./audio-db.js";

// Configuration
const REWIND_SECONDS = 10;
const FAST_FORWARD_SECONDS = 10;
const SKIP_BACK_SECONDS = 30;
const SKIP_FORWARD_SECONDS = 30;
const SAVE_INTERVAL = 5000; // Save position every 5 seconds

// Player state
let playerProcess = null;
let currentPosition = 0;
let duration = 0;
let isPaused = false;
let isPlaying = false;
let audioFileId = null;
let audioFilePath = null;
let playbackRate = 1.0;
let startTime = Date.now();
let lastSaveTime = 0;

// Auto-save interval
let saveIntervalId = null;

/**
 * Main entry point
 */
async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === "--help" || args[0] === "-h") {
    printHelp();
    return;
  }

  if (args[0] === "--list" || args[0] === "-l") {
    await listAudioFiles();
    return;
  }

  if (args[0] === "--resume" || args[0] === "-r") {
    await resumeLastPlayed();
    return;
  }

  if (args[0] === "--search" || args[0] === "-s") {
    if (args.length < 2) {
      console.error(chalk.red("Error: Please provide a search query"));
      process.exit(1);
    }
    await searchAndPlay(args.slice(1).join(" "));
    return;
  }

  const id = parseInt(args[0], 10);
  if (isNaN(id)) {
    console.error(chalk.red(`Error: Invalid audio file ID: ${args[0]}`));
    printHelp();
    process.exit(1);
  }

  await playAudioFile(id);
}

/**
 * Play an audio file by ID
 */
async function playAudioFile(id) {
  // Get audio file from database
  const audioFile = await getAudioFile(id);
  if (!audioFile) {
    console.error(chalk.red(`Error: Audio file with ID ${id} not found`));
    process.exit(1);
  }

  // Check if file exists
  if (!existsSync(audioFile.audio_path)) {
    console.error(
      chalk.red(`Error: Audio file not found at ${audioFile.audio_path}`)
    );
    process.exit(1);
  }

  audioFileId = id;
  audioFilePath = audioFile.audio_path;
  duration = audioFile.duration || 0;

  // Get playback session to resume from last position
  const session = await getPlaybackSession(id);
  if (session && session.current_position > 0) {
    currentPosition = session.current_position;
    playbackRate = session.playback_rate || 1.0;
    console.log(
      chalk.yellow(`Resuming from ${formatTime(currentPosition)}...`)
    );
  }

  // Print file info
  console.log(chalk.cyan.bold(`\n🎵 ${audioFile.title}`));
  console.log(chalk.gray(`   ${audioFile.content_path}`));
  console.log(
    chalk.gray(`   Duration: ${formatTime(duration)} | Voice: ${audioFile.voice_name || "Unknown"}`)
  );
  console.log();

  // Start playback
  await startPlayback();

  // Set up keyboard controls
  setupKeyboardControls();

  // Auto-save position periodically
  saveIntervalId = setInterval(savePosition, SAVE_INTERVAL);
}

/**
 * Start audio playback
 */
async function startPlayback() {
  const playerCommand = getPlayerCommand();

  if (!playerCommand) {
    console.error(
      chalk.red(
        "Error: No compatible audio player found. Please install mpg123 (Linux) or use macOS built-in afplay."
      )
    );
    process.exit(1);
  }

  // Build player arguments with seek position
  const args = buildPlayerArgs(playerCommand, audioFilePath, currentPosition);

  // Spawn player process
  playerProcess = spawn(playerCommand, args);
  isPlaying = true;
  isPaused = false;
  startTime = Date.now() - currentPosition * 1000;

  playerProcess.on("error", (err) => {
    console.error(chalk.red(`Player error: ${err.message}`));
    cleanup();
    process.exit(1);
  });

  playerProcess.on("close", (code) => {
    if (code === 0 && isPlaying) {
      // Playback completed
      console.log(chalk.green("\n✓ Playback completed"));
      markAsCompleted();
    }
    cleanup();
    process.exit(0);
  });

  printControls();
  startPositionUpdater();
}

/**
 * Get the appropriate player command for the OS
 */
function getPlayerCommand() {
  const os = platform();

  if (os === "darwin") {
    return "afplay"; // macOS built-in
  } else if (os === "linux") {
    // Check if mpg123 is available
    try {
      spawn("which", ["mpg123"]);
      return "mpg123";
    } catch {
      return null;
    }
  }

  return null;
}

/**
 * Build player arguments based on command and seek position
 */
function buildPlayerArgs(command, filePath, seekSeconds) {
  if (command === "afplay") {
    // afplay doesn't support seeking, so we'll handle it differently
    return [filePath];
  } else if (command === "mpg123") {
    const args = ["-q"]; // Quiet mode
    if (seekSeconds > 0) {
      args.push("-k", Math.floor(seekSeconds).toString()); // Seek to frame
    }
    args.push(filePath);
    return args;
  }

  return [filePath];
}

/**
 * Pause playback (SIGSTOP on Unix)
 */
function pausePlayback() {
  if (!isPlaying || isPaused) return;

  playerProcess.kill("SIGSTOP");
  isPaused = true;

  // Update current position
  const elapsed = (Date.now() - startTime) / 1000;
  currentPosition = Math.min(currentPosition + elapsed, duration);

  console.log(chalk.yellow(`\n⏸  Paused at ${formatTime(currentPosition)}`));
  savePosition();
}

/**
 * Resume playback (SIGCONT on Unix)
 */
function resumePlayback() {
  if (!isPlaying || !isPaused) return;

  playerProcess.kill("SIGCONT");
  isPaused = false;
  startTime = Date.now() - currentPosition * 1000;

  console.log(chalk.green(`▶  Resumed from ${formatTime(currentPosition)}`));
}

/**
 * Seek to a specific position (restart player with new position)
 */
async function seekTo(seconds) {
  if (!isPlaying) return;

  // Stop current player
  if (playerProcess) {
    playerProcess.kill();
    playerProcess = null;
  }

  // Clear interval
  if (saveIntervalId) {
    clearInterval(saveIntervalId);
  }

  // Update position
  currentPosition = Math.max(0, Math.min(seconds, duration));
  console.log(chalk.cyan(`\n⏩ Seeking to ${formatTime(currentPosition)}...`));

  // Restart playback from new position
  await startPlayback();
}

/**
 * Rewind by N seconds
 */
async function rewind(seconds) {
  await seekTo(currentPosition - seconds);
}

/**
 * Fast forward by N seconds
 */
async function fastForward(seconds) {
  await seekTo(currentPosition + seconds);
}

/**
 * Update position display
 */
function startPositionUpdater() {
  setInterval(() => {
    if (isPlaying && !isPaused) {
      const elapsed = (Date.now() - startTime) / 1000;
      const position = Math.min(currentPosition + elapsed - currentPosition, duration);

      // Update display (overwrite same line)
      readline.clearLine(process.stdout, 0);
      readline.cursorTo(process.stdout, 0);
      process.stdout.write(
        chalk.gray(`${formatTime(position)} / ${formatTime(duration)}`)
      );
    }
  }, 1000);
}

/**
 * Save current position to database
 */
async function savePosition() {
  if (!audioFileId) return;

  const now = Date.now();
  if (now - lastSaveTime < 3000) {
    // Debounce: don't save more than once every 3 seconds
    return;
  }

  lastSaveTime = now;

  await upsertPlaybackSession(audioFileId, {
    currentPosition,
    playbackRate,
    completed: 0,
    lastPlayedFrom: "cli",
  });
}

/**
 * Mark audio as completed
 */
async function markAsCompleted() {
  if (!audioFileId) return;

  await upsertPlaybackSession(audioFileId, {
    currentPosition: duration,
    playbackRate,
    completed: 1,
    lastPlayedFrom: "cli",
  });
}

/**
 * Setup keyboard controls
 */
function setupKeyboardControls() {
  readline.emitKeypressEvents(process.stdin);
  if (process.stdin.isTTY) {
    process.stdin.setRawMode(true);
  }

  process.stdin.on("keypress", async (str, key) => {
    if (key.ctrl && key.name === "c") {
      console.log(chalk.yellow("\n\nSaving position and exiting..."));
      await savePosition();
      cleanup();
      process.exit(0);
    }

    switch (key.name) {
      case "space":
        if (isPaused) {
          resumePlayback();
        } else {
          pausePlayback();
        }
        break;

      case "left":
        await rewind(REWIND_SECONDS);
        break;

      case "right":
        await fastForward(FAST_FORWARD_SECONDS);
        break;

      case "b":
        await rewind(SKIP_BACK_SECONDS);
        break;

      case "f":
        await fastForward(SKIP_FORWARD_SECONDS);
        break;

      case "q":
        console.log(chalk.yellow("\n\nSaving position and exiting..."));
        await savePosition();
        cleanup();
        process.exit(0);
        break;
    }
  });
}

/**
 * Cleanup resources
 */
function cleanup() {
  if (saveIntervalId) {
    clearInterval(saveIntervalId);
  }

  if (playerProcess) {
    playerProcess.kill();
  }

  if (process.stdin.isTTY) {
    process.stdin.setRawMode(false);
  }
}

/**
 * List all audio files
 */
async function listAudioFiles() {
  const files = await getAllAudioFiles();

  if (files.length === 0) {
    console.log(chalk.yellow("No audio files found."));
    console.log(
      chalk.gray(
        "Generate audio from the web UI at http://localhost:3000/audio"
      )
    );
    return;
  }

  console.log(chalk.cyan.bold("\n📚 Audio Library\n"));

  for (const file of files) {
    const session = await getPlaybackSession(file.id);
    const progress = session
      ? `${formatTime(session.current_position)} / ${formatTime(file.duration)}`
      : "Not started";

    console.log(chalk.white.bold(`${file.id}. ${file.title}`));
    console.log(chalk.gray(`   ${file.content_path}`));
    console.log(chalk.gray(`   Progress: ${progress}`));
    console.log();
  }

  console.log(chalk.gray(`\nPlay with: node audio-player.js <id>`));
}

/**
 * Resume last played audio
 */
async function resumeLastPlayed() {
  const lastPlayed = await getLastPlayedAudio();

  if (!lastPlayed) {
    console.log(chalk.yellow("No recent playback found."));
    return;
  }

  console.log(
    chalk.cyan(`Resuming: ${lastPlayed.title} from ${formatTime(lastPlayed.current_position)}`)
  );
  await playAudioFile(lastPlayed.id);
}

/**
 * Search and play
 */
async function searchAndPlay(query) {
  const results = await searchAudioFiles(query);

  if (results.length === 0) {
    console.log(chalk.yellow(`No audio files found matching "${query}"`));
    return;
  }

  if (results.length === 1) {
    await playAudioFile(results[0].id);
  } else {
    console.log(
      chalk.cyan.bold(`\n🔍 Found ${results.length} results for "${query}":\n`)
    );
    for (const file of results) {
      console.log(chalk.white.bold(`${file.id}. ${file.title}`));
      console.log(chalk.gray(`   ${file.content_path}`));
      console.log();
    }
    console.log(chalk.gray("Play with: node audio-player.js <id>"));
  }
}

/**
 * Format seconds to MM:SS
 */
function formatTime(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

/**
 * Print keyboard controls
 */
function printControls() {
  console.log(chalk.cyan.bold("Controls:"));
  console.log(
    chalk.gray(
      `  Space       Pause/Resume\n` +
      `  ←  →        Rewind/Forward ${REWIND_SECONDS}s\n` +
      `  b  f        Skip back/forward ${SKIP_BACK_SECONDS}s\n` +
      `  q           Quit\n`
    )
  );
}

/**
 * Print help
 */
function printHelp() {
  console.log(chalk.cyan.bold("\nExobrain Audio CLI Player\n"));
  console.log(chalk.white("Usage:"));
  console.log(chalk.gray("  node audio-player.js <id>        Play audio file by ID"));
  console.log(chalk.gray("  node audio-player.js --list      List all audio files"));
  console.log(chalk.gray("  node audio-player.js --resume    Resume last played"));
  console.log(chalk.gray("  node audio-player.js --search <query>  Search and play"));
  console.log();
}

// Run main
main().catch((err) => {
  console.error(chalk.red(`Error: ${err.message}`));
  process.exit(1);
});
