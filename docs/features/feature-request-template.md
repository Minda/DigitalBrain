## Feature Request

**Feature Name**: [Short descriptive name]
**Project**: [Parent project name or link]

TODAY: [Month Day Year]

---

### Current State

Currently the app:

- [Describe current behavior 1]
- [Describe current behavior 2]
- [Describe current behavior 3]

---

### Goal

**Problem Statement**: [What problem does this solve for the user?]

**Proposed Solution**: [High-level description of how we'll solve it]

---

### Desired Behavior

[Describe how the feature should work]

**User Journey**:
```mermaid
flowchart TD
    Start([User initiates action]) --> Check{Has permission?}
    Check -->|Yes| Action[Perform main action]
    Check -->|No| Denied[Show error message]
    Action --> Validate{Input valid?}
    Validate -->|Yes| Process[Process request]
    Validate -->|No| Error[Show validation error]
    Error --> Action
    Process --> Result[Display results]
    Result --> End([Task completed])
    Denied --> End

    %% Customize this flow to match your feature's user journey
    %% Add decision points, actions, and outcomes as needed
```

**Requirements**:

- [ ] [Requirement 1]
- [ ] [Requirement 2]
- [ ] [Requirement 3]

**Nice to Have**:

- [ ] [Optional enhancement 1]
- [ ] [Optional enhancement 2]

**State Transitions** (if applicable):
```mermaid
stateDiagram-v2
    [*] --> Initial
    Initial --> Active: User activates
    Initial --> Disabled: Admin disables
    Active --> Processing: Submit action
    Processing --> Complete: Success
    Processing --> Error: Failure
    Error --> Active: Retry
    Complete --> Archived: After 30 days
    Archived --> [*]
    Disabled --> Active: Admin enables

    note right of Processing
        Async operation
        Show loading state
    end note

    %% Modify states and transitions to match your feature
    %% Add notes for important state behaviors
```

---

### Technical Context

**System Components**:
```mermaid
graph LR
    %% Frontend Layer
    UI[Web UI] -->|REST API| Gateway[API Gateway]
    Mobile[Mobile App] -->|REST API| Gateway

    %% Backend Services
    Gateway --> Auth[Auth Service]
    Gateway --> Core[Core Logic]
    Core -->|Query/Update| DB[(Database)]
    Core -->|Cache| Redis[(Redis Cache)]
    Core -->|Events| Queue[Message Queue]

    %% External Services
    Queue --> Email[Email Service]
    Core --> Storage[File Storage]
    Core --> Analytics[Analytics]

    %% Styling
    style UI fill:#e1f5ff
    style Mobile fill:#e1f5ff
    style DB fill:#ffe1e1
    style Redis fill:#ffe1e1
    style Email fill:#fff4e1
    style Storage fill:#fff4e1
    style Analytics fill:#fff4e1

    %% Customize components and connections for your feature
    %% Add or remove services as needed
```

**Relevant Files**:

- [file path 1]
- [file path 2]

**Related Docs**:

- [doc link 1]

**Database Changes**:

- [ ] New schema required? [Yes/No]
- [ ] Schema changes needed? [Yes/No]

---

### Documentation

- [ ] Add to feature docs in: [location]
- [ ] Update "last updated" date to today

---

### Open Questions

- [ ] [Question 1 - include options A, B, C if applicable]
- [ ] [Question 2]
- [ ] [Question 3]

---

### Approval Checklist

- [ ] Schema/DB changes reviewed
- [ ] Directory structure approved
- [ ] Technical approach agreed upon

---

**Requested By**: [Name]
**Date**: [YYYY-MM-DD]
**Priority**: [Low / Medium / High / Critical]
**Status**: [Draft / In Review / Approved / In Progress / Complete]