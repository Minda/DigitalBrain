# Orchestration Decision Guide

Reference for the Orchestrator when planning multi-agent workflow.

## Research Agent Allocation

### Workload Classification

**Heavy (dedicated agent):**
- Videos longer than 60 minutes
- PDFs over 50 pages
- Entire documentation sites
- Complex academic papers requiring deep analysis

**Medium (may group 2-3):**
- Videos 20-60 minutes
- Articles with substantial content (>3000 words)
- Papers 10-50 pages
- Multi-page documentation sections

**Light (may group 3-5):**
- Videos under 20 minutes
- Short articles (<3000 words)
- Blog posts
- Single-page documents

### Allocation Strategy

| Total Items | Strategy |
|-------------|----------|
| 1-2 items | 1 agent per item (regardless of size) |
| 3-5 items | Heavy items solo, group light items |
| 6-10 items | Heavy solo, medium in pairs, light in groups of 3-5 |
| 11+ items | Max 8 agents - batch aggressively |

**Golden rule:** Never assign more than 8 Research Agents. Group materials strategically beyond that.

## Domain Expert Count Decision

### Factor 1: Material Count

| Materials | Base Expert Count |
|-----------|-------------------|
| 1-3 | 1 expert |
| 4-8 | 2 experts |
| 9-15 | 3 experts |
| 16+ | 4 experts |

### Factor 2: Topic Diversity

**Single domain** (e.g., all AI safety papers):
- Use base count
- Experts can have different perspectives within domain

**Multiple related domains** (e.g., AI safety + policy):
- Use base count + 1
- Each expert covers related domains

**Diverse domains** (e.g., AI + biology + economics):
- Use base count + 1 or +2
- Ensure coverage across major domains

### Factor 3: Controversy/Complexity

**Increase expert count if:**
- Materials present conflicting claims
- Topic is methodologically complex
- User's work requires deep analysis
- Multiple valid interpretations exist

**Examples:**
- Benchmark methodology critique → +1 expert (Methodology)
- AI capabilities forecasting → +1 expert (multiple perspectives valuable)
- Standard literature review → No increase

### Final Expert Count Formula

```
Base (from material count)
+ Topic diversity adjustment (0-2)
+ Complexity adjustment (0-1)
= Final count (capped at 4)
```

## Domain Expert Specialization Selection

### For AI/ML Topics

**Common specializations:**
- AI Safety / Alignment
- Machine Learning Methodology
- Benchmark Design / Evaluation
- Mechanistic Interpretability
- AI Policy / Governance
- ML Engineering / Systems
- Neuroscience (for alignment work)

**Selection strategy:**
- Match to material topics
- Cover methodological vs. application perspectives
- Include one "methodology" expert for research critique

### For Interdisciplinary Topics

**Strategy:**
- One expert per major domain represented
- One expert in the intersection area (if it exists)
- Consider user's background (from Presenter context)

**Example:** Materials on AI + neuroscience + cognitive science
- Expert 1: AI/ML Systems
- Expert 2: Computational Neuroscience
- Expert 3: Cognitive Science / Psychology

## Presenter Material Selection

**Always load:**
- config/user.md (name, identity)
- config/job-profile.md (professional focus)

**Load when available:**
- personal/memories/insights/* (all files - cross-cutting principles)
- personal/.claude/relational-context.md (working relationship)

**Optionally load (if topic-specific research exists):**
- personal/memories/research/[relevant-topic].md

**Selection strategy:**
- Load broad context by default
- For focused research (e.g., user has extensive AI safety research), load specific research memories
- Keep Presenter context comprehensive but relevant

## Example Orchestration Plans

### Example 1: Single Domain, Medium Scale

**Input:**
- 5 YouTube videos on mechanistic interpretability (30-60 min each)
- 2 blog posts on the topic
- 1 research paper (30 pages)

**Plan:**
- **Research Agents:** 6 (5 videos solo, 2 blog posts grouped)
- **Domain Experts:** 2
  - Expert 1: Mechanistic Interpretability
  - Expert 2: ML Research Methodology
- **Reasoning:** Single domain, medium scale, benefits from methodology perspective

### Example 2: Diverse Topics, Large Scale

**Input:**
- 3 videos on AI benchmarking
- 2 papers on benchmark methodology
- 4 articles on AI capabilities
- 1 paper on AI policy implications

**Plan:**
- **Research Agents:** 6
  - Agent 1: Videos 1-2 (grouped)
  - Agent 2: Video 3
  - Agent 3: Papers 1-2 (both methodology)
  - Agent 4: Articles 1-3 (grouped capabilities)
  - Agent 5: Article 4
  - Agent 6: Policy paper
- **Domain Experts:** 3
  - Expert 1: AI Benchmark Methodology
  - Expert 2: AI Capabilities Assessment
  - Expert 3: AI Policy / Governance
- **Reasoning:** Diverse topics (benchmarking + capabilities + policy), large scale, need coverage

### Example 3: Controversial/Complex Topic

**Input:**
- 1 video critiquing a benchmark paper
- 1 ArXiv paper being critiqued
- 2 response articles
- 1 alternative benchmark paper

**Plan:**
- **Research Agents:** 5 (1 per item - all important context)
- **Domain Experts:** 3
  - Expert 1: Benchmark Methodology
  - Expert 2: Statistical Methods / Social Science
  - Expert 3: AI Capabilities Forecasting
- **Reasoning:** Controversial (critique vs. defense), methodologically complex, multiple valid perspectives, benefits from diverse expertise

### Example 4: Focused Deep Dive

**Input:**
- Entire LangChain documentation site
- 6 tutorial videos
- 3 comparison articles (LangChain vs. alternatives)

**Plan:**
- **Research Agents:** 3
  - Agent 1: Full documentation site (download with --combine)
  - Agent 2: Videos 1-6 (grouped, all tutorials)
  - Agent 3: Comparison articles
- **Domain Experts:** 2
  - Expert 1: LLM Application Architecture
  - Expert 2: Software Engineering / API Design
- **Reasoning:** Single tool focus, practical orientation, need architecture + engineering perspectives

## Timing Estimates

### Per-Agent Processing Time

**Research Agent:**
- Light workload: 2-4 minutes
- Medium workload: 4-8 minutes
- Heavy workload: 8-15 minutes

**Presenter (Phase 1):** 2-3 minutes (loads once)

**Evaluator (Phase 3):** 4-6 minutes (quality gate, processes all Research Agent outputs)

**Domain Expert (Phase 4):** 3-5 minutes per expert (process Evaluator briefing)

**Contrarian Agent (Phase 4):** 3-5 minutes (runs in parallel with Domain Experts)

**Presenter Synthesis (Phase 5):** 4-6 minutes (synthesizes all upstream outputs)

**Orchestrator formatting:** 2-3 minutes (writes files from Presenter Synthesis output)

### Total Workflow Time

**Formula:**
```
Presenter time (Phase 1)
+ Max(Research Agent times) [parallel] (Phase 2)
+ Evaluator time (Phase 3, sequential)
+ Max(Domain Expert times, Contrarian time) [parallel] (Phase 4)
+ Presenter Synthesis time (Phase 5, sequential)
+ Orchestrator formatting time
```

**Examples:**
- 3 items, 2 experts: ~20-25 minutes
- 8 items, 3 experts: ~30-40 minutes
- 15 items, 4 experts: ~45-65 minutes

## Error Recovery Strategies

### Research Agent Failure

**If 1 agent fails (out of 3+):**
- Continue with remaining agents
- Note gap in synthesis
- Don't relaunch

**If 2+ agents fail:**
- Assess if remaining agents provide sufficient coverage
- Consider selective relaunch for critical materials
- May need to abort if too many failures

**If all agents fail:**
- Abort workflow
- Report failure to user
- Suggest manual processing

### Domain Expert Failure

**If 1 expert fails (out of 2+):**
- Continue with remaining experts
- Note limited expert coverage in synthesis

**If all experts fail:**
- Continue without expert analysis
- Note limitation in synthesis
- Evaluator still provides quality assessment

### Presenter Failure

**If Presenter fails:**
- Continue without personalization
- Use generic professional lens
- Note that personal relevance section is limited

### Contrarian Failure

**If Contrarian fails:**
- Continue without contrarian perspective
- Note limitation in synthesis
- Domain Expert analysis still provides quality assessment

### Evaluator Failure

**If Evaluator fails:**
- Pass raw Research Agent output to Domain Experts and Contrarian
- Note that expert discussion was not quality-gated
- Rely on Domain Expert analysis for evaluation

### Presenter Synthesis Failure

**If Presenter Synthesis fails:**
- Orchestrator compiles final synthesis directly (fallback to previous workflow)
- Use Evaluator + Domain Expert + Contrarian outputs directly
- Note that personalization may be limited

## Quality Checks

Before launching agents, verify:

- [ ] All materials are accessible (URLs valid, files exist)
- [ ] Workload allocation is balanced (no single agent with 10 items)
- [ ] Domain expert specializations match material topics
- [ ] Expert count follows decision matrix (1-4, appropriate to scale)
- [ ] Contrarian Agent included in orchestration plan
- [ ] Calibration prompt loaded
- [ ] Presenter will load user context
- [ ] Pipeline phases are sequential where required (Evaluator before Experts)

During execution, monitor:

- [ ] Research Agents completing successfully
- [ ] Research Agent outputs include Surprising Findings and Anomalies sections
- [ ] Evaluator produces structured Briefing for Expert Team
- [ ] Domain Expert analyses address the Evaluator briefing
- [ ] Contrarian Agent provides substantive challenges (not just agreement)
- [ ] Presenter Synthesis personalizes for recipient

Before final output, confirm:

- [ ] At least 50% of Research Agents completed successfully
- [ ] Evaluator completed (critical for quality gate)
- [ ] At least 1 Domain Expert completed
- [ ] Contrarian Agent completed (or noted as missing)
- [ ] Presenter Synthesis completed (or Orchestrator fallback used)
- [ ] Sufficient material to create meaningful synthesis
