# Project Type Definitions

Complete reference for the four project types in the Q1 Projects database.

## Active Project

### Definition
A concrete project with specific deliverables, clear success criteria, and a defined end date.

### When to Use
- You have a specific outcome you want to achieve
- The work has a natural completion point
- You can estimate when it will be done (even if roughly)
- Success can be measured objectively

### Properties to Set
- **Project Type**: "Active Project"
- **Start Date**: When you're beginning work
- **End Date**: Target completion date (required)
- **Project Scale**: Estimated hours (quick/small/med/large)
- **Status**: One of standard workflow states
- **Progress**: Track % completion
- **Category**: Thematic categorization
- **Tags**: May include shared tags with related Ongoing Projects

### Tracking Method
- Update Progress % as work advances
- Move through Status workflow (Backlog → In Progress → Completed)
- Mark complete when deliverable is finished
- Archive after completion

### Examples
| Project | Hours | Duration | Why Active |
|---------|-------|----------|------------|
| Build portfolio website | 30 | 3 weeks | Clear deliverable, measurable completion |
| Complete BlueDot Unit 3 | 10 | 1 week | Course has defined end, assignments due |
| Write Substack post on multi-agent safety | 5 | 3 days | Single article, publish = done |
| Implement Gmail bulk ops CLI | 15 | 2 weeks | Feature set defined, can ship v1 |

### Relationship to Other Types
- **Connects to Ongoing Projects**: Via shared Category/Tags
  - Example: "Build portfolio site" (Active) supports "Job search" (Ongoing)
- **Does NOT connect to Habits**: Habits are background, Active Projects are foreground
- **Can use Templates**: Start from template when creating

---

## Habit/Routine

### Definition
A recurring activity performed on a regular schedule (daily, weekly) with no end date. The goal is consistency, not completion.

### When to Use
- The activity repeats indefinitely
- Success is measured by streaks/frequency, not outcomes
- There's no "done" state—it continues as long as it's valuable
- It's maintenance or self-care, not project work

### Properties to Set
- **Project Type**: "Habit/Routine"
- **Start Date**: When you began the habit
- **End Date**: NULL (leave empty)
- **Status**: "In Progress" (stays there forever)
- **Progress**: N/A or used for streak tracking
- **Category**: Usually "🩷 Personal" or relevant area
- **Tags**: "Recurring" (for backward compatibility)

### Tracking Method
- Create sub-items for each occurrence (check-ins)
  - Example: Daily medication → sub-item per day
  - Example: Weekly review → sub-item per week
- Track streaks if motivating (how many days in a row)
- **Never mark as Completed**—this is ongoing

### Examples
| Habit | Frequency | Tracking Method |
|-------|-----------|-----------------|
| Medication & supplement schedule | Daily | Daily check-in sub-items |
| Daily journaling | Daily | One sub-item per day |
| Weekly review | Weekly | Sunday sub-items with reflection notes |
| Morning routine | Daily | Checkbox list, reset daily |

### Relationship to Other Types
- **Independent from Active Projects**: Background maintenance, not tied to deliverables
- **May relate to Ongoing Projects**: Weekly review might touch all areas
- **Never becomes Template**: Habits are instances, not blueprints

---

## Ongoing Project

### Definition
An open-ended area of responsibility with no concrete end date or vague completion criteria. More like PARA "Areas" than traditional projects.

### When to Use
- You have ongoing responsibility but no specific deliverable
- The work continues until external circumstances change
- You can track milestones but not "completion"
- Multiple Active Projects might relate to this area

### Properties to Set
- **Project Type**: "Ongoing Project"
- **Start Date**: When responsibility began
- **End Date**: NULL or vague future date (e.g., "when hired")
- **Status**: "In Progress"
- **Progress**: Percentage of milestones completed (if meaningful)
- **Category**: Thematic area (Job Search, WellAware, etc.)
- **Tags**: May share tags with related Active Projects

### Tracking Method
- Create child pages or sub-items for milestones/sessions
  - Example: Job search → "Applied to 5 roles", "Interview with Meta"
  - Example: Anusha work → "Case study 1 review", "Case study 2 draft"
- Track progress via milestone completion, not end date
- **Never mark as Completed**—mark as "On Hold" or archive when responsibility ends

### Examples
| Ongoing Project | Vague End | Milestone Tracking |
|-----------------|-----------|-------------------|
| Job search | "When hired" | Applications submitted, interviews scheduled |
| Work with Anusha | "Project ends" | Case studies reviewed, feedback provided |
| Maintain WellAware codebase | Indefinite | Bug fixes, feature adds, refactors |
| BlueDot participation | "Course ends" | Sessions attended, assignments submitted |

### Relationship to Other Types
- **Parent to Active Projects**: Active Projects often support Ongoing Projects
  - Example: "Job search" (Ongoing) + "Build portfolio site" (Active, 30h)
  - Link via shared Category/Tags (both tagged "🔵 Job Search")
- **Different from Habits**: Habits are routines, Ongoing Projects are responsibilities
- **May have Templates**: Can create template for recurring session types

---

## Template

### Definition
A reference starting point for creating new projects. Contains structure, placeholders, and best practices but is never used directly.

### When to Use
- You've found a project pattern you want to reuse
- New team members need a starting point
- You want consistency across similar projects
- The template represents best practices you've learned

### Properties to Set
- **Project Type**: "Template"
- **Category**: "Template"
- **Start Date**: N/A
- **End Date**: N/A
- **Status**: N/A (ignored)
- **Progress**: N/A

### Tracking Method
- **Never track progress on templates**
- Templates are copied/instantiated, not executed
- Update template when you learn better practices
- Version templates if structure changes significantly

### Examples
| Template | Use Case |
|----------|----------|
| P \\| PROJECT_TEMPLATE | Standard project structure with all sections |
| Quick Win Template (<=3 hours) | Small, focused projects |
| Research Synthesis Template | Multi-source research projects |
| Weekly Planning Template | Recurring weekly review structure |

### Relationship to Other Types
- **Source for Active Projects**: Copy template when starting new Active Project
- **Source for Ongoing Projects**: Some ongoing work has templated sessions
- **Not for Habits**: Habits don't need templates (they're simple recurring items)

---

## Decision Matrix: Which Type to Use?

| Question | Active Project | Habit/Routine | Ongoing Project | Template |
|----------|----------------|---------------|-----------------|----------|
| Has end date? | ✅ Yes, specific | ❌ No | ❌ No or vague | N/A |
| Clear deliverable? | ✅ Yes | ❌ No | ❌ Not concrete | N/A |
| Repeats regularly? | ❌ No | ✅ Yes | ⚠️ Sessions may | N/A |
| Can be "completed"? | ✅ Yes | ❌ Never | ❌ Never | N/A |
| Tracks progress? | ✅ % to completion | ⚠️ Streaks | ⚠️ Milestones | ❌ No |
| Example duration | Days to months | Indefinite | Months to years | N/A |

---

## Migration Guide

For existing items in the database:

### Tagged "Recurring" + No End Date → Habit/Routine
- Medication schedule
- Daily journaling
- Weekly reviews

### Tagged "Recurring" + Has End Date → Ongoing Project
- Job search (ends when hired)
- BlueDot participation (ends when course completes)
- Anusha collaboration (ends when project wraps)

### Category = "Template" → Template
- P | PROJECT_TEMPLATE
- Any other template items

### Everything Else → Active Project
- All concrete projects with deadlines
- Discrete deliverables
- Standard workflow items

---

## Common Mistakes

### Mistake: Making a Habit an Active Project
**Symptom**: Daily medication marked as "Active Project" with end date next week
**Fix**: Change to Habit/Routine, remove end date
**Why**: Medication is ongoing maintenance, not a completable project

### Mistake: Making an Ongoing Project Active
**Symptom**: "Job search" as Active Project with end date "March 31"
**Fix**: Change to Ongoing Project, track milestones instead
**Why**: You can't guarantee when you'll be hired—it's open-ended

### Mistake: Never completing Active Projects
**Symptom**: 50 Active Projects, all "In Progress", none ever finished
**Fix**: Review each—some should be Ongoing, others should be completed or archived
**Why**: Active Projects must have completion points or they're not actually projects

### Mistake: Using Template as Project
**Symptom**: Template has Progress %, Status changes, gets worked on
**Fix**: Copy template to create new Active Project, work on the copy
**Why**: Templates are blueprints, not instances

---

## Integration Notes

### For GTD Skill
- Weekly planning filters by Project Type to show appropriate views
- Active Projects appear in timeline
- Habits appear in daily routines
- Ongoing Projects appear in areas review
- Templates hidden from planning views

### For Notion Projects Skill
- Set Project Type when creating projects
- Default to Active Project unless specified
- Offer template selection for new projects
- Validate that Active Projects have end dates

### For PARA Skill
- Active Projects = PARA Projects
- Ongoing Projects = PARA Areas
- Habits = Part of PARA Areas (personal maintenance)
- Templates = PARA Resources (reusable patterns)
