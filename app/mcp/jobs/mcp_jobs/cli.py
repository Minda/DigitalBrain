"""
CLI entrypoint for job scraping — used by cron jobs.

Bypasses Claude entirely. Calls scraper functions directly.

Usage:
    uv run python -m mcp_jobs.cli scrape --source hn
    uv run python -m mcp_jobs.cli scrape --source 80k
    uv run python -m mcp_jobs.cli scrape --all

Cron example (daily 9am Monday):
    0 9 * * 1 cd /path/to/app/mcp/jobs && uv run python -m mcp_jobs.cli scrape --all
"""

import asyncio
import click

from mcp_jobs.scrapers.hn import scrape_hn
from mcp_jobs.scrapers.eightykhours import scrape_80k
from mcp_jobs.db import count_jobs, delete_jobs
from mcp_jobs.classifier import classify_jobs


@click.group()
def cli():
    pass


@cli.command()
@click.option("--source", type=click.Choice(["hn", "80k"]), help="Which source to scrape")
@click.option("--all", "scrape_all", is_flag=True, help="Scrape all sources")
@click.option("--show-browser", is_flag=True, default=False, help="Run browser non-headless (80k only)")
@click.option("--json", "output_json", is_flag=True, default=False, help="Output result as JSON")
def scrape(source: str, scrape_all: bool, show_browser: bool, output_json: bool):
    """Scrape job listings and store in the database."""
    import json as _json

    if not source and not scrape_all:
        raise click.UsageError("Specify --source <name> or --all")

    sources = ["hn", "80k"] if scrape_all else [source]

    async def run():
        results = []
        for src in sources:
            if not output_json:
                click.echo(f"Scraping {src}...")
            try:
                if src == "hn":
                    result = await scrape_hn()
                elif src == "80k":
                    result = await scrape_80k(headless=not show_browser)
                else:
                    click.echo(f"Unknown source: {src}", err=True)
                    continue

                results.append(result.model_dump())

                if not output_json:
                    click.echo(
                        f"  {src}: {result.jobs_new} new, {result.jobs_updated} updated, "
                        f"{result.jobs_skipped} skipped (of {result.jobs_found} found)"
                    )
                    if result.thread_title:
                        click.echo(f"  Thread: {result.thread_title}")
            except Exception as e:
                if output_json:
                    results.append({"source": src, "error": str(e)})
                else:
                    click.echo(f"  {src} failed: {e}", err=True)

        if output_json:
            click.echo(_json.dumps(results[0] if len(results) == 1 else results))

    asyncio.run(run())


@cli.command()
@click.option("--all", "delete_all", is_flag=True, help="Delete all jobs")
@click.option("--source", type=click.Choice(["hn", "80k"]), help="Delete jobs from specific source")
@click.option("--before", "before_date", help="Delete jobs discovered before date (YYYY-MM-DD)")
@click.option("--after", "after_date", help="Delete jobs discovered after date (YYYY-MM-DD)")
@click.option("--between", "date_range", nargs=2, help="Delete jobs between dates (START END)")
@click.option("--force", is_flag=True, help="Skip confirmation prompt")
@click.option("--dry-run", is_flag=True, help="Show count without deleting")
@click.option("--json", "output_json", is_flag=True, help="Output result as JSON")
def delete(delete_all, source, before_date, after_date, date_range, force, dry_run, output_json):
    """Delete jobs from the database with flexible filtering."""
    import json as _json

    # Validate arguments
    if not delete_all and not source and not before_date and not after_date and not date_range:
        raise click.UsageError(
            "Must specify at least one filter: --all, --source, --before, --after, or --between"
        )

    # Handle --between option
    if date_range:
        after_date = date_range[0]
        before_date = date_range[1]

    async def run():
        # Count jobs that will be deleted
        count = await count_jobs(
            source=source,
            before_date=before_date,
            after_date=after_date,
        )

        if count == 0:
            if output_json:
                click.echo(_json.dumps({"deleted": 0, "message": "No jobs match the filter"}))
            else:
                click.echo("No jobs match the filter. Nothing to delete.")
            return

        # Build filter description
        filters = []
        if source:
            filters.append(f"source={source}")
        if before_date:
            filters.append(f"before {before_date}")
        if after_date:
            filters.append(f"after {after_date}")
        filter_desc = ", ".join(filters) if filters else "all jobs"

        # Dry run mode
        if dry_run:
            if output_json:
                click.echo(_json.dumps({"count": count, "filters": filter_desc, "dry_run": True}))
            else:
                click.echo(f"Would delete {count} job(s) ({filter_desc})")
            return

        # Confirmation prompt (unless --force)
        if not force:
            if not output_json:
                click.echo(f"About to delete {count} job(s) ({filter_desc})")
                click.confirm("Are you sure?", abort=True)

        # Delete jobs
        deleted = await delete_jobs(
            source=source,
            before_date=before_date,
            after_date=after_date,
        )

        if output_json:
            click.echo(_json.dumps({"deleted": deleted, "filters": filter_desc}))
        else:
            click.echo(f"Deleted {deleted} job(s)")

    asyncio.run(run())


@cli.command()
@click.option("--batch-size", default=50, show_default=True, help="Max jobs to classify in this run")
@click.option("--force", is_flag=True, help="Reclassify jobs that already have a relevance score")
@click.option("--json", "output_json", is_flag=True, default=False, help="Output result as JSON")
def classify(batch_size: int, force: bool, output_json: bool):
    """Classify unclassified jobs using Claude."""
    import json as _json

    async def run():
        if not output_json:
            click.echo(f"Classifying up to {batch_size} jobs...")
        try:
            result = await classify_jobs(batch_size=batch_size, force=force)

            if output_json:
                click.echo(_json.dumps(result))
            else:
                if result["classified"] == 0:
                    click.echo("No jobs to classify.")
                else:
                    tokens = result["tokens_used"]
                    click.echo(f"  Classified: {result['classified']} jobs (run #{result['run_id']})")
                    click.echo(f"  Remaining:  {result['remaining']}")
                    click.echo(f"  Model:      {result['model']}")
                    click.echo(f"  Tokens:     {tokens['input']} in / {tokens['output']} out")
        except Exception as e:
            if output_json:
                click.echo(_json.dumps({"error": str(e)}))
            else:
                click.echo(f"  Failed: {e}", err=True)
            raise SystemExit(1)

    asyncio.run(run())


def main():
    cli()


if __name__ == "__main__":
    main()
