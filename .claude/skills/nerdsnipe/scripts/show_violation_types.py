#!/usr/bin/env python3
"""
Display the different types of intellectual taste violations for nerdsnipe targeting.
"""

def show_violation_menu():
    """Display the violation types as a visual menu."""

    print("""
╔════════════════════════════════════════════════════╗
║  🎯 INTELLECTUAL TASTE VIOLATIONS                  ║
╠════════════════════════════════════════════════════╣
║                                                    ║
║  1. 🔧 INEFFICIENCY - "100x slower than needed"   ║
║  2. 🎭 IGNORANCE - "We have no idea why"          ║
║  3. ⚡ PARADOX - "X yet also not-X"               ║
║  4. ⚖️  ASYMMETRY - "Superhuman at A, fails at B"  ║
║  5. 💎 ELEGANCE - "Embarrassingly crude"          ║
║  6. 🗑️  WASTE - "Leaving gold on the table"       ║
║  7. 🕸️  STAGNATION - "Stuck for years"            ║
║  8. 🎯 ASSUMPTION - "Everyone assumes, no proof"  ║
║  9. 📈 DISCONTINUITY - "Magic threshold at X"     ║
║  10. 📏 MEASUREMENT - "Metrics are theater"       ║
║                                                    ║
╠════════════════════════════════════════════════════╣
║  Each violation targets a different intellectual  ║
║  discomfort. Choose based on what will most       ║
║  offend your audience's sense of rightness.       ║
╚════════════════════════════════════════════════════╝
    """)

def show_violation_examples():
    """Show examples of each violation type."""

    examples = {
        "INEFFICIENCY": [
            "It's computationally offensive that we train billion-parameter models for 2+2",
            "We waste 99% of compute on redundant calculations",
            "This takes 1000x longer than the theoretical minimum"
        ],
        "IGNORANCE": [
            "We deploy systems we fundamentally don't understand",
            "It's epistemologically broken that we can't explain basic behaviors",
            "We're flying blind with systems controlling billions"
        ],
        "PARADOX": [
            "How can agents fail at cooperation yet we fear coordination?",
            "Models that can't count letters write perfect sonnets",
            "The impossible coexistence of competence and incompetence"
        ],
        "ASYMMETRY": [
            "Superhuman at chess, subhuman at tic-tac-toe",
            "The shocking gap between generation and verification",
            "Writes code perfectly, can't debug a print statement"
        ],
        "ELEGANCE": [
            "We're using sledgehammers for brain surgery",
            "The solution is 10,000 lines of spaghetti code",
            "Such an ugly hack for a simple problem"
        ],
        "WASTE": [
            "Every hallucination contains patterns we ignore",
            "The untapped goldmine of error analysis",
            "We throw away 90% of the signal as noise"
        ],
        "STAGNATION": [
            "Five years later, still can't get agents to ask questions",
            "Zero progress on cooperation despite billions invested",
            "The field has been stuck at this barrier since 2019"
        ],
        "ASSUMPTION": [
            "Everyone assumes scaling will solve this, but no evidence",
            "The cargo cult of 'emergent properties'",
            "The unexamined belief that bigger is smarter"
        ],
        "DISCONTINUITY": [
            "Why exactly 0.9% connectivity? Not 0.8%, not 1.0%",
            "The phase transition at precisely 7B parameters",
            "The suspicious threshold at exactly 93% failure"
        ],
        "MEASUREMENT": [
            "We optimize for benchmark scores while actual capability regresses",
            "Goodhart's law is laughing at our safety metrics",
            "The metric captures everything except what matters"
        ]
    }

    for violation, examples_list in examples.items():
        print(f"\n{violation}:")
        for i, example in enumerate(examples_list, 1):
            print(f"  {i}. {example}")

def analyze_text_for_violations(text: str):
    """Suggest which violations to target based on text content."""

    print("\n📊 VIOLATION ANALYSIS")
    print("=" * 50)

    violations_found = []

    # Check for different violation indicators
    if "%" in text or "times" in text:
        violations_found.append(("INEFFICIENCY", "Found metrics suggesting waste"))

    if any(word in text.lower() for word in ["don't know", "unknown", "mystery"]):
        violations_found.append(("IGNORANCE", "Found knowledge gaps"))

    if any(word in text.lower() for word in ["but", "yet", "despite", "however"]):
        violations_found.append(("PARADOX", "Found contradictions"))

    if "fail" in text.lower():
        violations_found.append(("STAGNATION", "Found persistent failures"))

    if any(word in text.lower() for word in ["better", "worse", "gap"]):
        violations_found.append(("ASYMMETRY", "Found capability imbalances"))

    if violations_found:
        print("Suggested violations to emphasize:")
        for violation, reason in violations_found:
            print(f"  • {violation}: {reason}")
    else:
        print("No obvious violations detected. Consider:")
        print("  • ASSUMPTION - Challenge accepted beliefs")
        print("  • IGNORANCE - Highlight unknown mechanisms")

    print("\n" + "=" * 50)

def main():
    """Main entry point."""
    import sys

    if len(sys.argv) > 1:
        # Analyze provided text
        text = " ".join(sys.argv[1:])
        analyze_text_for_violations(text)
    else:
        # Show menu
        show_violation_menu()
        print("\nShow examples? (y/n): ", end="")
        if input().lower() == 'y':
            show_violation_examples()

if __name__ == "__main__":
    main()