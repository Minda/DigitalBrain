#!/usr/bin/env python3
"""
Full Bluedot course scraper that visits every discovered lesson URL.
"""

import asyncio
import json
import re
from pathlib import Path
from typing import List, Dict, Optional

from bluedot_browser import BluedotBrowser


class BluedotFullScraper:
    """Complete course scraper using discovered URLs."""

    def __init__(self, course_slug: str = "technical-ai-safety", output_dir: str = "downloads/bluedot"):
        self.course_slug = course_slug
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.pdfs_dir = self.output_dir / "pdfs"
        self.pdfs_dir.mkdir(exist_ok=True)

        self.transcripts_dir = self.output_dir / "transcripts"
        self.transcripts_dir.mkdir(exist_ok=True)

    def extract_youtube_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL."""
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

    async def download_youtube_transcript(self, video_id: str, unit_num: int, lesson_num: int) -> Optional[str]:
        """Download YouTube transcript."""
        transcript_file = self.transcripts_dir / f"unit{unit_num}_lesson{lesson_num}_video_{video_id}.txt"

        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            text = '\n'.join([entry['text'] for entry in transcript])

            with open(transcript_file, 'w', encoding='utf-8') as f:
                f.write(f"# Unit {unit_num}, Lesson {lesson_num} - Video Transcript\n")
                f.write(f"# Video ID: {video_id}\n")
                f.write(f"# URL: https://www.youtube.com/watch?v={video_id}\n\n")
                f.write(text)

            print(f"    ✅ Transcript: {video_id}")
            return str(transcript_file)
        except Exception as e:
            print(f"    ⚠️  Transcript error for {video_id}: {e}")
            return None

    async def extract_page_data(self, page, unit_num: int, lesson_num: int) -> Dict:
        """Extract all data from a lesson page."""
        data = {
            'unit': unit_num,
            'lesson': lesson_num,
            'url': page.url,
            'title': await page.title(),
            'links': [],
            'youtube_videos': [],
            'transcript_paths': []
        }

        try:
            # Extract links
            links = await page.query_selector_all('a[href]')
            for link in links:
                href = await link.get_attribute('href')
                text = (await link.inner_text()).strip()

                if href and not href.startswith('#'):
                    if href.startswith('/'):
                        href = f"https://bluedot.org{href}"
                    data['links'].append({'text': text, 'url': href})

            # Extract YouTube videos
            iframes = await page.query_selector_all('iframe[src*="youtube"]')
            for iframe in iframes:
                src = await iframe.get_attribute('src')
                video_id = self.extract_youtube_id(src)
                if video_id and video_id not in [v['id'] for v in data['youtube_videos']]:
                    data['youtube_videos'].append({
                        'id': video_id,
                        'url': f"https://www.youtube.com/watch?v={video_id}"
                    })

            # Check links for YouTube URLs
            for link_data in data['links']:
                if 'youtube.com' in link_data['url'] or 'youtu.be' in link_data['url']:
                    video_id = self.extract_youtube_id(link_data['url'])
                    if video_id and video_id not in [v['id'] for v in data['youtube_videos']]:
                        data['youtube_videos'].append({
                            'id': video_id,
                            'url': f"https://www.youtube.com/watch?v={video_id}",
                            'text': link_data['text']
                        })

            # Download transcripts
            for video in data['youtube_videos']:
                transcript_path = await self.download_youtube_transcript(
                    video['id'], unit_num, lesson_num
                )
                if transcript_path:
                    data['transcript_paths'].append(transcript_path)

        except Exception as e:
            print(f"    ⚠️  Error extracting data: {e}")

        return data

    async def save_as_pdf(self, page, unit_num: int, lesson_num: int) -> Optional[str]:
        """Save page as PDF."""
        pdf_path = self.pdfs_dir / f"unit{unit_num}_lesson{lesson_num}.pdf"
        try:
            await page.pdf(path=str(pdf_path), format='A4', print_background=True)
            print(f"    ✅ PDF saved")
            return str(pdf_path)
        except Exception as e:
            print(f"    ❌ PDF error: {e}")
            return None

    async def scrape_all_lessons(self):
        """Scrape all lessons from the course."""
        print("="*70)
        print("BLUEDOT FULL COURSE SCRAPER")
        print("="*70)

        # Define all lesson URLs manually based on what we discovered
        lessons = []

        # Unit 1: 1 lesson (we know this exists)
        for i in range(1, 2):  # Just lesson 1
            lessons.append((1, i))

        # Unit 2: 4 lessons
        for i in range(1, 5):
            lessons.append((2, i))

        # Unit 3: 6 lessons
        for i in range(1, 7):
            lessons.append((3, i))

        # Unit 4: 2 lessons
        for i in range(1, 3):
            lessons.append((4, i))

        # Unit 5: 3 lessons
        for i in range(1, 4):
            lessons.append((5, i))

        # Unit 6: 7 lessons
        for i in range(1, 8):
            lessons.append((6, i))

        print(f"\nTotal lessons to scrape: {len(lessons)}")
        print()

        all_data = []

        async with BluedotBrowser(headless=False) as browser:
            for unit_num, lesson_num in lessons:
                url = f"https://bluedot.org/courses/{self.course_slug}/{unit_num}/{lesson_num}"

                print(f"📄 Unit {unit_num}, Lesson {lesson_num}")
                print(f"   {url}")

                try:
                    # Navigate to lesson
                    await browser.page.goto(url, wait_until='networkidle', timeout=45000)
                    await asyncio.sleep(2)

                    # Save PDF
                    pdf_path = await self.save_as_pdf(browser.page, unit_num, lesson_num)

                    # Extract data
                    lesson_data = await self.extract_page_data(browser.page, unit_num, lesson_num)
                    lesson_data['pdf_path'] = pdf_path

                    all_data.append(lesson_data)

                    # Show stats
                    if lesson_data['youtube_videos']:
                        print(f"    📹 Videos: {len(lesson_data['youtube_videos'])}")
                    print(f"    🔗 Links: {len(lesson_data['links'])}")
                    print()

                except Exception as e:
                    print(f"    ❌ Error: {e}\n")
                    continue

        # Save everything
        self.save_course_data(all_data)

        print("="*70)
        print("✅ SCRAPING COMPLETE!")
        print("="*70)
        print(f"\nResults saved to: {self.output_dir}")

    def save_course_data(self, all_data: List[Dict]):
        """Save all course data to files."""
        # Group by unit
        units = {}
        for lesson in all_data:
            unit_num = lesson['unit']
            if unit_num not in units:
                units[unit_num] = []
            units[unit_num].append(lesson)

        # Save per-unit markdown files
        for unit_num, lessons in sorted(units.items()):
            md_file = self.output_dir / f"unit_{unit_num}_complete.md"

            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(f"# Unit {unit_num} - {self.course_slug}\n\n")
                f.write(f"**Lessons:** {len(lessons)}\n\n")
                f.write("---\n\n")

                for lesson in sorted(lessons, key=lambda x: x['lesson']):
                    f.write(f"## Lesson {lesson['lesson']}: {lesson['title']}\n\n")
                    f.write(f"**URL:** {lesson['url']}\n\n")

                    if lesson.get('pdf_path'):
                        f.write(f"**PDF:** `{lesson['pdf_path']}`\n\n")

                    # YouTube videos
                    if lesson.get('youtube_videos'):
                        f.write(f"### YouTube Videos ({len(lesson['youtube_videos'])})\n\n")
                        for i, video in enumerate(lesson['youtube_videos'], 1):
                            f.write(f"{i}. **{video['id']}**\n")
                            f.write(f"   - [Watch on YouTube]({video['url']})\n")
                            if video.get('text'):
                                f.write(f"   - Title: {video['text']}\n")
                            f.write("\n")

                    # Transcripts
                    if lesson.get('transcript_paths'):
                        f.write(f"### Transcripts\n\n")
                        for transcript in lesson['transcript_paths']:
                            f.write(f"- `{transcript}`\n")
                        f.write("\n")

                    # Links (filter out duplicates and navigation)
                    unique_links = []
                    seen_urls = set()
                    for link in lesson.get('links', []):
                        if link['url'] not in seen_urls and link['text']:
                            unique_links.append(link)
                            seen_urls.add(link['url'])

                    if unique_links:
                        f.write(f"### Relevant Links ({len(unique_links)})\n\n")
                        for link in unique_links[:20]:  # Limit to first 20 to avoid clutter
                            if link['text']:
                                f.write(f"- [{link['text']}]({link['url']})\n")
                        f.write("\n")

                    f.write("---\n\n")

            print(f"📝 Saved: {md_file.name}")

        # Save complete JSON
        json_file = self.output_dir / "complete_course_data.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2)
        print(f"💾 Saved: {json_file.name}")

        # Save master index
        self.save_master_index(units)

    def save_master_index(self, units: Dict):
        """Save a master index of the entire course."""
        md_file = self.output_dir / "COURSE_INDEX.md"

        total_lessons = sum(len(lessons) for lessons in units.values())
        total_videos = sum(
            len(lesson.get('youtube_videos', []))
            for lessons in units.values()
            for lesson in lessons
        )

        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"# {self.course_slug.replace('-', ' ').title()}\n\n")
            f.write(f"## Course Overview\n\n")
            f.write(f"- **Total Units:** {len(units)}\n")
            f.write(f"- **Total Lessons:** {total_lessons}\n")
            f.write(f"- **Total YouTube Videos:** {total_videos}\n\n")
            f.write("---\n\n")

            for unit_num, lessons in sorted(units.items()):
                f.write(f"## Unit {unit_num}\n\n")
                f.write(f"**Lessons:** {len(lessons)}\n\n")

                for lesson in sorted(lessons, key=lambda x: x['lesson']):
                    f.write(f"### {lesson['lesson']}. {lesson['title']}\n\n")
                    f.write(f"- [View Lesson]({lesson['url']})\n")

                    if lesson.get('pdf_path'):
                        f.write(f"- [PDF]({lesson['pdf_path']})\n")

                    if lesson.get('youtube_videos'):
                        f.write(f"- Videos: {len(lesson['youtube_videos'])}\n")

                    f.write("\n")

                f.write("---\n\n")

        print(f"📋 Saved master index: {md_file.name}")


async def main():
    scraper = BluedotFullScraper(
        course_slug="technical-ai-safety",
        output_dir="downloads/bluedot_technical_ai_safety_complete"
    )
    await scraper.scrape_all_lessons()


if __name__ == "__main__":
    asyncio.run(main())