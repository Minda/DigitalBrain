#!/usr/bin/env python3
"""
Quick rename orchestrator - determines what to rename and delegates
Primary use: instant conversation renaming with just "rename"
"""

import os
import sys
import json
from pathlib import Path

# Import from conversations-manage skill
sys.path.insert(0, '/Users/min/Documents/Projects/DigitalBrain/.claude/skills/conversations-manage')


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
    elif target == "tab":
        return rename_terminal(custom_title)  # Alias for terminal
    else:
        return f"Don't know how to rename '{target}' yet"


def rename_current_conversation(custom_title=None):
    """Rename current conversation with smart suggestions"""

    from suggest_titles import suggest_conversation_titles
    from rename_conversation import rename_conversation

    if custom_title:
        # Direct rename if title provided
        result = rename_conversation(custom_title)
        return result

    # Generate smart suggestions
    suggestions, conv_file = suggest_conversation_titles()

    if not suggestions:
        return "Could not analyze conversation for suggestions"

    # Return structured data for Claude to handle with AskUserQuestion
    return {
        'action': 'show_suggestions',
        'suggestions': suggestions,
        'conversation_file': str(conv_file.name) if conv_file else None,
        'message': 'Choose a title for this conversation'
    }


def apply_rename(title_choice, suggestions=None, conversation_id=None):
    """Apply the selected rename choice"""
    from rename_conversation import rename_conversation

    if isinstance(title_choice, int) and suggestions:
        # User selected a numbered option
        if 1 <= title_choice <= len(suggestions):
            selected_title = suggestions[title_choice - 1]
            result = rename_conversation(selected_title, conversation_id)
            return result
    elif isinstance(title_choice, str):
        # User provided custom title
        result = rename_conversation(title_choice, conversation_id)
        return result

    return "Invalid selection"


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
        # For VS Code integrated terminal
        os.system(f'echo -ne "\\033]2;{title}\\007"')
        return f"✅ Terminal renamed to: {title}"
    elif sys.platform.startswith("linux"):
        os.system(f'echo -ne "\\033]0;{title}\\007"')
        return f"✅ Terminal renamed to: {title}"
    else:
        return "Terminal renaming not supported on this platform"


def main():
    """CLI entry point for testing"""
    import argparse

    parser = argparse.ArgumentParser(description="Quick rename tool")
    parser.add_argument('target', nargs='?', default='conversation',
                      help='What to rename (conversation, terminal)')
    parser.add_argument('--title', '-t', help='Custom title to use')
    parser.add_argument('--analyze', '-a', action='store_true',
                      help='Just analyze and show suggestions')

    args = parser.parse_args()

    if args.analyze:
        # Just show analysis
        from suggest_titles import suggest_conversation_titles
        suggestions, conv_file = suggest_conversation_titles()
        if suggestions:
            print("\n🎯 Title Suggestions:")
            for i, title in enumerate(suggestions, 1):
                print(f"{i}. {title}")
        return

    result = quick_rename(args.target, args.title)

    if isinstance(result, dict):
        # Structured response for interactive mode
        if result.get('action') == 'show_suggestions':
            print(f"\n🎯 {result['message']}")
            print("=" * 60)
            for i, title in enumerate(result['suggestions'], 1):
                print(f"{i}. {title}")
            print(f"{len(result['suggestions'])+1}. Enter custom title")
            print(f"{len(result['suggestions'])+2}. Cancel")
            print("=" * 60)

            # In actual use, Claude would handle this with AskUserQuestion
            choice = input("Select option: ").strip()
            try:
                choice_num = int(choice)
                if choice_num <= len(result['suggestions']):
                    final_result = apply_rename(choice_num, result['suggestions'])
                    print(final_result)
                elif choice_num == len(result['suggestions']) + 1:
                    custom = input("Enter custom title: ").strip()
                    if custom:
                        final_result = apply_rename(custom)
                        print(final_result)
            except ValueError:
                print("Cancelled")
    else:
        print(result)


if __name__ == "__main__":
    main()