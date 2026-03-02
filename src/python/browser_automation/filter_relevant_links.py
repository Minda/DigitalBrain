#!/usr/bin/env python3
"""
Filter external links to keep only course-relevant content.

This script removes:
- Bluedot internal navigation (login, settings, about pages, etc.)
- Social media share links
- Generic course platform links
- Non-educational resources

Keeps:
- arXiv papers
- Research articles and blog posts about AI safety
- GitHub repositories with code/models
- YouTube videos (already downloaded)
- LessWrong/Alignment Forum posts
- Educational resources and fellowships
"""

import json
from pathlib import Path
from urllib.parse import urlparse
import re

def is_irrelevant_link(url: str) -> bool:
    """Check if a URL is irrelevant to course content."""
    url_lower = url.lower()

    # Bluedot internal navigation/platform links
    irrelevant_patterns = [
        r'bluedot\.org/(login|settings|about|join-us|privacy-policy|contact)',
        r'bluedot\.org/courses/[^/]+$',  # Course landing pages
        r'blog\.bluedot\.org$',  # Blog home page (specific posts are OK)
        r'lu\.ma/bluedotevents',  # Event calendar

        # Social media sharing
        r'twitter\.com/intent/tweet',
        r'facebook\.com/sharer',
        r'linkedin\.com/shareArticle',

        # Generic platform/tool homepages (not specific resources)
        r'^https?://(www\.)?bluedot\.org/?$',
        r'^https?://deepignorance\.ai/?$',
        r'^https?://jan\.ai/?$',

        # Form submissions and tracking
        r'web\.miniextensions\.com',
        r'airtable\.com/app',

        # Generic homepages without specific content
        r'^https?://[^/]+/?(\?utm_|$)',  # Homepage with just UTM params
    ]

    for pattern in irrelevant_patterns:
        if re.search(pattern, url_lower):
            return True

    return False

def is_high_value_link(url: str) -> bool:
    """Check if a URL is high-value course content."""
    url_lower = url.lower()

    high_value_patterns = [
        r'arxiv\.org',
        r'alignmentforum\.org',
        r'lesswrong\.com/posts',
        r'anthropic\.com/research',
        r'openai\.com/research',
        r'deepmind\.com',
        r'github\.com/[^/]+/[^/]+',  # Specific repos, not homepage
        r'huggingface\.co/[^/]+/[^/]+',  # Specific models/datasets
        r'blog\.bluedot\.org/p/',  # Specific blog posts
        r'alignment\.anthropic\.com',
        r'google\.com/generative-ai',
        r'docs\.google\.com/document',  # Shared documents
        r'notion\.(so|site)/.*-[a-f0-9]{32}',  # Specific Notion pages
        r'wikipedia\.org/wiki/',  # Wikipedia articles
        r'kairos\.fm',
        r'deepignorance\.ai/.*\?',  # Specific deep ignorance pages
        r'ar5iv\.org/pdf',  # arXiv HTML version
        r'medium\.com/.*/',  # Specific Medium articles
    ]

    for pattern in high_value_patterns:
        if re.search(pattern, url_lower):
            return True

    return False

def categorize_relevance(url: str) -> str:
    """Categorize link relevance."""
    if is_irrelevant_link(url):
        return 'irrelevant'
    elif is_high_value_link(url):
        return 'high_value'
    else:
        return 'medium_value'

def main():
    # Load the extracted links
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent.parent
    links_json = project_root / "downloads" / "bluedot_technical_ai_safety_complete" / "extracted_links" / "all_external_links.json"

    if not links_json.exists():
        print(f"❌ Links JSON not found: {links_json}")
        return

    print(f"📂 Loading links from: {links_json}\n")

    with open(links_json, 'r') as f:
        data = json.load(f)

    # Process all links
    all_links = data.get('all_links', [])
    links_by_lesson = data.get('links_by_lesson', {})

    print(f"Total links: {len(all_links)}\n")

    # Categorize links
    categorized = {
        'high_value': [],
        'medium_value': [],
        'irrelevant': []
    }

    for url in all_links:
        category = categorize_relevance(url)
        categorized[category].append(url)

    # Print summary
    print("="*80)
    print("RELEVANCE ANALYSIS")
    print("="*80 + "\n")

    print(f"✅ High Value (core course content): {len(categorized['high_value'])}")
    print(f"⚠️  Medium Value (supplementary): {len(categorized['medium_value'])}")
    print(f"❌ Irrelevant (navigation/platform): {len(categorized['irrelevant'])}\n")

    # Create filtered dataset
    filtered_links_by_lesson = {}
    for lesson_key, links in links_by_lesson.items():
        filtered = [url for url in links if categorize_relevance(url) != 'irrelevant']
        if filtered:
            filtered_links_by_lesson[lesson_key] = filtered

    # Save filtered results
    output_dir = links_json.parent
    filtered_json = output_dir / "filtered_course_resources.json"

    filtered_data = {
        "summary": {
            "total_original": len(all_links),
            "high_value": len(categorized['high_value']),
            "medium_value": len(categorized['medium_value']),
            "irrelevant_removed": len(categorized['irrelevant']),
            "lessons_with_resources": len(filtered_links_by_lesson)
        },
        "high_value_links": sorted(categorized['high_value']),
        "medium_value_links": sorted(categorized['medium_value']),
        "links_by_lesson": filtered_links_by_lesson
    }

    with open(filtered_json, 'w') as f:
        json.dump(filtered_data, f, indent=2)

    print(f"✅ Saved filtered data to: {filtered_json}")

    # Create markdown summary
    md_path = output_dir / "filtered_course_resources.md"
    with open(md_path, 'w') as f:
        f.write("# Filtered Course Resources\n\n")
        f.write("Only course-relevant external resources (navigation/platform links removed)\n\n")
        f.write(f"**Original total:** {len(all_links)} links\n")
        f.write(f"**After filtering:** {len(categorized['high_value']) + len(categorized['medium_value'])} links\n")
        f.write(f"**Removed:** {len(categorized['irrelevant'])} irrelevant links\n\n")

        f.write("---\n\n")

        # High value links
        f.write(f"## 📚 High Value Resources ({len(categorized['high_value'])})\n\n")
        f.write("Core course content: research papers, articles, code repositories\n\n")
        for url in sorted(categorized['high_value']):
            # Find which lessons reference this
            lessons = []
            for lesson_key, lesson_links in links_by_lesson.items():
                if url in lesson_links:
                    lessons.append(lesson_key)

            f.write(f"- {url}\n")
            if lessons:
                f.write(f"  - *Found in: {', '.join(lessons)}*\n")

        f.write("\n---\n\n")

        # Medium value links
        f.write(f"## 🔗 Medium Value Resources ({len(categorized['medium_value'])})\n\n")
        f.write("Supplementary content: fellowship programs, educational platforms, community resources\n\n")
        for url in sorted(categorized['medium_value']):
            f.write(f"- {url}\n")

        f.write("\n---\n\n")

        # Resources by lesson
        f.write("## 📖 Resources by Lesson\n\n")
        for lesson_key in sorted(filtered_links_by_lesson.keys()):
            links = filtered_links_by_lesson[lesson_key]
            f.write(f"### {lesson_key}\n\n")
            f.write(f"**Count:** {len(links)} resources\n\n")
            for url in links:
                category = categorize_relevance(url)
                emoji = "📚" if category == "high_value" else "🔗"
                f.write(f"{emoji} {url}\n")
            f.write("\n")

    print(f"✅ Saved markdown to: {md_path}")

    # Print examples of removed links
    print(f"\n📋 Sample of removed irrelevant links:")
    for url in sorted(categorized['irrelevant'])[:10]:
        print(f"  ❌ {url}")

    if len(categorized['irrelevant']) > 10:
        print(f"  ... and {len(categorized['irrelevant']) - 10} more")

    print(f"\n📋 Sample of high-value resources:")
    for url in sorted(categorized['high_value'])[:15]:
        print(f"  ✅ {url}")

    print(f"\n✨ Done! Filtered {len(categorized['irrelevant'])} irrelevant links")
    print(f"📁 {len(categorized['high_value']) + len(categorized['medium_value'])} relevant resources remaining")

if __name__ == "__main__":
    main()
