#!/usr/bin/env python3
"""
List recent Claude Code conversations with their titles and dates
"""

import json
from pathlib import Path
from datetime import datetime


def list_recent_conversations(limit=10):
    """List recent conversations with their titles and dates"""
    claude_dir = Path("/Users/min/.claude/projects/-Users-min-Documents-Projects-DigitalBrain")

    print(f"\n{'='*70}")
    print(f"{'Recent Claude Code Conversations':^70}")
    print(f"{'='*70}\n")

    conversations = []
    for conv_file in sorted(claude_dir.glob("*.jsonl"),
                          key=lambda x: x.stat().st_mtime,
                          reverse=True)[:limit]:

        # Try to get custom title
        title = "Untitled"
        message_count = 0

        with open(conv_file, 'r') as f:
            for line in f:
                message_count += 1
                try:
                    data = json.loads(line.strip())
                    if 'customTitle' in data:
                        title = data['customTitle']
                        # Don't break - keep counting messages
                except:
                    continue

        # Get modification time
        mtime = datetime.fromtimestamp(conv_file.stat().st_mtime)

        conversations.append({
            'id': conv_file.stem,
            'title': title,
            'date': mtime.strftime("%Y-%m-%d %H:%M"),
            'messages': message_count,
            'file': conv_file.name
        })

    # Print in a nice table format
    for i, conv in enumerate(conversations, 1):
        if i == 1:
            print(f"📍 CURRENT:")
        elif i == 2:
            print(f"\n📚 RECENT:")

        print(f"{i:2}. {conv['title'][:50]:<50}")
        print(f"    ID: {conv['id']}")
        print(f"    Date: {conv['date']} | Messages: {conv['messages']}")

        if i == 1:
            print(f"    Status: Active conversation")

    print(f"\n{'='*70}")
    print(f"Total conversations shown: {len(conversations)} of {len(list(claude_dir.glob('*.jsonl')))}")

    return conversations


if __name__ == "__main__":
    list_recent_conversations()