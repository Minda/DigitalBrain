# Skill Request
What follows is a skill request form. 

!!!SPECIAL INSTRUCTIONS
Wherever possible, as you create this new skill, please try to quote the original user verbatim, even if this means copying in their original phrasing, and then suggesting a full explaination that expands on what you percieve to be their intent. 

If there are areas you feel uncertain of, or that you are reaching, please voice these with the user and discuss with them. They made be able to provide you with extra information. It's safe to not already know everything; your job is to collaborate with the user so they can give you the guidance that you need to complete the task.

---

## 1. Overview

What will this skill do? Describe it in 2–3 sentences.
* Make sure that all of the directories in the project make it into the correct github repository
* Ensure that the git comment makes sense

Trigger keywords: git, github, git commit, commit

---

## 2. Invocation

### Slash command
`/commit _______________`

### Conversational triggers
What would a user say that should activate this skill?
"I want to commit this change"
""

### Context triggers
What situation or file type should activate this skill automatically?
* when the user wants to commit their work
*

---

## 3. Command Line Arguments

| Argument | Description | Required? |
|----------|-------------|-----------|
| `$0` | _______________ | Yes / No |
| `$1` | _______________ | Yes / No |

Or freeform `$ARGUMENTS`: _______________

---

## 4. Workflow Shape

### Is this one linear path, or does the skill handle different types of requests?

Describe 1–4 different things a user might ask this skill to do, and how the approach differs for each.

| User wants to... | Workflow |
|-------------------|----------|
| commit their local changes to github | → commit |
| _______________ | → _______________ |
| _______________ | → _______________ |

### Workflow steps

For each workflow above (or just one if the skill is linear), list the steps:

**Workflow: commit**
1. How many repositories are in this project? Which are public? Which are private?
-Then-
2. for each repository: Review what has changed since the last commit. make a list of all of the changes, feel free to scroll these changes and jot down your notes.
3. Come up with a succicient commit phrase from your notes for each repository of which has changed files. 
4. Return: the address(es) of the updated repositories
 
**Workflow: _______________**
1. _______________
2. _______________
3. _______________
4. Return: _______________

<!--
WHY THIS SECTION EXISTS:
Real skills almost always branch. A PDF skill routes between read/create/edit/merge.
A report skill routes between creation/update/restyle. Without explicit routing,
Claude either follows the wrong workflow or guesses — unreliably.

Example:
| User wants to...                        | Workflow         |
|-----------------------------------------|------------------|
| Create a report from raw data           | → Creation       |
| Update an existing report with new data | → Update         |
| Change the styling/format of a report   | → Restyle        |

Creation Workflow:
1. Identify data sources
2. Determine report type (financial, operational, executive)
3. Load appropriate reference file
4. Build report structure
5. Generate charts
6. Validate
-->

---

## 5. Known Failure Modes

What does Claude reliably get wrong when attempting this task without guidance? Be specific — these should be concrete mistakes, not general advice.

| What Claude does wrong | What it should do instead |
|------------------------|--------------------------|
| _______________ | _______________ |
| _______________ | _______________ |
| _______________ | _______________ |

<!--
WHY THIS SECTION EXISTS:
Every mature skill has a catalog of specific pitfalls. These come from iteration
and are often the most valuable part of the skill. Examples from real skills:

- DOCX: Uses unicode bullets (•) instead of LevelFormat.BULLET numbering config
- DOCX: Uses \n for line breaks instead of separate Paragraph elements
- XLSX: Calculates values in Python and hardcodes them instead of using Excel formulas
- XLSX: Uses ShadingType.SOLID (causes black backgrounds) instead of ShadingType.CLEAR
- PPTX: Defaults to blue color scheme regardless of topic
- PPTX: Repeats the same layout on every slide
- Frontend: Converges on Inter/Roboto/Space Grotesk and purple gradients
- PDF: Uses unicode subscript characters that render as black boxes in ReportLab
-->

---

## 6. Guidelines

| Always | Never |
|--------|-------|
| _______________ | _______________ |
| _______________ | _______________ |

**Ask user if:** _______________

---

## 7. Error Handling

### Input errors

| Condition | Response |
|-----------|----------|
| _______________ | "_______________ " |
| _______________ | "_______________" |

### Output verification

How should Claude verify that what it produced is actually correct before delivering it? What are the most common ways the output can be subtly wrong?

**Content checks:**
- [ ] _______________
- [ ] _______________

**Visual/structural checks:**
- [ ] _______________
- [ ] _______________

**Automated checks** (scripts, linters, validators to run):
- _______________
- _______________

Should Claude fix and re-verify in a loop? Yes

<!--
WHY THIS SECTION EXISTS:
Claude's first output is almost never flawless. Without explicit verification,
subtle errors ship unnoticed. Real skills mandate QA steps:

- PPTX: Convert slides to images, send to a subagent for visual inspection, then
  fix-and-verify in a loop until a clean pass completes.
- XLSX: Run recalc.py to recalculate all formulas, check for #REF!, #DIV/0!, etc.,
  fix every error, and re-run until status is "success."
- DOCX: Run `grep -iE "xxxx|lorem|ipsum"` to catch leftover placeholder text.

The instruction "Assume there are problems. Your job is to find them." appears
across multiple skills.
-->

---

## 8. Quality Standards

What does "excellent" look like for this output, beyond just being correct? Describe the quality bar, aesthetic standard, or professional expectation.

* Single sentence that encapsulates the intent of the commit
* The commit will be easy to read and rememeber what work was completed later
*

### Degrees of freedom

How much creative latitude should Claude have?

- [ ] **Low** — Follow exact specifications. Consistency is critical. Deviation is a bug.
- [ X] **Medium** — Preferred patterns exist, but some adaptation to context is fine.
- [ ] **High** — Multiple approaches are valid. Claude should use judgment and be creative.

<!--
WHY THIS SECTION EXISTS:
Some skills need Claude to aim far above "technically correct." The creative skills
(canvas-design, algorithmic-art) spend significant tokens framing expectations:

  "Pretend the user has already said: 'This needs to look like it came from a
  top-tier consulting firm, not a script.' Act accordingly."

  "The user ALREADY said 'It isn't perfect enough. It must be pristine, a
  masterpiece of craftsmanship, as if it were about to be displayed in a museum.'"

Even non-creative skills benefit from this. A financial model skill might say:
"This is not a data dump. Every element serves the reader's understanding."

The degrees-of-freedom question comes from the skill-creator's own guidance:
narrow bridge with cliffs = low freedom, open field = high freedom.
-->

---

## 9. Environmental Adaptation

Does this skill behave differently depending on what tools, integrations, and context are available?

### Data sources / inputs
How should Claude get the data it needs? List in order of preference, with fallbacks.

| If available... | Then... |
|-----------------|---------|
| _______________ | _______________ |
| _______________ | _______________ |
| Nothing / unclear | Ask the user: "_______________ " |

### Output format
Should the output format adapt to the user's situation?

| Context | Preferred format |
|---------|-----------------|
| _______________ | _______________ |
| _______________ | _______________ |
| User hasn't specified | Default to: _______________ |

### Integration-dependent behavior
List any integrations that unlock different behavior (e.g., Slack, Google Drive, databases):

- If _______________ is available: _______________
- If _______________ is NOT available: _______________

<!--
WHY THIS SECTION EXISTS:
The doc-coauthoring skill detects whether Slack/Drive integrations are connected and
adapts: pull context directly if available, suggest enabling connectors if not, or
fall back to asking the user to paste content.

Without this, skills either assume the best case (all tools available) and fail,
or assume the worst case (nothing available) and ignore powerful tools.
-->

---

## 10. File Structure

### What information does Claude need every time vs. only sometimes?

**Always needed** (goes in SKILL.md — kept under ~200 lines):
- if it's not available in the project, Claude may need to know which repositories exist in the project, and where they are stored.
- _______________

**Needed only for specific sub-tasks** (goes in separate reference files):

| Reference file | Loaded when... |
|----------------|----------------|
| _______________ | _______________ |
| _______________ | _______________ |
| _______________ | _______________ |

### Scripts to bundle

Which operations should be pre-written scripts that Claude runs, rather than code Claude writes from scratch?

| Script | What it does | Why Claude shouldn't improvise this |
|--------|-------------|-------------------------------------|
| _______________ | _______________ | _______________ |
| _______________ | _______________ | _______________ |

### Assets to bundle

Templates, fonts, images, or other files the skill needs at runtime:

| Asset | Purpose |
|-------|---------|
| _______________ | _______________ |
| _______________ | _______________ |

### Resulting structure

```
skill-name/
├── SKILL.md
├── references/
│   ├── 
│   └── 
├── scripts/
│   ├── 
│   └── 
└── assets/
    ├── 
    └── 
```

<!--
WHY THIS SECTION EXISTS:
Skills are not flat documents. Every non-trivial skill in the repository uses
progressive disclosure: SKILL.md stays lean (~200 lines) and routes to reference
files loaded on demand. This keeps the context window focused.

Examples:
- PDF: SKILL.md covers basics, FORMS.md loaded only for form-filling, REFERENCE.md
  for advanced features.
- MCP-builder: SKILL.md has the workflow, four reference files loaded at different
  phases (best practices, Python guide, TypeScript guide, evaluation guide).
- Internal-comms: SKILL.md is a thin router, four example files loaded based on
  communication type (3P updates, newsletter, FAQ, general).

Scripts are often the core of the skill:
- DOCX: unpack.py, pack.py, comment.py, accept_changes.py
- XLSX: recalc.py for formula recalculation
- Web-artifacts-builder: init-artifact.sh, bundle-artifact.sh
- Slack-gif-creator: entire core/ library (gif_builder, validators, easing)

Assets provide fixed scaffolding:
- Algorithmic-art: viewer.html template
- Canvas-design: 40+ bundled font files
- Theme-factory: PDF showcase + 10 theme definition files
- Web-artifacts-builder: pre-packaged shadcn components
-->

---

## 11. Example Interaction

Show a complete example of this skill in action.

**User:** "commit changes"

**Claude should:**
1. create concise commit statements
2. check the statements with the user
3. commit the project
4. Verify: _______________
5. Return: github links

---

## 12. Options

- [ ] **Manual only** — require `/slash-command` to invoke
- [ X] **Auto-invoke** — Claude activates when context matches (default)

---


Intelligently detect which have changes and only commit those
skill flag this kind of thing
plain descriptive prose plus feat:, fix:, docs:
whatever helps keep the commit readable, memorable and concise
always check the statements and ask for user feedback first

---

a correction I needed to make:
you don't need to ask to push. you should assume the user wants this unless they ask you not to. so pushing is the default.


after I edited my next file:
you don't need to commit now, only if I ask to commit. I'm curious what made you think I wanted to commit?