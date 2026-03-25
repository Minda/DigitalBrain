# Standard Project Template Structure

<!-- Notion Template Reference -->
<!-- Template: P | PROJECT_TEMPLATE -->
<!-- URL: https://www.notion.so/mindamyers/P-PROJECT_TEMPLATE-31f3caf373e08041a6c0db48b2a0bb2b -->
<!-- Template ID: 31f3caf373e08041a6c0db48b2a0bb2b -->

All projects in the Q1 Projects | 2026 database use this consistent structure:

## Full Template

```markdown
::: callout {icon="/icons/verified_gray.svg" color="gray_bg"}
### Objective
---
<What this project accomplishes>
:::

<columns>
  <column>
    ::: callout {icon="/icons/target_gray.svg" color="gray_bg"}
    ### Goals
    ---
    1. Goal X and how it accomplishes the objective
    2. Goal Y and how it accomplishes the objective
    3. Goal Z and how it accomplishes the objective
    :::
  </column>
  <column>
    ::: callout {icon="/icons/list_gray.svg" color="gray_bg"}
    ### Deliverables
    ---
    - How X will be accomplished
    - How Y will be accomplished
    - How Z will be accomplished
    :::
  </column>
</columns>

<columns>
  <column>
    ::: callout {icon="/icons/link_gray.svg" color="gray_bg"}
    ### Links
    ---
    - [Link name](url)
    :::
  </column>
  <column>
    ::: callout {icon="/icons/book_gray.svg" color="gray_bg"}
    ### Pages
    ---
    <page url="...">Related Page</page>
    :::
  </column>
</columns>

<columns>
  <column>
    ::: callout {icon="/icons/checklist_gray.svg" color="gray_bg"}
    ### TODO
    ---
    **Category 1:**
    - [ ] Task 1
    - [ ] Task 2

    **Category 2:**
    - [ ] Task 3
    :::
  </column>
  <column>
    ::: callout {icon="/icons/arrow-right_gray.svg" color="gray_bg"}
    ### Key Decisions
    ---
    - *2026-03-09* | Decision description
    :::
  </column>
</columns>

::: callout {icon="/icons/list-indent_gray.svg" color="gray_bg"}
**Table of Contents**
---
<table_of_contents color="gray"/>
:::

---

<columns>
  <column>
    # Work Log
    ...
  </column>
  <column>
    # Implementation Notes
    ...
  </column>
</columns>

---
# Open Questions
```

## Template Sections

### Objective (Required)
**Purpose:** What this project accomplishes
**Format:** Single paragraph or 2-3 bullet points
**Icon:** `/icons/verified_gray.svg`

### Goals (Required)
**Purpose:** 3 goals and how each accomplishes the objective
**Format:** Numbered list with explanations
**Icon:** `/icons/target_gray.svg`

### Deliverables (Required)
**Purpose:** Concrete outputs that will be produced
**Format:** Bulleted list
**Icon:** `/icons/list_gray.svg`

### Links (Optional)
**Purpose:** External resources, documents, repos
**Format:** Markdown links
**Icon:** `/icons/link_gray.svg`

### Pages (Optional)
**Purpose:** Child Notion pages related to this project
**Format:** `<page url="...">Title</page>`
**Icon:** `/icons/book_gray.svg`

### TODO (Optional but recommended)
**Purpose:** Actionable task list organized by category
**Format:** Checkboxes grouped under category headings
**Icon:** `/icons/checklist_gray.svg`

### Key Decisions (Recommended)
**Purpose:** Date-stamped decision log
**Format:** `- *YYYY-MM-DD* | Decision description`
**Icon:** `/icons/arrow-right_gray.svg`

### Work Log (Optional)
**Purpose:** Chronological record of work done
**Format:** Free-form, often dated entries

### Implementation Notes (Optional)
**Purpose:** Technical details, code snippets, approaches tried
**Format:** Free-form with code blocks

### Open Questions (Optional)
**Purpose:** Unanswered questions, blockers, unknowns
**Format:** Bulleted list

## Filling the Template

When creating a new project, replace placeholders:

**Objective callout:**
```markdown
::: callout {icon="/icons/verified_gray.svg" color="gray_bg"}
### Objective
---
<Actual objective from user>
:::
```

**Goals:**
```markdown
1. <Goal 1> — <how it accomplishes objective>
2. <Goal 2> — <how it accomplishes objective>
3. <Goal 3> — <how it accomplishes objective>
```

**Deliverables:**
```markdown
- <Deliverable 1>
- <Deliverable 2>
- <Deliverable 3>
```

**TODOs:**
```markdown
**Category:**
- [ ] Task 1
- [ ] Task 2
```

**Key Decisions:**
```markdown
- *<today's date>* | Created this project
```
