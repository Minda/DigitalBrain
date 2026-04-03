#!/usr/bin/env python3
"""
Transform text into nerdsnipeable content that smart people can't resist.
Based on Neel Nanda's patterns for making research problems magnetic.
"""

import sys
import re
import random
from pathlib import Path
from typing import Dict, List, Tuple

class NerdsnipeTransformer:
    """Transform boring text into irresistible problems."""

    def __init__(self):
        # Organized by violation type
        self.taste_violations = {
            'inefficiency': [
                "It's absurdly inefficient that",
                "We're wasting 90% of our effort on",
                "This takes 100x longer than it should:",
                "It's computationally offensive that",
                "The overhead is grotesque when"
            ],
            'ignorance': [
                "We have no idea why",
                "It's intellectually dishonest that we pretend to understand",
                "We're flying blind with",
                "We can't even explain why",
                "It's epistemologically broken that"
            ],
            'paradox': [
                "It makes no sense that",
                "The paradox is screaming:",
                "How can it be that",
                "It defies logic that",
                "The impossible coexistence of"
            ],
            'asymmetry': [
                "The shocking asymmetry:",
                "Superhuman at X, subhuman at Y:",
                "The inexplicable gap between",
                "It's bizarrely lopsided that",
                "The capability cliff between"
            ],
            'elegance': [
                "The solution is embarrassingly crude:",
                "We're using sledgehammers for surgery when",
                "It's aesthetically painful that",
                "Such an ugly hack:",
                "The mathematical ugliness of"
            ],
            'waste': [
                "We're leaving gold on the table:",
                "It's criminal that we ignore",
                "The squandered opportunity:",
                "We throw away 99% of",
                "The neglected goldmine of"
            ],
            'stagnation': [
                "We've been stuck for years on",
                "Zero progress despite",
                "Nobody has cracked",
                "Years later, we still can't",
                "The persistent failure to"
            ],
            'assumption': [
                "Everyone assumes but no one has shown",
                "The unexamined belief that",
                "The field's blind spot:",
                "The cargo cult of",
                "The unfounded certainty that"
            ],
            'discontinuity': [
                "The suspicious threshold at exactly",
                "Why precisely at",
                "The unexplained discontinuity at",
                "The phase transition at",
                "The magic number"
            ],
            'measurement': [
                "We optimize for X while caring about Y:",
                "The metric doesn't capture",
                "We can't even measure",
                "Goodhart's law is laughing at",
                "Our metrics are theater:"
            ]
        }

        # Flatten for random selection
        self.all_violations = []
        for category in self.taste_violations.values():
            self.all_violations.extend(category)

        self.fruit_phrases = [
            "This field is incredibly young and full of low-hanging fruit",
            "Most of these problems have never been seriously studied",
            "You could be the first",
            "No one has done this systematically",
            "The fruit is hanging so low it's touching the ground"
        ]

        self.difficulty_map = {
            'easy': 'A',
            'medium': 'B',
            'hard': 'C',
            'ambitious': 'D'
        }

    def analyze_nerdsnipe_score(self, text: str) -> Dict[str, int]:
        """Analyze how nerdsnipeable the current text is."""
        scores = {
            'intellectual_offense': 0,
            'low_hanging_fruit': 0,
            'concrete_problems': 0,
            'first_steps': 0,
            'community_hooks': 0,
            'visual_evidence': 0
        }

        # Check for intellectual offense
        if any(phrase in text.lower() for phrase in ['offend', 'absurd', 'bothers me', 'shocking']):
            scores['intellectual_offense'] = 75

        # Check for low-hanging fruit language
        if 'low-hanging' in text.lower() or 'you could be first' in text.lower():
            scores['low_hanging_fruit'] = 80

        # Check for concrete problems
        if re.search(r'problem \d+|step \d+|task \d+', text.lower()):
            scores['concrete_problems'] = 60

        # Check for first steps
        if any(phrase in text.lower() for phrase in ['first step', 'start by', 'begin with', 'try this']):
            scores['first_steps'] = 70

        # Check for community
        if any(word in text.lower() for word in ['discord', 'community', 'collaborate', 'join']):
            scores['community_hooks'] = 50

        # Check for visuals
        if '```' in text or '│' in text or '█' in text:
            scores['visual_evidence'] = 60

        return scores

    def detect_violation_type(self, text: str) -> str:
        """Detect which type of intellectual violation fits best."""
        text_lower = text.lower()

        # Pattern matching for violation types
        if any(word in text_lower for word in ['waste', 'inefficient', 'slow', 'overhead']):
            return 'inefficiency'
        elif any(word in text_lower for word in ['unknown', "don't know", 'no idea', 'unexplained']):
            return 'ignorance'
        elif any(word in text_lower for word in ['but', 'yet', 'despite', 'however', 'contradiction']):
            return 'paradox'
        elif 'fail' in text_lower and '%' in text:
            return 'stagnation'
        elif any(word in text_lower for word in ['gap', 'difference', 'better at', 'worse at']):
            return 'asymmetry'
        elif any(word in text_lower for word in ['assume', 'belief', 'think', 'suppose']):
            return 'assumption'
        elif re.search(r'exactly \d+%|precisely \d+|specific', text_lower):
            return 'discontinuity'
        elif any(word in text_lower for word in ['measure', 'metric', 'optimize', 'score']):
            return 'measurement'
        elif any(word in text_lower for word in ['crude', 'ugly', 'hack', 'brute']):
            return 'elegance'
        elif any(word in text_lower for word in ['ignore', 'unused', 'untapped', 'potential']):
            return 'waste'
        else:
            return 'general'

    def add_intellectual_offense(self, text: str) -> str:
        """Add intellectual offense framing to boring statements."""
        lines = text.split('\n')
        transformed = []

        for line in lines:
            if line.strip() and not line.startswith('#'):
                # Identify key statistics or facts that need emphasis
                if re.search(r'\d+%|\d+ of \d+|\d+x', line):
                    violation_type = self.detect_violation_type(line)

                    if violation_type != 'general' and violation_type in self.taste_violations:
                        starter = random.choice(self.taste_violations[violation_type])
                    else:
                        starter = random.choice(self.all_violations)

                    # Format based on starter ending
                    if starter.endswith(':'):
                        transformed.append(f"**{starter}** {line}")
                    else:
                        transformed.append(f"**{starter} {line.lower()}**")
                else:
                    transformed.append(line)
            else:
                transformed.append(line)

        return '\n'.join(transformed)

    def add_difficulty_ratings(self, text: str) -> str:
        """Add difficulty ratings to problems."""
        # Find problems/tasks/questions
        problem_pattern = r'(Problem|Question|Task|Challenge)[\s:#]*(\d+)?[:\s]*(.*?)(?=\n|$)'

        def replace_problem(match):
            prefix = match.group(1)
            number = match.group(2) or ''
            content = match.group(3)

            # Assign difficulty based on keywords
            if any(word in content.lower() for word in ['simple', 'basic', 'start', 'replicate']):
                rating = '[A]'
            elif any(word in content.lower() for word in ['analyze', 'investigate', 'substantial']):
                rating = '[B-C]'
            elif any(word in content.lower() for word in ['complex', 'comprehensive', 'revolutionary']):
                rating = '[C-D]'
            else:
                rating = '[B]'

            # Add star for exciting ones
            star = '🌟 ' if random.random() > 0.6 else ''
            no_prior = ' [No prior work]' if random.random() > 0.5 else ''

            return f"{star}**{prefix} {number}**: {content} {rating}{no_prior}"

        return re.sub(problem_pattern, replace_problem, text)

    def add_concrete_first_steps(self, problems: List[str]) -> List[str]:
        """Add concrete first steps to each problem."""
        enhanced = []
        starters = [
            "**Concrete first step:** ",
            "**Start here:** ",
            "**This weekend:** ",
            "**Hour 1:** "
        ]

        for problem in problems:
            enhanced.append(problem)
            if 'Problem' in problem or 'Question' in problem:
                step = random.choice(starters)
                enhanced.append(f"{step}Set up the environment and try the simplest version.")

        return enhanced

    def add_visual_evidence(self, text: str) -> str:
        """Add ASCII visualizations to make mysteries visible."""
        if '0.9%' in text or 'threshold' in text.lower():
            visual = """
```
Coordination vs Connectivity:
0.0-0.8%: ░░░░░░░░░░ (near zero)
0.9%:     ████████░░ (sudden jump!)
1.0-2.0%: ██████████ (plateau)
           ↑ What happens here?
```"""
            text += '\n' + visual

        if '93%' in text and 'fail' in text.lower():
            visual = """
```
Success Rate by Agent Count:
2 agents:  ██░░░░░░░░ 20%
3 agents:  █░░░░░░░░░ 10%
4+ agents: ░░░░░░░░░░ 7%
           ↑ Why does it collapse?
```"""
            text += '\n' + visual

        return text

    def transform_to_nerdsnipe(self, text: str) -> Tuple[str, Dict]:
        """Main transformation function."""
        # Analyze original
        original_scores = self.analyze_nerdsnipe_score(text)
        original_score = sum(original_scores.values()) // len(original_scores)

        # Apply transformations
        transformed = text
        transformed = self.add_intellectual_offense(transformed)
        transformed = self.add_difficulty_ratings(transformed)
        transformed = self.add_visual_evidence(transformed)

        # Add header if it's a long document
        if len(transformed.split('\n')) > 20:
            header = f"""# {self.count_problems(transformed)} Concrete Open Problems

*{random.choice(self.fruit_phrases)}*

## Why This Should Offend You

"""
            transformed = header + transformed

        # Add footer call to action
        footer = """

## Your First Concrete Step

1. **Choose a problem rated A**
2. **Spend this weekend trying it**
3. **Post your results (negative results are valuable!)**

**What are you waiting for?**
"""
        transformed += footer

        # Analyze transformed
        new_scores = self.analyze_nerdsnipe_score(transformed)
        new_score = sum(new_scores.values()) // len(new_scores)

        improvements = {
            'original_score': original_score,
            'new_score': new_score,
            'problems_found': self.count_problems(transformed),
            'visuals_added': transformed.count('```'),
            'stars_added': transformed.count('🌟'),
        }

        return transformed, improvements

    def count_problems(self, text: str) -> int:
        """Count the number of problems in text."""
        return len(re.findall(r'(Problem|Question|Task|Challenge)[\s:#]*\d+', text))

    def print_transformation_summary(self, improvements: Dict):
        """Print a summary visualization to console."""
        score_bar = '█' * (improvements['new_score'] // 10) + '░' * (10 - improvements['new_score'] // 10)

        print(f"""
┌─────────────────────────────────────┐
│  🧲 NERDSNIPE TRANSFORMATION       │
├─────────────────────────────────────┤
│  Original Score:  ░░░░░░░░░░ {improvements['original_score']:2d}%   │
│  Transformed:     {score_bar} {improvements['new_score']:2d}%   │
├─────────────────────────────────────┤
│  ✅ Problems identified: {improvements['problems_found']:2d}        │
│  ✅ Visual evidence: {improvements['visuals_added']:2d}            │
│  ✅ Excitement stars: {improvements['stars_added']:2d}           │
│  ⚡ Ready to hook smart people!    │
└─────────────────────────────────────┘
        """)

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: nerdsnipe.py <file_or_text>")
        sys.exit(1)

    input_arg = ' '.join(sys.argv[1:])

    # Check if it's a file
    if Path(input_arg).exists():
        with open(input_arg, 'r') as f:
            text = f.read()
        output_file = Path(input_arg).stem + '_nerdsnipe.md'
    else:
        text = input_arg
        output_file = None

    # Transform
    transformer = NerdsnipeTransformer()
    transformed, improvements = transformer.transform_to_nerdsnipe(text)

    # Output
    if output_file:
        with open(output_file, 'w') as f:
            f.write(transformed)
        print(f"✅ Nerdsnipe version saved to: {output_file}")
    else:
        print("\n=== NERDSNIPE VERSION ===\n")
        print(transformed)

    # Show summary
    transformer.print_transformation_summary(improvements)

if __name__ == "__main__":
    main()