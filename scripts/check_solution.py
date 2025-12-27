#!/usr/bin/env python3
"""
Solution Checker for LeetVibe

Main entry point for running test cases against user solutions.
Automatically selects the appropriate language runner based on file extension.

Usage (from terminal, no Claude needed):
    leetvibe-submit 002
    leetvibe-submit ./path/to/solution.py

Or directly:
    python check_solution.py <quiz_id>
    python check_solution.py <solution_file_path>
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from runners.base_runner import RunResult
from runners.python_runner import PythonRunner
from runners.typescript_runner import TypeScriptRunner
from runners.cpp_runner import CppRunner
from runners.swift_runner import SwiftRunner
from runners.kotlin_runner import KotlinRunner


# Map file extensions to runners
RUNNER_MAP = {
    '.py': PythonRunner,
    '.ts': TypeScriptRunner,
    '.tsx': TypeScriptRunner,
    '.js': TypeScriptRunner,
    '.jsx': TypeScriptRunner,
    '.cpp': CppRunner,
    '.cc': CppRunner,
    '.cxx': CppRunner,
    '.swift': SwiftRunner,
    '.kt': KotlinRunner,
    '.kts': KotlinRunner,
}


def get_leetvibe_dir() -> Path:
    """Get the .leetvibe directory in the current project."""
    cwd = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
    return Path(cwd) / '.leetvibe'


def get_learning_history_path() -> Path:
    """Get path to the learning history file."""
    return Path.home() / '.leetvibe' / 'learning-history.json'


def mark_quiz_complete(quiz_id: str, concept: str, score: float) -> None:
    """Mark a quiz as completed in the learning history."""
    history_path = get_learning_history_path()

    # Load existing history
    if history_path.exists():
        try:
            with open(history_path, 'r') as f:
                history = json.load(f)
        except (json.JSONDecodeError, IOError):
            history = {"concepts": {}}
    else:
        history = {"concepts": {}}

    # Update the concept entry
    if concept in history.get('concepts', {}):
        history['concepts'][concept]['quiz_completed'] = True
        history['concepts'][concept]['quiz_score'] = score
        history['concepts'][concept]['completed_at'] = datetime.now().isoformat()
    else:
        # Create new entry if it doesn't exist
        history.setdefault('concepts', {})[concept] = {
            'first_seen': datetime.now().isoformat(),
            'times_seen': 1,
            'quiz_completed': True,
            'quiz_score': score,
            'quiz_id': quiz_id,
            'completed_at': datetime.now().isoformat(),
        }

    # Save
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with open(history_path, 'w') as f:
        json.dump(history, f, indent=2)


def find_solution_file(quiz_id: str) -> Path | None:
    """Find the solution file for a given quiz ID."""
    solutions_dir = get_leetvibe_dir() / 'solutions'
    if not solutions_dir.exists():
        return None

    # Look for any file matching the quiz ID prefix
    for ext in RUNNER_MAP.keys():
        candidates = list(solutions_dir.glob(f'{quiz_id}-*{ext}'))
        if candidates:
            return candidates[0]

    return None


def parse_test_cases_from_solution(solution_path: Path) -> dict | None:
    """Extract test cases from comments in solution file.

    Test cases are embedded as comments like:
    # TEST:001:{"input": [1], "expected": 1}
    // TEST:001:{"input": [1], "expected": 1}
    """
    content = solution_path.read_text()

    # Extract quiz ID from filename
    quiz_id = solution_path.stem.split('-')[0]

    # Find all test case comments
    # Match both # and // comment styles
    pattern = rf'(?:#|//)\s*TEST:{quiz_id}:(\{{.*?\}})'
    matches = re.findall(pattern, content)

    if not matches:
        return None

    test_cases = []
    for match in matches:
        try:
            tc = json.loads(match)
            test_cases.append(tc)
        except json.JSONDecodeError:
            pass

    if not test_cases:
        return None

    # Extract function name from the solution
    # Look for def func_name( or function func_name( or func func_name(
    func_pattern = r'(?:def|function|func|fun)\s+(\w+)\s*\('
    func_match = re.search(func_pattern, content)
    function_name = func_match.group(1) if func_match else "solve"

    return {
        "function_name": function_name,
        "test_cases": test_cases
    }


def run_solution(solution_path: Path, test_cases: dict) -> RunResult:
    """Run the solution with the appropriate runner."""
    ext = solution_path.suffix.lower()

    if ext not in RUNNER_MAP:
        # Return error result
        return RunResult(
            total=0,
            passed=0,
            failed=0,
            results=[],
            compile_error=f"Unsupported file extension: {ext}"
        )

    runner_class = RUNNER_MAP[ext]
    runner = runner_class(solution_path, test_cases)

    try:
        return runner.run_all_tests()
    finally:
        runner.cleanup()


def main():
    parser = argparse.ArgumentParser(description='Check LeetVibe solution')
    parser.add_argument('target', help='Quiz ID (e.g., 001) or path to solution file')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()

    # Determine if target is a quiz ID or file path
    target_path = Path(args.target)

    if target_path.exists():
        # Direct path to solution file
        solution_path = target_path
    else:
        # Assume it's a quiz ID
        quiz_id = args.target.lstrip('0') or '0'  # Handle leading zeros
        quiz_id = f'{int(quiz_id):03d}'  # Normalize to 3 digits

        solution_path = find_solution_file(quiz_id)

        if not solution_path:
            print(f"Error: No solution file found for quiz {quiz_id}", file=sys.stderr)
            print(f"Check .leetvibe/solutions/ for available quizzes", file=sys.stderr)
            sys.exit(1)

    # Parse test cases from solution file comments
    test_cases = parse_test_cases_from_solution(solution_path)

    if not test_cases:
        print(f"Error: Could not parse test cases from {solution_path}", file=sys.stderr)
        print(f"Test cases should be in comments like: # TEST:001:{{...}}", file=sys.stderr)
        sys.exit(1)

    # Extract quiz ID and concept from filename
    filename_parts = solution_path.stem.split('-', 1)
    quiz_id = filename_parts[0]
    concept = filename_parts[1] if len(filename_parts) > 1 else "unknown"

    # Run the solution
    print(f"\n  LeetVibe Quiz {quiz_id}: {concept.replace('_', ' ').title()}")
    print(f"  {'=' * 50}\n")

    result = run_solution(solution_path, test_cases)

    if args.json:
        output = {
            'total': result.total,
            'passed': result.passed,
            'failed': result.failed,
            'score': result.score,
            'all_passed': result.all_passed,
            'compile_error': result.compile_error,
            'results': [
                {
                    'passed': r.passed,
                    'input': r.input_data,
                    'expected': r.expected,
                    'actual': r.actual,
                    'error': r.error,
                    'time_ms': r.execution_time_ms
                }
                for r in result.results
            ]
        }
        print(json.dumps(output, indent=2))
    else:
        # Get the runner to format results
        ext = solution_path.suffix.lower()
        runner_class = RUNNER_MAP.get(ext, PythonRunner)
        runner = runner_class(solution_path, test_cases)
        print(runner.format_results(result))

    # If all tests passed, mark as complete
    if result.all_passed:
        mark_quiz_complete(quiz_id, concept, result.score)
        print(f"\n  [COMPLETE] Quiz {quiz_id} marked as done!")
        print(f"  Progress saved to ~/.leetvibe/learning-history.json\n")
    else:
        print(f"\n  [INCOMPLETE] {result.failed} test(s) failed. Keep trying!\n")

    # Exit with appropriate code
    sys.exit(0 if result.all_passed else 1)


if __name__ == '__main__':
    main()
