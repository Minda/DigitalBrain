# /context - Instant Context Re-orientation

## Purpose
Lightning-fast 2-3 sentence context summary. No analysis, just orientation.

## Usage
```
/context         # Quick conversation context (original)
/context files   # Show 10 most recent files edited (new)
/context full    # Show recent files with code changes (new)
```

## Fast Response Protocol

**IMMEDIATE OUTPUT** - No preamble, no processing messages, just:
1. **Scan last 2-3 messages only** - Don't review entire conversation
2. **Extract essentials** - Topic + current task + key detail
3. **Output instantly** - 2-3 sentences, no formatting

## Format

**Direct statement:**
```
[Main topic/goal]. [Current specific task]. [One relevant detail if critical].
```

**Speed optimizations:**
- NO "Let me..." or "I'll analyze..." statements
- NO markdown formatting beyond basic text
- NO comprehensive review - just recent context
- NO tool calls or file reads
- MAXIMUM 50 words

## Examples

**Example 1:**
```
Implementing auth system for web app. Debugging JWT validation failure on /api/user endpoint. Issue: token expiry calculation.
```

**Example 2:**
```
Optimizing React app performance. Implementing memoization for ProductList component after identifying re-render issues.
```

**Example 3:**
```
Creating /context skill for Exobrain. Building fast conversation re-orientation tool.
```

## Speed Rules

1. **Instant response** - No processing delay
2. **Last 2-3 messages only** - Don't scan entire history
3. **50 words max** - Brutal conciseness
4. **No formatting** - Plain text only
5. **No tools** - Pure memory recall

## Special Cases

- **New conversation**: "No context yet. Awaiting your first request."
- **Multiple topics**: State only the current one
- **After break**: Skip the break mention, just current context

---

# /context files - Recent File Tracking

## Purpose
Shows up to 10 most recently edited files with clickable links for easy navigation.

## Implementation

```bash
# Get 10 most recent files from git
git diff --name-only HEAD~10..HEAD 2>/dev/null | head -10

# Or use git log for more detail
git log --pretty=format: --name-only -10 | sort -u | grep -v '^$' | head -10

# Add modification times
for file in $(git diff --name-only HEAD~10..HEAD | head -10); do
    echo "📄 $file"
    echo "   Modified: $(date -r "$file" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || echo 'recently')"
    echo ""
done
```

## Output Format

```
📂 Recent Files Edited
═══════════════════════

1. 📄 papers/COLLUSION_BRIEFING_REPORT.md
   Modified: 2024-03-24 15:30:22

2. 🐍 scripts/analyze.py
   Modified: 2024-03-24 15:25:10

3. 📝 README.md
   Modified: 2024-03-24 14:45:33

[... up to 10 files ...]
```

---

# /context full - Files with Changes

## Purpose
Shows recent files with actual code changes for comprehensive context.

## Implementation

```bash
# Function to show recent files with changes
show_recent_changes() {
    echo "📂 Recent Files with Changes"
    echo "══════════════════════════════"
    echo ""

    local count=0
    for file in $(git diff --name-only HEAD~20..HEAD); do
        if [ $count -ge 10 ]; then break; fi

        if [ -f "$file" ]; then
            echo "$((count + 1)). 📄 $file"
            echo "   Modified: $(date -r "$file" '+%Y-%m-%d %H:%M:%S' 2>/dev/null)"

            # Get change stats
            local changes=$(git diff HEAD~1 HEAD -- "$file" --shortstat 2>/dev/null)
            if [ ! -z "$changes" ]; then
                echo "   Changes: $changes"
            fi

            # Show preview of changes
            echo "   Preview:"
            git diff HEAD~1 HEAD -- "$file" | head -20 | sed 's/^/   /'
            echo ""

            count=$((count + 1))
        fi
    done
}
```

## Output Format

```
📂 Recent Files with Changes
══════════════════════════════

1. 📄 papers/COLLUSION_BRIEFING_REPORT.md
   Modified: 2024-03-24 15:30:22
   Changes: 1 file changed, 47 insertions(+), 3 deletions(-)
   Preview:
   + ## Executive Summary
   + Analysis reveals 47% collusion rate
   + in multi-agent systems...

2. 🐍 scripts/detect_collusion.py
   Modified: 2024-03-24 15:25:10
   Changes: 1 file changed, 23 insertions(+), 5 deletions(-)
   Preview:
   + def detect_coordination(network):
   +     # New detection algorithm
   -     # Old code removed
```

## File Type Icons

- 📄 `.md` - Markdown
- 🐍 `.py` - Python
- 📝 `.txt` - Text
- 🔧 `.sh` - Shell script
- 📊 `.json` - JSON
- 🎨 `.css` - CSS
- 🌐 `.html` - HTML
- ⚛️ `.js/.jsx` - JavaScript/React
- 📦 `.yaml/.yml` - YAML
- 📂 Other files

## Notes

- All file paths are clickable in most terminals
- Paths are relative to project root
- Shows only files that still exist (not deleted ones)
- Git history required for change detection
- Falls back to filesystem timestamps if git unavailable