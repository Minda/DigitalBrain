#!/usr/bin/env python3
"""
Analyze conversation content and suggest 4 meaningful titles
"""

import json
import re
from pathlib import Path
from collections import Counter
from datetime import datetime


def extract_conversation_features(conv_file):
    """Extract key features from conversation to build title suggestions"""

    features = {
        'tools_used': Counter(),
        'files_mentioned': set(),
        'directories': set(),
        'commands': Counter(),
        'skills': set(),
        'topics': [],
        'actions': Counter(),
        'errors': [],
        'questions': [],
        'first_message': "",
        'main_request': "",
        'key_terms': Counter()
    }

    with open(conv_file, 'r') as f:
        message_count = 0
        for line in f:
            try:
                data = json.loads(line.strip())
                message_count += 1

                # Get first user message as main context
                if message_count <= 5 and data.get('role') == 'user':
                    content = str(data.get('content', ''))
                    if len(content) > 20 and not features['first_message']:
                        features['first_message'] = content[:500]
                        # Extract main request from first message
                        features['main_request'] = extract_main_intent(content)

                # Analyze content for features
                if 'content' in data:
                    content = str(data['content'])

                    # Extract file paths
                    file_paths = re.findall(r'/[A-Za-z0-9_\-./]+\.[A-Za-z]{2,4}', content)
                    for path in file_paths:
                        features['files_mentioned'].add(Path(path).name)
                        if '/' in path:
                            features['directories'].add(Path(path).parent.name)

                    # Extract tool uses
                    if 'tool_calls' in data or '<invoke name=' in content:
                        tools = re.findall(r'<invoke name="([^"]+)"', content)
                        for tool in tools:
                            features['tools_used'][tool] += 1

                    # Extract skills
                    if 'Skill' in content or '/[a-z-]+' in content:
                        skills = re.findall(r'/([a-z][a-z\-]+)', content)
                        features['skills'].update(skills)

                    # Extract commands
                    if 'bash' in content.lower() or 'command' in content.lower():
                        cmds = re.findall(r'(?:git|npm|python|cargo|uv|ls|cd|mkdir|rm) [a-z\-]+', content.lower())
                        for cmd in cmds[:5]:  # Limit to avoid spam
                            features['commands'][cmd.split()[0]] += 1

                    # Extract key technical terms
                    tech_terms = re.findall(r'\b(?:AI|API|SQL|JSON|CLI|MCP|LLM|Claude|ChatGPT|BlueDot|Notion|GitHub|Docker|React|TypeScript|Python|Rust|database|server|frontend|backend|skill|agent|workflow|conversation)\b', content, re.IGNORECASE)
                    for term in tech_terms:
                        features['key_terms'][term.upper() if len(term) <= 4 else term.capitalize()] += 1

                    # Detect questions
                    if '?' in content and message_count <= 10:
                        questions = re.findall(r'[A-Z][^.?!]*\?', content)
                        features['questions'].extend(questions[:2])

                    # Detect actions/verbs
                    action_verbs = re.findall(r'\b(?:create|build|fix|update|rename|search|find|analyze|debug|implement|add|remove|delete|install|configure|setup|test|deploy)\b', content, re.IGNORECASE)
                    for verb in action_verbs:
                        features['actions'][verb.lower()] += 1

            except json.JSONDecodeError:
                continue

    return features


def extract_main_intent(content):
    """Extract the main intent from user's first message"""
    content_lower = content.lower()

    # Common patterns to identify main request
    patterns = [
        (r'(?:can you|could you|please|i want to|i need to|help me|let\'s|let me) ([^.?!]{10,50})', 1),
        (r'^([^.?!]{15,60})(?:[.?!]|$)', 1),
        (r'(?:how to|how do i|how can i) ([^.?!]{10,50})', 1),
        (r'(?:i\'m trying to|i want to|need to) ([^.?!]{10,50})', 1),
    ]

    for pattern, group in patterns:
        match = re.search(pattern, content_lower)
        if match:
            intent = match.group(group).strip()
            # Clean up the intent
            intent = re.sub(r'^(to |the |a |an )', '', intent)
            intent = re.sub(r'[,;:].*', '', intent)
            return intent[:60]

    # Fallback: use first sentence fragment
    first_sentence = re.split(r'[.?!]', content)[0]
    return first_sentence[:60] if first_sentence else "Conversation"


def generate_title_suggestions(features):
    """Generate 4 different title suggestions based on features"""
    suggestions = []

    # Title 1: Action + Primary Target
    # Format: "[Main Action] [Primary File/Directory/Skill]"
    if features['actions']:
        main_action = features['actions'].most_common(1)[0][0].capitalize()
        if features['skills']:
            target = f"{list(features['skills'])[0]} skill"
        elif features['files_mentioned']:
            target = list(features['files_mentioned'])[0]
        elif features['directories']:
            target = f"{list(features['directories'])[0]}/"
        else:
            target = "project files"
        suggestions.append(f"{main_action} {target}")

    # Title 2: Main Request Based
    # Format: Simplified version of what user asked for
    if features['main_request']:
        # Capitalize first word and key terms
        words = features['main_request'].split()
        title_words = []
        for word in words[:8]:  # Limit length
            if word.upper() in features['key_terms'] or word.capitalize() in features['key_terms']:
                title_words.append(word.upper() if len(word) <= 4 else word.capitalize())
            else:
                title_words.append(word)
        request_title = ' '.join(title_words)
        # Capitalize first letter
        if request_title:
            request_title = request_title[0].upper() + request_title[1:]
        suggestions.append(request_title)

    # Title 3: Tool/Tech Stack Focus
    # Format: "[Tech/Tool]: [Action/Purpose]"
    if features['key_terms']:
        top_terms = features['key_terms'].most_common(2)
        if top_terms:
            main_tech = top_terms[0][0]
            if features['actions']:
                action = features['actions'].most_common(1)[0][0]
                suggestions.append(f"{main_tech}: {action.capitalize()} implementation")
            elif len(top_terms) > 1:
                suggestions.append(f"{main_tech} + {top_terms[1][0]} integration")
            else:
                suggestions.append(f"{main_tech} configuration")

    # Title 4: Question-based (if user asked a question)
    # Format: Answer to "what was done"
    if features['questions']:
        # Convert question to statement
        question = features['questions'][0]
        question_lower = question.lower()
        if 'how' in question_lower:
            if features['actions']:
                verb = features['actions'].most_common(1)[0][0].capitalize()
                suggestions.append(f"{verb} guide & implementation")
        elif 'what' in question_lower or 'where' in question_lower:
            if features['files_mentioned']:
                suggestions.append(f"Exploring {list(features['files_mentioned'])[0]}")
            else:
                suggestions.append("Project exploration & analysis")
        elif 'can' in question_lower or 'could' in question_lower:
            suggestions.append(f"Feature feasibility: {features['main_request'][:30]}")

    # Fallback titles if we don't have enough
    fallback_titles = [
        f"Working with {list(features['directories'])[0] if features['directories'] else 'project'}",
        f"{features['tools_used'].most_common(1)[0][0] if features['tools_used'] else 'Development'} session",
        f"Project: {datetime.now().strftime('%b %d')} updates",
        "Technical implementation session"
    ]

    # Ensure we have 4 unique suggestions
    while len(suggestions) < 4:
        for fallback in fallback_titles:
            if fallback not in suggestions and len(suggestions) < 4:
                suggestions.append(fallback)

    # Clean up and truncate suggestions
    final_suggestions = []
    for i, title in enumerate(suggestions[:4]):
        # Clean up extra spaces, capitalize properly
        title = re.sub(r'\s+', ' ', title).strip()
        # Ensure first letter is capitalized
        if title:
            title = title[0].upper() + title[1:]
        # Truncate to reasonable length but keep meaningful
        if len(title) > 50:
            title = title[:47] + "..."
        final_suggestions.append(title)

    return final_suggestions


def suggest_conversation_titles(conversation_id=None):
    """Main function to suggest titles for a conversation"""

    # Get the Claude projects directory
    claude_dir = Path("/Users/min/.claude/projects/-Users-min-Documents-Projects-DigitalBrain")

    if conversation_id:
        conv_file = claude_dir / f"{conversation_id}.jsonl"
    else:
        # Find the most recent conversation
        conv_files = sorted(claude_dir.glob("*.jsonl"),
                          key=lambda x: x.stat().st_mtime,
                          reverse=True)
        if not conv_files:
            return None, "No conversations found"
        conv_file = conv_files[0]

    if not conv_file.exists():
        return None, f"Conversation file not found: {conv_file}"

    print(f"\n🔍 Analyzing conversation: {conv_file.name}")
    print("   Extracting key features...")

    # Extract features from conversation
    features = extract_conversation_features(conv_file)

    # Generate suggestions
    suggestions = generate_title_suggestions(features)

    # Display analysis summary
    print(f"\n📊 Conversation Analysis:")
    print(f"   • Primary actions: {', '.join([a[0] for a in features['actions'].most_common(3)])}" if features['actions'] else "   • No specific actions detected")
    print(f"   • Key terms: {', '.join([t[0] for t in features['key_terms'].most_common(5)])}" if features['key_terms'] else "   • No key terms detected")
    print(f"   • Tools used: {', '.join([t[0] for t in features['tools_used'].most_common(3)])}" if features['tools_used'] else "   • No tools detected")
    print(f"   • Skills involved: {', '.join(list(features['skills'])[:3])}" if features['skills'] else "   • No skills detected")

    return suggestions, conv_file


def interactive_title_selection():
    """Interactive function to let user choose from suggestions"""
    import sys

    suggestions, conv_file = suggest_conversation_titles()

    if not suggestions:
        print(conv_file)  # Error message
        return

    print(f"\n💡 Title Suggestions:")
    print("=" * 60)

    for i, title in enumerate(suggestions, 1):
        print(f"{i}. {title}")

    print(f"5. Enter custom title")
    print(f"6. Keep as Untitled")
    print("=" * 60)

    while True:
        try:
            choice = input("\n🎯 Select option (1-6): ").strip()

            if choice == '6':
                print("❌ Keeping conversation untitled")
                return None
            elif choice == '5':
                custom_title = input("📝 Enter custom title: ").strip()
                if custom_title:
                    return custom_title
                else:
                    print("❌ No title entered")
                    return None
            elif choice in ['1', '2', '3', '4']:
                selected_title = suggestions[int(choice) - 1]
                print(f"\n✅ Selected: '{selected_title}'")
                return selected_title
            else:
                print("❌ Invalid choice. Please select 1-6")
        except (ValueError, IndexError):
            print("❌ Invalid input. Please try again.")
        except KeyboardInterrupt:
            print("\n❌ Cancelled")
            return None


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        # Interactive mode with selection
        selected_title = interactive_title_selection()
        if selected_title:
            # Now rename the conversation with selected title
            from rename_conversation import rename_conversation
            result = rename_conversation(selected_title)
            print(result)
    else:
        # Just show suggestions
        suggestions, conv_file = suggest_conversation_titles()
        if suggestions:
            print(f"\n💡 Suggested Titles:")
            for i, title in enumerate(suggestions, 1):
                print(f"{i}. {title}")