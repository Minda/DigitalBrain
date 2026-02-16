# Clothing Email Classifier & Unsubscribe Bot - Implementation Plan

**Created**: 2026-02-13
**Status**: Ready for execution
**Goal**: Classify clothing purchase emails, label them, extract and process marketing email unsubscribe links

---

## **Step 0: Setup & Infrastructure**

### 0a. Reorganize MCP Gmail ✅
- ~~Create `app/` directory at project root~~
- ~~Move `vendor/mcp-gmail` → `app/mcp/gmail`~~
- ~~Update `.gitignore` to use `app/**/` patterns for any depth~~
- Update MCP server config in `~/.claude.json`:
  - All paths: `/vendor/mcp-gmail/` → `/app/mcp/gmail/`
- Test: `claude mcp list`

**Manual Review**: Gmail MCP server healthy

### 0b. Create Data Structure
- `personal/data/email-classifier/` directory
- Database: `personal/data/email-classifier/clothing_emails.db`
- Tables:
  - `classifications` (email_id, sender, subject, date, category, confidence)
  - `marketing_emails` (email_id, sender, subject, unsubscribe_link, status)
  - `unsubscribe_log` (timestamp, sender, link, result)

### 0c. Get Total Email Count
- Query Gmail for total inbox count
- Calculate required sample size (95% confidence, 5% margin of error)
- Show: "Account has X emails, need Y sample size"

**Manual Review**: Confirm sample size seems reasonable

---

## **Step 1: Statistical Sample Processing**

### Actions
- Randomly sample N emails (calculated from Step 0c)
- Use random date ranges to ensure representative sample
- Run classification on sample:
  - **Clothing purchase**: orders, shipping, receipts, returns
  - **Clothing marketing**: promotions, sales
  - **Other**: not clothing-related
- Save results to `personal/data/email-classifier/`
- Display classification table

### Statistics Output
```
Sample: N emails processed
- Clothing purchases: X (Y%)
- Clothing marketing: A (B%)
- Other: C (D%)

Estimated total inbox:
- ~E purchase emails (±F)
- ~G marketing emails (±H)
- Total clothing: ~I emails (±J)
```

**Manual Review**: Verify classifications, approve extrapolation

---

## **Step 2: Small Batch Test (20 emails)**

### Actions
- Select 20 emails from classified sample:
  - 10 purchase emails
  - 10 marketing emails
- Extract unsubscribe links from marketing emails
- Show detailed results for each email
- Save to database

**Manual Review**:
- Check classification accuracy
- Verify unsubscribe links are legitimate

---

## **Step 3: Label Test (5 emails)**

### Actions
- Create "Clothing Purchases" Gmail label
- Apply to 5 purchase emails from test batch
- **PAUSE for review**
- If successful, apply to remaining 5

**Manual Review**: Check Gmail, verify labels correct

---

## **Step 4: Archive Test (3 emails)**

### Actions
- Ensure data saved to database first
- Archive 3 marketing emails
- **PAUSE for review**
- If successful, archive remaining 7

**Manual Review**:
- Emails in archive?
- Data in `personal/data/email-classifier/clothing_emails.db`?

---

## **Step 5: Unsubscribe Test (2 links)**

### Actions
- Select 2 unsubscribe links from database
- Automated click/visit
- Log results
- Monitor for confirmation emails

**Manual Review**: Wait 2-3 days, verify no new emails from those senders

---

## **Step 6: Full Sample Batch**

### Actions
- Process all emails from statistical sample
- Show summary before execution
- Execute: label purchases, archive marketing, extract links
- Generate report

**Manual Review**: Spot-check results

---

## **Step 7: Full Inbox Processing**

### Actions
- Based on Step 6 success, process entire inbox
- Batch processing (100 emails at a time)
- Progress reporting
- Final statistics

---

## **Step 8: Create Reusable Skill**

### Files Created
- `app/agents/clothing-classifier/` - Agent directory
- `src/python/classify_clothing_emails.py` - Main script
- `.claude/skills/managing-clothing-emails/SKILL.md`
- `.claude/skills/managing-clothing-emails/README.md`
- `app/mcp/gmail/README.md` - Updated with privacy note

### Documentation Sections
**Privacy Note (in all relevant files):**
```
⚠️ PRIVACY: All email-derived data MUST be stored in personal/
- Email content, subjects, senders
- Classification results
- Unsubscribe links
- Processing logs
DO NOT commit email data to public repository.
```

---

## Safety Features
- ✅ Statistically valid sampling (95% confidence, 5% margin of error)
- ✅ All email data in `personal/` (private repo)
- ✅ Manual approval at each step
- ✅ Archive (not delete) for reversibility
- ✅ Complete audit trail
- ✅ Credentials gitignored

## Data Privacy Principle

**Rule: All email-derived data goes in `personal/`**
- Email content, subjects, senders
- Classification results
- Unsubscribe links database
- Any logs containing email data

## Technical Stack
- Python 3.10+ with `uv`
- Gmail MCP server (in `app/mcp/gmail/`)
- SQLite database (in `personal/data/email-classifier/`)
- Claude API for classification
- `requests` library for unsubscribe automation

## Outputs
- Database: `personal/data/email-classifier/clothing_emails.db`
- Logs: `personal/data/email-classifier/logs/`
- Reports: Summary statistics with confidence intervals

## Open Source Integration Options
1. **Inbox Zero** (github.com/elie222/inbox-zero) - Full AI email assistant
2. **Gmail Unsubscriber** (github.com/labnol/unsubscribe-gmail) - Google Apps Script
3. **Custom Python solution** - Recommended for full control

---

## Next Steps
1. Review this plan
2. Confirm approach
3. Execute Step 0 (setup)
4. Proceed through steps with manual review at each checkpoint
