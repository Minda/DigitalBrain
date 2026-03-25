#!/bin/bash
# Add this to your .zshrc or .bashrc to display GTD options on startup
# Usage: source ~/.claude/skills/gtd/startup_display.sh

# Function to display GTD options
show_gtd() {
    python3 ~/.claude/skills/gtd/gtd_options.py 2>/dev/null || cat << 'EOF'
╔═══════════════════════════════════════════════╗
║  🎯 GTD QUICK COMMANDS                        ║
╠═══════════════════════════════════════════════╣
║  /gtd visualize      → Current focus & next   ║
║  /gtd visualize-week → Weekly plan & capacity ║
║  /gtd tradeoffs      → Allocation options     ║
║  "let's plan my week/day" → Interactive plan  ║
╚═══════════════════════════════════════════════╝
EOF
}

# Display on startup (optional - comment out if too noisy)
# show_gtd

# Alias for manual display
alias gtd-help='show_gtd'
alias gtd-options='show_gtd'
alias gtd?='show_gtd'