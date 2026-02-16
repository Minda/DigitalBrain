# Anthropic Skills to Consider When Creating a New Skill

**Source:** [https://github.com/anthropics/skills](https://github.com/anthropics/skills)

Before writing a new skill from scratch, check whether an existing skill in Anthropic's repo already covers the need—or can be extended. Install via Claude Code: `/plugin marketplace add anthropics/skills`, then install `document-skills` or `example-skills`.

## When to Use This Reference

- **Creating a new skill** — Scan the categories below; if one matches your use case, read that skill's SKILL.md in the repo first.
- **Extending document/file handling** — Prefer building on docx/pdf/pptx/xlsx if your task is creating or editing those formats.
- **MCP or tooling** — Check mcp-builder and web-artifacts-builder for patterns.
- **Design or comms** — Check brand-guidelines, frontend-design, internal-comms for structure and tone.

## Skills by Category

### Document creation & editing (source-available, production reference)

| Skill       | Use when… |
|------------|-----------|
| **docx**   | Creating or editing Word documents (.docx). |
| **pdf**    | Creating, editing, or extracting from PDFs (e.g. form fields). |
| **pptx**   | Creating or editing PowerPoint presentations. |
| **xlsx**   | Creating or editing Excel spreadsheets. |

These are more complex, production-style skills; use them as reference for structure and patterns, not necessarily to copy verbatim.

### Development & technical

| Skill                 | Use when… |
|-----------------------|-----------|
| **mcp-builder**       | Building or configuring MCP servers. |
| **web-artifacts-builder** | Generating web artifacts (HTML, etc.) in a structured way. |
| **webapp-testing**    | Testing web applications (e.g. browser-based flows). |

### Creative & design

| Skill                 | Use when… |
|-----------------------|-----------|
| **algorithmic-art**   | Generating algorithmic or procedural art. |
| **canvas-design**     | Designing or laying out canvas-style visuals. |
| **frontend-design**   | UI/frontend design and layout. |
| **theme-factory**     | Creating or managing themes (e.g. color, style). |
| **slack-gif-creator** | Creating GIFs for Slack or similar. |

### Enterprise & communication

| Skill               | Use when… |
|---------------------|-----------|
| **brand-guidelines** | Applying brand voice, tone, and style. |
| **internal-comms**   | Drafting or formatting internal communications. |
| **doc-coauthoring**  | Coauthoring or collaborative document workflows. |

### Skill authoring

| Skill            | Use when… |
|------------------|-----------|
| **skill-creator**| Creating or refining skills (official Anthropic version; compare with this repo's skill-creator for local conventions). |

## Suggested workflow when creating a new skill

1. **Match to category** — Find the row above that best matches your goal (documents, MCP, design, comms, etc.).
2. **Open that skill in the repo** — e.g. `https://github.com/anthropics/skills/tree/main/skills/<skill-name>`.
3. **Read its SKILL.md** — Note frontmatter, structure, and any scripts or references.
4. **Decide:** adopt/install that skill, fork and adapt it, or use it only as a pattern for your new skill.
5. **Use this skill-creator** — Follow the steps in SKILL.md (use case, components, init, write, package, iterate) so your skill fits this project's structure and the Agent Skills spec.

## Links

- Repo: https://github.com/anthropics/skills  
- Agent Skills standard: https://agentskills.io  
- Template: https://github.com/anthropics/skills/tree/main/template  
- Spec: https://github.com/anthropics/skills/tree/main/spec  
