"""
Unit tests for 80k Hours parsing helpers.
These test parse_job_cards() with fixture data — no browser required.
TC-S9
"""

from tests.conftest import EIGHTYKHOURS_CARDS_RAW
from mcp_jobs.scrapers.eightykhours import parse_job_cards


class TestParseJobCards:
    def test_valid_cards_are_returned(self):
        jobs = parse_job_cards(EIGHTYKHOURS_CARDS_RAW)
        companies = [j["company"] for j in jobs]
        assert "Anthropic" in companies
        assert "Google DeepMind" in companies

    def test_missing_company_is_filtered(self):
        """TC-S5: Cards without a company are skipped."""
        jobs = parse_job_cards(EIGHTYKHOURS_CARDS_RAW)
        companies = [j["company"] for j in jobs]
        assert "" not in companies

    def test_missing_url_is_filtered(self):
        cards = [{"url": "", "company": "Acme", "description": "Good job", "title": "Eng", "location": "Remote", "posted_at": None}]
        jobs = parse_job_cards(cards)
        assert len(jobs) == 0

    def test_missing_description_is_filtered(self):
        cards = [{"url": "https://80k.org/job/1", "company": "Acme", "description": "", "title": "Eng", "location": "Remote", "posted_at": None}]
        jobs = parse_job_cards(cards)
        assert len(jobs) == 0

    def test_optional_fields_allowed_to_be_none(self):
        cards = [{
            "url": "https://80k.org/job/1",
            "company": "Acme",
            "description": "A great job.",
            "title": None,
            "location": None,
            "posted_at": None,
        }]
        jobs = parse_job_cards(cards)
        assert len(jobs) == 1
        assert jobs[0]["title"] is None
        assert jobs[0]["location"] is None

    def test_whitespace_stripped_from_fields(self):
        cards = [{
            "url": "  https://80k.org/job/1  ",
            "company": "  Acme  ",
            "description": "  Good job.  ",
            "title": "  Engineer  ",
            "location": "  Remote  ",
            "posted_at": None,
        }]
        jobs = parse_job_cards(cards)
        assert jobs[0]["company"] == "Acme"
        assert jobs[0]["title"] == "Engineer"
        assert jobs[0]["url"] == "https://80k.org/job/1"

    def test_count_of_valid_cards(self):
        """Fixture has 3 cards, 1 with missing company — expect 2."""
        jobs = parse_job_cards(EIGHTYKHOURS_CARDS_RAW)
        assert len(jobs) == 2


class TestEightyKHoursScrapeIntegration:
    """
    Full browser integration tests — marked as integration, skipped by default.
    Run with: uv run pytest -m integration
    """

    import pytest

    @pytest.mark.integration
    async def test_live_scrape_returns_jobs(self):
        from mcp_jobs.scrapers.eightykhours import scrape_80k
        result = await scrape_80k(headless=True)
        assert result.jobs_found > 0
        assert result.source == "80k"
