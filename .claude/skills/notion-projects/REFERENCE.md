# Notion Projects Quick Reference

## Database IDs

### Q1 Projects | 2026
- **Data Source ID**: `collection://3173caf3-73e0-81d0-9628-000bac03a5a4`
- **Database URL**: https://www.notion.so/3173caf373e081e58893dfbd0787f2a0
- **Path**: 1. PROJECTS → Q1: 2026 → Q1 Projects | 2026

### Template
- **Name**: "P | PROJECT_TEMPLATE"
- **Page ID**: `31f3caf373e08041a6c0db48b2a0bb2b`
- **URL**: https://www.notion.so/31f3caf373e08041a6c0db48b2a0bb2b

## Property Reference

### Task/Project Name (Title)
- **Format**: "P | <project-name>"
- **Example**: "P | AI Agent Reliability — Meeting Prep"

### Status Options
- "Committed & Not Started" ← default
- "Backlog"
- "In Progress"
- "On Hold"
- "Delayed"
- "Completed"

### Priority Options
- "High"
- "Medium" ← default
- "Low"

### Category Options
- "🔵 Job Search"
- "🟣 AI Safety"
- "🤖 Agentic AI"
- "🟢 WellAware"
- "📚 Learning"
- "✍️ Writing"
- "🩷 Personal"
- "⚪ Other" ← default
- "🟤 Deadlines"

### Tags Options (Multi-select)
- "Urgent"
- "Review"
- "Planning" ← default
- "Execution"
- "Milestone"
- "Recurring"

### Date Properties
```json
{
  "date:Start Date:start": "YYYY-MM-DD",
  "date:Start Date:is_datetime": 0,
  "date:End Date:start": "YYYY-MM-DD",
  "date:End Date:is_datetime": 0
}
```

### Other Properties
- **Progress**: Number (0-1, displayed as percentage)
- **Objective**: Text (what project accomplishes)
- **Project Title**: Text (short title)
- **Next**: Text (immediate next action)
- **Dependencies**: Text (what this depends on)

## Quick Create Template

```
mcp__notion__notion-create-pages(
  parent={"data_source_id": "3173caf3-73e0-81d0-9628-000bac03a5a4"},
  pages=[{
    "properties": {
      "Task/Project Name": "P | <PROJECT NAME>",
      "Objective": "<WHAT IT ACCOMPLISHES>",
      "Project Title": "<SHORT TITLE>",
      "Status": "Committed & Not Started",
      "Priority": "Medium",
      "Category": "⚪ Other",
      "Tags": ["Planning"],
      "Progress": 0,
      "date:Start Date:start": "YYYY-MM-DD",
      "date:Start Date:is_datetime": 0,
      "date:End Date:start": "YYYY-MM-DD",
      "date:End Date:is_datetime": 0,
      "Next": "<FIRST ACTION>"
    },
    "content": "... see SKILL.md for full template ..."
  }]
)
```

## Example Projects

### Meeting Prep Project
- **ID**: `31f3caf373e081d9a0d8cd8b1c9f3639`
- **Name**: "P | Toward a Science of AI Agent Reliability — Meeting Prep"
- **Category**: "⚪ Other"
- **Has child page**: Research Synthesis (Full)
- **Structure**: Standard template with summary section + child page link

### BlueDot Technical AI Safety
- **ID**: `3173caf373e081dfa19ad055f38b20e4`
- **Name**: "P | BlueDot: Technical AI Safety Project"
- **Category**: "🟣 AI Safety"

### BlueDot Governance
- **ID**: `3173caf373e0812d8f63e3fc6c6f6eca`
- **Name**: "P | BlueDot: Frontier AI Governance"
- **Category**: "🟣 AI Safety"

## Common Commands

### Search for project
```
mcp__notion__notion-search(
  query="project name",
  data_source_url="collection://3173caf3-73e0-81d0-9628-000bac03a5a4"
)
```

### Fetch project details
```
mcp__notion__notion-fetch(id="page-id-or-url")
```

### Create new project
See Quick Create Template above

### Update project
```
mcp__notion__notion-update-page(
  page_id="page-id",
  command="update_content",
  content_updates=[{...}]
)
```

## Naming Conventions

- **Projects**: "P | <Name>"
- **Learning**: "[L] <Name>" (uses different template)
- **Features**: "[F] <Name>" (uses different template)
- **Templates**: "_TEMPLATE_" suffix

## Related Databases

The Q1 Projects database has relations to:
- **Blocked by**: Other projects blocking this one
- **Blocking**: Other projects this one blocks
- **Parent item**: Parent project (for sub-projects)
- **Sub-item**: Child projects

All use the same data source: `collection://3173caf3-73e0-81d0-9628-000bac03a5a4`
