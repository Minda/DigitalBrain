"""
Job classifier using Claude Haiku with structured output.

Mirrors the TypeScript classifier at app/web/src/modules/jobs/classifier.ts.
Uses tool use to get structured JSON output from the model.

Usage (via CLI):
    uv run python -m mcp_jobs.cli classify
    uv run python -m mcp_jobs.cli classify --batch-size 100 --json
    uv run python -m mcp_jobs.cli classify --force  # reclassify all
"""

import asyncio
import json
from pathlib import Path
from typing import Optional

import aiosqlite
import anthropic
from langsmith.wrappers import wrap_anthropic

from mcp_jobs.db import get_db_path, now_iso

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

MODEL_ID = "claude-haiku-4-5-20251001"
CONCURRENCY = 10
_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
PROFILE_PATH = _PROJECT_ROOT / "config" / "job-profile.md"

# ---------------------------------------------------------------------------
# Structured output tool schema
# ---------------------------------------------------------------------------

CLASSIFICATION_TOOL = {
    "name": "classify_job",
    "description": "Classify a job posting for relevance to the user's preferences",
    "input_schema": {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
                "description": "2-3 sentence summary of the job posting",
            },
            "relevance": {
                "type": "integer",
                "description": "Relevance to user profile (1-3): 1=perfect match, 2=good match, 3=distant match",
                "minimum": 1,
                "maximum": 3,
            },
            "breakdown": {
                "type": "object",
                "properties": {
                    "roleMatch": {
                        "type": "integer",
                        "description": "How well the role matches target roles (1-3): 1=great, 2=ok, 3=poor",
                        "minimum": 1,
                        "maximum": 3,
                    },
                    "techMatch": {
                        "type": "integer",
                        "description": "How well tech stack matches interests (1-3): 1=great, 2=ok, 3=poor",
                        "minimum": 1,
                        "maximum": 3,
                    },
                    "locationFit": {
                        "type": "integer",
                        "description": "How well location matches preferences (1-3): 1=great, 2=ok, 3=poor",
                        "minimum": 1,
                        "maximum": 3,
                    },
                    "dealbreakers": {
                        "type": "boolean",
                        "description": "True if any dealbreakers are present",
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "1-2 sentence explanation of the score",
                    },
                },
                "required": ["roleMatch", "techMatch", "locationFit", "dealbreakers", "reasoning"],
            },
        },
        "required": ["summary", "relevance", "breakdown"],
    },
}

# ---------------------------------------------------------------------------
# Profile + few-shot loading
# ---------------------------------------------------------------------------


def load_user_profile() -> str:
    if not PROFILE_PATH.exists():
        raise FileNotFoundError(
            f"Job profile not found at {PROFILE_PATH}. "
            "Create config/job-profile.md with your preferences before classifying."
        )
    content = PROFILE_PATH.read_text().strip()
    if "[e.g.," in content:
        raise ValueError(
            "Job profile still contains placeholder text. "
            "Edit config/job-profile.md with your actual preferences before classifying."
        )
    return content


async def load_few_shot_examples(db_path: str) -> list[dict]:
    """Load up to 10 recent relevance corrections to use as few-shot calibration."""
    examples = []
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT job_id, payload
               FROM events
               WHERE event_type = 'relevance_corrected'
               ORDER BY created_at DESC
               LIMIT 10"""
        ) as cursor:
            corrections = await cursor.fetchall()

        for corr in corrections:
            if not corr["job_id"] or not corr["payload"]:
                continue
            try:
                payload = json.loads(corr["payload"])
                new_relevance = payload.get("newRelevance")
                if new_relevance is None:
                    continue
            except (json.JSONDecodeError, KeyError):
                continue

            async with db.execute(
                "SELECT company, title, location, description FROM postings WHERE id = ?",
                (corr["job_id"],),
            ) as jcursor:
                job = await jcursor.fetchone()

            if job:
                examples.append(
                    {
                        "company": job["company"],
                        "title": job["title"],
                        "location": job["location"],
                        "description": job["description"],
                        "relevance": new_relevance,
                    }
                )

    return examples


def build_few_shot_block(examples: list[dict]) -> str:
    if not examples:
        return ""

    lines = []
    for ex in examples:
        label = ex.get("title") or "Untitled"
        loc = f" ({ex['location']})" if ex.get("location") else ""
        desc = (ex.get("description") or "")[:150].replace("\n", " ")
        lines.append(f"- {ex['company']} — {label}{loc}: relevance={ex['relevance']}\n  \"{desc}...\"")

    return (
        "\nHere are examples of how the user rated previous jobs (use these to calibrate):\n"
        + "\n".join(lines)
        + "\n"
    )


# ---------------------------------------------------------------------------
# Single job classification
# ---------------------------------------------------------------------------


async def classify_single_job(
    client: anthropic.AsyncAnthropic,
    job: dict,
    profile: str,
    few_shot_block: str,
) -> dict:
    """Call Claude to classify one job. Returns dict with job_id, result, usage."""
    system = (
        "You are a job relevance classifier. Given a user's job preferences and a job posting, "
        "classify the job on a 1-3 relevance scale.\n\n"
        f"User Profile:\n{profile}"
        f"{few_shot_block}\n"
        "Rate the job based on how well it matches the user's preferences: "
        "1=perfect match (meets most criteria), "
        "2=good match (meets some criteria, worth reviewing), "
        "3=distant match (tangentially related)."
    )

    prompt = (
        f"Company: {job['company']}\n"
        f"Title: {job.get('title') or 'Not specified'}\n"
        f"Location: {job.get('location') or 'Not specified'}\n\n"
        f"Description:\n{job['description']}"
    )

    response = await client.messages.create(
        model=MODEL_ID,
        max_tokens=1024,
        system=system,
        tools=[CLASSIFICATION_TOOL],
        tool_choice={"type": "tool", "name": "classify_job"},
        messages=[{"role": "user", "content": prompt}],
    )

    tool_use = next((b for b in response.content if b.type == "tool_use"), None)
    if not tool_use:
        raise ValueError(f"No tool use in response for job {job['id']}")

    result = tool_use.input

    # Clamp all integer scores to 1-3
    result["relevance"] = max(1, min(3, result["relevance"]))
    bd = result.get("breakdown", {})
    bd["roleMatch"] = max(1, min(3, bd.get("roleMatch", 3)))
    bd["techMatch"] = max(1, min(3, bd.get("techMatch", 3)))
    bd["locationFit"] = max(1, min(3, bd.get("locationFit", 3)))

    return {
        "job_id": job["id"],
        "result": result,
        "usage": {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens,
        },
    }


# ---------------------------------------------------------------------------
# Batch classification
# ---------------------------------------------------------------------------


async def classify_jobs(
    batch_size: int = 50,
    force: bool = False,
    db_path: Optional[str] = None,
) -> dict:
    """
    Classify unclassified jobs in the database.

    Args:
        batch_size: Max number of jobs to classify in this run (default 50).
        force: If True, reclassify jobs that already have a relevance score.
        db_path: Override database path (uses default if None).

    Returns:
        Dict with run_id, classified, remaining, model, tokens_used.
    """
    path = db_path or get_db_path()

    profile = load_user_profile()
    examples = await load_few_shot_examples(path)
    few_shot_block = build_few_shot_block(examples)

    where = "1=1" if force else "(relevance = 0 OR relevance IS NULL)"

    async with aiosqlite.connect(path) as db:
        db.row_factory = aiosqlite.Row

        async with db.execute(
            f"SELECT id, company, title, location, description FROM postings WHERE {where} LIMIT ?",
            (batch_size,),
        ) as cursor:
            jobs_to_classify = [dict(row) for row in await cursor.fetchall()]

        if not jobs_to_classify:
            return {
                "run_id": 0,
                "classified": 0,
                "remaining": 0,
                "model": MODEL_ID,
                "tokens_used": {"input": 0, "output": 0},
            }

        async with db.execute(f"SELECT COUNT(*) FROM postings WHERE {where}") as cursor:
            total_unclassified = (await cursor.fetchone())[0]
        remaining_after = max(0, total_unclassified - len(jobs_to_classify))

        cursor = await db.execute(
            "INSERT INTO classification_runs (started_at, model, jobs_total, status) VALUES (?, ?, ?, 'running')",
            (now_iso(), MODEL_ID, len(jobs_to_classify)),
        )
        run_id = cursor.lastrowid
        await db.commit()

    client = wrap_anthropic(anthropic.AsyncAnthropic())
    total_input = 0
    total_output = 0
    classified = 0

    try:
        for i in range(0, len(jobs_to_classify), CONCURRENCY):
            batch = jobs_to_classify[i : i + CONCURRENCY]

            tasks = [classify_single_job(client, job, profile, few_shot_block) for job in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            async with aiosqlite.connect(path) as db:
                for res in results:
                    if isinstance(res, Exception):
                        print(f"  Classification failed: {res}")
                        continue

                    total_input += res["usage"]["input"]
                    total_output += res["usage"]["output"]
                    r = res["result"]

                    await db.execute(
                        """UPDATE postings
                           SET relevance = ?, score = ?, score_breakdown = ?, summary = ?, updated_at = ?
                           WHERE id = ?""",
                        (
                            r["relevance"],
                            r["relevance"],  # use relevance as score for now
                            json.dumps(r["breakdown"]),
                            r["summary"],
                            now_iso(),
                            res["job_id"],
                        ),
                    )
                    classified += 1
                await db.commit()

        async with aiosqlite.connect(path) as db:
            await db.execute(
                """UPDATE classification_runs
                   SET completed_at = ?, jobs_classified = ?, jobs_skipped = ?,
                       input_tokens = ?, output_tokens = ?, status = 'completed'
                   WHERE id = ?""",
                (
                    now_iso(),
                    classified,
                    len(jobs_to_classify) - classified,
                    total_input,
                    total_output,
                    run_id,
                ),
            )
            await db.commit()

    except Exception as e:
        async with aiosqlite.connect(path) as db:
            await db.execute(
                """UPDATE classification_runs
                   SET completed_at = ?, jobs_classified = ?, input_tokens = ?,
                       output_tokens = ?, status = 'failed', error = ?
                   WHERE id = ?""",
                (now_iso(), classified, total_input, total_output, str(e), run_id),
            )
            await db.commit()
        raise

    return {
        "run_id": run_id,
        "classified": classified,
        "remaining": remaining_after,
        "model": MODEL_ID,
        "tokens_used": {"input": total_input, "output": total_output},
    }
