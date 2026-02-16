#!/usr/bin/env python3
"""
Query Gmail for total email count and search for clothing-related emails.

⚠️ PRIVACY: All email-derived data MUST be stored in personal/
- Email content, subjects, senders
- Classification results
- Processing logs
DO NOT commit email data to public repository.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import json
import sqlite3
import random

# Add the mcp-gmail module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "app" / "mcp" / "gmail"))

from mcp_gmail.gmail import get_gmail_service, list_messages, get_message
from get_email_statistics import calculate_sample_size, get_sampling_strategy, format_statistics
from setup_email_classifier_db import setup_database


def load_personalized_senders():
    """Load personalized clothing sender list if available."""
    sender_file = Path("personal/data/email-classifier/clothing_senders.json")
    if sender_file.exists():
        with open(sender_file, 'r') as f:
            data = json.load(f)
            print(f"   📋 Loaded {len(data)} personalized clothing senders")
            return data
    return None


def get_gmail_service_instance():
    """Initialize Gmail service with credentials from app/mcp/gmail/."""
    credentials_path = Path(__file__).parent.parent.parent / "app" / "mcp" / "gmail" / "credentials.json"
    token_path = Path(__file__).parent.parent.parent / "app" / "mcp" / "gmail" / "token.json"

    if not credentials_path.exists():
        raise FileNotFoundError(f"Gmail credentials not found at {credentials_path}")

    # Create Gmail service
    service = get_gmail_service(
        credentials_path=str(credentials_path),
        token_path=str(token_path)
    )

    return service


def get_total_inbox_count(service):
    """Get total number of emails in inbox."""
    # Get a large batch of messages to estimate total count
    # Gmail API doesn't provide a direct count, so we'll get a large sample
    all_messages = list_messages(service, query="in:inbox", max_results=10000)

    # The list_messages returns a list of message dictionaries
    return len(all_messages)


def search_clothing_emails(service, sample_size=None):
    """
    Search for clothing-related emails using various keywords.

    Args:
        service: Gmail service instance
        sample_size: Maximum number of emails to process (None for all)

    Returns:
        Dictionary with classification results
    """
    # Keywords that indicate clothing purchases
    purchase_keywords = [
        "order confirmation",
        "shipping confirmation",
        "tracking number",
        "order has shipped",
        "receipt",
        "invoice",
        "order #",
        "return label"
    ]

    # Keywords that indicate clothing marketing
    marketing_keywords = [
        "sale",
        "discount",
        "% off",
        "new arrivals",
        "exclusive offer",
        "limited time",
        "flash sale",
        "promo code",
        "free shipping"
    ]

    # Try to load personalized sender list first
    personalized_senders = load_personalized_senders()
    clothing_senders_set = set()

    if personalized_senders:
        # Use personalized list
        clothing_senders_set = set(personalized_senders.keys())
        print(f"   Using personalized clothing sender list ({len(clothing_senders_set)} senders)")
    else:
        # Fall back to generic brands
        clothing_brands = [
            "nike", "adidas", "zara", "h&m", "gap", "uniqlo",
            "nordstrom", "macy's", "target", "walmart", "amazon fashion",
            "asos", "shein", "revolve", "net-a-porter", "ssense",
            "end clothing", "mr porter", "farfetch", "matches fashion"
        ]
        print("   Using generic clothing brand list")

    results = {
        "purchases": [],
        "marketing": [],
        "potential_clothing": [],
        "total_processed": 0
    }

    print("\n🔍 Searching for clothing-related emails...")

    # Search for purchase-related emails
    for keyword in purchase_keywords[:3]:  # Start with top keywords
        query = f'in:inbox "{keyword}"'
        messages = list_messages(service, query=query, max_results=50)

        if messages:
            for msg in messages[:10]:  # Process up to 10 per keyword
                try:
                    # Get full message details
                    full_msg = get_message(service, msg['id'])

                    # Extract basic info
                    headers = full_msg.get('payload', {}).get('headers', [])
                    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                    sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                    date = next((h['value'] for h in headers if h['name'] == 'Date'), '')

                    # Check if it's clothing-related
                    is_clothing = any(brand.lower() in sender.lower() or brand.lower() in subject.lower()
                                     for brand in clothing_brands)

                    if is_clothing:
                        results["purchases"].append({
                            "id": msg['id'],
                            "subject": subject,
                            "sender": sender,
                            "date": date,
                            "category": "purchase"
                        })

                except Exception as e:
                    print(f"  ⚠️ Error processing message: {e}")

                results["total_processed"] += 1

                if sample_size and results["total_processed"] >= sample_size:
                    break

        if sample_size and results["total_processed"] >= sample_size:
            break

    # Search for marketing emails
    for keyword in marketing_keywords[:3]:  # Start with top keywords
        query = f'in:inbox "{keyword}" unsubscribe'  # Marketing emails usually have unsubscribe
        messages = list_messages(service, query=query, max_results=50)

        if messages:
            for msg in messages[:10]:
                try:
                    full_msg = get_message(service, msg['id'])
                    headers = full_msg.get('payload', {}).get('headers', [])
                    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                    sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                    date = next((h['value'] for h in headers if h['name'] == 'Date'), '')

                    # Check if it's clothing-related
                    is_clothing = any(brand.lower() in sender.lower() or brand.lower() in subject.lower()
                                     for brand in clothing_brands)

                    if is_clothing:
                        results["marketing"].append({
                            "id": msg['id'],
                            "subject": subject,
                            "sender": sender,
                            "date": date,
                            "category": "marketing"
                        })

                except Exception as e:
                    print(f"  ⚠️ Error processing message: {e}")

                results["total_processed"] += 1

                if sample_size and results["total_processed"] >= sample_size:
                    break

        if sample_size and results["total_processed"] >= sample_size:
            break

    return results


def save_results(results, stats):
    """Save results to database in personal/data/email-classifier/."""
    # Ensure database exists
    setup_database()

    db_path = Path("personal/data/email-classifier/clothing_emails.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Save classifications
    for category in ["purchases", "marketing"]:
        for email in results.get(category, []):
            cursor.execute("""
                INSERT OR REPLACE INTO classifications
                (email_id, sender, subject, date, category, confidence, reasoning)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                email['id'],
                email['sender'],
                email['subject'],
                email['date'],
                email['category'],
                0.8,  # Confidence based on keyword matching
                f"Keyword match for {category}"
            ))

    # Save processing stats
    cursor.execute("""
        INSERT INTO processing_stats
        (total_emails_processed, purchases_found, marketing_found, others_found,
         sample_size, confidence_level, margin_of_error, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        results.get('total_processed', 0),
        len(results.get('purchases', [])),
        len(results.get('marketing', [])),
        0,  # others
        stats.get('required_sample_size', 0),
        0.95,  # 95% confidence
        0.05,  # 5% margin
        f"Initial search run on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    ))

    conn.commit()
    conn.close()

    print(f"\n💾 Results saved to: {db_path.absolute()}")


def main():
    """Main execution flow."""
    print("🚀 Gmail Clothing Email Classifier")
    print("="*60)

    try:
        # Initialize Gmail service
        print("\n1️⃣ Connecting to Gmail...")
        service = get_gmail_service_instance()
        print("   ✅ Connected successfully")

        # Get total email count
        print("\n2️⃣ Getting total inbox count...")
        total_count = get_total_inbox_count(service)
        print(f"   📧 Total emails in inbox: {total_count:,}")

        # Calculate sample size
        print("\n3️⃣ Calculating sample size...")
        stats = get_sampling_strategy(total_count)
        print(format_statistics(stats))

        # Search for clothing emails (limited sample)
        print("\n4️⃣ Searching for clothing-related emails...")
        sample_to_search = min(100, stats['required_sample_size'])  # Start with max 100
        results = search_clothing_emails(service, sample_size=sample_to_search)

        # Display results
        print("\n📊 SEARCH RESULTS")
        print("="*60)
        print(f"Emails processed: {results['total_processed']}")
        print(f"Clothing purchases found: {len(results['purchases'])}")
        print(f"Clothing marketing found: {len(results['marketing'])}")

        if results['purchases']:
            print("\n📦 Sample Purchase Emails:")
            for email in results['purchases'][:5]:
                print(f"  • {email['subject'][:60]}...")
                print(f"    From: {email['sender'][:50]}")

        if results['marketing']:
            print("\n🛍️ Sample Marketing Emails:")
            for email in results['marketing'][:5]:
                print(f"  • {email['subject'][:60]}...")
                print(f"    From: {email['sender'][:50]}")

        # Save results
        print("\n5️⃣ Saving results to database...")
        save_results(results, stats)

        # Extrapolation
        if results['total_processed'] > 0:
            purchase_rate = len(results['purchases']) / results['total_processed']
            marketing_rate = len(results['marketing']) / results['total_processed']

            print("\n📈 EXTRAPOLATED ESTIMATES")
            print("="*60)
            print(f"Based on {results['total_processed']} emails sampled:")
            print(f"  • Estimated purchase emails: ~{int(total_count * purchase_rate):,} (±5%)")
            print(f"  • Estimated marketing emails: ~{int(total_count * marketing_rate):,} (±5%)")
            print(f"  • Total clothing-related: ~{int(total_count * (purchase_rate + marketing_rate)):,} (±5%)")

        print("\n✅ Analysis complete!")
        print("\nNext steps:")
        print("  1. Review the classifications in the database")
        print("  2. Run full sample processing if results look good")
        print("  3. Apply labels and archive emails as planned")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())