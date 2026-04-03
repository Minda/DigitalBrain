Base directory for this skill: /Users/min/Documents/Projects/DigitalBrain/.claude/skills/rename

# Rename Skill

Quick-trigger skill for renaming various items: conversations, terminal titles, files, and more. Primary focus is on conversation renaming with smart title suggestions.

## Primary Trigger

- **"rename"** - Instantly triggers conversation renaming with smart suggestions
- **"/rename"** - Command version of the trigger

## Additional Triggers

- "rename this"
- "change the name"
- "update the title"
- "rename terminal"
- "rename tab"
- "call this"
- "title this"

## Commands

- `/rename` - Default: Rename current conversation with smart suggestions
- `/rename conversation` - Explicitly rename conversation
- `/rename terminal [title]` - Rename terminal tab/window
- `/rename file [path]` - Rename a file (future)
- `/rename project` - Rename project (future)

## Workflow

### Default Flow (Just "rename")

When user says just "rename" or "/rename":

1. **Analyze current context** to determine what to rename
2. **If in a conversation**: Trigger smart title suggestions
3. **Generate 4 intelligent options** based on conversation content
4. **Let user choose** via AskUserQuestion tool
5. **Apply the rename** immediately to conversation
6. **Sync terminal title** automatically to match

### Smart Title Generation

The skill uses the conversations-manage skill's intelligence to:
- Analyze conversation content for key terms, actions, files
- Generate 4 differentiated titles that start with unique words
- **Keep titles concise: 5-6 words maximum**
- Prioritize actionable information (verbs, specific nouns)
- Make titles scannable at a glance
- Use specific details over generic descriptions

## Implementation

**IMPORTANT: Always use the proper rename script, not manual JSON editing!**

The rename_conversation.py script does TWO critical things:
1. Updates `customTitle` in the first-line metadata
2. Adds a dedicated `custom-title` type entry to the JSONL

**Fail Mode:** Only updating the metadata field will not properly rename the conversation in Claude's interface. You MUST add the custom-title entry.

### Correct Usage

```bash
# Always use the proper script
python3 .claude/skills/conversations-manage/rename_conversation.py "New Title"
```

```python
#!/usr/bin/env python3
"""
Quick rename orchestrator - determines what to rename and delegates
"""

import os
import sys
import subprocess
from pathlib import Path

# Import from conversations-manage skill
sys.path.insert(0, '/Users/min/Documents/Projects/DigitalBrain/.claude/skills/conversations-manage')
from suggest_titles import suggest_conversation_titles


def quick_rename(target=None, custom_title=None):
    """
    Quick rename based on context

    Args:
        target: Optional target (conversation, terminal, file)
        custom_title: Optional pre-specified title
    """

    if not target or target == "conversation":
        # Default: rename current conversation
        return rename_current_conversation(custom_title)
    elif target == "terminal":
        return rename_terminal(custom_title)
    else:
        return f"Don't know how to rename '{target}' yet"


def rename_current_conversation(custom_title=None):
    """Rename current conversation with smart suggestions"""

    if custom_title:
        # IMPORTANT: Use the rename_conversation.py script via subprocess
        # Do NOT manually edit the JSONL file
        script_path = '/Users/min/Documents/Projects/DigitalBrain/.claude/skills/conversations-manage/rename_conversation.py'
        result = subprocess.run(
            ['python3', script_path, custom_title],
            capture_output=True,
            text=True
        )
        return result.stdout

    # Generate smart suggestions
    suggestions, conv_file = suggest_conversation_titles()

    if not suggestions:
        return "Could not analyze conversation for suggestions"

    # In Claude, we'll use AskUserQuestion to let user choose
    # For CLI testing, we can show the suggestions
    print("\n🎯 Quick Rename - Choose a title:")
    print("=" * 60)

    for i, title in enumerate(suggestions, 1):
        print(f"{i}. {title}")

    print(f"5. Enter custom title")
    print(f"6. Cancel")
    print("=" * 60)

    # This is where Claude would use AskUserQuestion
    # For now, return suggestions for Claude to handle
    return {
        'suggestions': suggestions,
        'conversation_file': str(conv_file),
        'action': 'choose_title'
    }


def rename_terminal(title):
    """Rename terminal tab/window"""

    if not title:
        return "Please provide a title for the terminal"

    # Different commands for different terminals/OS
    if sys.platform == "darwin":  # macOS
        # For iTerm2
        os.system(f'echo -ne "\\033]0;{title}\\007"')
        # For Terminal.app
        os.system(f'printf "\\e]1;{title}\\a"')
        return f"Terminal renamed to: {title}"
    elif sys.platform.startswith("linux"):
        os.system(f'echo -ne "\\033]0;{title}\\007"')
        return f"Terminal renamed to: {title}"
    else:
        return "Terminal renaming not supported on this platform"
```

### Auto-Sync Terminal Title

After successfully renaming a conversation, automatically update the terminal title using smart detection:

```bash
# Rename conversation first
python3 .claude/skills/conversations-manage/rename_conversation.py "New Title"

# Then sync terminal title (auto-detects terminal type)
python3 .claude/skills/rename/scripts/set_terminal_title.py "New Title"
```

**Supported Terminals:**

| Terminal | Support | Method |
|----------|---------|--------|
| iTerm2 (macOS) | ✅ Full | ANSI escape codes |
| Terminal.app (macOS) | ✅ Full | ANSI escape codes |
| GNOME Terminal (Linux) | ✅ Full | ANSI escape codes |
| Alacritty, Kitty, WezTerm | ✅ Full | ANSI escape codes |
| tmux | ✅ Full | `tmux rename-window` |
| GNU screen | ✅ Full | `screen -X title` |
| VS Code integrated | ⚠️ Limited | Not supported - shows notification |

**Detection Logic:**
- Checks `TERM_PROGRAM`, `TMUX`, `STY`, `VSCODE_INJECTION` environment variables
- Automatically uses the correct method for each terminal type
- Gracefully handles unsupported terminals

**User Feedback Examples:**

iTerm2/Terminal.app:
```
✅ Renamed conversation to: "New Title"
✅ Terminal title updated (iTerm2)
```

VS Code:
```
✅ Renamed conversation to: "New Title"
ℹ️  Terminal title (VS Code terminal doesn't support renaming)
```

tmux:
```
✅ Renamed conversation to: "New Title"
✅ Terminal title updated (tmux window)
```

**Implementation in Claude:**
When handling a rename request:
1. Get user's title choice
2. Run `rename_conversation.py` with the chosen title
3. Run `set_terminal_title.py` to update terminal (auto-detects type)
4. Provide appropriate feedback based on terminal support

## Usage Examples

### Quick Conversation Rename (iTerm2)
```
User: "rename"
Assistant:
🎯 Quick Rename - Choose a title:
1. Build conversations-manage skill with renaming
2. Add BlueDot search and conversation tools
3. Create smart conversation naming skill
4. Implement quick rename functionality prototype

[User selects option 2]
✅ Renamed conversation to: "Add BlueDot search and conversation tools"
✅ Terminal title updated (iTerm2)
```

### Quick Conversation Rename (VS Code)
```
User: "rename"
Assistant:
🎯 Quick Rename - Choose a title:
1. Build conversations-manage skill with renaming
2. Add BlueDot search and conversation tools
3. Create smart conversation naming skill
4. Implement quick rename functionality prototype

[User selects option 2]
✅ Renamed conversation to: "Add BlueDot search and conversation tools"
ℹ️  Terminal title (VS Code terminal doesn't support renaming)
```

### Quick Conversation Rename (tmux)
```
User: "rename"
Assistant:
🎯 Quick Rename - Choose a title:
1. Build conversations-manage skill with renaming
2. Add BlueDot search and conversation tools
3. Create smart conversation naming skill
4. Implement quick rename functionality prototype

[User selects option 2]
✅ Renamed conversation to: "Add BlueDot search and conversation tools"
✅ Terminal title updated (tmux window)
```

### Terminal Rename
```
User: "rename terminal AI Development"
Assistant: ✅ Terminal renamed to: "AI Development"
```

### With Custom Title
```
User: "rename this to Project Planning Session"
Assistant: ✅ Renamed conversation to: "Project Planning Session"
```

## Integration Points

This skill leverages:
- **conversations-manage**: For smart title generation and conversation renaming
- **AskUserQuestion**: For interactive title selection
- **System commands**: For terminal title changes

## Why This Skill?

1. **Speed**: Single word "rename" triggers intelligent renaming
2. **Context-aware**: Knows what you likely want to rename
3. **Smart defaults**: Conversation renaming is the most common use case
4. **Extensible**: Can add file, project, folder renaming later
5. **Cross-platform**: Terminal renaming works on macOS and Linux

## Future Enhancements

- [ ] File renaming with smart suggestions
- [ ] Project renaming (update all references)
- [ ] Batch renaming capabilities
- [ ] Folder structure renaming
- [ ] Git branch renaming
- [ ] Variable/function renaming in code

## Notes

- The skill prioritizes conversation renaming as the default action
- Terminal renaming uses ANSI escape codes that work in most modern terminals
- Smart suggestions ensure titles are meaningful and differentiated
- Integration with conversations-manage ensures consistency