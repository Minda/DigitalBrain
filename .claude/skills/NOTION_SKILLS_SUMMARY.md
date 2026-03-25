# Notion Skills Summary

Documentation of the new Notion skills created and what we learned about working with Notion MCP.

## Skills Created

### 1. notion-edits
**Location**: `.claude/skills/notion-edits/`

**Purpose**: Complete workflow for updating and editing existing Notion pages

**Key Features**:
- Three update patterns: replace_content, update_content, create child + link
- Notion-flavored markdown reference
- Common errors and solutions
- Child page preservation strategies

**Files**:
- `SKILL.md` - Main skill documentation
- `REQUIREMENTS.md` - Technical requirements and what we learned

### 2. notion-projects
**Location**: `.claude/skills/notion-projects/`

**Purpose**: Create and manage project pages in Q1 Projects | 2026 database

**Key Features**:
- Standard project template structure
- Property schema reference
- Database location tracking
- Integration with research-synthesis skill

**Files**:
- `SKILL.md` - Main skill documentation
- `REFERENCE.md` - Quick reference for IDs, properties, examples

## What We Needed for Success

### Critical Requirement: Authentication

**The Problem**: Notion MCP tools don't work unless the server is authenticated.

**The Solution**: User must run `claude mcp` when they see "⚠ Needs authentication"

**How to Check**:
```bash
claude mcp list
```

**Expected Output**:
```
notion: https://mcp.notion.com/mcp (HTTP) - ✓ Connected
```

### Working Pattern: Direct MCP Tool Invocation

**What Worked**: ✅ Direct function calls to MCP tools
```
mcp__notion__notion-create-pages(...)
mcp__notion__notion-update-page(...)
mcp__notion__notion-fetch(...)
```

**What Didn't Work**:
- ❌ Bash commands (`claude mcp call`)
- ❌ Task agents (they don't have MCP tool access)
- ❌ Python scripts invoking MCP tools

### Key Constraint: Child Page Preservation

**The Issue**: When updating content that contains child page links, you must preserve them or Notion MCP throws a validation error.

**Solutions**:
1. Include child pages in `new_str`: `<page url="...">`
2. Insert content in a different location that doesn't affect child pages
3. Use `allow_deleting_content: true` (only if you actually want to delete)

## Successful Workflow Example

This is the exact pattern that worked for adding research synthesis to meeting prep:

```
Step 1: Create child page with full content
  mcp__notion__notion-create-pages
    parent: {"page_id": "parent-id"}
    pages: [{
      properties: {"title": "Full Synthesis"},
      content: "... complete detailed content ..."
    }]

Step 2: Fetch parent to see structure
  mcp__notion__notion-fetch(id: "parent-id")
  # Check for child pages, find safe insertion point

Step 3: Add summary section with link to child
  mcp__notion__notion-update-page
    page_id: "parent-id"
    command: "update_content"
    content_updates: [{
      old_str: "---\n# Existing Section",
      new_str: "---\n\n# Summary\n\nKey points...\n\n**Full** → <page url=\"child-url\">\n\n---\n# Existing Section"
    }]
```

**Result**: Parent page has summary, child page has full details, everything preserved correctly.

## Database Reference

### Q1 Projects | 2026
- **Data Source ID**: `collection://3173caf3-73e0-81d0-9628-000bac03a5a4`
- **Database URL**: https://www.notion.so/3173caf373e081e58893dfbd0787f2a0
- **Template**: "P | PROJECT_TEMPLATE" (`31f3caf373e08041a6c0db48b2a0bb2b`)

### Standard Properties
- **Task/Project Name**: "P | <name>" (title)
- **Status**: "Committed & Not Started", "In Progress", "Completed", etc.
- **Category**: Job Search, AI Safety, Learning, Writing, Personal, Other, etc.
- **Priority**: High, Medium, Low
- **Tags**: Planning, Urgent, Review, Execution, etc.
- **Dates**: Start Date, End Date (use `date:Property:start` format)

## Integration Example: Research Synthesis + Project

Complete workflow combining **research-synthesis** + **notion-projects** + **notion-edits**:

```
1. User asks to analyze paper for meeting prep

2. Create project page (notion-projects):
   - Task/Project Name: "P | Paper Discussion — AI Reliability"
   - Category: "📚 Learning"
   - Standard template structure

3. Run research synthesis (research-synthesis skill):
   - Download paper
   - Multi-agent analysis
   - Generate synthesis + audio version

4. Add synthesis to project (notion-edits):
   - Create child page with full synthesis
   - Add summary section to project page
   - Link child page from summary

5. Result: Project page ready for meeting prep
   - Objectives, goals, TODOs in main page
   - Summary of key findings visible
   - Link to full detailed synthesis
```

**Live Example**:
- Project: https://www.notion.so/31f3caf373e081d9a0d8cd8b1c9f3639
- Full Synthesis Child: https://www.notion.so/31f3caf373e081618ca7efc8de8a890d

## Permissions Configuration

Already configured in `.claude/settings.local.json`:

```json
{
  "permissions": {
    "allow": [
      "mcp__notion__notion-create-pages",
      "mcp__notion__notion-fetch",
      "mcp__notion__notion-update-page",
      "mcp__notion__notion-search"
    ]
  }
}
```

These tools run without asking permission, enabling smooth workflows.

## Common Pitfalls and Solutions

### Pitfall 1: MCP Not Authenticated
**Symptom**: Tools fail silently or return authentication errors
**Solution**: Run `claude mcp` to reconnect

### Pitfall 2: Child Pages Deleted Accidentally
**Symptom**: Validation error about deleting child pages
**Solution**: Include child pages in `new_str` or change insertion point

### Pitfall 3: old_str Doesn't Match
**Symptom**: Validation error, "content not found"
**Solution**: Fetch page first, copy exact content including whitespace

### Pitfall 4: Invalid Property Values
**Symptom**: Validation error on create/update
**Solution**: Use exact property names from schema (see REFERENCE.md)

### Pitfall 5: Template Content Not Applying
**Symptom**: Created page is blank or missing template content
**Solution**: Don't include `content` when using `template_id`

## Future Database Locations

When adding more project databases, update both skills:

**In notion-projects SKILL.md**:
- Add new database section with data_source_id
- Document property schema
- Add usage examples

**In notion-projects REFERENCE.md**:
- Add database ID to quick reference
- Document any unique properties
- Add example projects

## Related Skills

- **fetching-notion-content**: Search and retrieve Notion content
- **research-synthesis**: Multi-agent research analysis
- **agents-spinning-up**: Agent calibration (used by research-synthesis)
- **agent-customizing-content**: Personalization (used by research-synthesis)

## Summary

**New capabilities enabled**:
1. ✅ Create project pages from templates
2. ✅ Update existing pages with new content
3. ✅ Add child pages with detailed content
4. ✅ Link child pages from parent summaries
5. ✅ Preserve existing structure while adding new sections

**Technical foundation**:
- Notion MCP server authentication
- Direct tool invocation pattern
- Child page preservation strategies
- Exact string matching for updates

**Documented workflows**:
- Replace entire page content
- Surgical content updates
- Create child + link from parent
- Integrate research synthesis with projects

**All patterns tested and working** on real project: AI Agent Reliability meeting prep.
