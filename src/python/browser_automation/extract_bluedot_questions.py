#!/usr/bin/env python3
"""
Extract all questions from Blue Dot Technical AI Safety course (Units 1-6).

This script navigates the Blue Dot course website and extracts all exercise questions
from units 1-6, saving them to a structured markdown file.
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright, Page
from typing import List, Dict, Any


async def extract_unit_questions(page: Page, unit_number: int) -> Dict[str, Any]:
    """
    Navigate to a unit page and extract all questions.

    Args:
        page: Playwright page object
        unit_number: Unit number (1-6)

    Returns:
        Dictionary with unit structure and questions
    """
    # Navigate to the unit page
    url = f"https://bluedot.org/courses/technical-ai-safety/{unit_number}/"
    print(f"\nNavigating to Unit {unit_number}: {url}")

    await page.goto(url, wait_until="networkidle", timeout=60000)
    await asyncio.sleep(2)  # Give time for dynamic content to load

    # Extract unit title
    unit_title = await page.locator("h1").first.text_content() if await page.locator("h1").count() > 0 else f"Unit {unit_number}"
    unit_title = unit_title.strip() if unit_title else f"Unit {unit_number}"

    print(f"Unit title: {unit_title}")

    # Extract lessons and questions
    lessons = []

    # Try to find all lesson sections
    lesson_sections = await page.locator('[class*="lesson"], [class*="section"], article, section').all()

    print(f"Found {len(lesson_sections)} potential lesson sections")

    # Also try to extract any visible questions/exercises
    # Look for common patterns: input fields, textareas, multiple choice options
    questions = []

    # Extract all visible text to understand structure
    page_content = await page.content()

    # Look for forms, questions, exercises
    form_elements = await page.locator('form, [class*="question"], [class*="exercise"], [class*="quiz"]').all()

    for idx, element in enumerate(form_elements):
        try:
            question_text = await element.text_content()
            if question_text and len(question_text.strip()) > 10:
                questions.append({
                    'index': idx,
                    'text': question_text.strip()[:500],  # First 500 chars
                    'html': await element.inner_html()
                })
        except Exception as e:
            print(f"Error extracting element {idx}: {e}")

    return {
        'unit_number': unit_number,
        'title': unit_title,
        'url': url,
        'lessons': lessons,
        'questions': questions,
        'page_content_length': len(page_content)
    }


async def main():
    """Main extraction function."""

    output_dir = Path("/Users/min/Documents/Projects/DigitalBrain/downloads/bluedot_technical_ai_safety_complete")
    output_file = output_dir / "extracted_questions_raw.json"

    all_units = []

    async with async_playwright() as p:
        # Launch a fresh browser instance
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = context.pages[0] if context.pages else await context.new_page()

        # Navigate to the course and wait for user to log in
        print("\n" + "="*60)
        print("MANUAL LOGIN REQUIRED")
        print("="*60)
        print(f"\nNavigating to Blue Dot course...")

        try:
            await page.goto("https://bluedot.org/courses/technical-ai-safety/1/", timeout=60000)
        except Exception as e:
            print(f"Note: Page load may have timed out, but that's okay.")
            print(f"The browser window should be open.\n")

        print("\nPlease log in to the Blue Dot course in the browser window.")
        print("You have 60 seconds to log in...")
        print("The script will automatically continue after the wait period.\n")

        # Wait for user to log in (60 seconds)
        for i in range(60, 0, -10):
            print(f"  {i} seconds remaining...")
            await asyncio.sleep(10)

        print("\nContinuing with extraction...\n")

        # Extract questions from units 1-6
        for unit_num in range(1, 7):
            try:
                unit_data = await extract_unit_questions(page, unit_num)
                all_units.append(unit_data)
                print(f"Extracted {len(unit_data['questions'])} question elements from Unit {unit_num}")
            except Exception as e:
                print(f"Error extracting Unit {unit_num}: {e}")
                all_units.append({
                    'unit_number': unit_num,
                    'error': str(e)
                })

        await browser.close()

    # Save raw extraction
    with open(output_file, 'w') as f:
        json.dump(all_units, f, indent=2)

    print(f"\n✓ Saved raw extraction to {output_file}")
    print(f"  Total units processed: {len(all_units)}")

    # Create initial markdown summary
    create_markdown_summary(all_units, output_dir)


def create_markdown_summary(units: List[Dict[str, Any]], output_dir: Path):
    """Create a markdown summary of extracted content."""

    summary_file = output_dir / "extraction_summary.md"

    with open(summary_file, 'w') as f:
        f.write("# Blue Dot Course - Question Extraction Summary\n\n")
        f.write("This file summarizes the automated extraction from the Blue Dot course website.\n\n")

        for unit in units:
            unit_num = unit.get('unit_number', '?')
            f.write(f"## Unit {unit_num}\n\n")

            if 'error' in unit:
                f.write(f"**Error:** {unit['error']}\n\n")
                continue

            f.write(f"**Title:** {unit.get('title', 'Unknown')}\n\n")
            f.write(f"**URL:** {unit.get('url', '')}\n\n")
            f.write(f"**Question elements found:** {len(unit.get('questions', []))}\n\n")

            # Show first few question snippets
            questions = unit.get('questions', [])
            if questions:
                f.write("**Sample questions:**\n\n")
                for q in questions[:3]:  # First 3 only
                    f.write(f"- {q['text'][:200]}...\n")
                f.write("\n")

    print(f"✓ Created summary at {summary_file}")


if __name__ == "__main__":
    asyncio.run(main())
