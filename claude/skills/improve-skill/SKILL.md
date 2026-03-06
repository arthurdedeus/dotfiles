---
name: improve-skill
description: Refine a skill or agent after using it by incorporating generalizable patterns from the session. Use after a skill/agent produced suboptimal guidance, missed a failure class, or required workarounds. Not for one-off fixes.
---

# Improve a skill or agent from session learnings

After using a skill or agent, review how it performed and fold recurring, generalizable patterns back into its definition.

## Step 1: Identify the skill or agent

Determine which skill or agent was used in this session. Read its `.md` file.

For skills: check `.agents/skills/` first (source of truth, symlinked to `.claude/skills/`), then `.claude/skills/`.
For agents: check `~/.claude/agents/` for agent `.md` files.

## Step 2: Reflect on the session

Review what happened during the skill's execution. Identify:

- **Wasted work** — Did the skill lead you to attempt fixes/actions that were futile? What signal, if recognized earlier, would have avoided that?
- **Missing triage** — Were there error classes or preconditions the skill didn't teach you to check upfront?
- **Missing patterns** — Did you discover a recurring fix strategy, workaround, or rule that the skill doesn't cover?
- **Wrong ordering** — Would reordering the skill's steps have produced a better outcome?
- **Missing guardrails** — Did you do something the skill should explicitly warn against?

## Step 3: Filter for generalizability

For each candidate improvement from Step 2, apply these filters:

### Include if:

- The pattern applies to a **class** of inputs, not a single instance (e.g. "stale generated types" vs "logicType.ts line 42 was wrong")
- It would save time in **future sessions** with different specific details
- It describes a **root cause category** and its resolution strategy
- It extends an existing concept in the skill (e.g. adding a new entry to a triage checklist, a new rule to a rules list)

### Exclude if:

- It is a one-off fix for a specific file, variable, or error message
- It encodes a preference that belongs in `CLAUDE.md` or `CLAUDE.local.md`, not the skill
- It duplicates guidance already present in the skill
- It would make the skill significantly longer without proportional value

## Step 4: Choose the integration point

Improvements should extend the skill's existing structure, not restructure it. Prefer:

1. **Adding an entry to an existing list** (triage checklist, rules, fix priority) — lowest friction
2. **Adding a new subsection** within an existing step — when the pattern needs more context than a bullet
3. **Adding a new step** — only when the improvement represents a distinct phase the skill doesn't cover at all

Avoid renumbering existing steps if possible (use X.5 numbering for insertions between steps to keep the existing mental model stable).

## Step 5: Apply and verify

1. Draft the specific text changes
2. Present the changes to the user with a brief rationale for each
3. On approval, apply the edits to the skill file
4. Read the full skill file back to verify it reads coherently with the additions

## Rules

- Keep additions concise — match the density and tone of the surrounding skill text
- Use bold lead-ins for list entries to enable scanning (e.g. `**Pattern name** — description`)
- Never remove existing content unless it is demonstrably wrong or superseded by the new addition
- If the session revealed that the skill's entire approach is wrong, flag this to the user rather than patching around it — a rewrite may be warranted
- Do not add session-specific examples (file paths, exact error text). Instead, describe the pattern abstractly with enough detail to recognize it
- Limit changes to 1-3 additions per invocation to avoid skill bloat. If there are more candidates, prioritize by time-saved-per-future-session
