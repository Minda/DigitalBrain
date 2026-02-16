# Creating Plans & Documentation Skill

A comprehensive system for creating implementation plans AND managing project/feature documentation with visual diagrams and relationship tracking.

## What This Skill Does

### 1. Implementation Plans (`/plans/`)
Creates structured, step-by-step plans for complex projects that:
- Break down tasks into manageable phases
- Include manual review checkpoints
- Implement safety measures and rollback strategies
- Handle personal data appropriately
- Use statistical sampling for large datasets

### 2. Project Documentation (`/docs/`)
Manages feature requests and project documentation with:
- Feature requests with user journey diagrams
- Project documentation with architecture diagrams
- Bidirectional linking between features and projects
- Status tracking and index maintenance
- Mermaid diagrams for visualization

## Files in This Skill

- `SKILL.md` - Main skill instructions and methodology
- `plan-template.md` - Reusable template for new plans
- `quick-reference.md` - Quick lookup guide and patterns
- `documentation-diagrams.md` - Guide for filling out mermaid diagrams in docs
- `README.md` - This file

## When to Use This Skill

✅ **Use for Implementation Plans when:**
- User requests a complex multi-step project
- Task involves processing personal/sensitive data
- Changes could have significant impact
- User explicitly asks for a plan
- Operation needs to be reversible

✅ **Use for Documentation when:**
- User wants to document a new project
- User needs to create a feature request
- User asks about project/feature status
- Need to track relationships between features and projects
- Want visual diagrams for architecture or workflows

❌ **Don't use when:**
- Task is simple and straightforward
- User wants immediate execution without planning
- Task is purely informational
- No data or system changes involved

## How It Works

1. **Gather Requirements** - Understand the goal and constraints
2. **Design Plan Structure** - Create phases with checkpoints
3. **Add Safety Measures** - Include rollback and validation
4. **Save to `/plans/`** - Document for review and execution
5. **Execute with Reviews** - Follow plan with user confirmation

## Example Usage

### Creating an Implementation Plan
```markdown
User: "I want to organize all my emails and unsubscribe from marketing lists"

Claude: "This is a complex task that involves processing personal data.
Let me create a comprehensive plan to do this safely and systematically.

I'll break this down into:
1. Assessment phase to understand scope
2. Test phase with small batches
3. Validation checkpoints
4. Full processing with progress tracking

The plan will include safety measures and keep all your email data
in the private personal/ directory."

[Creates plan at /plans/email-organization.md]
```

### Creating Documentation
```markdown
User: "Document a new project for building a notification system"

Claude: "I'll create project documentation for the notification system.
This will include:
- Project goals and scope
- Architecture diagrams showing system components
- Risk assessment matrix
- Placeholder for related features

I'll also set up the structure for tracking individual features
as they're defined."

[Creates project at /docs/projects/2025-02-15-notification-system.md]
[Updates /docs/projects/README.md index]
```

## Key Principles

### Safety First
- Test with small batches (5→20→100→all)
- Archive instead of delete
- Include rollback procedures
- Manual review after risky operations

### Privacy Conscious
- Personal data stays in `personal/`
- Credentials in `.gitignore`
- Clear privacy warnings in plans
- No sensitive data in public repos

### Statistically Valid
- Calculate proper sample sizes
- Show confidence levels (95% ± 5%)
- Provide estimations with ranges
- Test assumptions before full runs

## Integration with Other Skills

Works well with:
- `saving-memories` - Preserve insights from execution
- `learning` - Document what worked/didn't work
- `self-regulation` - When plan involves sensitive operations

## Storage Structure

### Implementation Plans → `/plans/`
- Step-by-step execution plans
- Safety checkpoints and rollback procedures
- Test batches and validation steps
- Named: `project-name.md` (no date prefix)

### Feature Documentation → `/docs/features/`
- Individual feature requests
- User journey and state diagrams
- Linked to parent projects
- Named: `YYYY-MM-DD-feature-name.md`

### Project Documentation → `/docs/projects/`
- High-level project scope and goals
- Architecture and risk diagrams
- Lists related features
- Named: `YYYY-MM-DD-project-name.md`

### Key Difference:
- **`/plans/`** = HOW to implement (execution steps)
- **`/docs/`** = WHAT to build (requirements & design)

## Success Metrics

A good plan has:
- ✅ Clear, measurable goals
- ✅ 5-10 distinct phases
- ✅ Manual reviews every 2-3 steps
- ✅ Success criteria for each phase
- ✅ Safety/rollback procedures
- ✅ Privacy considerations documented

## Tips

1. **Start small** - Test with tiny batches first
2. **Document assumptions** - Make them explicit
3. **Plan for failure** - Include error handling
4. **Get user buy-in** - Review before execution
5. **Track progress** - Update plan status as you go

---

Created: 2024-02-13
Updated: 2025-02-15 (Added documentation workflows)
Part of the Exobrain project