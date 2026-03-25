---
name: writing-drafting-article
description: Draft a Substack or blog article from existing notes, preserving original phrasing. Asks for source locations (Notion pages, files), weaves content into cohesive narrative with inline links, and generates a references section. Use when user wants to turn notes into an article or says "draft from my notes."
allowed-tools: [ToolSearch, mcp__notion__notion-search, mcp__notion__notion-fetch, mcp__notion__notion-create-pages, mcp__notion__notion-update-page, Read, WebSearch]
---

# Writing: Drafting Article from Existing Notes

Transform existing notes and research into a cohesive article while preserving the user's original voice.

## Core Principle

**Preserve original phrasing wherever possible.** See `writing-style` skill for comprehensive voice guidelines and LLM avoidance patterns.

The user's words carry their intent in ways paraphrasing cannot. Your job is to **curate and structure**, not rewrite.

## Quick Start

1. Ask for source location(s) — Notion page, file path, or pasted content
2. Fetch and read all source material
3. Identify the unifying thread (ask if unclear)
4. Draft article preserving original phrasing
5. Add inline links where references exist
6. Generate references section at the end

## Instructions

### Step 1: Gather Sources

Ask: *"Where is the writing you want to draft from?"*

Accept:
- Notion page title or URL
- File path
- Pasted content
- Multiple sources (will weave together)

### Step 2: Fetch and Analyze

For each source:
1. Fetch full content
2. Extract key passages (preserve exact wording)
3. Identify all links/references
4. Note any `[] verify` tags for fact-checking

### Step 3: Find the Thread

Before drafting, identify what connects the material:
- What's the central insight?
- What's the emotional arc?
- What's the takeaway?

If unclear, ask: *"What's the thread you want to pull on?"*

### Step 4: Draft the Article

Structure using the user's original sentences and paragraphs:
- **Lead with their words** — find the most compelling original phrase for the opening
- **Preserve paragraph structure** where it works
- **Only add transitions** where necessary to connect sections
- **Keep her voice** — if she wrote casually, keep it casual

### Step 5: Add Links

For every claim or reference:
1. Check if source material had a link → use it inline
2. If no link but claim is specific → search web to verify and add source
3. Mark any unverified claims with `[needs source]`

Link style: Inline markdown `[text](url)` — not footnotes (use writing-adding-footnotes skill for that style)

### Step 6: Generate References Section

At the end of the article, add:

```markdown
---

## References

- [Title](url) — brief context
- [Title](url) — brief context
```

Include all links used in the article, organized by section or topic.

## Output Location

Ask: *"Where should I create this draft?"*

Options:
- New Notion page under the source page
- New Notion page in Weekly Reports
- Local markdown file
- Output directly in chat

## Anti-Patterns

❌ **Rewriting in AI voice** — Don't smooth out her writing into generic prose
❌ **Adding flourishes** — No "In conclusion," "It's worth noting," "Interestingly"
❌ **Over-structuring** — Her natural flow may be better than forced sections
❌ **Guessing links** — If you can't verify it, mark it

## Related Skills

- `writing-adding-footnotes` — Convert inline links to footnote style
- `substack-writing` — Voice and style guidance for Substack specifically
- `fetching-notion-content` — Accessing Notion workspace

## Example Interaction

**User:** Draft an article from my Week of Jan 26 note

**Claude:** Let me fetch that note...

*[Fetches content]*

I see several threads here: agent harnesses, human readiness, two AGI paths, and your relational constitution experiment.

What's the thread you want to pull on? Or should I propose a unifying frame?

**User:** The human readiness angle

**Claude:** Got it. I'll draft around "the real frontier is human-AI coherence" using your original phrasing. Where should I create this draft — as a subpage of the weekly note, or somewhere else?
