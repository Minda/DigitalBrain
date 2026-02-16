# Email Clothing Classifier Skill

Discover, classify, and manage clothing-related emails in Gmail using personalized sender detection and purchase history analysis.

## Overview

This skill provides a two-stage approach to identifying and classifying clothing-related emails:

1. **Discovery Phase**: Build a personalized list of clothing senders specific to your inbox
2. **Classification Phase**: Use the personalized list to classify emails as purchases, marketing, or other

## Prerequisites

- Gmail API credentials configured in `app/mcp/gmail/`
- Python environment with Google API libraries
- Personal data directory structure (`personal/data/email-classifier/`)

## Usage

### Stage 1: Discover Your Clothing Senders

First, run the discovery script to build your personalized clothing sender list:

```bash
python src/python/discover_clothing_senders.py
```

This script will:
1. Connect to your Gmail account
2. Extract all unique senders from your inbox (up to 2000 emails)
3. Identify potential clothing brands using pattern matching
4. **Check purchase history**: For each potential clothing sender, search if they've ever sent order confirmations
5. Present an interactive review where you can:
   - Confirm clothing senders
   - Mark as "marketing only" (no purchases)
   - Mark as "purchases" (has sent order confirmations)
   - Skip non-clothing senders

The script automatically suggests categorization based on purchase history:
- If purchase emails found → suggests "purchases"
- If no purchases found → suggests "marketing only"

### Stage 2: Classify Your Emails

Once you have a personalized sender list, run the main classifier:

```bash
python src/python/gmail_clothing_classifier.py
```

This will:
1. Load your personalized sender list (if available)
2. Search for clothing emails using both sender matching and keyword detection
3. Calculate sample sizes for statistical accuracy
4. Save results to SQLite database
5. Provide extrapolated estimates for your entire inbox

## Files and Locations

### Scripts
- `src/python/discover_clothing_senders.py` - Sender discovery and purchase history checker
- `src/python/gmail_clothing_classifier.py` - Main email classifier
- `src/python/setup_email_classifier_db.py` - Database setup utility
- `src/python/get_email_statistics.py` - Statistical sampling calculator

### Data Storage (Private)
All email-derived data is stored in `personal/` (private repository):
- `personal/data/email-classifier/clothing_senders.json` - Personalized sender list with categories
- `personal/data/email-classifier/clothing_senders_list.txt` - Simple text list of senders
- `personal/data/email-classifier/clothing_emails.db` - SQLite database with classifications

## Key Features

### Purchase History Detection
The discovery script checks if each sender has ever sent purchase-related emails by searching for:
- "order confirmation"
- "shipping confirmation"
- "tracking number"
- "order has shipped"
- "invoice"
- "receipt"

This helps distinguish between:
- **Purchase senders**: Actually process orders (e.g., Nike.com, Amazon)
- **Marketing-only senders**: Only send promotional emails (e.g., newsletter services)
- **Mixed senders**: Both purchases and marketing

### Personalized Detection
Instead of relying on a generic list of brands, the system:
1. Learns from YOUR specific inbox
2. Identifies the actual senders YOU receive emails from
3. Categorizes based on YOUR purchase history
4. Builds a reusable personalized list

### Statistical Sampling
The classifier uses proper statistical methods to:
- Calculate required sample sizes for 95% confidence
- Provide margin of error estimates
- Extrapolate findings to your entire inbox

## Example Workflow

```bash
# 1. First time setup - discover your clothing senders
$ python src/python/discover_clothing_senders.py

🚀 Gmail Clothing Sender Discovery Tool
============================================================
1️⃣ Connecting to Gmail...
   ✅ Connected successfully

2️⃣ Extracting unique senders...
   Found 1,234 unique senders from 2,000 emails

3️⃣ Identifying potential clothing brands...
   • Likely clothing: 45
   • Maybe clothing: 23
   • Likely not clothing: 1,166

4️⃣ Starting interactive review...

📧 [1/45] orders@nike.com
   Name: Nike Store
   Total emails: 15
   🔍 Checking for purchase emails... ✅ Found 3 purchase emails!
   Purchase example: "Your Nike Order #12345 Has Shipped..."
   Recent subjects:
     • Your Nike Order #12345 Has Shipped
     • Flash Sale: 40% Off Select Styles
   Confirm? [Y/n/m/p/q] (suggested: p): p

[Continue reviewing...]

# 2. Run the classifier with your personalized list
$ python src/python/gmail_clothing_classifier.py

🚀 Gmail Clothing Email Classifier
============================================================
   📋 Loaded 25 personalized clothing senders
   Using personalized clothing sender list (25 senders)

📊 SEARCH RESULTS
============================================================
Emails processed: 100
Clothing purchases found: 8
Clothing marketing found: 42

📈 EXTRAPOLATED ESTIMATES
Based on 100 emails sampled:
  • Estimated purchase emails: ~240 (±5%)
  • Estimated marketing emails: ~1,260 (±5%)
  • Total clothing-related: ~1,500 (±5%)
```

## Privacy & Security

- All email content and sender information is stored in `personal/` directory
- The `personal/` directory should be a separate private git repository
- Never commit email data to the public repository
- Scripts themselves (in `src/python/`) contain no personal data

## Customization

### Adding More Purchase Keywords
Edit `purchase_indicators` in `discover_clothing_senders.py`:
```python
purchase_indicators = {
    "strong": [
        '"order confirmation"',
        '"your package"',  # Add custom keywords
        # ...
    ]
}
```

### Adjusting Brand Detection
Modify the `brand_patterns` list in `discover_clothing_senders.py` to add regional or niche brands.

### Changing Sample Sizes
Adjust `max_emails` parameter in the discovery script:
```python
senders = extract_all_senders(service, max_emails=5000)  # Check more emails
```

## Troubleshooting

### "Module not found" Error
- Check that `app/mcp/gmail/` directory exists
- Ensure Google API libraries are installed: `pip install google-auth google-auth-oauthlib google-api-python-client`

### No Clothing Emails Found
1. Run the discovery script first to build personalized list
2. Check that your personalized sender list exists: `personal/data/email-classifier/clothing_senders.json`
3. Try lowering the matching threshold or adding more keywords

### Authentication Issues
- Ensure `credentials.json` and `token.json` exist in `app/mcp/gmail/`
- Delete `token.json` and re-authenticate if token expired

## Next Steps

After classification, you could:
1. Apply Gmail labels to categorized emails
2. Create filters to auto-archive marketing emails
3. Track purchase frequency and spending patterns
4. Set up unsubscribe automation for unwanted marketing