#!/usr/bin/env python3
"""
Create a comprehensive question worksheet from extracted PDF text.

Scans all PDF text files for Exercise sections and creates a structured worksheet
with:
- All questions organized by unit and lesson
- Space for raw answers
- Space for polished final answers
- Directional prompts for complex questions
"""

import re
from pathlib import Path
from typing import List, Dict, Any


def extract_exercises_from_text(text: str, unit_num: int, lesson_num: int) -> List[Dict[str, Any]]:
    """Extract exercise questions from PDF text."""

    exercises = []

    # Find the Exercises section
    exercises_match = re.search(r'Exercises\s+(.*?)(?:Continue|Shortcuts|$)', text, re.DOTALL | re.IGNORECASE)

    if not exercises_match:
        return exercises

    exercises_text = exercises_match.group(1)

    # Extract exercise sections - each has a title and question/requirements
    # Pattern: Look for capitalized headings followed by content

    # Method 1: Look for explicit questions with numbered requirements
    numbered_questions = re.finditer(
        r'([A-Z][a-z\s]+)\s+([A-Z][^.!?]*\?.*?)(?:1\.|Write\s+\d+)',
        exercises_text,
        re.DOTALL
    )

    for match in numbered_questions:
        title = match.group(1).strip()
        question_text = match.group(2).strip()

        exercises.append({
            'unit': unit_num,
            'lesson': lesson_num,
            'title': title,
            'text': question_text,
            'type': 'written_response'
        })

    # Method 2: Look for comprehension questions (numbered lists)
    if 'Comprehension' in exercises_text or 'questions' in exercises_text.lower():
        # Extract the full comprehension section
        comp_match = re.search(
            r'(Comprehension\s+questions.*?)(?:Enter your answer|Complete|Continue|$)',
            exercises_text,
            re.DOTALL | re.IGNORECASE
        )

        if comp_match:
            comp_text = comp_match.group(1)
            exercises.append({
                'unit': unit_num,
                'lesson': lesson_num,
                'title': 'Comprehension Questions',
                'text': comp_text[:2000],  # Limit length
                'type': 'comprehension'
            })

    # Method 3: Look for multiple choice questions
    mc_match = re.search(
        r'([A-Z][a-z\s]+)\s+(Which\s+statement.*?)Select an option',
        exercises_text,
        re.DOTALL | re.IGNORECASE
    )

    if mc_match:
        title = mc_match.group(1).strip()
        question = mc_match.group(2).strip()

        exercises.append({
            'unit': unit_num,
            'lesson': lesson_num,
            'title': title,
            'text': question,
            'type': 'multiple_choice'
        })

    return exercises


def create_worksheet():
    """Create the master worksheet."""

    pdf_text_dir = Path('downloads/bluedot_technical_ai_safety_complete/pdf_text')
    output_file = Path('downloads/bluedot_technical_ai_safety_complete/MASTER_WORKSHEET.md')

    print('Creating comprehensive question worksheet...\n')

    # Collect all exercises
    all_exercises = []

    for pdf_file in sorted(pdf_text_dir.glob('unit*.md')):
        # Extract unit and lesson number
        match = re.match(r'unit(\d+)_lesson(\d+)\.md', pdf_file.name)
        if not match:
            continue

        unit_num = int(match.group(1))
        lesson_num = int(match.group(2))

        print(f'Processing Unit {unit_num}, Lesson {lesson_num}...')

        # Read the file
        text = pdf_file.read_text()

        # Extract exercises
        exercises = extract_exercises_from_text(text, unit_num, lesson_num)

        print(f'  Found {len(exercises)} exercise(s)')

        all_exercises.extend(exercises)

    # Create the worksheet
    with open(output_file, 'w') as f:
        f.write('# Blue Dot Technical AI Safety Course - Master Question Worksheet\n\n')
        f.write('**Instructions:**\n\n')
        f.write('1. For each question, first fill in the "Your Raw Answer" section with your initial thoughts\n')
        f.write('2. Review and refine your answer in the "Final Answer" section\n')
        f.write('3. The final answers will be submitted to the course platform\n\n')
        f.write('---\n\n')
        f.write(f'**Total Questions Found:** {len(all_exercises)}\n\n')
        f.write('---\n\n')

        current_unit = None

        for ex in all_exercises:
            # Unit header
            if ex['unit'] != current_unit:
                current_unit = ex['unit']
                f.write(f'\n## Unit {current_unit}\n\n')

            # Lesson and exercise header
            f.write(f'### Unit {ex["unit"]}, Lesson {ex["lesson"]}: {ex["title"]}\n\n')
            f.write(f'**Type:** {ex["type"]}\n\n')

            # Question text
            f.write('**Question:**\n\n')
            f.write(f'{ex["text"]}\n\n')

            # Directional prompts based on type
            if ex['type'] == 'written_response':
                f.write('**Directional Prompts (check which angles to explore):**\n\n')
                f.write('- [ ] Technical analysis (mechanisms, how it works)\n')
                f.write('- [ ] Real-world examples and case studies\n')
                f.write('- [ ] Limitations and failure modes\n')
                f.write('- [ ] Ethical/governance implications\n')
                f.write('- [ ] Connections to other concepts in the course\n\n')

            elif ex['type'] == 'comprehension':
                f.write('**Approach:**\n\n')
                f.write('- Answer each numbered question systematically\n')
                f.write('- Use specific examples from the readings\n')
                f.write('- Keep answers concise but complete\n\n')

            elif ex['type'] == 'multiple_choice':
                f.write('**Strategy:**\n\n')
                f.write('- Eliminate clearly wrong answers first\n')
                f.write('- Look for qualifier words (always, never, only)\n')
                f.write('- Choose the most nuanced/accurate option\n\n')

            # Answer sections
            f.write('**Your Raw Answer:**\n\n')
            f.write('```\n')
            f.write('[Write your initial thoughts and answer here]\n\n\n\n\n')
            f.write('```\n\n')

            f.write('**Final Answer (for submission):**\n\n')
            f.write('```\n')
            f.write('[Polished, final answer goes here]\n\n\n\n\n')
            f.write('```\n\n')

            f.write('---\n\n')

    print(f'\n✓ Created master worksheet at: {output_file}')
    print(f'  Total exercises included: {len(all_exercises)}')

    # Also create a summary
    summary_file = output_file.parent / 'WORKSHEET_SUMMARY.md'
    with open(summary_file, 'w') as f:
        f.write('# Worksheet Summary\n\n')
        f.write(f'**Total Questions:** {len(all_exercises)}\n\n')

        by_unit = {}
        for ex in all_exercises:
            unit = ex['unit']
            if unit not in by_unit:
                by_unit[unit] = []
            by_unit[unit].append(ex)

        for unit_num in sorted(by_unit.keys()):
            f.write(f'## Unit {unit_num}\n\n')
            f.write(f'**Total questions:** {len(by_unit[unit_num])}\n\n')

            for ex in by_unit[unit_num]:
                f.write(f'- Lesson {ex["lesson"]}: {ex["title"]} ({ex["type"]})\n')

            f.write('\n')

    print(f'✓ Created summary at: {summary_file}')


if __name__ == '__main__':
    create_worksheet()
