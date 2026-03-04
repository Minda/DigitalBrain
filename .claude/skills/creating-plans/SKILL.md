# Creating Plans Skill

**Purpose**: Create systematic, step-by-step implementation plans with safety checkpoints and manual review stages.

## When to Use

Use this skill when:
- User requests a complex multi-step project
- Task requires careful sequencing and validation
- Changes could have significant impact (email processing, data migration, etc.)
- User explicitly asks for a plan before execution
- Working with personal/sensitive data

## Process

### 1. Gather Requirements

Ask the user:
- What is the end goal?
- What constraints exist?
- What safety measures are needed?
- Should changes be reversible?
- Where should data be stored?

Use `AskUserQuestion` tool if multiple options exist.

### 2. Design Plan Structure

Each plan should have:
- **Clear phases/steps** (Step 0, Step 1, etc.)
- **Manual review checkpoints** after risky operations
- **Success criteria** for each step
- **Safety features** section
- **Rollback strategy** if things go wrong

### 3. Plan Components

```markdown
# [Project Name] - Implementation Plan

**Created**: [Date]
**Status**: Ready for execution / In Progress / Complete
**Goal**: [Clear one-sentence goal]

---

## Step N: [Step Title]

### Actions
- Bullet points of specific actions
- Include exact commands or file paths
- Note any prerequisites

### Success Criteria
- ✅ Specific measurable outcomes
- ✅ What success looks like

**Manual Review**: [What user should check]

---

## Safety Features
- List all safety measures
- Rollback procedures
- Data backup requirements

## Privacy & Security
- Where sensitive data is stored
- What should NOT be committed to git
```

### 4. Privacy Considerations

Always consider:
- **Personal data** → Store in `personal/` (private repo)
- **Credentials** → Add to `.gitignore`
- **API keys** → Use environment variables
- **Email/user data** → Never in public repo

Add privacy warnings where appropriate:
```
⚠️ PRIVACY: All email-derived data MUST be stored in personal/
```

### 5. Statistical Validation

For sampling/processing plans:
- Calculate proper sample sizes
- Include confidence levels
- Show margin of error
- Provide estimations with ranges

### 6. Testing Strategy

Include test phases:
1. **Dry run** - Preview without changes
2. **Small batch** - Test with 5-10 items
3. **Medium batch** - Test with 20-50 items
4. **Full run** - Complete processing

### 7. Save the Plan

Always save plans to `/plans/` directory:
```python
Write("/plans/[project-name].md", plan_content)
```

### 8. Create Documentation (if needed)

For features and projects, also create documentation in `/plans/`:
- **Features**: `/plans/YYYY-MM-DD-feature-name.md`
- **Projects**: `/plans/YYYY-MM-DD-project-name.md`

See `documentation-diagrams.md` for guidance on filling out mermaid diagrams.

## Documentation Workflows

### Creating a New Project

1. **Copy the template**:
   ```python
   Read("/plans/project-template.md")
   ```

2. **Create new file with date prefix**:
   ```python
   Write("/plans/YYYY-MM-DD-project-name.md", content)
   ```

3. **Fill out all sections**:
   - Overview and problem space
   - Goals and success metrics
   - Scope (in/out)
   - Related features (link them!)
   - Architecture diagrams (see `documentation-diagrams.md`)
   - Milestones and timeline
   - Risk assessment with matrix

4. **Update the plans index**:
   ```python
   Edit("/plans/README.md")
   # Add to appropriate category and status section
   ```

5. **Create initial features if needed**

### Creating a New Feature

1. **Copy the template**:
   ```python
   Read("/plans/feature-request-template.md")
   ```

2. **Create new file with date prefix**:
   ```python
   Write("/plans/YYYY-MM-DD-feature-name.md", content)
   ```

3. **Link to parent project** (REQUIRED):
   ```markdown
   **Project**: [Project Name](YYYY-MM-DD-project-name.md)
   ```

4. **Fill out all sections**:
   - Current state and problem
   - Desired behavior with user journey
   - Technical context with diagrams
   - Requirements and nice-to-haves
   - Open questions

5. **Update the plans index**:
   ```python
   Edit("/plans/README.md")
   # Add under parent project section
   ```

6. **Update parent project's feature list**:
   ```python
   Edit("/plans/YYYY-MM-DD-project-name.md")
   # Add to "Related Features" section
   ```

### Updating Documentation Status

**Feature Status Flow**:
- `Draft` → `In Review` → `Approved` → `In Progress` → `Complete`

**Project Status Flow**:
- `Planning` → `In Progress` → `On Hold` (optional) → `Complete`

**Where to update**:
1. In the document itself (Status field)
2. In the appropriate README index
3. In parent project (if feature)

### Maintaining Feature-Project Relationships

**Every feature MUST**:
- Reference its parent project in the header
- Include project link in format: `[Project Name](YYYY-MM-DD-name.md)`

**Every project SHOULD**:
- List all child features in "Related Features" section
- Show feature status and count
- Update feature dependency graph

**Bidirectional linking**:
```markdown
# In feature file:
**Project**: [Documentation System](2025-02-15-documentation-system.md)

# In project file:
- [x] Documentation Structure - Complete
  - Link: `2025-02-15-docs-project-structure.md`
```

### Quick Status Check

To see all features for a project:
```python
Grep("project-name", "/plans/", output_mode="files_with_matches")
```

To check feature status:
```python
Grep("Status:", "/plans/YYYY-MM-DD-*.md", output_mode="content")
```

## Example Plans

### Available Templates
- `email-classifier-plan.md` - Email processing with ML classification
- `data-migration-plan.md` - Moving data between systems
- `api-integration-plan.md` - Integrating external services
- `skill-creation-plan.md` - Creating new Claude skills

## Plan Execution Workflow

1. **Create plan** → `/plans/[name].md`
2. **Review with user** → Get approval
3. **Execute Step 0** → Setup/infrastructure
4. **Manual review** → User confirms
5. **Continue steps** → With checkpoints
6. **Document results** → Update plan status

## Tips

### DO:
- Break complex tasks into 5-10 clear steps
- Add manual review after every 2-3 automated steps
- Include rollback procedures
- Test with small batches first
- Document all assumptions
- Calculate statistical samples properly
- Keep personal data separate

### DON'T:
- Skip manual review checkpoints
- Process all data at once without testing
- Commit sensitive data to public repos
- Delete data (archive instead)
- Assume one-size-fits-all

## Usage Examples

```python
# User asks for complex project
"I need to reorganize my entire email archive"

# Response using this skill:
"Let me create a comprehensive plan for this. I'll break it down into
safe, reversible steps with checkpoints where you can review progress."

# Create plan with:
- Statistical sampling
- Test batches
- Manual reviews
- Rollback strategy
```

## Related Skills
- `saving-memories` - For preserving important discoveries
- `learning` - Document insights from plan execution
- `self-regulation` - If plan involves sensitive operations

## Plan Status Tracking

Mark plan status in the document:
- `Status: Draft` - Still being designed
- `Status: Ready for execution` - Approved, ready to start
- `Status: In Progress - Step N` - Currently executing
- `Status: Complete` - Successfully finished
- `Status: Paused` - Waiting for user input
- `Status: Rolled back` - Reverted due to issues

---

Remember: A good plan is the foundation of successful execution. Take time to think through edge cases and failure modes before starting.