# GTD Startup Display Setup

This guide shows how to display GTD options when opening a new terminal window.

## Quick Test

Run this anytime to see GTD options:
```bash
python3 .claude/skills/gtd/gtd_options.py
```

## Option 1: Manual Aliases (Recommended)

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
# GTD help aliases
alias gtd-help='python3 ~/Documents/Projects/DigitalBrain/.claude/skills/gtd/gtd_options.py'
alias gtd?='python3 ~/Documents/Projects/DigitalBrain/.claude/skills/gtd/gtd_options.py'
```

Then reload your shell:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

Now you can type `gtd?` or `gtd-help` anytime to see options.

## Option 2: Automatic Display on Startup

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
# Show GTD options on terminal startup
if [ -f ~/Documents/Projects/DigitalBrain/.claude/skills/gtd/gtd_options.py ]; then
    python3 ~/Documents/Projects/DigitalBrain/.claude/skills/gtd/gtd_options.py
fi
```

## Option 3: Use the Startup Script

Source the provided script in your `~/.zshrc` or `~/.bashrc`:

```bash
# GTD startup display
source ~/Documents/Projects/DigitalBrain/.claude/skills/gtd/startup_display.sh

# Uncomment this line in the script to auto-display:
# show_gtd
```

This gives you these aliases:
- `gtd-help` - Show GTD options
- `gtd-options` - Show GTD options
- `gtd?` - Show GTD options (shortest)

## What You'll See

```
╔═══════════════════════════════════════════════╗
║  🎯 GTD QUICK COMMANDS                        ║
╠═══════════════════════════════════════════════╣
║  /gtd visualize      → Current focus & next   ║
║  /gtd visualize-week → Weekly plan & capacity ║
║  /gtd tradeoffs      → Allocation options     ║
║  "let's plan my week/day" → Interactive plan  ║
╚═══════════════════════════════════════════════╝
```

## Customization

Edit `gtd_options.py` to:
- Add more commands
- Change the display format
- Include additional help text
- Show different info based on day of week

## Disable

To stop showing on startup, simply remove or comment out the lines you added to your shell config.