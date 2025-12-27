---
description: Skip a LeetVibe quiz
allowed-tools: Read, Bash
---

# Skip LeetVibe Quiz

Mark quiz $ARGUMENTS as skipped in the learning history.

## Process

1. **Validate quiz exists** in `.leetvibe/quizzes/`

2. **Update learning history** at `~/.leetvibe/learning-history.json`:
   - Set `quiz_skipped: true` for the concept
   - Record `skipped_at` timestamp

3. **Optionally move quiz** to a `.leetvibe/skipped/` directory

4. **Confirm to user**

## Output

```
Skipped quiz {id}: {concept}

You can revisit this later with /leetvibe:unskip {id}
or delete the entry from ~/.leetvibe/learning-history.json
```

## Arguments

$ARGUMENTS should be the quiz ID:
- `/leetvibe:skip 001`
