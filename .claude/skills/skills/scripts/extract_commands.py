#!/usr/bin/env python3
"""
Extract and display skill commands in various formats.
Part of the /skills command skill.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class SkillInfo:
    name: str
    description: str
    commands: List[str]
    category: str

class SkillCommandExtractor:
    """Extract commands from skill files and format for display."""

    # Category mappings based on skill names/purposes
    CATEGORIES = {
        '📝 Content & Writing': [
            'writing', 'documentation', 'footnotes', 'drawings', 'ascii',
            'cheatsheets', 'substack', 'article'
        ],
        '🧠 Memory & Learning': [
            'learning', 'memories', 'memory', 'grounding', 'insights',
            'saving-memories', 'loading-memories', 'carried-forward'
        ],
        '📊 Planning & Organization': [
            'gtd', 'week', 'planning', 'projects', 'todo', 'organize',
            'conversations-manage', 'weekly'
        ],
        '🔧 Development & Tools': [
            'commit', 'git', 'architecture', 'analyze', 'optimization',
            'skill-creator', 'skill-optimization', 'debug'
        ],
        '🌐 Web & Integration': [
            'notion', 'download', 'fetch', 'web', 'url', 'email',
            'youtube', 'gmail'
        ],
        '🤖 AI & Agents': [
            'agent', 'spinning', 'calibration', 'customizing', 'panel',
            'synthesis', 'multi-agent'
        ],
        '📈 Visualization': [
            'hypercontext', 'excalidraw', 'diagram', 'visual', 'ascii',
            'drawing'
        ],
        '🎓 Education': [
            'course', 'learning-panels', 'research', 'synthesis', 'digest',
            'bluedot'
        ],
        '⚙️ System': [
            'waking', 'wrapping', 'context', 'relational', 'constitution',
            'self-regulation', 'recognizing'
        ]
    }

    def __init__(self, skills_dir: Path = None):
        self.skills_dir = skills_dir or Path('.claude/skills')

    def categorize_skill(self, name: str, description: str) -> str:
        """Determine category for a skill based on name and description."""
        combined = f"{name} {description}".lower()

        for category, keywords in self.CATEGORIES.items():
            for keyword in keywords:
                if keyword in combined:
                    return category

        return '🔮 Other'

    def extract_commands(self, content: str, description: str) -> List[str]:
        """Extract command patterns from skill content."""
        commands = []
        seen = set()

        # Extract slash commands
        slash_cmds = re.findall(r'/[\w-]+(?:\s+[\w-]+)?', description)
        for cmd in slash_cmds:
            cmd = cmd.strip()
            if cmd and cmd not in seen:
                commands.append(cmd)
                seen.add(cmd)

        # Extract quoted triggers
        quoted = re.findall(r'"([^"]+)"', description)
        for q in quoted:
            q = q.strip()
            if (q and q not in seen and
                not q.startswith('/') and
                3 < len(q) < 40 and
                not any(x in q for x in ['.', '(', ')', ':', '{', '}', '[', ']', ';'])):
                commands.append(f'"{q}"')
                seen.add(q)

        # Look in content for command definitions
        if '## Commands' in content or '## Command' in content:
            # Extract commands from markdown tables
            table_cmds = re.findall(r'\|\s*`?(/[\w-]+[^`|]*)`?\s*\|', content)
            for cmd in table_cmds:
                cmd = cmd.strip().strip('`')
                if cmd and cmd not in seen:
                    commands.append(cmd)
                    seen.add(cmd)

        return commands[:6]  # Limit to 6 commands per skill

    def extract_brief_description(self, description: str) -> str:
        """Extract a brief description from the full description."""
        # Take the first sentence or clause
        desc = description.split('. ')[0]
        desc = desc.split(', ')[0]

        # Remove trigger examples
        desc = re.sub(r'Use when.*$', '', desc)
        desc = re.sub(r'Triggers on.*$', '', desc)
        desc = re.sub(r'Also when.*$', '', desc)

        # Truncate if still too long
        if len(desc) > 60:
            desc = desc[:57] + '...'

        return desc.strip()

    def load_skills(self) -> List[SkillInfo]:
        """Load all skills from the skills directory."""
        skills = []

        for skill_file in sorted(self.skills_dir.glob('*/SKILL.md')):
            try:
                with open(skill_file) as f:
                    content = f.read()

                # Extract metadata
                name_match = re.search(r'^name: (.+)$', content, re.MULTILINE)
                name = name_match.group(1) if name_match else skill_file.parent.name

                desc_match = re.search(r'^description: (.+)$', content, re.MULTILINE)
                description = desc_match.group(1) if desc_match else ''

                # Extract commands
                commands = self.extract_commands(content, description)

                # Categorize
                category = self.categorize_skill(name, description)

                # Create skill info
                skill = SkillInfo(
                    name=name,
                    description=self.extract_brief_description(description),
                    commands=commands,
                    category=category
                )

                skills.append(skill)

            except Exception as e:
                print(f"Warning: Failed to process {skill_file}: {e}", file=sys.stderr)
                continue

        return skills

    def format_default(self, skills: List[SkillInfo]) -> str:
        """Format skills in hybrid tree+box view."""
        output = []
        output.append("Skills Command Reference")
        output.append("━" * 55)
        output.append("")

        # Group by category
        by_category = defaultdict(list)
        for skill in skills:
            by_category[skill.category].append(skill)

        # Sort categories
        category_order = list(self.CATEGORIES.keys()) + ['🔮 Other']

        for category in category_order:
            if category not in by_category:
                continue

            output.append(f"├── {category}")
            output.append("│   ┌" + "─" * 68 + "┐")

            for skill in by_category[category]:
                output.append(f"│   │ {skill.name:<66} │")

                if skill.commands:
                    # Primary command with description
                    primary = skill.commands[0].strip('"')
                    output.append(f"│   │   └─ {primary} — {skill.description:<40} │")

                    # Additional commands
                    if len(skill.commands) > 1:
                        others = " | ".join(skill.commands[1:4])
                        if len(skill.commands) > 4:
                            others += " | ..."
                        output.append(f"│   │      Also: {others:<49} │")
                else:
                    output.append(f"│   │   └─ [no commands defined]                                   │")

                output.append(f"│   │{' ' * 68}│")

            # Remove last empty line and close box
            if output[-1].strip() == "│   │" + " " * 68 + "│":
                output.pop()
            output.append("│   └" + "─" * 68 + "┘")
            output.append("│")

        # Stats
        total_skills = len(skills)
        total_commands = sum(len(s.commands) for s in skills)
        output.append(f"Total: {total_skills} skills | {total_commands}+ commands")
        output.append("Use /skills compact for condensed view | /skills search <term> to filter")

        return "\n".join(output)

    def format_compact(self, skills: List[SkillInfo]) -> str:
        """Format skills in compact single-line view."""
        output = []
        output.append("Skills Quick Reference")
        output.append("━" * 55)

        for skill in sorted(skills, key=lambda s: s.name):
            if skill.commands:
                cmds = " | ".join(skill.commands[:4])
                if len(skill.commands) > 4:
                    cmds += " | ..."
                output.append(f"{skill.name}: {cmds}")

        output.append("")
        output.append(f"Total: {len(skills)} skills")

        return "\n".join(output)

    def format_tree(self, skills: List[SkillInfo]) -> str:
        """Format skills in pure tree view."""
        output = []
        output.append("Skills")

        # Group by category
        by_category = defaultdict(list)
        for skill in skills:
            by_category[skill.category].append(skill)

        categories = list(by_category.keys())

        for i, category in enumerate(categories):
            is_last_category = i == len(categories) - 1
            cat_prefix = "└── " if is_last_category else "├── "

            output.append(f"{cat_prefix}{category}")

            skills_in_cat = by_category[category]
            for j, skill in enumerate(skills_in_cat):
                is_last_skill = j == len(skills_in_cat) - 1

                if is_last_category:
                    skill_prefix = "    └── " if is_last_skill else "    ├── "
                else:
                    skill_prefix = "│   └── " if is_last_skill else "│   ├── "

                if skill.commands:
                    cmds = ", ".join(skill.commands[:3])
                    if len(skill.commands) > 3:
                        cmds += ", ..."
                    output.append(f"{skill_prefix}{skill.name}: {cmds}")
                else:
                    output.append(f"{skill_prefix}{skill.name}: [no commands]")

        return "\n".join(output)

    def search_skills(self, skills: List[SkillInfo], term: str) -> List[SkillInfo]:
        """Filter skills by search term."""
        term = term.lower()
        results = []

        for skill in skills:
            # Search in name, description, and commands
            searchable = f"{skill.name} {skill.description} {' '.join(skill.commands)}".lower()
            if term in searchable:
                results.append(skill)

        return results

    def format_search(self, skills: List[SkillInfo], term: str) -> str:
        """Format search results."""
        results = self.search_skills(skills, term)

        if not results:
            return f"No skills found matching '{term}'\nTry broadening your search or use /skills to see all."

        output = []
        output.append(f"Skills matching '{term}':")
        output.append("━" * 55)

        for skill in results:
            if skill.commands:
                cmds = " | ".join(skill.commands[:4])
                output.append(f"{skill.name}: {cmds}")
            else:
                output.append(f"{skill.name}: [no commands defined]")

            # Add description on next line if it mentions the search term
            if term in skill.description.lower():
                output.append(f"  └─ {skill.description}")

        output.append("")
        output.append(f"Found {len(results)} matching skills")

        return "\n".join(output)

def main():
    """Main entry point for the script."""
    extractor = SkillCommandExtractor()

    # Load all skills
    skills = extractor.load_skills()

    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == 'compact':
            print(extractor.format_compact(skills))
        elif command == 'tree':
            print(extractor.format_tree(skills))
        elif command == 'search' and len(sys.argv) > 2:
            search_term = ' '.join(sys.argv[2:])
            print(extractor.format_search(skills, search_term))
        else:
            print(f"Unknown command: {command}")
            print("Usage: extract_commands.py [compact|tree|search <term>]")
    else:
        # Default view
        print(extractor.format_default(skills))

if __name__ == '__main__':
    main()