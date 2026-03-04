# Managing Email Skill

Comprehensive Gmail management tools for cleaning up labels, organizing emails, and maintaining a healthy inbox using the Gmail MCP server and Python automation.

## Overview

This skill provides tools and workflows for:

1. **Label Management**: Delete obsolete labels, organize active labels, prevent label sprawl
2. **Email Classification**: AI-powered categorization (clothing, shopping, etc.)
3. **Bulk Operations**: Batch label deletion with safety checks
4. **Statistics & Analysis**: Understand email patterns and label usage

## Prerequisites

- Gmail MCP server configured in `app/mcp/gmail/`
- Python environment with Gmail API libraries
- OAuth credentials and token for Gmail API access
- Project and feature documentation in `plans/`

## Core Workflows

### 1. Bulk Archive / Trash / Mark-Read by Query

Clean up large volumes of email in one command using any Gmail search query.

#### Python CLI (`src/python/gmail_bulk_operations.py`)

```bash
# Dry-run first — always preview before running
uv run src/python/gmail_bulk_operations.py \
    --query "category:social -(label:important OR label:starred)" \
    --operation archive \
    --dry-run

# Archive all Social emails (not important/starred)
uv run src/python/gmail_bulk_operations.py \
    --query "category:social -(label:important OR label:starred)" \
    --operation archive

# Trash old promotions
uv run src/python/gmail_bulk_operations.py \
    --query "category:promotions older_than:1y" \
    --operation trash

# Mark all unread social emails as read
uv run src/python/gmail_bulk_operations.py \
    --query "is:unread category:social" \
    --operation mark-read
```

**Supported operations:** `archive` · `trash` · `mark-read` · `mark-unread`

**How it works:** Paginates all matching messages (no cap), then uses Gmail's
`batchModify` API in batches of 1000 — far fewer API calls than per-message ops.

#### Via MCP Tool (interactive with Claude)

```python
# Dry-run — count without changing anything
batch_archive_messages(
    query="category:social -(label:important OR label:starred)",
    dry_run=True
)

# Run for real
batch_archive_messages(
    query="category:social -(label:important OR label:starred)"
)
```

#### Workflow: Archive Social Inbox

1. Dry-run to confirm count
2. Run archive
3. Verify in Gmail that Social tab is clear

#### Safety

- Always do `--dry-run` first to see the count
- `archive` is reversible (emails stay in All Mail)
- `trash` gives 30-day recovery window
- Important/starred emails are excluded by the recommended query pattern

### 2. Label Cleanup & Deletion

Clean up years of accumulated Gmail labels systematically.

#### Phase-Based Deletion Approach

**Planning**:
1. Review all current labels: `python list_gmail_labels.py`
2. Create keep/delete lists in feature documentation
3. Start with test deletions (5-10 labels) to verify safety

**Execution**:
```python
# List all labels organized by type
from mcp_gmail.config import settings
from mcp_gmail.gmail import get_gmail_service, get_labels

service = get_gmail_service(
    credentials_path=settings.credentials_path,
    token_path=settings.token_path,
    scopes=settings.scopes
)

labels = get_labels(service, user_id=settings.user_id)

# Sort and display
system_labels = [l for l in labels if l.get('type') == 'system']
user_labels = [l for l in labels if l.get('type') != 'system']

print(f"System labels (cannot delete): {len(system_labels)}")
print(f"User labels (can delete): {len(user_labels)}")
```

**Phased Deletion Pattern**:
```python
# Phase template for safe batch deletion
from mcp_gmail.gmail import delete_label

phase_labels = [
    ("Label_123", "Old Project Name"),
    ("Label_456", "Obsolete System"),
    # ...
]

# Verify, delete, and confirm
for label_id, label_name in phase_labels:
    try:
        delete_label(service, label_id, user_id=settings.user_id)
        print(f"✓ Deleted: {label_name}")
    except Exception as e:
        print(f"✗ Failed: {label_name} - {e}")
```

#### Safety Measures

1. **Test First**: Always start with 3-5 low-risk labels
2. **System Protection**: Cannot delete INBOX, SENT, TRASH, etc.
3. **Emails Preserved**: Deleting labels doesn't delete emails
4. **Reversible**: Labels can be recreated if needed
5. **Verification**: Script confirms deletion after each batch

### 2. Label Organization Strategy

**Keep Labels For**:
- Tax & legal documents (greencard, tn visa, taxes, insurance)
- Travel & events (flights, tickets, reservations)
- Active shopping categories (clothing purchases, returns)
- Research & reference materials
- Current organizational systems (S/, C/, Sortd)
- Personal/sentimental (<3, important contacts)

**Delete Labels For**:
- Completed projects (old companies, defunct products)
- Obsolete email systems (old Boomerang, outdated prefixes)
- Old housing/job searches that are complete
- Expired time-based labels (specific dates/years)
- Unclear/cryptic single-character labels with no context
- IMAP legacy labels (if using web Gmail only)

### 3. Email Classification

See the `email-clothing-classifier` skill for AI-powered email categorization.

This integrates with label management by:
1. Creating targeted labels for classifications
2. Automatically applying labels to categorized emails
3. Providing statistics on email categories

### 4. MCP Server Tools

The Gmail MCP server (`app/mcp/gmail/`) provides these label management tools:

```python
# Available via MCP
list_available_labels()          # Get all labels with IDs
delete_gmail_label(label_id)     # Delete a specific label
add_label_to_message(msg_id, label_id)
remove_label_from_message(msg_id, label_id)
mark_message_read(msg_id)
```

## Files and Locations

### Scripts
- `src/python/gmail_bulk_operations.py` - Bulk archive/trash/mark-read by query (CLI)
- `src/python/list_gmail_labels.py` - Display all labels organized by type
- `plans/2026-02-15-delete-old-gmail-labels.md` - Deletion plan with keep/delete lists
- `plans/2026-02-15-email-management.md` - Overall email management project

### MCP Server
- `app/mcp/gmail/mcp_gmail/server.py` - MCP tools (`batch_archive_messages` + label ops)
- `app/mcp/gmail/mcp_gmail/gmail.py` - Core Gmail API functions (`list_all_message_ids`, `batch_modify_messages_labels`, etc.)

### Data Storage
All email data should be in `personal/` (private repository):
- `personal/data/email-classifier/` - Classification databases
- Project/feature docs can be in public `plans/` (no personal data)

## Common Workflows

### Workflow: Clean Up Old Labels

**Step 1**: List and categorize
```bash
python /tmp/list_gmail_labels.py > labels_audit.txt
```

**Step 2**: Create deletion plan
- Document in `plans/YYYY-MM-DD-delete-old-gmail-labels.md`
- List labels to keep (~80 active labels)
- List labels to delete (~100 obsolete labels)

**Step 3**: Execute in phases
```bash
# Phase 1: Test (5 labels)
python /tmp/delete_phase1_test.py

# Phase 2: Old systems (8 labels)
python /tmp/delete_phase2_systems.py

# Phase 3: Old projects (40 labels)
python /tmp/delete_phase3_projects.py

# Phase 4: Final cleanup (remaining)
python /tmp/delete_phase4_cleanup.py
```

**Step 4**: Verify and document
- Confirm target label count achieved
- Update feature doc with completion status
- Document any labels that couldn't be deleted

### Workflow: Prevent Future Label Sprawl

**Best Practices**:
1. Use hierarchical labels (Parent/Child) instead of flat structure
2. Maintain 3-4 main organizational systems maximum
3. Archive old system labels when switching to new system
4. Quarterly review: Check for labels with 0 messages
5. Create labels with clear, descriptive names (not cryptic codes)

**Organizational Systems**:
- **S/ (Status)**: Workflow states (Inbox, Read, Action, Finished)
- **C/ (Category)**: Content categories (Learning, Health, Resources)
- **Sortd/Shared**: Project-based organization
- **Specific Categories**: Tax, Travel, Clothing (functional categories)

## Example: Complete Label Cleanup Session

```bash
# 1. Assess current state
python /tmp/list_gmail_labels.py
# Output: 181 total labels (18 system, 163 user)

# 2. Phase 1: Test deletion (5 labels)
python /tmp/delete_phase1_test.py
# Result: 181 → 176 labels ✓

# 3. Phase 2: Delete old systems (8 labels)
python /tmp/delete_phase2_systems.py
# Result: 176 → 168 labels ✓

# 4. Phase 3: Delete old projects (40 labels)
python /tmp/delete_phase3_projects.py
# Result: 168 → 128 labels ✓

# 5. Phase 4: Final cleanup (remaining ~48 labels)
python /tmp/delete_phase4_cleanup.py
# Result: 128 → 80 labels ✓

# 6. Verify final state
python /tmp/list_gmail_labels.py
# Output: 80 user labels (target achieved!)
```

## Troubleshooting

### "Cannot delete label" Error
- Check if it's a system label (INBOX, SENT, etc.) - these cannot be deleted
- Verify label ID is correct
- Ensure Gmail API permissions include `gmail.labels` scope

### Label still shows after deletion
- Refresh Gmail in browser (Ctrl+R)
- Check that deletion script completed successfully
- Verify with `list_available_labels()` tool

### Want to undo a deletion
- Labels can be recreated manually in Gmail
- Re-applying labels to emails requires identifying those emails first
- Consider exporting label before deletion if uncertain

## Integration with Other Skills

**Clothing Classifier** (`email-clothing-classifier`):
- Uses email classification to create targeted labels
- Can automatically apply Clothing/* labels based on AI categorization

**Notion Integration** (`fetching-notion-content`):
- Document label cleanup plans in Notion
- Track progress and decisions

## Privacy & Security

- All label operations go through authenticated Gmail MCP server
- Label deletion removes labels only, not emails
- Scripts contain no personal email data
- Document deletion plans in public docs (no sensitive label names)
- Store email-derived data in `personal/` only

## Next Steps

After label cleanup:
1. **Set up filters**: Auto-apply remaining labels to new emails
2. **Create workflows**: S/ system for status-based organization
3. **Schedule reviews**: Quarterly label audit to prevent sprawl
4. **Automate classification**: Use AI to categorize incoming emails
5. **Integrate with automation**: Unsubscribe bots, auto-archive rules

## Skill Invocation

Use this skill when:
- "clean up Gmail labels"
- "delete old email labels"
- "organize my inbox"
- "too many Gmail labels"
- "email label management"
- "gmail cleanup"
- "archive social emails"
- "bulk archive inbox"
- "delete everything matching"
- "clear out promotions"
- "batch email operation"
