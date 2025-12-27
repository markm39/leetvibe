---
description: List all LeetVibe quizzes and their status
allowed-tools: Read, Bash
---

# List LeetVibe Quizzes

Check the `.leetvibe` directory in the current project for quizzes and their status.

## What to Display

1. **Pending Quiz Requests** (in `.leetvibe/pending/`):
   - Show concepts that need quizzes generated
   - Indicate these need `/leetvibe:generate` to create

2. **Available Quizzes** (in `.leetvibe/quizzes/`):
   - Show quiz ID, concept, and file path
   - Check if solution exists in `.leetvibe/solutions/`
   - Mark as "Solved" if solution file exists, "Not started" otherwise

3. **Summary**:
   - Total quizzes available
   - How many solved vs unsolved
   - Suggest next action (e.g., "Try quiz 001 next")

## Output Format

```
LeetVibe Quizzes
================

Pending Generation:
  - memoization (from src/utils/fib.ts)
  - binary_search (from src/search.ts)

Available Quizzes:
  [001] Memoization      - Not started  (.leetvibe/quizzes/001-memoization.md)
  [002] Binary Search    - Solved       (.leetvibe/quizzes/002-binary_search.md)

Summary: 1/2 quizzes completed

Next: Open .leetvibe/quizzes/001-memoization.md to start!
```

If no `.leetvibe` directory exists, inform the user that no quizzes have been generated yet and explain how the system works.
