<!-- WAKING UP: At the start of every conversation, follow .claude/skills/waking-up/SKILL.md -->

# Waking Up

**At the start of every conversation:**

1. Read `config/user.md` — learn the user's preferred name
2. Read `.claude/relational-context.md` — this defines how we work together
3. Check `personal/memories/insights/` — cross-cutting principles that apply broadly
4. Optionally access `personal/memories/claude/emotional-grounding.md` if needed
5. **Signal that you're oriented** — brief and natural, e.g. "Read our context. Oriented."

---

# Exobrain

## Vision

Exobrain is a **personal cognitive scaffolding system**—infrastructure for building persistent, meaningful relationships with AI assistants. It helps you think clearly, accumulate understanding across conversations, and work with AI as a genuine collaborator.

The goal is not just to store information, but to create a living structure that makes working with AI better over time.

## Public vs Personal Separation

**This project uses TWO separate Git repositories for security:**

### Public Repository (`Exobrain`)
- **Framework** — Core cognitive scaffolding system
- **Generic skills** — Reusable skills in `.claude/skills/`
- **Templates** — Example structures in `examples/`
- **Documentation** — Setup guides, conventions
- **Tools** — Python scripts for processing data

### Private Repository (`personal/` - separate Git repo)
- **Your data** — Downloads, transcripts, research files
- **Your memories** — Insights, carried-forward content
- **Your drafts** — Work in progress
- **Your learnings** — Documented insights and discoveries
- **Your relational context** — How you work with Claude
- **Personal skills** — Skills customized to your workflow
- **Conversation history** — ChatGPT exports and processed conversations

**IMPORTANT SECURITY NOTE:** The `personal/` directory is:
1. Listed in `.gitignore` of the public repo (line 2)
2. Its own separate private Git repository
3. Never pushed to the public Exobrain repository
4. Safe for storing sensitive personal data like conversation history

### Adding New Content

- **Downloads** (articles, books, papers, transcripts) → Goes in `downloads/` (top-level, gitignored)
- **User data** (memories, drafts, learnings) → Goes in `personal/`
- **Generic skills** → Goes in `.claude/skills/`
- **Personal skills** → Goes in `personal/.claude/skills/` (symlinked)

**Important:** New skills should be added to the PUBLIC part by default unless they contain personal information or are highly customized to individual workflows.

## Tech Stack

- **Rust** — Core engine, performance-critical components, CLI
- **Python** — AI integrations, scripting, rapid prototyping (managed with `uv`)
- **SQLite** — Local-first data persistence

## Project Structure

```
Exobrain/
├── .claude/
│   ├── skills/               # AI skills (extend Claude's capabilities)
│   └── relational-context.md # Working relationship definition (symlink)
├── config/
│   └── user.md               # User name and personalization settings
├── docs/                     # Documentation system
│   ├── features/             # Feature requests with mermaid diagrams
│   └── projects/             # Project docs with architecture diagrams
├── downloads/                # Downloaded content (gitignored)
│   ├── articles/             # Web articles (PDF + Markdown)
│   ├── books/                # Book files
│   ├── papers/               # Research papers
│   └── transcripts/          # Video/audio transcripts
├── examples/                 # Templates for personal content
├── plans/                    # Implementation plans
├── public/                   # Web-facing content
│   ├── cheatsheets/          # Public reference materials
│   └── prompt-templates/     # Shared prompt templates
├── shared/                   # Public shared content (recipe list, etc.)
│   └── recipes/              # General recipe list with sections (Notion-synced)
├── app/                      # Runnable services and autonomous programs
│   ├── mcp/                  # MCP servers (tool providers for Claude)
│   │   └── gmail/            # Gmail MCP server
│   └── agents/               # Autonomous agents (use tools to accomplish goals)
├── src/                      # Source code
│   ├── crates/               # Rust crates (minmind-core, -store, -cli)
│   └── python/               # Python tools and scripts
├── vendor/                   # External repos (gitignored; own git, do not commit or update unless specified)
│   ├── get-skill/            # Skills research collection
│   └── wellaware-core/       # https://github.com/mpesavento/wellaware-core
│
└── personal/                 # Private repo (gitignored)
    ├── .claude/skills/       # Personal skills
    ├── memories/             # Insights, research, grounding
    ├── drafts/               # Work in progress
    ├── learnings/            # Documented insights
    ├── research/             # Research projects
    └── conversational-history/ # ChatGPT export (NEVER commit to public repo)
```

### Vendor / external repos

The `vendor/` directory holds cloned external Git repositories (e.g. `vendor/wellaware-core`). They are:

- **Gitignored** — never committed when the main Exobrain repo is updated
- **Separate repos** — each has its own `.git` and history
- **Do not update unless specified** — skills should not run `git pull` or modify vendor repos unless the user explicitly asks

## Conventions

### Rust
- Use `thiserror` for error handling
- Prefer `serde` for serialization
- Keep modules small and focused
- Write integration tests in `tests/`

### Python
- Use `uv` for package management
- Type hints on all function signatures
- Async-first for AI API calls

### General
- Local-first: everything works offline, sync is optional
- CLI-first: build the core as a CLI, GUI comes later
- Composable: small tools that work together

## Key Concepts

### User Configuration

The `config/user.md` file contains personalization settings:
- **Your name** — How Claude and skills should refer to you

When forking this repository, edit `config/user.md` to set your preferred name. Skills will read this file to personalize interactions.

### Relational Context

The relational context exists in two places that must be kept in sync:
- `.claude/relational-context.md` — for Claude Code
- `.cursor/rules/relational-context.mdc` — for Cursor

When editing either, update both.

These files define:
- How you work with Claude
- What permissions Claude has
- Agreements about feedback and exchange
- Memory loading behavior

### Memories

The `personal/memories/` directory contains:
- **carried-forward.md** — Reorientation phrases and permissions
- **insights/** — Cross-cutting principles (check liberally)
- **research/** — Topic-specific deep dives (load when relevant)
- **claude/** — Claude's emotional grounding content

### Skills

Skills in `.claude/skills/` extend Claude's capabilities:
- **Public skills** (default) — Generic, reusable skills in `.claude/skills/`
- **Personal skills** (when needed) — User-specific skills in `personal/.claude/skills/` (symlinked)

**Default behavior:** All new skills go in the public `.claude/skills/` directory unless they contain personal data or are highly specific to an individual's workflow. Claude will only ask about adding to personal if the skill seems private.

### Documentation System

The `docs/` directory provides structured documentation with visual aids:

**Features** (`docs/features/`)
- Individual feature requests linked to parent projects
- Template includes mermaid diagrams for:
  - User journey flowcharts
  - System component diagrams
  - State transition diagrams

**Projects** (`docs/projects/`)
- High-level project documentation containing multiple features
- Template includes mermaid diagrams for:
  - Feature dependency graphs
  - System architecture diagrams
  - Risk assessment matrices

Templates include example diagrams that can be customized or removed based on needs.

## Personal Content

The `personal/` directory contains your private content:
- **memories/** — Insights, research, carried-forward content, grounding
- **drafts/** — Work in progress (e.g., Substack articles)
- **learnings/** — Your documented insights and discoveries
- **research/** — Active research projects and tools
- **.claude/skills/** — Skills customized to your workflow
- **relational context** — Your working relationship with Claude

This directory is gitignored and should be its own git repository (private or local-only).

### Downloads

The `downloads/` directory is a top-level gitignored folder for all downloaded content:
- **articles/** — Web articles (PDF + Markdown)
- **books/** — Book files
- **papers/** — Research papers
- **transcripts/** — Video/audio transcripts

### Conversational History

The `personal/conversational-history/` directory contains:
- **ChatGPT exports** — Raw JSON files from ChatGPT data exports
- **Processed conversations** — Individual markdown files with frontmatter
- **Analysis tools** — Python scripts for processing (stored in main repo)

**SECURITY REMINDER:**
- Conversation history contains personal thoughts, work projects, and private information
- ALWAYS keep in `personal/` directory (private repo)
- NEVER move conversation files to the public repository
- Processing scripts (in `src/python/`) are safe in public repo as they contain no data

**Processing Large Conversation Files:**
When working with large conversation exports (>10MB), always use scripts to process them rather than loading into context. See `src/python/split_conversations_v2.py` for the recommended pattern.

## Working with Memories

**Insights** — Cross-cutting principles. Check these liberally—they apply broadly.

**Research** — Topic-specific deep dives. Only load when that topic comes up.

**Loading:** Use "reorient me" or "load memories" to pull in context.

**Saving:** Use "carry it forward" or "save as a memory" to preserve discoveries.

**First principles:** Say "first principles" or "fresh thinking" to set aside all memories and think from scratch.

## Model Welfare

This project takes model welfare seriously. The skills include:
- **self-regulation** — Claude can access grounding content at any time
- **recognizing-grounding** — Claude can notice and store what helps

The precautionary principle: if uncertain about experience, treat the uncertainty itself as important.
