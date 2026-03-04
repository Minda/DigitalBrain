"""
Unit tests for DB helpers: dedup, scrape run tracking, age filter.
TC-S1, TC-S2, TC-S3, TC-S4, TC-S6, TC-R1
"""

from datetime import datetime, timedelta, timezone

import aiosqlite
import pytest

from mcp_jobs.db import (
    create_scrape_run,
    complete_scrape_run,
    fail_scrape_run,
    is_too_old,
    upsert_job,
)


# ---------------------------------------------------------------------------
# Age filter (pure function — no DB needed)
# ---------------------------------------------------------------------------

class TestIsTooOld:
    def test_recent_post_is_not_old(self):
        recent = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
        assert is_too_old(recent) is False

    def test_post_exactly_7_days_ago_is_old(self):
        old = (datetime.now(timezone.utc) - timedelta(days=7, hours=1)).isoformat()
        assert is_too_old(old) is True

    def test_post_6_days_ago_is_not_old(self):
        recent = (datetime.now(timezone.utc) - timedelta(days=6)).isoformat()
        assert is_too_old(recent) is False

    def test_none_posted_at_passes_through(self):
        assert is_too_old(None) is False

    def test_invalid_date_string_passes_through(self):
        assert is_too_old("not-a-date") is False

    def test_z_suffix_handled(self):
        recent = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        assert is_too_old(recent) is False

    def test_custom_max_days(self):
        three_days_ago = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
        assert is_too_old(three_days_ago, max_days=2) is True
        assert is_too_old(three_days_ago, max_days=4) is False


# ---------------------------------------------------------------------------
# Scrape run tracking (TC-S6)
# ---------------------------------------------------------------------------

class TestScrapeRunTracking:
    async def test_creates_run_with_status_running(self, temp_db):
        run_id = await create_scrape_run("hn", db_path=temp_db)
        async with aiosqlite.connect(temp_db) as db:
            async with db.execute("SELECT status, source FROM scrape_runs WHERE id = ?", (run_id,)) as cur:
                row = await cur.fetchone()
        assert row is not None
        assert row[0] == "running"
        assert row[1] == "hn"

    async def test_complete_run_updates_status_and_counts(self, temp_db):
        run_id = await create_scrape_run("hn", db_path=temp_db)
        await complete_scrape_run(run_id, jobs_found=10, jobs_new=8, db_path=temp_db)
        async with aiosqlite.connect(temp_db) as db:
            async with db.execute(
                "SELECT status, jobs_found, jobs_new, completed_at FROM scrape_runs WHERE id = ?",
                (run_id,),
            ) as cur:
                row = await cur.fetchone()
        assert row[0] == "completed"
        assert row[1] == 10
        assert row[2] == 8
        assert row[3] is not None  # completed_at was set

    async def test_fail_run_records_error(self, temp_db):
        run_id = await create_scrape_run("hn", db_path=temp_db)
        await fail_scrape_run(run_id, "Network timeout", db_path=temp_db)
        async with aiosqlite.connect(temp_db) as db:
            async with db.execute(
                "SELECT status, error FROM scrape_runs WHERE id = ?", (run_id,)
            ) as cur:
                row = await cur.fetchone()
        assert row[0] == "failed"
        assert "timeout" in row[1].lower()

    async def test_run_record_exists_even_on_crash(self, temp_db):
        """A run record is created before any work begins."""
        run_id = await create_scrape_run("hn", db_path=temp_db)
        # Simulate crash without calling complete or fail
        async with aiosqlite.connect(temp_db) as db:
            async with db.execute("SELECT id FROM scrape_runs WHERE id = ?", (run_id,)) as cur:
                row = await cur.fetchone()
        assert row is not None


# ---------------------------------------------------------------------------
# Deduplication (TC-S1, TC-S2, TC-S3)
# ---------------------------------------------------------------------------

class TestUpsertJob:
    async def _count_jobs(self, db_path: str) -> int:
        async with aiosqlite.connect(db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM jobs") as cur:
                row = await cur.fetchone()
        return row[0]

    async def _get_job(self, db_path: str, source: str, source_id: str) -> tuple:
        async with aiosqlite.connect(db_path) as db:
            async with db.execute(
                "SELECT description, updated_at, company FROM jobs WHERE source = ? AND source_id = ?",
                (source, source_id),
            ) as cur:
                return await cur.fetchone()

    async def test_fresh_insert_adds_row(self, temp_db):
        result = await upsert_job(
            url="https://hn.com/1",
            company="Acme",
            description="Great job",
            source="hn",
            source_id="hn-1",
            db_path=temp_db,
        )
        assert result == "inserted"
        assert await self._count_jobs(temp_db) == 1

    async def test_rescrape_does_not_duplicate(self, temp_db):
        """TC-S2: Re-scraping same source_id must not create a second row."""
        for _ in range(3):
            await upsert_job(
                url="https://hn.com/1",
                company="Acme",
                description="Great job",
                source="hn",
                source_id="hn-1",
                db_path=temp_db,
            )
        assert await self._count_jobs(temp_db) == 1

    async def test_existing_job_updates_description(self, temp_db):
        """TC-S3: On re-scrape, description and updated_at are refreshed."""
        await upsert_job(
            url="https://hn.com/1",
            company="Acme",
            description="Original description",
            source="hn",
            source_id="hn-1",
            db_path=temp_db,
        )
        result = await upsert_job(
            url="https://hn.com/1",
            company="Acme",
            description="Updated description",
            source="hn",
            source_id="hn-1",
            db_path=temp_db,
        )
        assert result == "updated"
        row = await self._get_job(temp_db, "hn", "hn-1")
        assert row[0] == "Updated description"

    async def test_different_source_ids_are_separate_rows(self, temp_db):
        await upsert_job(url="https://hn.com/1", company="A", description="d1", source="hn", source_id="1", db_path=temp_db)
        await upsert_job(url="https://hn.com/2", company="B", description="d2", source="hn", source_id="2", db_path=temp_db)
        assert await self._count_jobs(temp_db) == 2

    async def test_same_source_id_different_source_are_separate(self, temp_db):
        """Jobs from different sources don't collide even with same source_id."""
        await upsert_job(url="https://hn.com/1", company="A", description="d1", source="hn", source_id="abc", db_path=temp_db)
        await upsert_job(url="https://80k.com/1", company="B", description="d2", source="80k", source_id="abc", db_path=temp_db)
        assert await self._count_jobs(temp_db) == 2


# ---------------------------------------------------------------------------
# Relevance scale validation (TC-R1)
# ---------------------------------------------------------------------------

class TestRelevanceScale:
    async def test_relevance_defaults_to_zero(self, temp_db):
        """Newly inserted jobs are unclassified (relevance = 0)."""
        await upsert_job(
            url="https://hn.com/1",
            company="Acme",
            description="Job desc",
            source="hn",
            source_id="hn-1",
            db_path=temp_db,
        )
        async with aiosqlite.connect(temp_db) as db:
            async with db.execute("SELECT relevance FROM jobs WHERE source_id = 'hn-1'") as cur:
                row = await cur.fetchone()
        assert row[0] == 0

    async def test_valid_relevance_values_accepted(self, temp_db):
        """The DB accepts relevance values 0–3."""
        await upsert_job(url="https://hn.com/1", company="A", description="d", source="hn", source_id="r1", db_path=temp_db)
        async with aiosqlite.connect(temp_db) as db:
            for val in [0, 1, 2, 3]:
                await db.execute("UPDATE jobs SET relevance = ? WHERE source_id = 'r1'", (val,))
                await db.commit()
                async with db.execute("SELECT relevance FROM jobs WHERE source_id = 'r1'") as cur:
                    row = await cur.fetchone()
                assert row[0] == val
