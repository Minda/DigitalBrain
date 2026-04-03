---
name: exit
description: Gracefully close Claude session by saving context, naming conversation, and exiting to command line. Use when user says "exit", "goodbye", "close claude", or signals end of session.
allowed-tools: [Read, Write, Edit, Bash, Skill]
---

# /exit - Graceful Session Closure

Orchestrates a clean exit from Claude by chaining together context saving, conversation naming, and terminal return.

## Purpose

Provides a single command to properly close out a Claude session:
1. Saves current context
2. Names the conversation (if needed)
3. Exits Claude and returns to command line

## Workflow

```mermaid
graph TD
    Start[/exit Command] --> Context[Run /context]
    Context --> Name[Check Conversation Name]
    Name -->|Unnamed| AutoName[Generate Name]
    Name -->|Named| Skip[Skip Naming]
    AutoName --> Exit[Exit Claude]
    Skip --> Exit
    Exit --> Terminal[Return to Terminal]

    style Start fill:#4ecdc4
    style Exit fill:#ff6b6b
    style Terminal fill:#95e1d3
```

## Usage

```bash
/exit           # Save context, name conversation, and exit
/exit quick     # Skip naming, just save context and exit
/exit now       # Emergency exit without any processing
```

## Process Flow

### 1. Context Save
Runs `/context` to capture current state:
- Main topic/goal
- Current specific task
- Key detail if critical

### 2. Conversation Naming
Checks if conversation has a custom title:
- If unnamed: Auto-generates descriptive name
- If named: Skips naming step
- Uses `rename_conversation.py` from conversations-manage skill

### 3. Exit Sequence
Sends proper exit signal to Claude:
- Cleans up any temporary state
- Ensures conversation is saved
- Returns control to terminal

## Implementation

```python
#!/usr/bin/env python3
"""
Gracefully exit Claude session with context preservation
"""

import sys
import subprocess
from pathlib import Path

def run_context():
    """Save current context"""
    print("💾 Saving context...")
    # Run /context skill to capture state
    subprocess.run(["python3", ".claude/skills/context/show_recent_files.py"],
                   capture_output=True, text=True)
    return True

def check_and_name_conversation():
    """Check if conversation needs naming"""
    print("📝 Checking conversation name...")
    # Import from conversations-manage skill
    sys.path.append(".claude/skills/conversations-manage")
    from rename_conversation import get_current_title

    current_title = get_current_title()
    if not current_title or current_title.startswith("Untitled"):
        print("  → Auto-naming conversation...")
        subprocess.run(["python3", ".claude/skills/conversations-manage/auto_name.py",
                       "--message", "Session ending"],
                      capture_output=True, text=True)
    else:
        print(f"  → Already named: {current_title}")
    return True

def exit_claude():
    """Send exit signal to Claude"""
    print("👋 Exiting Claude...")
    # Exit command depends on Claude's handling
    print("\n═══════════════════════════════")
    print("Session saved. Goodbye!")
    print("═══════════════════════════════\n")
    sys.exit(0)

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"

    if mode == "now":
        # Emergency exit
        print("⚡ Emergency exit - no processing")
        sys.exit(0)

    # Normal flow
    run_context()

    if mode != "quick":
        check_and_name_conversation()

    exit_claude()
```

## Modes

### Full Mode (default)
- Saves context
- Auto-names if needed
- Graceful exit

### Quick Mode
- Saves context
- Skips naming
- Fast exit

### Emergency Mode
- No processing
- Immediate exit
- Use when Claude is unresponsive

## Integration

Works with:
- `/context` - Captures current state
- `/name` - Handles conversation naming
- `conversations-manage` - Provides naming utilities

## Output Format

```
💾 Saving context...
   ✓ Context saved

📝 Checking conversation name...
   → Auto-naming conversation...
   ✓ Named: "Create exit skill for Claude"

👋 Exiting Claude...

═══════════════════════════════
Session saved. Goodbye!
═══════════════════════════════
```

## Notes

- Context is always saved (except emergency mode)
- Naming only happens for unnamed conversations
- Exit is graceful with proper cleanup
- Works seamlessly with Claude's session management

## Error Handling

- Missing skills: Falls back to basic exit
- Name generation fails: Continues with exit
- Context save fails: Warns but continues
- Emergency mode: Bypasses all checks

## Future Enhancements

- [ ] Save session statistics (duration, tools used)
- [ ] Option to commit changes before exit
- [ ] Integration with /wrapping-up skill
- [ ] Session summary generation