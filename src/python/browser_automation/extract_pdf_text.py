#!/usr/bin/env python3
"""
Extract text content from course PDFs to verify they contain actual content.

Uses pdftotext and PyPDF2 to extract text, then analyzes:
- Total text length
- Keyword presence (AI safety, alignment, etc.)
- Link presence in text
- Whether PDF seems to have real content vs. just being a rendered page
"""

import subprocess
from pathlib import Path
import re
from collections import defaultdict

def extract_text_with_pdftotext(pdf_path: Path) -> str:
    """Extract text using pdftotext command-line tool."""
    try:
        result = subprocess.run(
            ['pdftotext', '-layout', str(pdf_path), '-'],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"  ⚠️  Error with pdftotext: {e}")
        return None

def extract_text_with_pypdf(pdf_path: Path) -> str:
    """Extract text using PyPDF2 library."""
    try:
        import PyPDF2
        text_parts = []
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text_parts.append(page.extract_text())
        return '\n'.join(text_parts)
    except ImportError:
        return None
    except Exception as e:
        print(f"  ⚠️  Error with PyPDF2: {e}")
        return None

def analyze_text(text: str, pdf_name: str) -> dict:
    """Analyze extracted text for content quality."""
    if not text:
        return {
            'has_text': False,
            'text_length': 0,
            'word_count': 0,
            'has_content': False
        }

    # Clean up text
    text_clean = ' '.join(text.split())

    # Count words
    word_count = len(text_clean.split())

    # Look for AI safety keywords
    keywords = [
        r'\bAI safety\b',
        r'\balignment\b',
        r'\bRLHF\b',
        r'\breward\b',
        r'\btransform(er|ers)\b',
        r'\bmodel\b',
        r'\bevaluation\b',
        r'\bcapabilit(y|ies)\b',
        r'\bmechanistic interpretability\b',
        r'\badversarial\b',
        r'\bscalable oversight\b',
        r'\bconstitutional AI\b',
    ]

    keyword_matches = defaultdict(int)
    for keyword in keywords:
        matches = re.findall(keyword, text_clean, re.IGNORECASE)
        if matches:
            keyword_matches[keyword] = len(matches)

    # Extract URLs from text
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+[^\s<>"{}|\\^`\[\].,;:!?\)]'
    urls = re.findall(url_pattern, text)

    # Check if it looks like it has real content
    has_content = (
        word_count > 100 and  # At least 100 words
        len(keyword_matches) > 0  # Has some AI safety keywords
    )

    return {
        'has_text': True,
        'text_length': len(text),
        'word_count': word_count,
        'keyword_matches': dict(keyword_matches),
        'total_keywords_found': sum(keyword_matches.values()),
        'unique_urls': len(set(urls)),
        'urls': list(set(urls))[:10],  # First 10 unique URLs
        'has_content': has_content,
        'first_200_chars': text_clean[:200] if text_clean else ''
    }

def main():
    # Find PDFs directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent.parent
    pdfs_dir = project_root / "downloads" / "bluedot_technical_ai_safety_complete" / "pdfs"

    if not pdfs_dir.exists():
        print(f"❌ PDFs directory not found: {pdfs_dir}")
        return

    print(f"📂 Analyzing PDFs in: {pdfs_dir}\n")

    pdf_files = sorted(pdfs_dir.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files\n")
    print("="*80)

    results = {}
    summary_stats = {
        'has_text': 0,
        'no_text': 0,
        'has_content': 0,
        'total_words': 0,
        'total_urls': 0
    }

    for pdf_path in pdf_files:
        print(f"\n📄 {pdf_path.name}")

        # Try pdftotext first, then PyPDF2
        text = extract_text_with_pdftotext(pdf_path)
        if text is None:
            print("  ⚠️  pdftotext not available, trying PyPDF2...")
            text = extract_text_with_pypdf(pdf_path)

        if text is None:
            print("  ❌ Could not extract text with any method")
            summary_stats['no_text'] += 1
            continue

        # Analyze the text
        analysis = analyze_text(text, pdf_path.name)

        if analysis['has_text']:
            summary_stats['has_text'] += 1
            summary_stats['total_words'] += analysis['word_count']
            summary_stats['total_urls'] += analysis['unique_urls']

            if analysis['has_content']:
                summary_stats['has_content'] += 1

            print(f"  ✅ Extracted {analysis['word_count']} words")
            print(f"  📊 Keywords found: {analysis['total_keywords_found']}")
            print(f"  🔗 Unique URLs: {analysis['unique_urls']}")

            if analysis['total_keywords_found'] > 0:
                top_keywords = sorted(
                    analysis['keyword_matches'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:3]
                print(f"  🏷️  Top keywords: {', '.join(f'{k}({v})' for k, v in top_keywords)}")

            if not analysis['has_content']:
                print(f"  ⚠️  Warning: Low content quality")

            # Show preview
            if analysis['first_200_chars']:
                print(f"  📝 Preview: {analysis['first_200_chars']}...")

        results[pdf_path.name] = analysis

    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80 + "\n")

    print(f"Total PDFs: {len(pdf_files)}")
    print(f"PDFs with text: {summary_stats['has_text']}")
    print(f"PDFs without text: {summary_stats['no_text']}")
    print(f"PDFs with good content: {summary_stats['has_content']}")
    print(f"\nTotal words extracted: {summary_stats['total_words']:,}")
    print(f"Average words per PDF: {summary_stats['total_words'] // len(pdf_files) if pdf_files else 0:,}")
    print(f"Total unique URLs found: {summary_stats['total_urls']}")

    # Save results
    output_dir = pdfs_dir.parent / "pdf_analysis"
    output_dir.mkdir(exist_ok=True)

    # Save detailed analysis
    import json
    json_path = output_dir / "pdf_text_analysis.json"
    with open(json_path, 'w') as f:
        json.dump({
            'summary': summary_stats,
            'pdfs': results
        }, f, indent=2)

    print(f"\n✅ Saved analysis to: {json_path}")

    # Save URLs found in PDFs
    all_urls = []
    for pdf_name, analysis in results.items():
        if 'urls' in analysis:
            for url in analysis['urls']:
                all_urls.append({'pdf': pdf_name, 'url': url})

    if all_urls:
        urls_md_path = output_dir / "urls_found_in_pdfs.md"
        with open(urls_md_path, 'w') as f:
            f.write("# URLs Found in Course PDFs\n\n")
            f.write(f"**Total unique URLs:** {summary_stats['total_urls']}\n\n")

            # Group by PDF
            by_pdf = defaultdict(list)
            for item in all_urls:
                by_pdf[item['pdf']].append(item['url'])

            for pdf_name in sorted(by_pdf.keys()):
                f.write(f"## {pdf_name}\n\n")
                for url in sorted(set(by_pdf[pdf_name])):
                    f.write(f"- {url}\n")
                f.write("\n")

        print(f"✅ Saved URLs to: {urls_md_path}")

    # Identify problematic PDFs
    problematic = [
        name for name, analysis in results.items()
        if not analysis.get('has_content', False)
    ]

    if problematic:
        print(f"\n⚠️  PDFs with low content quality ({len(problematic)}):")
        for name in problematic:
            print(f"  - {name}")

if __name__ == "__main__":
    main()
