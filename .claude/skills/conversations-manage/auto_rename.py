#!/usr/bin/env python3
"""
Enhanced auto-rename that automatically picks and applies a title
while showing alternatives for easy selection
"""

import json
import sys
from pathlib import Path
from suggest_titles import suggest_conversation_titles, extract_conversation_features, generate_title_suggestions
from rename_conversation import rename_conversation_with_feedback


def auto_rename_with_suggestions(conversation_id=None):
    """
    Automatically rename conversation with best suggestion,
    showing alternatives for easy selection
    """
    # Generate suggestions
    suggestions, conv_file = suggest_conversation_titles(conversation_id)

    if not suggestions:
        print(f"❌ Error: {conv_file}")  # Error message
        return False

    # Auto-select the first (best) suggestion
    selected_title = suggestions[0]

    print(f"\n{'='*70}")
    print(f"🎯 AUTO-RENAMING CONVERSATION")
    print(f"{'='*70}")

    # Apply the auto-selected title
    print(f"\n✅ Applying title: '{selected_title}'")
    result = rename_conversation_with_feedback(selected_title, conversation_id)

    if not result["success"]:
        print(f"❌ Failed to rename: {result.get('error', 'Unknown error')}")
        return False

    # Show all suggestions with easy selection commands
    print(f"\n💡 ALTERNATIVE TITLES (if you prefer a different one):")
    print(f"{'─'*70}")

    for i, title in enumerate(suggestions, 1):
        if i == 1:
            print(f"{i}. {title} ← [SELECTED]")
        else:
            print(f"{i}. {title}")

    print(f"{'─'*70}")
    print(f"\n📝 TO CHANGE: Copy and run one of these commands:")

    # Generate easy copy-paste commands for each alternative
    for i, title in enumerate(suggestions[1:], 2):  # Start from second option
        # Escape quotes in title for shell command
        escaped_title = title.replace('"', '\\"').replace('$', '\\$')
        print(f"   python3 .claude/skills/conversations-manage/rename_conversation.py \"{escaped_title}\"")

    print(f"\n🎨 CUSTOM: To use your own title:")
    print(f"   python3 .claude/skills/conversations-manage/rename_conversation.py \"Your Custom Title Here\"")

    print(f"{'='*70}\n")

    return True


def quick_rename(title_number=None, custom_title=None, conversation_id=None):
    """
    Quick rename using a number selection or custom title
    Usage:
        quick_rename(2)  # Use suggestion #2
        quick_rename(custom_title="My Title")  # Use custom title
    """
    if custom_title:
        # Direct rename with custom title
        result = rename_conversation_with_feedback(custom_title, conversation_id)
        return result["success"]

    if title_number:
        # Get suggestions and pick the numbered one
        suggestions, conv_file = suggest_conversation_titles(conversation_id)

        if not suggestions or title_number < 1 or title_number > len(suggestions):
            print(f"❌ Invalid selection: {title_number}")
            return False

        selected_title = suggestions[title_number - 1]
        print(f"✅ Applying title #{title_number}: '{selected_title}'")
        result = rename_conversation_with_feedback(selected_title, conversation_id)
        return result["success"]

    print("❌ No title specified")
    return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Auto-rename conversation with suggestions")
    parser.add_argument("--pick", type=int, help="Pick suggestion number (1-4)")
    parser.add_argument("--custom", type=str, help="Use custom title")
    parser.add_argument("--conversation", type=str, help="Specific conversation ID")

    args = parser.parse_args()

    if args.pick:
        # Quick selection by number
        success = quick_rename(title_number=args.pick, conversation_id=args.conversation)
        sys.exit(0 if success else 1)
    elif args.custom:
        # Quick custom title
        success = quick_rename(custom_title=args.custom, conversation_id=args.conversation)
        sys.exit(0 if success else 1)
    else:
        # Default: auto-rename with suggestions
        success = auto_rename_with_suggestions(args.conversation)
        sys.exit(0 if success else 1)