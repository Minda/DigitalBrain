---
name: course-learning-panels
description: Run multi-agent expert panel discussions on course materials. 4 expert personas review each document individually, discuss it together, and produce discussion logs + study notes. Use when user says "panel discussion", "have them review", "multi-agent coursework", or wants expert perspectives on learning material.
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, Task, TodoWrite]
---

# Course Learning Panels

Run multi-agent expert panel discussions across course materials. Each document gets its own focused panel discussion with 4 expert personas, producing a discussion log and structured course notes.

## Quick Start

1. Identify all documents in the course unit/directory
2. Launch one agent per document (never bundle >2 documents per agent)
3. Each agent simulates a 4-person panel discussion
4. Collect outputs and create cross-cutting synthesis

## When to Use

- Processing course materials (articles, papers, transcripts, notes)
- Reviewing technical content from multiple expert perspectives
- Creating study notes with deeper insight than solo reading provides
- Any collection of documents that benefits from multi-perspective analysis

## When Not to Use

- Single short document (just discuss it directly)
- Pure factual extraction (no discussion needed, just summarize)
- Content that requires real-time web lookup (use research tools instead)

---

## Workflow: Expert Panel Review

### Step 1: Scan and Inventory

Identify all documents to discuss. Auto-detect by file type:

```
Directory scan:
├── articles/*.pdf     → Blog posts, articles
├── papers/*.pdf       → Research papers (arxiv, etc.)
├── transcripts/*.md   → Video/audio transcripts
├── *.md               → Notes, reflection questions, concept maps
└── *.pdf              → Other PDFs
```

**Organize by lesson/unit prefix** (e.g., `U2L2_`, `U2L3_`) if available.

Present the inventory to the user before launching:
- File name, type, estimated size
- Grouping by lesson/topic
- Total count of panel discussions to run

### Step 2: Configure Personas

**Default panel (4 experts):**

| Persona | Lens | Key Question |
|---------|------|-------------|
| **Systems Thinker** | Architecture, layers, interactions, scaling | "How do the pieces fit together?" |
| **Failure Analyst** | Breaks, vulnerabilities, adversarial dynamics | "Where does this break?" |
| **Power Analyst** | Governance, accountability, who decides | "Who has power here?" |
| **Learning Synthesizer** | Mental models, schemas, what to remember | "What should a student take away?" |

These can be customized to specific people (e.g., Demis Hassabis, Magnus Carlsen, Garry Kasparov, Justin Sung) or roles. The user chooses.

### Step 3: Launch Individual Panels

**Critical lesson learned: ONE document per agent. Never bundle more than 2.**

Bundling 3+ documents per agent causes:
- Slower execution (the heaviest task bottlenecks everything)
- Shallower coverage per document
- Agents that never complete when given too many large PDFs

**File type reading strategy:**

| File Type | Size | Strategy |
|-----------|------|----------|
| Blog post PDF | <100KB | Read all pages |
| Research paper PDF | >100KB | Read pages 1-15 (abstract, intro, methodology, key results) |
| Transcript (.md) | Any | Read entire file |
| Notes (.md) | Any | Read entire file |
| Large paper PDF | >2MB | Read pages 1-10, then specific sections if needed |

**Agent prompt template:**

```
You are simulating a panel discussion between 4 experts reviewing [DOCUMENT TYPE].

**Read this file:** [FILE_PATH]
(Reading instructions based on file type/size)

**Write output to:** [OUTPUT_DIR]/[NUMBER]_[DESCRIPTIVE_NAME]_discussion.md

## Panelists
[Persona descriptions — 2-3 lines each, including their key question and what they bring]

## Output Format
Start with title + source metadata. Then:

### Section 1: Discussion Log ([EXCHANGE_COUNT] exchanges)
Multi-turn conversation. Speakers build on each other, disagree productively,
stay in character. React to specific content from the document.
End with each panelist's single biggest takeaway.

### Section 2: Course Notes
Structured study notes: key concepts, findings, strengths/limitations,
connections to broader themes, questions to sit with.
```

**Exchange count by document richness:**

| Document Type | Exchanges |
|--------------|-----------|
| Short article (<10 pages) | 12-15 |
| Long article or blog post | 15-18 |
| Research paper | 15-20 |
| Comprehensive notes/synthesis | 25-30 |
| Reflection questions | 20-25 |

### Step 4: Track Progress

Use TodoWrite to track all panels. Check progress by listing output directory:

```bash
ls -la [OUTPUT_DIR]/
```

Each completed panel produces a markdown file. Missing files = still running.

### Step 5: Synthesis Outputs

After all panels complete, launch synthesis agents. Available synthesis types:

**A. Surprising Findings Synthesis**
Read all panel outputs and extract:
- Surprising numbers and data points
- Counterintuitive dynamics
- Hidden connections between documents
- Where panelists disagreed most
- "If You Only Remember 5 Things"

**B. Full Course Notes Synthesis**
Organize all insights by topic/theme (not by document):
- Core concepts and frameworks
- Key research findings
- Open problems and debates
- Study questions and mental models

**C. Cross-Cutting Themes**
Identify patterns that span multiple documents:
- Recurring failure modes
- Governance gaps
- Technical-political tensions
- Research agenda connections

Launch synthesis agents AFTER all panels complete, not before.

---

## Lessons Learned (from first deployment)

### What Worked

1. **Parallel execution** — 20 agents running simultaneously produced ~640KB of output efficiently. Always launch all agents in parallel.

2. **Individual document discussions** — One agent per document produces focused, deep analysis. Each document gets proper attention.

3. **Distinct personas** — The 4-persona framework creates genuine diversity. A systems thinker, a failure analyst, a power critic, and a learning synthesizer cover complementary angles.

4. **Structured output format** — Discussion log + course notes in every file creates consistency. Students can read just the notes or dive into the full discussion.

5. **Background execution** — Running agents in background lets the user keep working. Check progress by listing the output directory.

6. **Numbered files** — Sequential numbering (01_, 02_, ...) makes progress tracking easy and creates natural reading order.

### What Had Challenges

1. **Bundling too many documents in one agent** — An agent given 8 PDFs to read and discuss was the slowest task and bottlenecked everything. It was still running after all 13 individual agents finished. **Fix: One document per agent, always.**

2. **Two-pass problem** — Initially bundled documents by lesson (3 agents for 13 documents), then had to launch individual agents when the user wanted per-document depth. **Fix: Default to individual. Ask before bundling.**

3. **PDF reading uncertainty** — Some PDFs may have garbled text, images-only pages, or be too large. No error handling was built in. **Fix: Check PDF readability early. If a PDF fails to read, report it and skip.**

4. **Large paper page limits** — Arxiv papers (30-60 pages) needed manual page limits. This was an ad hoc judgment call each time. **Fix: Use the file type/size table above as a standard.**

5. **Synthesis agent reading load** — The synthesis agent had to read ~640KB of text across 19 files. This was slow. **Fix: For large collections (>15 files), consider having the synthesis agent read only the Course Notes sections, not the full discussion logs.**

6. **No output validation** — No way to check if each agent actually produced both sections (discussion log + notes) or if the quality was consistent. **Fix: After completion, spot-check 2-3 files for format compliance.**

### Design Principles for Future Workflows

1. **Atomic agents** — One document, one agent, one output file. Composability over monoliths.

2. **Inventory before launch** — Always show the user what will be processed and get confirmation before launching 10+ agents.

3. **Progressive synthesis** — Don't wait for everything to finish. Surface early findings as panels complete.

4. **Personas as parameters** — The persona framework should be configurable. Different courses benefit from different expert panels.

5. **File naming convention** — `[NN]_[descriptive-name]_discussion.md` where NN is zero-padded sequence number.

---

## Output Directory Structure

```
panel_discussions/
├── 01_[document_name]_discussion.md
├── 02_[document_name]_discussion.md
├── ...
├── NN_[document_name]_discussion.md
├── SURPRISING_FINDINGS_SYNTHESIS.md
├── FULL_COURSE_NOTES_SYNTHESIS.md
└── CROSS_CUTTING_THEMES.md
```

## Example Persona Sets

### Technical AI Safety (used in first deployment)
- Demis Hassabis (systems thinker, neuroscience, DeepMind)
- Magnus Carlsen (pattern recognition, failure analysis, optimization)
- Garry Kasparov (power dynamics, governance, accountability)
- Justin Sung (learning science, metacognition, mental models)

### Software Engineering
- Systems Architect (scalability, tradeoffs, patterns)
- Security Researcher (attack surfaces, threat models)
- Product Manager (user impact, business value, priorities)
- Junior Developer (learning perspective, documentation quality)

### Research Paper Review
- Domain Expert (depth, methodology critique)
- Statistician (experimental design, validity)
- Practitioner (real-world applicability)
- Science Communicator (clarity, accessibility, implications)

## Error Handling

| Error | Response |
|-------|----------|
| PDF unreadable | Report to user, skip document, note in synthesis |
| Agent times out | Check output file for partial results, relaunch if needed |
| Too many documents (>25) | Batch into groups, launch in waves |
| User wants different personas | Reconfigure and relaunch affected panels only |
