---
name: notion-edits
description: Update and edit existing Notion pages using MCP tools. Use when user asks to update, modify, or add content to Notion pages. Handles content updates, page replacements, and child page creation.
allowed-tools: [mcp__notion__notion-fetch, mcp__notion__notion-update-page, mcp__notion__notion-create-pages]
---

# Editing Notion Pages

Complete workflow for updating existing Notion pages using the Notion MCP tools.

## Prerequisites

**CRITICAL**: The Notion MCP server must be authenticated and connected.

**Check connection status**:
```bash
claude mcp list
```

**Expected output**: `notion: https://mcp.notion.com/mcp (HTTP) - ✓ Connected`

**If you see "⚠ Needs authentication"**, the user must run:
```bash
claude mcp
# This will trigger authentication and reconnect
```

**DO NOT proceed** with Notion operations until the server shows "✓ Connected".

## Three Update Patterns

### Pattern 1: Replace Entire Page Content

Use when you want to completely replace a page's body with new content.

```
mcp__notion__notion-update-page
  page_id: "page-id-here"
  command: "replace_content"
  new_str: "# New Content\n\nComplete new markdown content..."
```

**Use case**: Template pages, complete rewrites, fresh content

**Example**: Creating a new project page from a template

### Pattern 2: Surgical Content Updates

Use when you want to update specific sections while preserving the rest.

```
mcp__notion__notion-update-page
  page_id: "page-id-here"
  command: "update_content"
  content_updates: [
    {
      old_str: "# Old Section\nOld content here",
      new_str: "# Updated Section\nNew content here"
    }
  ]
```

**CRITICAL CONSTRAINT**: If the page has child pages or databases, you MUST include them in `new_str` using `<page url="...">` or `<database url="...">` tags, OR the update will fail with a validation error.

**Use case**: Adding sections, updating specific content, preserving most of the page

**Example**: Adding a summary section while keeping existing structure

### Pattern 3: Create Child Page + Add Summary

Use when you want to add detailed content as a child page and link to it from the parent.

**Step 1: Create child page**
```
mcp__notion__notion-create-pages
  parent: {"page_id": "parent-page-id"}
  pages: [{
    "properties": {"title": "Child Page Title"},
    "content": "# Full detailed content\n\n..."
  }]
```

**Step 2: Fetch parent page**
```
mcp__notion__notion-fetch
  id: "parent-page-id"
```

Check for existing child pages in the output (look for `<page url="...">` tags).

**Step 3: Add summary to parent**
```
mcp__notion__notion-update-page
  page_id: "parent-page-id"
  command: "update_content"
  content_updates: [{
    old_str: "# Existing Section",
    new_str: "# New Summary Section\n\nSummary content...\n\n**Full details** → <page url=\"child-page-url\">Child Page Title</page>\n\n# Existing Section"
  }]
```

**Use case**: Research synthesis, detailed analysis, meeting prep with full notes

**Example**: Adding research synthesis to meeting prep page (what we just did!)

## Notion-Flavored Markdown

Notion uses enhanced markdown. Key features:

### Headers
```markdown
# Heading 1
## Heading 2
### Heading 3
```

### Callouts
```markdown
::: callout {icon="🔬" color="blue_bg"}
### Title
---
Content here
:::
```

**Colors**: `gray_bg`, `blue_bg`, `green_bg`, `yellow_bg`, `red_bg`, `purple_bg`, `pink_bg`, `brown_bg`

**Icons**: Use emoji or `/icons/name_gray.svg`

### Columns
```markdown
<columns>
  <column>
    Content in first column
  </column>
  <column>
    Content in second column
  </column>
</columns>
```

### Links to Pages/Databases
```markdown
<page url="https://www.notion.so/page-id">Page Title</page>
<database url="https://www.notion.so/database-id">Database Name</database>
```

### Dividers
```markdown
---
```

### Lists
```markdown
- Bullet item
- Another item

1. Numbered item
2. Another numbered item

- [ ] Todo item unchecked
- [x] Todo item checked
```

### Text Formatting
```markdown
**bold**
*italic*
`inline code`
~~strikethrough~~
```

### Blockquotes
```markdown
> Quote text
> Multiple lines
```

## Workflow: Update Existing Page

### Step 1: Fetch Current Content

Always fetch first to see what you're working with:

```
mcp__notion__notion-fetch
  id: "page-id-or-url"
```

**Extract from output**:
- Current content structure
- Existing child pages (look for `<page url="...">` tags)
- Page title and properties

### Step 2: Determine Update Strategy

**Questions to ask**:
1. Replace entire content or update specific sections?
2. Are there child pages/databases to preserve?
3. Should new content be a child page or inline?

**Decision tree**:
- **Complete rewrite + no children** → Use `replace_content`
- **Complete rewrite + has children** → Use `replace_content`, include children in `new_str`
- **Add/update sections** → Use `update_content`
- **Add detailed content** → Create child page, then add summary link

### Step 3: Execute Update

Choose the appropriate pattern (see above).

### Step 4: Verify

Optionally fetch the page again to confirm changes, or provide the Notion URL to the user.

## Common Errors and Solutions

### Error: "This operation would delete N child page(s)"

**Cause**: Using `update_content` where `new_str` doesn't include existing child pages.

**Solution**:
1. Fetch the page to find child page URLs
2. Include them in `new_str`: `<page url="...">`
3. OR use `allow_deleting_content: true` (dangerous!)
4. OR insert content in a different location that doesn't affect child pages

**Example fix**:
```markdown
# New Section

Summary here

---
# Old Section (don't modify this part that has the child page)
<page url="existing-child-page-url">Child Page</page>
```

### Error: "validation_error" with old_str not found

**Cause**: The `old_str` doesn't exactly match content in the page.

**Solution**:
1. Fetch the page to see exact content
2. Copy the exact string including whitespace/newlines
3. Make sure you're not including line numbers from fetch output

### Error: "⚠ Needs authentication"

**Cause**: Notion MCP server not authenticated.

**Solution**: User must run `claude mcp` to authenticate.

## Best Practices

1. **Always fetch first** - Know what you're working with
2. **Preserve child pages** - Don't accidentally delete linked content
3. **Use precise old_str** - Match content exactly for `update_content`
4. **Test on non-critical pages** - Verify approach before updating important content
5. **Provide Notion URLs** - Let user see the result
6. **Use appropriate pattern** - Don't replace when you can update

## Examples

### Example 1: Add Summary Section to Meeting Prep

```
# Fetch to see structure
mcp__notion__notion-fetch(id="page-id")

# Insert before existing section
mcp__notion__notion-update-page(
  page_id="page-id",
  command="update_content",
  content_updates=[{
    old_str="---\n# Discussion Questions",
    new_str="---\n\n# Summary\n\nKey points...\n\n---\n# Discussion Questions"
  }]
)
```

### Example 2: Create Research Synthesis Child Page

```
# Step 1: Create child page
mcp__notion__notion-create-pages(
  parent={"page_id": "parent-id"},
  pages=[{
    "properties": {"title": "Full Synthesis"},
    "content": "# Complete Analysis\n\n..."
  }]
)

# Returns: page_id and url of new page

# Step 2: Add link to parent
mcp__notion__notion-update-page(
  page_id="parent-id",
  command="update_content",
  content_updates=[{
    old_str="# Notes",
    new_str="# Notes\n\n**Full synthesis** → <page url=\"new-page-url\">Full Synthesis</page>"
  }]
)
```

### Example 3: Replace Template Content

```
# Get template ID from database
mcp__notion__notion-fetch(id="database-id")
# Look in <templates> section for template_id

# Create new page from template
mcp__notion__notion-create-pages(
  parent={"data_source_id": "collection-id"},
  pages=[{
    "template_id": "template-id",
    "properties": {
      "Task Name": "My Project"
    }
  }]
)

# Then replace placeholder content
mcp__notion__notion-update-page(
  page_id="new-page-id",
  command="replace_content",
  new_str="# My Project\n\nActual content..."
)
```

## Related Skills

- **fetching-notion-content**: Search and retrieve Notion pages
- **notion-projects**: Create and manage project pages in Q1 Projects database
