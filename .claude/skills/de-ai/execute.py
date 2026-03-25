#!/usr/bin/env python3
"""
Execute de-AI transformation as a Claude skill.
Usage: /de-ai [optional text or instructions]
"""

import sys
import os
import json
import tempfile
from pathlib import Path

# Add the skill directory to path
sys.path.insert(0, str(Path(__file__).parent))

from de_ai import de_ai_text, analyze_ai_score

def get_recent_assistant_output():
    """Get the most recent assistant output from conversation history."""
    # This would need to be implemented based on how Claude stores conversation history
    # For now, return a placeholder message
    return "Please provide text to de-AI, or copy the text you want modified."

def main():
    # Check if text was provided as argument
    if len(sys.argv) > 1:
        input_text = ' '.join(sys.argv[1:])
    else:
        # Read from stdin if piped
        if not sys.stdin.isatty():
            input_text = sys.stdin.read()
        else:
            # No input provided - try to get recent output
            print("No text provided. Looking for recent assistant output...")
            input_text = get_recent_assistant_output()

    if not input_text or input_text == "Please provide text to de-AI, or copy the text you want modified.":
        print("❌ No text to de-AI. Please provide text after /de-ai or copy the text you want modified.")
        sys.exit(1)

    # Check if it's instructions about what to modify
    if input_text.lower().startswith(('make ', 'modify ', 'change ', 'update ', 'fix ')):
        print(f"📝 Instruction received: {input_text}")
        print("Please copy the specific text you want to modify and run /de-ai again.")
        sys.exit(0)

    # Analyze the original text
    score, issues = analyze_ai_score(input_text)

    if score > 0:
        print(f"\n📊 Original AI Score: {score}/100")
        if issues and score > 20:
            print("\n🔍 Issues detected:")
            for issue in issues[:5]:
                print(f"  • {issue}")

    # Transform the text
    transformed = de_ai_text(input_text)

    # Show the result
    print("\n" + "="*60)
    print("✨ DE-AI'D VERSION")
    print("="*60 + "\n")
    print(transformed)

    # Show improvement if significant
    if score > 20:
        new_score, _ = analyze_ai_score(transformed)
        improvement = score - new_score
        print(f"\n📈 Result: AI score reduced from {score} to {new_score} (-{improvement} points)")

        if new_score > 30:
            print("\n💡 Tip: The text still has some AI patterns. Consider:")
            print("  • Adding more specific examples from your experience")
            print("  • Including actual names, dates, or numbers")
            print("  • Writing in your natural voice and rhythm")

if __name__ == "__main__":
    main()