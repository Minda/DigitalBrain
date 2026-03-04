# Web Applications Documentation

**All documentation for web applications should be contained in this `/docs/web` directory.**

This directory tracks the evolution, features, and changes for all web applications in the Exobrain project.

## Purpose

- **Feature Documentation**: Comprehensive specs for each web app feature
- **Change Logs**: Historical record of updates, modifications, and improvements
- **Architecture**: System design, component relationships, and data flows
- **API Documentation**: Endpoint specs, request/response formats, authentication

## Structure

```
docs/web/
├── README.md              # This file
├── jobs/                  # Job board application
│   ├── README.md          # Overview and architecture
│   ├── CHANGELOG.md       # Feature change log
│   ├── features/          # Individual feature docs
│   └── api/               # API documentation
└── [other-apps]/          # Future web applications
```

## Feature Change Logs

Each web application should maintain a **CHANGELOG.md** that tracks:

- **Feature Additions**: New functionality, components, or capabilities
- **Updates**: Modifications to existing features
- **Bug Fixes**: Resolved issues and patches
- **Architecture Changes**: System design updates
- **Breaking Changes**: API or behavior changes that affect usage

### Change Log Format

```markdown
# [App Name] Change Log

## [Feature Name]

### [Date] - [Type: Added/Updated/Fixed/Changed]
**Description**: Brief summary of the change

**Details**:
- Specific changes made
- Files affected
- Rationale for the change

**Impact**:
- User-facing changes
- API changes
- Performance implications

---
```

## Example: Job Board Application

The job board (`app/web`) is fully documented in `docs/web/jobs/`:

### Documentation Structure
- **[README.md](./jobs/README.md)** - Architecture, CLI reference, database schema
- **[CHANGELOG.md](./jobs/CHANGELOG.md)** - Complete feature history with dated entries
- **[features/deletion.md](./jobs/features/deletion.md)** - Job deletion feature documentation

### Features Documented
- Job scraping (Hacker News, 80,000 Hours)
- Job deletion with flexible filtering
- Database schema and shared SQLite access
- CLI commands (scrape, delete)
- MCP tools for Claude
- Testing strategy

### Each Feature Tracks
1. **Initial Implementation**: When and why it was added
2. **Iterations**: Improvements and refinements over time
3. **Technical Decisions**: Architecture choices and trade-offs
4. **Known Issues**: Current limitations or bugs
5. **Future Enhancements**: Planned improvements

## Documentation Guidelines

### When Adding Features
1. Create a feature document in `docs/web/[app]/features/`
2. Add an entry to the CHANGELOG.md
3. Update the app's README.md with the new feature
4. Document any API changes

### When Updating Features
1. Update the feature document
2. Add a dated entry to the CHANGELOG.md
3. Note breaking changes prominently
4. Update related documentation

### What to Document
- **User-Facing Changes**: New UI, modified behavior, added capabilities
- **Technical Changes**: Refactors, optimizations, architecture updates
- **Bug Fixes**: Resolved issues, edge cases handled
- **Configuration**: Environment variables, settings, deployment changes

### What NOT to Document Here
- **Implementation Plans**: Use `/plans/` directory
- **Temporary Notes**: Use project management tools
- **Code Comments**: Keep in source files

## Quick Start

To document a new web app feature:

1. Create the app directory: `docs/web/[app-name]/`
2. Add README.md with app overview
3. Create CHANGELOG.md
4. Document the initial feature set
5. Maintain change log with each update

## Related Documentation

- **`/docs/projects/`**: High-level project documentation
- **`/docs/features/`**: Cross-cutting feature requests
- **`/plans/`**: Implementation plans and technical architecture
- **`app/web/`**: Source code for web applications

## Principles

1. **Completeness**: Document all significant changes
2. **Clarity**: Write for future you and other developers
3. **Timeliness**: Update docs when making changes, not later
4. **Traceability**: Link features to commits, PRs, and issues
5. **User-Centric**: Explain impact, not just implementation
