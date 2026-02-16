# Plan: Haiku Email Classifier

**Created**: 2026-02-13
**Status**: Ready for execution
**Goal**: Classify clothing emails by sender using Anthropic Haiku, then label/trash based on multi-signal confidence

---

## Architecture: Two-Pass Classification

### Pass 1 — Sender-level gate (Haiku)
"Is this sender a clothing brand?" Binary yes/no per sender domain. ~184 API calls after subtracting 27 known senders. Cost: ~$0.02.

### Pass 2 — Email-level sorting (heuristic, free)
For confirmed clothing senders, classify individual emails as purchase/marketing/account using subject-line heuristics:
- **Purchase**: "order #", "shipped", "tracking", "receipt", "invoice", "return label", "refund"
- **Marketing**: "% off", "sale", "new arrivals", "promo", "free shipping", "limited time" + List-Unsubscribe header
- **Account**: "password", "verify", "security", "loyalty", "points", "credit card"

This solves the Everlane problem (same sender sends both order confirmations AND marketing).

### Multi-Signal Voting (not LLM self-reported confidence)

LLM confidence floats are poorly calibrated. Instead, combine signals:

| Signal combination | Classification | Action tier |
|---|---|---|
| Haiku="clothing" + List-Unsubscribe + no purchase history | Marketing | Auto-trash |
| Haiku="clothing" + purchase history found | Purchase | Auto-label + mark read |
| Haiku="clothing" + subject heuristic matches purchase | Purchase | Auto-label + mark read |
| Haiku="clothing" but signals disagree | Ambiguous | Label "Clothing - Review" only |
| Haiku="not clothing" | Skip | No action |

### Three-Phase Execution

1. **Phase 1 — Classify** (`--phase classify`): Classify all senders + emails. Zero Gmail actions. First run labels EVERYTHING for review (no auto-actions).
2. **Phase 2 — Label** (`--phase label`): Apply Gmail labels only (reversible). User reviews in Gmail.
3. **Phase 3 — Trash** (`--phase trash`): Move marketing to trash (30-day recovery). Only after user approves labeled set. Requires cooldown period after Phase 2.

Phases are independent CLI flags. Can run on different days.

---

## Critical Fixes (from architecture review)

### 1. `list_messages` silently caps at 500
The MCP wrapper makes one API call and ignores `nextPageToken`. Must implement `list_all_message_ids` with pagination loop.

### 2. OAuth scope missing
Gmail MCP requests `gmail.readonly` + `gmail.labels` but NOT `gmail.modify`. Trashing and batch-modifying labels require `gmail.modify`. Must add scope and re-authenticate before Phase 2/3.

### 3. Crash recovery
Write each classification to DB immediately (not batch at end). Add `run_state` tracking so script can resume after crash.

### 4. Use trash, not delete
`trash_message` gives 30-day recovery. Never call permanent delete.

---

## DB Schema Changes

### New table: `sender_classifications`
```sql
CREATE TABLE IF NOT EXISTS sender_classifications (
    sender_email TEXT PRIMARY KEY,
    sender_name TEXT,
    is_clothing BOOLEAN NOT NULL,
    is_mixed_sender BOOLEAN DEFAULT FALSE,
    confidence REAL,
    reasoning TEXT,
    classification_method TEXT CHECK(classification_method IN ('known', 'haiku', 'manual')),
    list_unsubscribe_seen BOOLEAN DEFAULT FALSE,
    has_purchase_history BOOLEAN DEFAULT FALSE,
    sample_subjects TEXT,
    run_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Add to existing `classifications` table
```sql
ALTER TABLE classifications ADD COLUMN action_status TEXT
    DEFAULT 'pending'
    CHECK(action_status IN ('pending', 'labeled', 'trashed', 'skipped'));
```

### New table: `run_state`
```sql
CREATE TABLE IF NOT EXISTS run_state (
    run_id TEXT PRIMARY KEY,
    phase TEXT NOT NULL CHECK(phase IN ('classify', 'label', 'trash')),
    status TEXT NOT NULL CHECK(status IN ('in_progress', 'completed', 'failed')),
    total_senders INTEGER,
    classified_count INTEGER DEFAULT 0,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME
);
```

---

## New file: `src/python/classify_emails_haiku.py`

### Functions

1. **`list_all_message_ids(service, query, max_total)`** — Paginate Gmail API with `nextPageToken` loop.

2. **`extract_unique_senders(service, message_ids)`** — Group message IDs by sender email. Returns `{email: {name, message_ids, sample_subjects}}`.

3. **`classify_sender_with_haiku(client, sender_email, sender_name, sample_subjects)`** — Pass 1. Few-shot prompt with 3-5 examples. Uses tool_use for structured output. Returns `{is_clothing, is_mixed_sender, reasoning}`.

4. **`classify_email_heuristic(subject, has_list_unsubscribe, has_purchase_history)`** — Pass 2. Subject-line regex + header signals. Returns `purchase | marketing | account | unknown`.

5. **`get_multi_signal_classification(haiku_result, email_heuristic, list_unsubscribe, purchase_history)`** — Voting function. Combines signals into final classification + action tier.

6. **`apply_labels(service, classifications, phase)`** — Uses `batch_modify_messages_labels` (up to 1000 IDs per call).

7. **`trash_marketing(service, classifications)`** — Phase 3. Pre-trash manifest, confirmation prompt, batch size limit of 100, cooldown check.

8. **`save_classification(conn, classification)`** — Write single result to DB immediately (crash recovery).

9. **`main()`** — CLI with `--phase` and `--dry-run` flags.

### Haiku prompt design

Few-shot examples instead of brand lists:
```
Example 1: sender="everlane@e.everlane.com", subjects=["Your order has shipped", "New summer linen"] -> is_clothing=true, is_mixed_sender=false
Example 2: sender="nerdwallet@mail.nerdwallet.com", subjects=["Best credit cards 2026"] -> is_clothing=false
Example 3: sender="deals@amazon.com", subjects=["Your Amazon order", "Lightning deals"] -> is_clothing=false (mixed mega-retailer, not primarily clothing)
Example 4: sender="creative-market@notifications.com", subjects=["New fonts this week"] -> is_clothing=false (design marketplace)
```

Use Anthropic tool_use for guaranteed structured output (no JSON parsing failures).

### Mixed sender handling

Static list (Amazon, Target, Walmart, eBay, Costco) + Haiku `is_mixed_sender` flag. Mixed senders get per-email Haiku classification instead of sender-level.

---

## Phase 3 Safety

- **Trash only** (30-day Gmail recovery window)
- **Pre-trash manifest** written to `personal/data/email-classifier/trash_manifest.json`
- **Confirmation prompt** showing count: "About to trash N emails from M senders. Continue?"
- **Batch limit**: 100 emails per batch
- **Cooldown**: Minimum 1 hour between Phase 2 completion and Phase 3
- **`--dry-run` is default**. Must pass `--execute` to actually trash.

---

## Files

| File | Action |
|------|--------|
| `src/python/classify_emails_haiku.py` | **New file** (main deliverable) |
| `src/python/setup_email_classifier_db.py` | Update with new tables |
| `personal/data/email-classifier/clothing_senders.json` | Updated by feedback loop |

## Cost

| What | API calls | Cost |
|------|-----------|------|
| Dry run (50 emails) | ~23 | ~$0.002 |
| Full sender classification | ~184 | ~$0.02 |

## Verification (dry run)

1. Run with `--dry-run` on 50 emails
2. Verify Haiku structured output via tool_use
3. Check multi-signal voting produces sensible tiers
4. Confirm known clothing senders (thredup, everlane) classify correctly
5. Confirm known false positives (nerdwallet, jetblue) classify as not-clothing
6. Verify DB writes succeed and are crash-recoverable
7. Print cost via `response.usage` token counts
