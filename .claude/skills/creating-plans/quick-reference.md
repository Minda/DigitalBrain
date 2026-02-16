# Quick Reference - Creating Plans

## When User Says...

| User Request | Your Response |
|-------------|---------------|
| "Let's do X" (complex task) | "Let me create a plan first to ensure we do this safely and systematically." |
| "Can you help with X?" (risky operation) | "I'll design a step-by-step plan with checkpoints where you can review progress." |
| "I want to process all my X" | "Let's start with a plan that includes test batches and statistical sampling." |
| "Build me a system for X" | "I'll create a comprehensive implementation plan with phases and validation steps." |
| "Document this project" | "I'll create a project document in `/docs/projects/` with architecture diagrams and feature tracking." |
| "Create a feature request" | "I'll create a feature request in `/docs/features/` linked to the parent project." |
| "What's the project status?" | "Let me check the project documentation and feature statuses." |
| "Update feature status" | "I'll update the status in both the feature document and index files." |

## Plan Structure Checklist

Before saving a plan, ensure it has:

- [ ] Clear goal statement
- [ ] Step-by-step phases (0-N)
- [ ] Manual review checkpoints
- [ ] Success criteria per step
- [ ] Safety features section
- [ ] Privacy/security notes
- [ ] Rollback strategy
- [ ] Test batch phases (5→20→100→all)

## Statistical Sampling

For any plan involving data processing:

| Total Items | Sample Size | Confidence |
|------------|-------------|------------|
| < 1,000 | ~30% | 95% ± 5% |
| 1,000-10,000 | ~370-400 | 95% ± 5% |
| > 10,000 | ~400 | 95% ± 5% |

## Safety Principles

1. **Test First**: Always test with 5-10 items
2. **Archive, Don't Delete**: Keep data recoverable
3. **Private Data**: Store in `personal/` only
4. **Manual Reviews**: After every major step
5. **Rollback Ready**: Plan how to undo changes

## File Organization

```
/plans/
├── [project-name].md          # The implementation plan
├── clothing-email-classifier.md
├── data-migration.md
└── api-integration.md

/docs/
├── features/                  # Feature documentation
│   └── YYYY-MM-DD-feature.md # With mermaid diagrams
└── projects/                  # Project documentation
    └── YYYY-MM-DD-project.md # With architecture diagrams

/personal/data/[project]/       # Project data (private)
├── database.db
├── logs/
└── backups/

/src/python/[project]/          # Project code (public)
└── main.py
```

## Documentation Quick Guide

### Creating Documentation

**New Feature**:
```bash
1. Read template: /docs/features/feature-request-template.md
2. Create file: /docs/features/YYYY-MM-DD-feature-name.md
3. Link to parent project
4. Update /docs/features/README.md
5. Update parent project's feature list
```

**New Project**:
```bash
1. Read template: /docs/projects/project-template.md
2. Create file: /docs/projects/YYYY-MM-DD-project-name.md
3. Fill architecture and risk diagrams
4. Update /docs/projects/README.md
5. Create initial features if needed
```

### Status Values

**Features**: `Draft` → `In Review` → `Approved` → `In Progress` → `Complete`
**Projects**: `Planning` → `In Progress` → `On Hold` → `Complete`

### Diagrams to Include

#### For Features (`/docs/features/`)
- **User Journey**: Flowchart of user steps
- **System Components**: Service interactions
- **State Transitions**: Feature states

#### For Projects (`/docs/projects/`)
- **Feature Dependencies**: What depends on what
- **Architecture**: System layers and services
- **Risk Matrix**: Impact vs likelihood

See `documentation-diagrams.md` for detailed mermaid diagram guidance.

### Relationship Rules

1. **Every feature** must have a `**Project**:` field linking to parent
2. **Every project** should list features in "Related Features" section
3. **Bidirectional links** - Update both sides when creating/modifying
4. **Status sync** - Update in document AND index files

## Quick Templates

### Minimal Plan (3 steps)
```markdown
## Step 0: Setup
- Install/configure
**Review**: Check working

## Step 1: Test
- Try with 5 items
**Review**: Verify results

## Step 2: Execute
- Process all items
**Review**: Confirm complete
```

### Standard Plan (6 steps)
```markdown
Step 0: Setup
Step 1: Assessment (measure scope)
Step 2: Test (5-10 items)
Step 3: Validate
Step 4: Batch (20-50 items)
Step 5: Full run
Step 6: Cleanup
```

### High-Risk Plan (9+ steps)
```markdown
Step 0: Setup & backup
Step 1: Assessment
Step 2: Dry run (no changes)
Step 3: Tiny test (1-2 items)
Step 4: Small test (5 items)
Step 5: Review & adjust
Step 6: Medium batch (20 items)
Step 7: Validation checkpoint
Step 8: Full processing
Step 9: Verification
Step 10: Documentation
```

## Response Templates

### Starting a Plan
"I'll create a comprehensive plan for this. Let me break it down into safe, testable steps with manual review points where you can verify everything is working correctly."

### After Creating Plan
"I've created a detailed plan and saved it to `/plans/[name].md`. The plan includes [N] steps with manual review checkpoints. Shall we start with Step 0 (setup)?"

### At Review Points
"✅ Step [N] complete. Please review:
- [What to check]
- [Expected outcome]
Ready to continue to Step [N+1]?"

## Common Patterns

### Data Processing Plan
1. Count total items
2. Calculate sample size
3. Test classification/processing
4. Apply to batches
5. Generate report

### Integration Plan
1. Set up credentials
2. Test connection
3. Validate data format
4. Small sync test
5. Full integration

### Migration Plan
1. Backup current state
2. Map old→new structure
3. Test with subset
4. Validate mapping
5. Migrate in batches
6. Verify completion

## Remember

> "A good plan today is better than a perfect plan tomorrow, but a careful plan with checkpoints is better than rushing into execution."

Save all plans to `/plans/` for future reference and documentation.