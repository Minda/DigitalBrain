"""
Shared fixtures for the jobs MCP test suite.
"""

import asyncio
import os
import tempfile
import pytest
import aiosqlite


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE,
    title TEXT,
    company TEXT NOT NULL,
    location TEXT,
    salary_min INTEGER,
    salary_max INTEGER,
    description TEXT NOT NULL,
    source TEXT NOT NULL,
    source_id TEXT,
    stage TEXT DEFAULT 'inbox',
    relevance INTEGER DEFAULT 0,
    starred INTEGER DEFAULT 0,
    summary TEXT,
    score REAL,
    score_breakdown TEXT,
    tier INTEGER DEFAULT 0,
    viewed INTEGER DEFAULT 0,
    tier_manually_set INTEGER DEFAULT 0,
    applied INTEGER DEFAULT 0,
    posted_at TEXT,
    discovered_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS scrape_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    jobs_found INTEGER DEFAULT 0,
    jobs_new INTEGER DEFAULT 0,
    jobs_filtered INTEGER DEFAULT 0,
    status TEXT DEFAULT 'running',
    error TEXT
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    job_id INTEGER,
    payload TEXT,
    created_at TEXT NOT NULL
);
"""


@pytest.fixture
async def temp_db(tmp_path):
    """
    A fresh SQLite database per test with the full jobs schema.
    Sets JOBS_DB_PATH env var so db.py picks it up automatically.
    """
    db_file = str(tmp_path / "test_jobs.db")
    async with aiosqlite.connect(db_file) as db:
        await db.executescript(SCHEMA_SQL)
        await db.commit()

    os.environ["JOBS_DB_PATH"] = db_file
    yield db_file
    del os.environ["JOBS_DB_PATH"]


# ---------------------------------------------------------------------------
# HN fixture data
# ---------------------------------------------------------------------------

HN_COMMENT_VALID = (
    "<p>Acme AI | Senior ML Engineer | Remote (US)</p>"
    "<p>We are building the next generation of AI-powered tools.</p>"
    "<p>Requirements: Python, PyTorch, 5+ years ML experience.</p>"
    "<p>Salary: $180k-$240k. Apply at <a href='https://acme.ai/jobs'>https://acme.ai/jobs</a></p>"
)

HN_COMMENT_MISSING_COMPANY = "<p> | Senior Engineer | Remote</p><p>Description here.</p>"

HN_COMMENT_OLD = (
    "<p>OldCorp | Data Scientist | New York, NY</p>"
    "<p>Great opportunity at OldCorp. Looking for data scientists.</p>"
)

HN_COMMENT_REMOTE_ONLY = (
    "<p>StartupCo | Product Engineer | Remote</p>"
    "<p>We're a small team building developer tools.</p>"
)

ALGOLIA_SEARCH_RESPONSE = {
    "hits": [
        {
            "objectID": "39894820",
            "title": "Ask HN: Who is hiring? (March 2026)",
            "points": 5,
        },
        {
            "objectID": "99999999",
            "title": "Ask HN: Who wants to be hired? (March 2026)",
            "points": 3,
        },
    ]
}

ALGOLIA_ITEMS_RESPONSE = {
    "id": 39894820,
    "title": "Ask HN: Who is hiring? (March 2026)",
    "children": [
        {
            "id": 111001,
            "type": "comment",
            "text": HN_COMMENT_VALID,
            "created_at_i": 1740960000,  # Recent
        },
        {
            "id": 111002,
            "type": "comment",
            "text": HN_COMMENT_REMOTE_ONLY,
            "created_at_i": 1740960000,
        },
        {
            "id": 111003,
            "type": "comment",
            "text": None,  # Deleted comment — should be skipped
            "deleted": True,
            "created_at_i": 1740960000,
        },
    ],
}


# ---------------------------------------------------------------------------
# 80k Hours fixture data
# ---------------------------------------------------------------------------

EIGHTYKHOURS_CARDS_RAW = [
    {
        "url": "https://80000hours.org/job-board/jobs/ml-engineer-at-anthropic",
        "company": "Anthropic",
        "title": "ML Engineer",
        "location": "Remote / San Francisco",
        "description": "Anthropic is looking for ML engineers to work on frontier AI safety research.",
        "posted_at": None,
    },
    {
        "url": "https://80000hours.org/job-board/jobs/research-scientist-at-deepmind",
        "company": "Google DeepMind",
        "title": "Research Scientist",
        "location": "London",
        "description": "Work on cutting-edge AI safety and alignment research.",
        "posted_at": None,
    },
    {
        # Missing company — should be filtered by parse_job_cards
        "url": "https://80000hours.org/job-board/jobs/unknown-role",
        "company": "",
        "title": "Engineer",
        "location": "Remote",
        "description": "Some description.",
        "posted_at": None,
    },
]
