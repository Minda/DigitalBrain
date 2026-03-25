#!/usr/bin/env python3
"""
Conversation History Indexer

Builds and maintains a SQLite index of all conversations for ultra-fast searching.
This replaces slow file-based searching with instant database queries.

Usage:
    python index_conversations.py          # Build/update index
    python index_conversations.py report   # Show statistics
    python index_conversations.py search "query"  # Search conversations
    python index_conversations.py recent   # Show recent conversations
"""

import sqlite3
import os
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import time


class ConversationIndex:
    """SQLite-backed conversation index for ultra-fast queries"""

    def __init__(self, db_path=None):
        self.db_path = db_path or os.path.expanduser("~/.claude/conversation_index.db")
        self.conn = None

    def connect(self):
        """Connect to SQLite database"""
        # Create directory if needed
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        """Create index tables with optimized schema"""

        # Main conversation table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY,
                path TEXT UNIQUE,
                filename TEXT,
                modified REAL,
                created REAL,
                size INTEGER,
                source TEXT,  -- 'claude' or 'chatgpt'
                title TEXT,
                model TEXT,
                topics TEXT,  -- JSON array
                summary TEXT,
                message_count INTEGER,
                indexed_at REAL
            )
        ''')

        # Optimized indexes for common queries
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_modified ON conversations(modified DESC)')
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_created ON conversations(created DESC)')
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_source ON conversations(source)')
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_model ON conversations(model)')

        # Full-text search table
        try:
            self.conn.execute('''
                CREATE VIRTUAL TABLE IF NOT EXISTS conversations_fts
                USING fts5(
                    path UNINDEXED,
                    title,
                    topics,
                    summary,
                    content=conversations
                )
            ''')
        except sqlite3.OperationalError:
            # Table already exists
            pass

        # Pre-computed statistics cache
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                date TEXT PRIMARY KEY,
                conversation_count INTEGER,
                topics TEXT,  -- JSON
                models_used TEXT,  -- JSON
                activity_pattern TEXT,  -- JSON
                computed_at REAL
            )
        ''')

        # User insights cache
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS user_insights (
                insight_type TEXT PRIMARY KEY,
                data TEXT,  -- JSON
                computed_at REAL
            )
        ''')

        self.conn.commit()

    def build_index(self, force=False):
        """Build or update the conversation index"""

        directories = [
            "/Users/min/.claude/projects/-Users-min-Documents-Projects-DigitalBrain",
            "/Users/min/Documents/Projects/DigitalBrain/personal/conversational-history"
        ]

        print("\n🔍 Building Conversation Index")
        print("=" * 50)

        total_indexed = 0
        start_time = time.time()

        for directory in directories:
            if os.path.exists(directory):
                print(f"\n📁 Indexing: {directory}")
                print(f"   Checking for conversation files...")
                count = self.index_directory(directory, force=force)
                total_indexed += count
                print(f"   ✓ Indexed {count} files")
            else:
                print(f"\n⚠️  Directory not found: {directory}")

        # Compute initial statistics
        print("\n📊 Computing statistics...")
        self.compute_statistics()

        elapsed = time.time() - start_time
        print("\n" + "=" * 50)
        print(f"✅ Indexing complete!")
        print(f"   • Total conversations: {total_indexed:,}")
        print(f"   • Time taken: {elapsed:.1f}s")
        print(f"   • Database: {self.db_path}")
        print(f"   • Size: {self.get_db_size():.1f}MB")

    def index_directory(self, directory, force=False):
        """Index all conversations in a directory"""

        indexed_count = 0
        skipped_count = 0

        # Determine source type
        source = 'claude' if '.claude' in directory else 'chatgpt'

        # Count total files first
        total_files = sum(1 for root, dirs, files in os.walk(directory)
                         for file in files if file.endswith(('.json', '.jsonl', '.md')))

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(('.json', '.jsonl', '.md')):
                    file_path = os.path.join(root, file)

                    # Check if needs indexing
                    if not force:
                        cursor = self.conn.execute(
                            "SELECT modified FROM conversations WHERE path = ?",
                            (file_path,)
                        )
                        existing = cursor.fetchone()

                        if existing:
                            try:
                                stat = os.stat(file_path)
                                if existing['modified'] >= stat.st_mtime:
                                    skipped_count += 1
                                    continue  # Skip unchanged files
                            except OSError:
                                continue

                    # Index the file
                    if self.index_file(file_path, source):
                        indexed_count += 1

                        # Show progress
                        if indexed_count % 100 == 0:
                            print(f"     Processing... {indexed_count} files indexed so far")

        if skipped_count > 0:
            print(f"     Skipped {skipped_count} unchanged files")

        self.conn.commit()
        return indexed_count

    def index_file(self, file_path, source):
        """Index a single conversation file"""
        try:
            stat = os.stat(file_path)

            # Extract metadata based on file type
            if file_path.endswith('.md'):
                # ChatGPT export format
                metadata = self.parse_chatgpt_markdown(file_path)
            elif file_path.endswith(('.json', '.jsonl')):
                # Claude format
                metadata = self.parse_claude_json(file_path)
            else:
                return False

            # Insert or update index
            self.conn.execute('''
                INSERT OR REPLACE INTO conversations
                (path, filename, modified, created, size, source, title, model,
                 topics, summary, message_count, indexed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                file_path,
                os.path.basename(file_path),
                stat.st_mtime,
                metadata.get('created', stat.st_mtime),
                stat.st_size,
                source,
                metadata.get('title', ''),
                metadata.get('model', ''),
                json.dumps(metadata.get('topics', [])),
                metadata.get('summary', ''),
                metadata.get('message_count', 0),
                time.time()
            ))

            # Update FTS index
            try:
                self.conn.execute('''
                    INSERT OR REPLACE INTO conversations_fts
                    (rowid, title, topics, summary)
                    SELECT id, title, topics, summary
                    FROM conversations
                    WHERE path = ?
                ''', (file_path,))
            except:
                pass  # FTS update can fail for various reasons

            return True

        except Exception as e:
            # Silently skip files with errors
            return False

    def parse_chatgpt_markdown(self, file_path):
        """Parse ChatGPT exported markdown file"""
        metadata = {
            'topics': [],
            'message_count': 0,
            'title': '',
            'model': '',
            'summary': ''
        }

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Read first 100 lines for metadata
                lines = []
                for i, line in enumerate(f):
                    if i >= 100:
                        break
                    lines.append(line)

                # Check if file has YAML frontmatter
                if lines and lines[0].strip() == '---':
                    # Parse YAML frontmatter
                    in_frontmatter = True
                    for line in lines[1:]:
                        if line.strip() == '---':
                            in_frontmatter = False
                            break
                        if in_frontmatter:
                            if line.startswith('title:'):
                                metadata['title'] = line[6:].strip().strip("'\"")[:200]
                            elif line.startswith('model:'):
                                metadata['model'] = line[6:].strip().strip("'\"")
                            elif line.startswith('created:'):
                                date_str = line[8:].strip().strip("'\"")
                                try:
                                    # Handle ISO format with microseconds
                                    if 'T' in date_str:
                                        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                                        metadata['created'] = dt.timestamp()
                                except:
                                    pass
                            elif line.startswith('message_count:'):
                                try:
                                    metadata['message_count'] = int(line[14:].strip())
                                except:
                                    pass
                else:
                    # Old format - look for headers
                    for line in lines:
                        if line.startswith('# ') and not metadata['title']:
                            metadata['title'] = line[2:].strip()[:200]
                        elif line.startswith('model:'):
                            metadata['model'] = line[6:].strip()
                        elif line.startswith('date:'):
                            date_str = line[5:].strip()
                            try:
                                # Try various date formats
                                for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S']:
                                    try:
                                        dt = datetime.strptime(date_str[:19], fmt)
                                        metadata['created'] = dt.timestamp()
                                        break
                                    except:
                                        continue
                            except:
                                pass

                # Get a summary from the content
                content = ''.join(lines[:50])
                if len(content) > 100:
                    # Clean up the summary
                    summary = content[50:250].replace('\n', ' ').replace('  ', ' ')
                    metadata['summary'] = summary[:150]

                # Count messages if not already set
                if metadata['message_count'] == 0:
                    metadata['message_count'] = content.count('\n## User') + content.count('\n## Assistant')

        except Exception:
            pass  # Silently handle file read errors

        return metadata

    def parse_claude_json(self, file_path):
        """Parse Claude conversation JSON/JSONL file"""
        metadata = {
            'topics': [],
            'message_count': 0,
            'title': '',
            'model': 'claude',
            'summary': ''
        }

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Read first line for JSONL format
                first_line = f.readline()
                if first_line:
                    try:
                        data = json.loads(first_line)
                        metadata['title'] = data.get('name', '')[:200]

                        # Handle various timestamp formats
                        created = data.get('created_at', data.get('timestamp', time.time()))
                        if isinstance(created, str):
                            try:
                                created = datetime.fromisoformat(created).timestamp()
                            except:
                                created = time.time()
                        metadata['created'] = created

                        # Count messages
                        f.seek(0)
                        line_count = sum(1 for line in f if line.strip())
                        metadata['message_count'] = line_count

                    except json.JSONDecodeError:
                        pass

        except Exception:
            pass  # Silently handle file read errors

        return metadata

    def search_recent(self, hours=168):
        """Get recent conversations (default: last 7 days)"""
        cutoff = (datetime.now() - timedelta(hours=hours)).timestamp()

        cursor = self.conn.execute('''
            SELECT path, filename, modified, source, title, summary, message_count
            FROM conversations
            WHERE modified > ?
            ORDER BY modified DESC
            LIMIT 50
        ''', (cutoff,))

        return cursor.fetchall()

    def search_topic(self, query):
        """Full-text search for topic"""
        try:
            cursor = self.conn.execute('''
                SELECT c.path, c.filename, c.modified, c.source, c.title, c.summary
                FROM conversations c
                JOIN conversations_fts fts ON c.rowid = fts.rowid
                WHERE conversations_fts MATCH ?
                ORDER BY c.modified DESC
                LIMIT 50
            ''', (query,))
            return cursor.fetchall()
        except:
            # Fallback to LIKE search if FTS fails
            cursor = self.conn.execute('''
                SELECT path, filename, modified, source, title, summary
                FROM conversations
                WHERE title LIKE ? OR summary LIKE ?
                ORDER BY modified DESC
                LIMIT 50
            ''', (f'%{query}%', f'%{query}%'))
            return cursor.fetchall()

    def get_statistics(self):
        """Get pre-computed statistics"""
        cursor = self.conn.execute('''
            SELECT
                COUNT(*) as total,
                COUNT(CASE WHEN source = 'claude' THEN 1 END) as claude_count,
                COUNT(CASE WHEN source = 'chatgpt' THEN 1 END) as chatgpt_count,
                MIN(created) as earliest,
                MAX(created) as latest,
                SUM(message_count) as total_messages
            FROM conversations
        ''')

        return cursor.fetchone()

    def compute_statistics(self):
        """Pre-compute and cache statistics"""

        # Model usage
        cursor = self.conn.execute('''
            SELECT model, COUNT(*) as count
            FROM conversations
            WHERE model != ''
            GROUP BY model
            ORDER BY count DESC
            LIMIT 20
        ''')

        model_stats = {row['model']: row['count'] for row in cursor.fetchall()}

        # Cache user insights
        self.conn.execute('''
            INSERT OR REPLACE INTO user_insights (insight_type, data, computed_at)
            VALUES ('model_usage', ?, ?)
        ''', (json.dumps(model_stats), time.time()))

        self.conn.commit()

    def show_report(self):
        """Show comprehensive statistics report"""

        stats = self.get_statistics()

        if not stats or stats['total'] == 0:
            print("\n⚠️  No conversations indexed yet. Run the indexer first.")
            return

        total = stats['total'] or 0
        claude_count = stats['claude_count'] or 0
        chatgpt_count = stats['chatgpt_count'] or 0

        earliest = datetime.fromtimestamp(stats['earliest']) if stats['earliest'] else datetime.now()
        latest = datetime.fromtimestamp(stats['latest']) if stats['latest'] else datetime.now()

        print(f"""
📊 Conversation History Report
{'=' * 50}

Database: {self.db_path}
Size: {self.get_db_size():.1f}MB
Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Coverage: {earliest.strftime('%b %Y')} → {latest.strftime('%b %Y')}
Duration: {(latest - earliest).days} days

Total Conversations: {total:,}
  • Claude Code:  {claude_count:,} ({claude_count*100//max(total,1)}%)
  • ChatGPT:      {chatgpt_count:,} ({chatgpt_count*100//max(total,1)}%)

Total Messages: {stats['total_messages'] or 0:,}
Avg Messages/Conversation: {(stats['total_messages'] or 0)//max(total,1)}

Top Models Used:""")

        # Show model usage
        cursor = self.conn.execute('''
            SELECT model, COUNT(*) as count
            FROM conversations
            WHERE model != ''
            GROUP BY model
            ORDER BY count DESC
            LIMIT 10
        ''')

        for row in cursor.fetchall():
            print(f"  • {row['model'][:30]:30} {row['count']:,}")

    def show_recent(self):
        """Show recent conversations"""

        results = self.search_recent(hours=168)

        print(f"\n📅 Recent Conversations (Last 7 Days)")
        print("=" * 50)

        if not results:
            print("\nNo recent conversations found.")
            return

        # Group by day
        by_day = defaultdict(list)
        for r in results:
            date = datetime.fromtimestamp(r['modified']).strftime('%Y-%m-%d')
            by_day[date].append(r)

        for date in sorted(by_day.keys(), reverse=True)[:7]:
            day_results = by_day[date]
            date_obj = datetime.strptime(date, '%Y-%m-%d')

            if date == datetime.now().strftime('%Y-%m-%d'):
                day_label = "Today"
            elif date == (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'):
                day_label = "Yesterday"
            else:
                day_label = date_obj.strftime('%A, %b %d')

            print(f"\n{day_label} ({len(day_results)} conversations):")

            for r in day_results[:5]:
                title = r['title'] or r['filename']
                if len(title) > 60:
                    title = title[:57] + "..."
                source = "📱" if r['source'] == 'claude' else "💬"
                print(f"  {source} {title}")

            if len(day_results) > 5:
                print(f"     ... and {len(day_results) - 5} more")

    def search(self, query):
        """Search for conversations"""

        results = self.search_topic(query)

        print(f"\n🔍 Search Results: '{query}'")
        print("=" * 50)

        if not results:
            print("\nNo matching conversations found.")
            return

        print(f"\nFound {len(results)} relevant conversations:\n")

        for r in results[:20]:
            date = datetime.fromtimestamp(r['modified']).strftime('%b %d, %Y')
            title = r['title'] or r['filename']
            if len(title) > 60:
                title = title[:57] + "..."

            source = "📱" if r['source'] == 'claude' else "💬"
            print(f"{source} {date}: {title}")

            if r['summary']:
                summary = r['summary'][:100]
                print(f"   {summary}...")

        if len(results) > 20:
            print(f"\n... and {len(results) - 20} more results")

    def get_db_size(self):
        """Get database file size in MB"""
        try:
            return os.path.getsize(self.db_path) / (1024 * 1024)
        except:
            return 0.0


def main():
    """Main entry point"""

    index = ConversationIndex()
    index.connect()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == 'report':
            index.show_report()
        elif command == 'recent':
            index.show_recent()
        elif command == 'search' and len(sys.argv) > 2:
            query = ' '.join(sys.argv[2:])
            index.search(query)
        elif command == 'force':
            index.build_index(force=True)
        else:
            print(f"Unknown command: {command}")
            print("\nUsage:")
            print("  python index_conversations.py          # Build/update index")
            print("  python index_conversations.py report   # Show statistics")
            print("  python index_conversations.py recent   # Show recent")
            print("  python index_conversations.py search 'query'  # Search")
            print("  python index_conversations.py force    # Force rebuild")
    else:
        # Default: build/update index
        index.build_index()


if __name__ == "__main__":
    main()