#!/usr/bin/env python3
"""
Fast automatic conversation naming based on first user message.
Designed for speed (< 100ms) with basic keyword extraction.
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime


def extract_quick_title(message_text):
    """
    Extract a quick title from the first user message.
    Prioritizes speed over sophistication.
    """

    # Limit message length for processing
    text = message_text[:500].strip()
    text_lower = text.lower()

    # Skip generic setup/warmup messages
    generic_patterns = [
        r'^claude\s+(warmup|setup|context|init|test)',
        r'^(test|hello|hi|hey)\s*$',
        r'^wake\s*up',
        r'^orient',
        r'^load\s+(context|memories)',
        r'^\s*$',  # Empty messages
    ]

    for pattern in generic_patterns:
        if re.match(pattern, text_lower):
            # Use a more meaningful fallback for generic messages
            return f"Session {datetime.now().strftime('%b %d %H:%M')}"

    # Quick extraction of main intent patterns - improved to be more specific
    action_patterns = [
        # Specific skill invocations
        (r'/(\w+)\s+(.{5,40})', lambda m: f"{m.group(1).capitalize()} {m.group(2)}"),
        (r'\b(skill|command):\s*(\w+)\s+(.{5,30})', lambda m: f"{m.group(2).capitalize()} {m.group(3)}"),

        # File and code operations
        (r'\b(create|build|make|write|generate)\s+(?:a\s+)?(.{5,40})', lambda m: f"Create {m.group(2)}"),
        (r'\b(fix|debug|solve|repair)\s+(.{5,40})', lambda m: f"Fix {m.group(2)}"),
        (r'\b(update|modify|change|edit|improve|enhance)\s+(.{5,40})', lambda m: f"Update {m.group(2)}"),
        (r'\b(rename|name)\s+(.{5,40})', lambda m: f"Rename {m.group(2)}"),
        (r'\b(refactor|optimize|clean)\s+(.{5,40})', lambda m: f"{m.group(1).capitalize()} {m.group(2)}"),

        # Search and analysis
        (r'\b(search|find|look for|locate)\s+(.{5,40})', lambda m: f"Search {m.group(2)}"),
        (r'\b(analyze|review|check|inspect|examine)\s+(.{5,40})', lambda m: f"Analyze {m.group(2)}"),

        # Setup and configuration
        (r'\b(install|setup|configure|deploy)\s+(.{5,40})', lambda m: f"Setup {m.group(2)}"),
        (r'\b(test|run|execute)\s+(.{5,40})', lambda m: f"Test {m.group(2)}"),

        # Questions - extract the key topic
        (r'\b(what|how|where|when|why|who)\s+(?:is|are|do|does|can|should)\s+(.{5,40})', lambda m: f"{m.group(1).capitalize()} {m.group(2)}"),

        # Help requests - extract the specific topic
        (r'\b(?:help|can you|could you|please)\s+(?:me\s+)?(\w+)\s+(.{5,30})', lambda m: f"{m.group(1).capitalize()} {m.group(2)}"),
    ]

    # Try pattern matching first
    for pattern, formatter in action_patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                title = formatter(match)
                # Clean up the title
                title = re.sub(r'\s+', ' ', title).strip()
                title = re.sub(r'[.?!,;]+$', '', title)
                # Capitalize first letter
                if title:
                    title = title[0].upper() + title[1:]
                # Truncate if too long
                if len(title) > 50:
                    title = title[:47] + "..."
                return title
            except:
                continue

    # Fallback: Extract key technical terms and create simple title
    tech_terms = []

    # Look for file names - improved to capture more patterns
    files = re.findall(r'[\w\-/]+\.\w{2,4}', text)
    if files:
        # Get just the filename, not the full path
        filename = files[0].split('/')[-1]
        # Look for action verbs associated with the file
        file_actions = re.findall(r'\b(edit|update|fix|create|read|open|modify|rename)\b', text_lower)
        if file_actions:
            return f"{file_actions[0].capitalize()} {filename}"
        else:
            return f"Working with {filename}"

    # Look for project/repo names (things with slashes or in backticks)
    project_patterns = [
        (r'`([^`]+)`', lambda m: f"Working on {m.group(1)}"),
        (r'\b(\w+/\w+)\b', lambda m: f"Project {m.group(1)}"),
        (r'"([^"]+)"', lambda m: f"About {m.group(1)}"),
    ]

    for pattern, formatter in project_patterns:
        match = re.search(pattern, text)
        if match:
            title = formatter(match)
            if len(title) <= 50:
                return title

    # Look for technical keywords - expanded list
    keywords = re.findall(
        r'\b(API|CLI|SQL|JSON|YAML|HTML|CSS|JavaScript|Python|Rust|'
        r'database|server|skill|agent|conversation|naming|auto-name|'
        r'file|code|script|function|test|bug|error|feature|component|'
        r'service|module|package|library|framework|tool)\b',
        text, re.IGNORECASE
    )

    if keywords:
        keyword = keywords[0]
        # Uppercase common acronyms
        if keyword.upper() in ['API', 'CLI', 'SQL', 'JSON', 'YAML', 'HTML', 'CSS']:
            keyword = keyword.upper()
        else:
            keyword = keyword.capitalize()

        # Try to find associated verb
        verbs = re.findall(
            r'\b(create|update|fix|debug|test|build|search|analyze|setup|'
            r'implement|develop|refactor|optimize|integrate|configure)\b',
            text_lower
        )
        if verbs:
            return f"{verbs[0].capitalize()} {keyword}"
        else:
            # Look for question words to create question-based titles
            if re.search(r'\b(what|how|where|when|why|who)\b', text_lower):
                return f"Question about {keyword}"
            else:
                return f"{keyword} work"

    # Extract main content words (skip common words)
    stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                  'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
                  'could', 'may', 'might', 'must', 'can', 'shall', 'to', 'of', 'in',
                  'for', 'on', 'with', 'at', 'by', 'from', 'up', 'about', 'into',
                  'through', 'during', 'before', 'after', 'above', 'below', 'between',
                  'under', 'i', 'me', 'you', 'we', 'they', 'it', 'this', 'that', 'and',
                  'but', 'or', 'if', 'then', 'than', 'so', 'as', 'let', "let's", 'make'}

    words = text.split()
    content_words = [w for w in words if w.lower() not in stop_words][:5]

    if len(content_words) >= 2:
        title = ' '.join(content_words[:4])
        title = re.sub(r'[.?!,;]+$', '', title)
        if len(title) > 50:
            title = title[:47] + "..."
        # Capitalize first letter only, preserve other casing
        if title:
            title = title[0].upper() + title[1:]
        return title

    # Ultimate fallback with timestamp
    return f"Session {datetime.now().strftime('%b %d %H:%M')}"


def apply_auto_name(conversation_id, title):
    """
    Apply the auto-generated name to the conversation.
    Similar to rename_conversation but without user feedback.
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
            return False
        conv_file = conv_files[0]

    if not conv_file.exists():
        return False

    # Read the file
    lines = []
    custom_title_found = False

    try:
        with open(conv_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)

                    # Update existing custom-title objects
                    if data.get('type') == 'custom-title':
                        custom_title_found = True
                        data['customTitle'] = title
                        data['autoGenerated'] = True  # Mark as auto-generated

                    lines.append(json.dumps(data, ensure_ascii=False))
                except json.JSONDecodeError:
                    lines.append(line)

        # If no custom-title exists, add one
        if not custom_title_found:
            custom_title_obj = {
                "type": "custom-title",
                "customTitle": title,
                "sessionId": conv_file.stem,
                "timestamp": datetime.now().isoformat() + "Z",
                "autoGenerated": True  # Mark as auto-generated
            }

            # Insert after first few lines
            insert_position = min(5, len(lines))
            lines.insert(insert_position, json.dumps(custom_title_obj, ensure_ascii=False))

        # Write back to file
        with open(conv_file, 'w') as f:
            for line in lines:
                f.write(line + '\n')

        return True

    except Exception as e:
        # Silently fail - don't interrupt user experience
        return False


def main():
    """
    Main function to auto-name conversation from command line.

    Usage: python3 auto_name.py --message "user message" [--conversation-id ID]
    """
    import argparse

    parser = argparse.ArgumentParser(description='Auto-name conversation from first message')
    parser.add_argument('--message', required=True, help='First user message')
    parser.add_argument('--conversation-id', help='Specific conversation ID (optional)')
    parser.add_argument('--debug', action='store_true', help='Print debug output')

    args = parser.parse_args()

    # Generate title from message
    title = extract_quick_title(args.message)

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