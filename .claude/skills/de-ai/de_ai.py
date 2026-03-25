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

def de_ai_text(text: str, preserve_meaning: bool = True) -> str:
    """
    Main transformation function.

    Args:
        text: The text to transform
        preserve_meaning: If True, be more conservative with changes

    Returns:
        De-AI'd text that sounds more human
    """
    if not text:
        return text

    # Apply transformations
    text = remove_phrases(text)
    text = replace_ai_words(text)
    text = reduce_hedging(text)
    text = simplify_structure(text)
    text = add_human_markers(text)

    if not preserve_meaning:
        text = break_rhythm(text)

    # Final cleanup
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Max two newlines

    return text.strip()

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
    if score > 0:
        print(f"\n📊 AI Score: {score}/100")
        if issues:
            print("Issues found:")
            for issue in issues[:5]:  # Show top 5 issues
                print(f"  • {issue}")
        print()

    # Transform
    result = de_ai_text(text)

    print("=" * 50)
    print("DE-AI'D TEXT:")
    print("=" * 50)
    print(result)

    # Show improvement
    new_score, _ = analyze_ai_score(result)
    if score > 0:
        print()
        print(f"✨ New AI Score: {new_score}/100 (improved by {score - new_score} points)")