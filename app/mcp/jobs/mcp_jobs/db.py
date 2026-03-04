"""
SQLite access layer for the jobs database.

The jobs.db file is shared with the Node.js app (Drizzle ORM).
This module reads/writes to the same schema using raw SQL via aiosqlite.

Database location: DigitalBrain/data/jobs.db
Override with env var: JOBS_DB_PATH
"""

import os
import aiosqlite
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

# 5 parents up from mcp_jobs/db.py → DigitalBrain/
_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
DEFAULT_DB_PATH = _PROJECT_ROOT / "data" / "jobs.db"


def get_db_path() -> str:
    return os.environ.get("JOBS_DB_PATH", str(DEFAULT_DB_PATH))


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def is_too_old(posted_at: Optional[str], max_days: int = 7) -> bool:
    """Return True if posted_at is more than max_days old. Unknown dates pass through."""
    if not posted_at:
        return False
    try:
        dt = datetime.fromisoformat(posted_at.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        cutoff = datetime.now(timezone.utc) - timedelta(days=max_days)
        return dt < cutoff
    except (ValueError, TypeError):
        return False


async def create_scrape_run(source: str, db_path: Optional[str] = None) -> int:
    """Insert a scrape_runs record with status=running. Returns run ID."""
    path = db_path or get_db_path()
    async with aiosqlite.connect(path) as db:
        cursor = await db.execute(
            "INSERT INTO scrape_runs (source, started_at, status) VALUES (?, ?, 'running')",
            (source, now_iso()),
        )
        await db.commit()
        return cursor.lastrowid


async def complete_scrape_run(
    run_id: int,
    jobs_found: int,
    jobs_new: int,
    db_path: Optional[str] = None,
) -> None:
    """Mark a scrape_runs record as completed with counts."""
    path = db_path or get_db_path()
    async with aiosqlite.connect(path) as db:
        await db.execute(
            """UPDATE scrape_runs
               SET status = 'completed', completed_at = ?, jobs_found = ?, jobs_new = ?
               WHERE id = ?""",
            (now_iso(), jobs_found, jobs_new, run_id),
        )
        await db.commit()


async def fail_scrape_run(run_id: int, error: str, db_path: Optional[str] = None) -> None:
    """Mark a scrape_runs record as failed."""
    path = db_path or get_db_path()
    async with aiosqlite.connect(path) as db:
        await db.execute(
            "UPDATE scrape_runs SET status = 'failed', completed_at = ?, error = ? WHERE id = ?",
            (now_iso(), error, run_id),
        )
        await db.commit()


async def upsert_job(
    *,
    url: str,
    company: str,
    description: str,
    source: str,
    source_id: str,
    title: Optional[str] = None,
    location: Optional[str] = None,
    posted_at: Optional[str] = None,
    db_path: Optional[str] = None,
) -> str:
    """
    Insert a new job or update an existing one (dedup by source + source_id).
    Returns 'inserted' or 'updated'.
    """
    path = db_path or get_db_path()
    ts = now_iso()
    async with aiosqlite.connect(path) as db:
        async with db.execute(
            "SELECT id FROM jobs WHERE source = ? AND source_id = ?",
            (source, source_id),
        ) as cursor:
            existing = await cursor.fetchone()

        if existing:
            await db.execute(
                "UPDATE jobs SET description = ?, updated_at = ? WHERE source = ? AND source_id = ?",
                (description, ts, source, source_id),
            )
            await db.commit()
            return "updated"
        else:
            await db.execute(
                """INSERT INTO jobs
                   (url, title, company, location, description, source, source_id,
                    posted_at, discovered_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (url, title, company, location, description, source, source_id,
                 posted_at, ts, ts),
            )
            await db.commit()
            return "inserted"


async def count_jobs(
    *,
    source: Optional[str] = None,
    before_date: Optional[str] = None,
    after_date: Optional[str] = None,
    db_path: Optional[str] = None,
) -> int:
    """
    Count jobs matching the given filters.

    Args:
        source: Filter by source ('hn', '80k', etc.)
        before_date: Count jobs discovered before this date (ISO format)
        after_date: Count jobs discovered after this date (ISO format)
        db_path: Database path (optional)

    Returns:
        Number of jobs matching filters
    """
    path = db_path or get_db_path()

    conditions = []
    params = []

    if source:
        conditions.append("source = ?")
        params.append(source)

    if before_date:
        conditions.append("discovered_at < ?")
        params.append(before_date)

    if after_date:
        conditions.append("discovered_at > ?")
        params.append(after_date)

    query = "SELECT COUNT(*) FROM jobs"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    async with aiosqlite.connect(path) as db:
        async with db.execute(query, params) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0


async def delete_jobs(
    *,
    source: Optional[str] = None,
    before_date: Optional[str] = None,
    after_date: Optional[str] = None,
    db_path: Optional[str] = None,
) -> int:
    """
    Delete jobs matching the given filters.

    Args:
        source: Filter by source ('hn', '80k', etc.)
        before_date: Delete jobs discovered before this date (ISO format)
        after_date: Delete jobs discovered after this date (ISO format)
        db_path: Database path (optional)

    Returns:
        Number of jobs deleted
    """
    path = db_path or get_db_path()

    conditions = []
    params = []

    if source:
        conditions.append("source = ?")
        params.append(source)

    if before_date:
        conditions.append("discovered_at < ?")
        params.append(before_date)

    if after_date:
        conditions.append("discovered_at > ?")
        params.append(after_date)

    query = "DELETE FROM jobs"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    async with aiosqlite.connect(path) as db:
        cursor = await db.execute(query, params)
        await db.commit()
        return cursor.rowcount
