#!/usr/bin/env python3
"""
Discover and categorize clothing-related email senders.

This script:
1. Fetches all unique senders from Gmail inbox
2. Identifies potential clothing brands using heuristics
3. Allows interactive review and categorization
4. Saves personalized clothing sender list

⚠️ PRIVACY: Sender data is stored in personal/ directory only.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json
import re
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple

# Add the mcp-gmail module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "app" / "mcp" / "gmail"))

from mcp_gmail.gmail import get_gmail_service, list_messages, get_message


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


def extract_all_senders(service, max_emails=2000):
    """
    Extract all unique senders from inbox.

    Returns:
        Dict with sender info: {email: {"name": str, "count": int, "subjects": list}}
    """
    print(f"\n📧 Fetching up to {max_emails:,} emails to analyze senders...")

    # Get messages from inbox
    messages = list_messages(service, query="in:inbox", max_results=max_emails)

    senders = defaultdict(lambda: {"name": "", "count": 0, "subjects": []})

    print(f"   Found {len(messages):,} messages. Extracting senders...")

    for i, msg in enumerate(messages):
        if i % 100 == 0 and i > 0:
            print(f"   Processed {i:,} messages...")

        try:
            # Get message details
            full_msg = get_message(service, msg['id'])
            headers = full_msg.get('payload', {}).get('headers', [])

            # Extract sender and subject
            sender_raw = next((h['value'] for h in headers if h['name'] == 'From'), '')
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')

            # Parse sender email and name
            email_match = re.search(r'<(.+?)>', sender_raw)
            if email_match:
                email = email_match.group(1).lower()
                name = sender_raw[:sender_raw.index('<')].strip().strip('"')
            else:
                email = sender_raw.lower().strip()
                name = ""

            # Update sender info
            senders[email]["count"] += 1
            if name and not senders[email]["name"]:
                senders[email]["name"] = name
            if subject and len(senders[email]["subjects"]) < 5:  # Keep sample subjects
                senders[email]["subjects"].append(subject[:80])

        except Exception as e:
            # Skip problematic messages
            continue

    print(f"\n✅ Found {len(senders)} unique senders from {len(messages)} emails")

    return dict(senders)


def check_sender_purchase_history(service, sender_email: str) -> Dict:
    """
    Check if a sender has ever sent purchase-related emails.

    Returns:
        Dict with purchase indicators found
    """
    purchase_indicators = {
        "strong": [
            '"order confirmation"',
            '"shipping confirmation"',
            '"tracking number"',
            '"order has shipped"',
            '"order #"',
            '"order number"',
            '"invoice"',
            '"receipt"',
            '"your order"',
            '"order details"'
        ],
        "medium": [
            '"has been shipped"',
            '"on its way"',
            '"delivered"',
            '"return label"',
            '"refund"',
            '"exchange"'
        ]
    }

    results = {
        "has_purchases": False,
        "purchase_count": 0,
        "sample_subjects": []
    }

    # Search for strong purchase indicators from this sender
    for indicator in purchase_indicators["strong"][:5]:  # Check top 5
        query = f'from:{sender_email} {indicator}'
        messages = list_messages(service, query=query, max_results=3)

        if messages:
            results["has_purchases"] = True
            results["purchase_count"] += len(messages)

            # Get a sample subject
            try:
                msg = get_message(service, messages[0]['id'])
                headers = msg.get('payload', {}).get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
                if subject:
                    results["sample_subjects"].append(subject[:100])
            except:
                pass

            break  # Found purchase evidence, no need to check more

    return results


def identify_potential_clothing_senders(senders: Dict) -> Dict[str, List[str]]:
    """
    Identify potential clothing-related senders using heuristics.

    Returns:
        Dict with categories: {
            "likely_clothing": [],
            "maybe_clothing": [],
            "likely_not_clothing": []
        }
    """

    # Keywords that strongly suggest clothing
    clothing_keywords = [
        'fashion', 'apparel', 'clothing', 'wear', 'style', 'boutique',
        'closet', 'wardrobe', 'outfit', 'dress', 'shirt', 'shoes',
        'jeans', 'pants', 'jacket', 'coat', 'athletic', 'sports',
        'designer', 'luxury', 'vintage', 'thrift', 'retail'
    ]

    # Known clothing brand patterns
    brand_patterns = [
        'nike', 'adidas', 'puma', 'reebok', 'under armour', 'champion',
        'gap', 'oldnavy', 'banana', 'zara', 'h&m', 'hm.com', 'uniqlo',
        'forever21', 'forever 21', 'urban outfitters', 'anthropologie',
        'nordstrom', 'macys', 'macy\'s', 'bloomingdale', 'saks', 'barneys',
        'target', 'walmart', 'kohls', 'kohl\'s', 'jcpenney', 'jc penney',
        'asos', 'boohoo', 'shein', 'zaful', 'romwe', 'fashionnova',
        'revolve', 'net-a-porter', 'ssense', 'farfetch', 'matches',
        'end clothing', 'mr porter', 'yoox', 'gilt', 'rue la la',
        'stitch fix', 'trunk club', 'rent the runway', 'thredup',
        'poshmark', 'mercari', 'depop', 'vinted', 'grailed',
        'patagonia', 'north face', 'columbia', 'arc\'teryx', 'outdoor',
        'lululemon', 'athleta', 'fabletics', 'gymshark', 'alo yoga',
        'victoria', 'pink', 'aerie', 'savage', 'skims', 'everlane',
        'reformation', 'allbirds', 'rothy', 'bombas', 'brooks',
        'vans', 'converse', 'new balance', 'asics', 'saucony',
        'ralph lauren', 'tommy', 'calvin klein', 'michael kors',
        'coach', 'kate spade', 'tory burch', 'rebecca minkoff',
        'gucci', 'prada', 'louis vuitton', 'chanel', 'hermes',
        'burberry', 'balenciaga', 'bottega', 'versace', 'armani'
    ]

    # Keywords that suggest NOT clothing
    non_clothing_keywords = [
        'bank', 'insurance', 'financial', 'news', 'media', 'software',
        'cloud', 'hosting', 'domain', 'food', 'restaurant', 'grocery',
        'pharmacy', 'health', 'medical', 'travel', 'airline', 'hotel',
        'car', 'auto', 'real estate', 'mortgage', 'education', 'school'
    ]

    categorized = {
        "likely_clothing": [],
        "maybe_clothing": [],
        "likely_not_clothing": []
    }

    for email, info in senders.items():
        name = info.get("name", "").lower()
        subjects_text = " ".join(info.get("subjects", [])).lower()
        combined_text = f"{email} {name} {subjects_text}"

        # Check for strong clothing indicators
        is_clothing_brand = any(brand in combined_text for brand in brand_patterns)
        has_clothing_keywords = sum(1 for kw in clothing_keywords if kw in combined_text) >= 2
        has_non_clothing = any(kw in combined_text for kw in non_clothing_keywords)

        # Categorize
        if is_clothing_brand or has_clothing_keywords:
            categorized["likely_clothing"].append(email)
        elif not has_non_clothing and any(kw in combined_text for kw in clothing_keywords):
            categorized["maybe_clothing"].append(email)
        else:
            categorized["likely_not_clothing"].append(email)

    return categorized


def interactive_review(service, senders: Dict, categorized: Dict[str, List[str]]) -> Dict[str, str]:
    """
    Interactive review process for user to confirm clothing senders.
    Now includes purchase history checking.

    Returns:
        Dict of {email: category} for confirmed clothing senders
    """
    confirmed = {}

    print("\n" + "="*60)
    print("🔍 SENDER REVIEW - LIKELY CLOTHING BRANDS")
    print("="*60)
    print("\nThese senders appear to be clothing-related.")
    print("We'll check if they've sent purchase confirmations.")
    print("\nOptions: Enter=confirm, 'n'=skip, 'm'=marketing only, 'p'=purchases, 'q'=quit\n")

    # Process likely clothing senders with purchase check
    for i, email in enumerate(categorized["likely_clothing"][:50]):  # Review top 50
        info = senders[email]
        print(f"\n📧 [{i+1}/{min(50, len(categorized['likely_clothing']))}] {email}")
        if info["name"]:
            print(f"   Name: {info['name']}")
        print(f"   Total emails: {info['count']}")

        # Check purchase history
        print("   🔍 Checking for purchase emails...", end=" ")
        purchase_info = check_sender_purchase_history(service, email)

        if purchase_info["has_purchases"]:
            print(f"✅ Found {purchase_info['purchase_count']} purchase emails!")
            if purchase_info["sample_subjects"]:
                print(f"   Purchase example: \"{purchase_info['sample_subjects'][0][:60]}...\"")
            suggested = "p"
        else:
            print("📣 No purchases found (likely marketing only)")
            suggested = "m"

        # Show sample subjects
        if info["subjects"]:
            print("   Recent subjects:")
            for subj in info["subjects"][:2]:
                print(f"     • {subj}")

        response = input(f"   Confirm? [Y/n/m/p/q] (suggested: {suggested}): ").lower().strip()

        if response == 'q':
            break
        elif response == 'n':
            continue
        elif response == 'm':
            confirmed[email] = "marketing"
        elif response == 'p':
            confirmed[email] = "purchase"
        else:  # Default Yes
            confirmed[email] = "clothing"

    # Quick review of maybe category
    if categorized["maybe_clothing"]:
        print("\n" + "="*60)
        print("🤔 MAYBE CLOTHING - QUICK REVIEW")
        print("="*60)
        print("\nThese might be clothing-related. Review if needed.\n")

        for email in categorized["maybe_clothing"][:20]:
            info = senders[email]
            print(f"• {email} ({info['count']} emails)")
            if info["name"]:
                print(f"  Name: {info['name']}")

        print("\nAdd any of these? Enter email addresses separated by commas (or press Enter to skip):")
        additions = input().strip()
        if additions:
            for email in additions.split(','):
                email = email.strip()
                if email in senders:
                    confirmed[email] = "clothing"

    return confirmed


def save_clothing_senders(confirmed: Dict[str, str], senders: Dict):
    """Save confirmed clothing senders to personal directory."""

    # Prepare data for saving
    clothing_senders = {}
    for email, category in confirmed.items():
        info = senders.get(email, {})
        clothing_senders[email] = {
            "name": info.get("name", ""),
            "category": category,
            "email_count": info.get("count", 0),
            "sample_subjects": info.get("subjects", [])[:3],
            "confirmed_date": datetime.now().isoformat(),
            "auto_detected": True
        }

    # Save to personal directory
    output_dir = Path("personal/data/email-classifier")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "clothing_senders.json"

    # Load existing if present
    existing = {}
    if output_file.exists():
        with open(output_file, 'r') as f:
            existing = json.load(f)

    # Merge with new data
    existing.update(clothing_senders)

    # Save updated list
    with open(output_file, 'w') as f:
        json.dump(existing, f, indent=2)

    print(f"\n💾 Saved {len(clothing_senders)} clothing senders to: {output_file}")

    # Also save a simple list for easy use
    simple_list = list(clothing_senders.keys())
    simple_file = output_dir / "clothing_senders_list.txt"
    with open(simple_file, 'w') as f:
        f.write('\n'.join(sorted(simple_list)))

    print(f"📝 Simple list saved to: {simple_file}")

    return output_file


def generate_summary_stats(senders: Dict, confirmed: Dict[str, str]):
    """Generate summary statistics."""

    print("\n" + "="*60)
    print("📊 SUMMARY STATISTICS")
    print("="*60)

    total_senders = len(senders)
    total_emails = sum(s["count"] for s in senders.values())

    clothing_senders = [e for e, cat in confirmed.items() if cat in ["clothing", "marketing", "purchase"]]
    clothing_emails = sum(senders[e]["count"] for e in clothing_senders if e in senders)

    marketing_senders = [e for e, cat in confirmed.items() if cat == "marketing"]
    marketing_emails = sum(senders[e]["count"] for e in marketing_senders if e in senders)

    purchase_senders = [e for e, cat in confirmed.items() if cat == "purchase"]
    purchase_emails = sum(senders[e]["count"] for e in purchase_senders if e in senders)

    print(f"\nTotal unique senders: {total_senders:,}")
    print(f"Total emails analyzed: {total_emails:,}")

    print(f"\nClothing-related senders: {len(clothing_senders)} ({len(clothing_senders)/total_senders*100:.1f}%)")
    print(f"Clothing-related emails: ~{clothing_emails:,} ({clothing_emails/total_emails*100:.1f}%)")

    print(f"\nBreakdown:")
    print(f"  • Marketing senders: {len(marketing_senders)}")
    print(f"  • Purchase senders: {len(purchase_senders)}")
    print(f"  • General clothing: {len(clothing_senders) - len(marketing_senders) - len(purchase_senders)}")

    # Top senders by volume
    if clothing_senders:
        print(f"\nTop 5 clothing senders by volume:")
        top_senders = sorted(
            [(e, senders[e]["count"]) for e in clothing_senders if e in senders],
            key=lambda x: x[1],
            reverse=True
        )[:5]

        for email, count in top_senders:
            name = senders[email].get("name", "")
            print(f"  • {name or email}: {count} emails")


def main():
    """Main execution flow."""
    print("🚀 Gmail Clothing Sender Discovery Tool")
    print("="*60)

    try:
        # Initialize Gmail service
        print("\n1️⃣ Connecting to Gmail...")
        service = get_gmail_service_instance()
        print("   ✅ Connected successfully")

        # Extract all senders
        print("\n2️⃣ Extracting unique senders...")
        senders = extract_all_senders(service, max_emails=1000)

        # Categorize potential clothing senders
        print("\n3️⃣ Identifying potential clothing brands...")
        categorized = identify_potential_clothing_senders(senders)

        print(f"   • Likely clothing: {len(categorized['likely_clothing'])}")
        print(f"   • Maybe clothing: {len(categorized['maybe_clothing'])}")
        print(f"   • Likely not clothing: {len(categorized['likely_not_clothing'])}")

        # Interactive review
        print("\n4️⃣ Starting interactive review...")
        confirmed = interactive_review(service, senders, categorized)

        if confirmed:
            # Save results
            print("\n5️⃣ Saving confirmed clothing senders...")
            output_file = save_clothing_senders(confirmed, senders)

            # Generate stats
            generate_summary_stats(senders, confirmed)

            print("\n✅ Discovery complete!")
            print(f"\nYour personalized clothing sender list has been saved.")
            print(f"The main classifier script can now use this list for better accuracy.")
        else:
            print("\n⚠️ No clothing senders confirmed. Run again to build your list.")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())