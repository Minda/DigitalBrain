# Audio Transcript Conversion Guide

Guidelines for converting synthesis reports into audio-friendly transcripts optimized for text-to-speech readers.

## Core Principles

1. **Write how you speak:** Use natural spoken language patterns
2. **Linear narrative:** No jumping around or cross-references
3. **Verbal signposting:** Guide the listener through the content
4. **Consistent pacing:** Vary between detail and summary to maintain engagement
5. **No visual dependencies:** Everything must make sense without seeing the text

## Conversion Rules

### Numbers and Symbols

| Written Form | Audio Form |
|--------------|------------|
| 50% | fifty percent |
| 3x | three times |
| 2/3 | two-thirds |
| O(1) | O of 1 or "constant time" |
| K = O(T) | K equals O of T |
| 3.3x gap | three point three times gap |
| ~50-60 | about fifty to sixty |
| ≥ | greater than or equal to |
| α → β | alpha leads to beta |

### Formatting Removal

**Before:**
```markdown
## Section Title

- Bullet point 1
- Bullet point 2
  - Sub-bullet A
  - Sub-bullet B
```

**After:**
```markdown
Let me talk about section title.

There are two main points here. First, bullet point 1. Second, bullet point 2. Within that second point, there are two parts: sub-bullet A and sub-bullet B.
```

### Tables to Prose

**Before:**
```markdown
| Model | Time Horizon | Performance |
|-------|--------------|-------------|
| GPT-4o | 30 min | Good |
| Claude | 50 min | Better |
```

**After:**
```markdown
Let me compare the models. GPT-4o has a thirty-minute time horizon with good performance. Claude has a fifty-minute time horizon with better performance.
```

### Lists to Narrative

**Before:**
```markdown
**Key findings:**
1. Finding one
2. Finding two
3. Finding three
```

**After:**
```markdown
There are three key findings. First, finding one. Second, finding two. And third, finding three.
```

### Technical Terms

**On first mention:**
```markdown
The paper introduces doubly-efficient debate - that's a framework where two AI systems compete to convince a verifier.
```

**Subsequent mentions:**
```markdown
In the doubly-efficient debate protocol...
```

**Avoid:**
- "As mentioned earlier" (listener can't reference back)
- "See Section X" (no visual access)
- "The above table shows" (no table visible)

## Structure Template

### Opening (30-60 seconds)

```markdown
Hi, this is your [topic] synthesis for [event/date]. I'm going to walk you through [what this covers].

[Brief context: why this matters, what you'll learn]

Let's start with the main findings.
```

### Body Sections

**Pattern for each section:**
1. **Introduce:** "Now let's talk about..."
2. **Explain:** Core content in conversational prose
3. **Connect:** "This connects to what I mentioned earlier about..."
4. **Transition:** "Next, I'll cover..."

**Example:**
```markdown
Now let's talk about the core contribution.

The problem is this: as AI systems tackle increasingly complex tasks like writing legal contracts, we can't afford to have human experts read entire outputs for training. We need verification methods that are extremely efficient in their use of human judgement.

The solution the paper proposes is called doubly-efficient debate. Here's how it works. Two AI systems, called provers A and B, compete to convince a verifier who has access to human judgement. The clever part is that the honest prover can always win using only polynomial simulation steps, even when competing against a dishonest prover with unlimited computation. Meanwhile, the verifier only needs to make a constant number of queries to human judgement - that number doesn't grow with how complex the task is.

This connects to scalable oversight, which I'll explain next.
```

### Closing (30-45 seconds)

```markdown
Let me wrap up with the key takeaways.

[3-4 main points in plain language]

The main things to remember are [critical 1-2 points].

For next steps, [actionable items].

That's your overview. The full synthesis report has additional details, references, and discussion questions.
```

## Timing Guidelines

**Target length:** 15-25 minutes at normal speaking pace (150-170 words per minute)

**Rough word counts:**
- Opening: 100-150 words (30-60 sec)
- Each major section: 300-500 words (2-3 min)
- Critical technical detail: 200-300 words (1-2 min)
- Closing: 80-120 words (30-45 sec)

**Pacing variation:**
- **Dense technical sections:** Slower, more explanatory
- **Context/implications:** Moderate pace
- **Summaries/transitions:** Quicker, connective

## Voice and Tone

### Use:
- "Let me explain..."
- "Here's what's important..."
- "The key insight is..."
- "This is where it gets interesting..."
- "You might be wondering..."

### Avoid:
- "As you can see..."
- "Refer to..."
- "The reader will notice..."
- Academic passive voice
- Overly formal transitions

## Handling Complex Content

### Technical Concepts

**Strategy:** Explain → Example → Recap

```markdown
The paper introduces something called the Lipschitz assumption. Here's what that means. If the oracle's probabilities change by a small amount epsilon, the machine's output probability changes by at most K times epsilon. Think of it like signal-to-noise ratio - small changes in input don't cause huge swings in output.

The Lipschitz assumption ensures that small oracle perturbations don't accumulate catastrophically over many steps. For time T steps, if K equals O of 1 - meaning K is constant - then you get meaningful guarantees.
```

### Equations/Proofs

**Avoid:** Reading equations verbatim
**Instead:** Explain the intuition

```markdown
The math shows that you can verify any polynomial-time computation using only constant human judgements. The formal statement involves Big-O notation, but the key idea is that verification cost doesn't grow with problem complexity - it stays bounded.
```

### Multiple Perspectives

**When presenting different views:**

```markdown
There are two ways to think about this. On one hand, [perspective A]. On the other hand, [perspective B]. The difference matters because [why it matters].
```

## Example Conversions

### Before: List of Findings

```markdown
## Key Findings

- Theorem 5.3: Any polynomial-time computation verifiable with O(T log T) prover time, O(l log T) verifier time
- Cross-examination enables spot-checking
- Lipschitz assumption K = O(1) gives best results
```

### After: Narrative Flow

```markdown
Let me walk you through the three key findings.

The first is Theorem five point three. It proves that any polynomial-time computation can be verified efficiently. The prover - that's the AI system producing the work - runs in O of T log T time. The verifier - checking the work - only needs O of l log T time, where l is the oracle query length. This is a huge improvement because the verifier is much faster than running the full computation.

The second finding is about cross-examination. This is the technique that enables spot-checking. Instead of reading an entire transcript, the verifier can query independent copies of the AI systems and just check specific locations where disagreement occurs. It's like debugging code by setting a breakpoint, rather than stepping through every line.

The third finding relates to the Lipschitz assumption. When K equals O of 1 - meaning it's a constant independent of the computation length - you get the best results. The paper shows you only need constant oracle queries in this case. This is the sweet spot for practical applications.
```

### Before: Table with Technical Data

```markdown
| Protocol | Prover Time | Verifier Time | Queries |
|----------|-------------|---------------|---------|
| Deterministic | O(T log T) | O(S log T) | O(1) |
| Stochastic | O(K²T log T) | O(K² + l log T) | O(K²) |
```

### After: Comparison Narrative

```markdown
The paper presents two protocols - one for deterministic oracles and one for stochastic oracles. Let me compare them.

For the deterministic case, the prover runs in O of T log T time. The verifier needs O of S log T time, where S is the space used. And crucially, only O of 1 oracle queries - that's constant, doesn't grow with problem size.

For the stochastic case, things are slightly more complex. The prover needs O of K squared T log T time. The verifier needs O of K squared plus l log T time. And you need O of K squared oracle queries. Remember that K is the Lipschitz constant I mentioned earlier. When K is constant, this is still very efficient.

The stochastic protocol is more realistic because it handles human judgement, which is inherently noisy and probabilistic. That's the version you'd actually use in practice.
```

## Quality Checklist

Before finalizing audio transcript, verify:

- [ ] No "see above/below" references
- [ ] All numbers spelled out
- [ ] No bullet points or tables
- [ ] Natural spoken transitions
- [ ] Technical terms explained on first use
- [ ] Sections introduced and concluded
- [ ] Consistent narrative voice
- [ ] Timing reasonable (15-25 min)
- [ ] No visual formatting cues
- [ ] Clear opening and closing

## Common Pitfalls

**Pitfall:** Too much detail retention
**Fix:** Summarize technical appendices, focus on main results

**Pitfall:** Reading lists verbatim
**Fix:** Convert to "First..., Second..., Third..." pattern

**Pitfall:** Abrupt topic changes
**Fix:** Add bridging sentences between sections

**Pitfall:** Assuming listener has visual context
**Fix:** Provide all necessary context verbally

**Pitfall:** Overly long sentences
**Fix:** Break into shorter, digestible chunks

## Testing

**Read aloud test:** If you wouldn't say it in conversation, rewrite it.

**Comprehension test:** Would someone understand without seeing any text?

**Engagement test:** Does it maintain interest for 20+ minutes?

**Accuracy test:** Does it preserve the key technical content?
