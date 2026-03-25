"""
Direct URL scraper - add jobs from specific URLs.

This scraper fetches a job posting from a direct URL and adds it to the database.
"""

import hashlib
import sys
from typing import Optional
from playwright.async_api import async_playwright
from mcp_jobs.models import ScrapeResult
from mcp_jobs.db import create_scrape_run, complete_scrape_run, fail_scrape_run, upsert_job


async def scrape_direct_url(
    url: str,
    *,
    company: Optional[str] = None,
    title: Optional[str] = None,
    location: Optional[str] = None,
    headless: bool = True,
) -> ScrapeResult:
    """
    Scrape a job posting from a direct URL.

    Args:
        url: The job posting URL
        company: Company name (optional, will try to extract if not provided)
        title: Job title (optional, will try to extract if not provided)
        location: Location (optional, will try to extract if not provided)
        headless: Run browser in headless mode

    Returns:
        ScrapeResult with job details
    """
    run_id = await create_scrape_run("direct")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=headless)
            page = await browser.new_page()

            # Set a realistic user agent
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })

            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(3000)
            except Exception as e:
                # Try without waiting for network idle
                if "Timeout" in str(e):
                    await page.goto(url, timeout=60000)
                    await page.wait_for_timeout(5000)
                else:
                    raise

            # Try to extract text content
            body = await page.locator("body").text_content()
            description = (body or "").strip()

            if not description:
                raise ValueError("Could not extract job description from page")

            # Extract company from URL or meta tags if not provided
            if not company:
                # Try og:site_name or company meta tag
                company = await page.locator('meta[property="og:site_name"]').get_attribute("content") or None
                if not company:
                    # Try to extract from domain
                    from urllib.parse import urlparse
                    domain = urlparse(url).netloc
                    company = domain.replace("www.", "").split(".")[0].title()

            # Extract title from page title or h1 if not provided
            if not title:
                title = await page.locator('meta[property="og:title"]').get_attribute("content") or None
                if not title:
                    title = await page.title()
                if not title:
                    h1 = await page.locator("h1").first.text_content()
                    title = h1.strip() if h1 else None

            await browser.close()

        # Generate a unique source_id from the URL
        source_id = hashlib.md5(url.encode()).hexdigest()[:16]

        # Upsert the job
        action = await upsert_job(
            url=url,
            company=company or "Unknown Company",
            title=title,
            location=location,
            description=description,
            source="direct",
            source_id=source_id,
        )

        jobs_new = 1 if action == "inserted" else 0
        jobs_updated = 1 if action == "updated" else 0

        await complete_scrape_run(run_id, jobs_found=1, jobs_new=jobs_new)

        return ScrapeResult(
            source="direct",
            run_id=run_id,
            jobs_found=1,
            jobs_new=jobs_new,
            jobs_updated=jobs_updated,
            jobs_skipped=0,
            thread_title=title,
        )

    except Exception as e:
        await fail_scrape_run(run_id, str(e))
        raise


async def scrape_direct_urls(
    urls: list[str],
    *,
    headless: bool = True,
) -> ScrapeResult:
    """
    Scrape multiple job postings from direct URLs.

    Args:
        urls: List of job posting URLs
        headless: Run browser in headless mode

    Returns:
        Combined ScrapeResult for all URLs
    """
    run_id = await create_scrape_run("direct")

    total_found = 0
    total_new = 0
    total_updated = 0
    total_skipped = 0

    for url in urls:
        try:
            result = await scrape_direct_url(url, headless=headless)
            total_found += result.jobs_found
            total_new += result.jobs_new
            total_updated += result.jobs_updated
            total_skipped += result.jobs_skipped
        except Exception as e:
            sys.stderr.write(f"Failed to scrape {url}: {e}\n")
            total_skipped += 1
            continue

    await complete_scrape_run(run_id, jobs_found=total_found, jobs_new=total_new)

    return ScrapeResult(
        source="direct",
        run_id=run_id,
        jobs_found=total_found,
        jobs_new=total_new,
        jobs_updated=total_updated,
        jobs_skipped=total_skipped,
    )
