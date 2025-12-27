#!/usr/bin/env python3
"""
Quiz Generator for LeetVibe

Generates self-contained solution files with embedded problem specs.
Called in background by the PostToolUse hook.

Usage:
    python generate_quiz.py <concept> <quiz_id> [--source-file <path>] [--language <ext>]
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Default language for solution files
DEFAULT_LANGUAGE = "py"

# Template for each language
TEMPLATES = {
    "py": '''"""
================================================================================
LEETVIBE QUIZ {quiz_id}: {concept_title}
================================================================================

PROBLEM:
{problem_description}

EXAMPLES:
{examples}

HINTS:
{hints}

When ready, run: /leetvibe:submit {quiz_id}
================================================================================
"""

{test_cases_comments}

def {function_name}({params}) -> {return_type}:
    # ====================== YOUR SOLUTION BELOW ======================

    pass  # Delete this and write your solution

    # ====================== YOUR SOLUTION ABOVE ======================
''',

    "ts": '''/**
 * ============================================================================
 * LEETVIBE QUIZ {quiz_id}: {concept_title}
 * ============================================================================
 *
 * PROBLEM:
 * {problem_description}
 *
 * EXAMPLES:
{examples}
 *
 * HINTS:
{hints}
 *
 * When ready, run: /leetvibe:submit {quiz_id}
 * ============================================================================
 */

{test_cases_comments}

export function {function_name}({params}): {return_type} {{
    // ====================== YOUR SOLUTION BELOW ======================

    throw new Error("Not implemented");  // Delete this and write your solution

    // ====================== YOUR SOLUTION ABOVE ======================
}}
''',

    "js": '''/**
 * ============================================================================
 * LEETVIBE QUIZ {quiz_id}: {concept_title}
 * ============================================================================
 *
 * PROBLEM:
 * {problem_description}
 *
 * EXAMPLES:
{examples}
 *
 * HINTS:
{hints}
 *
 * When ready, run: /leetvibe:submit {quiz_id}
 * ============================================================================
 */

{test_cases_comments}

export function {function_name}({params}) {{
    // ====================== YOUR SOLUTION BELOW ======================

    throw new Error("Not implemented");  // Delete this and write your solution

    // ====================== YOUR SOLUTION ABOVE ======================
}}
''',

    "cpp": '''/*
================================================================================
LEETVIBE QUIZ {quiz_id}: {concept_title}
================================================================================

PROBLEM:
{problem_description}

EXAMPLES:
{examples}

HINTS:
{hints}

When ready, run: /leetvibe:submit {quiz_id}
================================================================================
*/

{test_cases_comments}

{return_type} {function_name}({params}) {{
    // ====================== YOUR SOLUTION BELOW ======================

    // Delete this and write your solution
    return {{}};

    // ====================== YOUR SOLUTION ABOVE ======================
}}
''',

    "swift": '''/*
================================================================================
LEETVIBE QUIZ {quiz_id}: {concept_title}
================================================================================

PROBLEM:
{problem_description}

EXAMPLES:
{examples}

HINTS:
{hints}

When ready, run: /leetvibe:submit {quiz_id}
================================================================================
*/

{test_cases_comments}

func {function_name}({params}) -> {return_type} {{
    // ====================== YOUR SOLUTION BELOW ======================

    fatalError("Not implemented")  // Delete this and write your solution

    // ====================== YOUR SOLUTION ABOVE ======================
}}
''',

    "kt": '''/*
================================================================================
LEETVIBE QUIZ {quiz_id}: {concept_title}
================================================================================

PROBLEM:
{problem_description}

EXAMPLES:
{examples}

HINTS:
{hints}

When ready, run: /leetvibe:submit {quiz_id}
================================================================================
*/

{test_cases_comments}

fun {function_name}({params}): {return_type} {{
    // ====================== YOUR SOLUTION BELOW ======================

    TODO("Not implemented")  // Delete this and write your solution

    // ====================== YOUR SOLUTION ABOVE ======================
}}
''',
}

# Comment prefix for each language
COMMENT_PREFIX = {
    "py": "#",
    "ts": "//",
    "js": "//",
    "cpp": "//",
    "swift": "//",
    "kt": "//",
}

# Problem bank for each concept (fallback if Claude CLI fails)
PROBLEM_BANK = {
    "recursion": {
        "title": "Recursive Sum",
        "problem": "Write a function that calculates the sum of all numbers from 1 to n using recursion.",
        "function_name": "recursive_sum",
        "params": {"py": "n: int", "ts": "n: number", "js": "n", "cpp": "int n", "swift": "_ n: Int", "kt": "n: Int"},
        "return_type": {"py": "int", "ts": "number", "js": "", "cpp": "int", "swift": "Int", "kt": "Int"},
        "examples": [
            "recursive_sum(5) -> 15  (1+2+3+4+5)",
            "recursive_sum(1) -> 1",
            "recursive_sum(10) -> 55",
        ],
        "hints": [
            "Base case: what happens when n is 0 or 1?",
            "Recursive case: n + sum of (1 to n-1)",
            "recursive_sum(n) = n + recursive_sum(n-1)",
        ],
        "test_cases": [
            {"input": [1], "expected": 1},
            {"input": [5], "expected": 15},
            {"input": [10], "expected": 55},
            {"input": [100], "expected": 5050},
        ],
    },
    "memoization": {
        "title": "Climbing Stairs",
        "problem": "You are climbing a staircase with n steps. Each time you can climb 1 or 2 steps.\nHow many distinct ways can you reach the top? Use memoization for efficiency.",
        "function_name": "climb_stairs",
        "params": {"py": "n: int", "ts": "n: number", "js": "n", "cpp": "int n", "swift": "_ n: Int", "kt": "n: Int"},
        "return_type": {"py": "int", "ts": "number", "js": "", "cpp": "int", "swift": "Int", "kt": "Int"},
        "examples": [
            "climb_stairs(2) -> 2   (1+1 or 2)",
            "climb_stairs(3) -> 3   (1+1+1, 1+2, 2+1)",
            "climb_stairs(5) -> 8",
        ],
        "hints": [
            "Think about the last step - you came from step n-1 or n-2",
            "ways(n) = ways(n-1) + ways(n-2) ... looks familiar?",
            "Use a dict/map to cache computed values",
        ],
        "test_cases": [
            {"input": [1], "expected": 1},
            {"input": [2], "expected": 2},
            {"input": [3], "expected": 3},
            {"input": [5], "expected": 8},
            {"input": [10], "expected": 89},
        ],
    },
    "binary_search": {
        "title": "Binary Search",
        "problem": "Given a sorted array of integers and a target value, return the index of the target.\nIf not found, return -1. You must use O(log n) time complexity.",
        "function_name": "binary_search",
        "params": {"py": "nums: list[int], target: int", "ts": "nums: number[], target: number", "js": "nums, target", "cpp": "vector<int>& nums, int target", "swift": "_ nums: [Int], _ target: Int", "kt": "nums: List<Int>, target: Int"},
        "return_type": {"py": "int", "ts": "number", "js": "", "cpp": "int", "swift": "Int", "kt": "Int"},
        "examples": [
            "binary_search([1,2,3,4,5], 3) -> 2",
            "binary_search([1,2,3,4,5], 6) -> -1",
            "binary_search([5], 5) -> 0",
        ],
        "hints": [
            "Use two pointers: left and right",
            "Calculate mid = (left + right) // 2",
            "If nums[mid] < target, search right half; else search left half",
        ],
        "test_cases": [
            {"input": [[1,2,3,4,5], 3], "expected": 2},
            {"input": [[1,2,3,4,5], 1], "expected": 0},
            {"input": [[1,2,3,4,5], 5], "expected": 4},
            {"input": [[1,2,3,4,5], 6], "expected": -1},
            {"input": [[5], 5], "expected": 0},
        ],
    },
    "two_pointers": {
        "title": "Two Sum (Sorted)",
        "problem": "Given a sorted array, find two numbers that add up to a target sum.\nReturn their indices (1-indexed). Use the two-pointer technique.",
        "function_name": "two_sum",
        "params": {"py": "nums: list[int], target: int", "ts": "nums: number[], target: number", "js": "nums, target", "cpp": "vector<int>& nums, int target", "swift": "_ nums: [Int], _ target: Int", "kt": "nums: List<Int>, target: Int"},
        "return_type": {"py": "list[int]", "ts": "number[]", "js": "", "cpp": "vector<int>", "swift": "[Int]", "kt": "List<Int>"},
        "examples": [
            "two_sum([2,7,11,15], 9) -> [1,2]  (2+7=9)",
            "two_sum([2,3,4], 6) -> [1,3]  (2+4=6)",
        ],
        "hints": [
            "Start with pointers at both ends of the array",
            "If sum < target, move left pointer right",
            "If sum > target, move right pointer left",
        ],
        "test_cases": [
            {"input": [[2,7,11,15], 9], "expected": [1,2]},
            {"input": [[2,3,4], 6], "expected": [1,3]},
            {"input": [[1,2,3,4,5], 9], "expected": [4,5]},
        ],
    },
    "hash_map": {
        "title": "Two Sum",
        "problem": "Given an array of integers, find two numbers that add up to a target.\nReturn their indices. Use a hash map for O(n) time complexity.",
        "function_name": "two_sum",
        "params": {"py": "nums: list[int], target: int", "ts": "nums: number[], target: number", "js": "nums, target", "cpp": "vector<int>& nums, int target", "swift": "_ nums: [Int], _ target: Int", "kt": "nums: List<Int>, target: Int"},
        "return_type": {"py": "list[int]", "ts": "number[]", "js": "", "cpp": "vector<int>", "swift": "[Int]", "kt": "List<Int>"},
        "examples": [
            "two_sum([2,7,11,15], 9) -> [0,1]  (nums[0]+nums[1]=9)",
            "two_sum([3,2,4], 6) -> [1,2]",
            "two_sum([3,3], 6) -> [0,1]",
        ],
        "hints": [
            "Use a hash map to store {value: index}",
            "For each number, check if (target - num) exists in the map",
            "Build the map as you iterate",
        ],
        "test_cases": [
            {"input": [[2,7,11,15], 9], "expected": [0,1]},
            {"input": [[3,2,4], 6], "expected": [1,2]},
            {"input": [[3,3], 6], "expected": [0,1]},
        ],
    },
    "dfs": {
        "title": "Max Depth of Binary Tree",
        "problem": "Given the root of a binary tree, return its maximum depth.\nThe depth is the number of nodes along the longest path from root to leaf.",
        "function_name": "max_depth",
        "params": {"py": "root: TreeNode | None", "ts": "root: TreeNode | null", "js": "root", "cpp": "TreeNode* root", "swift": "_ root: TreeNode?", "kt": "root: TreeNode?"},
        "return_type": {"py": "int", "ts": "number", "js": "", "cpp": "int", "swift": "Int", "kt": "Int"},
        "examples": [
            "max_depth([3,9,20,null,null,15,7]) -> 3",
            "max_depth([1,null,2]) -> 2",
            "max_depth([]) -> 0",
        ],
        "hints": [
            "Use DFS - go deep before going wide",
            "Depth of a node = 1 + max(depth of left, depth of right)",
            "Base case: null node has depth 0",
        ],
        "test_cases": [
            {"input": [None], "expected": 0},
            {"input": [1], "expected": 1},
        ],
    },
    "dynamic_programming": {
        "title": "Coin Change",
        "problem": "Given coins of different denominations and a total amount, find the minimum\nnumber of coins needed to make that amount. Return -1 if impossible.",
        "function_name": "coin_change",
        "params": {"py": "coins: list[int], amount: int", "ts": "coins: number[], amount: number", "js": "coins, amount", "cpp": "vector<int>& coins, int amount", "swift": "_ coins: [Int], _ amount: Int", "kt": "coins: List<Int>, amount: Int"},
        "return_type": {"py": "int", "ts": "number", "js": "", "cpp": "int", "swift": "Int", "kt": "Int"},
        "examples": [
            "coin_change([1,2,5], 11) -> 3  (5+5+1)",
            "coin_change([2], 3) -> -1  (impossible)",
            "coin_change([1], 0) -> 0",
        ],
        "hints": [
            "Use DP: dp[i] = min coins needed for amount i",
            "For each amount, try all coins that fit",
            "dp[i] = min(dp[i], dp[i-coin] + 1) for each coin",
        ],
        "test_cases": [
            {"input": [[1,2,5], 11], "expected": 3},
            {"input": [[2], 3], "expected": -1},
            {"input": [[1], 0], "expected": 0},
            {"input": [[1,2,5], 5], "expected": 1},
        ],
    },
}


def get_leetvibe_dir() -> Path:
    """Get the .leetvibe directory in the current project."""
    cwd = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
    return Path(cwd) / '.leetvibe'


def get_problem_data(concept: str) -> dict:
    """Get problem data for a concept, using fallback bank if available."""
    if concept in PROBLEM_BANK:
        return PROBLEM_BANK[concept]

    # Generic fallback
    return {
        "title": concept.replace("_", " ").title(),
        "problem": f"Implement a solution demonstrating the {concept.replace('_', ' ')} concept.",
        "function_name": f"solve_{concept}",
        "params": {"py": "data", "ts": "data: any", "js": "data", "cpp": "auto data", "swift": "_ data: Any", "kt": "data: Any"},
        "return_type": {"py": "any", "ts": "any", "js": "", "cpp": "auto", "swift": "Any", "kt": "Any"},
        "examples": [f"solve_{concept}(...) -> ..."],
        "hints": [
            f"Think about the key properties of {concept.replace('_', ' ')}",
            "Consider edge cases",
            "Start with a simple approach, then optimize",
        ],
        "test_cases": [{"input": [], "expected": None}],
    }


def format_test_cases(quiz_id: str, test_cases: list, lang: str) -> str:
    """Format test cases as comments."""
    prefix = COMMENT_PREFIX.get(lang, "#")
    lines = []
    for tc in test_cases:
        tc_json = json.dumps({"input": tc["input"], "expected": tc["expected"]})
        lines.append(f"{prefix} TEST:{quiz_id}:{tc_json}")
    return "\n".join(lines)


def format_multiline_comment(text: str, lang: str, indent: str = "") -> str:
    """Format multi-line text for block comments."""
    lines = text.split('\n')
    if lang in ['ts', 'js', 'cpp', 'swift', 'kt']:
        # These use /* */ or /** */ style - add * prefix to each line
        return '\n'.join(f"{indent} * {line}" for line in lines)
    else:
        # Python uses # for each line
        return '\n'.join(f"{indent}# {line}" if line else f"{indent}#" for line in lines)


def generate_solution_file(concept: str, quiz_id: str, lang: str = "py") -> Path:
    """Generate a self-contained solution file."""
    leetvibe_dir = get_leetvibe_dir()
    solutions_dir = leetvibe_dir / 'solutions'
    solutions_dir.mkdir(parents=True, exist_ok=True)

    problem = get_problem_data(concept)
    template = TEMPLATES.get(lang, TEMPLATES["py"])

    # Format examples with proper comment continuation
    if lang in ['ts', 'js', 'cpp', 'swift', 'kt']:
        examples = "\n".join(f" *   {ex}" for ex in problem["examples"])
        hints = "\n".join(f" *   {i+1}. {hint}" for i, hint in enumerate(problem["hints"]))
        # Handle multi-line problem descriptions
        problem_lines = problem["problem"].split('\n')
        problem_description = "\n".join(f" * {line}" if i > 0 else line
                                        for i, line in enumerate(problem_lines))
    else:
        examples = "\n".join(f"  {ex}" for ex in problem["examples"])
        hints = "\n".join(f"  {i+1}. {hint}" for i, hint in enumerate(problem["hints"]))
        problem_description = problem["problem"]

    # Get language-specific params/return type
    params = problem["params"].get(lang, problem["params"].get("py", ""))
    return_type = problem["return_type"].get(lang, problem["return_type"].get("py", ""))

    # Format test cases as comments
    test_cases_comments = format_test_cases(quiz_id, problem["test_cases"], lang)

    # Generate content
    content = template.format(
        quiz_id=quiz_id,
        concept_title=problem["title"],
        problem_description=problem_description,
        examples=examples,
        hints=hints,
        function_name=problem["function_name"],
        params=params,
        return_type=return_type,
        test_cases_comments=test_cases_comments,
    )

    # Write file
    solution_path = solutions_dir / f"{quiz_id}-{concept}.{lang}"
    with open(solution_path, 'w') as f:
        f.write(content)

    return solution_path


def main():
    parser = argparse.ArgumentParser(description='Generate LeetVibe quiz solution file')
    parser.add_argument('concept', help='The concept to generate a quiz for')
    parser.add_argument('quiz_id', help='Quiz ID (e.g., 001)')
    parser.add_argument('--language', '-l', default=DEFAULT_LANGUAGE,
                        help='Language for solution file (py, ts, js, cpp, swift, kt)')
    parser.add_argument('--source-file', help='Source file where concept was detected')
    args = parser.parse_args()

    # Detect language from source file if provided
    lang = args.language
    if args.source_file:
        ext_map = {
            '.py': 'py', '.ts': 'ts', '.tsx': 'ts', '.js': 'js', '.jsx': 'js',
            '.cpp': 'cpp', '.cc': 'cpp', '.swift': 'swift', '.kt': 'kt',
        }
        source_ext = Path(args.source_file).suffix.lower()
        lang = ext_map.get(source_ext, lang)

    solution_path = generate_solution_file(args.concept, args.quiz_id, lang)
    print(f"[LeetVibe] Quiz ready: {solution_path}")


if __name__ == '__main__':
    main()
