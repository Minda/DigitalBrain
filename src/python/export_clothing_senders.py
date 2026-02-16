#!/usr/bin/env python3
"""
Export all potential clothing senders to a markdown file for manual review.

This script:
1. Fetches all unique senders from Gmail
2. Identifies potential clothing brands
3. Checks purchase history for each
4. Exports to a clean markdown file for easy editing

The output file can be manually edited to remove non-clothing brands.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json
import re
from collections import defaultdict
from typing import Dict, List, Tuple

# Add the mcp-gmail module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "app" / "mcp" / "gmail"))

from mcp_gmail.gmail import get_gmail_service, list_messages, get_message


def get_gmail_service_instance():
    """Initialize Gmail service with credentials from app/mcp/gmail/."""
    credentials_path = Path(__file__).parent.parent.parent / "app" / "mcp" / "gmail" / "credentials.json"
    token_path = Path(__file__).parent.parent.parent / "app" / "mcp" / "gmail" / "token.json"

    if not credentials_path.exists():
        raise FileNotFoundError(f"Gmail credentials not found at {credentials_path}")

    service = get_gmail_service(
        credentials_path=str(credentials_path),
        token_path=str(token_path)
    )

    return service


def extract_brand_name(email: str, sender_name: str = "") -> str:
    """
    Extract a clean brand name from email address and sender name.

    Examples:
    - "NAADAM <noreply@naadam.co>" -> "naadam"
    - "orders@nike.com" -> "nike"
    - "Gap Factory <email@e.gapfactory.com>" -> "gap factory"
    """
    # Clean the email address
    email = email.lower().strip()

    # Skip platform-specific patterns
    if 'nextdoor.com' in email:
        return None  # Don't extract brand from Nextdoor emails
    if 'slack.com' in email or 'instagram.com' in email:
        return None  # Don't extract from social platforms

    # Try to get brand from sender name first (often cleaner)
    if sender_name:
        # Remove common suffixes
        clean_name = sender_name.lower()

        # Skip if it contains neighborhood/location patterns
        if any(term in clean_name for term in ['neighbor', 'free items', 'your area', 'community']):
            return None

        clean_name = re.sub(r'\b(store|shop|online|.com|inc|llc|ltd|co|corp|company)\b', '', clean_name)
        clean_name = re.sub(r'[^\w\s-]', '', clean_name)  # Remove special chars except spaces and hyphens
        clean_name = ' '.join(clean_name.split())  # Normalize whitespace
        if clean_name and len(clean_name) > 2:
            return clean_name

    # Extract domain from email
    if '@' in email:
        domain = email.split('@')[1]
        # Remove common email subdomains
        domain = re.sub(r'^(email|mail|newsletter|notify|noreply|orders|support|info|hello|contact)\.', '', domain)
        domain = re.sub(r'^[a-z]\d*\.', '', domain)  # Remove single letter subdomains like "e."

        # Get the main part of domain (before .com, .net, etc)
        brand = domain.split('.')[0]

        # Clean up
        brand = re.sub(r'[^\w-]', '', brand)

        # Handle special cases
        if brand in ['gmail', 'yahoo', 'hotmail', 'outlook', 'aol']:
            # Try to get from the part before @
            local_part = email.split('@')[0]
            if not any(x in local_part for x in ['noreply', 'donotreply', 'no-reply']):
                brand = local_part.split('.')[0]
                brand = re.sub(r'[^\w-]', '', brand)

        return brand.lower()

    return email  # Fallback to full email


def extract_all_senders(service, max_emails=3000):
    """Extract all unique senders from inbox."""
    print(f"\n📧 Fetching up to {max_emails:,} emails to analyze senders...")

    messages = list_messages(service, query="in:inbox", max_results=max_emails)
    senders = defaultdict(lambda: {"name": "", "count": 0, "domains": set()})

    print(f"   Found {len(messages):,} messages. Extracting senders...")

    for i, msg in enumerate(messages):
        if i % 100 == 0 and i > 0:
            print(f"   Processed {i:,} messages...")

        try:
            full_msg = get_message(service, msg['id'])
            headers = full_msg.get('payload', {}).get('headers', [])

            sender_raw = next((h['value'] for h in headers if h['name'] == 'From'), '')

            # Parse sender email and name
            email_match = re.search(r'<(.+?)>', sender_raw)
            if email_match:
                email = email_match.group(1).lower()
                name = sender_raw[:sender_raw.index('<')].strip().strip('"')
            else:
                email = sender_raw.lower().strip()
                name = ""

            # Store by email
            senders[email]["count"] += 1
            if name and not senders[email]["name"]:
                senders[email]["name"] = name

            # Track domain
            if '@' in email:
                domain = email.split('@')[1]
                senders[email]["domains"].add(domain)

        except Exception as e:
            continue

    print(f"\n✅ Found {len(senders)} unique senders")
    return dict(senders)


def check_purchase_history_batch(service, email: str) -> bool:
    """Quick check if sender has ever sent purchase emails."""
    # Quick check with just one strong indicator
    query = f'from:{email} ("order confirmation" OR "shipping confirmation" OR "tracking number")'
    messages = list_messages(service, query=query, max_results=1)
    return len(messages) > 0


def identify_clothing_senders(senders: Dict) -> List[Tuple[str, Dict]]:
    """Identify potential clothing-related senders with improved filtering."""

    # Extended clothing keywords
    clothing_keywords = [
        'fashion', 'apparel', 'clothing', 'wear', 'style', 'boutique',
        'closet', 'wardrobe', 'outfit', 'dress', 'shirt', 'shoe',
        'jean', 'pant', 'jacket', 'coat', 'athletic', 'sport',
        'designer', 'luxury', 'vintage', 'thrift', 'retail',
        'mens', 'womens', 'kids', 'baby', 'maternity',
        'accessories', 'jewelry', 'handbag', 'wallet', 'belt',
        'underwear', 'lingerie', 'swimwear', 'activewear', 'loungewear',
        'formal', 'casual', 'streetwear', 'sustainable', 'eco'
    ]

    # Platform-specific exclusions (these are platforms, not brands)
    platform_exclusions = [
        'nextdoor.com', 'slack.com', 'instagram.com', 'zoom.us', 'quora.com',
        'facebook.com', 'twitter.com', 'linkedin.com', 'pinterest.com',
        'youtube.com', 'tiktok.com', 'snapchat.com', 'whatsapp.com',
        'discord.com', 'telegram.org', 'reddit.com', 'medium.com',
        'substack.com', 'ghost.io', 'mailchimp.com', 'constantcontact.com'
    ]

    # Finance/Economics newsletter indicators
    finance_indicators = [
        'nerdwallet', 'wallet' + 'hub', 'financial', 'economics', 'econom',
        'invest', 'trading', 'stocks', 'market' + 'watch', 'market' + 'nerd',
        'crypto', 'bitcoin', 'forex', 'banking', 'mortgage', 'loan',
        'credit' + 'card', 'insurance', 'mint.com', 'personalcapital',
        'robinhood', 'etrade', 'fidelity', 'vanguard', 'schwab'
    ]

    # Non-clothing marketplace indicators
    non_clothing_marketplace = [
        'notion', 'wordpress', 'shopify' + 'apps', 'chrome' + 'web',
        'app' + 'store', 'play' + 'store', 'software', 'digital',
        'template', 'plugin', 'extension', 'theme', 'font',
        'graphic', 'stock' + 'photo', 'creative' + 'market',
        'envato', 'themeforest', 'codecanyon', 'graphicriver'
    ]

    # Location/neighborhood service patterns
    neighborhood_patterns = [
        'neighbor', 'neighbourhood', 'community', 'local', 'nearby',
        'in your area', 'free items', 'garage sale', 'yard sale',
        'estate sale', 'moving sale', 'block party'
    ]

    # Organization/Foundation exclusions
    organization_indicators = [
        'foundation', 'institute', 'association', 'society', 'council',
        'committee', 'organization', '.org', '.edu', '.gov',
        'nonprofit', 'charity', 'donate', 'fundrais'
    ]

    # Travel exclusions
    travel_indicators = [
        'airline', 'airways', 'flight', 'hotel', 'resort', 'cruise',
        'travel', 'booking', 'expedia', 'kayak', 'trivago',
        'airbnb', 'vrbo', 'marriott', 'hilton', 'hyatt',
        'jetblue', 'united', 'american' + 'airlines', 'delta',
        'southwest', 'spirit', 'frontier', 'alaska' + 'air'
    ]

    # Known brand patterns (extended list)
    brand_patterns = [
        # Athletic
        'nike', 'adidas', 'puma', 'reebok', 'under armour', 'champion',
        'new balance', 'asics', 'saucony', 'brooks', 'hoka', 'salomon',
        'patagonia', 'north face', 'columbia', 'arcteryx', 'outdoor voices',
        'lululemon', 'athleta', 'fabletics', 'gymshark', 'alo yoga', 'girlfriend',

        # Fast Fashion
        'zara', 'h&m', 'hm.com', 'uniqlo', 'forever21', 'forever 21',
        'shein', 'boohoo', 'asos', 'zaful', 'romwe', 'fashion nova',
        'missguided', 'prettylittlething', 'nasty gal', 'dolls kill',

        # Department Stores
        'nordstrom', 'macys', "macy's", 'bloomingdale', 'saks', 'barneys',
        'neiman marcus', 'bergdorf', 'lord & taylor', 'jcpenney', 'jc penney',
        'kohls', "kohl's", 'dillards', 'belk', 'von maur',

        # Gap Inc Family
        'gap', 'oldnavy', 'old navy', 'banana republic', 'athleta', 'hill city',

        # Specialty Retail
        'anthropologie', 'urban outfitters', 'free people', 'madewell',
        'j.crew', 'jcrew', 'ann taylor', 'loft', 'white house black market',
        'chicos', 'talbots', 'lands end', 'll bean', 'llbean', 'eddie bauer',

        # Target/Walmart Fashion
        'target', 'walmart', 'amazon fashion', 'amazon essentials',

        # Luxury/Designer
        'gucci', 'prada', 'louis vuitton', 'chanel', 'hermes', 'burberry',
        'balenciaga', 'bottega', 'versace', 'armani', 'fendi', 'dior',
        'saint laurent', 'ysl', 'valentino', 'givenchy', 'celine',
        'ralph lauren', 'tommy hilfiger', 'calvin klein', 'michael kors',
        'coach', 'kate spade', 'tory burch', 'rebecca minkoff', 'marc jacobs',

        # Online Luxury
        'net-a-porter', 'ssense', 'farfetch', 'matchesfashion', 'mytheresa',
        'moda operandi', 'bergdorf', '24s', 'luisaviaroma', 'selfridges',
        'end clothing', 'mr porter', 'yoox', 'gilt', 'rue la la', 'hautelook',

        # Shoes
        'footlocker', 'foot locker', 'finish line', 'champs', 'dsw',
        'famous footwear', 'payless', 'aldo', 'steve madden', 'vans',
        'converse', 'dr martens', 'doc martens', 'ugg', 'birkenstock',
        'allbirds', 'rothys', "rothy's", 'tieks', 'toms', 'sketchers',

        # Underwear/Intimates
        'victoria secret', "victoria's secret", 'pink', 'aerie',
        'savage x fenty', 'skims', 'thirdlove', 'true&co', 'meundies',
        'bombas', 'stance', 'pair of thieves', 'tommy john', 'knix',

        # Subscription Boxes
        'stitch fix', 'stitchfix', 'trunk club', 'rent the runway',
        'le tote', 'gwynnie bee', 'dia&co', 'frank and oak', 'menlo club',

        # Resale/Secondhand
        'poshmark', 'mercari', 'depop', 'vinted', 'grailed', 'stockx',
        'goat', 'stadium goods', 'therealreal', 'vestiaire', 'rebag',
        'thredup', 'thred up', 'buffalo exchange', 'crossroads trading',

        # Direct to Consumer
        'everlane', 'reformation', 'outdoor voices', 'glossier',
        'warby parker', 'bonobos', 'untuckit', 'marine layer', 'faherty',
        'outerknown', 'taylor stitch', 'pact', 'kotn', 'tentree',

        # International
        'uniqlo', 'muji', 'cos', 'arket', '& other stories', 'weekday',
        'monki', 'topshop', 'topman', 'river island', 'next', 'marks spencer'
    ]

    potential_clothing = []

    for email, info in senders.items():
        name = info.get("name", "").lower()
        email_lower = email.lower()
        combined = f"{email_lower} {name}"

        # EXCLUSION CHECKS (in order of specificity)

        # 1. Check for platform exclusions (highest priority)
        if any(platform in email_lower for platform in platform_exclusions):
            continue

        # 2. Check for finance/economics newsletters
        if any(indicator in combined for indicator in finance_indicators):
            continue

        # 3. Check for non-clothing marketplaces
        if 'marketplace' in combined or 'market' in combined:
            # Check if it's a non-clothing marketplace
            if any(indicator in combined for indicator in non_clothing_marketplace):
                continue
            # Check if it's NOT a clothing-specific marketplace
            if not any(brand in combined for brand in brand_patterns):
                # Generic marketplace without clothing brand = skip
                continue

        # 4. Check for neighborhood/location services
        if any(pattern in combined for pattern in neighborhood_patterns):
            # Special case: if "free items" or "neighbors" appears, likely Nextdoor
            if 'free items' in combined or 'neighbor' in combined:
                continue

        # 5. Check for organizations/foundations
        if any(indicator in combined for indicator in organization_indicators):
            # Exception: some clothing brands have "foundation" in charitable arms
            if not any(brand in combined for brand in brand_patterns):
                continue

        # 6. Check for travel services
        if any(indicator in combined for indicator in travel_indicators):
            continue

        # 7. Additional context-aware checks
        # If email contains "ux", "research", "agentic" - likely tech/newsletter
        if any(term in combined for term in ['ux research', 'agentic', 'api', 'developer']):
            continue

        # Check for clothing indicators
        has_brand = any(brand in combined for brand in brand_patterns)
        has_keywords = sum(1 for kw in clothing_keywords if kw in combined) >= 1

        # Require stronger evidence if certain words present
        if 'market' in combined and not has_brand:
            # If "market" is present but no known brand, require 2+ clothing keywords
            has_keywords = sum(1 for kw in clothing_keywords if kw in combined) >= 2

        if has_brand or has_keywords:
            potential_clothing.append((email, info))

    return potential_clothing


def export_to_markdown(service, clothing_senders: List[Tuple[str, Dict]], all_senders: Dict):
    """Export clothing senders to a markdown file for review."""

    output_path = Path(".claude/skills/email-clothing-classifier/potential_clothing_senders.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n📝 Checking purchase history for {len(clothing_senders)} potential clothing senders...")
    print("   This may take a minute...")

    # Group by brand name and check purchase history
    brands = {}

    for i, (email, info) in enumerate(clothing_senders):
        if i % 10 == 0 and i > 0:
            print(f"   Checked {i}/{len(clothing_senders)} senders...")

        brand_name = extract_brand_name(email, info.get("name", ""))

        # Skip if brand name extraction returned None (filtered platforms)
        if brand_name is None:
            continue

        # Check for purchases
        has_purchases = check_purchase_history_batch(service, email)

        if brand_name not in brands:
            brands[brand_name] = {
                "emails": [],
                "total_count": 0,
                "has_purchases": False
            }

        brands[brand_name]["emails"].append({
            "address": email,
            "sender_name": info.get("name", ""),
            "count": info.get("count", 0),
            "has_purchases": has_purchases
        })
        brands[brand_name]["total_count"] += info.get("count", 0)
        if has_purchases:
            brands[brand_name]["has_purchases"] = True

    # Sort brands by total email count
    sorted_brands = sorted(brands.items(), key=lambda x: x[1]["total_count"], reverse=True)

    # Write to markdown
    with open(output_path, 'w') as f:
        f.write("# Potential Clothing Senders\n\n")
        f.write(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n")
        f.write("**Instructions:** Delete any lines that are NOT clothing brands. ")
        f.write("The remaining lines will be used as your personalized clothing sender list.\n\n")
        f.write("**Legend:**\n")
        f.write("- 📦 = Has sent purchase confirmations\n")
        f.write("- 📧 = Number of emails from this sender\n")
        f.write("- Lines are sorted by email frequency (most frequent first)\n\n")
        f.write("---\n\n")
        f.write("## Review and Edit This List\n\n")
        f.write("```\n")

        # Write simple brand list
        purchase_brands = []
        marketing_brands = []

        for brand_name, data in sorted_brands:
            if data["has_purchases"]:
                purchase_brands.append((brand_name, data))
            else:
                marketing_brands.append((brand_name, data))

        # Write purchase brands first
        if purchase_brands:
            f.write("# PURCHASE SENDERS (Have sent order confirmations)\n")
            for brand_name, data in purchase_brands:
                f.write(f"{brand_name}\n")

        # Then marketing brands
        if marketing_brands:
            f.write("\n# MARKETING ONLY (No purchase history found)\n")
            for brand_name, data in marketing_brands:
                f.write(f"{brand_name}\n")

        f.write("```\n\n")

        # Add detailed reference section
        f.write("## Detailed Reference\n\n")
        f.write("*For your information - the actual email addresses behind each brand:*\n\n")

        if purchase_brands:
            f.write("### Senders with Purchase History\n\n")
            for brand_name, data in purchase_brands[:50]:  # Limit detail section
                f.write(f"**{brand_name}** 📦 ({data['total_count']} emails)\n")
                for email_info in data["emails"]:
                    marker = "📦" if email_info["has_purchases"] else ""
                    f.write(f"- `{email_info['address']}` ({email_info['count']} emails) {marker}\n")
                f.write("\n")

        if marketing_brands:
            f.write("### Marketing Only Senders\n\n")
            for brand_name, data in marketing_brands[:50]:  # Limit detail section
                f.write(f"**{brand_name}** ({data['total_count']} emails)\n")
                for email_info in data["emails"][:3]:  # Limit emails shown per brand
                    f.write(f"- `{email_info['address']}` ({email_info['count']} emails)\n")
                f.write("\n")

        # Add statistics
        f.write("## Statistics\n\n")
        f.write(f"- Total potential clothing brands: {len(brands)}\n")
        f.write(f"- Brands with purchase history: {len(purchase_brands)}\n")
        f.write(f"- Marketing-only brands: {len(marketing_brands)}\n")
        f.write(f"- Total clothing emails: {sum(b[1]['total_count'] for b in sorted_brands)}\n")

    print(f"\n✅ Exported to: {output_path.absolute()}")
    return output_path


def main():
    """Main execution flow."""
    print("🚀 Clothing Sender Export Tool")
    print("="*60)

    try:
        # Initialize Gmail service
        print("\n1️⃣ Connecting to Gmail...")
        service = get_gmail_service_instance()
        print("   ✅ Connected successfully")

        # Extract all senders
        print("\n2️⃣ Extracting unique senders...")
        senders = extract_all_senders(service, max_emails=2000)

        # Identify potential clothing senders
        print("\n3️⃣ Identifying potential clothing brands...")
        clothing_senders = identify_clothing_senders(senders)
        print(f"   Found {len(clothing_senders)} potential clothing senders")

        # Export to markdown
        print("\n4️⃣ Exporting to markdown...")
        output_file = export_to_markdown(service, clothing_senders, senders)

        print("\n✅ Export complete!")
        print("\n📋 Next steps:")
        print(f"1. Open {output_file}")
        print("2. Delete any lines that are NOT clothing brands")
        print("3. Save the file")
        print("4. Run the classifier to use your personalized list")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())