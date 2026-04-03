#!/usr/bin/env python3
"""
Recent Files Context Skill
Shows recently edited files with optional change details
"""

import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

# File type icons
FILE_ICONS = {
    '.md': '📄',
    '.py': '🐍',
    '.txt': '📝',
    '.sh': '🔧',
    '.json': '📊',
    '.css': '🎨',
    '.html': '🌐',
    '.js': '⚛️',
    '.jsx': '⚛️',
    '.ts': '⚛️',
    '.tsx': '⚛️',
    '.yaml': '📦',
    '.yml': '📦',
    '.pdf': '📚',
    '.jpg': '🖼️',
    '.png': '🖼️',
    '.gif': '🖼️',
    '.svg': '🎨',
    '.mp4': '🎬',
    '.mp3': '🎵',
    '.zip': '📦',
}

def get_file_icon(filepath):
    """Get icon for file type"""
    ext = Path(filepath).suffix.lower()
    return FILE_ICONS.get(ext, '📂')

def get_recent_files(limit=10):
    """Get recently modified files from git"""
    try:
        # Try git first for tracked files
        result = subprocess.run(
            ['git', 'log', '--pretty=format:', '--name-only', f'-{limit*2}'],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            files = []
            seen = set()
            for line in result.stdout.strip().split('\n'):
                if line and line not in seen and os.path.exists(line):
                    files.append(line)
                    seen.add(line)
                    if len(files) >= limit:
                        break
            return files
    except:
        pass

    # Fallback to finding recently modified files
    try:
        result = subprocess.run(
            ['find', '.', '-type', 'f', '-not', '-path', '*/\.*', '-mtime', '-7'],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            files = []
            for line in result.stdout.strip().split('\n'):
                if line and os.path.exists(line):
                    files.append(line.lstrip('./'))

            # Sort by modification time
            files.sort(key=lambda x: os.path.getmtime(x) if os.path.exists(x) else 0, reverse=True)
            return files[:limit]
    except:
        pass

    return []

def get_file_changes(filepath):
    """Get change statistics for a file"""
    try:
        # Get diff stats
        result = subprocess.run(
            ['git', 'diff', 'HEAD~1', 'HEAD', '--shortstat', '--', filepath],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except:
        pass

    return None

def get_file_diff_preview(filepath, lines=10):
    """Get preview of changes for a file"""
    try:
        result = subprocess.run(
            ['git', 'diff', 'HEAD~1', 'HEAD', '--', filepath],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0 and result.stdout.strip():
            diff_lines = result.stdout.strip().split('\n')[:lines]
            # Filter to show only actual changes
            preview_lines = []
            for line in diff_lines:
                if line.startswith('+') or line.startswith('-'):
                    if not line.startswith('+++') and not line.startswith('---'):
                        preview_lines.append(line)
            return preview_lines[:5]  # Limit preview to 5 lines
    except:
        pass

    return None

def show_recent_files(full=False):
    """Main function to show recent files"""

    if full:
        print("📂 Recent Files with Changes")
        print("══════════════════════════════")
    else:
        print("📂 Recent Files Edited")
        print("═══════════════════════")

    print()

    files = get_recent_files()

    if not files:
        print("No recent files found.")
        return

    for i, filepath in enumerate(files, 1):
        icon = get_file_icon(filepath)

        # Make path clickable
        print(f"{i}. {icon} {filepath}")

        # Get modification time
        try:
            mtime = os.path.getmtime(filepath)
            mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            print(f"   Modified: {mtime_str}")
        except:
            print(f"   Modified: recently")

        if full:
            # Show change statistics
            changes = get_file_changes(filepath)
            if changes:
                print(f"   Changes: {changes}")

            # Show preview of changes
            preview = get_file_diff_preview(filepath)
            if preview:
                print("   Preview:")
                for line in preview:
                    print(f"   {line}")

        print()

def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == 'full':
        show_recent_files(full=True)
    else:
        show_recent_files(full=False)

if __name__ == '__main__':
    main()