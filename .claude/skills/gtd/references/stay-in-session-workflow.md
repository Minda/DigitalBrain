# Stay In Session Time Tracking Workflow

<!-- App Reference -->
<!-- Stay In Session: https://www.stayinsession.com/ -->
<!-- Changelog (features): https://www.stayinsession.com/changelog -->

## Overview

Stay In Session is a focus timer app with session tracking capabilities. Use it to track actual time allocation and compare against GTD weekly plans.

## Why Stay In Session?

- ✅ **Apple Shortcuts integration** - Can automate some workflows
- ✅ **CSV/JSON export** - Clean data for analysis
- ✅ **Project tagging** - Categorize sessions
- ✅ **Things 3 integration** - Pulls tasks automatically
- ❌ **No REST API yet** - Can't build MCP server (manual export required)

## Setup for Weekly Tracking

### 1. Install and Configure

1. Download Stay In Session from Mac App Store
2. Create project tags for your focus areas:
   - 💼 Job Applications
   - 🏗️ Job Board MVP
   - 📚 BlueDot Research
   - 🛠️ Productivity/Infra
   - 📧 Email/Admin
   - 🎯 Other Focused Work

### 2. Daily Ritual

**Morning:**
- Review today's plan from GTD skill
- Note estimated hours per category

**During Work:**
- Start Stay In Session timer when beginning focused work
- Tag session with appropriate project
- Add brief note about what you're working on
- End session when switching contexts or taking break

**Evening:**
- Review today's actual time vs. planned
- Note any significant deviations
- Prepare for tomorrow

### 3. Weekly Export (End of Week)

**Export Process:**
1. Open Stay In Session
2. Go to Settings → Export Data
3. Select date range (e.g., Mar 23-29, 2026)
4. Choose format:
   - **CSV** - Easier to read, good for spreadsheets
   - **JSON** - More detail, better for scripting
5. Save to: `personal/data/time-tracking/YYYY-Www-stay-in-session.[csv|json]`

**File naming convention:**
```
personal/data/time-tracking/2026-W12-stay-in-session.csv
personal/data/time-tracking/2026-W13-stay-in-session.json
```

## Analysis Workflow

### 1. Run Analysis Script

```bash
python3 src/python/analyze_time_tracking.py \
  personal/data/time-tracking/2026-W12-stay-in-session.csv \
  --planned "Job Applications: 8h
Job Board MVP: 8h
BlueDot Research: 4h" \
  --output personal/data/time-tracking/2026-W12-analysis.txt
```

### 2. Review Output

The script generates:
- **Total comparison** (planned vs. actual hours)
- **Per-category breakdown** with bar charts
- **Deviation analysis** (over/under allocations)
- **Planning accuracy percentage**
- **Insights** (best/worst estimates)

### 3. Update Weekly Plan

Use insights to:
- Adjust time estimates for next week
- Identify avoidance patterns
- Improve allocation decisions
- Update GTD skill tradeoff visualizations

## Automation Potential (Future)

### Apple Shortcuts Integration

Stay In Session supports Apple Shortcuts for:
- Starting/stopping sessions programmatically
- Getting current session metadata
- Chaining with other apps

**Future workflow:**
1. Create shortcut: "Weekly Time Export"
2. Runs every Sunday evening
3. Exports data automatically
4. Triggers analysis script
5. Updates Notion with results

### MCP Server (When Available)

If Stay In Session releases REST API:
1. Build MCP server for real-time queries
2. GTD skill can check actual vs. planned during week
3. Mid-week corrections based on current trajectory
4. Automatic Notion updates

## Data Privacy

**Local-first:**
- All Stay In Session data stays on your Mac
- Exports are local files
- No cloud sync (unless you configure iCloud)

**Where data goes:**
- Local: `personal/data/time-tracking/` (gitignored)
- Analysis: `personal/data/time-tracking/*-analysis.txt`
- Notion: Summary only (not raw time data)

## Project Tags Guide

### When to Use Which Tag

**💼 Job Applications**
- Writing cover letters
- Tailoring resumes
- Research on companies
- Application submission
- Interview prep

**🏗️ Job Board MVP**
- Coding features
- Database work
- UI/UX implementation
- Testing
- Deployment

**📚 BlueDot Research**
- Reading papers
- Taking notes
- Paper discussions/meetings
- Writing summaries
- Research synthesis

**🛠️ Productivity/Infra**
- Building tools (GTD, PARA skills)
- Setting up systems
- Configuration
- Meta-work on productivity

**📧 Email/Admin**
- Email processing
- Calendar management
- Administrative tasks
- Quick communications

**🎯 Other Focused Work**
- Anything else requiring deep focus
- One-off projects
- Learning sessions
- Creative work

## Common Pitfalls

### ❌ Don't Do This

1. **Forgetting to tag sessions** - Can't categorize later
2. **Too many tags** - Hard to analyze, creates noise
3. **Tracking breaks** - Only track focused work
4. **Perfectionism** - Rough accuracy is fine
5. **Skipping export** - Data only useful if analyzed

### ✅ Do This Instead

1. **Always tag immediately** - Make it a habit
2. **Use 5-7 tags max** - Keep it simple
3. **Only track focus time** - Ignore admin/breaks
4. **80% accuracy is fine** - Don't stress over minutes
5. **Weekly export ritual** - Sunday evening routine

## Troubleshooting

### Sessions not showing up in export

- Check date range matches your tracking period
- Verify sessions were saved (check app history)
- Try different export format (CSV vs. JSON)

### Can't categorize sessions

- Make sure project tags were set during session
- Check if tags were renamed after session
- Look for "Untagged" category in export

### Export file format issues

- Verify file extension (.csv or .json)
- Check for special characters in session names
- Try opening in text editor to inspect format

## Example Weekly Report

```
Time Tracking Analysis: Week Mar 23-29, 2026
======================================================================

Total Planned: 20.0h
Total Actual:  17.5h
Difference:    -2.5h

----------------------------------------------------------------------
Category                   Planned   Actual  Deviation
----------------------------------------------------------------------
Job Applications            8.0h     5.5h     -2.5h 📉
Job Board MVP               8.0h     9.0h     +1.0h ⚠️
BlueDot Research            4.0h     2.5h     -1.5h 📉
Productivity/Infra          0.0h     0.5h     +0.5h ⚠️

----------------------------------------------------------------------

## Insights

**Over-allocated** (spent more time than planned):
  • Job Board MVP: +1.0h
  • Productivity/Infra: +0.5h

**Under-allocated** (spent less time than planned):
  • Job Applications: -2.5h
  • BlueDot Research: -1.5h

**Planning Accuracy:** 78.3%

  Best:  Job Board MVP (87.5% accurate)
  Worst: Job Applications (68.8% accurate)

**Pattern detected:**
You're avoiding job applications (planned 8h, actual 5.5h). This
matches the "productive procrastination" pattern - building instead
of applying. Next week: Schedule applications in morning when
energy is highest.
```

## Integration with GTD Skill

The GTD skill uses this time tracking data to:

1. **Improve estimates** - Historical data informs future plans
2. **Spot patterns** - Recurring avoidance behaviors
3. **Reality check** - Compare ideal vs. real capacity
4. **Adjust tradeoffs** - Update allocation options based on actual behavior

This creates a feedback loop:
- GTD skill → Weekly plan → Track time → Analyze data → Improve GTD skill → Better plans
