#!/usr/bin/env python3
"""
Extract all links and YouTube URLs from PDF files.
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Set
import subprocess


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF using pdftotext."""
    try:
        result = subprocess.run(
            ['pdftotext', pdf_path, '-'],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout
    except Exception as e:
        print(f"  Error extracting text from {Path(pdf_path).name}: {e}")
        return ""


def extract_youtube_urls(text: str) -> List[str]:
    """Extract YouTube URLs from text."""
    patterns = [
        r'https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'https?://youtu\.be/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/v/([a-zA-Z0-9_-]{11})',
    ]

    video_ids = set()
    for pattern in patterns:
        matches = re.findall(pattern, text)
        video_ids.update(matches)

    return [f"https://www.youtube.com/watch?v={vid}" for vid in video_ids]


def extract_urls(text: str) -> List[str]:
    """Extract all URLs from text."""
    # Pattern for URLs
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, text)

    # Clean up URLs (remove trailing punctuation)
    cleaned_urls = []
    for url in urls:
        url = re.sub(r'[.,;:!?\)]+$', '', url)
        cleaned_urls.append(url)

    return list(set(cleaned_urls))


def categorize_urls(urls: List[str]) -> Dict:
    """Categorize URLs by type."""
    categorized = {
        'youtube': [],
        'arxiv': [],
        'github': [],
        'notion': [],
        'bluedot': [],
        'other': []
    }

    for url in urls:
        if 'youtube.com' in url or 'youtu.be' in url:
            categorized['youtube'].append(url)
        elif 'arxiv.org' in url:
            categorized['arxiv'].append(url)
        elif 'github.com' in url:
            categorized['github'].append(url)
        elif 'notion' in url:
            categorized['notion'].append(url)
        elif 'bluedot.org' in url:
            categorized['bluedot'].append(url)
        else:
            categorized['other'].append(url)

    return categorized


def scan_pdfs(pdf_dir: str, output_dir: str):
    """Scan all PDFs and extract links."""
    pdf_dir = Path(pdf_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(pdf_dir.glob("*.pdf"))

    print("="*70)
    print("PDF LINK EXTRACTION")
    print("="*70)
    print(f"\nScanning {len(pdf_files)} PDF files...")
    print()

    all_data = []
    all_youtube = set()
    all_urls = set()

    for pdf_file in pdf_files:
        print(f"📄 {pdf_file.name}")

        # Extract text
        text = extract_text_from_pdf(str(pdf_file))

        if not text:
            print("  ⚠️  Could not extract text")
            continue

        # Extract URLs
        urls = extract_urls(text)
        youtube_urls = extract_youtube_urls(text)

        # Parse unit and lesson from filename
        match = re.search(r'unit(\d+)_lesson(\d+)', pdf_file.name)
        if match:
            unit, lesson = match.groups()
        else:
            unit, lesson = "?", "?"

        pdf_data = {
            'file': pdf_file.name,
            'unit': unit,
            'lesson': lesson,
            'youtube_videos': youtube_urls,
            'all_urls': urls,
            'url_categories': categorize_urls(urls)
        }

        all_data.append(pdf_data)
        all_youtube.update(youtube_urls)
        all_urls.update(urls)

        # Print stats
        if youtube_urls:
            print(f"  📹 YouTube: {len(youtube_urls)}")
            for url in youtube_urls:
                print(f"     - {url}")

        print(f"  🔗 Total URLs: {len(urls)}")

        # Show interesting links
        categorized = categorize_urls(urls)
        if categorized['arxiv']:
            print(f"  📚 arXiv papers: {len(categorized['arxiv'])}")
        if categorized['github']:
            print(f"  💻 GitHub repos: {len(categorized['github'])}")
        if categorized['notion']:
            print(f"  📝 Notion pages: {len(categorized['notion'])}")

        print()

    # Save complete data
    json_file = output_dir / "extracted_links.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2)

    print("="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\nTotal YouTube videos found: {len(all_youtube)}")
    print(f"Total unique URLs found: {len(all_urls)}")
    print()

    # Save YouTube videos list
    if all_youtube:
        youtube_file = output_dir / "all_youtube_videos.txt"
        with open(youtube_file, 'w', encoding='utf-8') as f:
            f.write("# All YouTube Videos from Bluedot Technical AI Safety Course\n\n")
            for i, url in enumerate(sorted(all_youtube), 1):
                video_id = re.search(r'v=([a-zA-Z0-9_-]{11})', url)
                if video_id:
                    f.write(f"{i}. {url}\n")
                    f.write(f"   Video ID: {video_id.group(1)}\n\n")

        print(f"✅ YouTube videos saved to: {youtube_file.name}")

    # Categorize all URLs
    all_categorized = categorize_urls(list(all_urls))

    # Save categorized URLs
    categories_file = output_dir / "categorized_links.md"
    with open(categories_file, 'w', encoding='utf-8') as f:
        f.write("# All Links from Bluedot Technical AI Safety Course\n\n")

        for category, urls in all_categorized.items():
            if urls:
                f.write(f"## {category.title()} ({len(urls)})\n\n")
                for url in sorted(set(urls)):
                    f.write(f"- {url}\n")
                f.write("\n")

    print(f"✅ Categorized links saved to: {categories_file.name}")
    print(f"✅ Complete data saved to: {json_file.name}")

    # Print category summary
    print("\nLinks by category:")
    for category, urls in all_categorized.items():
        if urls:
            print(f"  - {category.title()}: {len(set(urls))}")

    print(f"\n📁 All files saved to: {output_dir}")

    return all_youtube


def main():
    pdf_dir = "downloads/bluedot_technical_ai_safety_complete/pdfs"
    output_dir = "downloads/bluedot_technical_ai_safety_complete/extracted_links"

    youtube_videos = scan_pdfs(pdf_dir, output_dir)

    if youtube_videos:
        print("\n" + "="*70)
        print("YOUTUBE VIDEOS TO DOWNLOAD")
        print("="*70)
        print("\nTo download all transcripts, run:\n")
        for url in sorted(youtube_videos):
            video_id = re.search(r'v=([a-zA-Z0-9_-]{11})', url)
            if video_id:
                print(f"# {url}")
                print(f"yt-dlp --skip-download --write-auto-sub --sub-lang en \\")
                print(f"  --output 'transcript_{video_id.group(1)}' '{url}'")
                print()


if __name__ == "__main__":
    main()