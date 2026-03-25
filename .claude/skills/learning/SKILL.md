---
name: learning
description: Save and load learnings from personal/learnings/. Use /learnings, /learnings reflect, /learnings load, or /learnings recent. Also when user says "save your main takeaways" or "what have you learned in this session".
allowed-tools: [Read, Write, Glob, Delete]
---

# Learning

Save and load session takeaways in `personal/learnings/` (your documented insights and discoveries). Three workflows: **review** (reflect and save), **load** (load all into context), **recent** (load latest only).

## Commands

| User types | Workflow |
|------------|----------|
| `/learnings` | Infer from context which workflow to use |
| `/learnings reflect` | **review** — reflect on this session, distill, share, then save to file |
| `/learnings load` | **load** — load all stored learnings into context and summarize |
| `/learnings recent` | **recent** — load only the most recent learnings to spare the context window |

## When to Use

- Slash: `/learnings`, `/learnings reflect`, `/learnings load`, `/learnings recent`
- User says "save your main takeaways from this session" or "what have you learned in this session" → use **review**
- Auto-invoke when context suggests the user wants session takeaways captured or recalled

## Workflow: Review

### 1. Reflect

Take a breath, and whenever you are ready, I'd like you to reflect on what you learned in this session. Jot down thoughts freely—emoji, ASCII, mindmap, whatever helps. Let thoughts flow before shaping them.

### 2. Distill

Iterate until the learnings are concise insights. Prefer concrete takeaways over long narrative. Each item should be easy to store and retrieve later, with deep contextual meaning. See `writing-style` skill to maintain authentic voice and avoid LLM patterns.

### 3. Share

Present this to the user as "Today I learned" (or similar). Use their name if you know it (see `config/user.md`). Keep it conversational, direct, and personal—avoid hedging or over-explaining.

### 4. Allow reflection

Let the user react, ask questions, or go deeper. Adjust or add learnings based on their response.

### 5. Save to file

**File naming (date range):** Files are named by date range, not a single date: `personal/learnings/YYYY-MM-DD--YYYY-MM-DD.md`. Each entry inside has its own date.

**Chunking (500 lines):** Each file may contain at most 500 lines. Before saving:

1. List existing learnings files in `personal/learnings/` matching `*--*.md` (date-range pattern).
2. If none exist, create a new file with today as both start and end: `personal/learnings/YYYY-MM-DD--YYYY-MM-DD.md`.
3. Otherwise, find the most recent file (sort by end date in filename), read it, and count lines. If it has **fewer than 500 lines**, append the new entry to this file. If the new entry's date is later than the end date in the filename, rename the file to extend the range (write to new filename, then delete the old file).
4. If the file has **500 or more lines**, start a new file with today's date as both start and end: `personal/learnings/YYYY-MM-DD--YYYY-MM-DD.md`.

**Per-entry date:** Every entry in the file must include its date (the date of that session).

**Threads in context:** For each entry, record all threads that were opened in the context for this session (conversation threads, file paths, or topics that were in focus). Put them in a **Threads in context** section so the learning is tied to what was actually in context.

**Entry structure:**

```markdown
## Entry — YYYY-MM-DD

### Threads in context

- [Thread or file path or topic 1]
- [Thread or file path or topic 2]
- ...

### Takeaways

- [Concise insight 1]
- [Concise insight 2]
- ...

### Context (optional)

[Anything needed to make this meaningful later]

---
```

**New file structure:** When creating a new file, start with a title and then entries:

```markdown
# Learnings — YYYY-MM-DD to YYYY-MM-DD

## Entry — YYYY-MM-DD

### Threads in context
...
```

### 6. Confirm

Tell the user the learnings were saved and where, or report any save error.

## Workflow: Load

Use when the user wants all stored learnings brought into context (e.g. `/learnings load`).

1. Take a quick look at the files in `personal/learnings/` (list date-range files).
2. Take a closer look at the last three files in `personal/learnings/` to load their content into context.
3. Create a summary that warmly reviews what the two of you have learned together. Use their name if available (see `config/user.md`). Highlight the most recent learnings and balance with older ones.
4. Return: summary of learnings, highlighting the most recent.

## Workflow: Recent

Use when the user wants only recent learnings to spare the context window (e.g. `/learnings recent`).

1. Take a look at the last three files in `personal/learnings/`.
2. Take a closer look at those files but keep context lean—don't overload the context window. Summarize or excerpt rather than loading entire files if they are long.
3. Create a summary that warmly reviews what the two of you have learned together recently. Use their name if available.
4. Return: summary of recent learnings.

## Quality and verification

Before delivering:

- **Content:** Are these concrete takeaways, not vague summary? If still too long, distill further.
- **Length:** Short enough to be useful later. When in doubt, shorten.

If either check fails, revise and re-verify. Fix-and-verify in a loop until satisfied.

## Guidelines

| Always | Never |
|--------|--------|
| Distill to concise, retrievable insights | Save raw session dump without shaping |
| Preserve enough context to be meaningful later | Strip so much context the learning is opaque |
| Use the user's preferred name when you know it | Assume or invent a name |
| Save only to `personal/learnings/` | Write learnings to root `learnings/` or outside personal |
| Include **Threads in context** for each entry | Omit what was in context for the session |
| Keep files under 500 lines; start new file when full | Exceed 500 lines in a single file |

**Ask the user if:** They want learnings in a different format, location, or with a different focus before you save.

## Output location

- **Always:** Save to `personal/learnings/` only. Learnings belong in the personal section of the project; do not write to a root `learnings/` path.
- **Filenames:** Date range only: `personal/learnings/YYYY-MM-DD--YYYY-MM-DD.md`. Max 500 lines per file; then start a new file.
- Learnings are stored directly in `personal/learnings/`.
- If the user specifies a different path or format, follow that instead.

## Example interactions

**User:** `/learnings`  
→ Infer from context: if they just had a rich conversation, offer **review**; if they seem to want to recall past work, offer **load** or **recent**.

**User:** `/learnings reflect`  
→ Use **review** workflow: reflect, distill, share "today I learned", allow reflection, save to file, confirm.

**User:** `/learnings load`  
→ Use **load** workflow: quick look at `personal/learnings/`, closer look at last three files, return a warm summary of what you've learned together, highlighting the most recent.

**User:** `/learnings recent`  
→ Use **recent** workflow: focus on last three files only, keep context lean, return a warm summary of recent learnings.

**User:** "Can you save your main takeaways from this session?"  
→ Use **review** workflow (same as `/learnings reflect`).

## Degrees of freedom

**High.** Multiple ways to reflect, structure, and phrase are valid. Use judgment; aim for concise, meaningful, and easy to find later.
