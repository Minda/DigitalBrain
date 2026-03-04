# Research Synthesis Skill

Multi-agent workflow for synthesizing research from any combination of content types (videos, articles, PDFs, papers, documentation sites). Orchestrates Research Agents, Domain Experts, an Evaluator, and a Presenter to produce comprehensive, validated synthesis reports.

## Quick Start

**Basic usage:**
```
"Research synthesis on AI benchmarks using this video [url], this paper [arxiv], and this article [url]"
```

**Or invoke directly:**
```
/research-synthesis [materials list]
```

## What It Does

1. **Processes any content type:** Videos, articles, PDFs, papers, documentation sites
2. **Intelligent workload allocation:** Heavy items get dedicated agents, light items grouped
3. **Domain expert validation:** 1-4 experts depending on scope and topic diversity
4. **Quality assessment:** Evaluator agent checks methodology and evidence quality
5. **Personal relevance:** Presenter agent loads your profile and contextualizes findings
6. **Comprehensive synthesis:** Integrates all perspectives into structured report

## Architecture

```
Orchestrator (main Claude)
  ├─> Presenter (loads your context once)
  ├─> Research Agents (1-8, process materials in parallel)
  ├─> Domain Experts (1-4, shared across all agents)
  └─> Evaluator (assesses quality)
      └─> Final Synthesis Report
```

**Key design principles:**
- Research Agents never communicate with each other (prevent groupthink)
- Presenter and Domain Experts shared across all Research Agents
- Parallel processing where possible
- Intelligent scaling based on workload

## Supported Content Types

| Type | Acquisition | Example |
|------|-------------|---------|
| YouTube videos | youtube-fetching-transcripts skill | https://youtube.com/watch?v=... |
| Web articles | download-url skill | https://blog.example.com/post |
| ArXiv papers | Bash curl download | https://arxiv.org/pdf/2503.14499 |
| Local PDFs | Direct read | /path/to/file.pdf |
| Local markdown | Direct read | /path/to/file.md |
| Documentation sites | download-url with --combine | https://docs.example.com (full site) |

## When to Use

Use this skill when:
- Processing multiple sources on a topic
- Mixing different content types (video + papers + articles)
- Preparing for presentations/talks
- Research requiring expert validation
- Need methodological assessment of sources
- Want personalized relevance analysis

## When NOT to Use

Don't use this skill when:
- Single short article (just read it)
- Quick fact-checking (use WebFetch)
- Only need transcripts (use youtube-fetching-transcripts)
- No synthesis needed (just downloading)

## Output Structure

The synthesis report includes:

1. **Executive Summary** - 3-4 sentence overview
2. **Materials Processed** - Inventory with quality ratings
3. **Key Findings** - 5-10 consolidated findings with evidence quality
4. **Domain Expert Analysis** - Expert perspectives on findings
5. **Methodological Assessment** - From Evaluator (strengths, weaknesses, red flags)
6. **Personal Relevance** - Customized to your work and interests
7. **Actionable Items** - Immediate, short-term, long-term actions
8. **Critical Assessment** - What to trust vs. question
9. **Gaps and Missing Perspectives** - What's not covered
10. **Appendices** - Full agent reports for reference

## Examples

### Example 1: Mixed Materials on AI Benchmarking

**Input:**
- 1 YouTube video (90 min critique)
- 1 ArXiv paper (45 pages)
- 1 summary PDF (8 pages)

**Orchestration:**
- 3 Research Agents (1 per item)
- 2 Domain Experts (AI Benchmark Methodology, Statistical Methods)
- Presenter loads AI research engineering profile
- Time: ~18 minutes

**Output:** Comprehensive synthesis with expert validation, methodological critique, and personalized relevance for preparing a talk.

See `references/example-workflow.md` for complete walkthrough.

### Example 2: Large Video Collection

**Input:**
- 8 conference talks on mechanistic interpretability (30-60 min each)

**Orchestration:**
- 8 Research Agents (1 per video, parallel)
- 3 Domain Experts (Mechanistic Interpretability, ML Safety, Neuroscience)
- Presenter loads interpretability research background
- Time: ~30 minutes

**Output:** Cross-video synthesis with expert perspectives and quality assessment.

### Example 3: Documentation Deep Dive

**Input:**
- Entire LangChain documentation site
- 3 tutorial videos
- 2 comparison articles

**Orchestration:**
- 3 Research Agents (1 for docs with --combine, 1 for videos grouped, 1 for articles)
- 2 Domain Experts (LLM Application Architecture, Software Engineering)
- Presenter loads software engineering profile
- Time: ~20 minutes

**Output:** Practical synthesis for adopting new technology.

## Scaling

| Materials | Agents | Experts | Time |
|-----------|--------|---------|------|
| 1-2 items | 1-2 | 1 | 5-10 min |
| 3-5 items | 2-3 | 1-2 | 10-20 min |
| 6-10 items | 3-5 | 2-3 | 20-35 min |
| 11+ items | 5-8 | 3-4 | 35-60 min |

## Migration from youtube-digesting-videos

This skill **supersedes** youtube-digesting-videos for most use cases.

**What changed:**
- Research Agents = previous per-video agents (but now content-agnostic)
- Presenter = previous personality agent (same pattern)
- Domain Experts = NEW (1-4 experts validate findings)
- Evaluator = NEW (methodological quality assessment)
- Content types = EXPANDED (was video-only, now any type)

**Backward compatibility:**
- All video-only workflows still work
- Same personalization approach (loads job-profile, insights, etc.)
- Can still use for single videos (though may be overkill)

**When to use old skill:**
- Legacy workflows that specifically reference youtube-digesting-videos
- If you want simpler output (no expert validation)
- Very quick video digests without synthesis

**Recommended transition:**
- Use research-synthesis as default for multi-source work
- Keep youtube-digesting-videos for video-only quick digests
- Eventually deprecate youtube-digesting-videos once research-synthesis proven stable

## File Structure

```
.claude/skills/research-synthesis/
├── SKILL.md                          # Main skill instructions
├── README.md                         # This file
└── references/
    ├── synthesis-template.md         # Output report template
    ├── orchestration-guide.md        # Decision matrices for planning
    └── example-workflow.md           # Complete example walkthrough
```

## Related Skills

**Used by this skill:**
- **youtube-fetching-transcripts** - Video transcript acquisition
- **download-url** - Article and documentation downloading
- **agents-spinning-up** - Agent calibration protocol
- **agent-customizing-content** - Presenter pattern (personal context)

**Replaced by this skill:**
- **youtube-digesting-videos** - Video-only predecessor (see migration guide above)

**Similar patterns:**
- **course-learning-panels** - Multi-agent expert panel discussions (could be retrofitted to use this)

## Advanced Usage

### Custom Expert Specializations

The orchestrator can specify any expert domain:
- AI Safety / Alignment
- Benchmark Design / Evaluation
- Mechanistic Interpretability
- ML Engineering / Systems
- AI Policy / Governance
- Neuroscience
- Statistics / Research Methods
- Software Architecture
- [Any domain relevant to materials]

### Workload Grouping Strategies

**Conservative (more agents, finer granularity):**
- Better for diverse materials
- Each agent has focused context
- Longer parallel processing time

**Aggressive (fewer agents, more grouping):**
- Better for similar materials
- Faster if agents can handle load
- Risk of context overload

**Recommended:** Start conservative, adjust based on results.

### Quality Thresholds

The Evaluator ranks sources by reliability. In your synthesis:
- **High confidence findings:** Multiple high-quality sources agree
- **Medium confidence:** Single high-quality source or multiple medium sources
- **Low confidence:** Only low-quality sources or significant conflicts

## Troubleshooting

### All Research Agents Failing

**Causes:**
- Invalid URLs or file paths
- Transcripts unavailable
- Network issues

**Solutions:**
- Verify all materials are accessible before launching
- Check URL format
- Try manual download first

### Expert Analysis Too Generic

**Causes:**
- Expert specialization too broad
- Materials don't match expert domain
- Not enough material to analyze

**Solutions:**
- Narrow expert specialization
- Ensure expert domains match materials
- For single-domain topics, use 1 expert but go deeper

### Synthesis Too Long/Verbose

**Causes:**
- Too many Research Agents with full outputs in appendix
- All expert analyses included verbatim

**Solutions:**
- Summarize agent outputs in appendices
- Consolidate expert perspectives by topic, not by agent
- Focus on key findings in main sections

## Contributing

To improve this skill:

1. **Add new content type support:**
   - Update Step 6a with acquisition instructions
   - Add to "Supported Content Types" table
   - Test with example materials

2. **Refine orchestration logic:**
   - Update `references/orchestration-guide.md`
   - Add decision matrices or heuristics
   - Document rationale

3. **Improve templates:**
   - Update `references/synthesis-template.md`
   - Keep structure, improve clarity
   - Add sections if generally useful

4. **Add examples:**
   - Create new example workflow in `references/`
   - Show different material types or scales
   - Document what made it effective

## License

Part of the Exobrain project. See main repository for license.
