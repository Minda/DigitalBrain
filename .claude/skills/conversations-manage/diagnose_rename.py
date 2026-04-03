#!/usr/bin/env python3
"""
Diagnose conversation rename issues and verify title persistence.
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def diagnose_conversation_rename(conversation_id=None):
    """Check if conversation was properly renamed and diagnose issues."""

    print("\n" + "="*70)
    print("🔍 CONVERSATION RENAME DIAGNOSIS")
    print("="*70)

    # Get the Claude projects directory
    claude_dir = Path("/Users/min/.claude/projects/-Users-min-Documents-Projects-DigitalBrain")

    if not claude_dir.exists():
        print("❌ ERROR: Claude projects directory not found!")
        print(f"   Expected: {claude_dir}")
        return False

    # Find conversation file
    if conversation_id:
        conv_file = claude_dir / f"{conversation_id}.jsonl"
        print(f"📁 Checking specific conversation: {conversation_id}")
    else:
        # Find the most recent conversation
        conv_files = sorted(claude_dir.glob("*.jsonl"),
                          key=lambda x: x.stat().st_mtime,
                          reverse=True)
        if not conv_files:
            print("❌ ERROR: No conversation files found!")
            return False
        conv_file = conv_files[0]
        print(f"📁 Checking most recent conversation: {conv_file.name}")

    if not conv_file.exists():
        print(f"❌ ERROR: Conversation file not found: {conv_file}")
        return False

    # Analyze the file
    print(f"\n📊 FILE ANALYSIS:")
    print(f"   Path: {conv_file}")
    print(f"   Size: {conv_file.stat().st_size:,} bytes")
    print(f"   Modified: {datetime.fromtimestamp(conv_file.stat().st_mtime)}")

    # Check for title
    custom_title_found = False
    custom_title_value = None
    custom_title_lines = []
    line_count = 0

    print(f"\n🔍 SEARCHING FOR TITLE...")

    with open(conv_file, 'r') as f:
        for i, line in enumerate(f, 1):
            line_count += 1
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)

                # Check for customTitle field
                if 'customTitle' in data:
                    custom_title_found = True
                    custom_title_value = data['customTitle']
                    custom_title_lines.append(i)

                    # Show what we found
                    if data.get('type') == 'custom-title':
                        print(f"   ✅ Found custom-title object at line {i}")
                        print(f"      Title: '{custom_title_value}'")
                        if 'timestamp' in data:
                            print(f"      Added: {data['timestamp']}")
                    else:
                        print(f"   📝 Found customTitle in {data.get('type', 'unknown')} at line {i}")

            except json.JSONDecodeError:
                pass  # Skip invalid JSON lines

    print(f"\n📈 SUMMARY:")
    print(f"   Total lines: {line_count}")

    if custom_title_found:
        print(f"   ✅ TITLE FOUND: '{custom_title_value}'")
        print(f"   📍 Locations: Lines {', '.join(map(str, custom_title_lines))}")
        print(f"\n✅ SUCCESS: Conversation is properly renamed!")
        print(f"   If not showing in UI, try:")
        print(f"   1. Refresh Claude window (Cmd+R)")
        print(f"   2. Restart Claude application")
        print(f"   3. Wait a moment for UI to update")
        return True
    else:
        print(f"   ❌ NO TITLE FOUND!")
        print(f"\n🔧 DIAGNOSIS:")
        print(f"   The conversation has not been renamed yet.")
        print(f"\n📝 TO FIX:")
        print(f"   1. Run: python3 .claude/skills/conversations-manage/suggest_titles.py")
        print(f"   2. Choose a title")
        print(f"   3. Run: python3 .claude/skills/conversations-manage/rename_conversation.py \"Your Title\"")
        return False

    print("\n" + "="*70)


def check_script_setup():
    """Check if the rename scripts are properly set up."""

    print("\n🔧 CHECKING SCRIPT SETUP...")

    skills_dir = Path(".claude/skills/conversations-manage")

    # Check for scripts
    scripts = {
        "suggest_titles.py": "Title suggestion script",
        "suggest_names.py": "Symlink to suggest_titles.py",
        "rename_conversation.py": "Rename execution script",
        "auto_name.py": "Auto-naming script",
    }

    all_good = True
    for script, description in scripts.items():
        script_path = skills_dir / script
        if script_path.exists():
            if script_path.is_symlink():
                target = script_path.resolve()
                print(f"   ✅ {script}: Symlink → {target.name}")
            else:
                print(f"   ✅ {script}: {description}")
        else:
            print(f"   ❌ {script}: MISSING! ({description})")
            all_good = False

    if not all_good:
        print("\n⚠️  Some scripts are missing. The skill may not work properly.")
        print("   Run setup commands to fix.")

    return all_good


if __name__ == "__main__":
    # Check script setup first
    setup_ok = check_script_setup()

    # Then diagnose conversation
    conversation_id = sys.argv[1] if len(sys.argv) > 1 else None
    rename_ok = diagnose_conversation_rename(conversation_id)

    # Overall status
    print("\n" + "="*70)
    if setup_ok and rename_ok:
        print("✅ EVERYTHING LOOKS GOOD!")
    elif setup_ok and not rename_ok:
        print("⚠️  Scripts OK, but conversation needs renaming")
    elif not setup_ok and rename_ok:
        print("⚠️  Conversation renamed, but scripts need fixing")
    else:
        print("❌ Multiple issues found - see above for fixes")
    print("="*70)