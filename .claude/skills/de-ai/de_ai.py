#!/usr/bin/env python3
"""
De-AI text transformation tool.
Removes AI-generated patterns and makes text sound more human.
"""

import re
import random
from typing import List, Tuple

# Overused AI words and their replacements
AI_REPLACEMENTS = {
    # Verbs
    r'\bdelve\b': ['look into', 'check', 'explore'],
    r'\bleverage\b': ['use', 'apply', 'work with'],
    r'\butilize\b': ['use', 'apply'],
    r'\bunderscore\b': ['show', 'highlight', 'point out'],
    r'\bshowcase\b': ['show', 'demonstrate', 'present'],
    r'\bfoster\b': ['build', 'create', 'develop'],
    r'\bnavigate\b': ['handle', 'manage', 'deal with'],
    r'\bstreamline\b': ['simplify', 'speed up', 'improve'],
    r'\benhance\b': ['improve', 'boost', 'make better'],
    r'\belevate\b': ['raise', 'improve', 'lift'],
    r'\bharness\b': ['use', 'tap into'],
    r'\bcaptivate\b': ['engage', 'interest', 'grab'],

    # Adjectives
    r'\bcomprehensive\b': ['complete', 'full', 'thorough'],
    r'\bcrucial\b': ['key', 'important', 'critical'],
    r'\bpivotal\b': ['important', 'key', 'central'],
    r'\bmeticulous\b': ['careful', 'detailed', 'precise'],
    r'\bintricate\b': ['complex', 'detailed'],
    r'\bnuanced\b': ['subtle', 'complex'],
    r'\brobust\b': ['strong', 'solid', 'reliable'],
    r'\bcommendable\b': ['good', 'praiseworthy', 'impressive'],
    r'\binvaluable\b': ['useful', 'helpful', 'essential'],
    r'\bcutting-edge\b': ['new', 'latest', 'advanced'],
    r'\bever-evolving\b': ['changing', 'developing'],
    r'\bmultifaceted\b': ['complex', 'varied'],
    r'\btransformative\b': ['changing', 'powerful'],

    # Nouns
    r'\blandscape\b': ['field', 'area', 'space'],
    r'\brealm\b': ['area', 'field', 'domain'],
    r'\btapestry\b': ['mix', 'combination', 'blend'],
    r'\bsymphony\b': ['combination', 'blend'],
    r'\bsynergy\b': ['teamwork', 'collaboration'],
    r'\bparadigm\b': ['model', 'approach', 'method'],
    r'\bframework\b': ['structure', 'system', 'approach'],
    r'\bcornerstone\b': ['foundation', 'basis', 'key part'],
    r'\bunderpinning\b': ['foundation', 'basis'],
}

# Phrases to remove entirely
PHRASES_TO_REMOVE = [
    r"it's important to note that",
    r"it is important to note that",
    r"in today's fast-paced world",
    r"in today's digital age",
    r"this is a testament to",
    r"whether you're a beginner or an expert",
    r"whether you are a beginner or an expert",
    r"let's face it",
    r"at its core",
    r"strikes a balance between",
    r"from .+ to .+",  # "from X to Y" pattern
    r"not just .+, but .+",  # "not just X, but Y" pattern
    r"in an era of",
    r"in the world of",
]

def replace_ai_words(text: str) -> str:
    """Replace overused AI words with more natural alternatives."""
    for pattern, replacements in AI_REPLACEMENTS.items():
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in reversed(list(matches)):
            # Choose a random replacement
            replacement = random.choice(replacements)
            # Preserve capitalization
            if match.group()[0].isupper():
                replacement = replacement.capitalize()
            text = text[:match.start()] + replacement + text[match.end():]
    return text

def remove_phrases(text: str) -> str:
    """Remove common AI phrases entirely."""
    for phrase in PHRASES_TO_REMOVE:
        text = re.sub(phrase, '', text, flags=re.IGNORECASE)
    # Clean up extra spaces
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s+([.,!?])', r'\1', text)
    return text.strip()

def break_rhythm(text: str) -> str:
    """Break up overly smooth sentence flow."""
    lines = text.split('\n')
    result = []

    for line in lines:
        if not line.strip():
            result.append(line)
            continue

        # Split long sentences occasionally
        sentences = re.split(r'(?<=[.!?])\s+', line)
        modified = []

        for i, sentence in enumerate(sentences):
            if len(sentence) > 100 and ', ' in sentence:
                # Sometimes break at commas
                if random.random() > 0.5:
                    parts = sentence.split(', ', 1)
                    if len(parts) == 2:
                        modified.append(parts[0] + '.')
                        modified.append(parts[1].capitalize())
                    else:
                        modified.append(sentence)
                else:
                    modified.append(sentence)
            else:
                modified.append(sentence)

        result.append(' '.join(modified))

    return '\n'.join(result)

def add_human_markers(text: str) -> str:
    """Add subtle human markers like informal language."""
    # Add contractions
    contractions = [
        (r"\bdo not\b", "don't"),
        (r"\bcannot\b", "can't"),
        (r"\bwill not\b", "won't"),
        (r"\bshould not\b", "shouldn't"),
        (r"\bwould not\b", "wouldn't"),
        (r"\bcould not\b", "couldn't"),
        (r"\bit is\b", "it's"),
        (r"\bthat is\b", "that's"),
        (r"\bwhat is\b", "what's"),
        (r"\bthey are\b", "they're"),
        (r"\bwe are\b", "we're"),
    ]

    for pattern, replacement in contractions:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return text

def reduce_hedging(text: str) -> str:
    """Remove excessive hedging and qualifiers."""
    hedges = [
        r'\bperhaps\b ',
        r'\bpossibly\b ',
        r'\bseems to\b ',
        r'\bappears to\b ',
        r'\bmight be\b ',
        r'\bcould be\b ',
        r'\bsomewhat\b ',
        r'\brather\b ',
        r'\bquite\b ',
        r'\bfairly\b ',
    ]

    for hedge in hedges:
        # Only remove some hedges, not all (to keep it natural)
        if random.random() > 0.6:
            text = re.sub(hedge, '', text, flags=re.IGNORECASE)

    return text

def simplify_structure(text: str) -> str:
    """Simplify overly complex sentence structures."""
    # Remove ALL em dashes - they're a dead giveaway of AI writing
    # Replace with more natural alternatives
    text = text.replace(' — ', '. ')  # Most become periods
    text = text.replace('— ', '. ')   # Handle spacing variants
    text = text.replace(' —', '.')
    text = text.replace('—', '. ')

    # Reduce parallel structures
    # Look for repeated "She/He/They [verb]" patterns
    subject_pattern = r'^(She|He|They|It|The \w+) \w+'
    lines = text.split('. ')

    last_pattern = None
    result = []
    parallel_count = 0

    for line in lines:
        match = re.match(subject_pattern, line)
        if match and match.group(1) == last_pattern:
            parallel_count += 1
            if parallel_count > 2:
                # Vary the structure
                line = "And " + line[len(match.group(1)):].strip().lower()
        else:
            parallel_count = 0

        if match:
            last_pattern = match.group(1)
        else:
            last_pattern = None

        result.append(line)

    return '. '.join(result)

def de_ai_text(text: str, preserve_meaning: bool = True, track_changes: bool = False) -> Tuple[str, List[Tuple[str, str, str]]]:
    """
    Main transformation function.

    Args:
        text: The text to transform
        preserve_meaning: If True, be more conservative with changes
        track_changes: If True, return a list of changes made

    Returns:
        Tuple of (De-AI'd text, list of changes if track_changes=True)
    """
    if not text:
        return text, []

    changes = []
    original = text

    # Track changes for each transformation
    prev_text = text
    text = remove_phrases(text)
    if text != prev_text and track_changes:
        changes.append(("Removed AI phrases", prev_text[:50] + "...", text[:50] + "..."))

    prev_text = text
    text = replace_ai_words(text)
    if text != prev_text and track_changes:
        changes.append(("Replaced AI words", prev_text[:50] + "...", text[:50] + "..."))

    prev_text = text
    text = reduce_hedging(text)
    if text != prev_text and track_changes:
        changes.append(("Reduced hedging", prev_text[:50] + "...", text[:50] + "..."))

    prev_text = text
    text = simplify_structure(text)
    if text != prev_text and track_changes:
        changes.append(("Removed em dashes", prev_text[:50] + "...", text[:50] + "..."))

    prev_text = text
    text = add_human_markers(text)
    if text != prev_text and track_changes:
        changes.append(("Added contractions", prev_text[:50] + "...", text[:50] + "..."))

    if not preserve_meaning:
        prev_text = text
        text = break_rhythm(text)
        if text != prev_text and track_changes:
            changes.append(("Broke rhythm", prev_text[:50] + "...", text[:50] + "..."))

    # Final cleanup
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Max two newlines

    return text.strip(), changes

def create_ascii_visual(original_score: int, new_score: int, changes_count: int) -> str:
    """
    Create a cute ASCII visualization of the de-AI transformation.
    Max 7 lines tall.
    """
    improvement = original_score - new_score

    # Pick visualization based on improvement level
    if improvement >= 70:
        # Major transformation - robot to human
        visual = [
            "  🤖 → 🧑  TRANSFORMATION COMPLETE!",
            "  ╔═══════════════════════════════╗",
            f"  ║ AI Score: {original_score:3d} → {new_score:3d} (-{improvement})     ║",
            f"  ║ Changes Made: {changes_count:2d}              ║",
            "  ║ [████████████████░░] 90%      ║",
            "  ╚═══════════════════════════════╝",
            "  ✨ Now sounds authentically human!"
        ]
    elif improvement >= 40:
        # Good improvement
        visual = [
            "  🤖 → 😊  MUCH BETTER!",
            "  ┌─────────────────────────────┐",
            f"  │ AI Score: {original_score:3d} → {new_score:3d} (-{improvement})   │",
            f"  │ Changes: {changes_count:2d}                  │",
            "  │ [███████████░░░░░░] 65%      │",
            "  └─────────────────────────────┘",
            "  ✓ Significantly more natural"
        ]
    elif improvement >= 20:
        # Moderate improvement
        visual = [
            "  🤖 → 🙂  IMPROVED",
            "  ┌─────────────────────────────┐",
            f"  │ Score: {original_score} → {new_score} (-{improvement})           │",
            f"  │ {changes_count} changes applied            │",
            "  │ [██████░░░░░░░░░░] 35%       │",
            "  └─────────────────────────────┘",
            "  → Noticeably more human"
        ]
    elif improvement > 0:
        # Minor improvement
        visual = [
            "  🤖 → 🤔  SLIGHTLY ADJUSTED",
            f"  Score: {original_score} → {new_score} (-{improvement})",
            f"  Made {changes_count} small tweaks",
            "  [███░░░░░░░░░░░░] 20%",
            "  → Minor improvements applied"
        ]
    else:
        # Already human
        visual = [
            "  🧑 ✓  ALREADY HUMAN!",
            f"  Score: {original_score}/100 (excellent)",
            "  No AI patterns detected",
            "  ──────────────────────",
            "  This text sounds natural!"
        ]

    return '\n'.join(visual[:7])  # Ensure max 7 lines

def analyze_ai_score(text: str) -> Tuple[float, List[str]]:
    """
    Analyze how AI-like a text is.

    Returns:
        Tuple of (score from 0-100, list of issues found)
    """
    issues = []
    score = 0

    # Check for AI words
    for pattern in AI_REPLACEMENTS:
        if re.search(pattern, text, re.IGNORECASE):
            score += 5
            cleaned_pattern = pattern.replace(r'\b', '').replace('\\', '')
            issues.append(f"Overused word: {cleaned_pattern}")

    # Check for AI phrases
    for phrase in PHRASES_TO_REMOVE[:10]:  # Check first 10 most common
        if re.search(phrase, text, re.IGNORECASE):
            score += 10
            issues.append(f"AI phrase: {phrase[:30]}...")

    # Check for ANY em dashes (huge AI tell)
    em_dash_count = text.count('—')
    if em_dash_count > 0:
        score += 10 * min(em_dash_count, 5)  # 10 points per dash, max 50
        issues.append(f"Em dashes found ({em_dash_count}) - huge AI tell")

    # Check for parallel structures
    sentences = re.split(r'[.!?]+', text)
    starts = [s.strip().split()[0] if s.strip() else '' for s in sentences]
    if len(starts) > 3:
        most_common = max(set(starts), key=starts.count)
        if starts.count(most_common) > len(starts) / 3:
            score += 10
            issues.append(f"Repetitive sentence starts with '{most_common}'")

    # Cap at 100
    score = min(score, 100)

    return score, issues

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Read from file or stdin
        if sys.argv[1] == '-':
            text = sys.stdin.read()
        else:
            with open(sys.argv[1], 'r') as f:
                text = f.read()
    else:
        # Interactive mode
        print("Enter text to de-AI (Ctrl+D when done):")
        text = sys.stdin.read()

    # Analyze first
    score, issues = analyze_ai_score(text)

    # Transform with change tracking
    result, changes = de_ai_text(text, track_changes=True)

    # Analyze the result
    new_score, _ = analyze_ai_score(result)

    # Create visualization
    visual = create_ascii_visual(int(score), int(new_score), len(changes))

    # Output the results
    print("\n" + visual)
    print("\n" + "=" * 50)
    print("DE-AI'D TEXT:")
    print("=" * 50)
    print(result)

    # Document changes
    if changes:
        print("\n" + "=" * 50)
        print("CHANGES MADE:")
        print("=" * 50)
        for i, (change_type, before, after) in enumerate(changes, 1):
            print(f"{i}. {change_type}")
            if len(before) < 100:
                print(f"   Before: {before}")
                print(f"   After:  {after}")
            print()

    # Show original text
    print("=" * 50)
    print("ORIGINAL TEXT:")
    print("=" * 50)
    print(text)

    # Detailed issues if high AI score
    if score > 20 and issues:
        print("\n" + "=" * 50)
        print("AI PATTERNS DETECTED:")
        print("=" * 50)
        for issue in issues:
            print(f"  • {issue}")