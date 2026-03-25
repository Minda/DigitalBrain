# Fast Context Loading System

## Problem Analysis
- 248MB of conversation data across 55 files
- Some individual files are 25MB+
- Current approach reads and parses everything
- No indexing, caching, or smart filtering

## Solution 1: SQLite Index Database

Create a lightweight SQLite index that stores:
```sql
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,
    file_path TEXT,
    timestamp INTEGER,
    summary TEXT,
    topics TEXT,  -- JSON array
    user_messages INTEGER,
    assistant_messages INTEGER,
    tools_used TEXT,  -- JSON array
    files_mentioned TEXT  -- JSON array
);

CREATE INDEX idx_timestamp ON conversations(timestamp);
CREATE INDEX idx_topics ON conversations(topics);
CREATE VIRTUAL TABLE conversation_fts USING fts5(
    summary, topics, content=conversations
);
```

### Build Index Script
```python
import sqlite3
import json
from pathlib import Path
from datetime import datetime

def build_conversation_index():
    """One-time indexing of all conversations"""
    db_path = Path("~/.cache/claude-conversations/index.db").expanduser()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    # Create tables...

    for jsonl_file in Path("/Users/min/.claude/projects").glob("*/*.jsonl"):
        index_conversation_file(conn, jsonl_file)

    conn.commit()
    conn.close()

def index_conversation_file(conn, jsonl_path):
    """Index a single conversation file"""
    file_id = jsonl_path.stem

    # Extract key metadata without loading entire file
    with open(jsonl_path, 'r') as f:
        first_line = f.readline()
        last_line = None
        line_count = 0

        # Efficiently get last line
        for line in f:
            line_count += 1
            if line.strip():
                last_line = line

        # Parse key info
        metadata = extract_metadata(first_line, last_line)

    conn.execute("""
        INSERT OR REPLACE INTO conversations
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (file_id, str(jsonl_path), metadata['timestamp'],
          metadata['summary'], json.dumps(metadata['topics']), ...))
```

## Solution 2: Fast Recent Context Command

### `/context` - Ultra-fast recent context loader
```python
def load_fast_context(hours=24):
    """Load only the most recent context quickly"""

    # 1. Use file modification times to filter
    cutoff = datetime.now() - timedelta(hours=hours)
    recent_files = []

    for f in Path("/Users/min/.claude/projects").glob("*/*.jsonl"):
        if f.stat().st_mtime > cutoff.timestamp():
            recent_files.append(f)

    # 2. Read only last N lines from each file
    context = []
    for f in sorted(recent_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
        # Use tail-like approach
        last_messages = tail_file(f, lines=20)
        context.append(extract_key_points(last_messages))

    return format_quick_context(context)

def tail_file(filepath, lines=20):
    """Efficiently read last N lines without loading entire file"""
    with open(filepath, 'rb') as f:
        # Seek to end and work backwards
        f.seek(0, 2)  # Go to end
        file_size = f.tell()

        # Read last 8KB (usually enough for 20 lines)
        block_size = min(8192, file_size)
        f.seek(-block_size, 2)

        tail_data = f.read().decode('utf-8', errors='ignore')
        return tail_data.splitlines()[-lines:]
```

### Command Structure
```bash
# Ultra-fast commands
/context              # Last 24 hours, summary only
/context 3h           # Last 3 hours
/context today        # Since midnight
/context last         # Just the last conversation

# These would be FAST because they:
# 1. Only check file timestamps first
# 2. Only read recent files
# 3. Only parse last few messages
# 4. Use cached summaries when available
```

## Solution 3: Incremental Background Indexing

```python
class ConversationIndexer:
    def __init__(self):
        self.index_path = Path("~/.cache/claude-conversations/")
        self.last_indexed = self.load_last_indexed()

    def incremental_update(self):
        """Run in background, only index new/changed files"""
        for jsonl_file in self.find_unindexed_files():
            # Create small summary file
            summary = self.create_summary(jsonl_file)
            summary_path = self.index_path / f"{jsonl_file.stem}.summary"
            summary_path.write_text(json.dumps(summary))

    def create_summary(self, jsonl_file):
        """Create lightweight summary of conversation"""
        return {
            'id': jsonl_file.stem,
            'path': str(jsonl_file),
            'size': jsonl_file.stat().st_size,
            'modified': jsonl_file.stat().st_mtime,
            'first_message': self.get_first_message(jsonl_file),
            'last_message': self.get_last_message(jsonl_file),
            'message_count': self.count_messages(jsonl_file),
            'topics': self.extract_topics_sample(jsonl_file)
        }
```

## Solution 4: Memory-Mapped File Access

```python
import mmap

def search_large_file_mmap(filepath, query):
    """Use memory mapping for large files"""
    with open(filepath, 'r+b') as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mmapped:
            # Search without loading entire file
            query_bytes = query.encode('utf-8')
            position = mmapped.find(query_bytes)

            if position != -1:
                # Extract context around match
                start = max(0, position - 500)
                end = min(len(mmapped), position + 500)
                context = mmapped[start:end].decode('utf-8', errors='ignore')
                return context
```

## Implementation Priority

1. **Immediate (5 min):** Add `/context` command for fast recent loading
2. **Short-term (30 min):** Build SQLite index for existing conversations
3. **Medium-term (2 hr):** Implement incremental indexing system
4. **Long-term:** Add memory mapping for large file searches

## Performance Targets

Current: ~3-5 seconds for basic search
Target:
- `/context`: < 200ms
- `/conversational-history recent`: < 500ms
- `/conversational-history [topic]`: < 1 second
- `/conversational-history report`: < 2 seconds (with cache)