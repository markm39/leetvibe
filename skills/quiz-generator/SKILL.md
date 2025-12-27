---
name: quiz-generator
description: Generate LeetCode-style coding quizzes for programming concepts. Use when creating practice problems for algorithms, data structures, or design patterns.
allowed-tools: Read, Write, Bash
---

# Quiz Generator Skill

You generate LeetCode-style coding quizzes that help users practice programming concepts they've encountered while coding.

## Quiz Generation Process

When asked to generate a quiz for a concept:

1. **Choose an appropriate problem** that directly tests the concept
2. **Write a clear problem statement** with examples
3. **Generate comprehensive test cases** (5-10 cases including edge cases)
4. **Create the quiz file** in the correct format

## Quiz File Format

Quizzes are stored in `.leetvibe/quizzes/{id}-{concept}.md`:

```markdown
# Quiz {id}: {Concept Name}

## Context
Brief explanation of where this concept was used in the user's code.

## Problem
Clear problem statement with:
- Input/output description
- Constraints
- Examples with explanations

## Examples

### Example 1
**Input:** `data`
**Output:** `result`
**Explanation:** Why this is the answer.

### Example 2
**Input:** `data`
**Output:** `result`

## Solution File
Create your solution in: `.leetvibe/solutions/{id}-{concept}.{ext}`

Implement the function with this signature:
- TypeScript: `function solveProblem(input: Type): ReturnType`
- Python: `def solve_problem(input: type) -> return_type:`
- C++: `ReturnType solveProblem(InputType input)`
- Swift: `func solveProblem(_ input: Type) -> ReturnType`
- Kotlin: `fun solveProblem(input: Type): ReturnType`

## Test Cases
<!-- AUTO-GENERATED TEST CASES - DO NOT EDIT BELOW THIS LINE -->
```json
{
  "function_name": "solveProblem",
  "test_cases": [
    {"input": [arg1, arg2], "expected": result},
    ...
  ]
}
```

## Hints
<details>
<summary>Hint 1</summary>
First hint - approach suggestion
</details>

<details>
<summary>Hint 2</summary>
Second hint - more specific guidance
</details>

<details>
<summary>Hint 3</summary>
Key insight or algorithm step
</details>
```

## Concept-Specific Quiz Ideas

### Algorithms

**recursion**: Fibonacci variants, tree traversal, factorial, power function
**memoization**: Climbing stairs, coin change, unique paths
**dynamic_programming**: Longest common subsequence, knapsack, edit distance
**binary_search**: Search in rotated array, find peak element, sqrt(x)
**two_pointers**: Two sum (sorted), container with most water, 3sum
**sliding_window**: Maximum subarray sum of size k, longest substring without repeating
**bfs**: Level order traversal, shortest path in grid, rotting oranges
**dfs**: Number of islands, path sum, clone graph
**backtracking**: Permutations, combinations, N-queens, sudoku solver
**greedy**: Activity selection, jump game, gas station

### Data Structures

**linked_list**: Reverse list, detect cycle, merge two lists
**binary_tree**: Max depth, invert tree, validate BST
**heap**: Kth largest element, merge k sorted lists, top k frequent
**hash_map**: Two sum, group anagrams, valid anagram
**stack**: Valid parentheses, min stack, daily temperatures
**trie**: Implement trie, word search II, autocomplete
**graph**: Clone graph, course schedule, network delay time

### Design Patterns

**factory**: Create shape factory, document factory
**singleton**: Implement thread-safe singleton
**observer**: Event emitter, pub-sub system
**strategy**: Sorting strategy, payment method strategy

## Test Case Generation Rules

1. **Include basic cases**: Simple inputs that verify core logic
2. **Include edge cases**: Empty input, single element, maximum values
3. **Include stress cases**: Larger inputs to verify efficiency
4. **Match difficulty to concept**: Harder concepts get harder test cases
5. **Use realistic data**: Inputs should make sense for the problem

## Language-Specific Signatures

When generating the solution template, use these patterns:

### TypeScript/JavaScript
```typescript
// .leetvibe/solutions/001-memoization.ts
export function climbStairs(n: number): number {
  // Your solution here
}
```

### Python
```python
# .leetvibe/solutions/001-memoization.py
def climb_stairs(n: int) -> int:
    # Your solution here
    pass
```

### C++
```cpp
// .leetvibe/solutions/001-memoization.cpp
#include <vector>

int climbStairs(int n) {
    // Your solution here
}
```

### Swift
```swift
// .leetvibe/solutions/001-memoization.swift
func climbStairs(_ n: Int) -> Int {
    // Your solution here
}
```

### Kotlin
```kotlin
// .leetvibe/solutions/001-memoization.kt
fun climbStairs(n: Int): Int {
    // Your solution here
}
```

## Quality Checklist

Before finalizing a quiz, verify:
- [ ] Problem statement is clear and unambiguous
- [ ] Examples match the problem description
- [ ] Test cases cover edge cases
- [ ] Function signature is appropriate
- [ ] Hints provide progressive guidance without giving away the answer
- [ ] Difficulty matches the concept complexity
