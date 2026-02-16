#!/usr/bin/env python3
"""
Classify clothing-related email senders using Claude Haiku.

Two-pass architecture:
  Pass 1: Sender-level — "Is this sender a clothing brand?" (Haiku)
  Pass 2: Email-level — "Is this email purchase/marketing/account?" (heuristic, free)

Supports two backends (auto-detected):
  - api: Anthropic Python SDK (requires ANTHROPIC_API_KEY)
  - cli: Claude CLI subprocess (works with Claude Max OAuth)

Multi-signal voting instead of LLM self-reported confidence.
Three-phase execution: classify → label → trash (independent CLI flags).
Batch progression with intermittent reviews: --batch 5|25|100|all

Usage:
  python classify_emails_haiku.py --phase classify [--dry-run] [--limit 50]
  python classify_emails_haiku.py --phase label --batch 5 --execute
  python classify_emails_haiku.py --phase label --batch all --execute
  python classify_emails_haiku.py --phase trash --dry-run
  python classify_emails_haiku.py --phase trash --batch 5 --execute
  python classify_emails_haiku.py --stats

⚠️ PRIVACY: All email-derived data MUST be stored in personal/
"""

import sys
import os
import re
import json
import time
import uuid
import sqlite3
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
from functools import wraps

# Load .env file if present
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

# Add the mcp-gmail module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "app" / "mcp" / "gmail"))

from mcp_gmail.gmail import (
    get_gmail_service, get_message, get_headers_dict,
    parse_message_body, get_labels, create_label,
    batch_modify_messages_labels, trash_message,
)
from setup_email_classifier_db import setup_database

import subprocess
import shutil

try:
    import anthropic
    HAS_ANTHROPIC_SDK = True
except ImportError:
    HAS_ANTHROPIC_SDK = False


# --- Constants ---

DB_PATH = Path("personal/data/email-classifier/clothing_emails.db")
SENDERS_JSON = Path("personal/data/email-classifier/clothing_senders.json")
BRANDS_FILE = Path("personal/data/email-classifier/clothing_brands.txt")

KNOWN_MIXED_SENDERS = {"amazon", "target", "walmart", "ebay", "costco", "etsy"}

PURCHASE_PATTERNS = re.compile(
    r"(order\s*#|order\s+confirm|ship(ping|ped)|track(ing|ed)|"
    r"receipt|invoice|return\s+label|refund|deliver(y|ed)|"
    r"your\s+order|has\s+shipped|on\s+its\s+way)",
    re.IGNORECASE
)

MARKETING_PATTERNS = re.compile(
    r"(%\s*off|sale\b|new\s+arrival|promo|free\s+shipping|"
    r"limited\s+time|flash\s+sale|exclusive|just\s+dropped|"
    r"don'?t\s+miss|last\s+chance|shop\s+now|clearance|"
    r"new\s+collection|trending|best\s+seller)",
    re.IGNORECASE
)

ACCOUNT_PATTERNS = re.compile(
    r"(password|verify|security|two.factor|2fa|"
    r"loyalty|points|reward|credit\s+card|account\s+update|"
    r"sign.in|log.in|confirm\s+your\s+email)",
    re.IGNORECASE
)


# --- Usage Tracking ---

class RunStats:
    """Track per-batch usage stats, flush to processing_stats table."""

    def __init__(self, run_id, phase, batch_size):
        self.run_id = run_id
        self.phase = phase
        self.batch_size = str(batch_size)
        self.start_time = time.time()
        self.emails_processed = 0
        self.purchases_found = 0
        self.marketing_found = 0
        self.others_found = 0
        self.labels_applied = 0
        self.emails_trashed = 0
        self.haiku_calls = 0
        self.haiku_cost_usd = 0.0
        self.gmail_api_calls = 0
        self.errors = 0

    def record_gmail_call(self, count=1):
        self.gmail_api_calls += count

    def record_haiku_call(self, cost_usd=0.0):
        self.haiku_calls += 1
        self.haiku_cost_usd += cost_usd

    def record_error(self):
        self.errors += 1

    @property
    def wall_time_seconds(self):
        return time.time() - self.start_time

    def flush_to_db(self, db_path):
        """Write stats to processing_stats table."""
        conn = sqlite3.connect(db_path)
        conn.execute("""
            INSERT INTO processing_stats
            (run_date, total_emails_processed, purchases_found, marketing_found,
             others_found, labels_applied, emails_archived,
             haiku_calls, haiku_cost_usd, gmail_api_calls, errors,
             wall_time_seconds, batch_size, phase, run_id, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            self.emails_processed,
            self.purchases_found,
            self.marketing_found,
            self.others_found,
            self.labels_applied,
            self.emails_trashed,
            self.haiku_calls,
            self.haiku_cost_usd,
            self.gmail_api_calls,
            self.errors,
            self.wall_time_seconds,
            self.batch_size,
            self.phase,
            self.run_id,
            None,
        ))
        conn.commit()
        conn.close()

    def print_summary(self):
        """Print end-of-batch summary."""
        print(f"\n{'='*60}")
        print(f"  Run Summary")
        print(f"{'='*60}")
        print(f"  Run ID: {self.run_id}")
        print(f"  Phase: {self.phase} | Batch: {self.batch_size}")
        print(f"")
        print(f"  Emails processed:    {self.emails_processed}")
        if self.phase in ("label", "classify"):
            print(f"    Purchases labeled: {self.purchases_found}")
            print(f"    Marketing labeled: {self.marketing_found}")
            print(f"    Review/Other:      {self.others_found}")
        if self.emails_trashed:
            print(f"    Trashed:           {self.emails_trashed}")
        print(f"")
        print(f"  API Usage:")
        print(f"    Gmail API calls:  {self.gmail_api_calls}")
        print(f"    Haiku calls:      {self.haiku_calls}")
        print(f"    Haiku cost:       ${self.haiku_cost_usd:.4f}")
        print(f"")
        print(f"  Time: {self.wall_time_seconds:.1f}s")
        print(f"  Errors: {self.errors}")


def print_cumulative_stats():
    """Print cumulative statistics from all runs."""
    db_path = DB_PATH
    if not db_path.exists():
        print("No database found. Run --phase classify first.")
        return

    # Ensure schema is up to date (adds new columns if missing)
    setup_database()
    conn = sqlite3.connect(db_path)

    cursor = conn.execute("""
        SELECT
            COUNT(*) as runs,
            COALESCE(SUM(total_emails_processed), 0) as total_processed,
            COALESCE(SUM(purchases_found), 0) as total_purchases,
            COALESCE(SUM(marketing_found), 0) as total_marketing,
            COALESCE(SUM(others_found), 0) as total_others,
            COALESCE(SUM(labels_applied), 0) as total_labels,
            COALESCE(SUM(emails_archived), 0) as total_trashed,
            COALESCE(SUM(haiku_calls), 0) as total_haiku,
            COALESCE(SUM(haiku_cost_usd), 0) as total_cost,
            COALESCE(SUM(gmail_api_calls), 0) as total_gmail,
            COALESCE(SUM(wall_time_seconds), 0) as total_time,
            COALESCE(SUM(errors), 0) as total_errors
        FROM processing_stats
    """)
    row = cursor.fetchone()

    if not row or row[0] == 0:
        print("No processing runs recorded yet.")
        conn.close()
        return

    (runs, processed, purchases, marketing, others, labels,
     trashed, haiku, cost, gmail, wall_time, errors) = row

    total_classified = purchases + marketing + others
    pct_p = (purchases / total_classified * 100) if total_classified else 0
    pct_m = (marketing / total_classified * 100) if total_classified else 0
    pct_o = (others / total_classified * 100) if total_classified else 0

    print(f"\n{'='*60}")
    print(f"  Cumulative Statistics")
    print(f"{'='*60}")
    print(f"  Runs: {runs}")
    print(f"  Total emails processed: {processed}")
    if total_classified:
        print(f"    Purchases: {purchases} ({pct_p:.0f}%)")
        print(f"    Marketing: {marketing} ({pct_m:.0f}%)")
        print(f"    Other:     {others} ({pct_o:.0f}%)")
    print(f"")
    print(f"  Labels applied: {labels}")
    print(f"  Emails trashed: {trashed}")
    print(f"  Haiku calls:    {haiku}")
    print(f"  Haiku cost:     ${cost:.4f}")
    print(f"  Gmail API calls: {gmail}")
    print(f"  Total time:     {wall_time:.1f}s")
    print(f"  Errors:         {errors}")

    # Show recent runs
    cursor = conn.execute("""
        SELECT run_date, phase, batch_size, total_emails_processed, errors
        FROM processing_stats
        ORDER BY run_date DESC
        LIMIT 5
    """)
    recent = cursor.fetchall()
    if recent:
        print(f"\n  Recent runs:")
        for run_date, phase, batch, count, errs in recent:
            date_short = run_date[:16] if run_date else "?"
            err_flag = f" ({errs} errors)" if errs else ""
            print(f"    {date_short} | {phase or '?':8s} | batch={batch or '?':4s} | {count or 0} emails{err_flag}")

    conn.close()


# --- Retry decorator ---

def retry_with_backoff(max_retries=3, base_delay=1.0, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries - 1:
                        raise
                    delay = base_delay * (2 ** attempt)
                    print(f"  ⚠️ {func.__name__} failed (attempt {attempt+1}): {e}. Retrying in {delay}s...")
                    time.sleep(delay)
        return wrapper
    return decorator


# --- Gmail helpers ---

def get_gmail_service_instance():
    """Initialize Gmail service with credentials from app/mcp/gmail/."""
    credentials_path = Path(__file__).parent.parent.parent / "app" / "mcp" / "gmail" / "credentials.json"
    token_path = Path(__file__).parent.parent.parent / "app" / "mcp" / "gmail" / "token.json"

    if not credentials_path.exists():
        raise FileNotFoundError(f"Gmail credentials not found at {credentials_path}")

    service = get_gmail_service(
        credentials_path=str(credentials_path),
        token_path=str(token_path),
    )
    return service


def list_all_message_ids(service, query="in:inbox", max_total=None):
    """
    Paginate Gmail API to collect all message IDs.
    The MCP wrapper silently caps at 500 — this handles nextPageToken properly.
    """
    all_messages = []
    page_token = None

    while True:
        kwargs = {"userId": "me", "q": query, "maxResults": 500}
        if page_token:
            kwargs["pageToken"] = page_token

        response = service.users().messages().list(**kwargs).execute()
        messages = response.get("messages", [])
        all_messages.extend(messages)

        if max_total and len(all_messages) >= max_total:
            return all_messages[:max_total]

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return all_messages


@retry_with_backoff(max_retries=3, base_delay=0.5)
def fetch_message(service, msg_id):
    """Fetch a single message with retry logic."""
    return get_message(service, msg_id)


@retry_with_backoff(max_retries=3, base_delay=0.5)
def fetch_message_metadata(service, msg_id, headers=None):
    """Fetch only message headers (no body). ~100x faster than full fetch."""
    if headers is None:
        headers = ['From', 'Subject', 'Date', 'List-Unsubscribe']
    return service.users().messages().get(
        userId='me', id=msg_id,
        format='metadata',
        metadataHeaders=headers,
    ).execute()


# --- Sender extraction ---

def extract_unique_senders(service, message_ids, max_sample_per_sender=3, run_stats=None):
    """
    Group messages by sender. For each sender, keep sample subjects and message IDs.
    Uses metadata-only fetches and rate limiting to stay within Gmail API quota.

    Returns: {email: {name, message_ids, sample_subjects, has_list_unsubscribe}}
    """
    senders = defaultdict(lambda: {
        "name": "", "message_ids": [], "sample_subjects": [],
        "has_list_unsubscribe": False
    })

    print(f"  Extracting senders from {len(message_ids)} messages...")

    for i, msg_ref in enumerate(message_ids):
        if i % 200 == 0 and i > 0:
            print(f"  Processed {i}/{len(message_ids)} messages...")

        # Rate limit: ~50 messages.get per second
        if i > 0 and i % 50 == 0:
            time.sleep(1.0)

        try:
            msg = fetch_message(service, msg_ref["id"])
            if run_stats:
                run_stats.record_gmail_call()
            headers = get_headers_dict(msg)

            sender_raw = headers.get("From", "")
            subject = headers.get("Subject", "")
            list_unsub = headers.get("List-Unsubscribe", "")

            # Parse sender email
            email_match = re.search(r'<(.+?)>', sender_raw)
            if email_match:
                email = email_match.group(1).lower()
                name = sender_raw[:sender_raw.index('<')].strip().strip('"')
            else:
                email = sender_raw.lower().strip()
                name = ""

            senders[email]["message_ids"].append(msg_ref["id"])
            if name and not senders[email]["name"]:
                senders[email]["name"] = name
            if subject and len(senders[email]["sample_subjects"]) < max_sample_per_sender:
                senders[email]["sample_subjects"].append(subject[:120])
            if list_unsub:
                senders[email]["has_list_unsubscribe"] = True

        except Exception:
            continue

    print(f"  Found {len(senders)} unique senders")
    return dict(senders)


# --- Known senders ---

def load_personalized_senders():
    """Load personalized clothing sender list if available."""
    if SENDERS_JSON.exists():
        with open(SENDERS_JSON, 'r') as f:
            data = json.load(f)
            return data
    return {}


def classify_known_sender(sender_email, personalized_senders):
    """
    Fast path: check if sender is in the known list.

    Mixed senders (Amazon, Target, etc.) are identified but NOT classified
    as clothing — they sell everything, so individual emails need further
    filtering that Phase 1 doesn't provide. They get logged as mixed
    senders but skipped for labeling.
    """
    # Check JSON file (dedicated clothing brands)
    for known_email, info in personalized_senders.items():
        if known_email in sender_email or sender_email.endswith(f"@{known_email}.com"):
            return {
                "is_clothing": True,
                "is_mixed_sender": False,
                "reasoning": f"Known clothing sender: {known_email}",
                "method": "known",
            }

    # Check known mixed senders — flag but don't label as clothing
    for mixed in KNOWN_MIXED_SENDERS:
        if mixed in sender_email:
            return {
                "is_clothing": False,
                "is_mixed_sender": True,
                "reasoning": f"Mixed mega-retailer: {mixed} — skipped (sells non-clothing too)",
                "method": "known",
            }

    return None


# --- Haiku classification (Pass 1) ---

HAIKU_SYSTEM_PROMPT = """You are classifying email senders. Given a sender's email address, display name, and sample email subjects, determine:
1. Is this sender primarily a clothing/fashion/footwear/accessories brand or retailer?
2. Is this a mixed mega-retailer that sells many categories beyond clothing?

Classification rules:
- "Clothing brand" means the sender's PRIMARY business is selling garments, shoes, or fashion accessories.
- Department stores (Nordstrom, Macy's) count as clothing even though they sell other items.
- Resale platforms focused on clothing (ThredUp, Poshmark) count as clothing.
- Outdoor/athletic brands (Patagonia, REI, lululemon) count as clothing.

NOT clothing (common false positives):
- Financial services, banks, credit cards (even if named like "NerdWallet")
- Software marketplaces (Notion Marketplace, Creative Market, Zoom App Marketplace)
- Social media platforms (Instagram suggestions, Slack notifications)
- Neighborhood services (Nextdoor, local community posts)
- Airlines, hotels, travel services (JetBlue, etc.)
- Food delivery, restaurants, grocery
- Organizations, foundations, newsletters about economics or technology"""

HAIKU_TOOL = {
    "name": "classify_sender",
    "description": "Classify whether an email sender is a clothing brand",
    "input_schema": {
        "type": "object",
        "properties": {
            "is_clothing": {
                "type": "boolean",
                "description": "True if the sender is primarily a clothing/fashion brand or retailer"
            },
            "is_mixed_sender": {
                "type": "boolean",
                "description": "True if this is a mega-retailer selling many categories (Amazon, Target, Walmart)"
            },
            "reasoning": {
                "type": "string",
                "description": "Brief explanation of the classification (1-2 sentences)"
            }
        },
        "required": ["is_clothing", "is_mixed_sender", "reasoning"]
    }
}


@retry_with_backoff(max_retries=3, base_delay=1.0)
def classify_sender_with_haiku(sender_email, sender_name, sample_subjects,
                               backend="cli", client=None):
    """
    Pass 1: Ask Haiku if this sender is a clothing brand.

    backend="api": Anthropic SDK with tool_use (structured output, requires API key)
    backend="cli": Claude CLI subprocess (works with Claude Max OAuth)
    """
    user_msg = f"""Classify this email sender:

Sender email: {sender_email}
Display name: {sender_name or '(none)'}
Sample subjects from this sender:
{chr(10).join(f'- "{s}"' for s in sample_subjects[:5])}"""

    if backend == "api":
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=256,
            system=HAIKU_SYSTEM_PROMPT,
            tools=[HAIKU_TOOL],
            tool_choice={"type": "tool", "name": "classify_sender"},
            messages=[{"role": "user", "content": user_msg}],
        )

        for block in response.content:
            if block.type == "tool_use":
                cost = (response.usage.input_tokens * 0.80
                        + response.usage.output_tokens * 4.00) / 1_000_000
                return {
                    "is_clothing": block.input["is_clothing"],
                    "is_mixed_sender": block.input.get("is_mixed_sender", False),
                    "reasoning": block.input.get("reasoning", ""),
                    "cost_usd": cost,
                }
        raise ValueError("Haiku did not return tool_use block")

    else:  # cli
        prompt = f"""{HAIKU_SYSTEM_PROMPT}

{user_msg}

Respond with ONLY a JSON object, no markdown fences, no extra text:
{{"is_clothing": true, "is_mixed_sender": false, "reasoning": "brief explanation"}}"""

        result = subprocess.run(
            ["claude", "-p", prompt, "--model", "haiku", "--output-format", "json"],
            capture_output=True, text=True, timeout=30,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Claude CLI failed: {result.stderr.strip()}")

        # Parse CLI JSON envelope
        cli_output = json.loads(result.stdout)
        response_text = cli_output.get("result", "")
        cost_usd = cli_output.get("cost_usd", 0.0)

        # Parse the model's JSON response
        try:
            parsed = json.loads(response_text)
        except json.JSONDecodeError:
            json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
            else:
                raise ValueError(f"Could not parse JSON from response: {response_text[:200]}")

        return {
            "is_clothing": parsed["is_clothing"],
            "is_mixed_sender": parsed.get("is_mixed_sender", False),
            "reasoning": parsed.get("reasoning", ""),
            "cost_usd": cost_usd,
        }


# --- Email-level heuristic (Pass 2) ---

def classify_email_heuristic(subject, has_list_unsubscribe):
    """
    Pass 2: Classify individual email by subject + headers.
    Returns: 'purchase' | 'marketing' | 'account' | 'unknown'

    Note: List-Unsubscribe alone is NOT sufficient to classify as marketing.
    Many purchase emails (shipping, order confirmations) include it for CAN-SPAM compliance.
    Only use it as a marketing signal when purchase/account patterns don't match.
    """
    if PURCHASE_PATTERNS.search(subject):
        return "purchase"
    if ACCOUNT_PATTERNS.search(subject):
        return "account"
    if MARKETING_PATTERNS.search(subject):
        return "marketing"
    # List-Unsubscribe is a weak signal — only use when nothing else matches
    if has_list_unsubscribe and not PURCHASE_PATTERNS.search(subject) and not ACCOUNT_PATTERNS.search(subject):
        return "marketing"
    return "unknown"


# --- Multi-signal voting ---

def get_action_tier(email_category, has_list_unsubscribe, has_purchase_history):
    """
    Combine signals into an action tier.

    Returns: 'auto_label' | 'auto_trash' | 'review' | 'skip'
    """
    if email_category == "purchase":
        return "auto_label"
    if email_category == "marketing" and has_list_unsubscribe:
        return "auto_trash"
    if email_category == "marketing":
        return "review"  # marketing without List-Unsubscribe is less certain
    if email_category == "account":
        return "skip"  # don't touch account/security emails
    return "review"  # unknown → human review


# --- Database ---

def get_db_connection():
    """Get a connection to the classifier database."""
    setup_database()
    return sqlite3.connect(DB_PATH)


def save_sender_classification(conn, sender_email, sender_name, result, run_id,
                                has_list_unsubscribe=False, has_purchase_history=False,
                                sample_subjects=None):
    """Write a single sender classification to DB immediately."""
    conn.execute("""
        INSERT OR REPLACE INTO sender_classifications
        (sender_email, sender_name, is_clothing, is_mixed_sender, confidence,
         reasoning, classification_method, list_unsubscribe_seen,
         has_purchase_history, sample_subjects, run_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        sender_email,
        sender_name,
        result["is_clothing"],
        result.get("is_mixed_sender", False),
        result.get("confidence", 0.0),
        result["reasoning"],
        result.get("method", "haiku"),
        has_list_unsubscribe,
        has_purchase_history,
        json.dumps(sample_subjects or []),
        run_id,
    ))
    conn.commit()


def save_email_classification(conn, email_id, sender, subject, date_str,
                               category, reasoning, action_status="pending"):
    """Write a single email classification to DB."""
    conn.execute("""
        INSERT OR REPLACE INTO classifications
        (email_id, sender, subject, date, category, confidence, reasoning, action_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        email_id, sender, subject, date_str, category, 0.0, reasoning, action_status,
    ))
    conn.commit()


def get_already_classified_senders(conn):
    """Get senders already classified in this DB (for resume support)."""
    cursor = conn.execute("SELECT sender_email FROM sender_classifications")
    return {row[0] for row in cursor.fetchall()}


def update_run_state(conn, run_id, phase, status, total_senders=None, classified_count=None):
    """Update run state for crash recovery."""
    if status == "in_progress":
        conn.execute("""
            INSERT OR REPLACE INTO run_state
            (run_id, phase, status, total_senders, classified_count, started_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (run_id, phase, status, total_senders, classified_count or 0,
              datetime.now().isoformat()))
    else:
        conn.execute("""
            UPDATE run_state
            SET status = ?, classified_count = ?, completed_at = ?
            WHERE run_id = ?
        """, (status, classified_count, datetime.now().isoformat(), run_id))
    conn.commit()


# --- Phase 1: Classify ---

def run_classify(service, limit=None, dry_run=True, backend="cli", client=None):
    """Phase 1: Classify all senders. Zero Gmail actions taken."""
    run_id = str(uuid.uuid4())[:8]
    conn = get_db_connection()

    print("\n📧 Phase 1: Classify Senders")
    print("=" * 60)

    # Load known senders
    personalized_senders = load_personalized_senders()
    if personalized_senders:
        print(f"  Loaded {len(personalized_senders)} known clothing senders")

    # Get all message IDs (paginated)
    print("\n  Fetching all inbox message IDs...")
    all_messages = list_all_message_ids(service, query="in:inbox", max_total=limit)
    print(f"  Found {len(all_messages)} messages")

    # Extract unique senders
    print("\n  Extracting unique senders...")
    senders = extract_unique_senders(service, all_messages)
    print(f"  Found {len(senders)} unique senders")

    # Check which senders are already classified (resume support)
    already_classified = get_already_classified_senders(conn)
    if already_classified:
        print(f"  Skipping {len(already_classified)} already-classified senders")

    # Track stats
    stats = {
        "total_senders": len(senders),
        "known_hits": 0, "haiku_calls": 0, "skipped": 0,
        "clothing_found": 0, "not_clothing": 0, "mixed_skipped": 0,
        "total_cost_usd": 0.0,
    }

    update_run_state(conn, run_id, "classify", "in_progress", total_senders=len(senders))

    # Classify each sender
    print(f"\n  Classifying {len(senders)} senders...")
    print("-" * 60)

    clothing_senders = {}

    for i, (email, info) in enumerate(senders.items()):
        if email in already_classified:
            stats["skipped"] += 1
            continue

        # Try known sender fast path
        known_result = classify_known_sender(email, personalized_senders)
        if known_result:
            save_sender_classification(
                conn, email, info["name"], known_result, run_id,
                has_list_unsubscribe=info["has_list_unsubscribe"],
                sample_subjects=info["sample_subjects"],
            )
            stats["known_hits"] += 1
            if known_result["is_mixed_sender"]:
                # Mixed senders (Amazon, etc.) are logged but skipped for labeling
                stats["mixed_skipped"] += 1
                if (i + 1) % 20 == 0:
                    print(f"  [{i+1}/{len(senders)}] {email} → mixed retailer (skipped)")
            else:
                stats["clothing_found"] += 1
                clothing_senders[email] = info
                if (i + 1) % 20 == 0:
                    print(f"  [{i+1}/{len(senders)}] {email} → known clothing ✓")
            continue

        # Call Haiku
        try:
            result = classify_sender_with_haiku(
                email, info["name"], info["sample_subjects"],
                backend=backend, client=client,
            )
            stats["haiku_calls"] += 1
            stats["total_cost_usd"] += result.get("cost_usd", 0.0)

            result["method"] = "haiku"

            save_sender_classification(
                conn, email, info["name"], result, run_id,
                has_list_unsubscribe=info["has_list_unsubscribe"],
                sample_subjects=info["sample_subjects"],
            )

            if result["is_clothing"]:
                stats["clothing_found"] += 1
                clothing_senders[email] = info
                mixed_tag = " (mixed)" if result["is_mixed_sender"] else ""
                print(f"  [{i+1}/{len(senders)}] {email} → CLOTHING{mixed_tag}: {result['reasoning']}")
            else:
                stats["not_clothing"] += 1
                if (i + 1) % 20 == 0:
                    print(f"  [{i+1}/{len(senders)}] {email} → not clothing")

        except Exception as e:
            print(f"  [{i+1}/{len(senders)}] {email} → ERROR: {e}")
            continue

        update_run_state(conn, run_id, "classify", "in_progress",
                        classified_count=stats["known_hits"] + stats["haiku_calls"])

    update_run_state(conn, run_id, "classify", "completed",
                    classified_count=stats["known_hits"] + stats["haiku_calls"])

    # Pass 2: Classify individual emails from clothing senders
    print(f"\n\n  Pass 2: Classifying individual emails from {len(clothing_senders)} clothing senders...")
    print("-" * 60)

    email_stats = {"purchase": 0, "marketing": 0, "account": 0, "unknown": 0}

    for sender_email, info in clothing_senders.items():
        for msg_id in info["message_ids"]:
            try:
                msg = fetch_message(service, msg_id)
                headers = get_headers_dict(msg)
                subject = headers.get("Subject", "")
                date_str = headers.get("Date", "")
                has_unsub = "List-Unsubscribe" in headers

                category = classify_email_heuristic(subject, has_unsub)
                email_stats[category] += 1

                action = get_action_tier(category, has_unsub, False)

                save_email_classification(
                    conn, msg_id, sender_email, subject, date_str,
                    category if category != "unknown" else "other",
                    f"Heuristic: {category}, List-Unsubscribe: {has_unsub}",
                    action_status="pending",
                )

            except Exception:
                continue

    conn.close()

    # Print summary
    print(f"\n\n{'='*60}")
    print("📊 CLASSIFICATION RESULTS")
    print("=" * 60)
    print(f"\nSender-level (Pass 1):")
    print(f"  Total senders:     {stats['total_senders']}")
    print(f"  Known (fast path): {stats['known_hits']}")
    print(f"  Mixed (skipped):   {stats['mixed_skipped']}")
    print(f"  Haiku API calls:   {stats['haiku_calls']}")
    print(f"  Skipped (cached):  {stats['skipped']}")
    print(f"  → Clothing:        {stats['clothing_found']}")
    print(f"  → Not clothing:    {stats['not_clothing']}")

    print(f"\nEmail-level (Pass 2):")
    print(f"  Purchase:  {email_stats['purchase']}")
    print(f"  Marketing: {email_stats['marketing']}")
    print(f"  Account:   {email_stats['account']}")
    print(f"  Unknown:   {email_stats['unknown']}")

    # Cost
    print(f"\nClaude CLI cost: ${stats['total_cost_usd']:.4f} ({stats['haiku_calls']} calls)")

    if dry_run:
        print("\n🏷️  DRY RUN — no Gmail actions taken. Review results, then run --phase label")

    return stats


# --- Phase 1 (Plan): Search known brands ---

def load_known_brands():
    """Load confirmed clothing brands from file."""
    if not BRANDS_FILE.exists():
        print(f"  Brands file not found: {BRANDS_FILE}")
        return []
    brands = []
    with open(BRANDS_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                brands.append(line)
    return brands


def run_phase1_search(service, dry_run=True):
    """
    Phase 1: Find and classify emails from known clothing brands using Gmail search.

    No LLM needed — just Gmail search per brand + purchase keyword heuristics.
    Much faster than scanning the whole inbox (~30 API calls, under 2 minutes).
    """
    run_id = f"{datetime.now().strftime('%Y-%m-%d')}_{str(uuid.uuid4())[:4]}"
    run_stats = RunStats(run_id, "phase1-search", "all")
    conn = get_db_connection()

    print("\n  Phase 1: Search Known Brands")
    print("=" * 60)

    brands = load_known_brands()
    if not brands:
        print("  No brands found. Add brands to personal/data/email-classifier/clothing_brands.txt")
        conn.close()
        return

    print(f"  Loaded {len(brands)} known clothing brands")

    # Use subject: operator to avoid body-match false positives
    # (marketing footers with "order history" links, "return policy", etc.)
    purchase_keywords = 'subject:(order OR shipped OR tracking OR receipt OR invoice OR return OR refund OR billing OR delivered OR confirmation)'
    marketing_keywords = 'subject:("% off" OR sale OR "new arrivals" OR promo OR "free shipping" OR "limited time" OR "shop now" OR clearance OR "new collection")'

    all_purchase_ids = []
    all_marketing_ids = []
    all_other_ids = []
    brand_stats = {}

    for brand in brands:
        # Quote multi-word brand names for exact from: matching
        from_term = f'from:"{brand}"' if " " in brand else f"from:{brand}"

        # Search for purchase emails from this brand
        purchase_query = f'{from_term} {purchase_keywords}'
        purchase_msgs = list_all_message_ids(service, query=purchase_query)
        run_stats.record_gmail_call()

        # Search for ALL emails from this brand
        all_msgs = list_all_message_ids(service, query=from_term)
        run_stats.record_gmail_call()

        purchase_ids = {m["id"] for m in purchase_msgs}
        all_ids = {m["id"] for m in all_msgs}
        non_purchase_ids = all_ids - purchase_ids

        # For non-purchase emails, check if they match marketing keywords
        marketing_query = f'{from_term} {marketing_keywords}'
        marketing_msgs = list_all_message_ids(service, query=marketing_query)
        run_stats.record_gmail_call()
        marketing_ids = {m["id"] for m in marketing_msgs} - purchase_ids  # exclude purchases
        other_ids = non_purchase_ids - marketing_ids

        all_purchase_ids.extend(purchase_ids)
        all_marketing_ids.extend(marketing_ids)
        all_other_ids.extend(other_ids)

        if purchase_ids or marketing_ids:
            brand_stats[brand] = {
                "purchase": len(purchase_ids),
                "marketing": len(marketing_ids),
                "other": len(other_ids),
                "total": len(all_ids),
            }
            print(f"  {brand:20s} → {len(purchase_ids):3d} purchase, {len(marketing_ids):3d} marketing, {len(other_ids):3d} other")

        # Rate limit between brands
        time.sleep(0.1)

    print(f"\n  Totals:")
    print(f"    Purchase emails:  {len(all_purchase_ids)}")
    print(f"    Marketing emails: {len(all_marketing_ids)}")
    print(f"    Other/unknown:    {len(all_other_ids)}")
    print(f"    Total:            {len(all_purchase_ids) + len(all_marketing_ids) + len(all_other_ids)}")

    if dry_run:
        print(f"\n  DRY RUN — no DB writes or Gmail labels.")
        print(f"  To save to DB: --phase search --execute")
        run_stats.emails_processed = len(all_purchase_ids) + len(all_marketing_ids) + len(all_other_ids)
        run_stats.purchases_found = len(all_purchase_ids)
        run_stats.marketing_found = len(all_marketing_ids)
        run_stats.others_found = len(all_other_ids)
        run_stats.flush_to_db(DB_PATH)
        run_stats.print_summary()
        conn.close()
        return

    # Save classifications to DB
    print(f"\n  Saving to database...")
    saved = 0

    # Fetch headers for purchase emails and save
    for i, msg_id in enumerate(all_purchase_ids):
        try:
            msg = fetch_message(service, msg_id)
            run_stats.record_gmail_call()
            headers = get_headers_dict(msg)
            sender = headers.get("From", "")
            subject = headers.get("Subject", "")
            date_str = headers.get("Date", "")

            save_email_classification(
                conn, msg_id, sender, subject, date_str,
                "purchase", "Phase 1: known brand + purchase keywords",
                action_status="pending",
            )
            saved += 1
        except Exception as e:
            run_stats.record_error()
        if (i + 1) % 50 == 0:
            time.sleep(1.0)
            print(f"    Saved {saved} purchase emails...")

    # Save marketing emails
    for i, msg_id in enumerate(all_marketing_ids):
        try:
            msg = fetch_message(service, msg_id)
            run_stats.record_gmail_call()
            headers = get_headers_dict(msg)
            sender = headers.get("From", "")
            subject = headers.get("Subject", "")
            date_str = headers.get("Date", "")

            save_email_classification(
                conn, msg_id, sender, subject, date_str,
                "marketing", "Phase 1: known brand + marketing keywords",
                action_status="pending",
            )
            saved += 1
        except Exception as e:
            run_stats.record_error()
        if (i + 1) % 50 == 0:
            time.sleep(1.0)

    # Save other/review emails
    for i, msg_id in enumerate(all_other_ids):
        try:
            msg = fetch_message(service, msg_id)
            run_stats.record_gmail_call()
            headers = get_headers_dict(msg)
            sender = headers.get("From", "")
            subject = headers.get("Subject", "")
            date_str = headers.get("Date", "")

            save_email_classification(
                conn, msg_id, sender, subject, date_str,
                "other", "Phase 1: known brand, no keyword match",
                action_status="pending",
            )
            saved += 1
        except Exception as e:
            run_stats.record_error()
        if (i + 1) % 50 == 0:
            time.sleep(1.0)

    conn.close()

    run_stats.emails_processed = saved
    run_stats.purchases_found = len(all_purchase_ids)
    run_stats.marketing_found = len(all_marketing_ids)
    run_stats.others_found = len(all_other_ids)

    print(f"\n  Saved {saved} classifications to DB")
    print(f"  Next: --phase label --batch 5 --execute")

    run_stats.flush_to_db(DB_PATH)
    run_stats.print_summary()


# --- Phase 2: Label ---

def run_label(service, dry_run=True, batch_size=None):
    """
    Phase 2: Apply Gmail labels based on classifications.

    Supports batch progression:
      --batch 5     → label first 5 pending emails (smoke test)
      --batch 25    → label next 25
      --batch 100   → label next 100
      --batch all   → label everything remaining
      (no --batch)  → dry run showing what would be labeled
    """
    run_id = f"{datetime.now().strftime('%Y-%m-%d')}_{str(uuid.uuid4())[:4]}"
    run_stats = RunStats(run_id, "label", batch_size or "dry-run")
    conn = get_db_connection()

    print("\n  Phase 2: Apply Labels")
    print("=" * 60)

    # Get pending classifications
    cursor = conn.execute("""
        SELECT email_id, category, sender, subject FROM classifications
        WHERE action_status = 'pending' AND category IN ('purchase', 'marketing', 'other')
    """)
    rows = cursor.fetchall()

    if not rows:
        print("  No pending classifications to label.")
        conn.close()
        return

    purchases = [(r[0], r[2], r[3]) for r in rows if r[1] == "purchase"]
    marketing = [(r[0], r[2], r[3]) for r in rows if r[1] == "marketing"]
    review = [(r[0], r[2], r[3]) for r in rows if r[1] == "other"]

    total_pending = len(purchases) + len(marketing) + len(review)
    print(f"  Pending: {len(purchases)} purchase, {len(marketing)} marketing, {len(review)} review")
    print(f"  Total pending: {total_pending}")

    if dry_run:
        print(f"\n  DRY RUN — would apply these labels:")
        print(f"    'Clothing/Purchases' → {len(purchases)} emails")
        print(f"    'Clothing/Marketing' → {len(marketing)} emails")
        print(f"    'Clothing/Review'    → {len(review)} emails")
        print(f"\n  To label, run: --phase label --batch 5 --execute")
        conn.close()
        return

    # Apply batch limit
    if batch_size and batch_size != "all":
        limit = int(batch_size)
        # Proportionally slice each category
        total = len(purchases) + len(marketing) + len(review)
        if total > limit:
            ratio = limit / total
            p_limit = max(1, int(len(purchases) * ratio)) if purchases else 0
            m_limit = max(1, int(len(marketing) * ratio)) if marketing else 0
            r_limit = limit - p_limit - m_limit
            purchases = purchases[:p_limit]
            marketing = marketing[:m_limit]
            review = review[:r_limit]
            print(f"\n  Batch limit: {limit} emails")
            print(f"    Purchases: {len(purchases)}, Marketing: {len(marketing)}, Review: {len(review)}")

    # Create labels if needed
    existing_labels = {l["name"]: l["id"] for l in get_labels(service)}
    run_stats.record_gmail_call()

    for label_name in ["Clothing/Purchases", "Clothing/Marketing", "Clothing/Review"]:
        if label_name not in existing_labels:
            result = create_label(service, label_name)
            existing_labels[label_name] = result["id"]
            run_stats.record_gmail_call()
            print(f"  Created label: {label_name}")

    labeled_samples = []  # For between-batch review output

    # Label purchases
    if purchases:
        ids = [p[0] for p in purchases]
        for batch_start in range(0, len(ids), 1000):
            batch = ids[batch_start:batch_start + 1000]
            batch_modify_messages_labels(
                service, batch,
                add_labels=[existing_labels["Clothing/Purchases"]],
            )
            run_stats.record_gmail_call()
        for eid in ids:
            conn.execute("UPDATE classifications SET action_status = 'labeled' WHERE email_id = ?", (eid,))
        run_stats.labels_applied += len(ids)
        run_stats.purchases_found += len(ids)
        for eid, sender, subject in purchases[:3]:
            labeled_samples.append(f'    "...{subject[-50:]}" → Purchase')
        print(f"  Labeled {len(ids)} purchase emails")

    # Label marketing
    if marketing:
        ids = [m[0] for m in marketing]
        for batch_start in range(0, len(ids), 1000):
            batch = ids[batch_start:batch_start + 1000]
            batch_modify_messages_labels(
                service, batch,
                add_labels=[existing_labels["Clothing/Marketing"]],
            )
            run_stats.record_gmail_call()
        for eid in ids:
            conn.execute("UPDATE classifications SET action_status = 'labeled' WHERE email_id = ?", (eid,))
        run_stats.labels_applied += len(ids)
        run_stats.marketing_found += len(ids)
        for eid, sender, subject in marketing[:2]:
            labeled_samples.append(f'    "...{subject[-50:]}" → Marketing')
        print(f"  Labeled {len(ids)} marketing emails")

    # Label review
    if review:
        ids = [r[0] for r in review]
        for batch_start in range(0, len(ids), 1000):
            batch = ids[batch_start:batch_start + 1000]
            batch_modify_messages_labels(
                service, batch,
                add_labels=[existing_labels["Clothing/Review"]],
            )
            run_stats.record_gmail_call()
        for eid in ids:
            conn.execute("UPDATE classifications SET action_status = 'labeled' WHERE email_id = ?", (eid,))
        run_stats.labels_applied += len(ids)
        run_stats.others_found += len(ids)
        print(f"  Labeled {len(ids)} review emails")

    run_stats.emails_processed = run_stats.labels_applied

    conn.commit()
    conn.close()

    # Between-batch review output
    if labeled_samples:
        print(f"\n  Sample of what was labeled:")
        for s in labeled_samples:
            print(s)

    # Remaining count
    remaining = total_pending - run_stats.labels_applied
    if remaining > 0:
        print(f"\n  Remaining: {remaining} emails pending")
        print(f"  Next: Review in Gmail → then run --batch {min(remaining, 100)}")
    else:
        print(f"\n  All pending emails labeled.")

    # Flush stats
    run_stats.flush_to_db(DB_PATH)
    run_stats.print_summary()


# --- Phase 3: Trash ---

def run_trash(service, execute=False, batch_size=None):
    """
    Phase 3: Trash marketing emails.

    Requires --execute flag (dry-run is default).
    Supports batch progression: --batch 5|25|100|all
    Writes pre-trash manifest for recovery with --phase untrash.
    """
    run_id = f"{datetime.now().strftime('%Y-%m-%d')}_{str(uuid.uuid4())[:4]}"
    run_stats = RunStats(run_id, "trash", batch_size or "dry-run")
    conn = get_db_connection()

    print("\n  Phase 3: Trash Marketing Emails")
    print("=" * 60)

    # Get labeled marketing emails
    cursor = conn.execute("""
        SELECT email_id, sender, subject FROM classifications
        WHERE action_status = 'labeled' AND category = 'marketing'
    """)
    rows = cursor.fetchall()

    if not rows:
        print("  No labeled marketing emails to trash.")
        conn.close()
        return

    # Show sender summary
    print(f"\n  {len(rows)} marketing emails ready to trash from:")
    sender_counts = defaultdict(int)
    for _, sender, _ in rows:
        sender_counts[sender] += 1
    for sender, count in sorted(sender_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"    {sender}: {count} emails")
    if len(sender_counts) > 10:
        print(f"    ...and {len(sender_counts) - 10} more senders")

    if not execute:
        print(f"\n  DRY RUN — pass --execute to actually trash emails")
        print(f"  Recommended: --phase trash --batch 5 --execute")
        print("  (Gmail trash auto-deletes after 30 days)")
        conn.close()
        return

    # Apply batch limit
    if batch_size and batch_size != "all":
        limit = int(batch_size)
        rows = rows[:limit]
        print(f"\n  Batch limit: {limit} emails")

    # Safety check: verify no purchase emails in the set
    email_ids_to_trash = [r[0] for r in rows]
    cursor = conn.execute(f"""
        SELECT email_id FROM classifications
        WHERE email_id IN ({','.join('?' * len(email_ids_to_trash))})
        AND category = 'purchase'
    """, email_ids_to_trash)
    purchase_in_trash = cursor.fetchall()
    if purchase_in_trash:
        print(f"\n  SAFETY HALT: {len(purchase_in_trash)} purchase emails found in trash set!")
        print("  This should never happen. Aborting.")
        run_stats.record_error()
        run_stats.flush_to_db(DB_PATH)
        conn.close()
        return

    # Write pre-trash manifest
    manifest_path = DB_PATH.parent / f"trash_manifest_{run_id}.json"
    manifest = [{"email_id": r[0], "sender": r[1], "subject": r[2]} for r in rows]
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"\n  Manifest saved to {manifest_path}")

    # Trash emails
    trashed = 0
    errors = 0
    for i, (email_id, sender, subject) in enumerate(rows):
        try:
            trash_message(service, email_id)
            run_stats.record_gmail_call()
            conn.execute("UPDATE classifications SET action_status = 'trashed' WHERE email_id = ?",
                       (email_id,))
            trashed += 1
        except Exception as e:
            print(f"  Failed to trash {email_id} ({sender}): {e}")
            run_stats.record_error()
            errors += 1

        # Rate limit
        if (i + 1) % 50 == 0:
            time.sleep(1.0)
            conn.commit()
            print(f"  Trashed {trashed}/{len(rows)}...")

        # Automatic halt on high error rate in batch
        if errors > 0 and trashed + errors <= 5:
            # Any error in first 5 = stop
            print(f"\n  HALT: Error in first 5 emails. Stopping for review.")
            break
        if errors > 0 and trashed + errors > 5 and (errors / (trashed + errors)) > 0.05:
            print(f"\n  HALT: Error rate exceeded 5% ({errors}/{trashed + errors}). Stopping.")
            break

    run_stats.emails_trashed = trashed
    run_stats.emails_processed = trashed + errors
    conn.commit()
    conn.close()

    # Show samples
    print(f"\n  Sample of trashed emails:")
    for _, sender, subject in rows[:5]:
        print(f'    "{subject[:60]}" ({sender})')

    remaining = len(cursor.fetchall()) if False else 0  # already consumed
    # Re-query remaining
    conn2 = get_db_connection()
    remaining = conn2.execute("""
        SELECT COUNT(*) FROM classifications
        WHERE action_status = 'labeled' AND category = 'marketing'
    """).fetchone()[0]
    conn2.close()

    if remaining > 0:
        print(f"\n  Remaining: {remaining} marketing emails")
        print(f"  Next: Check Gmail trash → then run --batch {min(remaining, 25)}")
    else:
        print(f"\n  All marketing emails trashed.")

    run_stats.flush_to_db(DB_PATH)
    run_stats.print_summary()


# --- Phase: Untrash (recovery) ---

def run_untrash(service, manifest_file=None):
    """Recover trashed emails from a manifest file."""
    from mcp_gmail.gmail import untrash_message

    manifest_dir = DB_PATH.parent

    if manifest_file:
        manifest_path = Path(manifest_file)
    else:
        # Find most recent manifest
        manifests = sorted(manifest_dir.glob("trash_manifest_*.json"), reverse=True)
        if not manifests:
            print("  No trash manifests found.")
            return
        manifest_path = manifests[0]

    print(f"\n  Untrash from: {manifest_path}")

    with open(manifest_path) as f:
        manifest = json.load(f)

    print(f"  {len(manifest)} emails to untrash")

    recovered = 0
    for item in manifest:
        try:
            untrash_message(service, item["email_id"])
            recovered += 1
        except Exception as e:
            print(f"  Failed to untrash {item['email_id']}: {e}")

    conn = get_db_connection()
    for item in manifest:
        conn.execute(
            "UPDATE classifications SET action_status = 'labeled' WHERE email_id = ?",
            (item["email_id"],)
        )
    conn.commit()
    conn.close()

    print(f"  Recovered {recovered}/{len(manifest)} emails")


# --- Main ---

def main():
    parser = argparse.ArgumentParser(description="Classify clothing emails with Haiku")
    parser.add_argument("--phase", choices=["search", "classify", "label", "trash", "untrash"],
                       default="search", help="Execution phase (search=Phase 1 brand search)")
    parser.add_argument("--dry-run", action="store_true", default=True,
                       help="Dry run (default: true)")
    parser.add_argument("--execute", action="store_true",
                       help="Actually perform actions (overrides --dry-run)")
    parser.add_argument("--limit", type=int, default=None,
                       help="Limit number of messages to process")
    parser.add_argument("--batch", type=str, default=None,
                       help="Batch size for progressive processing: 5, 25, 100, or 'all'")
    parser.add_argument("--backend", choices=["auto", "api", "cli"], default="auto",
                       help="Classification backend: api (Anthropic SDK), cli (Claude CLI), auto (detect)")
    parser.add_argument("--stats", action="store_true",
                       help="Show cumulative usage statistics and exit")
    parser.add_argument("--manifest", type=str, default=None,
                       help="Manifest file for --phase untrash")
    args = parser.parse_args()

    # Stats mode — no Gmail connection needed
    if args.stats:
        print_cumulative_stats()
        return 0

    dry_run = not args.execute

    print("  Haiku Email Classifier")
    print("=" * 60)

    try:
        # Initialize Gmail service
        print("\n  Connecting to Gmail...")
        service = get_gmail_service_instance()
        print("  Connected")

        if args.phase == "search":
            run_phase1_search(service, dry_run=dry_run)

        elif args.phase == "classify":
            # Resolve classification backend
            backend = args.backend
            client = None

            if backend == "auto":
                if HAS_ANTHROPIC_SDK and os.environ.get("ANTHROPIC_API_KEY"):
                    backend = "api"
                elif shutil.which("claude"):
                    backend = "cli"
                else:
                    print("No backend available. Either:")
                    print("   - Set ANTHROPIC_API_KEY and install anthropic package")
                    print("   - Install Claude CLI (claude)")
                    return 1

            if backend == "api":
                if not HAS_ANTHROPIC_SDK:
                    print("anthropic package not installed. Run: pip install anthropic")
                    return 1
                if not os.environ.get("ANTHROPIC_API_KEY"):
                    print("ANTHROPIC_API_KEY not set. Add it to .env or export it.")
                    return 1
                client = anthropic.Anthropic()
                print(f"  Backend: Anthropic SDK (API key)")
            else:
                if not shutil.which("claude"):
                    print("claude CLI not found in PATH.")
                    return 1
                print(f"  Backend: Claude CLI (OAuth)")

            run_classify(service, limit=args.limit, dry_run=dry_run,
                        backend=backend, client=client)

        elif args.phase == "label":
            run_label(service, dry_run=dry_run, batch_size=args.batch)

        elif args.phase == "trash":
            run_trash(service, execute=args.execute, batch_size=args.batch)

        elif args.phase == "untrash":
            run_untrash(service, manifest_file=args.manifest)

    except KeyboardInterrupt:
        print("\n\n  Interrupted. Progress saved to DB — safe to resume.")
        return 1
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
