# /de-ai - Remove AI-Generated Patterns from Text

## Purpose
Transform AI-generated text to sound more human by removing telltale patterns and adding authentic details.

## Usage

```
/de-ai
[text to modify]
```

Or just:
```
/de-ai
```
(Will use the most recent assistant output)

Or with directions:
```
/de-ai
Make the third paragraph sound more like a startup founder wrote it
```

## Core Transformations

### 1. Add Specific Details
- Replace generalizations with concrete examples
- Add operational details only an insider would know
- Include actual numbers, names, timeframes

### 2. Break Rhythm
- Vary sentence length dramatically
- Add pauses and afterthoughts
- Split flowing sentences into fragments

### 3. Insert Human Reactions
- Add "I" statements and personal observations
- Include what surprised or impressed you
- Show where you're witnessing from

### 4. Reorder by Importance
- Lead with what actually mattered to you
- Break logical flow for emotional truth
- Group by impact, not category

### 5. Leave Imperfections
- Don't fix every typo
- Allow informal punctuation
- Keep conversational fragments

### 6. Remove Em Dashes
- NEVER use "—" (em dash) - it's a massive AI tell
- Replace with periods, commas, or parentheses
- Use regular hyphens for compound words

### 7. Cut Hedging
- Remove "it's important to note"
- Delete unnecessary qualifiers
- Say what you mean directly

## Overused AI Words to Replace

**Verbs:** delve → look into, leverage → use, utilize → use, underscore → show, showcase → show, foster → build, navigate → handle, streamline → simplify

**Adjectives:** comprehensive → complete, crucial → key, pivotal → important, meticulous → careful, robust → strong, commendable → good, invaluable → useful, cutting-edge → new

**Nouns:** landscape → field, realm → area, tapestry → mix, symphony → combination, synergy → teamwork, paradigm → model, framework → structure

**Phrases to delete entirely:**
- "it's important to note that"
- "in today's fast-paced world"
- "this is a testament to"
- "whether you're a beginner or an expert"
- "at its core"
- "strikes a balance between"

## Implementation

The skill:
1. Identifies AI patterns in the text
2. Suggests specific replacements
3. Adds concrete details where possible
4. Varies sentence structure
5. Removes hedging language
6. Preserves the core message while making it sound human

## Examples

**Before:** "She demonstrates exceptional problem-solving capabilities and leverages cross-functional collaboration to drive innovative solutions."

**After:** "She solved our GPU memory issue in two days. Pulled in someone from infrastructure to help - they figured it out together."

**Before:** "This comprehensive approach underscores our commitment to delivering cutting-edge solutions."

**After:** "We built it this way because we wanted it to actually work."

## The Test

Read it aloud. Does it sound like a specific person talking? Not professional writing - but THIS person, in THIS context, explaining THIS thing.