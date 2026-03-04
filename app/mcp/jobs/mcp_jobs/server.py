"""
MCP server for job scraping tools.

Exposes scrape_hn and scrape_80k_hours as Claude tools.
Install: uv run mcp install mcp_jobs/server.py --name jobs

For UI-triggered scrapes, the Next.js app makes a Claude API call with these
tools available — Claude calls them and returns the result.
"""

from mcp.server.fastmcp import FastMCP

from mcp_jobs.scrapers.hn import scrape_hn
from mcp_jobs.scrapers.eightykhours import scrape_80k

mcp = FastMCP(
    "Jobs MCP Server",
    instructions=(
        "Scrape job listings from Hacker News and 80,000 Hours and store them "
        "in the local jobs database. Use these tools to fetch fresh job postings. "
        "Listings older than 7 days are automatically skipped."
    ),
)


@mcp.tool()
async def scrape_hn_jobs() -> dict:
    """
    Scrape the latest 'Ask HN: Who is Hiring?' thread and save new job listings
    to the database. Returns counts of jobs found, new, updated, and skipped.
    """
    result = await scrape_hn()
    return result.model_dump()


@mcp.tool()
async def scrape_80k_hours_jobs() -> dict:
    """
    Scrape the 80,000 Hours job board using browser automation and save new
    listings to the database. Returns counts of jobs found, new, updated, and skipped.
    """
    result = await scrape_80k()
    return result.model_dump()


@mcp.tool()
async def scrape_all_jobs() -> dict:
    """
    Scrape all configured job sources (HN + 80k Hours) and return a combined summary.
    """
    hn_result = await scrape_hn()
    eightykhours_result = await scrape_80k()

    return {
        "sources": {
            "hn": hn_result.model_dump(),
            "80k": eightykhours_result.model_dump(),
        },
        "totals": {
            "jobs_new": hn_result.jobs_new + eightykhours_result.jobs_new,
            "jobs_found": hn_result.jobs_found + eightykhours_result.jobs_found,
            "jobs_skipped": hn_result.jobs_skipped + eightykhours_result.jobs_skipped,
        },
    }


if __name__ == "__main__":
    mcp.run()
