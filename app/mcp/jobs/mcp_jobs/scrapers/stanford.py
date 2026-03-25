"""
Stanford University job scraper.

Uses Playwright to scrape job listings from Stanford careers site.
"""

import hashlib
from typing import Optional
from playwright.async_api import async_playwright

from mcp_jobs.db import (
    create_scrape_run,
    complete_scrape_run,
    fail_scrape_run,
    upsert_job,
    get_db_path,
)
from mcp_jobs.models import ScrapeResult


async def scrape_stanford(
    search_term: str = "software",
    max_jobs: int = 50,
    db_path: Optional[str] = None,
) -> ScrapeResult:
    """
    Scrape Stanford University job listings.

    Args:
        search_term: Search keyword (default: "software")
        max_jobs: Maximum number of jobs to scrape
        db_path: Database path

    Returns:
        ScrapeResult with job counts
    """
    path = db_path or get_db_path()
    run_id = await create_scrape_run("stanford", db_path=path)

    jobs_found = 0
    jobs_new = 0
    jobs_updated = 0
    jobs_skipped = 0

    try:
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Set realistic user agent
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })

            # Navigate to Stanford careers search
            url = f"https://careersearch.stanford.edu/jobs?q={search_term}"
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)

            # Wait for the page to load - Stanford uses server-side rendering
            try:
                # Wait for the main content area
                await page.wait_for_selector('#content, #job_list, #portal_content', timeout=10000)
            except:
                # If no main container, just wait a bit more
                await page.wait_for_timeout(2000)

            # Stanford uses pagination, so we need to handle multiple pages
            page_num = 1
            max_pages = 5  # Limit pages to avoid too many requests

            while page_num <= max_pages and jobs_found < max_jobs:
                # Extract job listings from current page
                # Stanford uses table rows or list items for jobs
                job_cards = await page.query_selector_all('tr.job-listing, tbody tr[class*="job"]')
                if not job_cards:
                    job_cards = await page.query_selector_all('li.job-listing, ul li[class*="job"]')
                if not job_cards:
                    # Try finding links that go to job detail pages
                    job_cards = await page.query_selector_all('a[href*="/jobs/"][href*="?job="]')
                if not job_cards:
                    # Try table rows in the main content area
                    job_cards = await page.query_selector_all('#content table tr, #job_list table tr')
                if not job_cards:
                    # Last resort - any links in the content area
                    job_cards = await page.query_selector_all('#content a[href*="job"], #portal_content a[href*="job"]')

                for card in job_cards[:max_jobs - jobs_found]:
                    try:
                        jobs_found += 1

                        # Extract text content from the card/row
                        card_text = await card.text_content() if card else ""

                        # Extract job title - might be in link text or td cell
                        title_elem = await card.query_selector('a, td:first-child, .job-title')
                        title = await title_elem.text_content() if title_elem else None
                        if not title and card_text:
                            # Try to extract from the full text
                            lines = card_text.strip().split('\n')
                            title = lines[0] if lines else None
                        if title:
                            title = title.strip()

                        # Always Stanford, but may have department info
                        company = "Stanford University"

                        # Extract location - often "Stanford, CA" by default
                        location_elem = await card.query_selector('td:nth-child(2), .location')
                        job_location = await location_elem.text_content() if location_elem else "Stanford, CA"
                        if job_location:
                            job_location = job_location.strip()

                        # Extract job type if available
                        type_elem = await card.query_selector('.job-type, [class*="type"], .employment-type')
                        job_type = await type_elem.text_content() if type_elem else None

                        # Extract salary if available
                        salary_elem = await card.query_selector('.salary, [class*="salary"], .compensation')
                        salary_text = await salary_elem.text_content() if salary_elem else None

                        # Get job URL
                        if card.get_by_role:
                            # If it's a card, find the link
                            link_elem = await card.query_selector('a[href*="/jobs/"]')
                        else:
                            # If it's already a link
                            link_elem = card

                        if link_elem:
                            job_href = await link_elem.get_attribute("href")
                            if job_href:
                                if not job_href.startswith("http"):
                                    job_url = f"https://careersearch.stanford.edu{job_href}"
                                else:
                                    job_url = job_href
                            else:
                                # Generate a unique URL based on title
                                unique_str = f"stanford-{title or 'job'}-{jobs_found}"
                                job_url = f"https://careersearch.stanford.edu/jobs/{hashlib.md5(unique_str.encode()).hexdigest()[:8]}"
                        else:
                            # Fallback URL
                            unique_str = f"stanford-{title or 'job'}-{jobs_found}"
                            job_url = f"https://careersearch.stanford.edu/jobs/{hashlib.md5(unique_str.encode()).hexdigest()[:8]}"

                        # Try to get a brief description
                        desc_elem = await card.query_selector('.description, .job-description, [class*="summary"]')
                        description = await desc_elem.text_content() if desc_elem else ""

                        if not description and title:
                            description = f"{title} at Stanford University"
                            if department:
                                description += f" in {department}"
                            if job_location:
                                description += f"\n\nLocation: {job_location}"
                            if job_type:
                                description += f"\nType: {job_type}"
                            if salary_text:
                                description += f"\nSalary: {salary_text}"

                        # Generate source ID
                        source_id = hashlib.md5(job_url.encode()).hexdigest()[:16]

                        # Upsert the job
                        result = await upsert_job(
                            url=job_url,
                            company=company,
                            title=title,
                            location=job_location,
                            description=description.strip(),
                            source="stanford",
                            source_id=source_id,
                            db_path=path,
                        )

                        if result == "inserted":
                            jobs_new += 1
                        else:
                            jobs_updated += 1

                    except Exception as e:
                        print(f"Error processing job card: {e}")
                        jobs_skipped += 1
                        continue

                # Check for next page
                next_button = await page.query_selector('a[aria-label="Next"], .pagination-next, button:has-text("Next")')
                if next_button and page_num < max_pages and jobs_found < max_jobs:
                    try:
                        await next_button.click()
                        await page.wait_for_timeout(2000)
                        page_num += 1
                    except:
                        break
                else:
                    break

            await browser.close()

        await complete_scrape_run(run_id, jobs_found=jobs_found, jobs_new=jobs_new, db_path=path)

    except Exception as e:
        await fail_scrape_run(run_id, str(e), db_path=path)
        raise

    return ScrapeResult(
        source="stanford",
        thread_title=f"Stanford University {search_term} jobs",
        jobs_found=jobs_found,
        jobs_new=jobs_new,
        jobs_updated=jobs_updated,
        jobs_skipped=jobs_skipped,
        run_id=run_id,
    )