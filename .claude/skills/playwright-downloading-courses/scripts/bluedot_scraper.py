#!/usr/bin/env python3
"""
Comprehensive Bluedot course scraper.

Downloads all course content including:
- PDFs of each lesson page
- YouTube video links and transcripts
- Organized markdown index files
"""

import asyncio
import json
import re
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urlparse, parse_qs
import subprocess

from bluedot_browser import BluedotBrowser


class BluedotCourseScraper:
    """Scrapes and downloads complete Bluedot course content."""

    def __init__(self, course_slug: str = "technical-ai-safety", output_dir: str = "downloads/bluedot"):
        """
        Initialize the course scraper.

        Args:
            course_slug: The course identifier in the URL
            output_dir: Directory to save all downloaded content
        """
        self.course_slug = course_slug
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        self.pdfs_dir = self.output_dir / "pdfs"
        self.pdfs_dir.mkdir(exist_ok=True)

        self.transcripts_dir = self.output_dir / "transcripts"
        self.transcripts_dir.mkdir(exist_ok=True)

        self.course_data = {
            'course_name': course_slug,
            'units': []
        }

    def extract_youtube_id(self, url: str) -> Optional[str]:
        """
        Extract YouTube video ID from various URL formats.

        Args:
            url: YouTube URL

        Returns:
            Video ID or None
        """
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
            r'youtube\.com\/embed\/([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    async def download_youtube_transcript(self, video_id: str, title: str) -> Optional[str]:
        """
        Download YouTube transcript using yt-dlp or youtube-transcript-api.

        Args:
            video_id: YouTube video ID
            title: Title for the transcript file

        Returns:
            Path to saved transcript or None
        """
        # Sanitize filename
        safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
        transcript_file = self.transcripts_dir / f"{safe_title}_{video_id}.txt"

        try:
            # Try using youtube-transcript-api first (faster)
            try:
                from youtube_transcript_api import YouTubeTranscriptApi

                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                text = '\n'.join([entry['text'] for entry in transcript])

                with open(transcript_file, 'w', encoding='utf-8') as f:
                    f.write(f"# YouTube Transcript: {title}\n")
                    f.write(f"# Video ID: {video_id}\n")
                    f.write(f"# URL: https://www.youtube.com/watch?v={video_id}\n\n")
                    f.write(text)

                print(f"  ✅ Downloaded transcript: {safe_title}")
                return str(transcript_file)

            except ImportError:
                # Fall back to yt-dlp
                print(f"  ⚠️  youtube-transcript-api not installed, using yt-dlp...")
                result = subprocess.run(
                    ['yt-dlp', '--skip-download', '--write-auto-sub', '--sub-format', 'txt',
                     '-o', str(transcript_file), f'https://www.youtube.com/watch?v={video_id}'],
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    print(f"  ✅ Downloaded transcript: {safe_title}")
                    return str(transcript_file)
                else:
                    print(f"  ❌ Failed to download transcript: {result.stderr}")
                    return None

        except Exception as e:
            print(f"  ❌ Error downloading transcript for {video_id}: {e}")
            return None

    async def extract_links_and_videos(self, page, lesson_title: str) -> Dict:
        """
        Extract all links and YouTube videos from the current page.

        Args:
            page: Playwright page object
            lesson_title: Title of the lesson

        Returns:
            Dictionary containing links and videos
        """
        data = {
            'title': lesson_title,
            'url': page.url,
            'links': [],
            'youtube_videos': []
        }

        try:
            # Extract all links
            links = await page.query_selector_all('a[href]')
            for link in links:
                href = await link.get_attribute('href')
                text = await link.inner_text()

                if href and not href.startswith('#'):
                    # Make absolute URL
                    if href.startswith('/'):
                        href = f"https://bluedot.org{href}"

                    data['links'].append({
                        'text': text.strip() if text else '',
                        'url': href
                    })

            # Extract YouTube videos (iframes and embedded)
            iframes = await page.query_selector_all('iframe[src*="youtube"]')
            for iframe in iframes:
                src = await iframe.get_attribute('src')
                video_id = self.extract_youtube_id(src)

                if video_id:
                    data['youtube_videos'].append({
                        'id': video_id,
                        'url': f"https://www.youtube.com/watch?v={video_id}",
                        'embed_url': src
                    })

            # Also check for direct YouTube links
            for link_data in data['links']:
                if 'youtube.com' in link_data['url'] or 'youtu.be' in link_data['url']:
                    video_id = self.extract_youtube_id(link_data['url'])
                    if video_id and video_id not in [v['id'] for v in data['youtube_videos']]:
                        data['youtube_videos'].append({
                            'id': video_id,
                            'url': f"https://www.youtube.com/watch?v={video_id}",
                            'text': link_data['text']
                        })

        except Exception as e:
            print(f"  ⚠️  Error extracting links: {e}")

        return data

    async def save_page_as_pdf(self, page, unit_num: int, lesson_num: int, title: str) -> str:
        """
        Save the current page as PDF.

        Args:
            page: Playwright page object
            unit_num: Unit number
            lesson_num: Lesson number
            title: Page title

        Returns:
            Path to saved PDF
        """
        safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
        pdf_path = self.pdfs_dir / f"unit_{unit_num}_lesson_{lesson_num}_{safe_title}.pdf"

        try:
            await page.pdf(path=str(pdf_path), format='A4', print_background=True)
            print(f"  ✅ Saved PDF: {pdf_path.name}")
            return str(pdf_path)
        except Exception as e:
            print(f"  ❌ Error saving PDF: {e}")
            return None

    async def get_course_structure(self, browser: BluedotBrowser) -> List[Dict]:
        """
        Get the course structure (units and lessons).

        Args:
            browser: BluedotBrowser instance

        Returns:
            List of units with their lessons
        """
        print("\n📚 Discovering course structure...")

        # Navigate to the main course page
        await browser.page.goto(f"https://bluedot.org/courses/{self.course_slug}",
                               wait_until='networkidle', timeout=30000)

        await asyncio.sleep(2)

        units = []

        # Try to find all unit links
        # This will need to be adjusted based on the actual page structure
        unit_links = await browser.page.query_selector_all('a[href*="/courses/"][href*="/"]')

        discovered_units = {}

        for link in unit_links:
            href = await link.get_attribute('href')
            text = await link.inner_text()

            # Parse unit and lesson numbers from URL
            # Expected format: /courses/technical-ai-safety/1/1
            match = re.search(rf'/courses/{self.course_slug}/(\d+)/(\d+)', href)
            if match:
                unit_num = int(match.group(1))
                lesson_num = int(match.group(2))

                if unit_num not in discovered_units:
                    discovered_units[unit_num] = {
                        'unit_number': unit_num,
                        'lessons': []
                    }

                discovered_units[unit_num]['lessons'].append({
                    'lesson_number': lesson_num,
                    'url': f"https://bluedot.org{href}" if href.startswith('/') else href,
                    'title': text.strip()
                })

        # Sort and convert to list
        for unit_num in sorted(discovered_units.keys()):
            unit = discovered_units[unit_num]
            # Sort lessons by lesson number
            unit['lessons'].sort(key=lambda x: x['lesson_number'])
            units.append(unit)

        print(f"  Found {len(units)} units")
        for unit in units:
            print(f"    Unit {unit['unit_number']}: {len(unit['lessons'])} lessons")

        return units

    async def scrape_course(self):
        """
        Main method to scrape the entire course.
        """
        print("="*70)
        print("BLUEDOT COURSE SCRAPER")
        print("="*70)
        print(f"\nCourse: {self.course_slug}")
        print(f"Output directory: {self.output_dir}")
        print()

        async with BluedotBrowser(headless=False) as browser:
            # Get course structure
            units = await self.get_course_structure(browser)

            if not units:
                print("❌ No course structure found. Please check the course URL.")
                return

            self.course_data['units'] = []

            # Scrape each unit
            for unit in units:
                unit_num = unit['unit_number']
                print(f"\n{'='*70}")
                print(f"📖 UNIT {unit_num}")
                print(f"{'='*70}")

                unit_data = {
                    'unit_number': unit_num,
                    'lessons': []
                }

                # Scrape each lesson
                for lesson in unit['lessons']:
                    lesson_num = lesson['lesson_number']
                    lesson_url = lesson['url']
                    lesson_title = lesson.get('title', f'Lesson {lesson_num}')

                    print(f"\n  📄 Lesson {unit_num}.{lesson_num}: {lesson_title}")
                    print(f"     URL: {lesson_url}")

                    try:
                        # Navigate to lesson
                        await browser.page.goto(lesson_url, wait_until='networkidle', timeout=30000)
                        await asyncio.sleep(2)

                        # Get actual page title
                        page_title = await browser.page.title()

                        # Save as PDF
                        pdf_path = await self.save_page_as_pdf(
                            browser.page, unit_num, lesson_num, lesson_title
                        )

                        # Extract links and videos
                        links_data = await self.extract_links_and_videos(
                            browser.page, page_title
                        )

                        lesson_data = {
                            'lesson_number': lesson_num,
                            'title': page_title,
                            'url': lesson_url,
                            'pdf_path': pdf_path,
                            'links': links_data['links'],
                            'youtube_videos': links_data['youtube_videos'],
                            'transcript_paths': []
                        }

                        # Download YouTube transcripts
                        if links_data['youtube_videos']:
                            print(f"  📹 Found {len(links_data['youtube_videos'])} YouTube video(s)")
                            for video in links_data['youtube_videos']:
                                transcript_path = await self.download_youtube_transcript(
                                    video['id'],
                                    f"{lesson_title}_video"
                                )
                                if transcript_path:
                                    lesson_data['transcript_paths'].append(transcript_path)

                        unit_data['lessons'].append(lesson_data)

                    except Exception as e:
                        print(f"  ❌ Error scraping lesson: {e}")
                        continue

                self.course_data['units'].append(unit_data)

                # Save unit index markdown
                self.save_unit_markdown(unit_data)

            # Save complete course data
            self.save_course_summary()

            print("\n" + "="*70)
            print("✅ SCRAPING COMPLETE!")
            print("="*70)
            print(f"\nAll content saved to: {self.output_dir}")
            print(f"  - PDFs: {self.pdfs_dir}")
            print(f"  - Transcripts: {self.transcripts_dir}")
            print(f"  - Index files: {self.output_dir}/*.md")

    def save_unit_markdown(self, unit_data: Dict):
        """
        Save a markdown index file for a unit.

        Args:
            unit_data: Unit data dictionary
        """
        unit_num = unit_data['unit_number']
        md_file = self.output_dir / f"unit_{unit_num}_index.md"

        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"# Unit {unit_num} - {self.course_slug}\n\n")

            for lesson in unit_data['lessons']:
                f.write(f"## Lesson {lesson['lesson_number']}: {lesson['title']}\n\n")
                f.write(f"**URL:** {lesson['url']}\n\n")

                if lesson.get('pdf_path'):
                    f.write(f"**PDF:** `{lesson['pdf_path']}`\n\n")

                # YouTube videos
                if lesson.get('youtube_videos'):
                    f.write(f"### YouTube Videos ({len(lesson['youtube_videos'])})\n\n")
                    for i, video in enumerate(lesson['youtube_videos'], 1):
                        f.write(f"{i}. **Video ID:** {video['id']}\n")
                        f.write(f"   - URL: {video['url']}\n")
                        if video.get('text'):
                            f.write(f"   - Title: {video['text']}\n")
                        f.write("\n")

                # Transcripts
                if lesson.get('transcript_paths'):
                    f.write(f"### Transcripts\n\n")
                    for transcript in lesson['transcript_paths']:
                        f.write(f"- `{transcript}`\n")
                    f.write("\n")

                # Links
                if lesson.get('links'):
                    f.write(f"### Links ({len(lesson['links'])})\n\n")
                    for link in lesson['links']:
                        if link['text']:
                            f.write(f"- [{link['text']}]({link['url']})\n")
                        else:
                            f.write(f"- {link['url']}\n")
                    f.write("\n")

                f.write("---\n\n")

        print(f"  📝 Saved index: {md_file.name}")

    def save_course_summary(self):
        """Save a complete course summary as JSON and markdown."""
        # JSON
        json_file = self.output_dir / "course_data.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.course_data, f, indent=2)

        # Markdown
        md_file = self.output_dir / "course_index.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"# {self.course_slug.replace('-', ' ').title()} - Complete Course Index\n\n")

            total_lessons = sum(len(unit['lessons']) for unit in self.course_data['units'])
            total_videos = sum(
                len(lesson.get('youtube_videos', []))
                for unit in self.course_data['units']
                for lesson in unit['lessons']
            )

            f.write(f"**Total Units:** {len(self.course_data['units'])}\n\n")
            f.write(f"**Total Lessons:** {total_lessons}\n\n")
            f.write(f"**Total YouTube Videos:** {total_videos}\n\n")
            f.write("---\n\n")

            for unit in self.course_data['units']:
                f.write(f"## Unit {unit['unit_number']}\n\n")
                f.write(f"**Lessons:** {len(unit['lessons'])}\n\n")

                for lesson in unit['lessons']:
                    f.write(f"### {lesson['lesson_number']}. {lesson['title']}\n\n")
                    f.write(f"- [View Lesson]({lesson['url']})\n")

                    if lesson.get('pdf_path'):
                        f.write(f"- [PDF]({lesson['pdf_path']})\n")

                    if lesson.get('youtube_videos'):
                        f.write(f"- YouTube Videos: {len(lesson['youtube_videos'])}\n")

                    f.write("\n")

        print(f"\n📊 Saved course summary: {md_file.name}")


async def main():
    """Main entry point."""
    scraper = BluedotCourseScraper(
        course_slug="technical-ai-safety",
        output_dir="downloads/bluedot_technical_ai_safety"
    )

    await scraper.scrape_course()


if __name__ == "__main__":
    asyncio.run(main())