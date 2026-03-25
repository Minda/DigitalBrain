# PARA Structure Guide

## The Four Categories

### Projects

**Definition:** Short-term efforts with a clear goal and a definite end date.

**Characteristics:**
- Has a specific outcome or deliverable
- Has a deadline or completion milestone
- Temporary by nature
- When complete, moves to Archives

**Examples:**
- "Launch Interactive Avatar MVP by Sept 12"
- "Complete Q1 2026 budget planning"
- "Migrate authentication system to OAuth"

**Project Folder Structure:**

```
ProjectName/
├── 00-Brief/              # Goals, scope, stakeholders
├── 01-Research/           # Project-specific background
├── 02-Assets/             # Raw materials
├── 03-Working/            # In-progress drafts
├── 04-Decisions/          # Approved specs and choices
└── 05-Deliverables/       # Final outputs
```

### Areas

**Definition:** Ongoing responsibilities with no fixed end date that you maintain to a certain standard.

**Characteristics:**
- No deadline (it's a continuous responsibility)
- Has a standard to maintain
- Active accountability
- Examples: Health, Finances, Relationships, Career Development

**What Belongs:**
- Standard operating procedures
- Regular review materials
- Ongoing maintenance items
- Role-specific responsibilities

**Examples:**
- "Financial Health" → budget templates, investment tracking
- "Engineering Excellence" → code review standards, learning goals
- "Client Relationships" → communication templates, account notes

### Resources

**Definition:** Topics of ongoing interest or reference material you may use in the future.

**Characteristics:**
- No timeline pressure
- No specific outcome required
- May inform future projects
- Kept for inspiration or reference

**Examples:**
- "Rust Programming" → tutorials, articles, code examples
- "ADHD Research" → papers, treatment protocols
- "UI/UX Patterns" → design inspiration, component libraries

### Archives

**Definition:** Inactive items from Projects, Areas, or Resources.

**Characteristics:**
- No longer active
- Kept for reference only
- Date-stamped for organization
- Rarely accessed

**Structure:**
```
Archive/
├── 2025/
│   ├── Q1/
│   │   └── ProjectName/
│   └── Q2/
└── 2026/
```

## How to Categorize

### Decision Tree

1. **Does it have a deadline or clear completion point?**
   - YES → It's a **Project**
   - NO → Continue to #2

2. **Is it something you need to maintain to a standard?**
   - YES → It's an **Area**
   - NO → Continue to #3

3. **Is it reference material or a topic of interest?**
   - YES → It's a **Resource**
   - NO → Continue to #4

4. **Is it no longer active?**
   - YES → It's **Archive**
   - NO → Reconsider if it actually fits into one of the above

## Maintenance Rituals

### Weekly Review
- Review active Projects for progress
- Archive completed Projects
- Update Areas as needed
- Clean up obsolete drafts

### Monthly Review
- Assess Area standards
- Review Resources for relevance
- Archive inactive items
- Promote reusable insights from completed Projects to Areas/Resources

### Quarterly Review
- Review all four categories
- Major cleanup of Archives
- Reassess Areas for changes in responsibility
- Prune Resources that are no longer relevant

## Common Mistakes

1. **Treating Projects as Areas**
   - Symptom: Projects that never end
   - Fix: Add a clear completion criterion or deadline

2. **Treating Areas as Projects**
   - Symptom: Feeling like you never complete your work
   - Fix: Recognize that Areas are ongoing; set specific Projects within them

3. **Hoarding in Resources**
   - Symptom: Hundreds of saved articles never read
   - Fix: Regular pruning; if you haven't used it in 6 months, archive it

4. **Not Archiving**
   - Symptom: Cluttered workspace with too many inactive items
   - Fix: Weekly archiving of completed Projects

## Separation of Concerns

**Company-wide SOPs** → Areas (`Operations/Legal`)

**Evergreen research** → Resources (`AI-Avatar/Compliance`)

**Finished artifacts** → Archives (timestamped)

**Active work** → Projects (with clear end dates)

## Integration with GTD

PARA provides the **organizational structure**.

GTD provides the **execution workflow**.

- GTD's "Projects" list maps to PARA Projects
- GTD's "Next Actions" come from active PARA Projects
- GTD's "Someday/Maybe" can live in PARA Resources
- GTD's "Reference" maps to PARA Resources and Archives
