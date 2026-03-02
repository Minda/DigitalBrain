#!/usr/bin/env python3
"""
Download all high-value resources from Units 1-5 (excluding Unit 6).

Downloads:
- arXiv papers as PDFs
- Research articles and blog posts as PDFs (using download-url skill)
- GitHub repositories (clone)
- All files are prefixed with lesson identifiers (e.g., U2L3_)
"""

import json
import subprocess
import time
import re
from pathlib import Path
from urllib.parse import urlparse

def sanitize_filename(name: str) -> str:
    """Make a string safe for use as a filename."""
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = name.strip('. ')
    if len(name) > 150:
        name = name[:150]
    return name

def get_lesson_prefix(unit: int, lesson: int) -> str:
    """Generate a lesson prefix like 'U1L1_'."""
    return f"U{unit}L{lesson}_"

def extract_arxiv_id(url: str) -> str:
    """Extract arXiv paper ID from URL."""
    patterns = [
        r'arxiv\.org/abs/(\d+\.\d+)',
        r'arxiv\.org/pdf/(\d+\.\d+)',
        r'ar5iv\.org/.*?/(\d+\.\d+)',
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
        if result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 1000:
            return True
        return False
    except Exception as e:
        print(f"    ❌ Error downloading arXiv {arxiv_id}: {e}")
        return False

def download_web_article(url: str, output_dir: Path, prefix: str) -> tuple:
    """Download web article as PDF using download-url skill."""
    try:
        # Create temporary directory for download
        temp_dir = output_dir / "temp_download"
        temp_dir.mkdir(exist_ok=True)

        # Use the download-url skill
        # Note: Using --script to auto-install inline dependencies
        result = subprocess.run(
            [
                'uv', 'run', '--script',
                '.claude/skills/download-url/scripts/download_article.py',
                url,
                '--output-dir', str(temp_dir)
            ],
            capture_output=True,
            text=True,
            timeout=180,
            cwd='/Users/min/Documents/Projects/DigitalBrain'
        )

        # Find the downloaded file (search recursively as download-url creates date subdirs)
        pdf_files = list(temp_dir.glob("**/*.pdf"))
        if pdf_files:
            downloaded_file = pdf_files[0]
            # Rename with lesson prefix
            new_name = f"{prefix}{downloaded_file.name}"
            final_path = output_dir / new_name
            downloaded_file.rename(final_path)

            # Clean up temp directory
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

            return True, final_path.name
        else:
            # Clean up temp directory
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False, None

    except subprocess.TimeoutExpired:
        print(f"    ⏱️  Timeout downloading {url}")
        return False, None
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False, None

def clone_github_repo(url: str, output_dir: Path, prefix: str) -> bool:
    """Clone a GitHub repository."""
    try:
        # Extract repo name from URL
        match = re.search(r'github\.com/([^/]+)/([^/\?#]+)', url)
        if not match:
            return False

        org, repo = match.groups()
        repo_name = f"{prefix}{org}_{repo}"
        clone_path = output_dir / repo_name

        if clone_path.exists():
            print(f"    ✓ Already cloned: {repo_name}")
            return True

        result = subprocess.run(
            ['git', 'clone', '--depth', '1', url, str(clone_path)],
            capture_output=True,
            timeout=300
        )

        if result.returncode == 0:
            # Remove .git directory to save space
            import shutil
            git_dir = clone_path / '.git'
            if git_dir.exists():
                shutil.rmtree(git_dir)
            return True
        return False

    except Exception as e:
        print(f"    ❌ Error cloning repo: {e}")
        return False

def categorize_url(url: str) -> str:
    """Determine resource type."""
    url_lower = url.lower()

    if 'arxiv.org' in url_lower or 'ar5iv' in url_lower:
        return 'arxiv'
    elif 'github.com' in url_lower:
        return 'github'
    elif 'huggingface.co' in url_lower:
        return 'huggingface'
    elif any(x in url_lower for x in ['anthropic.com', 'openai.com', 'deepmind.com']):
        return 'research_article'
    elif any(x in url_lower for x in ['lesswrong.com', 'alignmentforum.org']):
        return 'community_article'
    elif 'blog.bluedot.org/p/' in url_lower:
        return 'blog_article'
    elif 'docs.google.com' in url_lower:
        return 'google_doc'
    else:
        return 'other_article'

def main():
    # Load filtered resources
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent.parent
    filtered_json = project_root / "downloads" / "bluedot_technical_ai_safety_complete" / "extracted_links" / "filtered_course_resources.json"

    if not filtered_json.exists():
        print(f"❌ Filtered resources not found: {filtered_json}")
        return

    print(f"📂 Loading resources from: {filtered_json}\n")

    with open(filtered_json, 'r') as f:
        data = json.load(f)

    # Create output directories
    output_base = project_root / "downloads" / "bluedot_technical_ai_safety_complete" / "downloaded_resources"
    output_base.mkdir(exist_ok=True)

    (output_base / "arxiv_papers").mkdir(exist_ok=True)
    (output_base / "articles").mkdir(exist_ok=True)
    (output_base / "github_repos").mkdir(exist_ok=True)
    (output_base / "other").mkdir(exist_ok=True)

    # Get high-value links by lesson
    links_by_lesson = data.get('links_by_lesson', {})
    high_value_links = set(data.get('high_value_links', []))

    # Filter to Units 1-5 only
    units_1_to_5 = {}
    for lesson_key, links in links_by_lesson.items():
        match = re.match(r'Unit (\d+), Lesson (\d+)', lesson_key)
        if match:
            unit = int(match.group(1))
            if 1 <= unit <= 5:  # Only Units 1-5
                # Filter to high-value links only
                high_value_for_lesson = [url for url in links if url in high_value_links]
                if high_value_for_lesson:
                    units_1_to_5[lesson_key] = high_value_for_lesson

    print(f"Found {len(units_1_to_5)} lessons in Units 1-5 with high-value resources\n")
    print("="*80)

    # Statistics
    stats = {
        'arxiv': {'attempted': 0, 'succeeded': 0},
        'articles': {'attempted': 0, 'succeeded': 0},
        'github': {'attempted': 0, 'succeeded': 0},
        'other': {'attempted': 0, 'succeeded': 0},
    }

    downloaded_files = []

    for lesson_key in sorted(units_1_to_5.keys()):
        links = units_1_to_5[lesson_key]

        # Parse lesson info
        match = re.match(r'Unit (\d+), Lesson (\d+)', lesson_key)
        unit = int(match.group(1))
        lesson = int(match.group(2))
        prefix = get_lesson_prefix(unit, lesson)

        print(f"\n📚 {lesson_key} ({len(links)} high-value resources)")

        for url in links:
            resource_type = categorize_url(url)

            # Download based on type
            if resource_type == 'arxiv':
                arxiv_id = extract_arxiv_id(url)
                if arxiv_id:
                    output_path = output_base / "arxiv_papers" / f"{prefix}arxiv_{arxiv_id}.pdf"

                    if output_path.exists():
                        print(f"  ✓ arXiv {arxiv_id} (already downloaded)")
                        stats['arxiv']['succeeded'] += 1
                    else:
                        print(f"  📥 Downloading arXiv {arxiv_id}...")
                        stats['arxiv']['attempted'] += 1
                        if download_arxiv_paper(arxiv_id, output_path):
                            print(f"  ✅ Saved: {output_path.name}")
                            stats['arxiv']['succeeded'] += 1
                            downloaded_files.append({
                                'lesson': lesson_key,
                                'type': 'arxiv',
                                'url': url,
                                'file': output_path.name
                            })
                        else:
                            print(f"  ❌ Failed")
                        time.sleep(2)  # Rate limiting

            elif resource_type == 'github':
                print(f"  💻 GitHub: {url}")
                stats['github']['attempted'] += 1
                if clone_github_repo(url, output_base / "github_repos", prefix):
                    print(f"  ✅ Cloned successfully")
                    stats['github']['succeeded'] += 1
                    downloaded_files.append({
                        'lesson': lesson_key,
                        'type': 'github',
                        'url': url,
                        'file': 'cloned'
                    })
                time.sleep(1)

            elif resource_type in ['research_article', 'community_article', 'blog_article']:
                domain = urlparse(url).netloc.replace('www.', '')
                print(f"  📄 {domain}")
                print(f"     {url}")
                stats['articles']['attempted'] += 1

                # Try to download
                success, filename = download_web_article(url, output_base / "articles", prefix)
                if success:
                    print(f"  ✅ Saved: {filename}")
                    stats['articles']['succeeded'] += 1
                    downloaded_files.append({
                        'lesson': lesson_key,
                        'type': 'article',
                        'url': url,
                        'file': filename
                    })
                else:
                    print(f"  ⚠️  Could not download")
                time.sleep(3)  # Rate limiting for articles

            else:
                print(f"  🔗 {url}")
                stats['other']['attempted'] += 1

    # Print summary
    print("\n" + "="*80)
    print("DOWNLOAD SUMMARY - UNITS 1-5 HIGH-VALUE RESOURCES")
    print("="*80 + "\n")

    print(f"arXiv Papers:")
    print(f"  Attempted: {stats['arxiv']['attempted']}")
    print(f"  Succeeded: {stats['arxiv']['succeeded']}")

    print(f"\nArticles:")
    print(f"  Attempted: {stats['articles']['attempted']}")
    print(f"  Succeeded: {stats['articles']['succeeded']}")

    print(f"\nGitHub Repositories:")
    print(f"  Attempted: {stats['github']['attempted']}")
    print(f"  Succeeded: {stats['github']['succeeded']}")

    print(f"\nOther Resources:")
    print(f"  Identified: {stats['other']['attempted']}")

    print(f"\n📁 Files saved to: {output_base}")

    # Save manifest
    manifest_path = output_base / "UNITS_1-5_MANIFEST.md"
    with open(manifest_path, 'w') as f:
        f.write("# High-Value Resources Downloaded - Units 1-5\n\n")
        f.write(f"**Downloaded:** {len(downloaded_files)} files\n\n")

        f.write("## Statistics\n\n")
        f.write(f"- **arXiv Papers:** {stats['arxiv']['succeeded']}\n")
        f.write(f"- **Articles:** {stats['articles']['succeeded']}\n")
        f.write(f"- **GitHub Repos:** {stats['github']['succeeded']}\n\n")

        f.write("## Files by Lesson\n\n")

        current_lesson = None
        for item in sorted(downloaded_files, key=lambda x: x['lesson']):
            if item['lesson'] != current_lesson:
                current_lesson = item['lesson']
                f.write(f"\n### {current_lesson}\n\n")

            f.write(f"- **{item['type'].upper()}**: {item['file']}\n")
            f.write(f"  - Source: {item['url']}\n")

    print(f"✅ Saved manifest to: {manifest_path}")

    # Save JSON
    json_manifest = output_base / "downloads_manifest.json"
    with open(json_manifest, 'w') as f:
        json.dump({
            'summary': stats,
            'downloaded_files': downloaded_files
        }, f, indent=2)

    print(f"✅ Saved JSON manifest to: {json_manifest}")

if __name__ == "__main__":
    main()
