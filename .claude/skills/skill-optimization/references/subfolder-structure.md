# Skill Subfolder Structure Guide

How to organize skill content across subfolders for optimal token efficiency.

## Standard Structure

```
.claude/skills/skill-name/
├── SKILL.md                    # Main skill file (<1,000 words)
├── references/                 # Detailed documentation
│   ├── implementation-guide.md
│   ├── example-workflows.md
│   └── troubleshooting.md
├── scripts/                    # Executable tools
│   ├── process.py
│   └── validate.sh
├── templates/                  # Reusable file templates
│   └── OUTPUT_TEMPLATE.md
└── examples/                   # Complete usage examples (optional)
    └── real-world-scenario.md
```

## When to Create Each Subfolder

### `references/` (Always create)

**Purpose**: Detailed documentation that would bloat the main SKILL.md

**Create when**:
- Main SKILL.md exceeds 800 words
- You have verbose explanations of concepts
- Multiple detailed examples exist
- Technical implementation details are needed
- Troubleshooting guide would help

**Common files**:
- `implementation-guide.md` - Technical details, code patterns
- `example-workflows.md` - Complete end-to-end examples
- `troubleshooting.md` - Common issues and solutions
- `api-reference.md` - API details, parameters, return values
- `performance-patterns.md` - Optimization techniques
- `mermaid-best-practices.md` - Diagram creation guidelines
- `condensing-techniques.md` - How to reduce tokens

**What to move here**:
- Long code examples (>20 lines)
- Multiple example scenarios
- Detailed explanations of "why"
- Historical context or evolution notes
- Advanced usage patterns
- Edge case handling

### `scripts/` (Create when executable code exists)

**Purpose**: Python/shell scripts that automate skill operations

**Create when**:
- Skill performs file transformations
- Complex logic is reused across invocations
- Performance benefits from pre-built tools
- User might run operations outside Claude

**Common files**:
- `process_data.py` - Main processing script
- `validate.py` - Input validation
- `benchmark.py` - Performance testing
- `setup.sh` - Initial configuration
- `test.py` - Unit tests for logic

**What to put here**:
- Complete Python scripts (not code snippets)
- Shell automation tools
- Data transformation utilities
- Benchmarking tools
- Testing harnesses

**Example** - conversations-manage:
```
scripts/
├── rename_conversation.py        # Handles JSONL update + custom-title entry
├── suggest_titles.py              # Analyzes conversation and generates titles
├── list_conversations.py          # Quick CLI for listing recent
└── search_conversations.py        # Grep-style search with snippets
```

### `templates/` (Create when skill generates files)

**Purpose**: Reusable file templates that skill populates

**Create when**:
- Skill creates new files with standard structure
- Users need to see expected output format
- Multiple variations of output exist
- Template serves as documentation

**Common files**:
- `SKILL_TEMPLATE.md` - For skill-creator
- `PROJECT_TEMPLATE.md` - For notion-projects
- `ITERATIONS.md` - For skill-optimization tracking
- `OUTPUT_FORMAT.md` - Expected output structure
- `CONFIG_TEMPLATE.yaml` - Configuration file template

**What to put here**:
- Markdown templates with placeholders
- YAML/JSON configuration templates
- Output format examples
- Boilerplate structures

### `examples/` (Optional - create sparingly)

**Purpose**: Complete, real-world examples that are too long for references/

**Create when**:
- Examples are >500 words each
- Multiple complex scenarios exist
- Examples include images/diagrams
- Separating examples improves navigation

**Common files**:
- `research-workflow.md` - Complete research session example
- `debugging-session.md` - Real debugging walkthrough
- `multi-agent-synthesis.md` - Complex multi-step example

**What to put here**:
- Full conversation transcripts
- Before/after comparisons with detailed commentary
- Multi-step workflows with screenshots
- Case studies

**Warning**: Don't create this folder just for 1-2 short examples. Those belong in `references/example-workflows.md`.

## Progressive Disclosure Strategy

### Phase 1: Initial Skill (everything in SKILL.md)

When creating a new skill, start with everything in one file:
- Quick to write
- Easy to test
- Can see full context

### Phase 2: First Optimization (create references/)

When SKILL.md exceeds 1,000 words:
1. Create `references/` folder
2. Move detailed examples → `references/example-workflows.md`
3. Move implementation details → `references/implementation-guide.md`
4. Keep only essential instructions in SKILL.md

### Phase 3: Add Executable Scripts (create scripts/)

When you've written the same code pattern 3+ times:
1. Create `scripts/` folder
2. Extract reusable logic → `.py` or `.sh` files
3. Update SKILL.md to reference scripts
4. Add usage examples in `references/`

### Phase 4: Formalize Output (create templates/)

When skill generates structured output:
1. Create `templates/` folder
2. Document expected formats
3. Provide blank templates for users
4. Reference from SKILL.md

## Referencing Subfolders in SKILL.md

### Pattern 1: Inline Reference

```markdown
**Always use**: `python3 scripts/rename_conversation.py "Title"`

See `references/implementation-guide.md` for technical details.
```

### Pattern 2: Resources Section

```markdown
## Resources

- `references/performance-patterns.md` - Optimization techniques
- `references/mermaid-best-practices.md` - Diagram guidelines
- `references/condensing-techniques.md` - Token reduction strategies
- `templates/ITERATIONS.md` - Optimization history template
- `scripts/benchmark_skill.py` - Performance testing
```

### Pattern 3: See Also Links

```markdown
## Implementation Details

**File format**: JSONL (one JSON object per line)

**Custom title handling**: Use dedicated `type: "custom-title"` objects

See `references/implementation-details.md` for complete JSONL format specification.
```

## Token Savings by Subfolder

Based on real optimization results:

| Content Type | Location Before | Location After | Token Savings |
|--------------|----------------|----------------|---------------|
| Long examples (>50 lines) | SKILL.md | references/ | 400-800 tokens |
| Python code snippets | SKILL.md | scripts/ | 200-400 tokens |
| Detailed explanations | SKILL.md | references/ | 300-600 tokens |
| Template structures | SKILL.md | templates/ | 150-300 tokens |
| Troubleshooting guides | SKILL.md | references/ | 200-400 tokens |

**Average savings**: Moving appropriate content to subfolders reduces SKILL.md by **50-65%**.

## Checklist for Skill Organization

**Before optimization:**
- [ ] All content in single SKILL.md file
- [ ] File is >1,000 words (>1,500 tokens)
- [ ] Contains code examples >20 lines
- [ ] Has multiple detailed scenarios
- [ ] Includes troubleshooting information

**After optimization:**
- [ ] SKILL.md is <1,000 words (<1,500 tokens)
- [ ] Created `references/` with 2-4 focused documents
- [ ] Extracted scripts to `scripts/` if applicable
- [ ] Created templates in `templates/` if skill generates files
- [ ] All references use clear, consistent paths
- [ ] Resources section lists all subfolders
- [ ] Critical information remains in SKILL.md

## Anti-Patterns

**Don't:**
- Create empty placeholder folders "for future use"
- Split content into 10+ micro-files (hard to navigate)
- Put 2-line code snippets in scripts/ (keep inline)
- Reference files that don't exist yet
- Create deeply nested subfolder structures

**Do:**
- Create folders only when content actually needs separation
- Keep related content together (e.g., all examples in one file)
- Use descriptive filenames (`mermaid-best-practices.md` not `tips.md`)
- Maintain clear references from SKILL.md to subfolders
- Keep structure flat (max 2 levels deep)

## Example: Well-Organized Skill

```
.claude/skills/research-synthesis/
├── SKILL.md                         # 650 words - core workflow only
├── references/
│   ├── orchestration-guide.md       # Multi-agent coordination details
│   ├── synthesis-template.md        # Output format specification
│   ├── agent-personas.md            # Research/Evaluator/Expert profiles
│   └── example-workflows.md         # 3 complete synthesis examples
├── scripts/
│   ├── fetch_transcripts.py         # YouTube transcript fetching
│   ├── chunk_content.py             # Content splitting for agents
│   └── synthesize.py                # Main orchestration script
└── templates/
    ├── RESEARCH_OUTPUT.md           # Research agent output format
    ├── EVALUATION_CRITERIA.md       # Quality gate checklist
    └── SYNTHESIS_REPORT.md          # Final output template
```

**SKILL.md references**:
- Mentions scripts with `python3 scripts/fetch_transcripts.py`
- Links to orchestration guide for agent coordination
- Points to templates for output formats
- Resources section lists all files with descriptions

**Result**: Main file stays focused, all supporting content easily discoverable.
