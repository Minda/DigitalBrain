#!/usr/bin/env python3
"""Save all PDF text to markdown files for manual question extraction."""

import subprocess
from pathlib import Path
import re


def extract_pdf_text(pdf_path: Path) -> str:
    """Extract text using pdftotext."""
    try:
        result = subprocess.run(
            ['pdftotext', '-layout', str(pdf_path), '-'],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout
    except Exception as e:
        print(f"  Error: {e}")
        return ""


def main():
    pdfs_dir = Path('downloads/bluedot_technical_ai_safety 2/pdfs')
    output_dir = Path('downloads/bluedot_technical_ai_safety_complete/pdf_text')
    output_dir.mkdir(exist_ok=True)

    print(f'Extracting text from all PDFs in: {pdfs_dir}\n')

    pdf_files = sorted(pdfs_dir.glob('*.pdf'))
    print(f'Found {len(pdf_files)} PDF files\n')

    # Create one master file with all content
    master_file = output_dir.parent / 'all_units_full_text.md'

    with open(master_file, 'w') as master:
        master.write('# Blue Dot Technical AI Safety Course - Complete Text\n\n')
        master.write(f'Extracted from {len(pdf_files)} PDF files\n\n')
        master.write('---\n\n')

        for pdf_path in pdf_files:
            print(f'Processing {pdf_path.name}...')

            # Extract unit and lesson number
            match = re.match(r'unit(\d+)_lesson(\d+)\.pdf', pdf_path.name)
            if match:
                unit_num = int(match.group(1))
                lesson_num = int(match.group(2))
            else:
                print(f'  Skipping - could not parse filename')
                continue

            # Extract text
            text = extract_pdf_text(pdf_path)

            if not text:
                print(f'  No text extracted')
                continue

            print(f'  Extracted {len(text):,} characters')

            # Write to individual file
            individual_file = output_dir / f'unit{unit_num}_lesson{lesson_num}.md'
            with open(individual_file, 'w') as f:
                f.write(f'# Unit {unit_num}, Lesson {lesson_num}\n\n')
                f.write(f'**Source:** {pdf_path.name}\n\n')
                f.write('---\n\n')
                f.write(text)

            # Append to master file
            master.write(f'\n\n## Unit {unit_num}, Lesson {lesson_num}\n\n')
            master.write(f'**Source:** {pdf_path.name}\n\n')
            master.write(text)
            master.write('\n\n---\n\n')

    print(f'\n✓ Saved all PDF text to: {output_dir}')
    print(f'✓ Saved master file to: {master_file}')
    print(f'\nTotal files created: {len(list(output_dir.glob("*.md")))}')


if __name__ == '__main__':
    main()
