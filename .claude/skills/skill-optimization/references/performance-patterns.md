# Performance Optimization Patterns

Common bottlenecks and proven solutions for optimizing Claude Code skills.

## Pattern: File-Based → Index-Based

**When to use:** Searching through many files (>100 files or >10MB total)

**Problem:**
- Walking directory trees repeatedly
- Opening and parsing every file for searches
- O(n) complexity for every query
- Slow response times (10-30 seconds)

**Solution:**
Build a SQLite or JSON index that stores searchable metadata.

**Implementation:**
```python
import sqlite3
import json
from pathlib import Path

def build_index(content_dir, index_path):
    """Build SQLite FTS5 index for fast searching"""
    conn = sqlite3.connect(index_path)

    # Create FTS5 table for full-text search
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS content_fts USING fts5(
            file_path,
            title,
            content,
            metadata
        )
    """)

    # Index all files
    for file_path in Path(content_dir).rglob("*.md"):
        with open(file_path) as f:
            content = f.read()

        # Extract metadata (frontmatter, etc.)
        title = extract_title(content)
        metadata = extract_metadata(content)

        conn.execute("""
            INSERT INTO content_fts (file_path, title, content, metadata)
            VALUES (?, ?, ?, ?)
        """, (str(file_path), title, content, json.dumps(metadata)))

    conn.commit()
    conn.close()

def search_index(index_path, query):
    """Search index in <100ms"""
    conn = sqlite3.connect(index_path)
    cursor = conn.execute("""
        SELECT file_path, title, snippet(content_fts, 2, '<b>', '</b>', '...', 50)
        FROM content_fts
        WHERE content_fts MATCH ?
        ORDER BY rank
        LIMIT 20
    """, (query,))

    results = cursor.fetchall()
    conn.close()
    return results
```

**Expected Improvement:** 50-200x faster (15s → 0.1s)

**Real-world example:** conversational-history skill optimization

**Trade-offs:**
- ✅ Dramatically faster queries
- ✅ Supports complex search syntax
- ✅ Can index metadata separately
- ⚠️ One-time indexing cost (acceptable)
- ⚠️ Requires SQLite dependency
- ⚠️ Index needs updating when content changes

---

## Pattern: Full-Parse → Tail-Read

**When to use:** Only need recent data from large log files or append-only files

**Problem:**
- Reading entire multi-GB log files
- Parsing from beginning every time
- Most of the file is old data you don't need

**Solution:**
Read only the last N bytes of the file.

**Implementation:**
```python
def read_recent_logs(log_file, max_bytes=1024*1024):
    """Read only the last 1MB of a log file"""
    with open(log_file, 'rb') as f:
        # Seek to end
        f.seek(0, 2)
        file_size = f.tell()

        # Read last N bytes
        start_pos = max(0, file_size - max_bytes)
        f.seek(start_pos)

        # Read and decode
        data = f.read()
        return data.decode('utf-8', errors='ignore')

def get_recent_context(conversation_file, num_lines=100):
    """Get last N lines without reading entire file"""
    with open(conversation_file, 'rb') as f:
        # Estimate: ~80 bytes per line
        estimated_bytes = num_lines * 80

        f.seek(0, 2)
        file_size = f.tell()
        start = max(0, file_size - estimated_bytes)
        f.seek(start)

        lines = f.readlines()
        return [line.decode('utf-8') for line in lines[-num_lines:]]
```

**Expected Improvement:** 10-50x faster

**Real-world example:** fast_context.py in conversational-history

**Trade-offs:**
- ✅ Constant time regardless of file size
- ✅ Minimal memory usage
- ✅ No dependencies
- ⚠️ Need to estimate byte size per line
- ⚠️ May miss context boundaries

---

## Pattern: Sync → Async

**When to use:** Multiple independent operations (API calls, file reads, external commands)

**Problem:**
- Sequential operations waiting for each other
- Network latency compounds
- CPU sits idle during I/O

**Solution:**
Run operations in parallel using `asyncio` or `concurrent.futures`.

**Implementation:**
```python
import asyncio
import aiofiles
from pathlib import Path

# Before: Sequential (slow)
def process_files_sync(file_paths):
    results = []
    for path in file_paths:
        with open(path) as f:
            content = f.read()
        result = expensive_processing(content)
        results.append(result)
    return results

# After: Parallel (fast)
async def process_files_async(file_paths):
    async def process_one(path):
        async with aiofiles.open(path) as f:
            content = await f.read()
        return await expensive_processing_async(content)

    # Process all files concurrently
    results = await asyncio.gather(*[process_one(p) for p in file_paths])
    return results

# Or using ThreadPoolExecutor for CPU-bound work
from concurrent.futures import ThreadPoolExecutor

def process_files_parallel(file_paths, max_workers=4):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_file, file_paths))
    return results
```

**Expected Improvement:** 3-10x faster (scales with number of operations)

**Use cases:**
- Multiple API calls
- Processing multiple files
- Multiple external commands
- Network requests

**Trade-offs:**
- ✅ Better resource utilization
- ✅ Faster overall completion
- ⚠️ More complex error handling
- ⚠️ Need to manage concurrency limits
- ⚠️ Not helpful for single operations

---

## Pattern: Every-Time → Cache

**When to use:** Expensive computations with repeated inputs

**Problem:**
- Recalculating same results
- Fetching same data repeatedly
- No reuse across invocations

**Solution:**
Add a caching layer with TTL (time-to-live).

**Implementation:**
```python
import time
import hashlib
import json
from pathlib import Path

class DiskCache:
    """Simple disk-based cache with TTL"""

    def __init__(self, cache_dir, ttl_seconds=3600):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = ttl_seconds

    def _cache_key(self, key):
        """Generate cache filename from key"""
        key_hash = hashlib.sha256(str(key).encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"

    def get(self, key):
        """Get cached value if not expired"""
        cache_file = self._cache_key(key)

        if not cache_file.exists():
            return None

        # Check expiry
        mtime = cache_file.stat().st_mtime
        if time.time() - mtime > self.ttl:
            cache_file.unlink()
            return None

        with open(cache_file) as f:
            return json.load(f)

    def set(self, key, value):
        """Store value in cache"""
        cache_file = self._cache_key(key)
        with open(cache_file, 'w') as f:
            json.dump(value, f)

# Usage
cache = DiskCache("~/.cache/skill-name", ttl_seconds=3600)

def expensive_operation(input_data):
    # Check cache first
    cached = cache.get(input_data)
    if cached is not None:
        return cached

    # Compute if not cached
    result = do_expensive_computation(input_data)

    # Store in cache
    cache.set(input_data, result)
    return result
```

**In-memory cache (faster but doesn't persist):**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_function(arg1, arg2):
    # Computation here
    return result
```

**Expected Improvement:** 10-100x for cache hits

**Trade-offs:**
- ✅ Dramatic speedup for repeated operations
- ✅ Easy to implement
- ⚠️ Cache invalidation complexity
- ⚠️ Disk space usage
- ⚠️ Stale data risk

---

## Pattern: Full Parsing → Targeted Extraction

**When to use:** Only need specific fields from large structured files

**Problem:**
- Parsing entire JSON/YAML files
- Loading full document into memory
- Processing fields you don't need

**Solution:**
Use streaming parsers or targeted regex extraction.

**Implementation:**
```python
import re
import ijson  # streaming JSON parser

# Before: Full parse
def get_title_full(file_path):
    with open(file_path) as f:
        data = json.load(f)  # Loads entire file
    return data['metadata']['title']

# After: Targeted extraction
def get_title_fast(file_path):
    """Extract title without full parse"""
    with open(file_path) as f:
        # Read only first 1KB (frontmatter typically at start)
        header = f.read(1024)

    # Regex to extract title from YAML frontmatter
    match = re.search(r'^title:\s*(.+)$', header, re.MULTILINE)
    if match:
        return match.group(1).strip()

    return None

# For large JSON files, use streaming parser
def extract_specific_fields(json_file):
    """Stream parse large JSON file"""
    with open(json_file, 'rb') as f:
        parser = ijson.parse(f)

        for prefix, event, value in parser:
            if prefix == 'metadata.title':
                return value
```

**Expected Improvement:** 5-20x faster

**Use cases:**
- Extracting frontmatter from markdown
- Getting specific JSON fields
- Reading specific sections of XML
- Extracting metadata without full processing

**Trade-offs:**
- ✅ Much faster for large files
- ✅ Lower memory usage
- ⚠️ More fragile (assumes format)
- ⚠️ Misses complex nested data

---

## Pattern: Eager Loading → Lazy Loading

**When to use:** Skills with optional features or modes

**Problem:**
- Loading all references and resources upfront
- High token consumption even when not needed
- Slow skill initialization

**Solution:**
Load resources only when actually used.

**Implementation:**
```markdown
## Instructions

For basic usage, follow these steps:
1. ...
2. ...

For advanced features, see `references/advanced-usage.md`.

## Advanced Mode

[Only load this section if user explicitly requests advanced features]
```

**In code:**
```python
class Skill:
    def __init__(self):
        self.advanced_config = None  # Don't load yet

    def use_advanced_feature(self):
        if self.advanced_config is None:
            # Load only when needed
            self.advanced_config = load_advanced_config()

        return self.advanced_config
```

**Expected Improvement:** 2-5x faster initialization, lower base token usage

**Trade-offs:**
- ✅ Faster for common cases
- ✅ Lower baseline token usage
- ⚠️ Slightly slower for advanced cases
- ⚠️ More complex control flow

---

## Choosing the Right Pattern

| Your Bottleneck | Apply This Pattern | Expected Gain |
|-----------------|-------------------|---------------|
| Searching many files | File-Based → Index | 50-200x |
| Reading large log files | Full-Parse → Tail-Read | 10-50x |
| Multiple API calls | Sync → Async | 3-10x |
| Repeated computations | Every-Time → Cache | 10-100x |
| Full document parsing | Full-Parse → Targeted | 5-20x |
| Unused features loading | Eager → Lazy | 2-5x |

## Combination Strategies

Often, combining multiple patterns yields best results:

**Example: Conversational History Optimization**
1. File-Based → Index (200x improvement)
2. Every-Time → Cache (reports generation)
3. Full-Parse → Targeted (context extraction)

**Result:** 15-23s searches → <100ms

## Anti-Patterns

**Don't:**
- Apply optimizations before measuring
- Optimize for hypothetical future scale
- Add complexity for <10% improvement
- Cache everything (memory bloat)
- Skip incremental testing

**Do:**
- Profile first, optimize second
- Start with simplest solution
- Measure before and after
- Test with realistic data
- Document tradeoffs made

---

**Remember:** The best optimization is often simplification. Remove unnecessary work before making necessary work faster.
