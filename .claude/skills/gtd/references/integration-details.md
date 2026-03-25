# GTD Integration Details

Detailed integration information for Notion, PARA, and conversational history systems.

## Notion MCP Integration

**CRITICAL:** The Notion Q1 Projects | 2026 database is the **source of truth** for all projects.

### When Planning, GTD Skill:

1. **Fetches active projects** from Notion Q1 Projects database
2. **Checks project status** (In Progress, Committed & Not Started)
3. **Reviews deadlines** (End Date property)
4. **Reads progress** (Progress % property)
5. **Gets next actions** (Next property)
6. **Reads priority** (Priority property: High/Medium/Low)

### Notion MCP Permissions

This skill uses **Notion MCP** to:

- ✅ Read your Q1 Projects database
- ✅ View project statuses and progress
- ✅ Check deadlines and schedules
- ✅ **Create weekly planning pages** (when doing `/gtd visualize-week`)
- ❌ **NOT write todos automatically** (only when you explicitly request)

**Important:** The skill will NOT create random tasks in Notion. It will only write when you explicitly ask. This prevents accumulation of noise that degrades signal quality.

### Notion Database Schema

Expected properties in Q1 Projects database:

| Property | Type | Purpose |
|----------|------|---------|
| Task/Project Name | Title | Project identifier |
| Status | Select | In Progress, Committed & Not Started, etc. |
| Priority | Select | High, Medium, Low |
| End Date | Date | Deadline for completion |
| Progress | Number | % complete (0-100) |
| Next | Text | Next action/task |
| Category | Select | 🔵 Job Search, 🟣 AI Safety, etc. |
| Tags | Multi-select | Urgent, Execution, etc. |

## Local PARA Projects vs. Notion-Only Projects

**Notion is always the source of truth.** Local PARA project folders are **optional**.

### Create Local PARA Project Folder When:

- ✅ Project has significant local files (code, designs, large downloads)
- ✅ Need to track local work separately from Notion
- ✅ Multiple people collaborating with local artifacts
- ✅ Project requires local directory structure (e.g., software projects)

### Skip Local PARA Folder When:

- ❌ Project lives entirely in Notion (meetings, planning, research)
- ❌ All deliverables are in Notion or external systems
- ❌ No local file artifacts needed
- ❌ Project is purely coordination/planning

### Examples:

- **Job Board MVP** → Has local folder (code in `app/web/`, database files)
- **Weekly planning** → No local folder (lives in Notion + markdown cache)
- **Meeting prep** → No local folder (all in Notion)
- **BlueDot project** → Has local folder (`personal/projects/bluedot-ai-safety-project/`)

## Priority Tracking System

### How Priorities Are Shown in Visualizations

Projects from Notion have a **Priority** property (High/Medium/Low). The GTD skill uses this to:

**In visualizations:**
- **Size/prominence**: High priority projects shown larger or first
- **Color coding**: 🔴 High, 🟡 Medium, ⚪ Low (in terminal descriptions)
- **Sort order**: Priority × momentum (high priority + high momentum = top)

**In tradeoff analysis:**
- High-priority projects appear in more allocation options
- Delaying high-priority items shown as explicit cost
- Priority mismatches flagged (high priority but low allocation)

### Priority × Momentum Matrix

When showing active threads, consider both priority and momentum:

```
                 High Momentum    Low Momentum
High Priority    🎯 Do First      ⚠️  Why stuck?
Low Priority     🤔 Reconsider?   ⏸️  Pause/Archive
```

**Interpretation:**

- **🎯 Do First**: High priority + high momentum = optimal state, continue
- **⚠️ Why stuck?**: High priority but low momentum = investigate blockers
- **🤔 Reconsider?**: Low priority but high momentum = check if priority is wrong
- **⏸️ Pause/Archive**: Low priority + low momentum = consider pausing

### Momentum Calculation

Momentum is calculated from conversational history:

- **High**: Worked on 4+ of last 7 days
- **Medium**: Worked on 2-3 of last 7 days
- **Low**: Worked on 0-1 of last 7 days

Factors that increase momentum:
- Consecutive days of work (multiplier effect)
- Recent completion of milestones
- Active decisions and unblocking

Factors that decrease momentum:
- Long gaps between work sessions
- Repeated mentions of same blockers
- Context switches to other projects

## Weekly Planning Output Locations

### Markdown Cache (Optional)

Weekly planning can optionally create a local markdown file:

**Location:** `personal/areas/productivity/weekly-plans/`
**Naming:** `2026-W{week-number}-{month}-{day}.md`
**Example:** `2026-W12-Mar-23.md`

**Purpose:**
- Quick reference without opening Notion
- Version control of planning decisions
- Offline access
- Historical record of weekly plans

### Notion Planning Pages

When using `/gtd visualize-week`, optionally create a Notion page:

**Location:** Copy of "Researching TEMPLATE" in Notion
**Title:** `Week {dates}: Planning`
**Example:** `Week Mar 23-29: Planning`

**Contents:**
- Weekly visualization (ASCII art as code block)
- Active threads summary
- Tradeoff analysis (if generated)
- Decisions and rationale

## PARA Integration

The GTD skill uses PARA as its organizational foundation:

- **Active Projects** (from PARA) → Weekly planning input
- **Areas** (from PARA) → Source of ongoing responsibilities
- **Resources** (from PARA) → Reference when needed for tasks
- **Archives** (from PARA) → Ignore unless specifically relevant

**Reference:** `.claude/skills/para/references/para-structure-guide.md`

## Integration Testing Checklist

When modifying GTD skill, verify:

- [ ] Conversational history queries return expected results
- [ ] Notion MCP can read Q1 Projects database
- [ ] Priority values are correctly extracted
- [ ] Momentum calculations match recent work
- [ ] Tradeoff visualizations render correctly
- [ ] Reference links resolve correctly
- [ ] Weekly planning output is created in correct location
