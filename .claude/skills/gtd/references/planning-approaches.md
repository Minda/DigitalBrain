s?# Planning Approaches Reference

## Core Planning Methods

### 1. Decision Buffer Planning
**When Applied:** High decision-making capacity, multiple projects competing for attention

**Implementation:**
```python
def generate_decision_buffer(current_time, projects, energy_state):
    """Generate decision points instead of task lists"""
    decision_points = [
        "9am:  Decide - Deep work or maintenance?",
        "11am: Decide - Continue thread or switch?",
        "2pm:  Decide - High-cognition or admin?",
        "4pm:  Decide - Close loops or explore?"
    ]

    # Add context for each decision
    for dp in decision_points:
        context = analyze_project_state(projects, dp.time)
        dp.add_context(f"Options: {context.viable_projects}")
        dp.add_context(f"Energy match: {context.energy_fit}")

    return decision_points
```

**Output Format:**
```
📊 DECISION BUFFER - Thursday, April 3
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
9:00am  | Decision Point: Deep Focus vs Maintenance
        | Options: BlueDot analysis (high cognition)
        |          Skill updates (medium cognition)
        | Current energy: High ✅
        | Recommendation: Deep work window available

11:00am | Decision Point: Continue vs Switch
        | Current thread: [active task]
        | Alternative: Job board features (deadline)
        | Switching cost: ~15 min context rebuild
```

### 2. Bottleneck Hunting
**When Applied:** External deadlines present, blocked work detected, dependency chains

**Implementation:**
```python
def identify_bottlenecks(projects, collaborators, deadlines):
    """Find work that's blocking progress"""
    bottlenecks = {
        'blocking_others': [],    # What others need from you
        'blocking_future': [],    # What future-you needs
        'blocking_current': []    # What's stopping you now
    }

    # Scan for external dependencies
    for project in projects:
        if project.has_waiting_collaborator():
            bottlenecks['blocking_others'].append({
                'project': project.name,
                'blocker': project.next_deliverable,
                'impact': project.blocked_person,
                'urgency': calculate_urgency(project.deadline)
            })

    return prioritize_bottlenecks(bottlenecks)
```

**Output Format:**
```
🎯 BOTTLENECK ANALYSIS - Thursday, April 3
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BLOCKING OTHERS (Do First):
1. BlueDot Session 3 prep → Anusha waiting → Due tomorrow
2. Code review → Team blocked → 2 hours old

BLOCKING FUTURE YOU:
3. Conversation indexing → Degrading search → 500+ unindexed
4. Git commits → Work not saved → 12 files modified

BLOCKING CURRENT YOU:
5. Missing Notion context → Can't prioritize → Need fetch
```

### 3. Energy Arbitrage
**When Applied:** Variable energy throughout day, cognitive load mismatches detected

**Implementation:**
```python
def map_energy_to_tasks(current_energy, time_of_day, task_list):
    """Match tasks to energy states"""
    energy_map = {
        'high': ['BlueDot analysis', 'Architecture design', 'Complex debugging'],
        'medium': ['Skill creation', 'Feature implementation', 'Writing'],
        'low': ['Git commits', 'Indexing', 'Documentation', 'File organization']
    }

    # Calculate energy trajectory
    trajectory = predict_energy_curve(time_of_day, recent_patterns)

    # Generate time blocks with escape hatches
    schedule = []
    for hour in working_hours:
        expected_energy = trajectory[hour]
        matched_tasks = energy_map[expected_energy]
        schedule.append({
            'time': hour,
            'energy': expected_energy,
            'primary': matched_tasks[0],
            'escape': matched_tasks[-1],  # Low-energy fallback
            'deadline_override': check_urgent_deadlines(hour)
        })

    return schedule
```

**Output Format:**
```
⚡ ENERGY ARBITRAGE - Thursday, April 3
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Current Energy: Medium-High (post-coffee peak)
Trajectory: ↗️ Rising (next 2 hours) → ↘️ Decline (afternoon)

ENERGY BLOCKS:
┌─────────────────────────────────────┐
│ 9-11am  | HIGH ENERGY              │
│         | → BlueDot collusion analysis│
│         | [escape: review notes]      │
├─────────────────────────────────────┤
│ 11-1pm  | MEDIUM ENERGY            │
│         | → Job board features        │
│         | [escape: documentation]     │
├─────────────────────────────────────┤
│ 2-4pm   | LOW ENERGY               │
│         | → Git commits + indexing    │
│         | → Conversation archiving    │
└─────────────────────────────────────┘

⚠️ DEADLINE OVERRIDE at 3pm: BlueDot prep if not complete
```

### 4. Parallel Progress Pattern
**When Applied:** Multiple async processes available, context-switching acceptable

**Implementation:**
```python
def identify_parallel_opportunities(current_task, available_tools):
    """Find work that can run in background"""
    parallel_ops = []

    # Check for long-running processes
    if 'indexing' in available_tools:
        parallel_ops.append({
            'operation': 'conversation indexing',
            'duration': '5-10 min',
            'command': 'python index_conversations.py &'
        })

    if 'testing' in current_task.requirements:
        parallel_ops.append({
            'operation': 'test suite',
            'duration': '3-5 min',
            'command': 'npm test &'
        })

    # Calculate optimal interleaving
    schedule = optimize_parallel_work(current_task, parallel_ops)
    return schedule
```

**Output Format:**
```
🔄 PARALLEL PROGRESS OPPORTUNITIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CURRENT: Writing BlueDot analysis

BACKGROUND AVAILABLE:
• Conversation indexing (5-10 min)
• Job board build process (3 min)
• Notion sync (2-3 min)

SUGGESTED PATTERN:
1. Start: indexing process &
2. Focus: 25 min BlueDot writing
3. Check: indexing results
4. Start: build process &
5. Continue: BlueDot analysis
6. Natural break: Check build, commit if green
```

## Integration Points

### With Existing Commands

**`/gtd visualize`** enhancement:
- Add energy match indicator
- Show parallel opportunities
- Include next decision point

**`/gtd tradeoffs`** enhancement:
- Add bottleneck costs to each option
- Show energy requirements
- Include decision buffer alternative

**`/gtd plan`** new intelligence:
```python
def select_planning_approach(context):
    if context.has_external_deadlines and context.blocking_work:
        return 'bottleneck_hunting'
    elif context.energy_variability > 0.3:
        return 'energy_arbitrage'
    elif context.decision_complexity > threshold:
        return 'decision_buffer'
    elif context.has_async_processes:
        return 'parallel_progress'
    else:
        return 'hybrid'
```

## Visual Indicators

Add to existing visualizations:

```
Energy: ⚡⚡⚡⚡⚡ (High)
Blocks: 🚫 2 blocking others
Parallel: 🔄 3 background available
Decisions: 🎯 2 pending
```

## Fallback Behavior

If approach selection fails or user wants explicit control:

```bash
/gtd plan --approach=decisions
/gtd plan --approach=bottlenecks
/gtd plan --approach=energy
/gtd plan --approach=parallel
/gtd plan --approach=auto  # Default intelligent routing
```

## Success Metrics

Track which approaches work best:
- Decision Buffer: Reduced time in "what should I do?" state
- Bottleneck Hunting: Fewer blocked collaborators
- Energy Arbitrage: Higher completion rate on high-cognition tasks
- Parallel Progress: More tasks completed per session

## User Preferences

Store in `personal/preferences/gtd-config.md`:
```yaml
preferred_approach: auto
energy_tracking: enabled
decision_points: 4  # per day
parallel_threshold: 2  # min processes
bottleneck_check: hourly
```