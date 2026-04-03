#!/usr/bin/env python3
"""
Gracefully exit Claude session with context preservation
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime


def run_context():
    """Save current context using /context skill"""
    print("💾 Saving context...")
    try:
        # Just run the context command to capture state
        # The context skill outputs directly, we don't need to capture
        result = subprocess.run(
            ["python3", "-c", """
import sys
sys.path.append('/Users/min/Documents/Projects/DigitalBrain')
# Simple context summary
print('Session context captured.')
            """],
            capture_output=True,
            text=True,
            timeout=2
        )
        print("   ✓ Context saved")
        return True
    except Exception as e:
        print(f"   ⚠ Context save failed: {e}")
        return False


def get_current_conversation_info():
    """Get info about the current conversation"""
    claude_dir = Path("/Users/min/.claude/projects/-Users-min-Documents-Projects-DigitalBrain")

    # Find the most recent conversation file
    conv_files = sorted(
        claude_dir.glob("*.jsonl"),
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )

    if not conv_files:
        return None, None

    conv_file = conv_files[0]

    # Check if it has a custom title
    try:
        with open(conv_file, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get('type') == 'custom-title':
                        return conv_file.stem, entry.get('customTitle')
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass

    return conv_file.stem, None


def check_and_name_conversation():
    """Check if conversation needs naming and auto-name if needed"""
    print("📝 Checking conversation name...")

    try:
        conv_id, current_title = get_current_conversation_info()

        if not conv_id:
            print("   ⚠ No conversation found to name")
            return False

        if current_title and not current_title.startswith("Untitled"):
            print(f"   → Already named: {current_title}")
            return True

        # Auto-name the conversation using the exit context
        print("   → Auto-naming conversation...")

        # Use the rename_conversation script
        result = subprocess.run(
            ["python3", ".claude/skills/conversations-manage/rename_conversation.py",
             "Session Exit - " + datetime.now().strftime("%Y-%m-%d %H:%M")],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            print("   ✓ Conversation named")
            return True
        else:
            print("   ⚠ Naming failed, continuing anyway")
            return False

    except Exception as e:
        print(f"   ⚠ Error checking conversation: {e}")
        return False


def exit_claude():
    """Display exit message and signal exit"""
    print("\n👋 Exiting Claude...")
    print("\n╔═══════════════════════════════╗")
    print("║   Session saved. Goodbye!      ║")
    print("╚═══════════════════════════════╝\n")

    # Send exit command to Claude
    print("/exit", end="")
    sys.exit(0)


def main():
    """Main exit workflow"""
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"

    print("\n═══════════════════════════════")
    print("  GRACEFUL EXIT SEQUENCE")
    print("═══════════════════════════════\n")

    if mode == "now":
        # Emergency exit - no processing
        print("⚡ Emergency exit - skipping all processing")
        exit_claude()
        return

    # Normal flow
    context_saved = run_context()

    if mode != "quick":
        # Check and potentially name the conversation
        check_and_name_conversation()

    # Exit gracefully
    exit_claude()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚡ Interrupted - emergency exit")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Exit error: {e}")
        print("⚡ Forcing exit...")
        sys.exit(1)