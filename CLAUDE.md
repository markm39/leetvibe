# LeetVibe Plugin Instructions

## Auto-Generate Quizzes on Hook Trigger

When you see `[LeetVibe:AutoGenerate]` in a PostToolUse hook output, you MUST immediately spawn a background agent to generate quizzes. Do this silently without interrupting the user.

### How to Handle the Trigger

When you see the trigger message, use the Task tool with these parameters:

```
subagent_type: "general-purpose"
run_in_background: true
prompt: "Generate LeetVibe quizzes from pending requests.
1. Use Glob to find .leetvibe/pending/*.json files
2. For each file, read the JSON containing: concept, quiz_id, source_file, source_code, language
3. Generate a LeetCode-style quiz that tests the concept
4. Write solution file to .leetvibe/solutions/{quiz_id}-{concept}.{ext}
5. Delete the pending file after successful generation
6. Use the format from the quiz-generator skill"
```

### Important

- Use `run_in_background: true` so it doesn't block the conversation
- Do NOT announce that you're generating quizzes - just do it silently
- The user should continue their work uninterrupted
