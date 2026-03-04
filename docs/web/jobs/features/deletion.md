# Job Deletion Feature

**Status**: Implemented
**Added**: 2025-03-03
**CLI Command**: `delete`

---

## Overview

Delete jobs from the database with flexible filtering by source, date discovered, or both. Includes safety features like confirmation prompts, dry-run mode, and preview counts.

---

## Features

### Core Deletion Modes

1. **Delete All** - Remove all jobs from database
2. **Delete by Source** - Remove all jobs from specific source (hn, 80k)
3. **Delete by Date** - Remove jobs discovered before/after a date
4. **Delete by Date Range** - Remove jobs between two dates
5. **Combined Filters** - Mix source + date filters

### Safety Features

- **Confirmation Prompt** - Shows count and asks for confirmation before deleting
- **Dry Run Mode** - Preview count without actually deleting
- **Force Flag** - Skip confirmation for automated scripts
- **JSON Output** - Machine-readable output for integration

---

## Command Reference

### Basic Syntax

```bash
uv run python -m mcp_jobs.cli delete [OPTIONS]
```

### Options

| Option | Type | Description |
|--------|------|-------------|
| `--all` | flag | Delete all jobs (requires at least one filter if not specified) |
| `--source` | choice | Filter by source: `hn` or `80k` |
| `--before` | date | Delete jobs discovered before date (YYYY-MM-DD) |
| `--after` | date | Delete jobs discovered after date (YYYY-MM-DD) |
| `--between` | dates | Delete jobs between two dates (START END) |
| `--dry-run` | flag | Show count without deleting |
| `--force` | flag | Skip confirmation prompt |
| `--json` | flag | Output result as JSON |

---

## Usage Examples

### Delete All Jobs

```bash
# With confirmation
uv run python -m mcp_jobs.cli delete --all

# Output:
# About to delete 247 job(s) (all jobs)
# Are you sure? [y/N]: y
# Deleted 247 job(s)
```

### Delete by Source

```bash
# Delete all HN jobs
uv run python -m mcp_jobs.cli delete --source hn

# Delete all 80k Hours jobs
uv run python -m mcp_jobs.cli delete --source 80k
```

### Delete by Date

```bash
# Delete jobs discovered before Feb 1, 2025
uv run python -m mcp_jobs.cli delete --before 2025-02-01

# Delete jobs discovered after Jan 1, 2025
uv run python -m mcp_jobs.cli delete --after 2025-01-01
```

### Delete by Date Range

```bash
# Delete jobs discovered in January 2025
uv run python -m mcp_jobs.cli delete --between 2025-01-01 2025-01-31
```

### Combined Filters

```bash
# Delete HN jobs older than 30 days
uv run python -m mcp_jobs.cli delete --source hn --before 2025-02-01

# Delete 80k jobs from last week
uv run python -m mcp_jobs.cli delete --source 80k --after 2025-02-24
```

### Dry Run (Preview)

```bash
# Preview without deleting
uv run python -m mcp_jobs.cli delete --source hn --dry-run

# Output:
# Would delete 123 job(s) (source=hn)
```

### Force Mode (No Confirmation)

```bash
# For scripts and automation
uv run python -m mcp_jobs.cli delete --all --force

# Deletes immediately without prompt
# Output:
# Deleted 247 job(s)
```

### JSON Output

```bash
# Machine-readable output
uv run python -m mcp_jobs.cli delete --source hn --json

# Output:
# {"deleted": 123, "filters": "source=hn"}
```

---

## Common Use Cases

### 1. Clean Up Old Jobs

Delete jobs older than 30 days to keep database fresh:

```bash
# Calculate date 30 days ago
DATE_30_DAYS_AGO=$(date -v-30d +%Y-%m-%d)  # macOS
# DATE_30_DAYS_AGO=$(date -d "30 days ago" +%Y-%m-%d)  # Linux

# Delete old jobs
uv run python -m mcp_jobs.cli delete --before $DATE_30_DAYS_AGO
```

### 2. Remove Failed Scrape

If a scrape pulled in bad data, remove it:

```bash
# Check when jobs were added
sqlite3 data/jobs.db "SELECT DATE(discovered_at), COUNT(*) FROM jobs GROUP BY DATE(discovered_at) ORDER BY discovered_at DESC LIMIT 5"

# Delete jobs from today
uv run python -m mcp_jobs.cli delete --after 2025-03-03 --before 2025-03-04
```

### 3. Reset Specific Source

Start fresh with one source:

```bash
# Preview
uv run python -m mcp_jobs.cli delete --source 80k --dry-run

# Delete
uv run python -m mcp_jobs.cli delete --source 80k

# Re-scrape
uv run python -m mcp_jobs.cli scrape --source 80k
```

### 4. Automated Cleanup Script

Weekly cron job to delete old entries:

```bash
#!/bin/bash
# cleanup-old-jobs.sh

# Delete jobs older than 60 days
CUTOFF=$(date -v-60d +%Y-%m-%d)
cd /path/to/DigitalBrain/app/mcp/jobs
~/.local/bin/uv run python -m mcp_jobs.cli delete --before $CUTOFF --force --json
```

Add to crontab:
```
0 2 * * 0 /path/to/cleanup-old-jobs.sh
```

---

## Error Handling

### No Matches

If no jobs match the filter:

```bash
uv run python -m mcp_jobs.cli delete --source nonexistent

# Output:
# No jobs match the filter. Nothing to delete.
```

### Invalid Date Format

Dates must be ISO format (YYYY-MM-DD):

```bash
# Wrong format
uv run python -m mcp_jobs.cli delete --before 02/01/2025
# Error: Invalid date format

# Correct format
uv run python -m mcp_jobs.cli delete --before 2025-02-01
```

### User Aborts Confirmation

If you say "no" to confirmation prompt:

```bash
uv run python -m mcp_jobs.cli delete --all

# About to delete 247 job(s) (all jobs)
# Are you sure? [y/N]: n
# Aborted!
```

---

## Implementation Details

### Database Functions

**`count_jobs(**filters)`**
- Counts jobs matching filters
- Used for preview before deletion
- Returns integer count

**`delete_jobs(**filters)`**
- Deletes jobs matching filters
- Uses same filter interface as `count_jobs()`
- Returns count of deleted rows
- Wrapped in transaction (all-or-nothing)

### Filters

All filter parameters are optional and can be combined:

```python
await delete_jobs(
    source="hn",              # Optional: filter by source
    before_date="2025-02-01", # Optional: discovered before this date
    after_date="2025-01-01",  # Optional: discovered after this date
    db_path=None,             # Optional: custom DB path
)
```

### SQL Queries

Filters are combined with `AND`:

```sql
DELETE FROM jobs
WHERE source = ?
  AND discovered_at < ?
  AND discovered_at > ?
```

---

## Testing

### Unit Tests

Run the deletion test suite:

```bash
cd app/mcp/jobs
uv run pytest tests/test_delete.py -v
```

**Test Coverage:**
- `TestCountJobs` (9 tests)
  - Count all jobs
  - Count by source
  - Count by date (before, after, range)
  - Combined filters
  - Edge cases (empty DB, no matches)

- `TestDeleteJobs` (12 tests)
  - Delete all jobs
  - Delete by source
  - Delete by date (before, after, range)
  - Combined filters
  - Verify deletion counts
  - Edge cases

### Manual Testing

Test with real database:

```bash
# Check current state
sqlite3 data/jobs.db "SELECT source, COUNT(*) FROM jobs GROUP BY source"

# Dry run
uv run python -m mcp_jobs.cli delete --source hn --dry-run

# Actually delete
uv run python -m mcp_jobs.cli delete --source hn

# Verify
sqlite3 data/jobs.db "SELECT source, COUNT(*) FROM jobs GROUP BY source"

# Re-scrape to restore data
uv run python -m mcp_jobs.cli scrape --source hn
```

---

## Limitations

1. **No Undo** - Deletions are permanent (unless you have database backups)
2. **No Filter by Title/Company** - Only source and date filters supported
3. **No Cascading Deletes** - Related records (user_actions, events) may become orphaned
4. **Date Filter Uses discovered_at** - Not `posted_at` (which can be null)

---

## Future Enhancements

- [ ] Add `--filter` option for flexible SQL WHERE clauses
- [ ] Support deletion by tier, relevance, or viewed status
- [ ] Add confirmation preview showing sample jobs to be deleted
- [ ] Add `--backup` flag to create DB snapshot before deletion
- [ ] Add audit logging to events table
- [ ] Cascade delete related user_actions and events

---

## Related Documentation

- [Jobs README](../README.md) - Full application documentation
- [CHANGELOG](../CHANGELOG.md) - Feature history
- [Database Schema](../README.md#database-schema) - Table structure

## Files

- **Implementation**: `app/mcp/jobs/mcp_jobs/db.py:130-220`
- **CLI**: `app/mcp/jobs/mcp_jobs/cli.py:77-153`
- **Tests**: `app/mcp/jobs/tests/test_delete.py`
