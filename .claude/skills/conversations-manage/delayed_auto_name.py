#!/usr/bin/env python3
"""
Delayed auto-naming that waits for more context before naming the conversation.
This script monitors the conversation file and names it after sufficient context is available.
"""

import json
import time
import sys
from pathlib import Path
from datetime import datetime
from auto_name import extract_quick_title, apply_auto_name


def wait_for_context(conversation_id=None, timeout=30, min_messages=3):
    """
    Wait for enough conversation context before auto-naming.

    Args:
        conversation_id: Specific conversation ID (optional)
        timeout: Maximum seconds to wait
        min_messages: Minimum number of messages before naming

    Returns:
        Tuple of (success, conversation_text)
    """
    claude_dir = Path("/Users/min/.claude/projects/-Users-min-Documents-Projects-DigitalBrain")

    if conversation_id:
        conv_file = claude_dir / f"{conversation_id}.jsonl"
    else:
        # Find the most recent conversation
        conv_files = sorted(claude_dir.glob("*.jsonl"),
                          key=lambda x: x.stat().st_mtime,
                          reverse=True)
        if not conv_files:
            return False, ""
        conv_file = conv_files[0]

    if not conv_file.exists():
        return False, ""

    start_time = time.time()
    last_size = 0
    stable_count = 0
    conversation_text = []

    while time.time() - start_time < timeout:
        try:
            current_size = conv_file.stat().st_size

            # If file hasn't changed for 2 checks, consider it stable
            if current_size == last_size:
                stable_count += 1
                if stable_count >= 2:
                    break
            else:
                stable_count = 0
                last_size = current_size

            # Read conversation content
            messages = []
            with open(conv_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        # Look for user and assistant messages
                        if data.get('type') == 'message':
                            role = data.get('role', '')
                            content = data.get('content', '')
                            if role in ['user', 'assistant'] and content:
                                messages.append({
                                    'role': role,
                                    'content': content[:500]  # Limit length
                                })
                    except json.JSONDecodeError:
                        continue

            # Check if we have enough messages
            if len(messages) >= min_messages:
                # Combine user messages for context
                user_messages = [m['content'] for m in messages if m['role'] == 'user']
                # Also consider assistant responses for better context
                assistant_messages = [m['content'] for m in messages if m['role'] == 'assistant']

                # Build context from both user and assistant messages
                context_parts = []
                for msg in messages[:5]:  # Look at first 5 messages
                    if msg['role'] == 'user':
                        context_parts.append(msg['content'])

                conversation_text = ' '.join(context_parts)
                return True, conversation_text

            time.sleep(1)  # Wait before checking again

        except Exception as e:
            # Silent failure
            time.sleep(1)
            continue

    # Timeout reached or stable with insufficient messages
    return False, ""


def generate_contextual_title(conversation_text):
    """
    Generate a title based on full conversation context.
    Falls back to extract_quick_title if needed.
    """
    if not conversation_text:
        return f"Session {datetime.now().strftime('%b %d %H:%M')}"

    # Use the existing extraction logic but with more context
    title = extract_quick_title(conversation_text)

    # Additional refinement based on having more context
    # If title is still generic, try harder
    if title.startswith("Session "):
        # Try to extract the most substantive part
        words = conversation_text.split()

        # Look for the most important technical term or action
        important_terms = []
        for word in words:
            if len(word) > 4 and word[0].isupper():
                important_terms.append(word)

        if important_terms:
            return f"Discussion about {important_terms[0]}"

    return title


def main():
    """
    Main function for delayed auto-naming.

    Usage: python3 delayed_auto_name.py [--conversation-id ID] [--timeout SECONDS] [--min-messages N]
    """
    import argparse

    parser = argparse.ArgumentParser(description='Delayed auto-name with context awareness')
    parser.add_argument('--conversation-id', help='Specific conversation ID (optional)')
    parser.add_argument('--timeout', type=int, default=30, help='Max seconds to wait (default: 30)')
    parser.add_argument('--min-messages', type=int, default=3, help='Min messages before naming (default: 3)')
    parser.add_argument('--debug', action='store_true', help='Print debug output')

    args = parser.parse_args()

    if args.debug:
        print(f"Waiting for context (timeout: {args.timeout}s, min messages: {args.min_messages})")

    # Wait for sufficient context
    success, conversation_text = wait_for_context(
        args.conversation_id,
        args.timeout,
        args.min_messages
    )

    if not success or not conversation_text:
        if args.debug:
            print("Insufficient context, skipping auto-naming")
        sys.exit(1)

    # Generate title based on context
    title = generate_contextual_title(conversation_text)

    if args.debug:
        print(f"Generated title: {title}")

    # Apply the title
    success = apply_auto_name(args.conversation_id, title)

    if args.debug:
        if success:
            print(f"Successfully applied title: {title}")
        else:
            print("Failed to apply title")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()