#!/usr/bin/env python3
"""
Extract all external links from the complete_course_data.json file.

Since the PDFs don't have extractable text, we'll get the links from
the original JSON data that was captured during scraping.
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Set, Dict, List

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
    elif 'deepignorance.com' in url_lower:
        return 'Deep Ignorance'
    elif 'aws.amazon.com' in url_lower:
        return 'AWS / Amazon'
    else:
        return 'Other Resources'

def extract_youtube_id(url: str) -> str:
    """Extract YouTube video ID from URL."""
    patterns = [
        r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def is_external_link(url: str) -> bool:
    """Check if a URL is an external link (not internal Bluedot navigation)."""
    if not url.startswith('http'):
        return False

    # Skip internal Bluedot course navigation links
    if 'bluedot.org/courses/' in url and url.count('/') >= 5:
        # This is likely an internal course navigation link
        return False

    return True

def extract_links_from_lesson(lesson_data: dict) -> Set[str]:
    """Extract all links from a lesson's data."""
    links = set()

    # Extract from 'links' field
    if 'links' in lesson_data:
        for link in lesson_data['links']:
            # Link can be a string or a dict with 'url' field
            url = link.get('url') if isinstance(link, dict) else link
            if url and is_external_link(url):
                links.add(url)

    # Extract from 'youtube_videos' field
    if 'youtube_videos' in lesson_data:
        for video in lesson_data['youtube_videos']:
            if isinstance(video, dict) and 'url' in video:
                links.add(video['url'])
            elif isinstance(video, str):
                links.add(video)

    return links

def main():
    # Find the JSON file
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent.parent
    json_path = project_root / "downloads" / "bluedot_technical_ai_safety_complete" / "complete_course_data.json"

    if not json_path.exists():
        print(f"❌ JSON file not found: {json_path}")
        return

    print(f"📂 Reading data from: {json_path}\n")

    # Load the data
    with open(json_path, 'r') as f:
        course_data = json.load(f)

    # Extract all links
    all_links = set()
    links_by_unit = defaultdict(set)
    links_by_lesson = {}
    youtube_videos = {}

    print("Processing lessons...\n")

    # The data is a list of lessons, not a dict
    lessons_list = course_data if isinstance(course_data, list) else course_data.get('lessons', [])

    for lesson in lessons_list:
        unit = lesson.get('unit')
        lesson_num = lesson.get('lesson')
        lesson_key = f"Unit {unit}, Lesson {lesson_num}"

        # Extract links from this lesson
        lesson_links = extract_links_from_lesson(lesson)

        if lesson_links:
            links_by_lesson[lesson_key] = sorted(lesson_links)
            links_by_unit[f"Unit {unit}"].update(lesson_links)
            all_links.update(lesson_links)

            # Track YouTube videos
            for link in lesson_links:
                video_id = extract_youtube_id(link)
                if video_id:
                    youtube_videos[video_id] = {
                        'url': link,
                        'lesson': lesson_key
                    }

            print(f"  {lesson_key}: {len(lesson_links)} links")

    # Categorize all links
    categorized = defaultdict(set)
    for link in all_links:
        category = categorize_link(link)
        categorized[category].add(link)

    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80 + "\n")

    print(f"Total unique external links: {len(all_links)}")
    print(f"YouTube videos found: {len(youtube_videos)}\n")

    print("Links by category:")
    for category in sorted(categorized.keys()):
        print(f"  {category}: {len(categorized[category])}")

    # Save results
    output_dir = json_path.parent / "extracted_links"
    output_dir.mkdir(exist_ok=True)

    # Save as JSON
    json_output = {
        "summary": {
            "total_links": len(all_links),
            "total_lessons": len(links_by_lesson),
            "youtube_videos": len(youtube_videos)
        },
        "youtube_videos": {
            vid_id: {
                'url': data['url'],
                'lesson': data['lesson']
            } for vid_id, data in youtube_videos.items()
        },
        "links_by_category": {cat: sorted(links) for cat, links in categorized.items()},
        "links_by_unit": {unit: sorted(links) for unit, links in links_by_unit.items()},
        "links_by_lesson": links_by_lesson,
        "all_links": sorted(all_links)
    }

    json_output_path = output_dir / "all_external_links.json"
    with open(json_output_path, 'w') as f:
        json.dump(json_output, f, indent=2)

    print(f"\n✅ Saved JSON to: {json_output_path}")

    # Save as detailed Markdown
    md_path = output_dir / "all_external_links_detailed.md"
    with open(md_path, 'w') as f:
        f.write("# All External Links from Bluedot Technical AI Safety Course\n\n")
        f.write(f"**Source:** `complete_course_data.json`\n")
        f.write(f"**Total unique links:** {len(all_links)}\n")
        f.write(f"**Total lessons:** {len(links_by_lesson)}\n")
        f.write(f"**YouTube videos:** {len(youtube_videos)}\n\n")

        f.write("---\n\n")

        # YouTube videos
        if youtube_videos:
            f.write("## 📹 YouTube Videos\n\n")
            f.write(f"**Count:** {len(youtube_videos)}\n\n")
            for video_id, data in sorted(youtube_videos.items()):
                f.write(f"### {video_id}\n")
                f.write(f"- **URL:** {data['url']}\n")
                f.write(f"- **Found in:** {data['lesson']}\n\n")
            f.write("---\n\n")

        # Links by category
        f.write("## 📂 Links by Category\n\n")
        for category in sorted(categorized.keys()):
            f.write(f"### {category}\n\n")
            f.write(f"**Count:** {len(categorized[category])}\n\n")
            for link in sorted(categorized[category]):
                # Show which lessons contain this link
                lessons_with_link = []
                for lesson_key, lesson_links in links_by_lesson.items():
                    if link in lesson_links:
                        lessons_with_link.append(lesson_key)

                f.write(f"- {link}\n")
                if lessons_with_link:
                    f.write(f"  - Found in: {', '.join(lessons_with_link)}\n")
            f.write("\n---\n\n")

        # Links by unit
        f.write("## 📚 Links by Unit\n\n")
        for unit_name in sorted(links_by_unit.keys()):
            links = links_by_unit[unit_name]
            f.write(f"### {unit_name}\n\n")
            f.write(f"**Count:** {len(links)}\n\n")
            for link in sorted(links):
                f.write(f"- {link}\n")
            f.write("\n---\n\n")

        # Links by lesson
        f.write("## 📖 Links by Lesson\n\n")
        for lesson_key in sorted(links_by_lesson.keys()):
            links = links_by_lesson[lesson_key]
            f.write(f"### {lesson_key}\n\n")
            f.write(f"**Count:** {len(links)}\n\n")
            for link in links:
                f.write(f"- {link}\n")
            f.write("\n")

    print(f"✅ Saved detailed Markdown to: {md_path}")

    # Create a simple summary markdown
    summary_md_path = output_dir / "links_summary.md"
    with open(summary_md_path, 'w') as f:
        f.write("# External Links Summary\n\n")
        f.write(f"**Total:** {len(all_links)} unique external links\n\n")

        f.write("## By Category\n\n")
        for category in sorted(categorized.keys()):
            f.write(f"- **{category}:** {len(categorized[category])}\n")

        f.write(f"\n## YouTube Videos ({len(youtube_videos)})\n\n")
        for video_id in sorted(youtube_videos.keys()):
            f.write(f"- {video_id} - https://www.youtube.com/watch?v={video_id}\n")

    print(f"✅ Saved summary to: {summary_md_path}")

    # Print YouTube videos
    if youtube_videos:
        print(f"\n📹 YouTube Video IDs found ({len(youtube_videos)}):")
        for video_id, data in sorted(youtube_videos.items()):
            print(f"  - {video_id} ({data['lesson']})")

    print(f"\n✨ Done! Check the extracted_links/ directory for detailed results.")

if __name__ == "__main__":
    main()
