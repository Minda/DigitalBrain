#!/usr/bin/env python3
"""Merge multiple PDFs into a single PDF with bookmarks."""

import sys
from pathlib import Path
from pypdf import PdfWriter, PdfReader
from datetime import datetime

def merge_pdfs(pdf_paths, output_path, title="Merged Document"):
    """Merge multiple PDFs with bookmarks for navigation."""
    writer = PdfWriter()

    # Track page numbers for bookmarks
    current_page = 0

    # Add each PDF
    for pdf_path in pdf_paths:
        try:
            reader = PdfReader(pdf_path)
            num_pages = len(reader.pages)

            # Extract title from filename
            pdf_name = Path(pdf_path).stem
            # Clean up the title
            bookmark_title = pdf_name.replace("-coefficient-giving", "").replace("-", " ").title()

            # Add pages
            for page in reader.pages:
                writer.add_page(page)

            # Add bookmark for this section
            writer.add_outline_item(bookmark_title, current_page)
            current_page += num_pages

            print(f"✓ Added: {bookmark_title} ({num_pages} pages)")

        except Exception as e:
            print(f"✗ Error processing {pdf_path}: {e}")
            continue

    # Add metadata
    writer.add_metadata({
        '/Title': title,
        '/Author': 'Coefficient Giving',
        '/Subject': 'Navigating Transformative AI Fund - Complete Documentation',
        '/Creator': 'Exobrain PDF Merger',
        '/Producer': 'pypdf',
        '/CreationDate': datetime.now().isoformat()
    })

    # Write the merged PDF
    with open(output_path, 'wb') as output_file:
        writer.write(output_file)

    print(f"\n✓ Merged PDF saved to: {output_path}")
    print(f"  Total pages: {current_page}")

    return output_path

if __name__ == "__main__":
    # Define PDFs in logical order - only the Coefficient Giving files I just downloaded
    pdfs = [
        # Main fund page
        "downloads/articles/2026-02/navigating-transformative-ai-coefficient-giving.pdf",

        # RFPs and funding opportunities
        "downloads/articles/2026-02/request-for-proposals-ai-governance-coefficient-giving.pdf",
        "downloads/articles/2026-02/funding-for-work-that-builds-capacity-to-address-risks-from-transformative-ai-co.pdf",
        "downloads/articles/2026-02/career-development-and-transition-funding-coefficient-giving.pdf",

        # Research and approach
        "downloads/articles/2026-02/our-approach-to-ai-safety-and-security-coefficient-giving.pdf",
        "downloads/articles/2026-02/ai-safety-and-security-need-more-funders-coefficient-giving.pdf",
        "downloads/articles/2026-02/key-writings-on-ai-development-from-our-staff-coefficient-giving.pdf",

        # Team members
        "downloads/articles/2026-02/claire-zabel-coefficient-giving.pdf",
        "downloads/articles/2026-02/luke-muehlhauser-coefficient-giving.pdf",
        "downloads/articles/2026-02/peter-favaloro-coefficient-giving.pdf",
        "downloads/articles/2026-02/eli-rose-coefficient-giving.pdf",
    ]

    output_path = "downloads/articles/2026-02/coefficient-giving-complete-collection.pdf"

    merge_pdfs(
        pdfs,
        output_path,
        title="Coefficient Giving - Navigating Transformative AI Complete Collection"
    )