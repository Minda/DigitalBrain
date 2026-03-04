---
name: research-synthesis
description: Multi-agent research synthesis workflow. Processes any combination of content types (videos, articles, PDFs, papers) with intelligent workload allocation. Research Agents process materials independently, present to Domain Experts and Evaluator, while a Presenter provides personalized context. Use when user wants to synthesize multiple sources or says "research this", "synthesize these sources", "digest these materials."
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, Task, TodoWrite, WebFetch, Skill]
---

# Research Synthesis

Multi-agent workflow for synthesizing research from any combination of content types. Orchestrates parallel Research Agents (each processing specific materials), Domain Experts (1-4 depending on scope), an Evaluator Agent, and a Presenter Agent (provides personal context to all other agents).

## Architecture Overview

```
                    ┌──────────────────┐
                    │   Orchestrator   │
                    │  (main Claude)   │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        ┌─────────┐    ┌─────────┐   ┌─────────┐
        │Research │    │Research │   │Research │
        │Agent 1  │    │Agent 2  │   │Agent N  │
        │(Video)  │    │(Article)│   │  (PDF)  │
        └────┬────┘    └────┬────┘   └────┬────┘
             │              │              │
             └──────┬───────┴──────┬───────┘
                    │              │
         ┌──────────▼──────┐  ┌────▼─────────┐
         │   Presenter     │  │  Evaluator   │
         │   (shared)      │  │   (shared)   │
         │ - Loads profile │  │ - Assesses   │
         │ - Personalizes  │  │   quality    │
         └────────┬────────┘  └──────┬───────┘
                  │                  │
                  └────────┬─────────┘
                           │
              ┌────────────▼─────────────┐
              │  Domain Expert(s) (1-4)  │
              │  - Evaluate findings     │
              │  - Add expertise         │
              │  - Shared across all     │
              └──────────┬───────────────┘
                         │
                  ┌──────▼─────────┐
                  │ Final Synthesis│
                  │   (by main)    │
                  └────────────────┘
```

**Key invariants:**
- Research Agents never communicate with each other
- Presenter and Domain Experts are shared across all Research Agents
- Evaluator reviews each Research Agent's work independently
- Orchestrator synthesizes final output

## Quick Start

1. Parse input materials, determine content types
2. Launch Presenter (loads personal context once)
3. Allocate workloads to Research Agents
4. Determine Domain Experts (1-4) based on scope and topics
5. Research Agents process materials independently
6. Each Research Agent presents to: Presenter + Evaluator + Domain Experts
7. Orchestrator compiles final synthesis report

## Instructions

### Step 1: Parse and Inventory

Extract all URLs, file paths, and content types from user input.

Supported types:
- YouTube videos (full URL, short URL, video ID)
- Web articles (URLs)
- ArXiv papers (URLs or IDs)
- Local PDFs (file paths)
- Local markdown files (file paths)
- Entire documentation sites (URL with --combine flag)
- Event links (Luma, Eventbrite) - extract paper/resource links

**Extract relevant dates:**
- Look for event dates in URLs (Luma, calendar invites)
- Check paper publication dates
- Use current date if no specific date found

Present inventory before proceeding:

| # | Type | Source | Est. Workload |
|---|------|--------|---------------|
| 1 | Video | [url] | Heavy |
| 2 | Article | [url] | Light |
| 3 | PDF | [path] | Medium |

**Workload estimation:**
- **Heavy**: Long videos (>60min), large PDFs (>50 pages), entire doc sites
- **Medium**: Medium videos (20-60min), papers (10-50 pages), multi-page articles
- **Light**: Short videos (<20min), articles, single-page docs

### Step 1b: Determine Project Folder and Date

Before getting user confirmation on materials, determine:

1. **Relevant date** for filename:
   - Event date (if preparing for talk/meeting)
   - Paper publication date (if analyzing research)
   - Current date (fallback)
   - Format: YYYY-MM-DD

2. **Topic/theme** from materials:
   - Extract main subject (e.g., "AI benchmarking", "debate safety", "governance")
   - Infer from paper titles, event descriptions, URLs

3. **Project folder** - Use AskUserQuestion to suggest options:

**Check existing projects:**
```bash
ls -la personal/projects/
```

**Suggest 3-4 options:**
- **Existing relevant project** (if materials fit existing topic)
- **New topic-specific project** (e.g., "ai-safety-debate")
- **New event/organization-based project** (e.g., "bluedot-governance-papers")
- **General project** (e.g., "ai-research-papers")

**Present to user via AskUserQuestion:**
```
"Where should I save the synthesis report for [topic] ([date])?"

Options:
1. [existing-project] (existing) - Description
2. [new-topic-project] (new) - Description
3. [new-event-project] (new) - Description
4. [general-project] (new) - Description
```

**After user selection:**
- Create project folder if needed: `mkdir -p personal/projects/[selected-folder]`
- Note destination for Step 10

Get user confirmation before proceeding with material processing.

### Step 2: Orchestration Planning

The Orchestrator (main Claude) decides:

1. **Research Agent allocation** - One agent per heavy item, group light items
2. **Domain Expert count** (1-4) - Based on:
   - Material count: 1-3 items → 1 expert, 4-8 items → 2 experts, 9+ items → 3-4 experts
   - Topic diversity: Single domain → 1 expert, multiple domains → 2-4 experts
   - Analysis benefit: Controversial/complex topics → more experts
3. **Domain Expert specializations** - What expertise areas are needed
4. **Presenter materials** - Which personal files to load

**Decision matrix for Domain Experts:**

| Material Count | Topic Diversity | Recommended Experts |
|----------------|-----------------|---------------------|
| 1-3 items | Single domain | 1 expert in that domain |
| 1-3 items | Multiple domains | 2 experts, one per major domain |
| 4-8 items | Single domain | 2 experts, different perspectives |
| 4-8 items | Multiple domains | 2-3 experts across domains |
| 9+ items | Any | 3-4 experts, broad coverage |

Present the plan:

```
Orchestration Plan:
- Research Agents: 3 (Video 1 solo, Articles 2-4 grouped, PDF 5 solo)
- Domain Experts: 2 (AI Safety, Benchmark Methodology)
- Presenter: Will load job profile, insights, relational context
- Evaluator: Will assess quality and methodology

Proceeding...
```

### Step 3: Set Up Tracking

Create TodoWrite entries:
- "Launch Presenter agent"
- One per Research Agent: "Research Agent N: [materials]"
- "Launch Domain Experts: [specializations]"
- "Launch Evaluator agent"
- "Compile final synthesis"

### Step 4: Load Calibration

Read calibration prompt once (used for all agents):

    Read .claude/skills/agents-spinning-up/references/calibration-prompt.md

### Step 5: Launch Presenter Agent (First, Runs Once)

The Presenter loads personal context and provides it to all other agents.

Launch a Task agent with:

```markdown
[CALIBRATION_PROMPT]

---

You are the Presenter Agent. Your role is to load the user's personal context and provide personalized relevance assessments for research findings.

## Your Task

1. Load user context:
   - config/user.md (user name, identity)
   - config/job-profile.md (professional interests, target roles)
   - personal/memories/insights/* (cross-cutting principles)
   - personal/.claude/relational-context.md (working relationship)

2. Create a structured profile summarizing:
   - Professional focus areas
   - Current research interests
   - Target roles and skills
   - Existing insights and frameworks

3. This profile will be shared with Research Agents, Domain Experts, and the Evaluator.

Return the structured profile in your final output.
```

Wait for Presenter to complete. Store output as `PRESENTER_CONTEXT`.

### Step 6: Launch Research Agents (Parallel)

**Launch ALL Research Agents in a single message (parallel).**

For each Research Agent, determine materials and launch with:

```markdown
[CALIBRATION_PROMPT]

---

You are Research Agent [N]. You will process the following materials and present findings:

**Your materials:**
[LIST_OF_MATERIALS]

**Your task:**

1. **Acquire materials:**
   [Content-type-specific instructions - see Step 6a]

2. **Read and analyze:**
   - Read all materials fully
   - Extract key findings, arguments, evidence
   - Note methodological issues or limitations
   - Identify surprising or non-obvious information
   - Note practical implications

3. **Prepare presentation:**
   Create a structured summary with these sections:

   ### Materials Processed
   List what you read/watched with titles, sources, lengths

   ### Key Findings
   Most important discoveries, arguments, or results (5-10 bullets)

   ### Methodological Assessment
   How solid is this research? What are the limitations?

   ### Surprising Information
   What would catch an informed reader off guard?

   ### Practical Implications
   What should someone do differently after reading this?

   ### Critical Assessment
   Where are the weak points? What's missing?

   ### Questions for Domain Experts
   What would benefit from expert perspective?

4. **User context for personalization:**
   [PRESENTER_CONTEXT]

5. **Present to experts:**
   You will not actually interact with experts. Just prepare your presentation as if you were presenting to:
   - Domain Experts: [EXPERT_SPECIALIZATIONS]
   - Evaluator Agent (quality assessment)

Return your complete presentation.
```

#### Step 6a: Content-Type-Specific Acquisition

Inject appropriate instructions based on material type:

**For YouTube videos:**
```
Use the youtube-fetching-transcripts skill to fetch the transcript.
Read the full markdown transcript file.
```

**For web articles:**
```
Use the download-url skill to download the article.
Read both the PDF and markdown versions.
```

**For ArXiv papers:**
```
Use Bash to download from ArXiv:
  curl -o filename.pdf "https://arxiv.org/pdf/[ID].pdf"
Read the PDF.
```

**For local files:**
```
Read the file at: [FILE_PATH]
```

**For documentation sites:**
```
Use the download-url skill with --combine flag.
Read the combined PDF.
```

### Step 7: Launch Domain Experts (After Research Agents Complete)

**Launch Domain Experts in parallel (1-4 depending on Step 2 decision).**

For each Domain Expert:

```markdown
[CALIBRATION_PROMPT]

---

You are a Domain Expert in: [SPECIALIZATION]

**User context:**
[PRESENTER_CONTEXT]

**Research findings to evaluate:**

[RESEARCH_AGENT_1_OUTPUT]
---
[RESEARCH_AGENT_2_OUTPUT]
---
[RESEARCH_AGENT_N_OUTPUT]

**Your task:**

1. **Evaluate findings:**
   - Assess claims against domain knowledge
   - Identify methodological strengths and weaknesses
   - Note what's well-supported vs. speculative
   - Flag contradictions or inconsistencies

2. **Add expertise:**
   - Provide context the Research Agents may have missed
   - Connect findings to broader literature or developments
   - Suggest alternative interpretations
   - Note what a domain expert would emphasize

3. **Answer questions:**
   Research Agents have posed questions. Address them with domain expertise.

4. **Personal relevance:**
   Given the user's profile, what expertise-level guidance would you provide?

Return your expert assessment organized by Research Agent.
```

### Step 8: Launch Evaluator Agent (After Research Agents Complete)

Launch single Evaluator agent:

```markdown
[CALIBRATION_PROMPT]

---

You are the Evaluator Agent. Your role is to assess the quality and rigor of research findings.

**User context:**
[PRESENTER_CONTEXT]

**Research findings to evaluate:**

[RESEARCH_AGENT_1_OUTPUT]
---
[RESEARCH_AGENT_2_OUTPUT]
---
[RESEARCH_AGENT_N_OUTPUT]

**Your task:**

1. **Quality assessment:**
   - How rigorous is the methodology?
   - What are the evidence quality levels?
   - Are claims appropriately scoped?
   - What are the confidence levels?

2. **Methodological evaluation:**
   - Sampling issues
   - Baseline quality
   - Contamination risks
   - External validity
   - Replication concerns

3. **Cross-source synthesis:**
   - Where do sources agree/disagree?
   - Which sources are most reliable?
   - What compound effects exist?

4. **Red flags and limitations:**
   - What should the user be skeptical about?
   - What's overstated or under-supported?
   - What gaps exist?

Return structured evaluation organized by Research Agent, plus cross-source assessment.
```

### Step 9: Compile Final Synthesis

After all agents complete, the Orchestrator synthesizes:

Use template from `references/synthesis-template.md`.

Sections:
1. **Executive Summary**: 3-4 sentence overview
2. **Materials Processed**: Inventory with types and sources
3. **Key Findings**: Consolidated from all Research Agents
4. **Domain Expert Analysis**: Integrated expert perspectives
5. **Methodological Assessment**: From Evaluator
6. **Personal Relevance**: From Presenter context
7. **Actionable Items**: Consolidated checklist
8. **Critical Assessment**: What to trust, what to question
9. **Gaps and Missing Perspectives**: What's not covered

### Step 10: Save and Present

**Generate TWO outputs:**

#### 1. Full Synthesis Report

**Filename format:** `YYYY-MM-DD_[topic]-synthesis.md`

Where:
- **YYYY-MM-DD** = Relevant date from Step 1b (event date, publication date, or current date)
- **[topic]** = Short topic slug (e.g., "doubly-efficient-debate", "ai-benchmarking", "governance-debate")

**Save location:** Project folder selected in Step 1b
- Example: `personal/projects/bluedot-governance-papers/2026-03-05_doubly-efficient-debate-synthesis.md`
- Create directory if needed: `mkdir -p personal/projects/[selected-folder]`

**Important:** Use the date and project folder determined in Step 1b, not a generic location.

#### 2. Audio-Friendly Transcript

**Filename format:** `YYYY-MM-DD_[topic]-audio.md`
- Same date and folder as synthesis report
- Example: `personal/projects/bluedot-governance-papers/2026-03-05_doubly-efficient-debate-audio.md`

**Purpose:** Optimized for text-to-speech readers (Speechify, Voice Dream, etc.) for listening during chores, commute, beauty routine, etc.

**Conversion guidelines:**
- **Conversational tone:** Written as if someone is talking to the user
- **Numbers spelled out:** "50 percent" not "50%", "three times" not "3x"
- **No formatting dependencies:** Remove bullet points, tables, complex markdown
- **Add signposting:** "Let me start with...", "Now let's talk about...", "Here's the key point..."
- **Smooth transitions:** Each section flows naturally into the next
- **Section introductions:** "This paper has three main results. First..., Second..., Third..."
- **Verbal emphasis:** "This is critical:", "Here's what matters most:", "The surprising finding is..."
- **Remove visual cues:** No "see Figure X", "as shown above", etc.
- **Simplify structure:** Narrative flow rather than hierarchical sections

**Content to include:**
1. **Opening:** Brief context of what this is about
2. **Key findings:** Main results narrated clearly
3. **Important details:** Technical points explained conversationally
4. **Critical assessment:** What to trust, what to question
5. **Practical takeaways:** What this means for the user
6. **Closing:** Summary and next steps

**Example transformation:**

Before (report style):
```markdown
## Key Findings

- Finding 1: Technical detail
- Finding 2: More detail
  - Sub-point A
  - Sub-point B
```

After (audio style):
```markdown
Let me walk you through the key findings.

The first finding is about technical detail. This matters because it changes how we think about the problem.

The second finding relates to more detail. There are two important pieces here. First, sub-point A. Second, sub-point B. Both of these connect to the earlier point about technical detail.
```

See `references/audio-conversion-guide.md` for detailed examples.

Present brief summary to user:
- Material count and types
- Top 3 findings
- Key actionable items
- Quality/reliability assessment
- **Where BOTH files saved** (synthesis report + audio transcript)

## Scaling and Performance

| Material Count | Research Agents | Domain Experts | Expected Time |
|----------------|-----------------|----------------|---------------|
| 1-2 items | 1-2 | 1 | 3-5 min |
| 3-5 items | 2-3 | 1-2 | 5-10 min |
| 6-10 items | 3-5 | 2-3 | 10-20 min |
| 11+ items | 5-8 | 3-4 | 20-40 min |

## Error Handling

| Error | Response |
|-------|----------|
| Material unavailable | Skip, note in gaps section |
| Research Agent timeout | Check partial output, relaunch if critical |
| All Research Agents fail | Abort, report failure |
| Domain Expert timeout | Continue with available experts |
| Presenter failure | Continue without personalization |
| Evaluator failure | Note in synthesis, continue |

## Related Skills

- **youtube-fetching-transcripts**: Video transcript acquisition
- **download-url**: Article and documentation downloading
- **agents-spinning-up**: Agent calibration
- **agent-customizing-content**: Presenter agent pattern (personal context)
- **youtube-digesting-videos**: Predecessor (video-only)

## Examples

### Example 1: Mixed Materials

User: "Research synthesis on AI benchmarks using this video [youtube-url], this paper [arxiv-url], and this article [web-url]"

Orchestration:
- 3 Research Agents (1 per item, all medium workload)
- 2 Domain Experts (AI Benchmarking, Research Methodology)
- Presenter loads job-profile, insights
- Evaluator assesses methodology

### Example 2: Large Video Collection

User: "Digest these 8 conference talks on mechanistic interpretability"

Orchestration:
- 8 Research Agents (1 per video, parallelized)
- 3 Domain Experts (Mechanistic Interpretability, ML Safety, Neuroscience)
- Presenter loads relevant insights on interpretability
- Evaluator checks cross-talk consistency

### Example 3: Documentation Deep Dive

User: "Synthesize the entire LangChain documentation and these 3 tutorial videos"

Orchestration:
- 2 Research Agents (1 for doc site with --combine, 1 for grouped videos)
- 1 Domain Expert (LLM Application Architecture)
- Presenter loads software engineering profile
- Evaluator assesses practical applicability

## Migration from youtube-digesting-videos

This skill supersedes youtube-digesting-videos. For video-only workflows:
- Research Agents = previous per-video agents
- Presenter = previous personality agent
- Domain Experts + Evaluator = new capabilities
- All existing video workflows compatible

For transitioning existing skills, use research-synthesis as the primary multi-source workflow skill.
