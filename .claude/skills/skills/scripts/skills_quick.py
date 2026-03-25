#!/usr/bin/env python3
"""
Ultra-fast skills display using pre-computed data.
Run extract_commands.py refresh to regenerate the data.
"""

import sys

# Pre-computed skills data (run extract_commands.py refresh to update)
SKILLS_TREE = """Skills
├── 📝 Content & Writing
│   ├── adding-cheatsheets: /cheatsheets, "add this cheatsheet"
│   ├── creating-ascii-drawings: [no commands]
│   ├── download-url: "download url", "download article", "save this article", ...
│   ├── hypercontext: /hypercontext, /hypercontext compact, /hypercontext threads, ...
│   ├── research-synthesis: "research this", "synthesize these sources"
│   ├── saving-drawings: /memories, /drawings
│   ├── skill-creator: [no commands]
│   ├── writing-adding-footnotes: "add footnotes,", "add citations,"
│   ├── writing-documentation: /web, "document this", "create docs for", ...
│   ├── writing-drafting-article: [no commands]
│   ├── writing-style: [no commands]
│   └── writing-substack: [no commands]
├── 🧠 Memory & Learning
│   ├── agent-customizing-content: "customize this for me", "what's relevant here", "personal relevance"
│   ├── course-learning-panels: "panel discussion", "have them review", "multi-agent coursework"
│   ├── learning: /learnings, /learnings reflect, /learnings load, ...
│   ├── loading-memories: "reorient me", "load memories", "where did we leave off"
│   ├── recognizing-grounding: [no commands]
│   ├── saving-memories: "carry it forward,", "save as a memory,", "add to memories,"
│   ├── self-regulation: [no commands]
│   ├── waking-up: "wake up"
│   └── wrapping-up: "let's wrap up"
├── 🤖 AI & Agents
│   └── agents-spinning-up: "calibrate agents", "spin up agents"
├── 🔧 Development & Tools
│   ├── analyze-architecture: "analyze architecture", "what's the structure of this project"
│   ├── committing-work: "commit", "git commit", "commit my changes"
│   ├── excalidraw: [no commands]
│   ├── getting-file-view-links: [no commands]
│   └── skill-optimization: "optimize skill", "refine skill", "improve skill performance"
├── 🎓 Education
│   ├── bluedot-courses: [no commands]
│   └── courses: [no commands]
├── ⚙️ System
│   ├── context: [no commands]
│   ├── editing-relational-context: [no commands]
│   └── updating-constitution: [no commands]
├── 🔮 Other
│   ├── conversational-history: [no commands]
│   ├── creating-plans: [no commands]
│   ├── de-ai: [no commands]
│   ├── optimizing-images: [no commands]
│   ├── para: [no commands]
│   └── rename: [no commands]
├── 📊 Planning & Organization
│   ├── conversations-manage: "name conversation", "manage conversations", "list recent conversations", ...
│   ├── fetching-notion-content: "Notion", "find in Notion", "check my notes", ...
│   ├── gtd: /day, "let's plan my week/day", "help me prioritize", ...
│   ├── importing-conversations: [no commands]
│   ├── notion-projects: "create a Notion project", "add a project", "track this in Notion", ...
│   ├── notion-weekly-reports: /research, /reading, "weekly report", ...
│   ├── skills: /skills for, /skills compact, /skills tree, ...
│   └── week: "new week", "start my week", "weekly setup", ...
└── 🌐 Web & Integration
    ├── email-clothing-classifier: [no commands]
    ├── managing-email: [no commands]
    ├── notion-edits: [no commands]
    ├── playwright-downloading-courses: [no commands]
    ├── youtube-digesting-videos: "digest these videos", "watch these for me"
    └── youtube-fetching-transcripts: [no commands]"""

SKILLS_COMPACT = """Skills Quick Reference
━━━━━━━━━━━━━━━━━━━━━━━━━━
adding-cheatsheets: /cheatsheets | "add this cheatsheet"
agent-customizing-content: "customize this for me" | "what's relevant here" | "personal relevance"
agents-spinning-up: "calibrate agents" | "spin up agents"
analyze-architecture: "analyze architecture" | "what's the structure of this project"
committing-work: "commit" | "git commit" | "commit my changes"
conversations-manage: "name conversation" | "manage conversations" | "list recent conversations" | ...
course-learning-panels: "panel discussion" | "have them review" | "multi-agent coursework"
download-url: "download url" | "download article" | "save this article" | ...
fetching-notion-content: "Notion" | "find in Notion" | "check my notes" | ...
gtd: /day | "let's plan my week/day" | "help me prioritize" | ...
hypercontext: /hypercontext | /hypercontext compact | /hypercontext threads | ...
learning: /learnings | /learnings reflect | /learnings load | ...
loading-memories: "reorient me" | "load memories" | "where did we leave off"
notion-projects: "create a Notion project" | "add a project" | "track this in Notion" | ...
notion-weekly-reports: /research | /reading | "weekly report" | ...
research-synthesis: "research this" | "synthesize these sources"
saving-drawings: /memories | /drawings
saving-memories: "carry it forward," | "save as a memory," | "add to memories,"
skill-optimization: "optimize skill" | "refine skill" | "improve skill performance"
skills: /skills for | /skills compact | /skills tree | ...
waking-up: "wake up"
week: "new week" | "start my week" | "weekly setup" | ...
wrapping-up: "let's wrap up"
writing-adding-footnotes: "add footnotes," | "add citations,"
writing-documentation: /web | "document this" | "create docs for" | ...
youtube-digesting-videos: "digest these videos" | "watch these for me"

Total: 52 skills"""

def main():
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == 'compact':
            print(SKILLS_COMPACT)
        elif command == 'tree':
            print(SKILLS_TREE)
        elif command == 'refresh':
            print("Run: python3 extract_commands.py > skills_data.txt")
            print("Then update the constants in this file")
        else:
            print(f"Unknown command: {command}")
            print("Usage: skills_quick.py [compact|tree]")
    else:
        # Show full reference by running the main script
        import subprocess
        subprocess.run(['python3', 'extract_commands.py'], cwd='/Users/min/Documents/Projects/DigitalBrain/.claude/skills/skills/scripts')

if __name__ == '__main__':
    main()