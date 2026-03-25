# GTD Example Workflows

Real-world examples of how the GTD skill works in different scenarios.

## Example 1: Weekly Planning (Full Workflow)

**User:** "Let's plan my week"

**Claude:** "I'll help you plan your week. Let me first check what you've been working on recently..."

[Uses `/conversational-history recent`]

**Claude:** "Based on your recent conversations, I can see:

**Last 7 days activity:**
- Mar 20-22: Creating GTD and PARA productivity skills
- Mar 19: Job board classification and Notion database work
- Mar 18: Conversation history optimization with SQLite
- Mar 15: MCP server setup for Gmail

**Current momentum:**
- Strong focus on productivity systems (GTD/PARA)
- Job board project showing consistent attention
- Infrastructure work (MCP, SQLite indexing)

Before we dive into specific plans, let me show you the tradeoff options for how you could allocate your time this week..."

[Generates tradeoff visualization with 4 options]

**Claude:** "Here are four ways you could spend your ~20h of focused work this week:

[Shows full tradeoff matrix from tradeoff-matrix-template.md]

**STRONGEST OBJECTION to continuing infrastructure work:**
You've spent 3 of the last 5 days on productivity infrastructure. If you don't apply it to an actual project soon, you risk building tools you never use.

**Supporting facts:**
- You completed job classification system on Mar 19
- SQLite indexing made conversation history 200x faster
- You have new productivity skills but haven't tested them on real work yet
- Pattern: You tend to build infrastructure when avoiding harder decisions

**Which allocation pattern resonates with you? Or should I show different options?**"

---

## Example 2: Daily Planning (Morning Routine)

**User:** "Help me plan my day"

**Claude:** "Good morning! Let me check what you worked on yesterday and what's on your plate today..."

[Uses `/conversational-history today` and `/conversational-history 3h`]

**Claude:** "**Yesterday (Mar 22):**
- Optimized GTD skill structure
- Created reference documentation
- Worked on skill best practices

**Today's context:**
- Sunday (typical reflection/planning day)
- No urgent deadlines today
- Week ahead has job application deadlines

**Current Focus for Today:**

┌──────────────────────────────────┐
│ 📚 Weekly Planning & Review      │
│    Time: 2-3h                    │
│    Energy: Medium                │
└──────────────────────────────────┘

**Suggested priorities:**
1. Complete weekly planning session (use the tradeoffs view)
2. Review last week's accomplishments
3. Prepare Monday's deep work session
4. Optional: Light project work if energy permits

**Energy match:** ✅ Good - Sunday suits reflection work

**What feels most important to focus on today?**"

---

## Example 3: Mid-Day Check-In (Stuck/Uncertain)

**User:** "I'm not sure what to work on next"

**Claude:** "Let me help you figure out the best use of your time right now..."

[Quick check of recent activity + current time + energy level]

**Claude:** "**Current situation:**
- Time: 2:30 PM (afternoon slump typical)
- Just finished: Documentation work (1.5h)
- Remaining energy: Medium-Low

**Options based on your state:**

**Option A: Continue momentum (Low energy OK)**
- Finish GTD skill documentation
- Already in context, 30min to complete
- ✅ Completion feels good
- ❌ May be tired of docs

**Option B: Switch to lighter task (Low energy friendly)**
- Review job postings on Clera
- Requires less deep focus
- ✅ Makes progress on high-priority goal
- ❌ Context switch cost

**Option C: Take break and reset (Energy recovery)**
- Walk, snack, change of scene (30min)
- Come back fresh for deep work
- ✅ Better quality work later
- ❌ Loses some time now

**Recommendation:** You've been in documentation mode for 90min. Either finish the current doc (30min) then take a break, or switch to the lighter job posting review if you're burnt out.

**What sounds right to you?**"

---

## Example 4: Tradeoff Visualization Request

**User:** "/gtd tradeoffs"

**Claude:** "I'll generate allocation options showing different ways you could spend your time this week..."

[Fetches Notion priorities + recent work patterns]

**Claude:**

```
Week Mar 23-29, 2026: Priority Tradeoffs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Available: ~20h focused work
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OPTION A: Ship + Apply (Career Transition Focus)
┌────────────────────────────────────────────────────┐
│ 💼 Job Applications    12h  ████████████          │
│ 📝 Portfolio Polish     6h  ██████                │
│ 📚 Light Learning       2h  ██                    │
└────────────────────────────────────────────────────┘
     ↓ Tradeoffs
  ❌ No infrastructure improvements
  ❌ BlueDot project pauses
  ❌ Deep technical learning pauses
  ✅ Direct career progress (4-6 applications)
  ✅ Concrete applications submitted
  ✅ Portfolio ready to share
  ⚠️  Risk: Burnout from application grind

OPTION B: Build + Learn (Portfolio Development)
┌────────────────────────────────────────────────────┐
│ 🏗️  Job Board MVP     10h  ██████████            │
│ 📚 BlueDot Research     8h  ████████              │
│ 💼 Quick Apply          2h  ██                    │
└────────────────────────────────────────────────────┘
     ↓ Tradeoffs
  ❌ No bulk applications go out
  ❌ Career transition delays 1 week
  ❌ Infrastructure temptation
  ✅ Portfolio projects advance significantly
  ✅ Deep technical learning
  ✅ One thoughtful application
  ⚠️  Risk: Productive procrastination pattern

OPTION C: Hybrid Balance (Split Focus)
┌────────────────────────────────────────────────────┐
│ 💼 Job Applications     8h  ████████              │
│ 🏗️  Job Board MVP       6h  ██████                │
│ 📚 BlueDot Research      4h  ████                  │
│ 🛠️  Infrastructure       2h  ██                    │
└────────────────────────────────────────────────────┘
     ↓ Tradeoffs
  ❌ Nothing reaches completion
  ❌ High context switching cost
  ❌ Diluted progress across all areas
  ✅ Balanced progress
  ✅ Hedges multiple bets
  ✅ Feels less extreme
  ⚠️  Risk: Busy but not productive

OPTION D: Sprint to Ship (Single Focus)
┌────────────────────────────────────────────────────┐
│ 🏗️  Job Board MVP     16h  ████████████████      │
│ 📝 Write-up & Ship      4h  ████                  │
└────────────────────────────────────────────────────┘
     ↓ Tradeoffs
  ❌ Zero job applications this week
  ❌ Opportunity cost compounds
  ❌ BlueDot project pauses
  ✅ One completed portfolio piece
  ✅ Shipping momentum
  ✅ Demo-able for interviews
  ⚠️  Risk: Week passes with no career progress

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DECISION MATRIX:

                    Career    Portfolio   Learning   Energy
Option A            ████████  ██░░░░░░    ██░░░░░░   ████░░░░
Option B            ██░░░░░░  ████████    ████████   ██████░░
Option C            ████░░░░  ████░░░░    ████░░░░   ██░░░░░░
Option D            ░░░░░░░░  ████████    ██████░░   ████████

HIDDEN COSTS:

Context Switching Tax:
  A: Low - Single domain (applications + writing)
  B: Low - Single domain (technical projects)
  C: High - Four different contexts/mindsets
  D: Very Low - Single project sprint

Opportunity Cost Per Week:
  - Delaying applications: ~3-4 potential interviews lost
  - Pausing Job Board: 1 week delay on portfolio piece
  - Skipping BlueDot: Falls behind course schedule, deadline Apr 5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STRONGEST OBJECTION TO OPTION B (Build + Learn):

You've spent 3 of the last 5 days building infrastructure. Your Notion says job applications are HIGH PRIORITY and URGENT. Yet you're considering another week of building instead of applying. This is productive procrastination.

Your BlueDot synthesis from Unit 1 literally says: "APPLY IMMEDIATELY - don't build portfolio first." You're ignoring your own research.

**Future Self Question:** Will you-in-6-months thank you-now for building another feature, or for applying to 6 jobs?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Claude:** "Based on your stated priorities (HIGH PRIORITY job applications) and recent pattern (building instead of shipping), I'd recommend **Option A** this week.

But I'm not deciding for you - what feels right given these tradeoffs?"

---

## Example 5: Quick Visualization (Current State)

**User:** "/gtd visualize"

**Claude:**

```
Current Focus: Sunday, Mar 22, 2026 - 5:15 PM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Active Right Now:
┌──────────────────────────────────┐
│ 🛠️  GTD Skill Optimization       │
│    Time: 1-2h remaining          │
│    Energy: Medium                │
│    Progress: 80% done            │
└──────────────────────────────────┘

Active Threads (from Notion):
  🔴 Job Applications     (High Priority, Low Momentum) ⚠️
  🟡 BlueDot Project      (High Priority, Medium Momentum)
  🟡 Job Board MVP        (Medium Priority, High Momentum)

Next Actions:
  1. Finish GTD skill optimization (30-60min)
  2. Review week ahead commitments
  3. Set up Monday's first task

Energy Match: ✅ Good
  Sunday evening = Wrap-up time
  Optimization = Medium energy task
  Almost done = Completion dopamine

Recommendation:
Finish the GTD skill work, then spend 15min doing weekly planning
using the new tradeoff visualization you just built. Practice using
the tool you created.
```

---

## Example 6: End of Day Wrap-Up

**User:** "I finished X, what now?"

**Claude:** "Nice work completing [X]! Let me help you decide what's next..."

[Checks time of day, energy level, and remaining priorities]

**Claude:** "**Current state:**
- Time: 4:45 PM
- Remaining focused time: ~1-1.5h
- Energy: Probably declining

**Completed today:**
- ✅ GTD skill optimization
- ✅ Reference documentation created

**Options for remaining time:**

**Option A: Start tomorrow's first task (Momentum builder)**
- Begin job application research
- Won't finish today, but removes activation energy for tomorrow
- ✅ Monday starts easier
- ❌ Might feel incomplete today

**Option B: Do a quick win (Completion satisfying)**
- Review and bookmark 3-5 job postings
- Can finish in 30-45min
- ✅ Feels complete
- ✅ Makes Monday concrete

**Option C: Wrap up and plan (Strategic)**
- Weekly planning session using new GTD skill
- Ends day with clarity for week ahead
- ✅ High value use of time
- ✅ Tests what you just built

**Recommendation:** Option C - spend the remaining time doing weekly planning. You just optimized the GTD skill, so use it for its intended purpose. That'll give you a clear plan for tomorrow and test your own work.

**Sound good?**"

---

## Common Patterns and Variations

### Pattern: Infrastructure Avoidance

**Symptom:** User keeps working on tools instead of using them
**GTD Response:** Flag the pattern, show opportunity cost, recommend execution

### Pattern: Analysis Paralysis

**Symptom:** Too many options, can't choose
**GTD Response:** Reduce to 2 options, use tradeoff matrix, apply future self test

### Pattern: Scattered Focus

**Symptom:** Context switching between many projects
**GTD Response:** Show hidden costs of switching, recommend single-focus week

### Pattern: Deadline Pressure

**Symptom:** Multiple urgent items competing
**GTD Response:** Sort by consequence of delay, recommend what to drop/delegate

### Pattern: Low Energy Days

**Symptom:** Can't focus on hard tasks
**GTD Response:** Suggest lighter tasks that still make progress, or strategic rest
