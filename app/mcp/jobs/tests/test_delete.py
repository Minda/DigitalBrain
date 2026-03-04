"""
Unit tests for job deletion features.
Tests count_jobs() and delete_jobs() with various filter combinations.
"""

from datetime import datetime, timedelta, timezone

import aiosqlite
import pytest

from mcp_jobs.db import count_jobs, delete_jobs, upsert_job


class TestCountJobs:
    """Test count_jobs() with various filters."""

    async def test_count_all_jobs(self, temp_db):
        """Count all jobs in database."""
        await upsert_job(url="https://hn.com/1", company="A", description="d1", source="hn", source_id="1", db_path=temp_db)
        await upsert_job(url="https://hn.com/2", company="B", description="d2", source="hn", source_id="2", db_path=temp_db)
        await upsert_job(url="https://80k.com/1", company="C", description="d3", source="80k", source_id="3", db_path=temp_db)

        count = await count_jobs(db_path=temp_db)
        assert count == 3

    async def test_count_by_source(self, temp_db):
        """Count jobs from specific source."""
        await upsert_job(url="https://hn.com/1", company="A", description="d1", source="hn", source_id="1", db_path=temp_db)
        await upsert_job(url="https://hn.com/2", company="B", description="d2", source="hn", source_id="2", db_path=temp_db)
        await upsert_job(url="https://80k.com/1", company="C", description="d3", source="80k", source_id="3", db_path=temp_db)

        hn_count = await count_jobs(source="hn", db_path=temp_db)
        assert hn_count == 2

        eighty_k_count = await count_jobs(source="80k", db_path=temp_db)
        assert eighty_k_count == 1

    async def test_count_before_date(self, temp_db):
        """Count jobs discovered before a specific date."""
        old_date = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
        recent_date = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()

        # Insert jobs with different discovered_at dates
        async with aiosqlite.connect(temp_db) as db:
            await db.execute(
                """INSERT INTO jobs (url, company, description, source, source_id, discovered_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("https://hn.com/1", "A", "d1", "hn", "1", old_date, old_date),
            )
            await db.execute(
                """INSERT INTO jobs (url, company, description, source, source_id, discovered_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("https://hn.com/2", "B", "d2", "hn", "2", recent_date, recent_date),
            )
            await db.commit()

        # Count jobs before 5 days ago (should get the old one)
        cutoff = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
        count = await count_jobs(before_date=cutoff, db_path=temp_db)
        assert count == 1

    async def test_count_after_date(self, temp_db):
        """Count jobs discovered after a specific date."""
        old_date = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
        recent_date = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()

        async with aiosqlite.connect(temp_db) as db:
            await db.execute(
                """INSERT INTO jobs (url, company, description, source, source_id, discovered_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("https://hn.com/1", "A", "d1", "hn", "1", old_date, old_date),
            )
            await db.execute(
                """INSERT INTO jobs (url, company, description, source, source_id, discovered_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("https://hn.com/2", "B", "d2", "hn", "2", recent_date, recent_date),
            )
            await db.commit()

        # Count jobs after 5 days ago (should get the recent one)
        cutoff = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
        count = await count_jobs(after_date=cutoff, db_path=temp_db)
        assert count == 1

    async def test_count_date_range(self, temp_db):
        """Count jobs in a date range."""
        very_old = (datetime.now(timezone.utc) - timedelta(days=20)).isoformat()
        old = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
        recent = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()

        async with aiosqlite.connect(temp_db) as db:
            await db.execute(
                """INSERT INTO jobs (url, company, description, source, source_id, discovered_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("https://hn.com/1", "A", "d1", "hn", "1", very_old, very_old),
            )
            await db.execute(
                """INSERT INTO jobs (url, company, description, source, source_id, discovered_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("https://hn.com/2", "B", "d2", "hn", "2", old, old),
            )
            await db.execute(
                """INSERT INTO jobs (url, company, description, source, source_id, discovered_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("https://hn.com/3", "C", "d3", "hn", "3", recent, recent),
            )
            await db.commit()

        # Count jobs between 15 and 5 days ago (should get the 10-day old one)
        after = (datetime.now(timezone.utc) - timedelta(days=15)).isoformat()
        before = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
        count = await count_jobs(after_date=after, before_date=before, db_path=temp_db)
        assert count == 1

    async def test_count_combined_filters(self, temp_db):
        """Count jobs with source + date filters."""
        old_date = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
        recent_date = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()

        async with aiosqlite.connect(temp_db) as db:
            await db.execute(
                """INSERT INTO jobs (url, company, description, source, source_id, discovered_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("https://hn.com/1", "A", "d1", "hn", "1", old_date, old_date),
            )
            await db.execute(
                """INSERT INTO jobs (url, company, description, source, source_id, discovered_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("https://hn.com/2", "B", "d2", "hn", "2", recent_date, recent_date),
            )
            await db.execute(
                """INSERT INTO jobs (url, company, description, source, source_id, discovered_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("https://80k.com/1", "C", "d3", "80k", "3", old_date, old_date),
            )
            await db.commit()

        # Count old HN jobs (should be 1)
        cutoff = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
        count = await count_jobs(source="hn", before_date=cutoff, db_path=temp_db)
        assert count == 1

    async def test_count_empty_database(self, temp_db):
        """Count jobs in empty database returns 0."""
        count = await count_jobs(db_path=temp_db)
        assert count == 0

    async def test_count_no_matches(self, temp_db):
        """Count jobs with no matches returns 0."""
        await upsert_job(url="https://hn.com/1", company="A", description="d1", source="hn", source_id="1", db_path=temp_db)

        count = await count_jobs(source="80k", db_path=temp_db)
        assert count == 0


class TestDeleteJobs:
    """Test delete_jobs() with various filters."""

    async def _count_all(self, db_path: str) -> int:
        async with aiosqlite.connect(db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM jobs") as cur:
                row = await cur.fetchone()
        return row[0]

    async def test_delete_all_jobs(self, temp_db):
        """Delete all jobs from database."""
        await upsert_job(url="https://hn.com/1", company="A", description="d1", source="hn", source_id="1", db_path=temp_db)
        await upsert_job(url="https://hn.com/2", company="B", description="d2", source="hn", source_id="2", db_path=temp_db)
        await upsert_job(url="https://80k.com/1", company="C", description="d3", source="80k", source_id="3", db_path=temp_db)

        deleted = await delete_jobs(db_path=temp_db)
        assert deleted == 3
        assert await self._count_all(temp_db) == 0

    async def test_delete_by_source(self, temp_db):
        """Delete jobs from specific source."""
        await upsert_job(url="https://hn.com/1", company="A", description="d1", source="hn", source_id="1", db_path=temp_db)
        await upsert_job(url="https://hn.com/2", company="B", description="d2", source="hn", source_id="2", db_path=temp_db)
        await upsert_job(url="https://80k.com/1", company="C", description="d3", source="80k", source_id="3", db_path=temp_db)

        deleted = await delete_jobs(source="hn", db_path=temp_db)
        assert deleted == 2
        assert await self._count_all(temp_db) == 1

        # Verify the remaining job is from 80k
        remaining_count = await count_jobs(source="80k", db_path=temp_db)
        assert remaining_count == 1

    async def test_delete_before_date(self, temp_db):
        """Delete jobs discovered before a specific date."""
        old_date = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
        recent_date = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()

        async with aiosqlite.connect(temp_db) as db:
            await db.execute(
                """INSERT INTO jobs (url, company, description, source, source_id, discovered_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("https://hn.com/1", "A", "d1", "hn", "1", old_date, old_date),
            )
            await db.execute(
                """INSERT INTO jobs (url, company, description, source, source_id, discovered_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("https://hn.com/2", "B", "d2", "hn", "2", recent_date, recent_date),
            )
            await db.commit()

        cutoff = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
        deleted = await delete_jobs(before_date=cutoff, db_path=temp_db)
        assert deleted == 1
        assert await self._count_all(temp_db) == 1

    async def test_delete_after_date(self, temp_db):
        """Delete jobs discovered after a specific date."""
        old_date = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
        recent_date = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()

        async with aiosqlite.connect(temp_db) as db:
            await db.execute(
                """INSERT INTO jobs (url, company, description, source, source_id, discovered_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("https://hn.com/1", "A", "d1", "hn", "1", old_date, old_date),
            )
            await db.execute(
                """INSERT INTO jobs (url, company, description, source, source_id, discovered_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("https://hn.com/2", "B", "d2", "hn", "2", recent_date, recent_date),
            )
            await db.commit()

        cutoff = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
        deleted = await delete_jobs(after_date=cutoff, db_path=temp_db)
        assert deleted == 1
        assert await self._count_all(temp_db) == 1

    async def test_delete_date_range(self, temp_db):
        """Delete jobs in a date range."""
        very_old = (datetime.now(timezone.utc) - timedelta(days=20)).isoformat()
        old = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
        recent = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()

        async with aiosqlite.connect(temp_db) as db:
            await db.execute(
                """INSERT INTO jobs (url, company, description, source, source_id, discovered_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("https://hn.com/1", "A", "d1", "hn", "1", very_old, very_old),
            )
            await db.execute(
                """INSERT INTO jobs (url, company, description, source, source_id, discovered_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("https://hn.com/2", "B", "d2", "hn", "2", old, old),
            )
            await db.execute(
                """INSERT INTO jobs (url, company, description, source, source_id, discovered_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("https://hn.com/3", "C", "d3", "hn", "3", recent, recent),
            )
            await db.commit()

        # Delete jobs between 15 and 5 days ago
        after = (datetime.now(timezone.utc) - timedelta(days=15)).isoformat()
        before = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
        deleted = await delete_jobs(after_date=after, before_date=before, db_path=temp_db)
        assert deleted == 1
        assert await self._count_all(temp_db) == 2

    async def test_delete_combined_filters(self, temp_db):
        """Delete jobs with source + date filters."""
        old_date = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
        recent_date = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()

        async with aiosqlite.connect(temp_db) as db:
            await db.execute(
                """INSERT INTO jobs (url, company, description, source, source_id, discovered_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("https://hn.com/1", "A", "d1", "hn", "1", old_date, old_date),
            )
            await db.execute(
                """INSERT INTO jobs (url, company, description, source, source_id, discovered_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("https://hn.com/2", "B", "d2", "hn", "2", recent_date, recent_date),
            )
            await db.execute(
                """INSERT INTO jobs (url, company, description, source, source_id, discovered_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("https://80k.com/1", "C", "d3", "80k", "3", old_date, old_date),
            )
            await db.commit()

        # Delete old HN jobs only
        cutoff = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
        deleted = await delete_jobs(source="hn", before_date=cutoff, db_path=temp_db)
        assert deleted == 1
        assert await self._count_all(temp_db) == 2

        # Verify recent HN job and old 80k job remain
        hn_count = await count_jobs(source="hn", db_path=temp_db)
        assert hn_count == 1
        eighty_k_count = await count_jobs(source="80k", db_path=temp_db)
        assert eighty_k_count == 1

    async def test_delete_empty_database(self, temp_db):
        """Delete from empty database returns 0."""
        deleted = await delete_jobs(db_path=temp_db)
        assert deleted == 0

    async def test_delete_no_matches(self, temp_db):
        """Delete with no matches returns 0."""
        await upsert_job(url="https://hn.com/1", company="A", description="d1", source="hn", source_id="1", db_path=temp_db)

        deleted = await delete_jobs(source="80k", db_path=temp_db)
        assert deleted == 0
        assert await self._count_all(temp_db) == 1

    async def test_delete_returns_correct_count(self, temp_db):
        """Verify delete_jobs returns accurate deletion count."""
        await upsert_job(url="https://hn.com/1", company="A", description="d1", source="hn", source_id="1", db_path=temp_db)
        await upsert_job(url="https://hn.com/2", company="B", description="d2", source="hn", source_id="2", db_path=temp_db)
        await upsert_job(url="https://hn.com/3", company="C", description="d3", source="hn", source_id="3", db_path=temp_db)

        count_before = await count_jobs(db_path=temp_db)
        deleted = await delete_jobs(db_path=temp_db)
        count_after = await count_jobs(db_path=temp_db)

        assert count_before == 3
        assert deleted == 3
        assert count_after == 0
