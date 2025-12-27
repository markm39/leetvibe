---
description: Generate quizzes from pending concept requests
allowed-tools: Read, Write, Bash
model: claude-sonnet-4-20250514
---

# Generate LeetVibe Quizzes

Process pending quiz requests in `.leetvibe/pending/` and generate full quizzes.

## Process

1. **Check for pending requests** in `.leetvibe/pending/*.json`

2. **For each pending request**, generate a quiz using the quiz-generator skill:
   - Read the concept name and source context
   - Create an appropriate LeetCode-style problem
   - Generate 5-10 test cases including edge cases
   - Write the quiz to `.leetvibe/quizzes/{id}-{concept}.md`

3. **Clean up** the pending request file after successful generation

4. **Summarize** what was generated

## Quiz Generation Guidelines

Use the quiz-generator skill to create quizzes. Each quiz should:

- Have a clear problem statement
- Include 2-3 examples with explanations
- Provide function signatures for all supported languages
- Include 5-10 test cases in JSON format
- Have 3 progressive hints

## Output

```
Generated Quizzes
=================

[001] Memoization
     Problem: Climbing Stairs
     Test cases: 8
     File: .leetvibe/quizzes/001-memoization.md

[002] Binary Search
     Problem: Search in Rotated Array
     Test cases: 6
     File: .leetvibe/quizzes/002-binary_search.md

2 quizzes generated. Run /leetvibe:quiz to see all available quizzes.
```

## If No Pending Requests

```
No pending quiz requests found.

Quizzes are automatically requested when Claude uses new programming
concepts in your code. Keep coding and new quizzes will appear!
```
