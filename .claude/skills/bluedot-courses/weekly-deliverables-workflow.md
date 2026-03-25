# BlueDot Weekly Deliverables Workflow

## Quick Start

When the user asks "what do I need to do for BlueDot this week?" or "what are my BlueDot deliverables?", follow this workflow:

1. **Fetch the current project page** from Notion
2. **Extract the TODO section** and identify which session is upcoming
3. **Present deliverables** organized by priority and deadline
4. **Check for updates** in the Work Log section

## Workflow Steps

### Step 1: Fetch Project Page

```
mcp__notion__notion-fetch
  id: "https://www.notion.so/3173caf373e081dfa19ad055f38b20e4"
```

This is the main BlueDot Technical AI Safety Project page.

### Step 2: Parse TODO Section

The TODO section is organized by session:

**Session 3: Update and Iterate**
- Prepare to explain what you've tried/learned
- Write project tips and open questions
- Be ready to answer key uncertainty questions
- Document next steps after session

**Session 4: Write It Up** ⚠️ *Requires draft deliverables*
- DECISION: Which formats to produce?
- Create drafts with shareable links
- Prepare specific feedback requests
- Commit to submission plan

**Session 5: Project Demo**
- Submit final project BEFORE session
- Prepare 1-minute summary
- Have final links ready
- Write gratitude for group members

**Ongoing**
- DECISION: Apply for rapid small grant?
- Schedule mentor check-ins (weekly recommended)
- Post updates in Slack

### Step 3: Identify Current Session

Check the project properties and Work Log to determine:
- Which session is next?
- What's the deadline?
- What's already been completed?

### Step 4: Present Deliverables

Format output as:

```markdown
## BlueDot Deliverables This Week

**Upcoming Session:** [Session Number + Name]
**Deadline:** [Date if available]

### Required This Week:
- [ ] [Critical deliverables from TODO]
- [ ] [Time-sensitive items]

### Prepare For Next Session:
- [ ] [Items needed for upcoming session]

### Ongoing/Optional:
- [ ] [Long-term items]
- [ ] [Decisions to make]

### Recent Progress:
[Extract from Work Log section - latest 2-3 entries]
```

### Step 5: Check for Context

Look at these sections for additional context:
- **Work Log** - What's been done recently?
- **Key Decisions** - Any major choices made?
- **Open Questions** - What needs resolution?
- **Deliverables** callout - Overall project deliverables

## Session Timeline Reference

The course has 5 sessions over ~4 weeks:
- **Session 1:** Orientation & Project Selection
- **Session 2:** Initial Progress Check
- **Session 3:** Update and Iterate
- **Session 4:** Write It Up (requires drafts)
- **Session 5:** Final Demo (requires submission)

## Integration with Other Skills

This workflow integrates with:
- **fetching-notion-content** - Gets the latest project state
- **notion-edits** - Updates TODO items as completed
- **notion-projects** - Uses Q1 Projects structure

## Example Usage

**User asks:** "What do I need to do for BlueDot this week?"

**Response:**
1. Fetch Notion project page
2. Identify current session (e.g., Session 3)
3. Extract relevant TODOs
4. Present formatted deliverables
5. Check Work Log for recent progress
6. Highlight any urgent decisions

## Notes

- The TODO section is manually maintained in Notion - always fetch fresh
- Session dates may not be in the page - check calendar or ask user
- Some deliverables require decisions (marked with "DECISION:")
- Draft submissions need shareable links with comment permissions
