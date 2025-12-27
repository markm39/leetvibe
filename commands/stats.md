---
description: Show LeetVibe learning statistics
allowed-tools: Read, Bash
---

# LeetVibe Learning Statistics

Display the user's learning progress from `~/.leetvibe/learning-history.json`.

## Information to Show

1. **Overall Progress**:
   - Total concepts encountered
   - Quizzes completed
   - Quizzes skipped
   - Quizzes pending

2. **Score Summary**:
   - Average score on completed quizzes
   - Perfect scores count

3. **Concepts by Category**:
   - Algorithms mastered
   - Data structures practiced
   - Design patterns learned
   - Language features explored

4. **Recent Activity**:
   - Last 5 concepts encountered
   - When they were first seen
   - Quiz status for each

## Output Format

```
LeetVibe Learning Stats
=======================

Progress
--------
Concepts encountered:  15
Quizzes completed:     8 (53%)
Quizzes skipped:       2
Quizzes pending:       5

Scores
------
Average score:         87%
Perfect scores:        5

By Category
-----------
Algorithms:      recursion, memoization, binary_search, dfs
Data Structures: linked_list, binary_tree, hash_map
Patterns:        factory, observer
Language:        async_await

Recent Activity
---------------
1. memoization     - Completed (100%) - 2 days ago
2. binary_search   - Pending          - 3 days ago
3. linked_list     - Completed (83%)  - 1 week ago
4. recursion       - Completed (100%) - 2 weeks ago
5. hash_map        - Skipped          - 2 weeks ago
```

If no learning history exists, show a welcome message explaining how to get started.
