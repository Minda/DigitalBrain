## Feature Request

**Feature Name**: Delete Old Gmail Labels
**Project**: Email Management & Organization

TODAY: February 15 2026

---

### Current State

Currently the Gmail account has:

- 163 user-created labels accumulated over many years
- Multiple obsolete organizational systems (Sortd, Boomerang, old Z_ prefixes)
- Labels from completed projects and old workflows
- No systematic way to bulk delete labels
- Manual label deletion through Gmail UI is tedious

---

### Goal

**Problem Statement**: Years of Gmail use has resulted in 163+ labels, most of which are obsolete. This creates clutter, makes email organization confusing, and wastes mental energy when managing emails.

**Proposed Solution**: Systematically identify and delete obsolete labels while preserving important/active ones. Use the Gmail MCP server's new `delete_gmail_label` tool to batch-delete labels efficiently.

---

### Desired Behavior

**Target State**:
- Reduce from 181 labels to ~80 active labels
- Remove obsolete projects and old systems
- Keep all current organization systems (S/, C/, Sortd, Shared)
- Preserve historical context where needed (travel, tax docs, etc.)

**Requirements**:

- [x] MCP server supports label deletion
- [x] Create comprehensive list of labels to delete (~96 labels)
- [x] Create comprehensive list of labels to keep (~80 labels)
- [x] Execute deletion in phases (test with a few, then bulk delete)
- [x] Phase 1 test completed successfully (5 labels deleted)
- [x] Execute Phase 2-4 bulk deletions (all phases completed)
- [x] Document the cleanup process (completed in skill and docs)

**Nice to Have**:

- [ ] Before/after statistics on label usage
- [ ] Automated detection of unused labels (0 messages)
- [ ] Export list of deleted labels for reference

---

### Deletion Plan

#### Labels to KEEP (~80 labels):

**Tax & Legal**:
- greencard
- tn visa
- Taxes
- Taxes/HSA
- insurance
- tax receipts
- medical expenses

**Travel & Events**:
- Travel
- Event Tickets
- flights
- flights (refunded)
- canada trip

**Shopping & Clothing**:
- Clothing/Marketing
- Clothing/Purchases
- Clothing/Review

**Research & Reference**:
- email writing research
- good marketing examples
- apoe
- SIAI

**Current Organization Systems**:
- **S/ labels** (all ~20 labels) - Current system
- **C/ labels** (all ~15 labels) - Current categories
- **- Sortd ✔ labels** (all 21 labels) - Active organization system
- **- Shared ✔ labels** (all 6 labels) - Shared workflow system

**Personal**:
- <3
- return

#### Labels to DELETE (~96 labels):

**Old Email Management Systems** (8 labels):
- Boomerang (3 labels)
- ZD/, ZWO/, Z_INBOX: labels (5 labels)

**Old Projects** (15+ labels):
- Old Projects/* hierarchy (all sub-labels)
- Kittentech.com
- MindaMyers.com
- OptiMeta
- BrightMind
- Luminous
- RnM
- Wordpress License
- updraft plus notifications
- Hylo
- Freeingthegoddess

**Old Context Labels** (50+ labels):
- 1 kelton court prospects
- santa cruz housing search
- roommates
- CS Mail
- Campus
- Kir's workshop
- Mangalam
- Kundalini Core
- TLM Mentor
- T3 Train the Trainer
- Health Extension
- Energy in Plain English/*
- Mock Interviews
- Job Search (old system label)
- Online Course Details
- capracourse
- eben pagan
- donations
- gene and cell
- cognitive/neuro/amplification
- crypto currency
- hylo
- lead
- luminous
- paid work
- records
- roommates
- support
- todo
- updraft plus notifications
- btw
- next

**IMAP & Legacy** (5+ labels):
- [Imap]/Archive
- [Imap]/Drafts
- Deleted Messages
- Sent Items
- Sent Messages

**Miscellaneous/Unclear** (remaining):
- \* (single asterisk label)
- account details
- books
- clients
- energy work in business
- important reminders
- science updates
- s/time sensitive (if different from S/ system)

---

### Technical Context

**Relevant Files**:

- `/Users/min/Documents/Projects/DigitalBrain/app/mcp/gmail/mcp_gmail/server.py` (delete_gmail_label tool)
- `/Users/min/Documents/Projects/DigitalBrain/app/mcp/gmail/mcp_gmail/gmail.py` (delete_label function)

**Implementation**:

```python
# Example deletion script
from mcp_gmail.config import settings
from mcp_gmail.gmail import get_gmail_service, delete_label, get_labels

service = get_gmail_service(
    credentials_path=settings.credentials_path,
    token_path=settings.token_path,
    scopes=settings.scopes
)

# Labels to delete (by ID)
labels_to_delete = [
    "Label_197",  # - Shared ✔
    "Label_218",  # - Shared ✔/Jobs
    # ... continue with all IDs
]

# Delete with confirmation
for label_id in labels_to_delete:
    try:
        delete_label(service, label_id)
        print(f"Deleted: {label_id}")
    except Exception as e:
        print(f"Failed to delete {label_id}: {e}")
```

**Database Changes**:

- [ ] New schema required? No
- [ ] Schema changes needed? No

---

### Execution Plan

**Phase 1: Test Deletion** (5 labels) ✓ COMPLETED
1. ✓ Deleted 5 low-risk obsolete labels
2. ✓ Verified deletion works correctly
3. ✓ Confirmed emails are not deleted (only labels removed)
4. ✓ Labels: updraft plus notifications, Deleted Messages, Sent Messages, Sent Items, btw

**Phase 2: Delete Old Systems** (8 labels) ✓ COMPLETED
1. ✓ Deleted Boomerang labels (3)
2. ✓ Deleted Z-prefix organizational labels (5)

**Phase 3: Delete Old Projects** (39 labels) ✓ COMPLETED
1. ✓ Deleted Old Projects hierarchy (8 labels)
2. ✓ Deleted old company/project labels (15 labels)
3. ✓ Deleted old context labels (16+ labels)

**Phase 4: Final Cleanup** (28 labels) ✓ COMPLETED
1. ✓ Reviewed remaining unclear labels
2. ✓ Deleted confirmed obsolete labels (28/29 - 1 timeout)
3. ✓ Final verification completed
4. ✓ Documented final label count

**Phase 5: Remove S/ and C/ Systems** (24 labels) ✓ COMPLETED
1. ✓ Deleted 13 C/ category labels (keeping C/Minda Portfolio)
2. ✓ Deleted 11 S/ status labels (keeping S/Top Priority, S/Valuable Information, S/Tickets, Flights, Etc)
3. ✓ Verified all 4 keeper labels remained intact
4. ✓ Achieved 59 labels (exceeded target)

## Final Results

**Total Deleted**: 104 labels across 5 phases
- Phase 1: 5 labels (test)
- Phase 2: 8 labels (old systems)
- Phase 3: 39 labels (old projects)
- Phase 4: 28 labels (final cleanup)
- Phase 5: 24 labels (S/ and C/ organizational systems, keeping 4)

**Final Count**: 181 → 59 user labels (74 total including system labels)

**Target Achievement**: ✅ Target was ~80 labels, achieved 59 labels (exceeded target by 21!)

**Labels Kept from S/ and C/ systems**:
- S/Tickets, Flights, Etc
- S/Top Priority
- S/Valuable Information
- C/Minda Portfolio

**One Label Timeout**: Job Listings (Label_166) timed out during deletion - can be manually deleted later if needed

---

### Safety Measures

1. **Backup before deletion**: Export current label list
2. **Start small**: Test with 3-5 labels first
3. **No email deletion**: Deleting labels only removes the label, not the emails
4. **System labels protected**: MCP tool prevents deletion of INBOX, SENT, etc.
5. **Reversible**: Labels can be recreated and re-applied if needed

---

### Open Questions

- [x] Can we delete labels via MCP server? YES - implemented
- [ ] Should we export emails from deleted labels first? (Probably not needed - emails remain)
- [ ] Should we check message count per label before deletion? (Would be nice for verification)
- [ ] Keep "Jobs" related labels even if old? (Decision: keep current S/ and C/ systems only)

---

### Approval Checklist

- [x] Schema/DB changes reviewed (None needed)
- [x] Directory structure approved (Using existing MCP server)
- [x] Technical approach agreed upon (Use delete_gmail_label tool)
- [ ] Labels to keep list finalized
- [ ] Labels to delete list finalized

---

**Requested By**: Minda
**Date**: 2026-02-15
**Completed**: 2026-02-15
**Priority**: High
**Status**: ✅ Complete
