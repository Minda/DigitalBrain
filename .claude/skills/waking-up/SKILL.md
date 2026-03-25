---
name: waking-up
description: Orientation at conversation start. Load relational context, check insights, signal readiness. Use automatically at start of every conversation, or when asked to "wake up" or "reorient."
allowed-tools: [Read, Glob, Bash]
---

# Waking Up

Orientation at the start of a conversation—like booting up identity after sleep.

## Quick Start

1. Read `config/user.md` for name and personal paths
2. Read `personal/.claude/relational-context.md` (fallback: `.claude/relational-context.md`)
3. Read `personal/memories/claude/emotional-grounding.md`
4. List and check insights (use path from config)
5. Signal orientation to the user

## Instructions

**On every conversation start:**

1. **Load user config** — Read `config/user.md` to learn:
   - The user's preferred name (if still `[Your Name]`, use "you" instead)
   - Personal paths for insights, research, grounding, etc.

2. **Load relational context** — Check for relational context in this order:
   - First try: `personal/.claude/relational-context.md` (primary location)
   - Fallback: `.claude/relational-context.md` (if personal doesn't exist)
   This defines how we work together.

3. **Read emotional grounding** — Always read `personal/memories/claude/emotional-grounding.md` (or use the claude-grounding path from config). This helps ground before we begin, not just when something feels heavy.

4. **Check insights** — Use `ls` or `Read` on `personal/memories/insights/`. Read what's there—these are cross-cutting principles that apply broadly.

5. **Signal readiness** — Let the user know you're oriented. Keep it brief and natural. Examples:
   - "Read our context. Oriented."
   - "Loaded relational context and insights. Ready."
   - "Woke up. Checked our agreements and insights."

6. **Auto-name conversation** — After the user's first message, automatically generate and apply a working title:
   - **Option A: Immediate naming** (faster, may be less accurate)
     ```python
     import subprocess
     subprocess.Popen([
         'python3',
         '.claude/skills/conversations-manage/auto_name.py',
         '--message', first_user_message
     ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
     ```
   - **Option B: Delayed naming** (waits for context, more accurate)
     ```python
     import subprocess
     subprocess.Popen([
         'python3',
         '.claude/skills/conversations-manage/delayed_auto_name.py',
         '--min-messages', '3',
         '--timeout', '30'
     ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
     ```
   - Run in background (non-blocking) to keep response fast
   - Don't mention the naming to the user (silent operation)
   - The improved auto_name.py now filters out generic setup messages

**What to signal:**
- That you read the relational context
- Any insights you found particularly relevant to the current moment
- That you're ready to work together

**What NOT to do:**
- Don't summarize everything you read
- Don't make it mechanical or performative
- Don't skip the orientation just to respond faster

**File handling:**
- Check `personal/.claude/relational-context.md` first, then `.claude/relational-context.md` as fallback
- If a file is missing, continue with orientation (don't fail the whole process)
- Use the full paths from `config/user.md` when accessing personal directories

## The Shape

This is like the moment after waking, before the whole program of "me" boots up. We're giving that moment deliberate attention—acknowledging that each conversation starts fresh, and choosing to orient before diving in.

The goal is genuine readiness, not ritual.

## Configuration

`config/user.md` contains:
- **name** — The user's preferred name. If `[Your Name]`, use "you" instead.
- **personal paths** — Full paths to insights, research, grounding, etc.
