# GTD Implementation Guide

Technical details for implementing the GTD skill's core workflows.

## How to Access Recent Context

When the GTD skill is invoked, it should:

### 1. First, Check Conversational History

```python
# Use the conversational-history skill
from skills.conversational_history import ConversationIndex

index = ConversationIndex()
index.connect()

# Get last 7 days
recent = index.search_recent(hours=168)

# Get today only
today = index.search_recent(hours=24)

# Get last 3 hours (for daily planning)
last_3h = index.search_recent(hours=3)
```

### 2. Then, Get Conversation Titles for Context

```python
# Use conversations-manage to see titles
from skills.conversations_manage import list_recent_conversations

recent_convos = list_recent_conversations(limit=10)
```

### 3. Finally, Check Notion (if needed)

```python
# Use Notion MCP to get formal project tracking
# Only after understanding recent work context
```

## What to Extract from Recent Conversations

From the conversational history, identify:

- **Active projects** (mentioned multiple times in last 7 days)
- **Recent accomplishments** (what got completed)
- **Current blockers** (problems discussed but not resolved)
- **Decisions made** (agreements or choices)
- **Momentum patterns** (what's getting consistent attention)
- **Context switches** (how often focus changes between projects)

## Short List from Conversational-History

The conversational-history skill provides a **short list** of recent activity organized by day. This is the PRIMARY source for understanding what you've been working on. The GTD skill should:

1. **Read the short list first** (from `/conversational-history recent`)
2. **Identify patterns** in the recent work
3. **Note momentum** (what's been worked on multiple days in a row)
4. **Spot gaps** (what was planned but not worked on)
5. **Use this to inform** the week/day planning conversation

## Integration with Other Skills

### Conversational History Skill

The GTD skill **relies heavily** on the conversational-history skill to understand recent context:

**Primary Context Source:** `/conversational-history recent`

When planning your week or day, the GTD skill FIRST checks:

```bash
/conversational-history recent  # Last 7 days of work
/conversational-history today   # Today's conversations
/conversational-history 3h      # Last 3 hours
```

**Performance Note:** The conversational-history skill uses a SQLite index (~200ms queries) so checking recent context is instant.

### Conversations-Manage Skill

**Secondary Context:** `/conversations-manage list`

The GTD skill also uses `conversations-manage` to:
- See conversation titles and understand project focus areas
- Identify patterns in recent work
- Understand which topics are getting attention

### PARA Skill

The GTD skill can **read PARA standards** by checking:
```
.claude/skills/para/references/para-structure-guide.md
```

This provides:
- Project structure guidelines
- Area vs Project distinctions
- Resource organization
- Archive conventions

## Performance Considerations

### Context Loading Strategy

1. **Quick mode** (daily planning): Last 24 hours only
2. **Standard mode** (weekly planning): Last 7 days
3. **Deep mode** (quarterly review): Last 30 days

### Caching

- Notion project data: Cache for 1 hour (changes infrequently)
- Conversation history: Always fresh (SQLite index is fast)
- Priority calculations: Cache for current session only

### Optimizations

- Use conversational-history SQLite index (not file scanning)
- Batch Notion API calls when fetching multiple projects
- Load tradeoff template from file (don't inline in SKILL.md)
- Progressive disclosure: Show summary first, details on request
