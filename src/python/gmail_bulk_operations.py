#!/usr/bin/env python3
"""
gmail_bulk_operations.py

Standalone CLI tool for bulk Gmail operations using any Gmail query.
Uses the existing Gmail MCP server auth infrastructure.

Usage:
    # Dry-run: see how many messages match
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

    # Mark all read
    uv run src/python/gmail_bulk_operations.py \
        --query "is:unread category:social" \
        --operation mark-read

Run from the project root so that app/mcp/gmail is importable via sys.path.
"""

# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

import argparse
import sys
from pathlib import Path

# Allow importing from the Gmail MCP package without installing it
_MCP_GMAIL_ROOT = Path(__file__).resolve().parents[2] / "app" / "mcp" / "gmail"
if str(_MCP_GMAIL_ROOT) not in sys.path:
    sys.path.insert(0, str(_MCP_GMAIL_ROOT))

from mcp_gmail.config import settings  # noqa: E402
from mcp_gmail.gmail import (  # noqa: E402
    batch_modify_messages_labels,
    get_gmail_service,
    list_all_message_ids,
)

BATCH_SIZE = 1000  # Gmail batchModify hard limit

OPERATIONS = {
    "archive": {
        "description": "Remove INBOX label (move to All Mail)",
        "add_labels": [],
        "remove_labels": ["INBOX"],
    },
    "trash": {
        "description": "Add TRASH label and remove INBOX",
        "add_labels": ["TRASH"],
        "remove_labels": ["INBOX"],
    },
    "mark-read": {
        "description": "Remove UNREAD label",
        "add_labels": [],
        "remove_labels": ["UNREAD"],
    },
    "mark-unread": {
        "description": "Add UNREAD label",
        "add_labels": ["UNREAD"],
        "remove_labels": [],
    },
}


def run_bulk_operation(
    query: str,
    operation: str,
    dry_run: bool = False,
    verbose: bool = False,
) -> None:
    """
    Fetch all message IDs matching `query` and apply `operation` in batches.

    Args:
        query:     Gmail search query string.
        operation: One of the keys in OPERATIONS.
        dry_run:   If True, only report counts without modifying anything.
        verbose:   If True, print progress for each batch.
    """
    if operation not in OPERATIONS:
        print(f"Unknown operation {operation!r}. Valid: {', '.join(OPERATIONS)}", file=sys.stderr)
        sys.exit(1)

    op = OPERATIONS[operation]
    print(f"Operation : {operation} — {op['description']}")
    print(f"Query     : {query!r}")
    if dry_run:
        print("Mode      : DRY RUN (no changes will be made)\n")
    else:
        print()

    service = get_gmail_service(
        credentials_path=settings.credentials_path,
        token_path=settings.token_path,
        scopes=settings.scopes,
    )

    print("Fetching matching message IDs (this may take a moment for large mailboxes)...")
    all_ids = list_all_message_ids(service, query, user_id=settings.user_id)
    total = len(all_ids)

    if total == 0:
        print("No messages matched the query.")
        return

    print(f"Found {total} matching messages.\n")

    if dry_run:
        print(f"[dry-run] Would {operation} {total} messages.")
        return

    batches = [all_ids[i : i + BATCH_SIZE] for i in range(0, total, BATCH_SIZE)]
    n_batches = len(batches)

    for i, batch in enumerate(batches, 1):
        if verbose or n_batches > 1:
            print(f"  Batch {i}/{n_batches}: {len(batch)} messages...")
        batch_modify_messages_labels(
            service,
            message_ids=batch,
            add_labels=op["add_labels"] or None,
            remove_labels=op["remove_labels"] or None,
            user_id=settings.user_id,
        )

    print(f"\nDone. {operation.capitalize()}d {total} messages in {n_batches} API call(s).")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bulk Gmail operations using any Gmail query.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="\n".join(
            f"  {op:<12} {info['description']}" for op, info in OPERATIONS.items()
        ),
    )
    parser.add_argument(
        "--query",
        "-q",
        required=True,
        help='Gmail search query, e.g. "category:social -(label:important OR label:starred)"',
    )
    parser.add_argument(
        "--operation",
        "-o",
        required=True,
        choices=list(OPERATIONS),
        metavar="OPERATION",
        help=f"Action to perform. Choices: {', '.join(OPERATIONS)}",
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Count matching messages without making changes.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print progress for each batch.",
    )

    args = parser.parse_args()
    run_bulk_operation(
        query=args.query,
        operation=args.operation,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()
