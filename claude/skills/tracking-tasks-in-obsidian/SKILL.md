---
name: tracking-tasks-in-obsidian
description: Keep a living record of a non-trivial task's context, decisions, and rationale in Arthur's Obsidian vault (PARA + Kanban). Use at task start (once scope is clear) and at each significant decision, direction change, milestone, or wrap-up.
argument-hint: [task title]
---

# Tracking tasks in Obsidian

Keep a living document of a task's context, decisions, and thought process in the Obsidian vault as the work unfolds — so the *why* behind choices survives the session. Place the note correctly per PARA, and surface it on the Kanban dashboard.

Vault root (holds the PARA folders and `Dashboard.md`): `~/Documents/obsidian/PostHog`.

## When to use

- Starting substantial work: a feature, bug investigation, refactor, design, or multi-step task.
- You're a few prompts into something that turned out to be non-trivial and isn't tracked yet.
- Resuming, redirecting, deciding something significant, or finishing a tracked task.

**Skip for:** trivial one-off requests, pure Q&A, or quick edits. Don't track what doesn't deserve a paper trail.

This is a judgment call the agent makes — invoke it proactively; the user shouldn't have to ask.

## Boundary

| This skill | `/note` |
| --- | --- |
| Living task log in the Obsidian vault | Durable technical discovery in `~/.claude/notes/` |
| The journey: decisions, rationale, progress, status | The conclusion: how a system works, reusable forever |
| Linked on the Kanban dashboard | Per-repo reference, not on the board |

## Workflow

### 1. Find or create the tracking note

Pick a concise, human-readable **Title in sentence case** (e.g. `Multi-select role filter`). This exact string is both the filename and the `[[wikilink]]` on the board — keep it identical.

Decide the PARA folder (see table), then:

```bash
~/.claude/skills/tracking-tasks-in-obsidian/scripts/task-file.sh "<Title>" "<PARA folder>"
```

- `found\t<path>` → **read it and append**, never duplicate or overwrite history.
- `new\t<path>` → create it with the template below (`mkdir -p` the parent first).

### 2. Put it on the dashboard (kicked-off → In Progress)

```bash
~/.claude/skills/tracking-tasks-in-obsidian/scripts/dashboard-card.sh "<Title>"
```

Defaults to the **In Progress** column; the card `- [ ] [[<Title>]]` links straight to the note. The script *ensures* the card is in the column you pass — it adds the card if absent, **moves** it (preserving the card line) if it's elsewhere, and no-ops if it's already there. So always pass the column that matches the task's current phase.

### 3. Keep it alive as the work develops

Append at meaningful moments — after a key decision, when changing direction, hitting a milestone, before a long context handoff, and at the end. Capture the **why**, not just the what: alternatives considered and rejected, dead-ends, constraints discovered, links to branches/PRs/files. This is the part that's easy to skip and the most valuable — the reasoning is the point.

### 4. Move the card as the task progresses

The board column should reflect the task's phase. Re-run the same script with the new column at each transition — it moves the existing card:

```bash
~/.claude/skills/tracking-tasks-in-obsidian/scripts/dashboard-card.sh "<Title>" "In Review"   # PR opened
~/.claude/skills/tracking-tasks-in-obsidian/scripts/dashboard-card.sh "<Title>" "Done"         # merged / shipped
```

On completion, summarize the outcome in the note, and relocate it to `4 Archives` if the work is fully done. (Column names must match your board's headings exactly — the script errors out rather than guessing.)

## PARA placement

Tiago Forte's PARA, by **actionability**. A task almost always starts as a Project.

| Folder | Holds | Use for a task when… |
| --- | --- | --- |
| `1 Projects` | Efforts with a goal and a finish line | **Default.** Feature, bug, investigation, design — anything with an end state. |
| `2 Areas` | Ongoing responsibilities, no end date | It's a standing duty (on-call, recurring review), not a one-off. |
| `3 Resources` | Reference topics / interests | It's durable knowledge, not active work — prefer `/note` or a `3 Resources` subtopic. |
| `4 Archives` | Inactive items from the above | Only when parking or completing — never where work *starts*. |

Default to a single file `1 Projects/<Title>.md`. Use a subfolder only if the project will clearly spawn several notes.

## Note template

```markdown
# <Title>

One-line what-and-why.

- **Status:** In progress
- **Links:** branch `…`, PR #…, key files

## Goal / context
What we're doing and why it matters.

## Key decisions
- **<decision>** — **Why:** rationale. Alternatives considered: …

## Progress log
- <YYYY-MM-DD> — what happened, what was learned.

## Open questions / follow-ups
- …
```

Match the vault's existing notes: sentence-case headings, bullet-heavy, `[[wikilinks]]` to related notes, no YAML frontmatter (only `Dashboard.md` has it).

## Common mistakes

- **Filename ≠ card text.** They must match exactly or the `[[wikilink]]` breaks. Pass the same `<Title>` to both scripts.
- **Logging only the what.** The reasoning behind choices is the whole point — write the *why*.
- **Creating a second note** for the same task instead of reading and appending to the one `task-file.sh` returns as `found`.
- **Editing `Dashboard.md` by hand** — the script adds *and* moves cards idempotently; let it own the board.
- **Tracking trivia.** A skill invocation and a board card for a one-liner is noise.
