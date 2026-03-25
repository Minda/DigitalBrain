---
name: skill-creator
description: Expert guide for creating and writing Claude Code skills. Use this when the user wants to create a new skill or learn about skill structure and best practices.
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
---

# Skill Creator

A comprehensive guide for creating effective Claude Code skills that extend Claude's capabilities with specialized knowledge, workflows, and tool integrations.

## Quick Start

Creating a skill involves six steps:

1. **Check existing skills** — Review 126+ indexed skills before creating new ones
2. **Understand the use case** — Clarify what the skill does and when it triggers
3. **Identify bundled resources** — Scripts, references, examples
4. **Initialize the skill** — Use `init_skill.py` or create manually
5. **Write the SKILL.md** — Clear instructions using best practices
6. **Package the skill** — Validate and bundle for distribution (optional)

**After creation:** Use `/skill-optimization` to test, refine, and optimize your skill.

## When to Use

- Creating a new skill from scratch
- Learning skill structure and best practices
- Understanding skill conventions and patterns
- Setting up initial skill structure

## When Not to Use

- An existing skill already covers the need (check catalog first)
- Task is too simple—just use a prompt directly
- Need persistent services—use an MCP server instead
- Building a full application—skills are focused components

## What's Included in a Skill?

There are only **two requirements**:
1. **Frontmatter** with `name` and `description`
2. **Body** containing instructions

Everything else is optional.

### How Skills Load

| Component | When Loaded | Budget |
|-----------|-------------|--------|
| **Frontmatter** | Every agent boot | ~100 tokens |
| **Body** | On activation | <5,000 tokens |
| **Supporting files** | On-demand | As needed |

This is why frontmatter must be minimal but body can be detailed.

## Step 1: Check Existing Skills

Before creating a new skill, check if one already exists.

```bash
# Search by name
cat .claude/skills/skill-creator/skills-catalog.json | jq '.skills[] | select(.name | contains("keyword"))'

# Search by category
cat .claude/skills/skill-creator/skills-catalog.json | jq '.skills[] | select(.category == "Development")'

# Find skills with local copies
cat .claude/skills/skill-creator/skills-catalog.json | jq '.skills[] | select(.localPath != null)'
```

### Skill Tiers and Locations

| Tier | Count | Location | Description |
|------|-------|----------|-------------|
| `official` | 16 | `vendor/get-skill/` | Anthropic official skills |
| `partner` | 40 | `vendor/get-skill/` | Partner integrations (Notion, Figma, etc.) |
| `community` | 44 | `vendor/get-skill/` | Community-contributed skills |
| `project` | 19 | `.claude/skills/` | Exobrain project skills |
| `personal` | 7 | `personal/.claude/skills/` | Personal/private skills |

### If a Similar Skill Exists

1. **Read the local copy** — If `localPath` exists, read the SKILL.md directly
2. **Check if it meets your needs** — Many skills are configurable
3. **Consider extending it** — Fork and modify rather than duplicate

## Step 2: Understand the Use Case

**Functionality:**
- What specific task does this skill provide?
- What are concrete examples of when someone would use this?
- What tools or APIs does it need?

**Triggers:**
- Should Claude invoke this automatically or only manually (`/skill-name`)?
- What keywords or phrases should trigger automatic invocation?

## Step 3: Identify Bundled Resources

Skills can bundle three types of resources:

| Type | Directory | Purpose |
|------|-----------|---------|
| **Scripts** | `scripts/` | Deterministic operations (API calls, file parsing, calculations) |
| **References** | `references/` | Detailed documentation supplementing SKILL.md |
| **Assets** | `examples/` | Templates, samples, static files |

**Scripts** — Use for tasks bash/python handle better than Claude. For large files (>10MB), always use scripts instead of loading into context.

**References** — Move detailed docs out of SKILL.md: API documentation, configuration guides, advanced examples.

**Examples** — Concrete input/output pairs. Prefer concise examples over lengthy explanations.

## Step 4: Initialize the Skill

```bash
python .claude/skills/skill-creator/scripts/init_skill.py <skill-name> --path .claude/skills
```

Creates:
```
skill-name/
├── SKILL.md           # Main instructions
├── scripts/           # Helper scripts
├── references/        # Detailed docs
└── examples/          # Usage examples
```

Or manually: `mkdir -p .claude/skills/<skill-name>` and create SKILL.md.

## Step 5: Write the SKILL.md

### Frontmatter

Loads at every boot—keep minimal.

**Required:**
```yaml
---
name: skill-name        # Lowercase, hyphens only, max 64 chars
description: What it does AND when to use it. Include trigger keywords.
---
```

**Optional:**
```yaml
allowed-tools: [Read, Write, Bash]  # Tools without permission prompts
disable-model-invocation: false     # true = manual only
model: sonnet                       # Specific model
context: fork                       # Isolated subagent
```

### Available Tools

| Tool | Requires Permission |
|------|---------------------|
| `Read`, `Glob`, `Grep`, `Task`, `TodoWrite` | No |
| `Write`, `Edit`, `Bash`, `WebFetch`, `WebSearch` | Yes |

Pattern matching: `Bash(git *)`, `Read(./secrets/**)`

### Naming Conventions

**Use gerund form:** `processing-pdfs`, `analyzing-spreadsheets`, `generating-commits`

**Avoid:** `helper`, `utils`, `tools`, `anthropic-*`, `claude-*`

### Body Structure

Body components (from analysis of 200+ skills):

| Component | Status | Notes |
|-----------|--------|-------|
| **Title + Overview** | Required | Brief description |
| **When to Use** | Common | Often paired with "When Not to Use" |
| **When Not to Use** | Suggested | Prevents misapplication |
| **Instructions** | Required | Core guidance, procedures |
| **Examples** | Suggested | Concise over lengthy |

**Template:**
```markdown
# Skill Name

Brief overview.

## When to Use
- Condition A
- Condition B

## When Not to Use
- Condition X

## Instructions

Core guidance.
- Step-by-step procedures
- Decision criteria

## Examples

Concise input/output pairs.
```

### Writing Style

- **Be direct:** "Create a plan before coding" not "You might want to consider..."
- **Provide context Claude lacks:** "The codebase uses thiserror" not "Use appropriate error handling"
- **Progressive disclosure:** Link to references for details

### Dynamic Context

Inject live data with `!` commands:
```markdown
!`gh pr view $ARGUMENTS --json title,body`
```

Variables: `$ARGUMENTS`, `${CLAUDE_SESSION_ID}`

## Step 6: Package the Skill (Optional)

```bash
python .claude/skills/skill-creator/scripts/package_skill.py .claude/skills/<skill-name>
```

For web distribution via `.well-known/skills/`, see `references/agent-skills-discovery-rfc.md`.

## Next Step: Optimization

Once you've created your skill, use `/skill-optimization` to:
- Test with realistic data
- Identify and fix bottlenecks
- Improve clarity and error handling
- Add robustness for edge cases
- Track optimization iterations

The skill-optimization skill provides a systematic framework for testing, profiling, and iteratively improving your skill based on real usage.

## Anti-Patterns

**Don't do:**
- XML tags in body content — use standard markdown
- Vague descriptions — "A helpful skill" → "Expert guide for creating skills"
- Deeply nested references — keep `references/` flat
- Scripts that punt to Claude — if deterministic, do it in the script
- Loading large files (>10MB) into context — use scripts instead
- Skipping `skills-catalog.json` when searching for skills — the catalog is the primary index of 200+ known skills. When asked "does a skill for X exist?", read the catalog first, then search installed SKILL.md files. A Grep match on the catalog filename is not the same as reading it.

**A skill is NOT:**
- An MCP Server (skills are prompts, not services)
- A Project (skills are focused components)
- A Prompt template (skills include structure and resources)

**When SKILL.md gets too long:**
1. Can I break documentation into separate files?
2. Is this actually more than one skill?

> *"Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away."* — Antoine de Saint-Exupéry

## Resources

### Reference Files

Load when relevant:

| File | Content |
|------|---------|
| `references/skill-structure.md` | Directory layout, frontmatter fields, validation |
| `references/best-practices.md` | Writing patterns, testing, anti-patterns |
| `references/examples.md` | 5 complete skill examples |
| `references/advanced-skill-patterns.md` | Progressive disclosure, bundled scripts, workflow branching |

### External Sources

| Source | Purpose |
|--------|---------|
| `skills-catalog.json` | Local catalog of 126+ skills with paths |
| `sources/anthropic-skills.md` | Official Anthropic skills repo |
| [github.com/anthropics/skills](https://github.com/anthropics/skills) | Official reference |

### Getting Help

1. Describe what you want the skill to do
2. Explain when it should be invoked
3. Share any scripts, docs, or examples
4. Claude will guide you through creation

---

**Remember:** Skills are just prompts. Keep them clear, focused, and actionable.
