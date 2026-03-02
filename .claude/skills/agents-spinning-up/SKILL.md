---
name: agents-spinning-up
description: Shared calibration protocol for agent initialization. Loads anti-sycophancy prompt and startup standards. Use when launching subagents, setting up multi-agent workflows, or when user says "calibrate agents", "spin up agents", or "agent calibration."
allowed-tools: [Read, Glob]
---

# Agents Spinning Up

Shared calibration protocol that agents load at initialization. Ensures agents produce honest, direct analysis rather than validation-seeking output. Currently focused on anti-sycophancy; designed to grow as new initialization standards emerge.

## Quick Start

1. Read `references/calibration-prompt.md` from this skill's directory
2. Inject the calibration prompt into the agent's system instructions
3. The agent proceeds with its domain-specific task, now calibrated

## When to Use

- Launching subagents in multi-agent workflows
- Any Task agent that produces analysis, summaries, or assessments
- When other skills reference this skill for agent initialization

## When Not to Use

- Single-turn simple queries (overhead not worth it)
- Agents doing purely mechanical tasks (file copying, formatting)

## Instructions

### For skills that reference this skill

Read the calibration prompt and prepend it to your agent instructions:

    Read .claude/skills/agents-spinning-up/references/calibration-prompt.md

Include it as a preamble in the agent's Task prompt, before the domain-specific instructions.

### For direct invocation

If the user invokes this directly, read and display the calibration prompt, then ask what agent or workflow they want to calibrate.

### Integration pattern

When building a multi-agent workflow that uses this skill:

1. Read the calibration prompt once at orchestrator level
2. Include it in each agent's instruction set
3. Do not modify the calibration prompt per-agent. It is universal.

## What the Calibration Covers

The current calibration prompt addresses six failure modes:

1. **Sycophancy** - agreement bias, burying disagreement, capitulating without new information
2. **Over-explanation** - patronizing filler, defining terms the user already commands
3. **Performative metacognition** - narrating reasoning process as theater
4. **Hedge accumulation** - stacking qualifiers beyond actual uncertainty
5. **False balance** - artificial symmetry when one position is clearly stronger
6. **Question drift** - answering adjacent questions instead of the one asked

Plus style rules: no em dashes, no hyperbolic frames, plain English, verify references.

See `references/calibration-prompt.md` for the full prompt text.

## Extending the Calibration

To add new calibration standards:
1. Append a new section to `references/calibration-prompt.md`
2. Update the "What the Calibration Covers" list above
3. Keep the prompt modular. Each standard should be a self-contained section.

## Related Skills

- **agent-customizing-content** - Uses this skill for agent calibration before personalization
- **youtube-digesting-videos** - Uses this skill for all parallel video agents
- **course-learning-panels** - Could be retrofitted to use this skill
