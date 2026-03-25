# Command Clarity Audit & Revision Plan

## Overview

This audit evaluates each skill's command clarity and provides specific, actionable suggestions for improvement. Commands should be self-explanatory without needing to check the skill documentation.

## Clarity Rating System

- 🟢 **CLEAR** — Command intent is immediately obvious
- 🟡 **UNCLEAR** — Command needs context to understand
- 🔴 **VERY UNCLEAR** — Command gives no hint about function

## Revision Principles

1. **Every command should include a verb** (or clearly imply one)
   - ✅ Good: `/learnings reflect`, `/gtd visualize`
   - ❌ Bad: `/memories`, `/context`

2. **Skill names should describe the function**
   - ✅ Good: `saving-memories`, `creating-ascii-drawings`
   - ❌ Bad: `week`, `context`

3. **Related commands should share a namespace**
   - ✅ Good: `/learnings reflect` | `/learnings load`
   - ❌ Bad: `/research` | `/reading` (for weekly reports)

4. **Primary trigger should be obvious**
   - Each skill needs at least one clear, memorable command
   - Secondary triggers can be more flexible

5. **Avoid overlapping triggers**
   - `/memories` shouldn't trigger multiple different skills
   - Be specific: `/save-drawing` vs `/load-memories`

---

## 🟢 CLEAR Commands (No Changes Needed)

These skills have excellent command clarity:

### ✅ **gtd**
- Commands: `/gtd visualize` | `/gtd tradeoffs` | `"let's plan my week"`
- Why it works: Action verbs make intent crystal clear

### ✅ **learning**
- Commands: `/learnings reflect` | `/learnings load` | `/learnings recent`
- Why it works: Consistent namespace with clear actions

### ✅ **hypercontext**
- Commands: `/hypercontext` | `/hypercontext compact` | `/hypercontext threads`
- Why it works: Base command with clear modifiers

### ✅ **committing-work**
- Commands: `"commit"` | `"git commit"` | `"commit my changes"`
- Why it works: Standard git terminology

### ✅ **download-url**
- Commands: `"download url"` | `"save this article"` | `"download entire site"`
- Why it works: Verb + object pattern

---

## 🟡 UNCLEAR Commands (Needs Improvement)

### ⚠️ **saving-drawings**
- **Current:** `/memories` | `/drawings`
- **Problem:** `/memories` is vague - doesn't indicate drawings
- **Fix:**
  ```
  [ ] Change primary command to: /save-drawing
  [ ] Add alternative: /drawings save
  [ ] Add trigger: "save this diagram"
  ```
- **Rationale:** Makes both action (save) and target (drawing) explicit

### ⚠️ **notion-weekly-reports**
- **Current:** `/research` | `/reading` | `"weekly report"`
- **Problem:** `/research` and `/reading` don't clearly connect to weekly reports
- **Fix:**
  ```
  [ ] Change to: /weekly-report
  [ ] Add subcommands: /weekly-report research | /weekly-report reading
  [ ] Keep: "create weekly report" as trigger
  ```
- **Rationale:** Namespace commands under weekly context

### ⚠️ **fetching-notion-content**
- **Current:** `"Notion"` | `"find in Notion"`
- **Problem:** Just saying "Notion" is too broad
- **Fix:**
  ```
  [ ] Add primary: /notion search
  [ ] Add alternative: /notion fetch
  [ ] Keep triggers: "search Notion for" | "get from Notion"
  ```
- **Rationale:** Add verb to clarify the action

### ⚠️ **week**
- **Current:** `"new week"` | `"weekly setup"`
- **Problem:** Skill name "week" is too generic
- **Fix:**
  ```
  [ ] Rename skill to: weekly-setup
  [ ] Add slash command: /weekly-setup
  [ ] Keep triggers: "start my week" | "set up the week"
  ```
- **Rationale:** More descriptive skill name

### ⚠️ **waking-up**
- **Current:** `"wake up"` | `"reorient"`
- **Problem:** Missing slash command option
- **Fix:**
  ```
  [ ] Add: /wake-up or /startup
  [ ] Keep triggers: "wake up" | "reorient"
  ```
- **Rationale:** Provide slash command for consistency

---

## 🔴 VERY UNCLEAR Commands (Priority Fixes)

### ❌ **context**
- **Current:** No commands shown
- **Problem:** Skill name gives no hint about function
- **Fix:**
  ```
  [ ] Rename to: relational-context
  [ ] Add commands: /context load | /context edit
  [ ] Add trigger: "load our context"
  ```
- **Rationale:** Specify what kind of context

### ❌ **de-ai**
- **Current:** No commands shown
- **Problem:** Cryptic name, no clear triggers
- **Fix:**
  ```
  [ ] Add primary: /de-ai
  [ ] Add triggers: "remove AI artifacts" | "clean AI-generated content"
  [ ] Consider renaming to: ai-cleanup
  ```
- **Rationale:** Name suggests de-AI-ification but needs explicit commands

### ❌ **managing-email**
- **Current:** No commands shown
- **Problem:** No clear invocation method
- **Fix:**
  ```
  [ ] Add primary: /email
  [ ] Add subcommands: /email classify | /email archive
  [ ] Add trigger: "manage my email"
  ```
- **Rationale:** Standard command pattern with clear actions

### ❌ **courses**
- **Current:** No commands shown
- **Problem:** Too generic, no triggers
- **Fix:**
  ```
  [ ] Add: /courses or /course-materials
  [ ] Add triggers: "load course" | "study materials"
  ```
- **Rationale:** Needs explicit invocation

### ❌ **bluedot-courses**
- **Current:** No commands shown
- **Problem:** Unclear differentiation from generic courses
- **Fix:**
  ```
  [ ] Add: /bluedot
  [ ] Add triggers: "bluedot course" | "climate course"
  ```
- **Rationale:** Brand-specific command

### ❌ **email-clothing-classifier**
- **Current:** No commands shown
- **Problem:** Very specific skill with no triggers
- **Fix:**
  ```
  [ ] Add: /classify-clothing
  [ ] Add trigger: "classify clothing emails"
  [ ] Consider merging with managing-email skill
  ```
- **Rationale:** May be better as email subcommand

### ❌ **optimizing-images**
- **Current:** No commands shown
- **Problem:** No invocation method
- **Fix:**
  ```
  [ ] Add: /optimize-image <path>
  [ ] Add trigger: "optimize this image"
  ```
- **Rationale:** Clear action + target

### ❌ **creating-plans**
- **Current:** No commands shown
- **Problem:** Overlaps with gtd conceptually
- **Fix:**
  ```
  [ ] Add: /create-plan
  [ ] Add triggers: "create a plan for" | "plan this project"
  [ ] Consider if this duplicates gtd functionality
  ```
- **Rationale:** Distinguish from gtd planning

---

## Quick Fix Checklist

Copy this section for easy tracking:

### 🔴 High Priority (Fix these first)
```
[ ] context → Rename to relational-context, add /context load
[ ] de-ai → Add /de-ai command and triggers
[ ] managing-email → Add /email with subcommands
[ ] courses → Add /courses command
[ ] bluedot-courses → Add /bluedot command
[ ] email-clothing-classifier → Add /classify-clothing
[ ] optimizing-images → Add /optimize-image
[ ] creating-plans → Add /create-plan
```

### 🟡 Medium Priority
```
[ ] saving-drawings → Change /memories to /save-drawing
[ ] notion-weekly-reports → Change to /weekly-report with subcommands
[ ] fetching-notion-content → Add /notion search
[ ] week → Rename to weekly-setup, add /weekly-setup
[ ] waking-up → Add /wake-up or /startup
```

### 🟢 Low Priority (Already clear but could be enhanced)
```
[ ] Add slash variants for skills with only quoted triggers
[ ] Standardize hyphen use in multi-word commands
[ ] Add "Also:" section to all skills for alternatives
```

---

## Implementation Guide

For each skill that needs updating:

1. **Open the SKILL.md file**
   ```bash
   open .claude/skills/[skill-name]/SKILL.md
   ```

2. **Update the description field** to include clear commands:
   ```yaml
   description: [Brief function]. Use /command, /command subcommand, or "trigger phrase".
   ```

3. **Add a Commands section** if missing:
   ```markdown
   ## Commands

   - `/primary-command` — Main invocation
   - `/command subcommand` — Specific action
   - `"trigger phrase"` — Natural language trigger
   ```

4. **Test the updated command** to ensure it works

---

## Success Metrics

After implementing these changes:

- ✅ Every skill should have at least one slash command OR clear quoted trigger
- ✅ Related skills should have consistent command patterns
- ✅ Users should understand what a command does from its name alone
- ✅ No two skills should respond to the same ambiguous trigger
- ✅ The `/skills` output should be self-documenting

---

## Notes for Future Skills

When creating new skills:

1. **Start with the command**, not the implementation
2. **Use verbs** in your commands
3. **Test for conflicts** with existing commands
4. **Document triggers clearly** in the description
5. **Consider subcommands** for complex skills

---

*Generated by the /skills command clarity audit*