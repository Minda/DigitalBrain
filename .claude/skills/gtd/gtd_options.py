#!/usr/bin/env python3
"""Display GTD command options concisely."""

def print_gtd_options():
    """Print GTD options in a clean, concise format."""

    options = """
╔═══════════════════════════════════════════════╗
║  🎯 GTD QUICK COMMANDS                        ║
╠═══════════════════════════════════════════════╣
║  /gtd visualize      → Current focus & next   ║
║  /gtd visualize-week → Weekly plan & capacity ║
║  /gtd tradeoffs      → Allocation options     ║
║  "let's plan my week/day" → Interactive plan  ║
╚═══════════════════════════════════════════════╝
"""
    print(options.strip())

if __name__ == "__main__":
    print_gtd_options()