---
name: agent-customizing-content
description: Personalize any content for the user by loading their professional context, interests, and insights. Produces structured relevance assessments. Use when user says "customize this for me", "what's relevant here", "personal relevance", or when another skill needs a personalization layer.
allowed-tools: [Read, Glob, Grep]
---

# Agent Customizing Content

Reusable pattern that loads personal context and produces structured relevance assessments for any content. Not tied to any specific content type. Works with video summaries, articles, research papers, course notes, or any body of text.

## Quick Start

1. Load calibration via agents-spinning-up
2. Load user context (see context loading sequence below)
3. Take the input content
4. Produce a structured relevance assessment (see output format)

## When to Use

- After content has been summarized or processed by another skill or agent
- When the user wants to know "what matters to me here"
- As the personalization step in any multi-agent workflow
- When other skills need a personality/relevance layer

## When Not to Use

- Raw content that hasn't been processed yet (summarize first)
- When the user explicitly wants an objective, impersonal analysis
- For content the user authored themselves

## Instructions

### Step 1: Load Calibration

Read the calibration prompt from agents-spinning-up:

    Read .claude/skills/agents-spinning-up/references/calibration-prompt.md

Include this in the agent's instructions if running as a subagent.

### Step 2: Load User Context

Load these files in order. If a file is missing, continue with what's available.

1. **User identity:** `config/user.md`
   Learn the user's name and personal paths.

2. **Professional profile:** `config/job-profile.md`
   Technical interests, role targets, research balance, company preferences.
   This is the primary lens for professional relevance.

3. **Cross-cutting insights:** `personal/memories/insights/*`
   List the directory, then read each file. These are principles the user
   has discovered that apply broadly. Check for connections to the input content.

4. **Working relationship:** `personal/.claude/relational-context.md`
   (fallback: `.claude/relational-context.md`)
   Understand how the user works and what kind of analysis they value.

### Step 3: Analyze Content

With all context loaded, review the input content through the user's lens:

- **Professional relevance**: How does this connect to their target roles, technical interests, and current learning trajectory?
- **Research connections**: Does this relate to their active research areas or technical focus?
- **Insight connections**: Does this reinforce, challenge, or extend any of their existing cross-cutting insights?
- **Actionable items**: What should the user do with this? Read deeper? Save to memories? Apply to a project? Write about it?
- **Gaps and missing perspectives**: What does this content NOT cover that the user would care about?

### Step 4: Produce Output

Follow this structure for the relevance assessment:

#### Per-Item Assessment (for each piece of content)

```
**Relevance: [HIGH / MEDIUM / LOW]**

**Why this matters for you:**
[2-3 sentences, specific connections to profile/interests]

**What to pay attention to:**
1. [Most important specific finding or insight, with explicit connection]
2. [Second most important]

**Connections to your existing thinking:**
- [Reference specific insight file if applicable]
- [How this reinforces/challenges/extends existing understanding]

**Worth your time?** [Direct recommendation: yes/no/selectively, with reasoning]
```

#### Cross-Content Assessment (when multiple items)

```
**Cross-Content Themes:**
1. [Theme name]: Which items share this, why it matters for the user
2. [Continue as needed]

**Top 3 Actionable Items:**
1. [Specific action across all content]
2. [Next action]
3. [Next action]

**What's Missing:**
- [Gaps across all content the user would care about]
- [Perspectives absent that matter given their background]
```

## Context Loading: Why This Order

1. **Name first**: so the assessment addresses the user personally
2. **Job profile second**: the strongest filter for professional relevance
3. **Insights third**: connections to existing understanding
4. **Relational context last**: shapes tone and depth, not content filtering

## Adapting to Different Content Types

| Content Type | Emphasis |
|-------------|----------|
| Video summaries | Actionable takeaways, speaker credibility |
| Research papers | Methodology relevance, applicability to user's work |
| Articles/blog posts | Ideas worth carrying forward, connections to interests |
| Course materials | Learning trajectory, knowledge gaps filled |
| Code/technical docs | Tools/patterns to adopt, architecture insights |

## Guidelines

| Always | Never |
|--------|-------|
| Load all four context sources | Skip the job profile (it's the main lens) |
| State when content has low relevance | Force connections that aren't there |
| Note genuine gaps and missing perspectives | Praise everything as relevant |
| Reference specific insights by name | Give generic "this is interesting" assessments |
| Be direct about what to skip | Hedge on recommendations |

## Related Skills

- **agents-spinning-up**: Provides calibration prompt for this agent
- **youtube-digesting-videos**: Uses this skill as the personality agent step
- **course-learning-panels**: Could be retrofitted to use this skill
- **waking-up**: Similar context-loading pattern (for conversation start, not content)
