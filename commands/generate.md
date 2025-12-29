---
description: Generate quizzes from pending concept requests
allowed-tools: Read, Write, Bash, Glob
model: claude-sonnet-4-20250514
---

# Generate LeetVibe Quizzes

Process pending quiz requests in `.leetvibe/pending/` and generate full quizzes.

## Pending Request Format

Each file in `.leetvibe/pending/{id}-{concept}.json` contains:
```json
{
  "concept": "hash_set",
  "quiz_id": "007",
  "source_file": "/path/to/file.py",
  "source_code": "the code that triggered this concept",
  "language": "python",
  "timestamp": "2025-12-29T..."
}
```

## Process

1. **Check for pending requests** using `Glob` on `.leetvibe/pending/*.json`

2. **For each pending request**, read the JSON and generate a quiz:
   - Analyze the source_code to understand how the concept was used
   - Create a SIMILAR but ISOLATED LeetCode-style problem
   - Generate 5-10 test cases including edge cases
   - Write the solution file to `.leetvibe/solutions/{id}-{concept}.{ext}`

3. **Delete** the pending request file after successful generation

4. **Summarize** what was generated

## Quiz Generation Guidelines

Create quizzes that:
- Have a clear, specific problem statement (not generic placeholder text)
- Include 2-3 examples with concrete inputs and outputs
- Have 5-10 test cases including edge cases
- Have 3 progressive hints

## Solution File Format (Python example)

```python
"""
================================================================================
LEETVIBE QUIZ {quiz_id}: {Title}
================================================================================

PROBLEM:
{Clear problem statement with specific requirements}

EXAMPLES:
  function_name([1, 2, 3]) -> 6
  function_name([]) -> 0

HINTS:
  1. {First hint - approach suggestion}
  2. {Second hint - key insight}
  3. {Third hint - implementation detail}

When ready, run: /leetvibe:submit {quiz_id}
================================================================================
"""

# TEST:{quiz_id}:{"input": [[1, 2, 3]], "expected": 6}
# TEST:{quiz_id}:{"input": [[]], "expected": 0}
# ... more test cases

def function_name(data: list) -> int:
    # ====================== YOUR SOLUTION BELOW ======================

    pass  # Delete this and write your solution

    # ====================== YOUR SOLUTION ABOVE ======================
```

Use appropriate file extension based on language: .py, .ts, .js, .cpp, .swift, .kt

## Output

```
Generated Quizzes
=================

[001] Memoization
     Problem: Climbing Stairs
     Test cases: 8
     File: .leetvibe/solutions/001-memoization.py

[002] Binary Search
     Problem: Search in Rotated Array
     Test cases: 6
     File: .leetvibe/solutions/002-binary_search.py

2 quizzes generated. Run /leetvibe:submit <id> to test your solution.
```

## If No Pending Requests

```
No pending quiz requests found.

Quizzes are automatically requested when Claude uses new programming
concepts in your code. Keep coding and new quizzes will appear!
```
