---
name: improve-skill
description: Refine a skill or agent after a session reveals a reusable failure pattern, missing guardrail, or stale instruction.
---

# Improve a skill or agent

Use this skill for reusable lessons. Do not encode one-off fixes.

## Workflow

1. Identify the skill or agent used in the session.
2. Locate its source from the active skill manifest or agent configuration.
3. Read the full source and any referenced files.
4. Review the session for wasted work, missed checks, bad ordering, and unsafe defaults.
5. Separate reusable patterns from case-specific details.
6. Draft the smallest change that prevents the same failure class.
7. Show the proposed change and rationale before editing.
8. Apply the approved edit.
9. Read the full result and run any available validation.

## Include

Include a lesson when it:

- Applies to a class of tasks.
- Names a signal that an agent can recognize.
- Gives a clear response to that signal.
- Saves time or prevents harm in later sessions.

## Exclude

Exclude a lesson when it:

- Names one file, variable, customer, or incident.
- Repeats existing guidance.
- Belongs in repository instructions instead.
- Adds more text than future value.

## Editing rules

- Prefer one edit in an existing step.
- Add a section only when no current section fits.
- Replace stale or wrong text instead of layering exceptions over it.
- Keep the skill internally consistent.
- Limit each pass to the highest-value changes.

If the skill's core approach is wrong, propose a rewrite instead of patching it.
