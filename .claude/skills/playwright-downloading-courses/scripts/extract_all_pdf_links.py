#!/usr/bin/env python3
"""
Extract all external links from Bluedot course PDFs.

This script scans all PDFs in the pdfs/ directory and extracts:
- All HTTP/HTTPS URLs
- YouTube video links
- arXiv papers
- GitHub repositories
- Other external resources
"""

import re
import subprocess
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Set
import json

def extract_links_from_pdf_annotations(pdf_path: Path) -> Set[str]:
    """Extract links from PDF annotations using pdftotext or similar."""
    links = set()

    # Try using pdftotext to extract text
    try:
        result = subprocess.run(
            ['pdftotext', str(pdf_path), '-'],
            capture_output=True,
            text=True,
            timeout=10
        )
        text = result.stdout

        # Extract URLs using regex
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+[^\s<>"{}|\\^`\[\].,;:!?\)]'
        found_urls = re.findall(url_pattern, text)
        links.update(found_urls)

    except FileNotFoundError:
        print(f"  ⚠️  pdftotext not found - trying alternative method")
    except Exception as e:
        print(f"  ⚠️  Error extracting from {pdf_path.name}: {e}")

    return links

def extract_links_using_pypdf(pdf_path: Path) -> Set[str]:
    """Extract links from PDF using PyPDF2."""
    try:
        import PyPDF2
        links = set()

        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)

            for page_num, page in enumerate(reader.pages):
                # Try to extract annotations
                if '/Annots' in page:
                    annotations = page['/Annots']
                    for annotation in annotations:
                        obj = annotation.get_object()
                        if obj.get('/Subtype') == '/Link':
                            if '/A' in obj:
                                action = obj['/A']
                                if '/URI' in action:
                                    uri = action['/URI']
                                    if isinstance(uri, str):
                                        links.add(uri)

                # Also extract from page text
                try:
                    text = page.extract_text()
                    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+[^\s<>"{}|\\^`\[\].,;:!?\)]'
                    found_urls = re.findall(url_pattern, text)
                    links.update(found_urls)
                except Exception:
                    pass

        return links
    except ImportError:
        print(f"  ⚠️  PyPDF2 not installed - install with: uv pip install PyPDF2")
        return set()
    except Exception as e:
        print(f"  ⚠️  Error with PyPDF2 on {pdf_path.name}: {e}")
        return set()

def categorize_link(url: str) -> str:
    """Categorize a URL by its domain/type."""
    url_lower = url.lower()

    if 'arxiv.org' in url_lower:
        return 'arXiv Papers'
    elif 'github.com' in url_lower or 'huggingface.co' in url_lower:
        return 'Code Repositories'
    elif 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'YouTube Videos'
    elif 'alignmentforum.org' in url_lower or 'lesswrong.com' in url_lower:
        return 'Alignment Forum / LessWrong'
    elif 'notion.so' in url_lower or 'notion.site' in url_lower:
        return 'Notion Pages'
    elif 'anthropic.com' in url_lower:
        return 'Anthropic'
    elif 'openai.com' in url_lower:
        return 'OpenAI'
    elif 'deepmind.com' in url_lower or 'google.com' in url_lower:
        return 'Google / DeepMind'
    elif 'bluedot.org' in url_lower:
        return 'Bluedot (Internal)'
    else:
        return 'Other Resources'

def extract_youtube_id(url: str) -> str:
    """Extract YouTube video ID from URL."""
    patterns = [
        r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'youtu\.be/([a-zA-Z0-9_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def main():
    # Find PDFs directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent.parent
    pdfs_dir = project_root / "downloads" / "bluedot_technical_ai_safety_complete" / "pdfs"

    if not pdfs_dir.exists():
        print(f"❌ PDFs directory not found: {pdfs_dir}")
        return

    print(f"📂 Scanning PDFs in: {pdfs_dir}\n")

    # Collect all links
    all_links = set()
    links_by_file = {}
    youtube_videos = set()

    pdf_files = sorted(pdfs_dir.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files\n")

    for pdf_path in pdf_files:
        print(f"Processing {pdf_path.name}...")

        # Try multiple extraction methods
        links = set()
        links.update(extract_links_from_pdf_annotations(pdf_path))
        links.update(extract_links_using_pypdf(pdf_path))

        # Filter out internal Bluedot links (keep them but categorize)
        external_links = {link for link in links if link.startswith('http')}

        # Extract YouTube video IDs
        for link in external_links:
            video_id = extract_youtube_id(link)
            if video_id:
                youtube_videos.add(video_id)

        links_by_file[pdf_path.name] = sorted(external_links)
        all_links.update(external_links)

        print(f"  Found {len(external_links)} links\n")

    # Categorize links
    categorized = defaultdict(set)
    for link in all_links:
        category = categorize_link(link)
        categorized[category].add(link)

    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80 + "\n")

    print(f"Total unique links: {len(all_links)}")
    print(f"YouTube videos found: {len(youtube_videos)}\n")

    print("Links by category:")
    for category in sorted(categorized.keys()):
        print(f"  {category}: {len(categorized[category])}")

    # Save results
    output_dir = pdfs_dir.parent / "extracted_links"
    output_dir.mkdir(exist_ok=True)

    # Save as JSON
    json_output = {
        "summary": {
            "total_links": len(all_links),
            "total_pdfs": len(pdf_files),
            "youtube_videos": len(youtube_videos)
        },
        "youtube_video_ids": sorted(youtube_videos),
        "links_by_category": {cat: sorted(links) for cat, links in categorized.items()},
        "links_by_file": links_by_file
    }

    json_path = output_dir / "extracted_pdf_links.json"
    with open(json_path, 'w') as f:
        json.dump(json_output, f, indent=2)

    print(f"\n✅ Saved JSON to: {json_path}")

    # Save as Markdown
    md_path = output_dir / "extracted_pdf_links.md"
    with open(md_path, 'w') as f:
        f.write("# External Links Extracted from Bluedot Course PDFs\n\n")
        f.write(f"**Total PDFs processed:** {len(pdf_files)}\n")
        f.write(f"**Total unique links:** {len(all_links)}\n")
        f.write(f"**YouTube videos found:** {len(youtube_videos)}\n\n")

        f.write("---\n\n")

        # YouTube videos
        if youtube_videos:
            f.write("## YouTube Videos\n\n")
            for video_id in sorted(youtube_videos):
                f.write(f"- https://www.youtube.com/watch?v={video_id}\n")
            f.write("\n---\n\n")

        # Links by category
        for category in sorted(categorized.keys()):
            f.write(f"## {category}\n\n")
            f.write(f"**Count:** {len(categorized[category])}\n\n")
            for link in sorted(categorized[category]):
                f.write(f"- {link}\n")
            f.write("\n---\n\n")

        # Links by file
        f.write("## Links by PDF File\n\n")
        for filename in sorted(links_by_file.keys()):
            links = links_by_file[filename]
            if links:
                f.write(f"### {filename}\n\n")
                for link in links:
                    f.write(f"- {link}\n")
                f.write("\n")

    print(f"✅ Saved Markdown to: {md_path}")

    # Print YouTube videos
    if youtube_videos:
        print(f"\n📹 YouTube Video IDs found:")
        for video_id in sorted(youtube_videos):
            print(f"  - {video_id}")

if __name__ == "__main__":
    main()
