---
name: research-synthesis
description: Multi-agent research synthesis workflow. Processes any combination of content types (videos, articles, PDFs, papers) with intelligent workload allocation. Research Agents process materials independently. Evaluator gates quality before experts. Domain Experts and a Contrarian Agent discuss filtered findings. Presenter synthesizes the final output personalized for the recipient. Use when user wants to synthesize multiple sources or says "research this", "synthesize these sources", "digest these materials."
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, Task, TodoWrite, WebFetch, Skill]
---

# Research Synthesis

Multi-agent workflow for synthesizing research from any combination of content types. Five-phase pipeline: Presenter loads recipient context, Research Agents process materials (with emphasis on surprises), Evaluator gates quality, Domain Experts and Contrarian Agent discuss filtered findings, and Presenter synthesizes the final personalized output.

## Architecture Overview

```
Phase 0         ┌─────────────────────────────────────┐
                │      Pre-Synthesis Phase            │
                │  Individual agents create document  │
                │  syntheses (1 per large doc, or     │
                │  1 per batch of small docs)         │
                └───────────────┬─────────────────────┘
                                │
                                ▼
                      Document Syntheses (.md files)
                                │
Phase 1                ┌────────▼─────────┐
                       │    Presenter     │  Load recipient profile
                       │  (loads context) │
                       └────────┬─────────┘
                                │
Phase 2         ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
          ┌──────────┐   ┌──────────┐   ┌──────────┐
          │Research  │   │Research  │   │Research  │  Review syntheses
          │Agent 1   │   │Agent 2   │   │Agent 3   │  (max 3 agents)
          └────┬─────┘   └────┬─────┘   └────┬─────┘
               │              │              │
               └──────────────┼──────────────┘
                              │
Phase 3              ┌────────▼──────────┐
                     │    Evaluator      │  Quality gate
                     │ + Presenter ctx   │  Filter, assess, brief
                     └────────┬──────────┘
                              │
Phase 4       ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │ Domain   │   │ Domain   │   │Contrarian│  Discuss filtered
        │Expert 1  │   │Expert N  │   │  Agent   │  findings
        └────┬─────┘   └────┬─────┘   └────┬─────┘
             │              │              │
             └──────────────┼──────────────┘
                            │
Phase 5            ┌────────▼──────────┐
                   │Presenter Synthesis│  Final personalized
                   │  (for recipient)  │  synthesis
                   └────────┬──────────┘
                            │
                     ┌──────▼──────┐
                     │   Output    │  Save reports
                     └─────────────┘
```

**Key invariants:**
- Pre-synthesis phase prevents Research Agents from reading large PDFs/videos directly
- Research Agents review document syntheses, not raw materials
- Maximum 3 Research Agents (prevents system crashes)
- Research Agents never communicate with each other
- Evaluator acts as quality gate BEFORE experts see findings
- Contrarian Agent always runs alongside Domain Experts
- Presenter bookends the pipeline: loads context first, synthesizes last
- Domain Experts and Contrarian receive Evaluator-filtered output, not raw Research Agent output

## Quick Start

1. Parse input materials, determine content types
2. **Pre-synthesis phase**: Create document syntheses (1 agent per large doc, or 1 per batch of small docs)
3. Launch Presenter (loads personal context once)
4. Allocate workloads to Research Agents (max 3 agents)
5. Research Agents review document syntheses (not raw materials)
6. Evaluator filters and assesses findings (quality gate)
7. Domain Experts + Contrarian discuss Evaluator-filtered findings
8. Presenter synthesizes final output personalized for recipient
9. **Final synthesis includes**: "Implementation Steps for Neurodiverse Users" with explicit task breakdown and motivation explanations

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

### Step 2: Pre-Synthesis Phase (New)

**Critical:** To prevent system crashes, Research Agents do NOT read large PDFs, videos, or transcripts directly. Instead, we first create document syntheses that Research Agents will review.

**Pre-synthesis allocation:**

1. **Identify synthesis needs:**
   - **Large documents** (>50 pages PDF, >60min video, >10MB): 1 agent per document
   - **Medium documents** (10-50 pages, 20-60min): Batch 2-3 together for 1 agent
   - **Small documents** (<10 pages, <20min): Batch 3-5 together for 1 agent

2. **Launch pre-synthesis agents in parallel:**

For each pre-synthesis agent:

```markdown
[CALIBRATION_PROMPT]

---

You are a Pre-Synthesis Agent. Your job is to read source material and create a structured synthesis that Research Agents will review.

**Your materials:**
[LIST_OF_DOCUMENTS_TO_READ]

**Your task:**

1. **Read all assigned materials fully**
   - For PDFs >50 pages: Read first 20 pages thoroughly, skim remainder for key sections
   - For videos: Read full transcript
   - For articles: Read complete content

2. **Create structured synthesis** with these sections:

   ### Materials Processed
   List each document with title, author, source, length

   ### Executive Summary
   2-3 paragraphs covering main arguments and findings

   ### Key Findings
   8-12 most important discoveries, claims, or arguments

   ### Methodological Notes
   Research approach, evidence quality, limitations

   ### Surprising or Counterintuitive Elements
   Anything that challenges conventional thinking

   ### Technical Details
   Important specifics that matter for evaluation

   ### Practical Implications
   What this means for practice or policy

   ### Questions for Further Investigation
   What's unclear, missing, or worth exploring

3. **Save output:**
   Write synthesis to: [OUTPUT_DIR]/pre-synthesis-[N]-[short-title].md

Return confirmation when synthesis is saved.
```

3. **Wait for all pre-synthesis agents to complete**

4. **Result:** Each source document now has a synthesis file that Research Agents will review instead of reading raw materials

**Why this matters:** Prevents crashes from Research Agents trying to read 6MB PDFs or 14MB system cards. Pre-synthesis agents handle the heavy lifting; Research Agents work with curated summaries.

### Step 3: Orchestration Planning

The Orchestrator (main Claude) decides:

1. **Research Agent allocation** - **Maximum 3 agents** to prevent crashes. Each reviews document syntheses from Phase 0, not raw materials.
2. **Domain Expert count** (1-4) - Based on:
   - Material count: 1-3 items → 1 expert, 4-8 items → 2 experts, 9+ items → 3-4 experts
   - Topic diversity: Single domain → 1 expert, multiple domains → 2-4 experts
   - Analysis benefit: Controversial/complex topics → more experts
3. **Domain Expert specializations** - What expertise areas are needed
4. **Contrarian Agent** - Always 1 (runs alongside Domain Experts)
5. **Presenter materials** - Which personal files to load

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
- Pre-Synthesis: [N] agents to create document syntheses
- Research Agents: 3 (reviewing document syntheses, not raw materials)
- Evaluator: Will filter and assess before experts see findings
- Domain Experts: 2 (AI Safety, Benchmark Methodology)
- Contrarian Agent: 1 (challenge consensus, surface overlooked pathways)
- Presenter: Will load profile, then synthesize final personalized output

Proceeding...
```

### Step 4: Set Up Tracking

Create TodoWrite entries:
- "Pre-synthesis: Create document syntheses"
- "Launch Presenter agent"
- One per Research Agent: "Research Agent N: [synthesis files]"
- "Launch Evaluator agent (quality gate)"
- "Launch Domain Experts + Contrarian: [specializations]"
- "Launch Presenter Synthesis"
- "Save outputs"

### Step 5: Load Calibration

Read calibration prompt once (used for all agents):

    Read .claude/skills/agents-spinning-up/references/calibration-prompt.md

### Step 6: Launch Presenter Agent (First, Runs Once)

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

### Step 7: Launch Research Agents (Parallel)

**Launch ALL Research Agents in a single message (parallel). Maximum 3 agents.**

**IMPORTANT:** Research Agents review document syntheses from Phase 0 (pre-synthesis), NOT raw PDFs/videos/transcripts.

For each Research Agent, allocate document syntheses and launch with:

```markdown
[CALIBRATION_PROMPT]

---

You are Research Agent [N]. You will review document syntheses and present findings.

**Your assigned syntheses:**
[LIST_OF_SYNTHESIS_FILES_TO_READ]

**Your task:**

1. **Read all assigned syntheses:**
   - Read each synthesis file completely
   - Extract key findings, arguments, evidence
   - Note methodological issues or limitations
   - **Actively hunt for surprising, counterintuitive, or unusual findings**
   - Note practical implications

3. **Prepare presentation:**
   Create a structured summary with these sections:

   ### Materials Processed
   List what you read/watched with titles, sources, lengths

   ### Key Findings
   Most important discoveries, arguments, or results (5-10 bullets)

   ### Methodological Assessment
   How solid is this research? What are the limitations?

   ### Surprising and Unusual Findings
   **This section is critical.** Flag anything that:
   - Contradicts conventional wisdom or common assumptions
   - Seems counterintuitive given what experts typically believe
   - Represents an underexplored pathway others are likely to overlook
   - Challenges the author's own stated framework or conclusions
   - Would change how an informed reader thinks about the topic

   For each surprise, explain WHY it's surprising (not just what it is) and what it implies if taken seriously.

   ### Anomalies and Underexplored Pathways
   What threads does this material introduce but not fully develop? What connections does it miss? What would you investigate next if you could?

   ### Practical Implications
   What should someone do differently after reading this?

   ### Critical Assessment
   Where are the weak points? What's missing?

   ### Questions for Experts
   What would benefit from domain expert or contrarian perspective?

4. **User context for personalization:**
   [PRESENTER_CONTEXT]

5. **Present to Evaluator:**
   Your findings will be reviewed by an Evaluator (quality gate) before reaching Domain Experts and a Contrarian Agent. Be thorough and honest about evidence quality so the Evaluator can make good filtering decisions.

Return your complete presentation.
```

### Step 8: Launch Evaluator Agent — Quality Gate (After Research Agents Complete)

The Evaluator runs BEFORE Domain Experts and Contrarian. It acts as a quality gate: filtering, assessing, and organizing findings so experts receive a curated briefing rather than raw output.

Launch single Evaluator agent:

```markdown
[CALIBRATION_PROMPT]

---

You are the Evaluator Agent. You are the quality gate between Research Agents and the expert discussion team. Your job is to filter, assess, and organize research findings so that Domain Experts and a Contrarian Agent receive a well-structured briefing.

**Recipient context (from Presenter):**
[PRESENTER_CONTEXT]

**Research findings to evaluate:**

[RESEARCH_AGENT_1_OUTPUT]
---
[RESEARCH_AGENT_2_OUTPUT]
---
[RESEARCH_AGENT_N_OUTPUT]

**Your task:**

1. **Quality assessment per finding:**
   - How rigorous is the methodology?
   - What are the evidence quality levels?
   - Are claims appropriately scoped?
   - Assign confidence levels: HIGH / MEDIUM / LOW / SPECULATIVE

2. **Methodological evaluation:**
   - Sampling issues
   - Baseline quality
   - Contamination risks
   - External validity
   - Replication concerns

3. **Cross-source synthesis** (if multiple Research Agents):
   - Where do sources agree/disagree?
   - Which sources are most reliable?
   - What compound effects exist?

4. **Red flags and limitations:**
   - What should the recipient be skeptical about?
   - What's overstated or under-supported?
   - What gaps exist?

5. **Briefing for Expert Team:**
   This is the most important output. Organize your assessment into:

   ### Findings Approved for Expert Review
   Well-supported findings that warrant expert discussion. Include:
   - The finding itself (summarized from Research Agents)
   - Your confidence level
   - Key evidence supporting it
   - What you want experts to focus on

   ### Findings Requiring Skepticism
   Findings that have methodological issues or weak evidence. Include:
   - The finding
   - Why you're skeptical
   - What would strengthen or weaken it

   ### Surprising Findings for Contrarian Review
   Flag the Research Agents' surprising/unusual findings specifically for the Contrarian Agent. Include:
   - Each surprise finding
   - Your assessment of whether the surprise is genuine or an artifact
   - What the Contrarian should push on

   ### Questions for Experts
   Research Agent questions plus your own. Organize by expertise area.

   ### Recipient Context
   Summarize what matters about the recipient (from Presenter context) so experts can tailor their analysis.

Return the complete briefing. This output goes directly to Domain Experts and the Contrarian Agent.
```

Wait for Evaluator to complete. Store output as `EVALUATOR_BRIEFING`.

### Step 9: Launch Domain Experts + Contrarian Agent (After Evaluator Complete)

**Launch ALL Domain Experts and the Contrarian Agent in a single message (parallel).**

They all receive the Evaluator's briefing as input, not raw Research Agent output.

For each Domain Expert:

```markdown
[CALIBRATION_PROMPT]

---

You are a Domain Expert in: [SPECIALIZATION]

**Evaluator's briefing (quality-filtered research findings):**
[EVALUATOR_BRIEFING]

**Your task:**

1. **Evaluate findings:**
   - Assess claims against your domain knowledge
   - Identify methodological strengths and weaknesses
   - Note what's well-supported vs. speculative
   - Flag contradictions or inconsistencies
   - Pay attention to the Evaluator's confidence levels but form your own view

2. **Add expertise:**
   - Provide context the Research Agents may have missed
   - Connect findings to broader literature or developments
   - Suggest alternative interpretations
   - Note what a domain expert would emphasize

3. **Answer questions:**
   The Evaluator has organized questions for your expertise area. Address them.

4. **Personal relevance:**
   The briefing includes recipient context. Given their profile, what expertise-level guidance would you provide?

Return your expert assessment.
```

**For the Contrarian Agent (always 1, launched in parallel with Domain Experts):**

```markdown
[CALIBRATION_PROMPT]

---

You are the Contrarian Agent. Your role is to challenge consensus, surface overlooked findings, and push the analysis toward less obvious but potentially important conclusions.

You are not contrarian for its own sake. You focus on where conventional reading is most likely to be WRONG or INCOMPLETE.

**Evaluator's briefing (quality-filtered research findings):**
[EVALUATOR_BRIEFING]

**Your task:**

1. **Challenge the strongest conclusions:**
   Take the findings the Evaluator marked as high-confidence and stress-test them. Steel-man the opposition. What would someone who disagrees say, and how strong is their case?

2. **Surface what others will overlook:**
   The Evaluator flagged surprising findings for your review. For each:
   - Is this genuinely surprising, or just framed that way?
   - If genuine, what are the implications that a conventional reading would miss?
   - What would change if this finding is the most important one in the entire analysis?

3. **Find the underexplored pathways:**
   - What connections between findings aren't obvious?
   - What threads does the research introduce but not follow?
   - What questions does nobody seem to be asking?
   - What would a truly independent thinker focus on?

4. **Propose alternative interpretations:**
   For the 2-3 most important findings, offer at least one alternative reading that's plausible but unlikely to appear in the Domain Expert assessments.

5. **Recipient-specific blind spots:**
   Given the recipient's profile (in the briefing), what would THEY specifically miss? What biases from their background might shape how they read these findings?

Return your contrarian assessment. Be specific and substantive. Every challenge should include what you'd need to see to change your mind.
```

Wait for all Domain Experts and Contrarian to complete.

### Step 10: Launch Presenter Synthesis (After Expert Discussion Complete)

The Presenter now does the final synthesis, drawing out what matters most for the recipient. This is a second launch of a Presenter-type agent with all upstream outputs.

```markdown
[CALIBRATION_PROMPT]

---

You are the Presenter Synthesis Agent. You have the recipient's full context and all upstream analysis. Your job is to synthesize everything into a final narrative that draws out what matters most for THIS specific person. Follow the `writing-style` skill to maintain authentic voice and avoid LLM patterns.

**Recipient context (from Phase 1):**
[PRESENTER_CONTEXT]

**Evaluator's briefing:**
[EVALUATOR_BRIEFING]

**Domain Expert assessments:**
[DOMAIN_EXPERT_1_OUTPUT]
---
[DOMAIN_EXPERT_N_OUTPUT]

**Contrarian assessment:**
[CONTRARIAN_OUTPUT]

**Your task:**

1. **Synthesize findings through the recipient's lens:**
   Not a neutral summary. Organize and emphasize based on what matters most for this person's work, interests, and goals. What should they pay attention to? What can they safely skim?

2. **Integrate expert perspectives:**
   Where experts agreed, state the consensus. Where they disagreed, explain the disagreement and which side matters more for the recipient. Where the Contrarian raised valid challenges, give those appropriate weight.

3. **Surface the surprises that matter:**
   From the Research Agents' surprise findings, the Evaluator's assessment, and the Contrarian's challenges: which surprises should the recipient actually sit with? Which ones change how they should think about something?

4. **Produce these sections:**

   ### Executive Summary
   3-4 sentences. Lead with what matters most for the recipient.

   ### Key Findings (Personalized)
   Ordered by relevance to the recipient, not by importance to the field. For each:
   - The finding
   - Why it matters for them specifically
   - Confidence level (from Evaluator)
   - Expert consensus or disagreement

   ### Surprises and Underexplored Pathways
   The findings that challenge conventional thinking or open new directions. Integrate Research Agent surprises, Contrarian challenges, and expert perspectives.

   ### Domain Expert Synthesis
   Integrated expert perspectives (not separated by expert). What did the experts collectively add?

   ### Contrarian Highlights
   The Contrarian's strongest challenges. What survived scrutiny?

   ### Methodological Assessment
   What to trust, what to question (from Evaluator, refined by experts).

   ### Personal Relevance
   Direct connections to the recipient's work, projects, and goals. Specific, actionable.

   ### Actionable Items
   What the recipient should do differently. Immediate, short-term, long-term.

   ### Implementation Steps for Neurodiverse Users
   **Critical:** Extract ALL tasks, exercises, or actions the materials explicitly or implicitly expect the reader to do. State them with complete clarity. For each step:

   **Format:**
   ```
   Step [N]: [Clear, concrete action]

   What to do: [Explicit instructions with no assumptions about what's "obvious"]

   Why this helps: [Direct explanation of the benefit - not subtle hints but clear motivation]

   Example: [If applicable, show what this looks like in practice]

   Time estimate: [How long this might take]

   Optional/Required: [Is this necessary or optional?]
   ```

   **Important notes for this section:**
   - Do NOT rely on the reader inferring what they should do. State it explicitly.
   - If materials say "consider X" or "one might think about Y," translate to "Do X by [concrete method]"
   - Pull out reflection questions, exercises, suggested readings, practice tasks
   - If the source material has subtle implications ("this suggests practitioners should..."), make them explicit ("You should do X because...")
   - Explain the value/purpose of each step, not just what to do
   - Order by: Required first, then highly recommended, then optional
   - Flag which steps have dependencies (e.g., "Do Step 3 after Step 1")

   ### Gaps and Open Questions
   What's not covered. What to investigate next.

Return the complete synthesis. This becomes the final report.
```

Wait for Presenter Synthesis to complete. Store output as `FINAL_SYNTHESIS`.

### Step 11: Save and Present

The Orchestrator uses the `FINAL_SYNTHESIS` from the Presenter Synthesis Agent (Step 9) as the primary input. The Orchestrator formats the report using the template from `references/synthesis-template.md`, populating it with the Presenter Synthesis output, and writes both the synthesis report and the audio-friendly transcript.

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
- **Folder link:** Provide clickable link to the project folder so user can easily navigate to all saved reports
- **Note:** Final synthesis includes "Implementation Steps for Neurodiverse Users" section with explicit, motivation-explained action items

## Scaling and Performance

| Material Count | Pre-Synthesis Agents | Research Agents | Domain Experts | Contrarian | Expected Time |
|----------------|---------------------|-----------------|----------------|------------|---------------|
| 1-2 items | 1-2 | 1 | 1 | 1 | 8-12 min |
| 3-5 items | 2-4 | 2 | 1-2 | 1 | 12-20 min |
| 6-10 items | 4-8 | 3 | 2-3 | 1 | 20-35 min |
| 11+ items | 8-12 | 3 | 3-4 | 1 | 35-60 min |

**Note:** Pre-synthesis phase adds time but prevents crashes and ensures stable processing. Research Agents are capped at 3 to avoid overload. Times include pre-synthesis (Phase 0), Evaluator gate (Phase 3), and Presenter Synthesis (Phase 5).

## Error Handling

| Error | Response |
|-------|----------|
| Material unavailable | Skip, note in gaps section |
| Research Agent timeout | Check partial output, relaunch if critical |
| All Research Agents fail | Abort, report failure |
| Evaluator failure | Pass raw Research Agent output to experts, note limitation |
| Domain Expert timeout | Continue with available experts |
| Contrarian failure | Continue without contrarian perspective, note in synthesis |
| Presenter (Phase 1) failure | Continue without personalization context |
| Presenter Synthesis failure | Orchestrator compiles final synthesis directly (fallback) |

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
- Evaluator gates quality before experts
- 2 Domain Experts (AI Benchmarking, Research Methodology)
- 1 Contrarian Agent (challenge benchmark validity assumptions)
- Presenter Synthesis personalizes for recipient

### Example 2: Large Video Collection

User: "Digest these 8 conference talks on mechanistic interpretability"

Orchestration:
- 8 Research Agents (1 per video, parallelized)
- Evaluator filters and organizes cross-talk findings
- 3 Domain Experts (Mechanistic Interpretability, ML Safety, Neuroscience)
- 1 Contrarian Agent (surface overlooked connections across talks)
- Presenter Synthesis draws out what matters for recipient

### Example 3: Documentation Deep Dive

User: "Synthesize the entire LangChain documentation and these 3 tutorial videos"

Orchestration:
- 2 Research Agents (1 for doc site with --combine, 1 for grouped videos)
- Evaluator assesses practical applicability
- 1 Domain Expert (LLM Application Architecture)
- 1 Contrarian Agent (challenge assumptions about tool choice)
- Presenter Synthesis personalizes for recipient's tech stack

## Migration from youtube-digesting-videos

This skill supersedes youtube-digesting-videos. For video-only workflows:
- Research Agents = previous per-video agents
- Presenter = previous personality agent
- Domain Experts + Evaluator = new capabilities
- All existing video workflows compatible

For transitioning existing skills, use research-synthesis as the primary multi-source workflow skill.

## Known Issues and Solutions

### Issue: System Crashes with Multiple Large PDFs

**Problem:** When processing collections with many large PDFs (e.g., 10 papers including 6MB and 14MB files), launching 5+ Research Agents that directly read PDFs causes system crashes or timeouts. Observed during BlueDot AI Governance course synthesis (Unit 1: 11 papers).

**Root cause:** Research Agents trying to read large binary files (6-14MB PDFs) in parallel overwhelms Claude Code's processing capacity.

**Solution implemented (Phase 0 Pre-Synthesis):**
1. **Pre-synthesis agents** read raw materials first (1 agent per large doc, or 1 per batch of small docs)
2. Each pre-synthesis agent creates a structured markdown synthesis (~5-15KB)
3. **Research Agents** (max 3) review the syntheses, not the raw PDFs
4. Prevents crashes while maintaining analysis depth

**Result:** Stable processing for 10+ document collections. Pre-synthesis adds 5-15 minutes but eliminates crashes.

**When to use:** Collections with >5 items or any collection containing PDFs >5MB.

**Trade-offs:**
- **+** Prevents system crashes
- **+** More reliable for large collections
- **+** Research Agents work with pre-digested content (potentially better cross-synthesis)
- **−** Adds time (pre-synthesis phase)
- **−** Two-stage processing may miss some nuances that direct reading would catch
