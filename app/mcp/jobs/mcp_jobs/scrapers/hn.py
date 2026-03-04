"""
Hacker News "Who is Hiring" scraper.

Uses the Algolia HN API — no browser automation required.
Port of app/web/src/modules/jobs/scrapers/hn.ts
"""

import re
import html as html_lib
from datetime import datetime, timezone
from typing import Optional

import httpx

from mcp_jobs.db import (
    create_scrape_run,
    complete_scrape_run,
    fail_scrape_run,
    is_too_old,
    upsert_job,
    get_db_path,
)
from mcp_jobs.models import ScrapeResult

ALGOLIA_SEARCH = "https://hn.algolia.com/api/v1/search"
ALGOLIA_ITEMS = "https://hn.algolia.com/api/v1/items"

LOCATION_KEYWORDS = {
    "remote", "onsite", "on-site", "hybrid",
    "new york", "san francisco", "sf", "seattle", "boston",
    "austin", "chicago", "los angeles", "la", "denver",
    "atlanta", "miami", "portland", "washington", "dc",
    "toronto", "london", "berlin", "amsterdam", "paris",
    "singapore", "sydney", "tokyo", "montreal", "vancouver",
}

US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC",
}


# ---------------------------------------------------------------------------
# Parsing helpers (pure functions — easily unit-tested)
# ---------------------------------------------------------------------------

def strip_html(raw: str) -> str:
    """Convert HTML job posting to clean plain text."""
    text = re.sub(r"<p\s*/?>", "\n\n", raw, flags=re.IGNORECASE)
    text = re.sub(r"</p>", "\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)

    def replace_link(m: re.Match) -> str:
        href = m.group(1)
        link_text = re.sub(r"<[^>]+>", "", m.group(2)).strip()
        if not link_text or link_text == href:
            return href
        return f"{link_text} ({href})"

    text = re.sub(
        r'<a\s+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
        replace_link,
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    text = re.sub(r"<[^>]+>", "", text)
    text = html_lib.unescape(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_company(text: str) -> str:
    """Extract company from first pipe-separated segment of first line."""
    first_line = text.split("\n")[0]
    segments = [s.strip() for s in first_line.split("|")]
    return segments[0] if segments[0] else "Unknown"


def parse_title(text: str) -> Optional[str]:
    """Extract job title from second pipe-separated segment of first line."""
    first_line = text.split("\n")[0]
    segments = [s.strip() for s in first_line.split("|")]
    return segments[1] if len(segments) > 1 and segments[1] else None


def parse_location(text: str) -> Optional[str]:
    """
    Scan pipe-separated segments for location indicators.
    Returns the full segment text (e.g. 'Remote (US/EU timezones)').
    """
    first_line = text.split("\n")[0]
    segments = [s.strip() for s in first_line.split("|")]

    for segment in segments[1:]:  # skip company name
        lower = segment.lower()
        if any(re.search(r"\b" + re.escape(kw) + r"\b", lower) for kw in LOCATION_KEYWORDS):
            return segment
        # Check for standalone US state abbreviations
        words = re.findall(r"\b([A-Z]{2})\b", segment)
        if any(w in US_STATES for w in words):
            return segment

    return None


def _parse_hn_timestamp(created_at: Optional[int]) -> Optional[str]:
    """Convert HN Unix timestamp to ISO string."""
    if not created_at:
        return None
    return datetime.fromtimestamp(created_at, tz=timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# API calls
# ---------------------------------------------------------------------------

async def find_latest_hiring_thread(client: httpx.AsyncClient) -> tuple[str, str]:
    """
    Find the current 'Ask HN: Who is hiring?' thread via Algolia.
    Returns (story_id, thread_title).
    Raises ValueError if no suitable thread is found.
    """
    resp = await client.get(
        ALGOLIA_SEARCH,
        params={"query": "Ask HN: Who is hiring", "tags": "story", "hitsPerPage": "5"},
    )
    resp.raise_for_status()
    data = resp.json()

    for hit in data.get("hits", []):
        title: str = hit.get("title", "")
        lower = title.lower()
        if (
            "who is hiring" in lower
            and "who wants to be hired" not in lower
            and "freelancer" not in lower
        ):
            return hit["objectID"], title

    raise ValueError("Could not find a current 'Who is hiring' thread on HN")


async def fetch_thread_comments(client: httpx.AsyncClient, story_id: str) -> list[dict]:
    """Fetch top-level job-posting comments from an HN thread."""
    resp = await client.get(f"{ALGOLIA_ITEMS}/{story_id}", timeout=30.0)
    resp.raise_for_status()
    data = resp.json()

    comments = []
    for child in data.get("children", []):
        if (
            child.get("type") == "comment"
            and child.get("text")
            and not child.get("deleted")
        ):
            comments.append(child)
    return comments


# ---------------------------------------------------------------------------
# Main scrape function
# ---------------------------------------------------------------------------

async def scrape_hn(db_path: Optional[str] = None) -> ScrapeResult:
    """
    Scrape the latest HN 'Who is Hiring' thread and upsert jobs into the DB.
    Skips postings older than 7 days.
    """
    path = db_path or get_db_path()
    run_id = await create_scrape_run("hn", db_path=path)

    jobs_found = 0
    jobs_new = 0
    jobs_updated = 0
    jobs_skipped = 0
    thread_title = None

    try:
        async with httpx.AsyncClient() as client:
            story_id, thread_title = await find_latest_hiring_thread(client)
            comments = await fetch_thread_comments(client, story_id)

        for comment in comments:
            jobs_found += 1
            raw_html = comment.get("text", "")
            source_id = str(comment.get("id", ""))
            posted_at = _parse_hn_timestamp(comment.get("created_at_i"))

            # Skip postings older than 7 days
            if is_too_old(posted_at):
                jobs_skipped += 1
                continue

            text = strip_html(raw_html)
            company = parse_company(text)
            title = parse_title(text)
            location = parse_location(text)

            # Require non-empty company and description
            if not company or not text:
                jobs_skipped += 1
                continue

            # Build URL: link to the HN comment
            url = f"https://news.ycombinator.com/item?id={source_id}"

            result = await upsert_job(
                url=url,
                company=company,
                description=text,
                source="hn",
                source_id=source_id,
                title=title,
                location=location,
                posted_at=posted_at,
                db_path=path,
            )

            if result == "inserted":
                jobs_new += 1
            else:
                jobs_updated += 1

        await complete_scrape_run(run_id, jobs_found=jobs_found, jobs_new=jobs_new, db_path=path)

    except Exception as e:
        await fail_scrape_run(run_id, str(e), db_path=path)
        raise

    return ScrapeResult(
        source="hn",
        thread_title=thread_title,
        jobs_found=jobs_found,
        jobs_new=jobs_new,
        jobs_updated=jobs_updated,
        jobs_skipped=jobs_skipped,
        run_id=run_id,
    )
