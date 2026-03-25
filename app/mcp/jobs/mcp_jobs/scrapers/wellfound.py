"""
Wellfound (formerly AngelList) job scraper.

Uses Playwright to scrape job listings from Wellfound.
Searches for software engineering roles in the US.
"""

import re
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


async def scrape_wellfound(
    role: str = "software-engineer",
    location: str = "united-states",
    max_jobs: int = 50,
    db_path: Optional[str] = None,
) -> ScrapeResult:
    """
    Scrape Wellfound job listings.

    Args:
        role: Role slug (default: "software-engineer")
        location: Location slug (default: "united-states")
        max_jobs: Maximum number of jobs to scrape
        db_path: Database path

    Returns:
        ScrapeResult with job counts
    """
    path = db_path or get_db_path()
    run_id = await create_scrape_run("wellfound", db_path=path)

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

            # Navigate to Wellfound job listings
            url = f"https://wellfound.com/role/l/{role}/{location}"
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(3000)

            # Wait for job listings to load - be more flexible
            try:
                await page.wait_for_selector('[data-test="JobSearchResults"], [class*="JobSearchResults"], [class*="jobList"]', timeout=10000)
            except:
                # Try alternative approaches
                try:
                    await page.wait_for_selector('.styles_jobListings__, [class*="jobListing"], [class*="JobListing"]', timeout=5000)
                except:
                    # Just wait and continue - page might have loaded already
                    await page.wait_for_timeout(3000)

            # Scroll to load more jobs (Wellfound uses infinite scroll)
            previous_height = 0
            scroll_attempts = 0
            max_scroll_attempts = 5

            while scroll_attempts < max_scroll_attempts and jobs_found < max_jobs:
                # Scroll to bottom
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(2000)

                # Check if page height changed
                current_height = await page.evaluate("document.body.scrollHeight")
                if current_height == previous_height:
                    break
                previous_height = current_height
                scroll_attempts += 1

            # Extract job listings
            # Try multiple possible selectors - Wellfound frequently changes their structure
            job_cards = await page.query_selector_all('[data-test="StartupResult"], [data-test*="Job"]')
            if not job_cards:
                job_cards = await page.query_selector_all('[class*="styles_jobListing"], [class*="JobListing"]')
            if not job_cards:
                job_cards = await page.query_selector_all('[class*="job-listing"], [class*="startup"]')
            if not job_cards:
                # Try finding any divs/articles that contain job-like content
                job_cards = await page.query_selector_all('div[class*="styles_"], article[class*="styles_"]')

            for card in job_cards[:max_jobs]:
                try:
                    jobs_found += 1

                    # Extract company name
                    company_elem = await card.query_selector('[data-test="StartupResultName"]')
                    if not company_elem:
                        company_elem = await card.query_selector('h4')
                    if not company_elem:
                        company_elem = await card.query_selector('[class*="startup-link"]')

                    company = await company_elem.text_content() if company_elem else None
                    if not company:
                        jobs_skipped += 1
                        continue
                    company = company.strip()

                    # Extract job title
                    title_elem = await card.query_selector('[data-test="StartupResultJobListingName"]')
                    if not title_elem:
                        title_elem = await card.query_selector('.styles_jobTitle__')
                    if not title_elem:
                        title_elem = await card.query_selector('[class*="job-title"]')

                    title = await title_elem.text_content() if title_elem else None
                    if title:
                        title = title.strip()

                    # Extract location
                    location_elem = await card.query_selector('[class*="location"]')
                    if not location_elem:
                        location_elem = await card.query_selector('[data-test="StartupResultLocation"]')

                    job_location = await location_elem.text_content() if location_elem else None
                    if job_location:
                        job_location = job_location.strip()

                    # Extract salary if available
                    salary_elem = await card.query_selector('[class*="salary"]')
                    if not salary_elem:
                        salary_elem = await card.query_selector('[class*="compensation"]')

                    salary_text = await salary_elem.text_content() if salary_elem else None

                    # Extract description/tagline
                    desc_elem = await card.query_selector('[class*="tagline"]')
                    if not desc_elem:
                        desc_elem = await card.query_selector('[class*="description"]')
                    if not desc_elem:
                        desc_elem = await card.query_selector('span[class*="styles_tagline"]')

                    description = await desc_elem.text_content() if desc_elem else ""
                    if not description:
                        description = f"{title or 'Position'} at {company}"

                    # Add additional info to description
                    if job_location:
                        description += f"\n\nLocation: {job_location}"
                    if salary_text:
                        description += f"\nSalary: {salary_text}"

                    # Get job URL
                    link_elem = await card.query_selector('a[href*="/jobs/"]')
                    if not link_elem:
                        link_elem = await card.query_selector('a[href*="/company/"]')

                    if link_elem:
                        job_href = await link_elem.get_attribute("href")
                        if job_href:
                            if not job_href.startswith("http"):
                                job_url = f"https://wellfound.com{job_href}"
                            else:
                                job_url = job_href
                        else:
                            # Generate a unique URL based on company and title
                            unique_str = f"{company}-{title or 'job'}-{jobs_found}"
                            job_url = f"https://wellfound.com/jobs/{hashlib.md5(unique_str.encode()).hexdigest()[:8]}"
                    else:
                        # Fallback URL
                        unique_str = f"{company}-{title or 'job'}-{jobs_found}"
                        job_url = f"https://wellfound.com/jobs/{hashlib.md5(unique_str.encode()).hexdigest()[:8]}"

                    # Generate source ID
                    source_id = hashlib.md5(job_url.encode()).hexdigest()[:16]

                    # Upsert the job
                    result = await upsert_job(
                        url=job_url,
                        company=company,
                        title=title,
                        location=job_location,
                        description=description.strip(),
                        source="wellfound",
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

            await browser.close()

        await complete_scrape_run(run_id, jobs_found=jobs_found, jobs_new=jobs_new, db_path=path)

    except Exception as e:
        await fail_scrape_run(run_id, str(e), db_path=path)
        raise

    return ScrapeResult(
        source="wellfound",
        thread_title=f"{role} jobs in {location}",
        jobs_found=jobs_found,
        jobs_new=jobs_new,
        jobs_updated=jobs_updated,
        jobs_skipped=jobs_skipped,
        run_id=run_id,
    )