# Condensing Techniques for Skills

How to reduce token count while improving clarity.

## Core Strategies

### 1. Progressive Disclosure Pattern

**Move verbose content to subfolders:**
- `references/` - Detailed documentation, examples, technical specs
- `scripts/` - Executable code, automation tools
- `templates/` - Reusable file templates
- `examples/` - Complete example workflows

**Main SKILL.md should:**
- Contain only essential instructions
- Reference detailed docs with clear paths
- Keep critical warnings/caveats visible
- Target <1,000 words (<1,500 tokens)

**Example transformation:**

Before (120 lines):
```markdown
### How to Rename

First, you need to understand that conversation files are stored as JSONL...
Each line is a JSON object...
The customTitle field can appear in multiple locations...

Here's the complete Python code:
```python
import json
from pathlib import Path
# ... 80 lines of code ...
```

After you run this, you should verify...
```

After (8 lines):
```markdown
### Rename Conversation

**⚠️ CRITICAL**: Requires updating metadata + adding custom-title entry

**Always use**: `python3 rename_conversation.py "Title"`

See `references/rename-implementation.md` for technical details.
```

### 2. Front-Load Critical Information

Put the most important info first in each section:
1. **Warnings** - What will break if done wrong
2. **Quick command** - The actual thing to run
3. **Reference link** - Where to learn more

**Bad order:**
```markdown
Conversations are stored in JSONL format. The format has evolved over time.
Originally, customTitle was embedded in metadata, but now it's better to use
a dedicated custom-title object. You can read more about this in the technical
documentation. **Important**: Make sure you update both fields or it won't work.
```

**Good order:**
```markdown
**⚠️ CRITICAL**: Update both customTitle metadata AND custom-title entry

**Quick use**: `python3 rename_conversation.py "Title"`

See `references/implementation-details.md` for JSONL format evolution.
```

### 3. Bullet Points Over Prose

Replace paragraphs with scannable lists.

**Before (85 words):**
```markdown
When you're creating titles for conversations, you should think about several
factors. First, consider what actions were performed during the conversation,
such as creating, fixing, updating, or searching. Second, think about which
files or directories were touched, as this provides concrete context. Third,
identify any technologies that were used, like React, Python, or TypeScript.
Fourth, note which Claude skills were invoked. Finally, consider what the
user's original intent was when they started the conversation.
```

**After (36 words):**
```markdown
**Title generation factors:**
- Actions: create, fix, update, search
- Files/directories touched
- Technologies: React, Python, TypeScript
- Skills invoked
- User's original intent
```

### 4. Tables for Quick Reference

Use tables instead of repeated explanations.

**Before:**
```markdown
If you encounter a file walking bottleneck, consider using SQLite or JSON
indexing, which can provide 50-200x performance improvement.

When you have repeated reads of the same data, implement a caching layer,
which typically gives 10-100x speedup.

For large files, use streaming or tail reads instead of loading everything,
expect 10-50x improvement.
```

**After:**
```markdown
| Bottleneck | Solution | Expected Gain |
|------------|----------|---------------|
| File walking | SQLite/JSON index | 50-200x |
| Repeated reads | Caching layer | 10-100x |
| Large files | Streaming/tail | 10-50x |
```

### 5. Extract Examples to References

Keep 1-2 minimal examples inline, move complete examples to `references/examples.md`.

**Main SKILL.md:**
```markdown
## Usage

**Suggest titles**: "Name this conversation" → 4 intelligent options
**Rename**: "Rename to 'Project X'" → Updates title
**Search**: "Find conversations about jobs" → Matches + snippets

See `references/example-workflows.md` for complete scenarios.
```

**references/example-workflows.md:**
```markdown
# Example Workflows

## Complete Rename Flow

User: "Can we rename this conversation to 'BlueDot Course Search'?"

Assistant analyzes current conversation...
[detailed 40-line example with full output]

## Title Suggestion for Research Session

User: "Name this conversation"