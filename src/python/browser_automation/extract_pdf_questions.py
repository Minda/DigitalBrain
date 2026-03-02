#!/usr/bin/env python3
"""
Extract questions from Blue Dot course PDFs.

This script extracts text from all course PDF files and identifies exercise questions.

Dependencies:
    /// script
    dependencies = ["pypdf"]
    ///
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any
from pypdf import PdfReader


def extract_pdf_text(pdf_path: Path) -> str:
    """Extract all text from a PDF file."""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    text += f"\n--- Page {page_num + 1} ---\n"
                    text += page.extract_text()
                except Exception as e:
                    print(f"Error extracting page {page_num + 1} from {pdf_path.name}: {e}")
            return text
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return ""


def identify_questions(text: str, unit_num: int, lesson_num: int) -> List[Dict[str, Any]]:
    """
    Identify questions in the extracted text.

    Looks for patterns like:
    - "Question" or "Exercise" headers
    - Multiple choice indicators (A, B, C, D)
    - Written response prompts
    - Reflection questions
    """
    questions = []

    # Split into sections
    sections = re.split(r'\n---\s*Page\s+\d+\s*---\n', text)

    # Patterns to look for
    question_patterns = [
        r'(?i)(?:question|exercise|task|reflection)\s*\d*[:\.]?\s*(.{20,500})',
        r'(?i)write\s+(?:a|your)\s+(?:response|answer|reflection).{20,200}',
        r'(?i)explain\s+(?:in\s+your\s+own\s+words|how|why|what).{20,200}',
        r'(?i)(?:how|what|why|when|where|who)\s+(?:do|does|did|will|would|could|should).{20,200}[\?]',
    ]

    full_text = '\n'.join(sections)

    # Look for explicit exercise sections
    exercise_matches = re.finditer(r'(?i)(?:exercise|question|task|reflection)\s*\d*[:\.]?\s*(.+?)(?=(?:exercise|question|task|reflection)\s*\d*[:\.]|$)', full_text, re.DOTALL)

    for match in exercise_matches:
        question_text = match.group(0).strip()
        if len(question_text) > 30 and len(question_text) < 2000:  # Reasonable question length
            questions.append({
                'unit': unit_num,
                'lesson': lesson_num,
                'text': question_text[:1000],  # Limit to first 1000 chars
                'type': 'extracted'
            })

    return questions


def process_all_pdfs():
    """Process all PDF files and extract questions."""

    pdf_dir = Path("/Users/min/Documents/Projects/DigitalBrain/downloads/bluedot_technical_ai_safety 2/pdfs")
    output_dir = Path("/Users/min/Documents/Projects/DigitalBrain/downloads/bluedot_technical_ai_safety_complete")

    all_content = {}
    all_questions = []

    # Process each PDF
    pdf_files = sorted(pdf_dir.glob("unit*.pdf"))

    print(f"\nFound {len(pdf_files)} PDF files\n")

    for pdf_file in pdf_files:
        print(f"Processing: {pdf_file.name}")

        # Extract unit and lesson numbers from filename
        match = re.match(r'unit(\d+)_lesson(\d+)\.pdf', pdf_file.name)
        if not match:
            print(f"  Skipping - couldn't parse filename")
            continue

        unit_num = int(match.group(1))
        lesson_num = int(match.group(2))

        # Extract text
        text = extract_pdf_text(pdf_file)
        print(f"  Extracted {len(text)} characters")

        # Store full text
        all_content[pdf_file.stem] = {
            'unit': unit_num,
            'lesson': lesson_num,
            'filename': pdf_file.name,
            'text_length': len(text),
            'text': text
        }

        # Identify questions
        questions = identify_questions(text, unit_num, lesson_num)
        print(f"  Found {len(questions)} potential questions")

        all_questions.extend(questions)

    # Save extracted text
    text_output = output_dir / "extracted_pdf_text.json"
    with open(text_output, 'w') as f:
        json.dump(all_content, f, indent=2)
    print(f"\n✓ Saved all extracted text to {text_output}")

    # Save questions
    questions_output = output_dir / "extracted_questions.json"
    with open(questions_output, 'w') as f:
        json.dump(all_questions, f, indent=2)
    print(f"✓ Saved {len(all_questions)} questions to {questions_output}")

    # Create markdown summary
    create_questions_markdown(all_questions, all_content, output_dir)


def create_questions_markdown(questions: List[Dict[str, Any]], content: Dict[str, Any], output_dir: Path):
    """Create a markdown file with all extracted questions."""

    md_file = output_dir / "all_extracted_questions.md"

    with open(md_file, 'w') as f:
        f.write("# Blue Dot Technical AI Safety - All Extracted Questions\n\n")
        f.write(f"Total questions found: {len(questions)}\n\n")
        f.write("---\n\n")

        # Group by unit
        current_unit = None
        for q in sorted(questions, key=lambda x: (x['unit'], x['lesson'])):
            if q['unit'] != current_unit:
                current_unit = q['unit']
                f.write(f"\n## Unit {current_unit}\n\n")

            f.write(f"### Lesson {q['lesson']}\n\n")
            f.write(f"{q['text']}\n\n")
            f.write("---\n\n")

    print(f"✓ Created markdown summary at {md_file}")

    # Also create a summary with full PDF text organized by unit/lesson
    full_text_md = output_dir / "all_pdf_content.md"
    with open(full_text_md, 'w') as f:
        f.write("# Blue Dot Course - All PDF Content\n\n")

        for key in sorted(content.keys()):
            item = content[key]
            f.write(f"## Unit {item['unit']}, Lesson {item['lesson']}\n\n")
            f.write(f"**File:** {item['filename']}\n\n")
            f.write(f"**Content:**\n\n")
            f.write(f"```\n{item['text'][:5000]}\n...\n```\n\n")  # First 5000 chars
            f.write("---\n\n")

    print(f"✓ Created full content summary at {full_text_md}")


if __name__ == "__main__":
    process_all_pdfs()
