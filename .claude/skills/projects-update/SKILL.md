---
name: projects-update
description: Update the active projects registry. Use when starting new projects, changing priorities, or archiving completed work.
allowed-tools: [Read, Edit, Write]
---

# /projects - Project Registry Management

## Purpose
Manage the active projects registry that loads at startup to track ongoing work.

## Commands

### View Current Projects
```
/projects
/projects list
```
Shows the current active projects registry.

### Update Project Status
```
/projects update
```
Interactive update of project statuses and priorities.

### Add New Project
```
/projects add
```
Add a new project to the registry.

### Archive Project
```
/projects archive [project-name]
```
Move a project from active to archived status.

## Project Registry Structure

The registry (`personal/projects/ACTIVE_PROJECTS.md`) organizes projects by priority:

- **🔴 High Priority**: Active daily work
- **🟡 Medium Priority**: Weekly check-ins
- **🟢 Background**: As-needed maintenance

Each project entry includes:
- **Path**: Location in filesystem
- **Status**: Current state
- **Current Focus**: What's being worked on
- **Key Files**: Important documents
- **Next Steps**: Planned actions

## Update Protocol

Update the registry when:
1. Starting a new major project
2. Changing project priorities
3. Reaching project milestones
4. Archiving completed projects
5. Adding new key files or documentation

## Integration

This registry is automatically loaded by the `waking-up` skill at conversation start, providing immediate context about ongoing work without manual review.