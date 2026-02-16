# Documentation Hub

Welcome to the Exobrain documentation system. This directory contains structured documentation for projects, features, and other system components.

## Mermaid Diagram Support

Our documentation templates include **Mermaid diagrams** to help visualize:
- 🔄 **User workflows and journeys** - Step-by-step interaction flows
- 🏗️ **System architecture** - Component relationships and data flow
- 📊 **Feature dependencies** - Implementation order and relationships
- ⚠️ **Risk assessments** - Visual prioritization matrices
- 🔀 **State transitions** - Feature lifecycle and edge cases

These diagrams are included as examples in the templates - customize or remove them based on your needs.

## Structure

### 📁 features/
Feature requests and enhancement proposals. Each feature is linked to a parent project.

- **Format**: `YYYY-MM-DD-feature-name.md`
- **Template**: See `features/feature-request-template.md`
- **Purpose**: Track specific features, enhancements, and user requests

### 📁 projects/
High-level project documentation. Projects contain multiple related features.

- **Format**: `YYYY-MM-DD-project-name.md`
- **Template**: See `projects/project-template.md`
- **Purpose**: Define project scope, goals, and track related features

## Relationship Model

```
Project (one)
    └── Features (many)
```

Each **Project** can have multiple **Features**. Features should reference their parent project, and projects should list their related features.

## How It Differs From `/plans/`

- **`/plans/`** - Implementation plans, technical architecture, coding roadmaps
- **`/docs/projects/`** - Project documentation, scope, goals, feature tracking
- **`/docs/features/`** - Individual feature requests and enhancements

## Quick Links

- [Features Index](./features/README.md)
- [Projects Index](./projects/README.md)
- [Feature Request Template](./features/feature-request-template.md)
- [Project Template](./projects/project-template.md)

## Contributing

When adding new documentation:

1. Use the appropriate template
2. Follow the `YYYY-MM-DD-name` naming convention
3. Link features to their parent project
4. Update the relevant index file