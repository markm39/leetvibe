#!/usr/bin/env python3
"""
Concept Analysis Script for LeetVibe

This script is called by the PostToolUse hook after Write/Edit operations.
It analyzes the written code for programming concepts and triggers quiz
generation when new concepts are detected.

Input (stdin): JSON with tool_input containing file_path and content
Output (stdout): Status message for Claude Code context
"""

import json
import os
import sys
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime

# File extensions we analyze for concepts
CODE_EXTENSIONS = {
    '.ts', '.tsx', '.js', '.jsx',  # TypeScript/JavaScript
    '.py',                          # Python
    '.cpp', '.cc', '.cxx', '.h', '.hpp',  # C++
    '.swift',                       # Swift
    '.kt', '.kts',                  # Kotlin
}

# Concepts we track and can generate quizzes for
CONCEPT_CATEGORIES = {
    "algorithms": [
        "recursion", "memoization", "dynamic_programming",
        "binary_search", "two_pointers", "sliding_window",
        "bfs", "dfs", "backtracking", "greedy",
        "divide_and_conquer", "topological_sort",
    ],
    "data_structures": [
        "linked_list", "binary_tree", "binary_search_tree",
        "heap", "priority_queue", "hash_map", "hash_set",
        "stack", "queue", "deque", "trie", "graph",
        "disjoint_set", "segment_tree",
    ],
    "patterns": [
        "factory", "singleton", "observer", "strategy",
        "decorator", "adapter", "facade", "iterator",
    ],
    "language_features": [
        "async_await", "generators", "decorators",
        "closures", "higher_order_functions", "metaclasses",
    ],
}


def get_leetvibe_dir() -> Path:
    """Get the .leetvibe directory in the current project."""
    cwd = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
    leetvibe_dir = Path(cwd) / '.leetvibe'
    return leetvibe_dir


def get_learning_history_path() -> Path:
    """Get path to the learning history file."""
    # Store in user's home directory so it persists across projects
    home = Path.home()
    return home / '.leetvibe' / 'learning-history.json'


def load_learning_history() -> dict:
    """Load the learning history from disk."""
    history_path = get_learning_history_path()
    if history_path.exists():
        try:
            with open(history_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"concepts": {}}


def save_learning_history(history: dict) -> None:
    """Save the learning history to disk."""
    history_path = get_learning_history_path()
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with open(history_path, 'w') as f:
        json.dump(history, f, indent=2)


def is_code_file(file_path: str) -> bool:
    """Check if the file is a code file we should analyze."""
    if not file_path:
        return False
    ext = Path(file_path).suffix.lower()
    return ext in CODE_EXTENSIONS


def analyze_with_claude(code: str, file_path: str) -> list[str]:
    """Use Claude CLI to analyze code for concepts."""
    prompt = f"""Analyze this code and identify any programming concepts from this list.
Return ONLY a JSON array of concept names that are clearly demonstrated in the code.
Be conservative - only include concepts that are explicitly used, not just tangentially related.

Concepts to look for:
- Algorithms: recursion, memoization, dynamic_programming, binary_search, two_pointers, sliding_window, bfs, dfs, backtracking, greedy, divide_and_conquer, topological_sort
- Data Structures: linked_list, binary_tree, binary_search_tree, heap, priority_queue, hash_map, hash_set, stack, queue, deque, trie, graph, disjoint_set, segment_tree
- Design Patterns: factory, singleton, observer, strategy, decorator, adapter, facade, iterator
- Language Features: async_await, generators, decorators, closures, higher_order_functions, metaclasses

File: {file_path}

Code:
```
{code[:3000]}  # Limit to first 3000 chars to avoid token limits
```

Return ONLY a JSON array like: ["recursion", "memoization"]
If no significant concepts found, return: []"""

    try:
        result = subprocess.run(
            ['claude', '-p', prompt, '--output-format', 'text'],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
        )

        if result.returncode == 0:
            # Try to parse the response as JSON
            response = result.stdout.strip()
            # Find JSON array in response
            start = response.find('[')
            end = response.rfind(']') + 1
            if start != -1 and end > start:
                concepts = json.loads(response[start:end])
                # Validate concepts are from our list
                all_concepts = []
                for category in CONCEPT_CATEGORIES.values():
                    all_concepts.extend(category)
                return [c for c in concepts if c in all_concepts]
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, json.JSONDecodeError):
        pass

    return []


def get_next_quiz_id(leetvibe_dir: Path) -> str:
    """Get the next available quiz ID."""
    solutions_dir = leetvibe_dir / 'solutions'
    if not solutions_dir.exists():
        solutions_dir.mkdir(parents=True, exist_ok=True)
        return "001"

    # Check existing solutions
    existing = list(solutions_dir.glob('*'))
    if not existing:
        return "001"

    # Extract IDs and find max
    max_id = 0
    for solution_file in existing:
        try:
            quiz_id = int(solution_file.stem.split('-')[0])
            max_id = max(max_id, quiz_id)
        except (ValueError, IndexError):
            pass

    return f"{max_id + 1:03d}"


def get_language_from_file(file_path: str) -> str:
    """Determine language from file extension."""
    ext = Path(file_path).suffix.lower()
    ext_to_lang = {
        '.py': 'python',
        '.ts': 'typescript', '.tsx': 'typescript',
        '.js': 'javascript', '.jsx': 'javascript',
        '.cpp': 'cpp', '.cc': 'cpp', '.cxx': 'cpp',
        '.swift': 'swift',
        '.kt': 'kotlin', '.kts': 'kotlin',
    }
    return ext_to_lang.get(ext, 'python')


def write_pending_request(concept: str, quiz_id: str, source_file: str, source_code: str) -> Path:
    """Write a pending quiz request for Claude Code to process."""
    leetvibe_dir = get_leetvibe_dir()
    pending_dir = leetvibe_dir / 'pending'
    pending_dir.mkdir(parents=True, exist_ok=True)

    language = get_language_from_file(source_file)

    request = {
        "concept": concept,
        "quiz_id": quiz_id,
        "source_file": source_file,
        "source_code": source_code[:3000],  # Limit size
        "language": language,
        "timestamp": datetime.now().isoformat(),
    }

    pending_file = pending_dir / f"{quiz_id}-{concept}.json"
    with open(pending_file, 'w') as f:
        json.dump(request, f, indent=2)

    return pending_file


def main():
    # Read hook input from stdin
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)  # Silent exit on invalid input

    # Extract file path and content from tool input
    tool_input = hook_input.get('tool_input', {})
    file_path = tool_input.get('file_path', '')
    content = tool_input.get('content', '')

    # For Edit tool, we might have different structure
    if not content and 'new_string' in tool_input:
        content = tool_input.get('new_string', '')

    # Skip non-code files
    if not is_code_file(file_path):
        sys.exit(0)

    # Skip if content is too small to be meaningful
    if len(content) < 50:
        sys.exit(0)

    # Analyze for concepts
    concepts = analyze_with_claude(content, file_path)

    if not concepts:
        sys.exit(0)

    # Load learning history
    history = load_learning_history()
    leetvibe_dir = get_leetvibe_dir()

    # Find new concepts first
    new_concepts = []
    for concept in concepts:
        if concept not in history['concepts']:
            new_concepts.append(concept)
        else:
            history['concepts'][concept]['times_seen'] += 1

    # Assign unique quiz IDs upfront (before spawning background processes)
    quiz_assignments = []
    current_max_id = 0

    # Find current max ID
    solutions_dir = leetvibe_dir / 'solutions'
    if solutions_dir.exists():
        for f in solutions_dir.glob('*'):
            try:
                fid = int(f.stem.split('-')[0])
                current_max_id = max(current_max_id, fid)
            except (ValueError, IndexError):
                pass

    # Assign IDs sequentially
    for concept in new_concepts:
        current_max_id += 1
        quiz_id = f"{current_max_id:03d}"
        quiz_assignments.append((concept, quiz_id))

        # Add to history with assigned ID
        history['concepts'][concept] = {
            'first_seen': datetime.now().isoformat(),
            'times_seen': 1,
            'quiz_completed': False,
            'quiz_id': quiz_id,
            'source_file': file_path,
        }

    # Save updated history BEFORE spawning background processes
    save_learning_history(history)

    # Read source code for context
    source_code = ""
    try:
        with open(file_path, 'r') as f:
            source_code = f.read()
    except IOError:
        source_code = content  # Fall back to edit content

    # Write pending quiz requests for Claude Code to process
    for concept, quiz_id in quiz_assignments:
        write_pending_request(concept, quiz_id, file_path, source_code)

    # Output instruction for Claude Code to auto-generate quizzes in background
    if new_concepts:
        concepts_list = ", ".join(new_concepts)
        print(f"[LeetVibe] New concepts detected: {concepts_list}")
        print(f"[LeetVibe:AutoGenerate] Generate quizzes for pending requests in .leetvibe/pending/")


if __name__ == '__main__':
    main()
