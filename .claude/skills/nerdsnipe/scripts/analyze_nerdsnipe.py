#!/usr/bin/env python3
"""
Analyze how nerdsnipeable a text is and suggest improvements.
"""

import sys
import re
from pathlib import Path
from typing import Dict

def analyze_nerdsnipe_effectiveness(text: str) -> Dict[str, int]:
    """Score text on nerdsnipe dimensions."""

    scores = {}

    # 1. Intellectual Offense (0-100)
    offense_phrases = ['offend', 'absurd', 'bothers me', 'shocking', 'ridiculous', 'can\'t believe']
    offense_count = sum(1 for phrase in offense_phrases if phrase in text.lower())
    scores['Intellectual Offense'] = min(offense_count * 25, 100)

    # 2. Low-Hanging Fruit (0-100)
    fruit_phrases = ['low-hanging', 'first', 'no one has', 'never been', 'you could be', 'unsolved']
    fruit_count = sum(1 for phrase in fruit_phrases if phrase in text.lower())
    scores['Low-Hanging Fruit'] = min(fruit_count * 20, 100)

    # 3. Concrete Problems (0-100)
    problem_count = len(re.findall(r'problem \d+|question \d+|task \d+', text.lower()))
    scores['Concrete Problems'] = min(problem_count * 10, 100)

    # 4. Clear First Steps (0-100)
    step_phrases = ['first step', 'start by', 'begin with', 'concrete', 'weekend', 'try this']
    step_count = sum(1 for phrase in step_phrases if phrase in text.lower())
    scores['First Steps Clear'] = min(step_count * 20, 100)

    # 5. Community Hooks (0-100)
    community_words = ['discord', 'community', 'collaborate', 'join', 'together', 'spreadsheet']
    community_count = sum(1 for word in community_words if word in text.lower())
    scores['Community Hooks'] = min(community_count * 25, 100)

    # 6. Visual Evidence (0-100)
    visual_markers = ['```', '│', '█', '░', '▓', '═', '╔', '┌', 'graph', 'chart', 'diagram']
    visual_count = sum(1 for marker in visual_markers if marker in text)
    scores['Visual Evidence'] = min(visual_count * 15, 100)

    # 7. Difficulty Ratings (0-100)
    if re.search(r'\[A\]|\[B\]|\[C\]|\[D\]|difficulty:', text):
        scores['Difficulty Ratings'] = 100
    elif 'easy' in text.lower() or 'hard' in text.lower():
        scores['Difficulty Ratings'] = 50
    else:
        scores['Difficulty Ratings'] = 0

    # 8. Excitement Markers (0-100)
    excitement = text.count('!') + text.count('🌟') * 5 + text.count('exciting') * 3
    scores['Excitement Markers'] = min(excitement * 10, 100)

    return scores

def generate_bar(value: int, width: int = 10) -> str:
    """Generate a progress bar."""
    filled = int(value / 100 * width)
    return '█' * filled + '░' * (width - filled)

def get_recommendation(scores: Dict[str, int]) -> str:
    """Get the top recommendation for improvement."""
    # Find weakest area
    weakest = min(scores.items(), key=lambda x: x[1])

    recommendations = {
        'Intellectual Offense': "Add 'It offends me that...' framing",
        'Low-Hanging Fruit': "Emphasize 'no one has done this' opportunities",
        'Concrete Problems': "Number your problems explicitly (Problem 1, 2, 3...)",
        'First Steps Clear': "Add 'Concrete first step:' for each problem",
        'Community Hooks': "Add Discord/collaboration mentions",
        'Visual Evidence': "Add ASCII diagrams or visual mysteries",
        'Difficulty Ratings': "Add [A/B/C/D] difficulty ratings",
        'Excitement Markers': "Add 🌟 stars to exciting problems"
    }

    return recommendations.get(weakest[0], "Add more concrete problems")

def print_analysis(scores: Dict[str, int]):
    """Print the analysis visualization."""
    overall = sum(scores.values()) // len(scores)

    print("""
╔═══════════════════════════════════════╗
║  📊 NERDSNIPE EFFECTIVENESS          ║
╠═══════════════════════════════════════╣""")

    for dimension, score in scores.items():
        bar = generate_bar(score)
        print(f"║  {dimension:20s} {bar} {score:3d}% ║")

    print(f"""╠═══════════════════════════════════════╣
║  Overall Score:         {generate_bar(overall)} {overall:2d}% ║
║  Recommendation: {get_recommendation(scores):21s}║
╚═══════════════════════════════════════╝""")

    # Detailed suggestions if score is low
    if overall < 60:
        print("\n🎯 TOP IMPROVEMENTS NEEDED:")
        for dim, score in sorted(scores.items(), key=lambda x: x[1])[:3]:
            if score < 50:
                print(f"  • {dim}: Currently at {score}% - needs work!")

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: analyze_nerdsnipe.py <file_or_text>")
        sys.exit(1)

    input_arg = ' '.join(sys.argv[1:])

    # Check if it's a file
    if Path(input_arg).exists():
        with open(input_arg, 'r') as f:
            text = f.read()
        print(f"Analyzing: {input_arg}")
    else:
        text = input_arg
        print("Analyzing provided text...")

    # Analyze
    scores = analyze_nerdsnipe_effectiveness(text)

    # Display
    print_analysis(scores)

if __name__ == "__main__":
    main()