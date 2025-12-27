---
description: Submit and test a LeetVibe quiz solution
allowed-tools: Read, Bash
---

# Submit LeetVibe Solution

Run tests against the user's solution for quiz $ARGUMENTS.

## Process

1. **Parse the quiz ID** from $ARGUMENTS (e.g., "001" or "1")

2. **Find the solution file** in `.leetvibe/solutions/`:
   - Look for files matching `{quiz_id}-*` with any supported extension
   - Supported: .py, .ts, .js, .cpp, .swift, .kt

3. **Find the quiz file** in `.leetvibe/quizzes/`:
   - Match `{quiz_id}-*.md`

4. **Run the test checker**:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_solution.py" {quiz_id}
   ```

5. **Report results**:
   - Show pass/fail for each test case
   - Display input, expected output, and actual output for failures
   - Show final score (e.g., "5/6 tests passed")

## If Solution Not Found

Tell the user to create their solution file:
```
No solution found for quiz {id}.

Create your solution in one of these formats:
  .leetvibe/solutions/{id}-{concept}.py
  .leetvibe/solutions/{id}-{concept}.ts
  .leetvibe/solutions/{id}-{concept}.cpp
  .leetvibe/solutions/{id}-{concept}.swift
  .leetvibe/solutions/{id}-{concept}.kt
```

## Success Message

If all tests pass:
```
All tests passed! Great work on mastering {concept}!

Your learning history has been updated.
```

## Arguments

$ARGUMENTS should be the quiz ID, e.g.:
- `/leetvibe:submit 001`
- `/leetvibe:submit 1`
