## Project: [Project Name]

**Category**: [Infrastructure & Tools / AI & Automation / Data & Analytics / Integrations / User Experience]

TODAY: [Month Day Year]

---

### Overview

[High-level description of what this project aims to accomplish]

---

### Problem Space

**What problems are we solving?**

- [Problem 1]
- [Problem 2]
- [Problem 3]

**Who is affected?**

- [User group 1]
- [User group 2]

---

### Goals

**Primary Goals**:

- [ ] [Main objective 1]
- [ ] [Main objective 2]
- [ ] [Main objective 3]

**Success Metrics**:

- [How we'll measure success 1]
- [How we'll measure success 2]

---

### Scope

**In Scope**:

- [What's included 1]
- [What's included 2]
- [What's included 3]

**Out of Scope**:

- [What's not included 1]
- [What's not included 2]

---

### Related Features

**Feature Dependency Graph**:
```mermaid
graph TD
    %% Core features that others depend on
    Auth[User Authentication] --> Profile[User Profile]
    Auth --> Perms[Permission System]

    %% Feature dependencies
    Profile --> Settings[User Settings]
    Perms --> Admin[Admin Panel]
    Settings --> Notify[Notifications]
    Admin --> Analytics[Analytics Dashboard]

    %% Feature groups
    Notify --> Email[Email Integration]
    Notify --> Push[Push Notifications]

    %% Status styling
    classDef completed fill:#90EE90,stroke:#006400,stroke-width:2px
    classDef inProgress fill:#FFD700,stroke:#FF8C00,stroke-width:2px
    classDef planned fill:#87CEEB,stroke:#4682B4,stroke-width:2px

    %% Apply status (customize based on actual status)
    class Auth,Profile completed
    class Perms,Settings inProgress
    class Admin,Analytics,Notify,Email,Push planned

    %% Modify this graph to show your actual features and dependencies
    %% Update the status classes as features progress
```

Features that are part of this project:

- [ ] [Feature 1] - [Status]
  - Link: `../features/YYYY-MM-DD-feature-name.md`
- [ ] [Feature 2] - [Status]
  - Link: `../features/YYYY-MM-DD-feature-name.md`
- [ ] [Feature 3] - [Status]
  - Link: `../features/YYYY-MM-DD-feature-name.md`

---

### Technical Architecture

**System Architecture Diagram**:
```mermaid
graph TB
    subgraph "Client Layer"
        Web[Web Application<br/>React/Vue/Angular]
        Mobile[Mobile Apps<br/>iOS/Android]
        CLI[CLI Tool<br/>Node/Python]
    end

    subgraph "API Gateway"
        Gateway[API Gateway<br/>Rate Limiting, Auth]
    end

    subgraph "Service Layer"
        Auth[Auth Service<br/>JWT/OAuth]
        Core[Core API<br/>Business Logic]
        Worker[Background Workers<br/>Async Processing]
        Webhook[Webhook Service<br/>Event Handling]
    end

    subgraph "Data Layer"
        DB[(Primary Database<br/>PostgreSQL/MySQL)]
        Cache[(Cache Layer<br/>Redis)]
        Queue[Message Queue<br/>RabbitMQ/SQS]
        Storage[File Storage<br/>S3/MinIO]
    end

    subgraph "External Services"
        Email[Email Service<br/>SendGrid/SES]
        Payment[Payment Gateway<br/>Stripe/PayPal]
        Analytics[Analytics<br/>Mixpanel/GA]
        Monitor[Monitoring<br/>Datadog/Sentry]
    end

    %% Client connections
    Web --> Gateway
    Mobile --> Gateway
    CLI --> Gateway

    %% Gateway to services
    Gateway --> Auth
    Gateway --> Core

    %% Service interactions
    Core --> DB
    Core --> Cache
    Core --> Queue
    Core --> Storage
    Auth --> DB
    Auth --> Cache

    %% Worker processes
    Queue --> Worker
    Worker --> Email
    Worker --> Webhook

    %% External integrations
    Core --> Payment
    Core --> Analytics
    Gateway --> Monitor

    %% Modify this architecture to match your actual system design
    %% Add or remove layers and services as needed
```

**Key Components**:

- [Component 1] - [Description]
- [Component 2] - [Description]

**Dependencies**:

- [External dependency 1]
- [External dependency 2]

**Technology Stack**:

- [Technology 1]
- [Technology 2]

---

### Milestones

**Phase 1**: [Name] - [Target Date]
- [ ] [Deliverable 1]
- [ ] [Deliverable 2]

**Phase 2**: [Name] - [Target Date]
- [ ] [Deliverable 1]
- [ ] [Deliverable 2]

**Phase 3**: [Name] - [Target Date]
- [ ] [Deliverable 1]
- [ ] [Deliverable 2]

---

### Risks & Mitigation

**Risk Assessment Matrix**:
```mermaid
graph TB
    subgraph "🔴 Critical - High Impact / High Likelihood"
        R1[Data Security Breach<br/>Implement encryption & auditing]
        R2[API Rate Limits<br/>Add caching & throttling]
    end

    subgraph "🟠 High - High Impact / Low Likelihood"
        R3[Complete System Failure<br/>Multi-region deployment]
        R4[Key Vendor Dependency<br/>Maintain fallback options]
    end

    subgraph "🟡 Medium - Low Impact / High Likelihood"
        R5[Minor UI Bugs<br/>Comprehensive testing]
        R6[Performance Issues<br/>Monitoring & optimization]
    end

    subgraph "🟢 Low - Low Impact / Low Likelihood"
        R7[Documentation Gaps<br/>Regular doc reviews]
        R8[Config Drift<br/>Infrastructure as Code]
    end

    %% Styling
    classDef critical fill:#ff6b6b,stroke:#d92121,stroke-width:3px,color:#fff
    classDef high fill:#ffa94d,stroke:#fd7e14,stroke-width:2px
    classDef medium fill:#ffd43b,stroke:#fab005,stroke-width:2px
    classDef low fill:#8ce99a,stroke:#51cf66,stroke-width:2px

    class R1,R2 critical
    class R3,R4 high
    class R5,R6 medium
    class R7,R8 low

    %% Update risks to match your project's actual risk assessment
    %% Move risks between quadrants as likelihood/impact changes
```

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| [Risk 1] | High/Medium/Low | High/Medium/Low | [How to address] |
| [Risk 2] | High/Medium/Low | High/Medium/Low | [How to address] |

---

### Resources

**Documentation**:
- [Link to relevant docs]
- [Link to design docs]

**Related Projects**:
- [Link to related project]

**External References**:
- [Link to external resource]

---

### Team

**Project Lead**: [Name]
**Contributors**: [Names]
**Stakeholders**: [Names]

---

**Created**: [YYYY-MM-DD]
**Last Updated**: [YYYY-MM-DD]
**Status**: [Planning / In Progress / On Hold / Complete]
**Priority**: [Low / Medium / High / Critical]