# Project Properties Schema

<!-- Notion Database Reference -->
<!-- Database: Q1 Projects | 2026 -->
<!-- URL: https://www.notion.so/mindamyers/Q1-Projects-2026-3173caf373e0816d8f32dce784c1346f -->
<!-- Data Source ID: collection://3173caf3-73e0-81d0-9628-000bac03a5a4 -->

## Property Definitions

When creating or updating projects in the Q1 Projects | 2026 database, use these properties:

```json
{
  "Task/Project Name": "P | Project Title Here",
  "Objective": "What this project accomplishes",
  "Project Title": "Short title",
  "Status": "Committed & Not Started",
  "Priority": "Medium",
  "Category": "⚪ Other",
  "Tags": ["Planning"],
  "Progress": 0,
  "date:Start Date:start": "2026-03-09",
  "date:Start Date:is_datetime": 0,
  "date:End Date:start": "2026-03-10",
  "date:End Date:is_datetime": 0,
  "Next": "First action to take",
  "Dependencies": ""
}
```

## Property Options

### Status (Select - Required)

- **"Committed & Not Started"** (default) - Project approved but work hasn't begun
- **"Backlog"** - Future project, not yet committed
- **"In Progress"** - Active work happening
- **"On Hold"** - Paused temporarily
- **"Delayed"** - Behind schedule
- **"Completed"** - Finished and delivered

### Priority (Select - Required)

- **"High"** - Critical, time-sensitive, or high impact
- **"Medium"** (default) - Standard priority
- **"Low"** - Nice to have, can wait

### Category (Select - Required)

- **"🔵 Job Search"** - Job applications, interviews, career
- **"🟣 AI Safety"** - AI safety research and projects
- **"🤖 Agentic AI"** - Autonomous agent development
- **"🟢 WellAware"** - WellAware project work
- **"📚 Learning"** - Courses, reading, skill development
- **"✍️ Writing"** - Blog posts, articles, documentation
- **"🩷 Personal"** - Personal projects and goals
- **"⚪ Other"** (default) - Doesn't fit other categories
- **"🟤 Deadlines"** - Time-critical deliverables

### Tags (Multi-select - Optional)

Can select multiple:

- **"Urgent"** - Immediate attention required
- **"Review"** - Needs review or feedback
- **"Planning"** (default) - Still in planning phase
- **"Execution"** - Active execution phase
- **"Milestone"** - Key milestone or deliverable
- **"Recurring"** - Repeating project or ritual

### Progress (Number - Optional)

- Value: 0-100 (percentage complete)
- Default: 0
- Update as work progresses

### Dates (Date - Optional)

**Start Date:**
- Property: `date:Start Date:start`
- Format: `"YYYY-MM-DD"`
- Is datetime: `0` (date only, not timestamp)

**End Date:**
- Property: `date:End Date:start`
- Format: `"YYYY-MM-DD"`
- Is datetime: `0` (date only, not timestamp)

### Next (Text - Recommended)

- Immediate next action to take
- Should be concrete and actionable
- Example: "Read the paper: https://arxiv.org/abs/2602.16666"

### Dependencies (Text - Optional)

- What this project depends on
- Other projects, people, or external factors
- Can be simple text or links

## Common Property Combinations

### New Project (Planning Phase)
```json
{
  "Status": "Committed & Not Started",
  "Priority": "Medium",
  "Tags": ["Planning"],
  "Progress": 0
}
```

### Urgent Active Project
```json
{
  "Status": "In Progress",
  "Priority": "High",
  "Tags": ["Execution", "Urgent"],
  "Progress": 35
}
```

### Learning/Research Project
```json
{
  "Status": "In Progress",
  "Priority": "Medium",
  "Category": "📚 Learning",
  "Tags": ["Planning", "Review"],
  "Progress": 0
}
```

### Deadline-Driven Project
```json
{
  "Status": "In Progress",
  "Priority": "High",
  "Category": "🟤 Deadlines",
  "Tags": ["Execution", "Urgent"],
  "date:End Date:start": "2026-03-30"
}
```
