#!/usr/bin/env python3
"""
Rename a Claude Code conversation by updating its customTitle field
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def rename_conversation(new_title, conversation_id=None):
    """
    Rename a conversation by updating its customTitle field

    Args:
        new_title: The new title for the conversation
        conversation_id: Optional specific conversation ID (defaults to current)
    """
    # Get the Claude projects directory
    claude_dir = Path("/Users/min/.claude/projects/-Users-min-Documents-Projects-DigitalBrain")

    if conversation_id:
        # Find specific conversation
        conv_file = claude_dir / f"{conversation_id}.jsonl"
    else:
        # Find the most recent conversation (current one)
        conv_files = sorted(claude_dir.glob("*.jsonl"),
                          key=lambda x: x.stat().st_mtime,
                          reverse=True)
        if not conv_files:
            return "No conversations found"
        conv_file = conv_files[0]

    if not conv_file.exists():
        return f"Conversation file not found: {conv_file}"

    print(f"Updating conversation: {conv_file.name}")

    # Read all lines from the JSONL file
    lines = []
    title_updated = False

    with open(conv_file, 'r') as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)

                # Update the customTitle in the first JSON object or if it already exists
                if not title_updated and (i == 0 or 'customTitle' in data):
                    data['customTitle'] = new_title
                    title_updated = True
                    print(f"  → Set customTitle to: '{new_title}'")

                lines.append(json.dumps(data, ensure_ascii=False))
            except json.JSONDecodeError as e:
                # Keep original line if not valid JSON
                print(f"  Warning: Line {i+1} is not valid JSON, keeping as-is")
                lines.append(line)

    # If we haven't added the title yet, add it to the first line
    if not title_updated and lines:
        try:
            first_data = json.loads(lines[0])
            first_data['customTitle'] = new_title
            lines[0] = json.dumps(first_data, ensure_ascii=False)
            print(f"  → Added customTitle to first line: '{new_title}'")
        except:
            # If first line isn't valid JSON, prepend a new line with just the title
            title_line = json.dumps({'customTitle': new_title}, ensure_ascii=False)
            lines.insert(0, title_line)
            print(f"  → Prepended new line with customTitle: '{new_title}'")

    # Write back to file
    with open(conv_file, 'w') as f:
        for line in lines:
            f.write(line + '\n')

    return f"✅ Successfully renamed conversation to: '{new_title}'\n   File: {conv_file}"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python rename_conversation.py 'New Title' [conversation_id]")
        sys.exit(1)

    new_title = sys.argv[1]
    conversation_id = sys.argv[2] if len(sys.argv) > 2 else None

    result = rename_conversation(new_title, conversation_id)
    print(result)