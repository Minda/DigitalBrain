#!/usr/bin/env python3
"""
Enhanced conversation renaming with detailed feedback and proper customTitle handling
"""

import json
import sys
import shutil
from pathlib import Path
from datetime import datetime


def rename_conversation(new_title, conversation_id=None):
    """Wrapper for compatibility - calls the enhanced version"""
    return rename_conversation_with_feedback(new_title, conversation_id)


def rename_conversation_with_feedback(new_title, conversation_id=None):
    """
    Rename a conversation with detailed feedback about changes

    Args:
        new_title: The new title for the conversation
        conversation_id: Optional specific conversation ID (defaults to current)
    """
    # Get the Claude projects directory
    claude_dir = Path("/Users/min/.claude/projects/-Users-min-Documents-Projects-DigitalBrain")

    if conversation_id:
        conv_file = claude_dir / f"{conversation_id}.jsonl"
    else:
        # Find the most recent conversation
        conv_files = sorted(claude_dir.glob("*.jsonl"),
                          key=lambda x: x.stat().st_mtime,
                          reverse=True)
        if not conv_files:
            return {"error": "No conversations found", "success": False}
        conv_file = conv_files[0]

    if not conv_file.exists():
        return {"error": f"Conversation file not found: {conv_file}", "success": False}

    # Create backup
    backup_file = conv_file.with_suffix('.jsonl.backup')
    shutil.copy2(conv_file, backup_file)

    # Prepare detailed feedback
    feedback = {
        "file": str(conv_file),
        "conversation_id": conv_file.stem,
        "previous_title": None,
        "new_title": new_title,
        "changes": [],
        "success": False,
        "file_size": conv_file.stat().st_size,
        "total_lines": 0,
        "modified_lines": []
    }

    print(f"\n{'='*70}")
    print(f"📝 RENAMING CONVERSATION")
    print(f"{'='*70}")
    print(f"📁 File: {conv_file.name}")
    print(f"📏 Size: {feedback['file_size']:,} bytes")

    # Read and analyze the file
    lines = []
    custom_title_found = False
    existing_custom_title_lines = []
    first_message_line = -1

    with open(conv_file, 'r') as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            feedback["total_lines"] += 1

            try:
                data = json.loads(line)

                # Check for existing customTitle
                if 'customTitle' in data:
                    existing_custom_title_lines.append(i)
                    if not feedback["previous_title"]:
                        feedback["previous_title"] = data['customTitle']

                # Track if this is a custom-title type object
                if data.get('type') == 'custom-title':
                    custom_title_found = True
                    # Store the old title before updating
                    old_title = data.get('customTitle', 'Untitled')
                    # Update this line with new title
                    data['customTitle'] = new_title
                    feedback["modified_lines"].append(i)
                    feedback["changes"].append({
                        "line": i,
                        "type": "updated",
                        "before": old_title,
                        "after": new_title
                    })

                # Track first message line
                if first_message_line == -1 and data.get('role'):
                    first_message_line = i

                # IMPORTANT: Append the potentially modified data, not the original
                lines.append(json.dumps(data, ensure_ascii=False))

            except json.JSONDecodeError:
                lines.append(line)

    print(f"📊 Lines: {feedback['total_lines']}")

    # Display current state
    if feedback["previous_title"]:
        print(f"\n🏷️  BEFORE: '{feedback['previous_title']}'")
        print(f"   Found on lines: {', '.join(map(str, existing_custom_title_lines))}")
    else:
        print(f"\n🏷️  BEFORE: Untitled (no customTitle found)")

    print(f"✨ AFTER:  '{new_title}'")

    # If no custom-title type object exists, add one
    if not custom_title_found:
        # Create a new custom-title object
        custom_title_obj = {
            "type": "custom-title",
            "customTitle": new_title,
            "sessionId": conv_file.stem,
            "timestamp": datetime.now().isoformat() + "Z"
        }

        # Insert after first few lines (not at the very beginning)
        insert_position = min(5, len(lines))
        lines.insert(insert_position, json.dumps(custom_title_obj, ensure_ascii=False))

        feedback["modified_lines"].append(insert_position + 1)
        feedback["changes"].append({
            "line": insert_position + 1,
            "type": "added",
            "content": f"Added new custom-title object"
        })

        print(f"\n🆕 ADDED: New custom-title object at line {insert_position + 1}")
        print(f"   Content: {json.dumps(custom_title_obj, indent=2)}")

    # Write back to file
    with open(conv_file, 'w') as f:
        for line in lines:
            f.write(line + '\n')

    feedback["success"] = True

    # Display changes summary
    print(f"\n📝 CHANGES SUMMARY:")
    print(f"   • File modified: {conv_file.name}")
    print(f"   • Lines changed: {len(feedback['modified_lines'])}")
    print(f"   • Backup created: {backup_file.name}")

    # Show changed lines
    if feedback["changes"]:
        print(f"\n📍 MODIFIED LINES:")
        for change in feedback["changes"]:
            if change["type"] == "updated":
                print(f"   Line {change['line']}: Updated customTitle")
                print(f"      Before: '{change['before']}'")
                print(f"      After:  '{change['after']}'")
            elif change["type"] == "added":
                print(f"   Line {change['line']}: {change['content']}")

    # Final status
    print(f"\n✅ SUCCESS: Conversation renamed")
    print(f"   Title: '{new_title}'")
    print(f"   File: {conv_file}")
    print(f"{'='*70}\n")

    # Clickable file path for VS Code/editors
    print(f"📂 Click to open: {conv_file.resolve()}")

    return feedback


def verify_rename(conversation_id):
    """Verify that the rename was successful"""
    claude_dir = Path("/Users/min/.claude/projects/-Users-min-Documents-Projects-DigitalBrain")
    conv_file = claude_dir / f"{conversation_id}.jsonl"

    if not conv_file.exists():
        return None

    titles_found = []
    with open(conv_file, 'r') as f:
        for i, line in enumerate(f, 1):
            try:
                data = json.loads(line.strip())
                if 'customTitle' in data:
                    titles_found.append({
                        "line": i,
                        "title": data['customTitle'],
                        "type": data.get('type', 'embedded')
                    })
            except:
                continue

    return titles_found


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python rename_conversation_v2.py 'New Title' [conversation_id]")
        print("   or: python rename_conversation_v2.py --verify [conversation_id]")
        sys.exit(1)

    if sys.argv[1] == '--verify':
        conversation_id = sys.argv[2] if len(sys.argv) > 2 else None
        if not conversation_id:
            # Get most recent
            claude_dir = Path("/Users/min/.claude/projects/-Users-min-Documents-Projects-DigitalBrain")
            conv_files = sorted(claude_dir.glob("*.jsonl"),
                              key=lambda x: x.stat().st_mtime,
                              reverse=True)
            if conv_files:
                conversation_id = conv_files[0].stem

        titles = verify_rename(conversation_id)
        if titles:
            print(f"\n🔍 Titles found in {conversation_id}:")
            for t in titles:
                print(f"   Line {t['line']}: '{t['title']}' (type: {t['type']})")
        else:
            print(f"No titles found in {conversation_id}")
    else:
        new_title = sys.argv[1]
        conversation_id = sys.argv[2] if len(sys.argv) > 2 else None
        result = rename_conversation_with_feedback(new_title, conversation_id)

        if not result["success"]:
            sys.exit(1)