"""
Integration tests for the HN scraper with mocked HTTP (respx).
TC-S4, TC-S7
"""

from datetime import datetime, timedelta, timezone

import pytest
import respx
import httpx

from mcp_jobs.scrapers.hn import find_latest_hiring_thread, fetch_thread_comments, scrape_hn
from tests.conftest import ALGOLIA_SEARCH_RESPONSE, ALGOLIA_ITEMS_RESPONSE


ALGOLIA_SEARCH_URL = "https://hn.algolia.com/api/v1/search"
ALGOLIA_ITEMS_URL = "https://hn.algolia.com/api/v1/items/39894820"


class TestFindLatestHiringThread:
    @respx.mock
    async def test_finds_hiring_thread(self):
        respx.get(ALGOLIA_SEARCH_URL).mock(return_value=httpx.Response(200, json=ALGOLIA_SEARCH_RESPONSE))
        async with httpx.AsyncClient() as client:
            story_id, title = await find_latest_hiring_thread(client)
        assert story_id == "39894820"
        assert "hiring" in title.lower()

    @respx.mock
    async def test_excludes_wants_to_be_hired(self):
        """TC-S7: 'Who wants to be hired' threads are excluded."""
        response = {"hits": [{"objectID": "99", "title": "Ask HN: Who wants to be hired? (March 2026)"}]}
        respx.get(ALGOLIA_SEARCH_URL).mock(return_value=httpx.Response(200, json=response))
        async with httpx.AsyncClient() as client:
            with pytest.raises(ValueError, match="Could not find"):
                await find_latest_hiring_thread(client)

    @respx.mock
    async def test_excludes_freelancer_threads(self):
        response = {"hits": [{"objectID": "99", "title": "Ask HN: Freelancer? (March 2026)"}]}
        respx.get(ALGOLIA_SEARCH_URL).mock(return_value=httpx.Response(200, json=response))
        async with httpx.AsyncClient() as client:
            with pytest.raises(ValueError, match="Could not find"):
                await find_latest_hiring_thread(client)

    @respx.mock
    async def test_raises_if_no_matching_thread(self):
        respx.get(ALGOLIA_SEARCH_URL).mock(return_value=httpx.Response(200, json={"hits": []}))
        async with httpx.AsyncClient() as client:
            with pytest.raises(ValueError):
                await find_latest_hiring_thread(client)


class TestFetchThreadComments:
    @respx.mock
    async def test_returns_top_level_comments(self):
        respx.get(ALGOLIA_ITEMS_URL).mock(return_value=httpx.Response(200, json=ALGOLIA_ITEMS_RESPONSE))
        async with httpx.AsyncClient() as client:
            comments = await fetch_thread_comments(client, "39894820")
        # Fixture has 3 children: 2 valid comments + 1 deleted
        assert len(comments) == 2

    @respx.mock
    async def test_skips_deleted_comments(self):
        respx.get(ALGOLIA_ITEMS_URL).mock(return_value=httpx.Response(200, json=ALGOLIA_ITEMS_RESPONSE))
        async with httpx.AsyncClient() as client:
            comments = await fetch_thread_comments(client, "39894820")
        ids = [c["id"] for c in comments]
        assert 111003 not in ids  # deleted comment excluded

    @respx.mock
    async def test_skips_null_text_comments(self):
        data = {"id": 1, "children": [{"id": 2, "type": "comment", "text": None}]}
        respx.get(ALGOLIA_ITEMS_URL).mock(return_value=httpx.Response(200, json=data))
        async with httpx.AsyncClient() as client:
            comments = await fetch_thread_comments(client, "39894820")
        assert len(comments) == 0


class TestScrapeHnAgeFilter:
    """TC-S4: Jobs older than 7 days must not be inserted."""

    @respx.mock
    async def test_old_posts_are_skipped(self, temp_db):
        old_timestamp = int((datetime.now(timezone.utc) - timedelta(days=10)).timestamp())
        items_with_old_post = {
            "id": 39894820,
            "title": "Ask HN: Who is hiring? (March 2026)",
            "children": [
                {"id": 999, "type": "comment", "text": "<p>OldCorp | Engineer | Remote</p><p>Old job.</p>", "created_at_i": old_timestamp},
            ],
        }
        respx.get(ALGOLIA_SEARCH_URL).mock(return_value=httpx.Response(200, json=ALGOLIA_SEARCH_RESPONSE))
        respx.get("https://hn.algolia.com/api/v1/items/39894820").mock(
            return_value=httpx.Response(200, json=items_with_old_post)
        )

        result = await scrape_hn(db_path=temp_db)
        assert result.jobs_new == 0
        assert result.jobs_skipped == 1

    @respx.mock
    async def test_recent_posts_are_inserted(self, temp_db):
        recent_timestamp = int((datetime.now(timezone.utc) - timedelta(days=2)).timestamp())
        items_recent = {
            "id": 39894820,
            "title": "Ask HN: Who is hiring? (March 2026)",
            "children": [
                {
                    "id": 888,
                    "type": "comment",
                    "text": "<p>NewCo | ML Engineer | Remote</p><p>Great ML role at NewCo.</p>",
                    "created_at_i": recent_timestamp,
                },
            ],
        }
        respx.get(ALGOLIA_SEARCH_URL).mock(return_value=httpx.Response(200, json=ALGOLIA_SEARCH_RESPONSE))
        respx.get("https://hn.algolia.com/api/v1/items/39894820").mock(
            return_value=httpx.Response(200, json=items_recent)
        )

        result = await scrape_hn(db_path=temp_db)
        assert result.jobs_new == 1
        assert result.jobs_skipped == 0
