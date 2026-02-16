#!/usr/bin/env python3
"""
Scan Gmail category:promotions for unique senders.
Saves results to promotion_senders table in the email classifier DB.

⚠️ PRIVACY: Output goes to personal/ directory.
"""

import sys
import re
import sqlite3
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from classify_emails_haiku import (
    get_gmail_service_instance, list_all_message_ids,
    fetch_message_metadata, get_headers_dict,
)
from setup_email_classifier_db import setup_database

DB_PATH = Path("personal/data/email-classifier/clothing_emails.db")


def save_senders_to_db(senders):
    """Write unique senders to the promotion_senders table."""
    setup_database()
    conn = sqlite3.connect(DB_PATH)
    now = datetime.now().isoformat()
    inserted = 0
    updated = 0

    for email, info in senders.items():
        existing = conn.execute(
            "SELECT email_count FROM promotion_senders WHERE sender_email = ?",
            (email,)
        ).fetchone()

        if existing:
            conn.execute("""
                UPDATE promotion_senders
                SET email_count = ?, sender_name = ?, most_recent_subject = ?, updated_at = ?
                WHERE sender_email = ?
            """, (info["count"], info["name"], info["most_recent_subject"], now, email))
            updated += 1
        else:
            conn.execute("""
                INSERT INTO promotion_senders
                (sender_email, sender_name, email_count, most_recent_subject, source, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'promotions_scan', ?, ?)
            """, (email, info["name"], info["count"], info["most_recent_subject"], now, now))
            inserted += 1

    conn.commit()
    conn.close()
    return inserted, updated


def scan_promotions(limit=5000):
    print("Connecting to Gmail...")
    service = get_gmail_service_instance()
    print("Connected.\n")

    print("Fetching category:promotions message IDs...")
    messages = list_all_message_ids(service, query="category:promotions",
                                    max_total=limit)
    print(f"Found {len(messages)} promotion emails (limit={limit})\n")

    if not messages:
        return

    senders = {}
    last_new_count = 0

    print(f"Extracting unique senders (metadata-only)...")
    for i, msg_ref in enumerate(messages):
        if i % 100 == 0 and i > 0:
            new_this_batch = len(senders) - last_new_count
            print(f"  {i}/{len(messages)} messages, {len(senders)} unique senders (+{new_this_batch} last 100)")
            # Early stop: no new senders in last 100 messages
            if i >= 500 and new_this_batch == 0:
                print(f"  No new senders in last 100 — stopping early.")
                break
            last_new_count = len(senders)

        if i > 0 and i % 50 == 0:
            time.sleep(1.0)

        try:
            msg = fetch_message_metadata(service, msg_ref["id"],
                                         headers=['From', 'Subject'])
            headers = get_headers_dict(msg)
            sender_raw = headers.get("From", "")
            subject = headers.get("Subject", "")

            email_match = re.search(r'<(.+?)>', sender_raw)
            if email_match:
                sender_email = email_match.group(1).lower()
                sender_name = sender_raw[:email_match.start()].strip().strip('"')
            else:
                sender_email = sender_raw.strip().lower()
                sender_name = sender_email

            if sender_email not in senders:
                senders[sender_email] = {
                    "name": sender_name,
                    "count": 0,
                    "most_recent_subject": subject,
                }
            senders[sender_email]["count"] += 1

        except Exception:
            pass

    sorted_senders = sorted(senders.items(), key=lambda x: -x[1]["count"])

    print(f"\n{'Sender':<50} {'Count':>5}  Most Recent Subject")
    print("-" * 110)
    for email, info in sorted_senders:
        name = info["name"][:35] if info["name"] else email[:35]
        subj = info["most_recent_subject"][:45] if info["most_recent_subject"] else ""
        print(f"{name:<50} {info['count']:>5}  {subj}")

    # Save to DB
    inserted, updated = save_senders_to_db(senders)
    print(f"\n{len(senders)} unique senders → DB (promotion_senders): {inserted} new, {updated} updated")
    print(f"Scanned {min(i+1, len(messages))} of {len(messages)} messages")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5000)
    args = parser.parse_args()
    scan_promotions(limit=args.limit)
