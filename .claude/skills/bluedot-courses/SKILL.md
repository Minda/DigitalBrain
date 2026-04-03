# BlueDot Courses

Manages BlueDot-specific course information, structure, and resources. This skill stores URLs, course details, Notion notebook links, and other BlueDot-specific implementation details.

## Usage

Triggers:
- "BlueDot course"
- "BlueDot AI Alignment"
- "BlueDot resources"
- "BlueDot notebook"
- When working with BlueDot course materials

## Course Information

### Impact Course (2026)
**Course URL:** [Add course URL when available]
**Local Project:** `personal/projects/bluedot-impact/`
**Notion Project Page:** [Add Notion URL]
**Duration:** [Add duration]
**Start Date:** March 2026

**Key Materials:**
- Research Agenda: `personal/projects/bluedot-impact/109_concrete_problems_multiagent_safety.md`
- Moltbook Papers Analysis: `personal/projects/bluedot-impact/moltbook-analysis.md`
- Course Notes: `personal/projects/bluedot-impact/notes/`

### Technical AI Safety Project (2025)
**Course URL:** https://bluedot.org/courses/technical-ai-safety-project/1/1
**Local Project:** `personal/projects/bluedot-ai-safety-project/`
**Notion Project Page:** https://www.notion.so/mindamyers/P-BlueDot-Technical-AI-Safety-Project-3173caf373e081dfa19ad055f38b20e4
**Duration:** [Add duration]
**Start Date:** [Add start date]

**Course Structure:**
- Unit 1: [Title]
  - Resources: [URLs]
  - Assignments: [Details]
- Unit 2: [Title]
  - Resources: [URLs]
  - Assignments: [Details]
- [Continue with units...]

**Notion Notebooks:**
- Main Project Page: https://www.notion.so/mindamyers/P-BlueDot-Technical-AI-Safety-Project-3173caf373e081dfa19ad055f38b20e4
- Unit Notes: [Notion URLs]
- Assignment Submissions: [Notion URLs]
- Discussion Notes: [Notion URLs]

### Frontier AI Governance (2025)
**Course URL:** https://bluedot.org/courses/ai-governance/1/1
**Local Project:** `personal/projects/bluedot-frontier-governance/`
**Notion Project Page:** [Add Notion URL]
**Duration:** [Add duration]
**Start Date:** [Add start date]

**Course Structure:**
- Unit 1: [Title]
  - Resources: [URLs]
  - Assignments: [Details]
- Unit 2: [Title]
  - Resources: [URLs]
  - Assignments: [Details]
- [Continue with units...]

**Notion Notebooks:**
- Main Course Page: [Notion URL]
- Unit Notes: [Notion URLs]
- Assignment Submissions: [Notion URLs]
- Discussion Notes: [Notion URLs]

### Course Resources
**Key Downloads:**
- Course syllabus: `downloads/bluedot/syllabus.pdf`
- Reading materials: `downloads/bluedot/readings/`
- Lecture slides: `downloads/bluedot/slides/`

**Important Links:**
- Discussion forum: [URL]
- Office hours: [Schedule/URL]
- Course calendar: [URL]

## Workflow Integration

This skill works with the general `courses` skill to:
1. Provide BlueDot-specific URLs and resources
2. Map course structure to the general workflow
3. Connect to Notion notebooks for note-taking
4. Track BlueDot-specific assignments and deadlines

## Data Storage

**Local Storage:**
```
downloads/bluedot/
├── ai-alignment-2025/
│   ├── syllabus.pdf
│   ├── units/
│   │   ├── unit1/
│   │   ├── unit2/
│   │   └── ...
│   ├── readings/
│   ├── slides/
│   └── assignments/
└── [other-courses]/
```

**Notion Structure:**
```
BlueDot Courses/
├── AI Alignment 2025/
│   ├── Course Overview
│   ├── Unit Notes/
│   ├── Assignments/
│   ├── Discussion Notes/
│   └── Resources/
└── [Other Courses]/
```

## Course-Specific Commands

### Download Course Materials
```bash
# Download all materials for a unit
claude skill courses download-unit bluedot unit1

# Download specific resource
claude skill bluedot-courses download [resource-url]
```

### Access Notion Notes
```bash
# Open unit notes
claude skill bluedot-courses notion unit1

# Create new assignment page
claude skill bluedot-courses notion create-assignment [name]
```

## Integration Points

- **courses skill:** Provides the general workflow framework
- **course-learning-panels:** Processes course materials with expert panels
- **fetching-notion-content:** Retrieves and updates Notion notebooks
- **download-url:** Downloads course materials and readings

## Notes

- Keep course URLs and Notion links up to date
- Store sensitive course materials in `personal/` if needed
- Use this skill for BlueDot-specific details, not general course workflows