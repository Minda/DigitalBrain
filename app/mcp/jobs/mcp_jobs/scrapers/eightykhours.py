"""
80,000 Hours job board scraper.

Uses Playwright for browser automation — the job board requires JavaScript rendering.
Reuses the anti-detection and session persistence patterns from
src/python/browser_automation/bluedot_browser.py

NOTE: CSS selectors below are based on 80k's current markup and may need adjustment
      if the site redesigns. Run with headless=False the first time to verify them.
"""

from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright, BrowserContext

from mcp_jobs.db import (
    create_scrape_run,
    complete_scrape_run,
    fail_scrape_run,
    is_too_old,
    upsert_job,
    get_db_path,
)
from mcp_jobs.models import ScrapeResult

JOB_BOARD_URL = "https://80000hours.org/job-board/"
AUTH_FILE = Path(__file__).parent.parent / ".auth" / "eightykhours_state.json"

# CSS selectors — verify against live site with headless=False if results are empty
SELECTORS = {
    "job_card": ".job-listing, [class*='job-card'], article[class*='job']",
    "title": "h2, h3, [class*='title'], [class*='role']",
    "company": "[class*='org'], [class*='company'], [class*='employer']",
    "location": "[class*='location'], [class*='remote']",
    "link": "a[href]",
}

STEALTH_SCRIPT = """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
window.chrome = { runtime: {} };
"""


# ---------------------------------------------------------------------------
# Pure parsing helpers (testable without browser)
# ---------------------------------------------------------------------------

def parse_job_cards(cards_data: list[dict]) -> list[dict]:
    """
    Filter and normalise raw card data extracted by the browser.
    Removes cards missing required fields.
    Returns list of dicts with: url, company, title, location, description.
    """
    jobs = []
    for card in cards_data:
        company = (card.get("company") or "").strip()
        url = (card.get("url") or "").strip()
        description = (card.get("description") or "").strip()

        if not company or not url or not description:
            continue

        jobs.append({
            "url": url,
            "company": company,
            "title": (card.get("title") or "").strip() or None,
            "location": (card.get("location") or "").strip() or None,
            "description": description,
            "posted_at": card.get("posted_at"),
        })
    return jobs


# ---------------------------------------------------------------------------
# Browser helpers
# ---------------------------------------------------------------------------

async def _make_context(playwright, headless: bool) -> BrowserContext:
    browser = await playwright.chromium.launch(
        headless=headless,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-web-security",
            "--disable-features=IsolateOrigins,site-per-process",
        ],
    )
    viewport = {"width": 1920, "height": 1080}
    ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    if AUTH_FILE.exists():
        print(f"Loading 80k session from {AUTH_FILE}")
        context = await browser.new_context(
            storage_state=str(AUTH_FILE), viewport=viewport, user_agent=ua
        )
    else:
        print("No saved 80k session — creating fresh context")
        AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
        context = await browser.new_context(viewport=viewport, user_agent=ua)

    await context.add_init_script(STEALTH_SCRIPT)
    return context


async def fetch_job_board(headless: bool = True) -> list[dict]:
    """
    Open the 80k job board in a browser and extract raw card data.
    Returns list of raw dicts (before parse_job_cards filtering).
    """
    async with async_playwright() as playwright:
        context = await _make_context(playwright, headless=headless)
        page = await context.new_page()

        await page.goto(JOB_BOARD_URL, wait_until="networkidle", timeout=30_000)

        # Save session for next run
        await context.storage_state(path=str(AUTH_FILE))

        cards_data = []
        cards = await page.query_selector_all(SELECTORS["job_card"])

        for card in cards:
            # Title
            title_el = await card.query_selector(SELECTORS["title"])
            title = await title_el.inner_text() if title_el else None

            # Company/org
            company_el = await card.query_selector(SELECTORS["company"])
            company = await company_el.inner_text() if company_el else None

            # Location
            location_el = await card.query_selector(SELECTORS["location"])
            location = await location_el.inner_text() if location_el else None

            # Link — get the card's href or the first link inside it
            link_el = await card.query_selector(SELECTORS["link"])
            href = await link_el.get_attribute("href") if link_el else None
            if href and href.startswith("/"):
                href = f"https://80000hours.org{href}"

            # Description — fetch full text from the detail page if we have a URL
            description = None
            if href:
                try:
                    detail_page = await context.new_page()
                    await detail_page.goto(href, wait_until="networkidle", timeout=20_000)
                    # Main content: try common selectors for job detail text
                    desc_el = await detail_page.query_selector(
                        "main, .job-description, [class*='description'], article"
                    )
                    description = await desc_el.inner_text() if desc_el else await detail_page.inner_text("body")
                    await detail_page.close()
                except Exception as e:
                    print(f"Could not fetch detail page {href}: {e}")

            cards_data.append({
                "url": href,
                "title": title,
                "company": company,
                "location": location,
                "description": description,
                "posted_at": None,  # 80k doesn't expose structured post dates in the listing
            })

        await context.close()
        return cards_data


# ---------------------------------------------------------------------------
# Main scrape function
# ---------------------------------------------------------------------------

async def scrape_80k(headless: bool = True, db_path: Optional[str] = None) -> ScrapeResult:
    """
    Scrape the 80,000 Hours job board and upsert jobs into the DB.
    Uses source='80k', source_id=url (no numeric IDs available).
    """
    path = db_path or get_db_path()
    run_id = await create_scrape_run("80k", db_path=path)

    jobs_found = 0
    jobs_new = 0
    jobs_updated = 0
    jobs_skipped = 0

    try:
        raw_cards = await fetch_job_board(headless=headless)
        jobs_found = len(raw_cards)

        for job in parse_job_cards(raw_cards):
            if is_too_old(job.get("posted_at")):
                jobs_skipped += 1
                continue

            # Use URL as source_id — 80k job URLs are stable
            source_id = job["url"]

            result = await upsert_job(
                url=job["url"],
                company=job["company"],
                description=job["description"],
                source="80k",
                source_id=source_id,
                title=job.get("title"),
                location=job.get("location"),
                posted_at=job.get("posted_at"),
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
        source="80k",
        jobs_found=jobs_found,
        jobs_new=jobs_new,
        jobs_updated=jobs_updated,
        jobs_skipped=jobs_skipped,
        run_id=run_id,
    )
