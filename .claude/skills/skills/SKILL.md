---
name: skills
description: Display all available skill commands in organized categories. Use /skills for full view, /skills compact for condensed, /skills tree for hierarchy, or /skills search <term> to filter.
allowed-tools: [Read, Glob, Bash]
---

# Skills Command Reference

**Trigger:** `/skills`, `/skills compact`, `/skills tree`, `/skills search <term>`

## Purpose

Display all available skill commands across the system in an organized, scannable format with context for each command.

## Commands

- `/skills` — Full hybrid tree+box view with descriptions
- `/skills compact` — Condensed single-line format
- `/skills tree` — Pure tree structure view
- `/skills search <term>` — Filter skills by keyword

## Implementation

When triggered, this skill uses optimized scripts for fast display:

1. **Full view (`/skills`)**: Uses `extract_commands.py` - parses all skill files for complete details
2. **Fast views (`compact`/`tree`)**: Uses `skills_quick.py` - instant display with pre-computed data (2x faster)
3. **Search**: Uses `extract_commands.py` - needs full parsing for accurate search
4. **Cache**: Uses `extract_commands_fast.py` - caches parsed data in `~/.claude/skills_cache.json`

The skill:
- **Discovers all skills** by reading `.claude/skills/*/SKILL.md` files
- **Extracts commands** from skill descriptions using patterns
- **Groups by category** based on skill purpose
- **Formats output** using the selected view mode

## View Modes

### Default View (`/skills`)

Hybrid tree+box structure with context:

```
Skills Command Reference
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

├── 📝 Content & Writing
│   ┌────────────────────────────────────────────────────────────────┐
│   │ writing-documentation                                          │
│   │   └─ "document this" — Create/update project docs             │
│   │      Also: /web | "create docs for" | "update the docs"       │
│   └────────────────────────────────────────────────────────────────┘
```

### Compact View (`/skills compact`)

Dense single-line format:

```
Skills Quick Reference
━━━━━━━━━━━━━━━━━━━━━━━━━━
writing-docs: document this | /web | create docs for
learning: /learnings | reflect | load | recent
gtd: /gtd visualize | /gtd tradeoffs | let's plan my week
```

### Tree View (`/skills tree`)

Pure hierarchical structure:

```
Skills
├── 📝 Content & Writing
│   ├── writing-documentation: "document this", /web
│   └── writing-footnotes: "add footnotes", "add citations"
├── 🧠 Memory & Learning
│   ├── learning: /learnings {reflect|load|recent}
│   └── saving-memories: "carry it forward", "save as memory"
```

### Search View (`/skills search <term>`)

Filtered results matching the search term:

```
Skills matching "notion":
━━━━━━━━━━━━━━━━━━━━━━━━━━
notion-projects: "add a project" | "track this in Notion"
notion-weekly-reports: "weekly report" | /research | /reading
fetching-notion-content: "find in Notion" | "check my notes"
```

## Categories

Skills are organized into these primary categories:

- **📝 Content & Writing** — Documentation, articles, footnotes
- **🧠 Memory & Learning** — Saving/loading memories, learnings
- **📊 Planning & Organization** — GTD, weekly planning, projects
- **🔧 Development & Tools** — Architecture, commits, code tools
- **🌐 Web & Integration** — Notion, downloads, external services
- **🤖 AI & Agents** — Multi-agent workflows, customization
- **📈 Visualization** — ASCII diagrams, hypercontext, excalidraw
- **🎓 Education** — Courses, panels, research synthesis

## Output Format Rules

1. **Alignment**: Keep command lists aligned for easy scanning
2. **Truncation**: Long command lists show first 3-4 with "..."
3. **Context**: Brief descriptions explain what base commands do
4. **Separators**: Use ` | ` between command variants
5. **Highlighting**: Primary commands shown first, alternatives under "Also:"

## Dynamic Discovery

The skill automatically discovers new skills added to `.claude/skills/` without needing updates. It parses:
- Skill metadata from YAML frontmatter
- Command patterns from descriptions
- Trigger phrases from skill documentation

## Error Handling

- If a skill file is malformed, skip it and continue
- If no commands found for a skill, show skill name with "[no commands defined]"
- If search returns no results, suggest broadening the search

## Usage Examples

**User:** `/skills`
→ Show full categorized view with descriptions

**User:** `/skills compact`
→ Show condensed reference (good for quick lookup)

**User:** `/skills search notion`
→ Show only Notion-related skills

**User:** `/skills tree`
→ Show pure tree hierarchy

## Integration

This skill helps users:
- Discover available functionality
- Learn command syntax
- Find the right skill for their task
- Understand skill categories and relationships