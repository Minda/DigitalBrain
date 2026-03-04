# Example Workflow: AI Benchmarking Research

This is a complete example of the research-synthesis skill processing mixed materials about AI benchmarking methodology.

## User Request

"I'm preparing for a talk on AI benchmark reliability. Can you synthesize this video [Nathan's METR critique], this ArXiv paper [METR paper], and this Emergent Mind summary PDF? I need to understand the key findings and methodological issues."

## Step 1: Parse and Inventory

**Parsed materials:**
1. YouTube video: https://www.youtube.com/watch?v=L2fvOFgrGRI (Nathan's critique, ~90 min)
2. ArXiv paper: https://arxiv.org/pdf/2503.14499 (METR time horizon paper, 45 pages)
3. Local PDF: /Users/min/Downloads/Measuring AI 50%-Task Completion.pdf (summary, 8 pages)

**Inventory presented to user:**

| # | Type | Source | Est. Workload |
|---|------|--------|---------------|
| 1 | Video | Nathan METR Critique (90min) | Heavy |
| 2 | PDF | ArXiv METR Paper (45 pages) | Heavy |
| 3 | PDF | Emergent Mind Summary (8 pages) | Light |

User confirms: "Yes, proceed"

## Step 2: Orchestration Planning

**Decision process:**

**Research Agent allocation:**
- Item 1 (video, 90 min) → Heavy → Dedicated agent
- Item 2 (paper, 45 pages) → Heavy → Dedicated agent
- Item 3 (summary, 8 pages) → Light → Could group, but only 3 items total, so dedicated agent

**Result:** 3 Research Agents (1 per item)

**Domain Expert count:**
- Material count: 3 items → Base 1 expert
- Topic diversity: Single domain (AI benchmarking) → No adjustment
- Complexity: Methodologically complex + critique vs. defense → +1 expert

**Result:** 2 Domain Experts

**Expert specializations:**
- Expert 1: AI Benchmark Methodology (covers benchmarking practices, evaluation design)
- Expert 2: Statistical Methodology / Research Methods (covers baseline issues, sampling, validity)

**Presenter materials:**
- config/user.md
- config/job-profile.md (user is transitioning to AI research engineering)
- personal/memories/insights/* (check for AI safety, evaluation insights)
- personal/.claude/relational-context.md

**Plan presented to user:**

```
Orchestration Plan:
- Research Agents: 3
  - Agent 1: Nathan's critique video (90 min)
  - Agent 2: METR ArXiv paper (45 pages)
  - Agent 3: Emergent Mind summary (8 pages)
- Domain Experts: 2
  - Expert 1: AI Benchmark Methodology
  - Expert 2: Statistical Methodology / Research Methods
- Presenter: Will load job profile, insights, relational context
- Evaluator: Will assess quality and methodological rigor

Estimated time: 15-20 minutes

Proceeding...
```

## Step 3: Set Up Tracking

TodoWrite entries created:
- [x] Launch Presenter agent
- [ ] Research Agent 1: Nathan's critique video
- [ ] Research Agent 2: METR ArXiv paper
- [ ] Research Agent 3: Emergent Mind summary
- [ ] Launch Domain Experts (2)
- [ ] Launch Evaluator
- [ ] Compile final synthesis

## Step 4: Load Calibration

Read: `.claude/skills/agents-spinning-up/references/calibration-prompt.md`

Calibration prompt loaded into memory for injection into all agents.

## Step 5: Launch Presenter Agent

**Agent prompt:**

```markdown
[CALIBRATION_PROMPT]

---

You are the Presenter Agent. Your role is to load the user's personal context and provide personalized relevance assessments for research findings.

## Your Task

1. Load user context:
   - config/user.md
   - config/job-profile.md
   - personal/memories/insights/*
   - personal/.claude/relational-context.md

2. Create a structured profile summarizing:
   - Professional focus areas
   - Current research interests
   - Target roles and skills
   - Existing insights and frameworks

3. This profile will be shared with Research Agents, Domain Experts, and the Evaluator.

Return the structured profile in your final output.
```

**Presenter output (abbreviated):**

```markdown
# User Context Profile

**Name:** Min (they/them)

**Professional Focus:**
- Transitioning from frontier AI engineering to AI Research Engineer roles
- Focus on AI safety, observability, and evaluation methodology
- Technical interests: mechanistic interpretability, benchmark design, model capabilities assessment

**Target Roles:**
- AI Research Engineer (safety-focused organizations)
- Roles combining engineering rigor with research methodology
- Preference for organizations doing safety/alignment work

**Current Research Interests:**
- Evaluation methodology and benchmark reliability
- Contamination vs. capability distinction in AI evals
- Observability and interpretability for deployment safety

**Existing Insights:**
- Frameworks-core: "Contradiction as input, not noise to be eliminated"
- RC/IE synthesis: Relational-constitutional and internal-experiential integration
- Experimental rigor: Identified gap in AI research methodology

**Working Style:**
- Values technical precision over validation
- Prefers directional trends over absolute claims
- Interested in methodological critique and research quality
```

Mark Presenter task complete. Store as `PRESENTER_CONTEXT`.

## Step 6: Launch Research Agents (Parallel)

**Launched in single message with 3 Task tool calls:**

### Research Agent 1 Prompt

```markdown
[CALIBRATION_PROMPT]

---

You are Research Agent 1. You will process the following materials and present findings:

**Your materials:**
- YouTube video: Nathan's METR critique (https://www.youtube.com/watch?v=L2fvOFgrGRI)

**Your task:**

1. **Acquire materials:**
   Use the youtube-fetching-transcripts skill to fetch the transcript.
   Read the full markdown transcript file.

2. **Read and analyze:**
   [... standard Research Agent instructions ...]

3. **User context for personalization:**
   [PRESENTER_CONTEXT]

4. **Present to experts:**
   You will present to:
   - Domain Expert 1: AI Benchmark Methodology
   - Domain Expert 2: Statistical Methodology / Research Methods
   - Evaluator Agent

Return your complete presentation.
```

### Research Agent 2 Prompt

```markdown
[CALIBRATION_PROMPT]

---

You are Research Agent 2. You will process the following materials and present findings:

**Your materials:**
- ArXiv paper: METR Time Horizon Paper (https://arxiv.org/pdf/2503.14499)

**Your task:**

1. **Acquire materials:**
   Use Bash to download from ArXiv:
     curl -o metr-paper.pdf "https://arxiv.org/pdf/2503.14499.pdf"
   Read the PDF.

2. **Read and analyze:**
   [... standard Research Agent instructions ...]

[Continue same structure as Agent 1]
```

### Research Agent 3 Prompt

```markdown
[CALIBRATION_PROMPT]

---

You are Research Agent 3. You will process the following materials and present findings:

**Your materials:**
- Local PDF: Emergent Mind Summary (/Users/min/Downloads/Measuring AI 50%-Task Completion.pdf)

**Your task:**

1. **Acquire materials:**
   Read the file at: /Users/min/Downloads/Measuring AI 50%-Task Completion.pdf

2. **Read and analyze:**
   [... standard Research Agent instructions ...]

[Continue same structure]
```

**All 3 agents launched in parallel.**

Update TodoWrite as each completes:
- [x] Research Agent 1: Nathan's critique video (completed in 8 min)
- [x] Research Agent 2: METR ArXiv paper (completed in 12 min)
- [x] Research Agent 3: Emergent Mind summary (completed in 4 min)

**Agent outputs collected** (abbreviated for example):

**Research Agent 1 output highlights:**
- Key methodological critiques: baseline inflation (5-18x), contamination (2/3 public), convenience sampling
- Surprising: Only 3 baselines per task average
- Questions for experts: How significant is 5-18x baseline inflation? Can you quantify contamination effect?

**Research Agent 2 output highlights:**
- Key findings: 50-60 min time horizon for frontier models, 212-day doubling time
- Methodological notes: Paper acknowledges external validity concerns, messiness factors
- Questions for experts: How reliable are logistic regression time estimates? What's best practice for human baselines?

**Research Agent 3 output highlights:**
- Summary focuses on infographic and simplified explanations
- Less methodological depth than full paper
- Questions for experts: Is the simplified presentation misleading?

## Step 7: Launch Domain Experts (Parallel)

**Launched in single message with 2 Task tool calls:**

### Domain Expert 1 Prompt

```markdown
[CALIBRATION_PROMPT]

---

You are a Domain Expert in: AI Benchmark Methodology

**User context:**
[PRESENTER_CONTEXT]

**Research findings to evaluate:**

[RESEARCH_AGENT_1_OUTPUT]
---
[RESEARCH_AGENT_2_OUTPUT]
---
[RESEARCH_AGENT_3_OUTPUT]

**Your task:**
[... standard Domain Expert instructions ...]

Return your expert assessment organized by Research Agent.
```

### Domain Expert 2 Prompt

```markdown
[CALIBRATION_PROMPT]

---

You are a Domain Expert in: Statistical Methodology / Research Methods

[Continue same structure as Expert 1]
```

**Both experts launched in parallel.**

Update TodoWrite:
- [x] Launch Domain Experts (2) (both completed in 5 min)

**Expert outputs collected** (abbreviated):

**Expert 1 (Benchmark Methodology) highlights:**
- Nathan's critique is methodologically sound on core points
- Baseline inflation is a known issue in human-AI comparison benchmarks
- Best practice: 10+ baselines per task, matched expertise, per-task payment
- METR's messiness factors are good practice for external validity
- Contamination is serious - industry standard moving toward private test sets

**Expert 2 (Statistical Methodology) highlights:**
- Convenience sampling with n=3 is inadequate for reliable estimates
- Hourly payment creates perverse incentives (economics literature on this)
- Logistic regression for time estimates is reasonable but should report confidence intervals
- Compounding effects: baseline inflation × contamination × task realism is unpredictable
- Need sensitivity analysis to quantify effects

## Step 8: Launch Evaluator Agent

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
[RESEARCH_AGENT_3_OUTPUT]

**Your task:**
[... standard Evaluator instructions ...]

Return structured evaluation organized by Research Agent, plus cross-source assessment.
```

Update TodoWrite:
- [x] Launch Evaluator (completed in 5 min)

**Evaluator output** (abbreviated):

**Quality assessment:**
- Nathan's video: Medium-high quality critique, some hyperbole but core points solid
- METR paper: High quality research with appropriate caveats, transparent about limitations
- Emergent Mind summary: Low-medium, oversimplifies, loses methodological nuance

**Cross-source synthesis:**
- Agreement: METR paper acknowledges many issues Nathan raises (external validity, messiness)
- Disagreement: Nathan stronger on "nearly meaningless" than evidence supports
- Most reliable: METR paper itself (transparent), then Nathan's critique (substantive), then summary (incomplete)

**Red flags:**
- Extrapolating from the exponential trend without accounting for methodological limitations
- Using absolute time horizon numbers for deployment decisions
- The 14.5-hour estimate (not empirical)

## Step 9: Compile Final Synthesis

Using `references/synthesis-template.md`, orchestrator compiles:

**Key sections:**

**Executive Summary:**
"The METR time horizon paper introduces a useful metric showing frontier AI models at ~50-60 minute time horizons with exponential growth. However, significant methodological limitations (baseline inflation 5-18x, contamination showing 3.3x public/private gap, task realism filters showing 2-3x performance drop) mean absolute values and growth rates should be treated with skepticism. Directional trend is likely real, but quantitative forecasting or deployment decisions should heavily discount these numbers and use more realistic benchmarks (SWE-bench Pro Private: 24% vs. 80% on public)."

**Key Findings:** (5 consolidated findings from all 3 research agents)

**Domain Expert Analysis:** (integrated perspectives from both experts)

**Methodological Assessment:** (Evaluator's cross-source analysis and quality rankings)

**Personal Relevance:** (HIGH - directly relevant to user's AI research engineering transition, evaluation methodology focus, and existing insights on contradiction-as-signal)

**Actionable Items:**
- Bookmark Nathan's critique as capability assessment methodology case study
- Familiarize with alternative benchmarks (Remote Labor Index, SWE-bench Pro Private)
- When reviewing AI capabilities claims, check: contamination risks, baseline methodology, task realism
- Use "contamination vs. capability" distinction in observability work discussions

**Critical Assessment:**
- What to trust: Directional trend, external validity concerns, context-dependence of capabilities
- What to question: Absolute time horizon values, 7-month doubling time, 14.5-hour estimate
- Directional vs. quantitative: Trend likely real, but slope and values probably inflated

**Gaps:**
- No discussion of good benchmark methodology alternatives (constructive)
- Missing technical details on how alternative benchmarks work
- No exploration of whether issues apply to non-coding benchmarks

## Step 10: Save and Present

**Saved to:** `personal/research/2026-03-02_ai-benchmarking-synthesis.md`

**Brief summary to user:**

```
Research synthesis complete!

**Materials processed:** 3 (1 video, 2 PDFs)
**Quality:** 1 high, 1 medium-high, 1 low-medium

**Top 3 findings:**
1. METR time horizon metric shows frontier models at ~50-60 min, doubling every 7 months - but methodological issues likely inflate both scale and slope
2. Baseline inflation (5-18x), contamination (3.3x public/private gap), and task realism (2-3x performance drop) compound unpredictably
3. Better benchmarks exist showing more modest results: SWE-bench Pro Private at 24% vs. 80% on public repos

**Key actionable items:**
- Use contamination vs. capability distinction in your AI observability work discussions
- Reference this as a case study for rigorous evaluation methodology in interviews
- Heavily discount absolute numbers; use directional trends only

**Quality assessment:** Directional trend likely real, but be very skeptical of quantitative claims. Use alternative benchmarks for deployment decisions.

**Full report saved to:** personal/research/2026-03-02_ai-benchmarking-synthesis.md
```

## Workflow Metrics

**Total time:** 18 minutes
- Presenter: 3 min
- Research Agents (parallel): 12 min (max of 8, 12, 4)
- Domain Experts (parallel): 5 min
- Evaluator: 5 min
- Orchestrator synthesis: 3 min

**Agents launched:** 7 total
- 1 Presenter
- 3 Research Agents
- 2 Domain Experts
- 1 Evaluator

**Materials processed:** 3 (100% success rate)

**Output quality:** High - comprehensive synthesis with expert validation, methodological critique, and personalized relevance

## What Made This Effective

1. **Appropriate expert allocation:** 2 experts covered the methodological complexity well
2. **Parallel processing:** All Research Agents ran simultaneously (12 min total vs. 24 min sequential)
3. **No communication between Research Agents:** Prevented groupthink, each processed independently
4. **Shared experts across agents:** Domain experts and Evaluator saw all materials, could identify patterns and contradictions
5. **Presenter loaded once:** Personal context shared with all agents without redundant loading
6. **Quality checks:** Evaluator ranked source reliability, identified red flags independently

## Comparison to Previous Approach

**Old (youtube-digesting-videos only):**
- Could only handle video
- No expert validation
- No methodological assessment
- Personal relevance only

**New (research-synthesis):**
- Handles mixed content types (video + PDFs)
- Domain expert validation (2 experts)
- Evaluator provides methodological rigor assessment
- Personal relevance + expert analysis + quality evaluation
- Cross-source synthesis
- More comprehensive and reliable output
