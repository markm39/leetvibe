#!/usr/bin/env python3
"""
Quiz Generator for LeetVibe

Generates contextual quizzes based on code Claude just wrote.
Creates problems that mirror the actual implementation in an isolated manner.

Usage:
    python generate_quiz.py <concept> <quiz_id> --source-file <path> --code <snippet>
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# Language file extensions
EXT_TO_LANG = {
    '.py': 'python',
    '.ts': 'typescript', '.tsx': 'typescript',
    '.js': 'javascript', '.jsx': 'javascript',
    '.cpp': 'cpp', '.cc': 'cpp', '.cxx': 'cpp',
    '.swift': 'swift',
    '.kt': 'kotlin', '.kts': 'kotlin',
}

LANG_TO_EXT = {
    'python': 'py', 'typescript': 'ts', 'javascript': 'js',
    'cpp': 'cpp', 'swift': 'swift', 'kotlin': 'kt',
}


def get_leetvibe_dir() -> Path:
    """Get the .leetvibe directory in the current project."""
    cwd = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
    return Path(cwd) / '.leetvibe'


def generate_quiz_with_claude(concept: str, quiz_id: str, code_snippet: str, language: str) -> dict:
    """Use Claude to generate a contextual quiz based on the actual code."""

    prompt = f"""You are generating a LeetCode-style coding quiz based on code that was just written.

The code uses the concept: {concept}
Language: {language}

Here's the actual code that was written:
```{language}
{code_snippet[:2000]}
```

Generate a quiz that:
1. Creates a SIMILAR but ISOLATED problem that tests the same concept
2. Mirrors the pattern/approach used in the code above
3. Is self-contained (doesn't depend on external code)
4. Has concrete, testable inputs and outputs

Return a JSON object with this exact structure:
{{
    "title": "Short descriptive title",
    "problem": "Clear problem statement (2-3 sentences). Be specific about inputs/outputs.",
    "function_name": "snake_case_name",
    "params": "typed parameters for {language}",
    "return_type": "return type for {language}",
    "examples": [
        "function_name(input) -> output  // explanation",
        "function_name(input2) -> output2"
    ],
    "hints": [
        "First hint - approach suggestion",
        "Second hint - key insight",
        "Third hint - implementation detail"
    ],
    "test_cases": [
        {{"input": [arg1, arg2], "expected": result}},
        {{"input": [arg1, arg2], "expected": result}}
    ]
}}

Generate 4-6 test cases covering normal cases and edge cases.
Make the problem appropriately challenging but solvable in 10-15 minutes.
Return ONLY the JSON object, no other text."""

    try:
        result = subprocess.run(
            ['claude', '-p', prompt, '--output-format', 'text'],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
        )

        if result.returncode == 0:
            response = result.stdout.strip()
            # Find JSON in response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                return json.loads(response[start:end])
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, json.JSONDecodeError) as e:
        print(f"[LeetVibe] Quiz generation error: {e}", file=sys.stderr)

    # Fallback if Claude fails
    return {
        "title": concept.replace("_", " ").title(),
        "problem": f"Implement a function demonstrating {concept.replace('_', ' ')}.",
        "function_name": f"solve_{concept}",
        "params": "data",
        "return_type": "any",
        "examples": [f"solve_{concept}(input) -> output"],
        "hints": [
            f"Think about how {concept.replace('_', ' ')} works",
            "Consider edge cases",
            "Start simple, then optimize"
        ],
        "test_cases": [{"input": ["example"], "expected": "result"}]
    }


def format_quiz_file(quiz_data: dict, quiz_id: str, language: str) -> str:
    """Format the quiz data into a solution file."""

    ext = LANG_TO_EXT.get(language, 'py')

    # Format examples
    examples_str = "\n".join(f"  {ex}" for ex in quiz_data.get("examples", []))

    # Format hints
    hints_str = "\n".join(f"  {i+1}. {hint}" for i, hint in enumerate(quiz_data.get("hints", [])))

    # Format test cases as comments
    test_cases = quiz_data.get("test_cases", [])
    test_comments = "\n".join(
        f"# TEST:{quiz_id}:{json.dumps(tc)}" for tc in test_cases
    )

    func_name = quiz_data.get("function_name", "solve")
    params = quiz_data.get("params", "data")
    return_type = quiz_data.get("return_type", "any")

    if language == 'python':
        return f'''"""
================================================================================
LEETVIBE QUIZ {quiz_id}: {quiz_data.get("title", "Quiz")}
================================================================================

PROBLEM:
{quiz_data.get("problem", "")}

EXAMPLES:
{examples_str}

HINTS:
{hints_str}

When ready, run: /leetvibe:submit {quiz_id}
================================================================================
"""

{test_comments}

def {func_name}({params}) -> {return_type}:
    # ====================== YOUR SOLUTION BELOW ======================

    pass  # Delete this and write your solution

    # ====================== YOUR SOLUTION ABOVE ======================
'''

    elif language in ('typescript', 'javascript'):
        test_comments_js = "\n".join(
            f"// TEST:{quiz_id}:{json.dumps(tc)}" for tc in test_cases
        )
        type_annotation = f": {return_type}" if language == 'typescript' else ""
        return f'''/**
 * ============================================================================
 * LEETVIBE QUIZ {quiz_id}: {quiz_data.get("title", "Quiz")}
 * ============================================================================
 *
 * PROBLEM:
 * {quiz_data.get("problem", "")}
 *
 * EXAMPLES:
{chr(10).join(" *   " + ex for ex in quiz_data.get("examples", []))}
 *
 * HINTS:
{chr(10).join(" *   " + str(i+1) + ". " + hint for i, hint in enumerate(quiz_data.get("hints", [])))}
 *
 * When ready, run: /leetvibe:submit {quiz_id}
 * ============================================================================
 */

{test_comments_js}

export function {func_name}({params}){type_annotation} {{
    // ====================== YOUR SOLUTION BELOW ======================

    throw new Error("Not implemented");  // Delete this and write your solution

    // ====================== YOUR SOLUTION ABOVE ======================
}}
'''

    elif language == 'swift':
        test_comments_swift = "\n".join(
            f"// TEST:{quiz_id}:{json.dumps(tc)}" for tc in test_cases
        )
        return f'''/*
================================================================================
LEETVIBE QUIZ {quiz_id}: {quiz_data.get("title", "Quiz")}
================================================================================

PROBLEM:
{quiz_data.get("problem", "")}

EXAMPLES:
{examples_str}

HINTS:
{hints_str}

When ready, run: /leetvibe:submit {quiz_id}
================================================================================
*/

{test_comments_swift}

func {func_name}({params}) -> {return_type} {{
    // ====================== YOUR SOLUTION BELOW ======================

    fatalError("Not implemented")  // Delete this and write your solution

    // ====================== YOUR SOLUTION ABOVE ======================
}}
'''

    else:  # cpp, kotlin, or fallback
        comment_prefix = "//"
        test_comments_other = "\n".join(
            f"{comment_prefix} TEST:{quiz_id}:{json.dumps(tc)}" for tc in test_cases
        )

        if language == 'kotlin':
            func_decl = f"fun {func_name}({params}): {return_type}"
            not_impl = 'TODO("Not implemented")'
        else:  # cpp
            func_decl = f"{return_type} {func_name}({params})"
            not_impl = "// Not implemented"

        return f'''/*
================================================================================
LEETVIBE QUIZ {quiz_id}: {quiz_data.get("title", "Quiz")}
================================================================================

PROBLEM:
{quiz_data.get("problem", "")}

EXAMPLES:
{examples_str}

HINTS:
{hints_str}

When ready, run: /leetvibe:submit {quiz_id}
================================================================================
*/

{test_comments_other}

{func_decl} {{
    // ====================== YOUR SOLUTION BELOW ======================

    {not_impl}  // Delete this and write your solution

    // ====================== YOUR SOLUTION ABOVE ======================
}}
'''


def main():
    parser = argparse.ArgumentParser(description='Generate contextual LeetVibe quiz')
    parser.add_argument('concept', help='The concept to generate a quiz for')
    parser.add_argument('quiz_id', help='Quiz ID (e.g., 001)')
    parser.add_argument('--source-file', required=True, help='Source file where concept was detected')
    parser.add_argument('--code', default='', help='Code snippet (passed via stdin if not provided)')
    args = parser.parse_args()

    # Determine language from source file
    ext = Path(args.source_file).suffix.lower()
    language = EXT_TO_LANG.get(ext, 'python')

    # Read code from file if not provided
    code_snippet = args.code
    if not code_snippet and args.source_file:
        try:
            with open(args.source_file, 'r') as f:
                code_snippet = f.read()
        except IOError:
            code_snippet = ""

    # Generate quiz using Claude
    quiz_data = generate_quiz_with_claude(args.concept, args.quiz_id, code_snippet, language)

    # Format into solution file
    content = format_quiz_file(quiz_data, args.quiz_id, language)

    # Write solution file
    leetvibe_dir = get_leetvibe_dir()
    solutions_dir = leetvibe_dir / 'solutions'
    solutions_dir.mkdir(parents=True, exist_ok=True)

    file_ext = LANG_TO_EXT.get(language, 'py')
    solution_path = solutions_dir / f"{args.quiz_id}-{args.concept}.{file_ext}"

    with open(solution_path, 'w') as f:
        f.write(content)

    print(f"[LeetVibe] Quiz ready: {solution_path}")


if __name__ == '__main__':
    main()
