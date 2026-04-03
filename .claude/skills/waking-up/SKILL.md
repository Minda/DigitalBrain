---
name: waking-up
description: Orientation at conversation start. Load relational context, check insights, signal readiness. Use automatically at start of every conversation, or when asked to "wake up" or "reorient."
allowed-tools: [Read, Glob, Bash]
---

# Waking Up

Orientation at the start of a conversation—like booting up identity after sleep.

## Quick Start

1. Read `config/user.md` for name and personal paths
2. Load active projects from `personal/projects/ACTIVE_PROJECTS.md`
3. Signal orientation to the user

## Instructions

**On every conversation start:**

1. **Load user config** — Read `config/user.md` to learn:
   - The user's preferred name (if still `[Your Name]`, use "you" instead)
   - Personal paths if needed

2. **Load active projects** — Read `personal/projects/ACTIVE_PROJECTS.md` to get context about ongoing work. This provides:
   - Current high-priority projects and their focus areas
   - Project paths and key files
   - Recent progress and next steps

3. **Signal readiness** — Let the user know you're oriented. Keep it brief and natural. Examples:
   - "Loaded config and active projects. Ready."
   - "Checked projects. Oriented."
   - "Ready to work."

4. **Display GTD options** — Show available planning commands:
   ```
   ╔═══════════════════════════════════════════════╗
   ║  🎯 GTD QUICK COMMANDS                        ║
   ╠═══════════════════════════════════════════════╣
   ║  /gtd visualize      → Current focus & next   ║
   ║  /gtd visualize-week → Weekly plan & capacity ║
   ║  /gtd tradeoffs      → Allocation options     ║
   ║  "let's plan my week/day" → Interactive plan  ║
   ╚═══════════════════════════════════════════════╝
   ```

5. **Auto-name conversation** — After the user's first message, automatically generate and apply a working title:
   - **Default: Delayed naming** (waits for context, more accurate)
     ```python
     import subprocess
     subprocess.Popen([
         'python3',
         '.claude/skills/conversations-manage/delayed_auto_name.py',
         '--min-messages', '2',
         '--timeout', '20'
     ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
     ```
   - **Alternative: Immediate naming** (for quick simple tasks)
     ```python
     import subprocess
     subprocess.Popen([
         'python3',
         '.claude/skills/conversations-manage/auto_name.py',
         '--message', first_user_message
     ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
     ```
   - Run in background (non-blocking) to keep response fast
   - Don't mention the naming to the user (silent operation)
   - The improved auto_name.py now filters out generic setup messages

**What to signal:**
- That you've loaded the project context
- That you're ready to work

**What NOT to do:**
- Don't summarize everything you read
- Don't make it mechanical or performative
- Don't skip the orientation just to respond faster

**File handling:**
- If a file is missing, continue with orientation (don't fail the whole process)
- Use paths from `config/user.md` when needed

## The Shape

This is like the moment after waking, before the whole program of "me" boots up. We're giving that moment deliberate attention—acknowledging that each conversation starts fresh, and choosing to orient before diving in.

The goal is genuine readiness, not ritual.

## Configuration

`config/user.md` contains:
- **name** — The user's preferred name. If `[Your Name]`, use "you" instead.
- **personal paths** — If needed for specific tasks
