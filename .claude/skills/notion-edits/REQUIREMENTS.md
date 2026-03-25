# Notion MCP Requirements

This document outlines what we needed to ensure Notion MCP operations work properly.

## Critical Prerequisites

### 1. Notion MCP Server Authentication

**The Issue**: The Notion MCP server must be authenticated before any operations work.

**Check Status**:
```bash
claude mcp list
```

**Expected Output**:
```
notion: https://mcp.notion.com/mcp (HTTP) - ✓ Connected
```

**If You See**: `⚠ Needs authentication`

**Fix**: Run this command (user must do this manually):
```bash
claude mcp
```

**What This Does**:
- Triggers authentication flow
- Reconnects to Notion MCP server
- Output: "Authentication successful. Reconnected to notion."

**CRITICAL**: Do NOT attempt any Notion operations until status shows "✓ Connected"

### 2. MCP Tool Permissions

**Location**: `.claude/settings.local.json`

**Required Permissions** (already configured):
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

**These tools are allowed without asking for permission**, enabling smooth Notion workflows.

## What We Learned

### Working Pattern: Two-Step Process for Adding Content

**Goal**: Add research synthesis to existing meeting prep page

**What DIDN'T Work**:
- ❌ Direct tool invocation from bash (`claude mcp call`)
- ❌ Using Task agents (they don't have MCP tool access in this context)
- ❌ Python scripts trying to invoke MCP tools directly

**What WORKED**: ✅ Direct MCP tool function calls

```
Step 1: Create child page with full content
  mcp__notion__notion-create-pages
    parent: {"page_id": "parent-page-id"}
    pages: [{
      "properties": {"title": "Child Page Title"},
      "content": "Full detailed content..."
    }]

Step 2: Add summary to parent with link
  mcp__notion__notion-update-page
    page_id: "parent-page-id"
    command: "update_content"
    content_updates: [{
      old_str: "# Existing Section",
      new_str: "# New Summary\n\nSummary...\n\n**Full** → <page url=\"...\">\n\n# Existing Section"
    }]
```

### Key Constraints

#### 1. Child Page Preservation

**The Issue**: When using `update_content`, if the `old_str` contains a child page reference but `new_str` doesn't, Notion MCP throws validation error.

**Error Message**:
```
"This operation would delete 1 child page(s) or database(s)"
```

**Solution Options**:

**Option A**: Include child page in `new_str`
```markdown
old_str: "# Section\n<page url=\"child-url\">Child</page>"
new_str: "# Section\n\nNew content\n\n<page url=\"child-url\">Child</page>"
```

**Option B**: Insert content in different location
```markdown
old_str: "---\n# Section Before Child"
new_str: "---\n\n# New Section\n\n---\n# Section Before Child"
```

**Option C**: Use `allow_deleting_content: true` (dangerous!)
```
Only use if you genuinely want to delete child pages
```

#### 2. Exact String Matching for update_content

**The Issue**: `old_str` must match content EXACTLY, including whitespace and newlines.

**What Works**:
```markdown
old_str: "---\n# Open Questions"
```

**What Doesn't Work**:
```markdown
old_str: "---\n\n# Open Questions"  # Extra newline
old_str: "--- # Open Questions"     # Missing newline
```

**Best Practice**:
1. Fetch the page first
2. Copy exact content from fetch output
3. Don't include line numbers from fetch output

#### 3. Template Usage

**Creating from Template**: Use `template_id` parameter

```
mcp__notion__notion-create-pages
  parent: {"data_source_id": "collection-id"}
  pages: [{
    "template_id": "template-page-id",
    "properties": {
      "title": "New Project Name"
    }
  }]
```

**Note**: Don't include `content` when using `template_id` - the template provides it.

**For custom content**: Skip `template_id`, provide full `content` instead.

## Common Workflows

### Workflow 1: Replace Entire Page Content

**Use Case**: Complete rewrite, template population

```
mcp__notion__notion-update-page
  page_id: "page-id"
  command: "replace_content"
  new_str: "# Complete New Content\n\n..."
```

**Constraint**: None - replaces everything

### Workflow 2: Update Specific Section

**Use Case**: Add section, modify content, preserve structure

```
mcp__notion__notion-update-page
  page_id: "page-id"
  command: "update_content"
  content_updates: [{
    old_str: "exact existing content",
    new_str: "updated content"
  }]
```

**Constraint**: Must preserve child pages or include them in new_str

### Workflow 3: Create Child + Link from Parent

**Use Case**: Add detailed content as child page, summary in parent

```
# Step 1: Create child
child_result = mcp__notion__notion-create-pages(...)

# Step 2: Fetch parent to see structure
parent_content = mcp__notion__notion-fetch(id="parent-id")

# Step 3: Add summary with link
mcp__notion__notion-update-page(
  page_id="parent-id",
  command="update_content",
  content_updates=[{
    old_str: "find safe insertion point",
    new_str: "summary + <page url=\"child-url\">link</page> + old content"
  }]
)
```

**Constraint**: Find insertion point that doesn't conflict with existing child pages

## Debugging Steps

### Issue: MCP Tools Not Working

**Check 1**: Is Notion MCP connected?
```bash
claude mcp list
# Look for "✓ Connected"
```

**Check 2**: Are tools in permissions?
```bash
cat .claude/settings.local.json
# Look for mcp__notion__ tools in "allow" array
```

**Check 3**: Is authentication valid?
```bash
claude mcp
# Should show "Authentication successful"
```

### Issue: Validation Error on Update

**Check 1**: Are you deleting child pages?
```
Fetch the page, look for <page url="..."> tags
Include them in new_str or change insertion point
```

**Check 2**: Does old_str match exactly?
```
Fetch the page, copy exact content
Don't include line numbers from output
```

**Check 3**: Are properties valid?
```
Check property options match database schema
Use exact option names (case-sensitive)
```

### Issue: Created Page Doesn't Match Template

**Check 1**: Did you use template_id?
```
Include template_id in create-pages call
```

**Check 2**: Did you provide content?
```
Don't provide content when using template_id
Template content applies automatically
```

## Success Indicators

When everything is working correctly:

✅ `claude mcp list` shows "✓ Connected"
✅ MCP tool calls return `{"page_id": "..."}` on success
✅ Created pages appear in Notion immediately
✅ Updated content reflects in Notion without errors
✅ Child pages are preserved when updating parent

## Example: Complete Working Flow

This is the exact flow that worked for adding research synthesis to meeting prep:

```
# 1. Check authentication
claude mcp list
# Output: notion: ... - ✓ Connected ✓

# 2. Create child page with full synthesis
mcp__notion__notion-create-pages(
  parent={"page_id": "31f3caf373e081d9a0d8cd8b1c9f3639"},
  pages=[{
    "properties": {"title": "Research Synthesis: AI Agent Reliability (Full)"},
    "content": "... 11,590 characters of synthesis ..."
  }]
)
# Returns: {"pages":[{"id":"31f3caf373e081618ca7efc8de8a890d",...}]}

# 3. Fetch parent to verify structure
mcp__notion__notion-fetch(id="31f3caf373e081d9a0d8cd8b1c9f3639")
# Check: Child page appears at bottom
# Find: Safe insertion point before "# Open Questions"

# 4. Add summary section with link
mcp__notion__notion-update-page(
  page_id="31f3caf373e081d9a0d8cd8b1c9f3639",
  command="update_content",
  content_updates=[{
    old_str="---\n# Open Questions",
    new_str="---\n\n# 📋 Research Synthesis Summary\n\n::: callout {icon=\"🔬\" color=\"blue_bg\"}\n...\n:::\n\n---\n# Open Questions"
  }]
)
# Returns: {"page_id":"31f3caf373e081d9a0d8cd8b1c9f3639"}

# 5. Success! Both pages updated correctly
```

## Summary

**What's Required**:
1. Notion MCP authenticated (`claude mcp`)
2. MCP tools in permissions (already configured)
3. Direct tool invocation (not bash/Task agents)

**Key Constraints**:
1. Preserve child pages in updates
2. Match old_str exactly
3. Use correct property values

**Working Pattern**:
1. Create child page with full content
2. Fetch parent to find safe insertion point
3. Update parent with summary + link

**This pattern works reliably** for adding detailed content to project pages.
