# LeetVibe

**Learn while you vibe code.** A Claude Code plugin that automatically generates LeetCode-style coding quizzes when new programming concepts appear in your code.

## How It Works

```
You code with Claude
        |
        v
Claude writes code using memoization
        |
        v
[LeetVibe] New concept: memoization
[LeetVibe] Generating quiz -> .leetvibe/solutions/001-memoization.ts
        |
        v
You keep coding (no interruption!)
        |
        v
When ready, solve the quiz in your IDE
        |
        v
$ leetvibe submit 001
All tests passed!
[COMPLETE] Quiz 001 marked as done!
```

## Installation

### Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/markm39/leetvibe/main/install.sh | bash
```

### Manual Install

```bash
git clone https://github.com/markm39/leetvibe.git ~/.leetvibe-plugin
chmod +x ~/.leetvibe-plugin/bin/leetvibe
export PATH="$PATH:$HOME/.leetvibe-plugin/bin"
```

## Usage

### 1. Start Claude with LeetVibe

```bash
# If you used the installer:
leetvibe-claude

# Or manually:
claude --plugin-dir ~/.leetvibe-plugin
```

### 2. Code Normally

Just code with Claude as usual. When Claude writes code using algorithms, data structures, or design patterns you haven't seen before, LeetVibe automatically:

- Detects the new concept
- Generates a quiz in the background
- Creates a solution file in `.leetvibe/solutions/`

### 3. Solve Quizzes (When You Want)

```bash
# List available quizzes
leetvibe list

# Open a quiz in your editor
code .leetvibe/solutions/001-memoization.ts

# Submit when done
leetvibe submit 001
```

### 4. Track Progress

```bash
leetvibe stats
```

## Quiz Format

Each quiz is a self-contained solution file:

```typescript
/**
 * ============================================================================
 * LEETVIBE QUIZ 001: Climbing Stairs
 * ============================================================================
 *
 * PROBLEM:
 * You are climbing a staircase with n steps. Each time you can climb 1 or 2 steps.
 * How many distinct ways can you reach the top? Use memoization for efficiency.
 *
 * EXAMPLES:
 *   climb_stairs(2) -> 2   (1+1 or 2)
 *   climb_stairs(3) -> 3   (1+1+1, 1+2, 2+1)
 *
 * HINTS:
 *   1. Think about the last step - you came from step n-1 or n-2
 *   2. ways(n) = ways(n-1) + ways(n-2) ... looks familiar?
 *
 * When ready, run: leetvibe submit 001
 * ============================================================================
 */

// TEST:001:{"input": [1], "expected": 1}
// TEST:001:{"input": [2], "expected": 2}
// TEST:001:{"input": [5], "expected": 8}

export function climb_stairs(n: number): number {
    // ====================== YOUR SOLUTION BELOW ======================

    // Your code here!

    // ====================== YOUR SOLUTION ABOVE ======================
}
```

## Supported Languages

LeetVibe generates quizzes in the same language as your source code:

- TypeScript / JavaScript
- Python
- C++
- Swift
- Kotlin

## Detected Concepts

LeetVibe recognizes these programming concepts:

**Algorithms:**
- Recursion, Memoization, Dynamic Programming
- Binary Search, Two Pointers, Sliding Window
- BFS, DFS, Backtracking, Greedy

**Data Structures:**
- Linked Lists, Trees, Graphs, Tries
- Heaps, Hash Maps, Stacks, Queues

**Design Patterns:**
- Factory, Singleton, Observer, Strategy

## CLI Commands

| Command | Description |
|---------|-------------|
| `leetvibe list` | List all available quizzes |
| `leetvibe submit <id>` | Test and submit a solution |
| `leetvibe stats` | Show learning progress |

## Files

```
.leetvibe/                    # Created in your project
  solutions/                  # Quiz files (solve these!)
    001-memoization.ts
    002-binary_search.py

~/.leetvibe/                  # Global config
  learning-history.json       # Your progress across all projects
```

## Requirements

- Claude Code CLI (`claude`)
- Python 3.8+
- Language-specific tools for running tests:
  - TypeScript: `tsx` or `ts-node` or `bun`
  - Python: `python3`
  - C++: `g++` or `clang++`
  - Swift: `swift`
  - Kotlin: `kotlinc`

## How Detection Works

LeetVibe uses a PostToolUse hook that fires after Claude writes code. It:

1. Analyzes the code using Claude CLI
2. Identifies programming concepts
3. Checks against your learning history
4. Generates quizzes only for new concepts
5. Runs entirely in the background (no interruption)

## License

MIT
