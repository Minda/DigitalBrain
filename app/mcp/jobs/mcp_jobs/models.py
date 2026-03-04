from pydantic import BaseModel
from typing import Optional


class Job(BaseModel):
    id: Optional[int] = None
    url: str
    title: Optional[str] = None
    company: str
    location: Optional[str] = None
    description: str
    source: str
    source_id: Optional[str] = None
    posted_at: Optional[str] = None
    discovered_at: str
    updated_at: str


class ScrapeResult(BaseModel):
    source: str
    thread_title: Optional[str] = None  # HN thread title, or None for other sources
    jobs_found: int = 0    # Total listings examined
    jobs_new: int = 0      # Newly inserted
    jobs_updated: int = 0  # Existing, description refreshed
    jobs_skipped: int = 0  # Skipped (too old, missing fields)
    run_id: int


class ClassifyResult(BaseModel):
    run_id: int
    classified: int
    remaining: int
    model: str
    tokens_used: dict
