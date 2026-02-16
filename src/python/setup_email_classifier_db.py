#!/usr/bin/env python3
"""
Setup SQLite database for email classifier.

⚠️ PRIVACY: All email-derived data MUST be stored in personal/
- Email content, subjects, senders
- Classification results
- Unsubscribe links
- Processing logs
DO NOT commit email data to public repository.
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path


def setup_database(verbose=False):
    """Create the email classifier database with required tables."""
    # Ensure database is in personal directory (private repo)
    db_path = Path("personal/data/email-classifier/clothing_emails.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Table for email classifications
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS classifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_id TEXT UNIQUE NOT NULL,
            sender TEXT NOT NULL,
            subject TEXT NOT NULL,
            date DATETIME NOT NULL,
            category TEXT NOT NULL CHECK(category IN ('purchase', 'marketing', 'other')),
            confidence REAL CHECK(confidence >= 0 AND confidence <= 1),
            reasoning TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Drop legacy marketing_emails table (was empty, replaced by sender_unsubscribe)
    cursor.execute("DROP TABLE IF EXISTS marketing_emails")

    # Table for all unique promotion senders (from category:promotions scan)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS promotion_senders (
            sender_email TEXT PRIMARY KEY,
            sender_name TEXT,
            email_count INTEGER DEFAULT 0,
            most_recent_subject TEXT,
            source TEXT DEFAULT 'promotions_scan',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table for unsubscribe links per sender (multiple rows per sender allowed)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sender_unsubscribe (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_email TEXT NOT NULL,
            unsubscribe_url TEXT,
            unsubscribe_mailto TEXT,
            has_one_click BOOLEAN DEFAULT FALSE,
            source_email_id TEXT,
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'clicked', 'success', 'failed')),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Drop legacy unsubscribe_log (was empty, had FK to dropped marketing_emails)
    cursor.execute("DROP TABLE IF EXISTS unsubscribe_log")

    # Table for unsubscribe attempts log
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS unsubscribe_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            sender_email TEXT NOT NULL,
            unsubscribe_id INTEGER,
            link TEXT NOT NULL,
            method TEXT CHECK(method IN ('click', 'mailto', 'one_click', 'manual')),
            result TEXT CHECK(result IN ('success', 'failed', 'pending')),
            response_message TEXT,
            error_message TEXT,
            FOREIGN KEY (unsubscribe_id) REFERENCES sender_unsubscribe(id)
        )
    """)

    # Table for processing statistics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processing_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            total_emails_processed INTEGER,
            purchases_found INTEGER,
            marketing_found INTEGER,
            others_found INTEGER,
            labels_applied INTEGER,
            emails_archived INTEGER,
            unsubscribe_links_extracted INTEGER,
            sample_size INTEGER,
            confidence_level REAL,
            margin_of_error REAL,
            notes TEXT
        )
    """)

    # Table for sender-level classifications (Haiku classifier)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sender_classifications (
            sender_email TEXT PRIMARY KEY,
            sender_name TEXT,
            is_clothing BOOLEAN NOT NULL,
            is_mixed_sender BOOLEAN DEFAULT FALSE,
            confidence REAL CHECK(confidence >= 0 AND confidence <= 1),
            reasoning TEXT,
            classification_method TEXT CHECK(classification_method IN ('known', 'haiku', 'manual')),
            list_unsubscribe_seen BOOLEAN DEFAULT FALSE,
            has_purchase_history BOOLEAN DEFAULT FALSE,
            sample_subjects TEXT,
            run_id TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table for tracking run state (crash recovery)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS run_state (
            run_id TEXT PRIMARY KEY,
            phase TEXT NOT NULL CHECK(phase IN ('classify', 'label', 'trash')),
            status TEXT NOT NULL CHECK(status IN ('in_progress', 'completed', 'failed')),
            total_senders INTEGER,
            classified_count INTEGER DEFAULT 0,
            started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            completed_at DATETIME
        )
    """)

    # Add action_status to classifications if not present
    try:
        cursor.execute("ALTER TABLE classifications ADD COLUMN action_status TEXT DEFAULT 'pending'")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Add usage tracking columns to processing_stats
    for col_def in [
        "haiku_calls INTEGER DEFAULT 0",
        "haiku_cost_usd REAL DEFAULT 0.0",
        "gmail_api_calls INTEGER DEFAULT 0",
        "errors INTEGER DEFAULT 0",
        "wall_time_seconds REAL",
        "batch_size TEXT",
        "phase TEXT",
        "run_id TEXT",
    ]:
        try:
            cursor.execute(f"ALTER TABLE processing_stats ADD COLUMN {col_def}")
        except sqlite3.OperationalError:
            pass  # Column already exists

    # Create indexes for better query performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_classifications_category ON classifications(category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_classifications_date ON classifications(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_promo_senders_count ON promotion_senders(email_count)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sender_unsub_email ON sender_unsubscribe(sender_email)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sender_unsub_status ON sender_unsubscribe(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_unsubscribe_result ON unsubscribe_log(result)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sender_class_clothing ON sender_classifications(is_clothing)")

    conn.commit()
    conn.close()

    if verbose:
        print(f"Database created successfully at: {db_path.absolute()}")
        print("\nTables created:")
        print("  - classifications: Track all email classifications")
        print("  - sender_classifications: Sender-level classifications (Haiku)")
        print("  - promotion_senders: All unique senders from category:promotions")
        print("  - sender_unsubscribe: Unsubscribe links per sender (multiple per sender)")
        print("  - unsubscribe_log: Log all unsubscribe attempts")
        print("  - processing_stats: Track statistics for each processing run")
        print("  - run_state: Track classifier run progress (crash recovery)")
        print("\n  Remember: This database contains personal email data.")
        print("    It is stored in personal/ which is a private repository.")


if __name__ == "__main__":
    setup_database(verbose=True)