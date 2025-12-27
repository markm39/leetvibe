---
description: Get a hint for a LeetVibe quiz
allowed-tools: Read
---

# Get Hint for LeetVibe Quiz

Provide progressive hints for quiz $ARGUMENTS without giving away the answer.

## Process

1. **Find the quiz file** for the given ID in `.leetvibe/quizzes/`

2. **Check for existing hints** in the quiz markdown (under `## Hints` section)

3. **If hints exist**: Show the next unseen hint
   - Track which hints have been shown in conversation context
   - Reveal hints progressively (Hint 1, then Hint 2, etc.)

4. **If no hints section**: Generate appropriate hints based on:
   - The problem description
   - The concept being tested
   - Common approaches for this type of problem

## Hint Guidelines

- **Hint 1**: General approach or technique to consider
- **Hint 2**: More specific guidance on data structures or algorithms
- **Hint 3**: Key insight or edge case to handle
- **Final hint**: Pseudocode or step-by-step approach (but NOT the solution)

## Output Format

```
Hint for Quiz {id}: {Concept}

Hint {n}:
{hint content}

{remaining hints available or "No more hints - you've got this!"}
```

## Arguments

$ARGUMENTS should be the quiz ID:
- `/leetvibe:hint 001`
- `/leetvibe:hint 1`
