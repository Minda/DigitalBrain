#!/usr/bin/env python3
"""
Extract unsubscribe links from category:promotions and optionally clean up emails.

Incremental workflow:
1. Query category:promotions for unique senders (sorted by volume)
2. Extract unsubscribe link from ONE email per sender
3. Save to database + markdown audit file
4. Verify save successful
5. Delete all emails from that sender in category:promotions (if not dry-run)

⚠️ PRIVACY: All data stored in personal/ directory.
"""

import sys
import re
import sqlite3
import time
import argparse
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from urllib.parse import urlparse

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from classify_emails_haiku import (
    get_gmail_service_instance,
    list_all_message_ids,
    fetch_message_metadata,
    get_headers_dict,
)

# Attempt BeautifulSoup import (for HTML parsing)
try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False
    print("⚠️  BeautifulSoup not installed. Body parsing disabled. Install with: uv pip install beautifulsoup4")

DB_PATH = Path("personal/data/email-classifier/clothing_emails.db")
AUDIT_PATH = Path("personal/data/email-classifier/unsubscribe_audit.md")


def extract_sender_email(from_header):
    """Extract email address from From header."""
    email_match = re.search(r'<(.+?)>', from_header)
    if email_match:
        return email_match.group(1).lower()
    return from_header.strip().lower()


def extract_sender_name(from_header):
    """Extract sender name from From header."""
    email_match = re.search(r'<(.+?)>', from_header)
    if email_match:
        return from_header[:email_match.start()].strip().strip('"')
    return from_header


def parse_list_unsubscribe_header(header_value):
    """
    Parse List-Unsubscribe header which can contain multiple URLs.

    Format: <mailto:unsub@example.com>, <https://example.com/unsub>
    Returns: {'http': [...], 'mailto': [...]}
    """
    if not header_value:
        return {'http': [], 'mailto': []}

    # Extract URLs within < > brackets
    urls = re.findall(r'<([^>]+)>', header_value)

    http_links = []
    mailto_links = []

    for url in urls:
        url = url.strip()
        if url.startswith('http'):
            http_links.append(url)
        elif url.startswith('mailto:'):
            mailto_links.append(url)

    return {'http': http_links, 'mailto': mailto_links}


def extract_unsubscribe_from_body(body_html):
    """Extract unsubscribe links from HTML body."""
    if not HAS_BS4 or not body_html:
        return []

    try:
        soup = BeautifulSoup(body_html, 'html.parser')
        links = []

        # Find links with "unsubscribe" in text or URL
        for a_tag in soup.find_all('a', href=True):
            text = a_tag.get_text().lower()
            href = a_tag['href']

            if any(keyword in text for keyword in ['unsubscribe', 'opt out', 'remove me', 'email preferences']):
                if href.startswith('http'):
                    links.append(href)
            elif any(keyword in href.lower() for keyword in ['unsubscribe', 'optout', 'opt-out']):
                if href.startswith('http'):
                    links.append(href)

        return links
    except Exception as e:
        print(f"  ⚠️  Error parsing HTML body: {e}")
        return []


def get_message_body_html(service, message_id):
    """Fetch HTML body from message."""
    try:
        message = service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()

        payload = message.get('payload', {})

        # Check if multipart
        if 'parts' in payload:
            for part in payload['parts']:
                if part.get('mimeType') == 'text/html':
                    data = part.get('body', {}).get('data', '')
                    if data:
                        import base64
                        return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        else:
            # Single part message
            if payload.get('mimeType') == 'text/html':
                data = payload.get('body', {}).get('data', '')
                if data:
                    import base64
                    return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

        return None
    except Exception as e:
        print(f"  ⚠️  Error fetching body: {e}")
        return None


def query_promotions_senders(service, limit=None):
    """
    Query category:promotions and group by sender.

    Returns: List of (sender_email, sender_name, email_count, message_ids)
    """
    print("Querying category:promotions...")
    messages = list_all_message_ids(service, query="category:promotions", max_total=10000)
    print(f"  Found {len(messages)} promotional emails\n")

    if not messages:
        return []

    # Group by sender
    senders = defaultdict(lambda: {
        'name': '',
        'message_ids': [],
        'sample_subject': ''
    })

    print(f"Grouping by sender (metadata-only)...")
    for i, msg_ref in enumerate(messages):
        if i > 0 and i % 100 == 0:
            print(f"  Processed {i}/{len(messages)} messages, {len(senders)} unique senders")

        if i > 0 and i % 50 == 0:
            time.sleep(0.5)  # Rate limiting

        try:
            msg = fetch_message_metadata(service, msg_ref['id'], headers=['From', 'Subject'])
            headers = get_headers_dict(msg)

            from_header = headers.get('From', '')
            subject = headers.get('Subject', '')

            sender_email = extract_sender_email(from_header)
            sender_name = extract_sender_name(from_header)

            if sender_email not in senders:
                senders[sender_email]['name'] = sender_name
                senders[sender_email]['sample_subject'] = subject

            senders[sender_email]['message_ids'].append(msg_ref['id'])
        except Exception:
            continue

    # Convert to sorted list
    sender_list = [
        (email, info['name'], len(info['message_ids']), info['message_ids'], info['sample_subject'])
        for email, info in senders.items()
    ]

    # Sort by volume descending
    sender_list.sort(key=lambda x: x[2], reverse=True)

    # Apply limit
    if limit:
        sender_list = sender_list[:limit]

    print(f"\nFound {len(senders)} unique senders")
    if limit:
        print(f"Processing top {len(sender_list)} senders (--limit {limit})\n")

    return sender_list


def extract_unsubscribe_links(service, sender_email, message_id):
    """
    Extract all unsubscribe links from a message.

    Returns: {
        'http': [...],
        'mailto': [...],
        'has_one_click': bool
    }
    """
    # Fetch message with headers
    msg = service.users().messages().get(
        userId='me',
        id=message_id,
        format='full',
        metadataHeaders=['List-Unsubscribe', 'List-Unsubscribe-Post']
    ).execute()

    headers = get_headers_dict(msg)

    # Parse List-Unsubscribe header
    list_unsub = headers.get('List-Unsubscribe', '')
    links = parse_list_unsubscribe_header(list_unsub)

    # Check for RFC 8058 one-click support
    list_unsub_post = headers.get('List-Unsubscribe-Post', '')
    has_one_click = 'One-Click' in list_unsub_post

    # Try to extract from body HTML if no header links
    if not links['http'] and not links['mailto']:
        body_html = get_message_body_html(service, message_id)
        body_links = extract_unsubscribe_from_body(body_html)
        if body_links:
            links['http'].extend(body_links)

    return {
        'http': links['http'],
        'mailto': links['mailto'],
        'has_one_click': has_one_click
    }


def save_to_database(sender_email, links, source_email_id):
    """Save unsubscribe links to database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if sender already exists
    existing = cursor.execute(
        "SELECT id FROM sender_unsubscribe WHERE sender_email = ?",
        (sender_email,)
    ).fetchone()

    if existing:
        print(f"  ℹ️  Sender already in database (skipping)")
        conn.close()
        return False

    # Insert new record
    http_url = links['http'][0] if links['http'] else None
    mailto_url = links['mailto'][0] if links['mailto'] else None

    cursor.execute("""
        INSERT INTO sender_unsubscribe
        (sender_email, unsubscribe_url, unsubscribe_mailto, has_one_click, source_email_id, status)
        VALUES (?, ?, ?, ?, ?, 'pending')
    """, (sender_email, http_url, mailto_url, links['has_one_click'], source_email_id))

    conn.commit()
    conn.close()

    return True


def verify_database_save(sender_email):
    """Verify that sender was saved to database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    result = cursor.execute(
        "SELECT id FROM sender_unsubscribe WHERE sender_email = ?",
        (sender_email,)
    ).fetchone()

    conn.close()
    return result is not None


def write_to_audit_file(sender_email, sender_name, email_count, links, sample_subject, source_email_id, dry_run=False, deleted_count=None):
    """Write extraction details to markdown audit file."""
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Read existing content or create new
    if AUDIT_PATH.exists():
        with open(AUDIT_PATH, 'r') as f:
            content = f.read()
    else:
        content = "# Unsubscribe Link Extraction & Cleanup Audit\n\n"
        content += f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        content += "## Summary\n"
        content += "- Total senders processed: 0\n"
        content += "- Total unsubscribe links extracted: 0\n"
        content += "- Total emails deleted: 0\n\n"
        content += "---\n\n"

    # Update summary if it exists
    if "Total senders processed:" in content:
        # Extract current counts
        match = re.search(r'Total senders processed: (\d+)', content)
        if match:
            current_senders = int(match.group(1))
            content = re.sub(r'Total senders processed: \d+', f'Total senders processed: {current_senders + 1}', content)

        match = re.search(r'Total unsubscribe links extracted: (\d+)', content)
        if match:
            current_links = int(match.group(1))
            has_links = 1 if (links['http'] or links['mailto']) else 0
            content = re.sub(r'Total unsubscribe links extracted: \d+', f'Total unsubscribe links extracted: {current_links + has_links}', content)

        if deleted_count is not None:
            match = re.search(r'Total emails deleted: (\d+)', content)
            if match:
                current_deleted = int(match.group(1))
                content = re.sub(r'Total emails deleted: \d+', f'Total emails deleted: {current_deleted + deleted_count}', content)

    # Update last updated timestamp
    content = re.sub(r'Last updated: .*\n', f'Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n', content)
    if 'Last updated:' not in content:
        content = content.replace('Created:', f'Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\nCreated:')

    # Add sender entry
    sender_entry = f"\n## {sender_name} <{sender_email}>\n"
    sender_entry += f"- **Email Count**: {email_count:,} emails in category:promotions\n"

    if links['http']:
        sender_entry += f"- **Unsubscribe URL**: {links['http'][0]}\n"
        if len(links['http']) > 1:
            sender_entry += f"  - Additional URLs: {len(links['http']) - 1}\n"
    else:
        sender_entry += "- **Unsubscribe URL**: Not found\n"

    if links['mailto']:
        sender_entry += f"- **Unsubscribe Mailto**: {links['mailto'][0]}\n"
    else:
        sender_entry += "- **Unsubscribe Mailto**: Not found\n"

    sender_entry += f"- **One-Click Support**: {'Yes' if links['has_one_click'] else 'No'}\n"
    sender_entry += f"- **Source Email ID**: {source_email_id}\n"
    sender_entry += f"- **Sample Subject**: {sample_subject[:80]}\n"
    sender_entry += f"- **Extracted**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

    if dry_run:
        sender_entry += f"- **Status**: 🧪 DRY RUN - Would delete {email_count:,} emails\n"
    elif deleted_count is not None:
        sender_entry += f"- **Status**: ✅ Deleted {deleted_count:,} emails\n"
        sender_entry += f"- **Deleted**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    else:
        sender_entry += f"- **Status**: ⏳ Pending deletion\n"

    sender_entry += "\n---\n"

    content += sender_entry

    with open(AUDIT_PATH, 'w') as f:
        f.write(content)


def delete_promotional_emails(service, sender_email, dry_run=False):
    """Delete all emails from sender in category:promotions."""
    if dry_run:
        return 0

    # Query for all emails from this sender in promotions
    query = f'category:promotions from:{sender_email}'

    try:
        messages = list_all_message_ids(service, query=query, max_total=10000)

        if not messages:
            return 0

        print(f"  Deleting {len(messages)} emails from category:promotions...")

        # Batch delete (Gmail API supports up to 1000 per batch)
        batch_size = 1000
        deleted_count = 0

        for i in range(0, len(messages), batch_size):
            batch = messages[i:i+batch_size]
            message_ids = [msg['id'] for msg in batch]

            service.users().messages().batchDelete(
                userId='me',
                body={'ids': message_ids}
            ).execute()

            deleted_count += len(message_ids)
            time.sleep(0.5)  # Rate limiting

        return deleted_count

    except Exception as e:
        print(f"  ❌ Error deleting emails: {e}")
        return 0


def process_sender(service, sender_email, sender_name, email_count, message_ids, sample_subject, dry_run=False):
    """Process one sender: extract links, save to DB, optionally delete emails."""
    print(f"\n{'='*80}")
    print(f"Processing: {sender_name} <{sender_email}>")
    print(f"  Email count: {email_count:,}")

    # Extract unsubscribe links from most recent email
    source_email_id = message_ids[0]

    try:
        links = extract_unsubscribe_links(service, sender_email, source_email_id)

        if links['http']:
            print(f"  ✓ Found HTTP link: {links['http'][0]}")
        if links['mailto']:
            print(f"  ✓ Found mailto link: {links['mailto'][0]}")
        if links['has_one_click']:
            print(f"  ✓ Supports RFC 8058 one-click unsubscribe")

        if not links['http'] and not links['mailto']:
            print(f"  ⚠️  No unsubscribe links found")
            return False

        # Save to database
        saved = save_to_database(sender_email, links, source_email_id)

        if not saved:
            return False  # Already in database

        print(f"  ✓ Saved to database")

        # Verify save
        if not verify_database_save(sender_email):
            print(f"  ❌ Database verification failed!")
            return False

        print(f"  ✓ Verified database save")

        # Write to audit file (before deletion)
        write_to_audit_file(sender_email, sender_name, email_count, links, sample_subject, source_email_id, dry_run=dry_run)
        print(f"  ✓ Updated audit file")

        # Delete emails
        if dry_run:
            print(f"\n  🧪 DRY RUN - Would delete {email_count:,} emails from category:promotions")
        else:
            deleted_count = delete_promotional_emails(service, sender_email, dry_run=False)
            if deleted_count > 0:
                print(f"  ✓ Deleted {deleted_count:,} emails from category:promotions")
                # Update audit file with deletion confirmation
                write_to_audit_file(sender_email, sender_name, email_count, links, sample_subject, source_email_id, dry_run=False, deleted_count=deleted_count)
            else:
                print(f"  ⚠️  No emails found to delete (may have been deleted already)")

        return True

    except Exception as e:
        print(f"  ❌ Error processing sender: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Extract unsubscribe links from category:promotions and optionally clean up emails'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=1,
        help='Number of senders to process (default: 1)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Extract and save links but do NOT delete emails'
    )

    args = parser.parse_args()

    print("=" * 80)
    print("Unsubscribe Link Extraction & Cleanup")
    print("=" * 80)
    print(f"Mode: {'🧪 DRY RUN (no deletion)' if args.dry_run else '⚠️  REAL MODE (will delete emails)'}")
    print(f"Limit: {args.limit} sender(s)")
    print(f"Database: {DB_PATH}")
    print(f"Audit file: {AUDIT_PATH}")
    print("=" * 80)
    print()

    # Connect to Gmail
    print("Connecting to Gmail...")
    service = get_gmail_service_instance()
    print("  ✓ Connected\n")

    # Query promotions senders
    senders = query_promotions_senders(service, limit=args.limit)

    if not senders:
        print("No senders found in category:promotions")
        return

    # Process each sender
    processed = 0
    extracted = 0

    for sender_email, sender_name, email_count, message_ids, sample_subject in senders:
        success = process_sender(service, sender_email, sender_name, email_count, message_ids, sample_subject, dry_run=args.dry_run)
        processed += 1
        if success:
            extracted += 1

    # Summary
    print(f"\n{'='*80}")
    print("Summary")
    print("=" * 80)
    print(f"Senders processed: {processed}")
    print(f"Links extracted: {extracted}")
    if args.dry_run:
        print(f"Mode: DRY RUN - No emails deleted")
    else:
        print(f"Mode: REAL - Emails deleted from category:promotions")
    print(f"\nAudit file: {AUDIT_PATH}")
    print(f"Database: {DB_PATH}")
    print("=" * 80)


if __name__ == "__main__":
    main()
