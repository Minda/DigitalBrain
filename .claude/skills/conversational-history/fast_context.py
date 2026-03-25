#!/usr/bin/env python3
"""
Fast Context Loader - Optimized for speed
Loads recent conversation context in <200ms
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
import os
from typing import List, Dict, Optional

class FastContextLoader:
    def __init__(self):
        self.project_dir = Path("/Users/min/.claude/projects/-Users-min-Documents-Projects-DigitalBrain")
        self.cache_dir = Path.home() / ".cache" / "claude-conversations"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def load_context(self, hours: int = 24, max_files: int = 5) -> str:
        """
        Load recent context FAST
        - Only check file timestamps
        - Only read recent files
        - Only parse last few messages
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_files = self.get_recent_files(cutoff, max_files)

        if not recent_files:
            return "No recent conversations found."

        context_summary = []
        for file_path, mtime in recent_files:
            # Get quick summary without loading entire file
            summary = self.get_file_summary(file_path)
            context_summary.append(summary)

        return self.format_context(context_summary, hours)

    def get_recent_files(self, cutoff: datetime, max_files: int) -> List[tuple]:
        """Get recent files by modification time only"""
        recent = []

        # Quick filesystem scan - just stats, no reading
        for jsonl_file in self.project_dir.glob("*.jsonl"):
            try:
                mtime = datetime.fromtimestamp(jsonl_file.stat().st_mtime)
                if mtime > cutoff:
                    recent.append((jsonl_file, mtime))
            except:
                continue

        # Sort by most recent first
        recent.sort(key=lambda x: x[1], reverse=True)
        return recent[:max_files]

    def get_file_summary(self, file_path: Path) -> Dict:
        """Extract key info from file without loading it all"""
        summary = {
            'file': file_path.stem[:8],  # Short ID
            'time': datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%b %d %H:%M"),
            'size_mb': round(file_path.stat().st_size / 1024 / 1024, 1),
            'topics': [],
            'last_activity': None
        }

        # Check if we have a cached summary
        cache_file = self.cache_dir / f"{file_path.stem}.json"
        cache_valid = False

        if cache_file.exists():
            cache_mtime = cache_file.stat().st_mtime
            if cache_mtime >= file_path.stat().st_mtime:
                # Cache is still valid
                try:
                    with open(cache_file) as f:
                        cached = json.load(f)
                        summary.update(cached)
                        cache_valid = True
                except:
                    pass

        if not cache_valid:
            # Extract fresh summary using tail approach
            summary.update(self.extract_quick_summary(file_path))

            # Save to cache
            try:
                with open(cache_file, 'w') as f:
                    json.dump(summary, f)
            except:
                pass

        return summary

    def extract_quick_summary(self, file_path: Path) -> Dict:
        """Read only last 8KB of file for summary"""
        topics = set()
        last_activity = None

        try:
            file_size = file_path.stat().st_size
            # Read last 8KB or entire file if smaller
            read_size = min(8192, file_size)

            with open(file_path, 'rb') as f:
                if file_size > read_size:
                    f.seek(-read_size, 2)  # Seek from end

                tail_content = f.read().decode('utf-8', errors='ignore')

            # Quick pattern matching on tail content
            lines = tail_content.split('\\n')
            for line in lines[-20:]:  # Check last 20 lines
                if '"type":"user"' in line:
                    # Extract user message for topics
                    if 'skill' in line.lower():
                        topics.add('skills')
                    if 'job' in line.lower():
                        topics.add('jobs')
                    if 'notion' in line.lower():
                        topics.add('notion')
                    if 'conversation' in line.lower():
                        topics.add('history')

                    # Try to extract timestamp
                    if '"timestamp":' in line:
                        try:
                            import re
                            match = re.search(r'"timestamp":"([^"]+)"', line)
                            if match:
                                last_activity = match.group(1)[:16]  # Just date/time
                        except:
                            pass

        except Exception as e:
            pass

        return {
            'topics': list(topics)[:3],  # Top 3 topics
            'last_activity': last_activity
        }

    def format_context(self, summaries: List[Dict], hours: int) -> str:
        """Format context into readable output"""
        output = []
        output.append(f"FastContext: Last {hours} hours")
        output.append("━" * 40)
        output.append("")

        if not summaries:
            output.append("No recent activity")
            return "\\n".join(output)

        # Group by time
        today = []
        yesterday = []
        now = datetime.now()

        for summary in summaries:
            time_str = summary['time']
            if now.strftime("%b %d") in time_str:
                today.append(summary)
            else:
                yesterday.append(summary)

        if today:
            output.append(f"Today ({len(today)} conversations):")
            for s in today[:3]:  # Show max 3
                topics = ", ".join(s['topics']) if s['topics'] else "general"
                output.append(f"  • {s['time']} - {topics} ({s['size_mb']}MB)")

        if yesterday and hours > 24:
            output.append("")
            output.append(f"Earlier ({len(yesterday)} conversations):")
            for s in yesterday[:2]:  # Show max 2
                topics = ", ".join(s['topics']) if s['topics'] else "general"
                output.append(f"  • {s['time']} - {topics}")

        # Quick stats
        total_mb = sum(s['size_mb'] for s in summaries)
        all_topics = set()
        for s in summaries:
            all_topics.update(s['topics'])

        output.append("")
        output.append("Current Focus:")
        if all_topics:
            output.append(f"  → {', '.join(sorted(all_topics))}")
        output.append(f"  → {len(summaries)} active sessions ({total_mb:.1f}MB)")

        return "\\n".join(output)

    def load_last(self) -> str:
        """Load just the very last conversation"""
        files = list(self.project_dir.glob("*.jsonl"))
        if not files:
            return "No conversations found"

        # Get most recent file
        latest = max(files, key=lambda f: f.stat().st_mtime)

        # Read last 50 lines
        last_lines = self.tail_file(latest, 50)

        # Extract key info
        user_messages = []
        assistant_messages = []

        for line in last_lines:
            try:
                if '"role":"user"' in line:
                    # Try to extract content
                    if '"content":"' in line:
                        import re
                        match = re.search(r'"content":"([^"]{0,100})', line)
                        if match:
                            user_messages.append(match.group(1))
                elif '"role":"assistant"' in line and '"text":"' in line:
                    import re
                    match = re.search(r'"text":"([^"]{0,100})', line)
                    if match:
                        assistant_messages.append(match.group(1))
            except:
                continue

        output = []
        output.append("LastConversation:")
        output.append("━" * 40)
        output.append(f"File: {latest.stem[:8]}...")
        output.append(f"Time: {datetime.fromtimestamp(latest.stat().st_mtime).strftime('%b %d %H:%M')}")
        output.append("")

        if user_messages:
            output.append("Recent queries:")
            for msg in user_messages[-3:]:
                output.append(f"  • {msg[:60]}...")

        if assistant_messages:
            output.append("")
            output.append("Recent responses:")
            for msg in assistant_messages[-2:]:
                output.append(f"  • {msg[:60]}...")

        return "\\n".join(output)

    def tail_file(self, filepath: Path, lines: int = 50) -> List[str]:
        """Efficiently read last N lines"""
        try:
            with open(filepath, 'rb') as f:
                f.seek(0, 2)  # Go to end
                file_size = f.tell()

                # Read last 16KB
                block_size = min(16384, file_size)
                f.seek(-block_size, 2)

                tail_data = f.read().decode('utf-8', errors='ignore')
                return tail_data.splitlines()[-lines:]
        except:
            return []


def main():
    """CLI interface for fast context loading"""
    loader = FastContextLoader()

    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()

        if arg == "last":
            print(loader.load_last())
        elif arg == "today":
            # Since midnight
            hours = datetime.now().hour + (datetime.now().minute / 60)
            print(loader.load_context(int(hours) + 1))
        elif arg.endswith("h"):
            # Parse hours like "3h"
            try:
                hours = int(arg[:-1])
                print(loader.load_context(hours))
            except:
                print(loader.load_context())
        else:
            print(loader.load_context())
    else:
        # Default: last 24 hours
        print(loader.load_context())


if __name__ == "__main__":
    main()