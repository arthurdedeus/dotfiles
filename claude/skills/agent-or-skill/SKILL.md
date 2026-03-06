---
name: agent-or-skill
description: Help decide whether a use case should be built as a skill or an agent
---

The user wants to build something for Claude Code but isn't sure whether it should be a **skill** or an **agent**. Ask them to describe the use case if they haven't already, then advise based on these criteria:

## Decision framework

### Build a SKILL when:
- It's a repeatable workflow invoked with a `/slash-command`
- It runs inline in the current conversation and the user interacts with results directly
- It encodes a procedure, convention, or reference material (step-by-step instructions)
- It takes arguments and produces output the user acts on immediately
- It benefits from supporting files (scripts, templates, examples)

Examples: generating PR descriptions, fixing migrations, writing tests, creating standup summaries, resolving merge conflicts.

### Build an AGENT when:
- The task needs deep, focused analysis in isolation (don't pollute the main context)
- It should "go away and come back with results" — a clear hand-off moment
- It benefits from a specialized system prompt with domain expertise baked in
- It needs different tool restrictions (e.g., read-only for a reviewer)
- It needs a different model (e.g., Haiku for fast exploration, Opus for complex reasoning)
- The output is a structured artifact (review report, root cause analysis, implementation plan)

Examples: code review, bug root cause analysis, implementation planning, security audit, task orchestration across multiple steps.

### Key question to ask yourself:
**"Am I encoding a workflow I trigger, or delegating a role I'd hand off?"**
- Workflow I trigger → Skill
- Role I hand off → Agent

## Response format

After hearing the use case:
1. Recommend **skill** or **agent** with a one-sentence reason
2. If the answer isn't clear-cut, explain the tradeoff
3. Suggest a name and briefly outline what the file should contain
