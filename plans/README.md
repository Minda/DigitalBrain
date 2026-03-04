# Plans Index

This directory contains all planning documentation for the Exobrain system, including:
- **Implementation plans** - Step-by-step execution plans
- **Feature requests** - Individual feature proposals with technical details
- **Project documentation** - High-level projects containing multiple features

## Active Plans

### 🏗️ Infrastructure & Tools
- [2025-02-15-documentation-system.md](./2025-02-15-documentation-system.md) - **Status**: In Progress
  - Creating documentation structure for features, projects, and other system docs
  - **Features**: 1

### 📧 Email Management
- [2026-02-15-email-management.md](./2026-02-15-email-management.md) - **Status**: In Progress
  - Gmail cleanup, label management, and automation
  - **Features**: 2

## Plans by Status

### 🟢 Completed
_None yet_

### 🟡 In Progress
- [Documentation System](./2025-02-15-documentation-system.md) - Infrastructure for docs
- [Email Management](./2026-02-15-email-management.md) - Gmail cleanup and automation

### 🔵 Approved
- [Documentation Project Structure](./2025-02-15-docs-project-structure.md)

### ⚪ In Review
_None yet_

### 📝 Draft / Planning
_None yet_

## Plan Types

### Implementation Plans
Step-by-step execution plans for complex tasks:
- Clear phases with checkpoints
- Safety features and rollback strategies
- Success criteria for each step
- Located in `/plans/`

### Feature Requests
Individual feature proposals with:
- Current state and problem statement
- User journey diagrams
- Technical architecture
- Requirements and success criteria
- Template: [feature-request-template.md](./feature-request-template.md)

### Projects
High-level initiatives containing multiple features:
- Problem space and goals
- Feature dependency graphs
- System architecture
- Risk assessment
- Milestones and timeline
- Template: [project-template.md](./project-template.md)

## How to Add New Plans

### Implementation Plan
```bash
# Create in /plans/ with descriptive name
/plans/email-cleanup-automation.md
```

### Feature Request
1. Copy [feature-request-template.md](./feature-request-template.md)
2. Name it: `YYYY-MM-DD-feature-name.md`
3. Fill out all sections
4. Link to parent project
5. Add to this index

### Project Document
1. Copy [project-template.md](./project-template.md)
2. Name it: `YYYY-MM-DD-project-name.md`
3. Fill out all sections
4. Create related feature requests
5. Add to this index

## Project Categories

- **🏗️ Infrastructure & Tools** - Core system improvements
- **🤖 AI & Automation** - AI integrations and autonomous features
- **📊 Data & Analytics** - Data processing and analysis tools
- **🔌 Integrations** - External service integrations
- **📱 User Experience** - UI/UX improvements
- **📧 Email & Communication** - Email management and automation

## Templates

- [feature-request-template.md](./feature-request-template.md) - Feature request format with diagrams
- [project-template.md](./project-template.md) - Project documentation format with architecture

## Related

- [Documentation Hub](../docs/README.md)
- [Exobrain README](../README.md)
- [Creating Plans Skill](../.claude/skills/creating-plans/SKILL.md)
