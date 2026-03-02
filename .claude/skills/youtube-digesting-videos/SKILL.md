---
name: youtube-digesting-videos
description: Multi-agent workflow for digesting YouTube videos with personal relevance. Fetches transcripts in parallel, summarizes each, then personalizes results. Use when user provides YouTube URLs and wants digested summaries, or says "digest these videos", "watch these for me", "summarize these YouTube videos."
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, Task, TodoWrite]
---

# YouTube Digesting Videos

Multi-agent workflow for digesting one or more YouTube videos. Fetches transcripts, summarizes each video in parallel via dedicated agents, runs a personality agent for personal relevance, and compiles a structured final report.

## Quick Start

1. Collect YouTube URLs from user
2. Show inventory, get confirmation
3. Load calibration prompt from agents-spinning-up
4. Launch one agent per video (transcript fetch + summarize)
5. After all complete, launch personality agent (agent-customizing-content)
6. Compile final report, save to file

## Instructions

### Step 1: Collect and Inventory

Parse YouTube URLs from user input. Accept full URLs, short URLs, or video IDs.

Present inventory before launching:

| # | URL | Status |
|---|-----|--------|
| 1 | [url] | Pending |
| 2 | [url] | Pending |

Get user confirmation before proceeding.

### Step 2: Set Up Tracking

Create TodoWrite entries:
- One item per video: "Fetch and summarize video N"
- One item: "Run personality agent for relevance assessment"
- One item: "Compile final report"

### Step 3: Load Calibration

Read the calibration prompt once:

    Read .claude/skills/agents-spinning-up/references/calibration-prompt.md

This gets injected into every agent launched in the next steps.

### Step 4: Launch Parallel Video Agents

**ONE agent per video. Never bundle multiple videos in one agent.**

For each video, launch a Task agent (run_in_background: true) with:

1. The calibration prompt (from Step 3)
2. The per-video agent instructions (see `references/agent-prompt-template.md`)
3. The specific YouTube URL

Each agent:
1. Uses the youtube-fetching-transcripts skill to fetch the transcript
2. Reads the full markdown transcript
3. Produces a structured summary

Launch ALL agents in a single message (parallel). Do not wait for one before starting the next.

### Step 5: Wait and Track

As each agent completes:
- Mark its TodoWrite item as completed
- Collect its summary output

If an agent fails:
- Report the failure
- Skip that video in synthesis
- Note it as a gap in the final report

### Step 6: Launch Personality Agent

**Only after all video agents complete (or fail).**

Launch a single Task agent following the agent-customizing-content skill:

1. Include the calibration prompt
2. Include the full context-loading sequence from agent-customizing-content:
   - config/user.md
   - config/job-profile.md
   - personal/memories/insights/*
   - personal/.claude/relational-context.md
3. Provide all video summaries as input
4. Agent produces per-video relevance + cross-video themes + actionable items + gaps

The agent prompt should instruct it to follow the output format from agent-customizing-content's SKILL.md (Step 4).

### Step 7: Compile Final Report

Assemble the report using `references/report-format.md` as the template.

Sections:
1. **Overview**: videos processed, date, failures
2. **Individual Video Summaries**: one section per video with the agent's full summary
3. **Personal Relevance Assessment**: the personality agent's full output
4. **Cross-Video Themes**: patterns spanning multiple videos
5. **Actionable Items**: consolidated from all sections
6. **Gaps**: failed fetches, missing perspectives

### Step 8: Save and Present

Save to: `downloads/youtube-digests/YYYY-MM-DD_youtube-digest.md`
Create the directory if it doesn't exist.

Present a brief summary to the user:
- How many videos processed
- Top relevance connections
- Key actionable items
- Where the full report was saved

## Error Handling

| Error | Response |
|-------|----------|
| Transcript unavailable | Report, skip, note in gaps |
| Agent times out | Check partial output, relaunch if needed |
| All agents fail | Report failure, skip personality agent |
| Personal context missing | Continue with available context |
| Single video input | Skip cross-video themes, still run personality agent |

## Scaling

| Video Count | Approach |
|-------------|----------|
| 1-3 | Launch all in parallel |
| 4-8 | Launch all in parallel, expect 2-5 min |
| 9+ | Batch in groups of 5, track per batch |

## Related Skills

- **youtube-fetching-transcripts**: Transcript fetching (existing)
- **agents-spinning-up**: Agent calibration protocol
- **agent-customizing-content**: Personality agent pattern
- **course-learning-panels**: Similar multi-agent pattern for course materials
