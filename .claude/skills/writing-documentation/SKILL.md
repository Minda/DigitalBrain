---
name: writing-documentation
description: Create or update documentation for project features. Uses ALL CAPS feature files (JOBS.md, GMAIL.md) in docs/ with changelog as a section. Handles web app features (app/web + docs/web) and other service types (mcp, agents). Migrates legacy README.md + CHANGELOG.md pairs automatically. Use when user says "document this", "create docs for", "write documentation for", "update the docs", "add changelog entry".
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash]
---

# Writing Documentation

Creates and updates feature documentation following the project's doc structure convention.

## Quick Start

1. User says "document the jobs feature" or "update docs for gmail MCP"
2. Determine workflow (`create` or `update`) and feature type (web vs other)
3. Write to the correct location, return a summary of files changed

---

## Doc Structure Convention

| Location | Purpose | File naming |
|----------|---------|-------------|
| `docs/web/[feature]/FEATURE.md` | System perspective: product idea, test cases (plain English), changelog section | ALL CAPS (e.g. `JOBS.md`) |
| `docs/mcp/FEATURE.md` | Same, for MCP servers | ALL CAPS (e.g. `GMAIL.md`) |
| `docs/agents/FEATURE.md` | Same, for agents | ALL CAPS |
| `app/web/README.md` | Standalone operational docs: setup, run, API — anything needed to run the app as a standalone repo | `README.md` (standard) |

**Rules:**
- No `README.md` inside `docs/` for features — always use `FEATURE.md` in ALL CAPS
- No separate `CHANGELOG.md` — changelog is a `## Changelog` section inside `FEATURE.md`
- `app/web/README.md` is the exception: it stays as README because it's for the standalone repo audience

---

## Feature Type Reference

| Feature lives in | Doc location | Example |
|-----------------|-------------|---------|
| `app/web/` | `docs/web/[feature]/FEATURE.md` | `docs/web/jobs/JOBS.md` |
| `app/mcp/` | `docs/mcp/FEATURE.md` | `docs/mcp/GMAIL.md` |
| `app/agents/` | `docs/agents/FEATURE.md` | `docs/agents/RESEARCHER.md` |

---

## Capturing Feature Requests as Test Cases

**Trigger:** Any time the user describes a new feature they want built — before Claude presents a plan or writes any code — Claude should record the user's plain English instructions as test cases in the relevant `FEATURE.md`.

### When to trigger

- User asks Claude to "add", "build", "implement", or "create" something in a feature area
- User describes expected behavior in natural language ("it should...", "when I...", "I want...")
- Especially when Claude is about to enter plan mode or present implementation steps

### What to do

1. Identify which feature doc the request relates to (e.g. jobs → `docs/web/jobs/JOBS.md`)
2. If the doc doesn't exist yet, create it (follow Step 3a/3b below)
3. Write the user's instructions into a `## Test Cases` section as TC-XXX entries
4. Then proceed with planning or implementation

### Test case format

```markdown
## Test Cases

### [Feature area]

**TC-XXX: [Short title]**
[One sentence: what the user asked for, in their words or close paraphrase.]

- Given: [starting state]
- When: [user action or system trigger]
- Then: [expected outcome]
```

Number sequentially within a feature area (TC-J1, TC-J2 for jobs; TC-G1 for gmail, etc.).

**Keep language plain.** These are not unit tests — they're a record of intent that someone unfamiliar with the code can read and understand.

### Example

User says: *"I want to add a classifier to the project for the entries that land in the database from the jobs scrape. For now, this can be manually triggered. It should be written in Python."*

→ Before writing code, append to `docs/web/jobs/JOBS.md`:

```markdown
**TC-C1: Manual job classification**
User can trigger classification of unscraped jobs from the UI.

- Given: jobs in the database with relevance = 0
- When: user clicks the Classify button
- Then: Claude Haiku classifies each job and assigns relevance 1–3, a summary, and a score breakdown

**TC-C2: Python implementation**
The classifier runs as a Python process, not TypeScript.

- Given: classify button is clicked
- When: the Next.js API route handles the request
- Then: it spawns a Python subprocess via the mcp_jobs CLI
```

---

## Instructions

### Step 1 — Determine workflow and feature

- If user says "create docs", "document this", "write docs for" → **create**
- If user says "update docs", "add changelog entry", "document what changed" → **update**
- Identify the feature name from the user's request

### Step 2 — Check for legacy files (migrate if found)

Before writing, check if a legacy `README.md` + `CHANGELOG.md` pair exists in the target directory.

```
docs/web/[feature]/README.md   ← legacy
docs/web/[feature]/CHANGELOG.md ← legacy
```

If found:
1. Read both files
2. Create `FEATURE.md` with README content first, then append `## Changelog` section with the CHANGELOG content
3. Delete the two legacy files
4. Note the migration in your return summary

### Step 3a — Web feature branch

When the feature is a web app feature (lives in `app/web/`):

1. Read the feature's code: look in `app/web/src/app/`, `app/web/src/modules/`, `app/web/src/app/api/`
2. Read `docs/web/[feature]/FEATURE.md` if it exists
3. Determine which doc needs updating:
   - **Operational content** (setup, run commands, environment variables) → `app/web/README.md`
   - **Everything else** (product intent, schema, test cases, architecture, changelog) → `docs/web/[feature]/FEATURE.md`
4. Create the docs/web/[feature]/ directory if it doesn't exist

**`docs/web/[feature]/FEATURE.md` should contain:**
- Overview / product intent
- Architecture diagram (ASCII or mermaid)
- Data model / schema
- Sources and integrations
- Test cases in plain English (TC-XXX format)
- Running and CLI commands (system-level, not just startup)
- Known limitations / pending work
- `## Changelog` section (most recent entry first)

**Writing style:** See `writing-style` skill for voice guidelines. Documentation should be direct and practical, avoiding LLM patterns like "leveraging", "robust solutions", or excessive hedging.

### Step 3b — Other feature branch (MCP, agents)

1. Read the feature's code in `app/mcp/[feature]/` or `app/agents/[feature]/`
2. Read the existing doc if it exists
3. Write to `docs/[type]/FEATURE.md`

### Step 4 — Workflow: update

Same as create, but always append a new entry to the `## Changelog` section:

```markdown
### [Short Title] — YYYY-MM-DD [Added|Changed|Fixed|Removed]

[One sentence description of what changed.]

- [Detail 1]
- [Detail 2]

Files: [list of modified files]
```

Use today's date. Put the new entry at the top of the Changelog section (most recent first).

### Step 5 — Return summary

Always end with:

```
## Documentation Updated

### Files changed
- `docs/web/jobs/JOBS.md` — updated overview, added changelog entry
- `app/web/README.md` — added new API endpoint

### What was added
- [Outline of content added/changed]
```

---

## Examples

**"Document the jobs feature"**
→ create workflow, web branch
→ Reads `app/web/src/app/(jobs)/`, `app/web/src/modules/jobs/`
→ Writes `docs/web/jobs/JOBS.md`

**"Add a changelog entry for the new classifier"**
→ update workflow, web branch
→ Reads `app/web/src/modules/jobs/classifier.ts`
→ Appends dated entry to `## Changelog` in `docs/web/jobs/JOBS.md`

**"Document the gmail MCP server"**
→ create workflow, MCP branch
→ Reads `app/mcp/gmail/`
→ Writes `docs/mcp/GMAIL.md`

---

## When to Use

- "document [feature]"
- "create docs for [feature]"
- "update the docs for [feature]"
- "add a changelog entry for [what changed]"
- "write documentation for [feature]"
- **Automatically, before planning or coding** — when the user describes a new feature in plain English, record their words as TC-XXX test cases in the relevant FEATURE.md before presenting a plan

## When Not to Use

- Writing code comments or inline docs → just edit the file directly
- Writing the `app/web/README.md` from scratch (operational setup) → do that directly, this skill handles feature docs
- General note-taking → use `saving-memories` skill instead
