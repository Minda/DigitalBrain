# PARA

<!-- Notion Links (update here if URLs change) -->
<!-- Q1 Projects Database (Source of Truth): https://www.notion.so/mindamyers/Q1-Projects-2026-3173caf373e0816d8f32dce784c1346f -->
<!-- Project Template: https://www.notion.so/mindamyers/P-PROJECT_TEMPLATE-31f3caf373e08041a6c0db48b2a0bb2b -->

Maintain and provide standards for the PARA (Projects, Areas, Resources, Archives) organizational system by Tiago Forte.

**Important:** Notion Q1 Projects database is the source of truth for projects. Local PARA folders are optional and only created when projects need local file storage.

## Trigger Phrases

- "PARA standards"
- "PARA structure"
- "PARA system"
- "how should I organize this in PARA"
- "PARA framework"

## What This Skill Does

This skill provides documentation and standards for the PARA organizational system, which divides information into four categories:

1. **Projects** – Short-term efforts with a clear goal and definite end date
2. **Areas** – Ongoing responsibilities with no fixed end date (e.g., health, finances, relationships)
3. **Resources** – Topics of ongoing interest or reference material for future use
4. **Archives** – Inactive items from any of the other three categories

The skill maintains best practices for how to structure projects, what belongs in each category, and how to maintain the system over time.

## How It Works

When invoked, this skill:

1. Provides access to PARA standards and templates
2. Offers guidance on categorizing information
3. Helps structure new projects according to PARA principles
4. Advises on archiving and cleanup rituals

## Key Standards

### Project Structure

A PARA project folder should contain:

| Sub-Folder | Typical Contents | Purpose |
|---|---|---|
| `00-Brief` | Goals, success criteria, stakeholder list | Orient everyone quickly |
| `01-Research` | Project-specific references, competitor scans, meeting notes | Context you'll delete or archive later |
| `02-Assets` | Design files, data sets, scripts, media | Raw ingredients for deliverables |
| `03-Working` | Drafts, notebooks, whiteboards, code branches | In-progress work you're actively touching |
| `04-Decisions` | Change logs, agreed-upon specs, approvals | Prevents re-litigating choices |
| `05-Deliverables` | Final docs, slide decks, demo links, invoices | Hand-off package or shipping artifact |

*(Structure is flexible – simplicity beats perfection)*

### Areas

Areas are **active, continuous responsibilities** you maintain to a certain standard over time:

- Not one-off goals (those are Projects)
- Not optional interests (those are Resources)
- Have ongoing accountability
- Examples: "Maintain financial health," "Stay fit," "Nurture client relationships"

### Resources

Topics of ongoing interest or reference material:

- No timeline pressure
- May inform future projects
- Keep for inspiration or reference
- Examples: "AI-Avatar/Compliance patterns," "Rust programming resources"

### Archives

Completed or inactive items from Projects, Areas, or Resources:

- Date-stamped for easy retrieval
- Moved when no longer active
- Kept for reference only
- Example: `Archive/2025-09/Interactive-Avatar-MVP/`

## Best Practices

1. **Weekly Cleanup Ritual** – Archive obsolete drafts to keep folders sharp
2. **Cross-Link Tasks** – Reference task manager IDs in filenames for traceability
3. **Hand-Off Ready** – New people should understand a project in < 5 minutes
4. **Separation of Concerns** – SOPs go in Areas, evergreen research in Resources, finished work in Archives
5. **Sunset Gracefully** – When projects complete, archive them and promote reusable insights to Areas/Resources

## Project Brief Template

Every project should start with a brief in `00-Brief/` containing:

1. **Summary** – Purpose, scope, success criteria
2. **Objective** – Specific deliverable(s)
3. **Success Criteria** – Measurable targets
4. **Scope In/Out** – Clear boundaries
5. **Stakeholders** – RACI matrix
6. **Milestones & Timeline** – Key dates and owners
7. **Dependencies & Risks** – Known blockers
8. **Budget** (if applicable)
9. **Open Questions** – Unresolved items

See `references/example-project-brief.md` for a complete example.

## File Locations

- Project brief template: `.claude/skills/para/references/project-brief-template.md`
- Example brief: `.claude/skills/para/references/example-project-brief.md`
- PARA structure guide: `.claude/skills/para/references/para-structure-guide.md`

## Notes

- The PARA system works best when **Projects** are the primary active work area
- **Areas** should be reviewed regularly but aren't urgent
- **Resources** are for browsing when inspiration is needed
- **Archives** are write-once, rarely accessed
- The GTD skill uses PARA as its underlying organizational framework
