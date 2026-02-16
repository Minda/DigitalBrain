#!/usr/bin/env python3
"""
Quick scan for clothing senders with improved filtering.
More efficient version that processes in smaller batches.
"""

import sys
from pathlib import Path
from collections import defaultdict
import re

# Add the mcp-gmail module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "app" / "mcp" / "gmail"))
from mcp_gmail.gmail import get_gmail_service, list_messages, get_message

def get_service():
    """Get Gmail service."""
    return get_gmail_service(
        credentials_path=str(Path(__file__).parent.parent.parent / "app" / "mcp" / "gmail" / "credentials.json"),
        token_path=str(Path(__file__).parent.parent.parent / "app" / "mcp" / "gmail" / "token.json")
    )

def scan_for_clothing():
    """Scan inbox for potential clothing senders."""

    # Known clothing brands
    known_brands = [
        'nike', 'adidas', 'puma', 'reebok', 'under armour',
        'gap', 'old navy', 'banana republic', 'zara', 'h&m', 'uniqlo',
        'nordstrom', 'macys', 'bloomingdale', 'saks',
        'anthropologie', 'urban outfitters', 'free people',
        'lululemon', 'athleta', 'fabletics', 'outdoor voices',
        'everlane', 'reformation', 'marine layer', 'rothys', 'allbirds',
        'patagonia', 'north face', 'columbia', 'rei',
        'asos', 'revolve', 'net-a-porter', 'ssense',
        'thredup', 'poshmark', 'depop', 'vinted',
        'stitch fix', 'rent the runway', 'trunk club',
        'ann taylor', 'j.crew', 'madewell', 'kate spade',
        'coach', 'michael kors', 'tory burch'
    ]

    # Exclusions
    platforms = ['slack.com', 'instagram.com', 'nextdoor.com', 'quora.com', 'zoom.us']
    finance_terms = ['nerdwallet', 'economics', 'stocks', 'invest', 'financial']

    print("🔍 Quick Clothing Sender Scan")
    print("="*50)

    service = get_service()
    print("✓ Connected to Gmail\n")

    print("Searching for known clothing brands...")
    found_brands = []

    # Search for each known brand
    for brand in known_brands:
        query = f'from:{brand} in:inbox'
        messages = list_messages(service, query=query, max_results=1)
        if messages:
            found_brands.append(brand)
            print(f"  ✓ {brand}")

    print(f"\n📊 Found {len(found_brands)} clothing brands in your inbox")

    # Now get a sample of all senders to find new ones
    print("\nScanning for additional potential clothing senders...")

    messages = list_messages(service, query="in:inbox", max_results=200)
    senders = defaultdict(int)

    for i, msg in enumerate(messages):
        if i % 20 == 0:
            print(f"  Processed {i}/{len(messages)} messages...")

        try:
            full_msg = get_message(service, msg['id'])
            headers = full_msg.get('payload', {}).get('headers', [])
            sender = next((h['value'] for h in headers if h['name'] == 'From'), '')

            # Extract email
            if '<' in sender:
                email = sender.split('<')[1].split('>')[0].lower()
            else:
                email = sender.lower()

            # Skip platforms
            if any(platform in email for platform in platforms):
                continue

            # Skip finance
            if any(term in email.lower() for term in finance_terms):
                continue

            senders[email] += 1
        except:
            pass

    print(f"\n✅ Scanned {len(messages)} messages")
    print(f"   Found {len(senders)} unique senders")

    # Filter for potential clothing
    clothing_keywords = ['fashion', 'apparel', 'clothing', 'wear', 'style', 'shop', 'boutique']
    potential_new = []

    for email, count in senders.items():
        # Skip if already found
        if any(brand in email for brand in found_brands):
            continue

        # Check for clothing indicators
        if any(kw in email for kw in clothing_keywords):
            potential_new.append((email, count))

    if potential_new:
        print(f"\n🆕 Potential new clothing senders:")
        for email, count in sorted(potential_new, key=lambda x: x[1], reverse=True)[:10]:
            print(f"  • {email} ({count} emails)")

    # Save results
    output_path = Path(".claude/skills/email-clothing-classifier/quick_scan_results.txt")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write("CONFIRMED CLOTHING BRANDS\n")
        f.write("="*30 + "\n")
        for brand in sorted(found_brands):
            f.write(f"{brand}\n")

        if potential_new:
            f.write("\n\nPOTENTIAL NEW SENDERS\n")
            f.write("="*30 + "\n")
            for email, count in sorted(potential_new, key=lambda x: x[1], reverse=True):
                f.write(f"{email} ({count} emails)\n")

    print(f"\n💾 Results saved to: {output_path}")

    return found_brands, potential_new

if __name__ == "__main__":
    found, potential = scan_for_clothing()
    print(f"\n✨ Summary: {len(found)} confirmed brands, {len(potential)} potential new senders")