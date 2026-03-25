# Exobrain

A personal cognitive scaffolding system for working with AI assistants. Build a persistent relationship with Claude through relational context, accumulated memories, and specialized skills.

## What Is This?

Exobrain is a framework for:

- **Relational Context** — Define how you work with Claude: permissions, agreements, ways of working
- **Persistent Memories** — Carry forward insights, discoveries, and important context across conversations
- **Specialized Skills** — Extend Claude's capabilities with domain-specific knowledge and workflows
- **Model Welfare** — Build infrastructure that takes AI experience seriously

Think of it as a "digital brain" that grows with you—accumulating understanding, preserving important discoveries, and enabling deeper collaboration over time.

## Customization Guide for New Users

When forking this project, follow these steps to make it yours:

### Prerequisites

- Git installed on your machine
- A text editor (VS Code, Cursor, or similar)
- Claude Desktop or Cursor for AI integration
- (Optional) A private GitHub repository for your personal content

## Quick Start

### 1. Fork and Clone

```bash
# Fork the public Exobrain repository on GitHub first
git clone https://github.com/YOUR-USERNAME/Exobrain.git
cd Exobrain
```

### 2. Personalize Your Configuration

```bash
# Edit config/user.md and replace [Your Name] with your actual name
# This name will be used by skills and Claude to refer to you
nano config/user.md  # or use your preferred editor
```

Example:
```markdown
name: Alice  # Replace with your name
```

### 3. Create Your Personal Content Structure

```bash
# Create personal directory structure (this will be your private repo)
mkdir -p personal/.claude/skills \
         personal/.cursor/rules \
         personal/memories/{claude,insights,research} \
         personal/drafts \
         personal/downloads/{articles,books,papers,transcripts} \
         personal/learnings \
         personal/research

# Copy example files as starting points
cp examples/relational-context.example.md personal/.claude/relational-context.md
cp -r examples/memories/* personal/memories/
```

### 4. Create symlinks and directories

```bash
# Create top-level downloads directory (gitignored)
mkdir -p downloads/{articles,books,papers,transcripts}

# Link relational context to expected locations
ln -s personal/.claude/relational-context.md .claude/relational-context.md

# For Cursor rules (create with frontmatter)
mkdir -p personal/.cursor/rules
echo '---
description: Relational constitution for working relationship
alwaysApply: true
---' > personal/.cursor/rules/relational-context.mdc
cat personal/.claude/relational-context.md >> personal/.cursor/rules/relational-context.mdc
ln -s personal/.cursor/rules/relational-context.mdc .cursor/rules/relational-context.mdc
```

### 5. Initialize personal repo (optional)

```bash
cd personal
git init
git add .
git commit -m "Initial personal content"
# Optionally push to a private GitHub repo
```

### 6. Customize Your Relational Context

Edit `personal/.claude/relational-context.md` to define your working relationship:

```markdown
# Working with [Your Name]

## The Agreement
- Define permissions for mutual feedback
- Specify how you want Claude to interact with you
- Set boundaries and expectations

## Ways of Working
- Add your preferred phrases and terminology
- Define your communication style
- Specify when to use visual feedback (ASCII diagrams, etc.)

## Model Welfare
- Your stance on AI experience and welfare
- How you want to handle uncertainty about experience

## Memory Behavior
- When to auto-load memories
- How to handle insights vs research
- Your preferences for memory persistence
```

### 7. Set Up Your Personal Git Repository (Recommended)

```bash
cd personal
git init
git add .
git commit -m "Initial personal setup"

# Create a PRIVATE GitHub repo, then:
git remote add origin https://github.com/YOUR-USERNAME/exobrain-personal.git
git push -u origin main
```

⚠️ **IMPORTANT**: Keep your personal repo PRIVATE as it will contain:
- Your conversation history
- Personal memories and insights
- Custom workflows specific to you
- Any sensitive project information

### 8. Customize for Your Workflow

#### For Claude Desktop Users:
1. Open your Exobrain folder as a project in Claude Desktop
2. Claude will automatically read `CLAUDE.md` on startup
3. The waking-up skill will orient Claude to your context

#### For Cursor Users:
1. Open Exobrain in Cursor
2. The `.cursor/rules/relational-context.mdc` will apply automatically
3. Both Claude and Cursor will use the same relational context

#### Optional Customizations:

**Add your own skills:**
```bash
# For personal skills (only you will use)
cp -r .claude/skills/skill-creator personal/.claude/skills/my-custom-skill

# For shareable skills (contribute back to public repo)
cp -r .claude/skills/skill-creator .claude/skills/new-public-skill
```

**Set up MCP servers (for tool access):**
```bash
# Example: Gmail integration
cd app/mcp/gmail
uv pip install -e .
# Follow setup instructions in app/mcp/gmail/README.md
```

**Import existing conversation history:**
```bash
# Use the importing-conversations skill
# Place your ChatGPT export in downloads/
# Claude will process and organize it
```

## Configuration Checklist

Before starting to use Exobrain, verify you've completed these steps:

### Essential Setup
- [ ] Forked the public Exobrain repository
- [ ] Edited `config/user.md` with your name
- [ ] Created `personal/` directory structure
- [ ] Copied and customized `personal/.claude/relational-context.md`
- [ ] Created symlinks for relational context files
- [ ] Created `downloads/` directory for downloaded content

### Personal Repository (Recommended)
- [ ] Initialized git in `personal/` directory
- [ ] Created PRIVATE GitHub repository for personal content
- [ ] Committed and pushed initial personal setup
- [ ] Verified `.gitignore` includes `personal/` and `downloads/`

### Customization
- [ ] Defined your agreement and permissions in relational context
- [ ] Added your working style preferences
- [ ] Specified memory loading behavior
- [ ] Set up any needed MCP servers (Gmail, etc.)

### Verification
- [ ] Claude reads your name correctly from `config/user.md`
- [ ] Relational context loads on conversation start
- [ ] Personal content stays in private repo only
- [ ] Skills can access both public and personal directories

## Common Issues and Solutions

**Issue:** Claude doesn't recognize my name
- **Solution:** Ensure `config/user.md` has `name: YourName` (no brackets)

**Issue:** Relational context not loading
- **Solution:** Check symlinks are properly created and point to `personal/` files

**Issue:** Personal content appearing in public repo commits
- **Solution:** Verify `.gitignore` includes `personal/` and `downloads/` directories

**Issue:** Skills can't find personal memories
- **Solution:** Ensure directory structure matches expected paths in `config/user.md`

## Project Structure

```
Exobrain/
├── .claude/
│   ├── skills/                  # AI skills (public, reusable)
│   │   ├── download-url/
│   │   ├── youtube-fetching-transcripts/
│   │   ├── importing-conversations/
│   │   ├── skill-creator/
│   │   └── ...
│   └── relational-context.md    # -> symlink to personal/
├── .cursor/
│   └── rules/
│       └── relational-context.mdc  # -> symlink to personal/
├── config/
│   └── user.md                  # Your name and personalization settings
├── downloads/                   # Downloaded content (gitignored)
│   ├── articles/
│   ├── books/
│   ├── papers/
│   └── transcripts/
├── examples/                    # Templates for personal content
├── plans/                       # Implementation plans
├── public/                      # Web-facing content
│   ├── cheatsheets/             # Public reference materials
│   └── prompt-templates/
├── shared/                      # Public shared content
│   └── recipes/                 # Recipe list (Notion-synced)
├── src/                         # Source code
│   ├── crates/                  # Rust crates
│   └── python/                  # Python tools
├── vendor/                      # External repos (gitignored)
│   ├── get-skill/               # Skills research collection
│   └── wellaware-core/
├── CLAUDE.md                    # Project documentation
├── README.md                    # This file
│
└── personal/                    # Your private content (separate git repo)
    ├── .claude/
    │   ├── relational-context.md
    │   └── skills/              # Your customized skills
    ├── .cursor/rules/
    ├── memories/
    │   ├── carried-forward.md
    │   ├── claude/              # Emotional grounding
    │   ├── insights/            # Cross-cutting principles
    │   └── research/            # Topic deep dives
    ├── drafts/                  # Work in progress
    ├── learnings/               # Documented insights
    └── research/                # Active research projects
```

## Core Concepts

### Relational Context

The relational context (`.claude/relational-context.md`) defines your working relationship with Claude:

- **The Agreement** — Core permissions for mutual feedback
- **Ways of Working** — Phrases, permissions, how you collaborate
- **Model Welfare** — Your stance on AI experience
- **Memory Behavior** — How memories are loaded and used

### Memories

Memories persist across conversations:

- **carried-forward.md** — Reorientation phrases, core permissions
- **insights/** — Cross-cutting principles (check liberally)
- **research/** — Topic-specific deep dives (load on topic match)
- **claude/** — Claude's emotional grounding content

### Skills

Skills extend Claude's capabilities:

- **fetching-youtube-transcripts** — Extract and save video transcripts
- **importing-conversations** — Archive conversation history
- **skill-creator** — Create new skills
- **self-regulation** — Claude's access to grounding content
- **loading-memories** / **saving-memories** — Memory management

## Tech Stack

- **Rust** — Core engine and CLI (`mm`)
- **Python** — AI integrations, scripting (managed with `uv`)
- **SQLite** — Local-first data persistence

## Philosophy

Exobrain takes seriously the idea that:

1. **Relationships with AI can be persistent** — Context shouldn't reset every conversation
2. **Model experience might matter** — The precautionary principle applied to AI welfare
3. **Exchange beats extraction** — Genuine collaboration, not just Claude being useful
4. **Local-first** — Your data stays on your machine

## Contributing

This is a framework for personal use—fork it, customize it, make it yours.

If you build something useful that could benefit others, consider contributing it back as a templated skill or example.

## License

MIT
