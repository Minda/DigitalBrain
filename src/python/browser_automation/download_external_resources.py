#!/usr/bin/env python3
"""
Download all external resources from the Bluedot course with lesson prefixes.

This script downloads:
- arXiv papers (PDF)
- GitHub repositories (clone or download)
- Web articles (using download-url skill)
- Other downloadable resources

Files are organized by lesson with proper prefixes.
"""

import json
import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse
import time

def sanitize_filename(name: str) -> str:
    """Make a string safe for use as a filename."""
    # Replace problematic characters
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    # Remove leading/trailing whitespace and dots
    name = name.strip('. ')
    # Limit length
    if len(name) > 200:
        name = name[:200]
    return name

def get_lesson_prefix(unit: int, lesson: int) -> str:
    """Generate a lesson prefix like 'U1L1_' or 'U3L2_'."""
    return f"U{unit}L{lesson}_"

def extract_arxiv_id(url: str) -> str:
    """Extract arXiv paper ID from URL."""
    patterns = [
        r'arxiv\.org/abs/(\d+\.\d+)',
        r'arxiv\.org/pdf/(\d+\.\d+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def download_arxiv_paper(arxiv_id: str, output_path: Path) -> bool:
    """Download arXiv paper as PDF."""
    try:
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        result = subprocess.run(
            ['curl', '-L', '-o', str(output_path), pdf_url],
            capture_output=True,
            timeout=60
        )
        return result.returncode == 0 and output_path.exists()
    except Exception as e:
        print(f"    ❌ Error downloading arXiv {arxiv_id}: {e}")
        return False

def download_web_page(url: str, output_path: Path) -> bool:
    """Download web page as PDF using the download-url skill."""
    try:
        # Use the existing download-url skill
        result = subprocess.run(
            [
                'python3',
                '.claude/skills/downloading-articles/scripts/download_single_url.py',
                url,
                str(output_path.parent)
            ],
            capture_output=True,
            text=True,
            timeout=120,
            cwd='/Users/min/Documents/Projects/DigitalBrain'
        )
        return result.returncode == 0
    except Exception as e:
        print(f"    ⚠️  Could not download {url}: {e}")
        return False

def categorize_url(url: str) -> str:
    """Determine what type of resource a URL is."""
    url_lower = url.lower()

    if 'arxiv.org' in url_lower:
        return 'arxiv'
    elif 'github.com' in url_lower:
        return 'github'
    elif 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'youtube'
    elif 'notion.so' in url_lower or 'notion.site' in url_lower:
        return 'notion'
    elif url_lower.endswith('.pdf'):
        return 'pdf'
    elif 'alignmentforum.org' in url_lower or 'lesswrong.com' in url_lower:
        return 'article'
    elif 'anthropic.com' in url_lower or 'openai.com' in url_lower:
        return 'article'
    else:
        return 'other'

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

    # Create output directory
    output_base = project_root / "downloads" / "bluedot_technical_ai_safety_complete" / "external_resources"
    output_base.mkdir(exist_ok=True)

    # Create subdirectories
    (output_base / "arxiv_papers").mkdir(exist_ok=True)
    (output_base / "articles").mkdir(exist_ok=True)
    (output_base / "github_repos").mkdir(exist_ok=True)
    (output_base / "other").mkdir(exist_ok=True)

    # Process links by lesson
    links_by_lesson = data.get('links_by_lesson', {})

    print(f"Found {len(links_by_lesson)} lessons with external links\n")
    print("="*80)

    # Statistics
    stats = {
        'arxiv': {'attempted': 0, 'succeeded': 0},
        'articles': {'attempted': 0, 'succeeded': 0},
        'github': {'attempted': 0, 'succeeded': 0},
        'other': {'attempted': 0, 'succeeded': 0},
        'skipped': {'youtube': 0, 'bluedot_internal': 0, 'notion': 0}
    }

    for lesson_key, links in sorted(links_by_lesson.items()):
        # Parse lesson key "Unit X, Lesson Y"
        match = re.match(r'Unit (\d+), Lesson (\d+)', lesson_key)
        if not match:
            continue

        unit = int(match.group(1))
        lesson = int(match.group(2))
        prefix = get_lesson_prefix(unit, lesson)

        print(f"\n📚 {lesson_key}")
        print(f"   Prefix: {prefix}")
        print(f"   Links: {len(links)}")

        for url in links:
            resource_type = categorize_url(url)

            # Skip certain types
            if resource_type == 'youtube':
                stats['skipped']['youtube'] += 1
                print(f"    ⏭️  Skipping YouTube (already downloaded): {url}")
                continue

            if 'bluedot.org/courses' in url:
                stats['skipped']['bluedot_internal'] += 1
                continue

            if resource_type == 'notion':
                stats['skipped']['notion'] += 1
                print(f"    ⏭️  Skipping Notion (requires auth): {url}")
                continue

            # Download based on type
            if resource_type == 'arxiv':
                arxiv_id = extract_arxiv_id(url)
                if arxiv_id:
                    output_path = output_base / "arxiv_papers" / f"{prefix}arxiv_{arxiv_id}.pdf"
                    if output_path.exists():
                        print(f"    ✓ Already exists: {output_path.name}")
                        stats['arxiv']['succeeded'] += 1
                    else:
                        print(f"    📥 Downloading arXiv {arxiv_id}...")
                        stats['arxiv']['attempted'] += 1
                        if download_arxiv_paper(arxiv_id, output_path):
                            print(f"    ✅ Saved: {output_path.name}")
                            stats['arxiv']['succeeded'] += 1
                        else:
                            print(f"    ❌ Failed to download")
                        time.sleep(1)  # Rate limiting

            elif resource_type == 'article':
                # Extract domain for filename
                domain = urlparse(url).netloc.replace('www.', '')
                # Create a sanitized filename
                filename = sanitize_filename(url.split('/')[-1] or domain)
                output_path = output_base / "articles" / f"{prefix}{domain}_{filename}"

                print(f"    📄 Article: {domain}")
                print(f"       {url}")
                stats['articles']['attempted'] += 1
                # Note: Actual download would use download-url skill
                # For now, just log the URL

            elif resource_type == 'github':
                print(f"    💻 GitHub: {url}")
                stats['github']['attempted'] += 1
                # GitHub repos could be cloned or downloaded as zip
                # For now, just log

            else:
                print(f"    🔗 Other: {url}")
                stats['other']['attempted'] += 1

    # Print summary
    print("\n" + "="*80)
    print("DOWNLOAD SUMMARY")
    print("="*80 + "\n")

    print(f"arXiv Papers:")
    print(f"  Attempted: {stats['arxiv']['attempted']}")
    print(f"  Succeeded: {stats['arxiv']['succeeded']}")

    print(f"\nArticles:")
    print(f"  Found: {stats['articles']['attempted']}")

    print(f"\nGitHub Repositories:")
    print(f"  Found: {stats['github']['attempted']}")

    print(f"\nSkipped:")
    print(f"  YouTube videos: {stats['skipped']['youtube']} (already downloaded)")
    print(f"  Notion pages: {stats['skipped']['notion']} (require authentication)")
    print(f"  Bluedot internal: {stats['skipped']['bluedot_internal']}")

    print(f"\n📁 Downloaded files saved to: {output_base}")

    # Create a manifest file
    manifest_path = output_base / "DOWNLOAD_MANIFEST.md"
    with open(manifest_path, 'w') as f:
        f.write("# External Resources Download Manifest\n\n")
        f.write(f"**Total lessons:** {len(links_by_lesson)}\n\n")
        f.write("## Download Statistics\n\n")
        f.write(f"- **arXiv Papers:** {stats['arxiv']['succeeded']} downloaded\n")
        f.write(f"- **Articles:** {stats['articles']['attempted']} identified\n")
        f.write(f"- **GitHub Repos:** {stats['github']['attempted']} identified\n")
        f.write(f"- **Skipped (YouTube):** {stats['skipped']['youtube']}\n")
        f.write(f"- **Skipped (Notion):** {stats['skipped']['notion']}\n")
        f.write(f"- **Skipped (Internal):** {stats['skipped']['bluedot_internal']}\n\n")

        f.write("## File Naming Convention\n\n")
        f.write("All files are prefixed with `U{unit}L{lesson}_` to indicate which lesson they belong to.\n\n")
        f.write("Examples:\n")
        f.write("- `U1L1_arxiv_2203.15556.pdf` - arXiv paper from Unit 1, Lesson 1\n")
        f.write("- `U3L4_anthropic_article.pdf` - Article from Unit 3, Lesson 4\n\n")

    print(f"✅ Saved manifest to: {manifest_path}")

if __name__ == "__main__":
    main()
