---
name: tracking-tasks-in-obsidian
description: Track context, decisions, issue links, and progress for a non-trivial task in Arthur's Obsidian PARA vault.
argument-hint: "[task title]"
---

# Track tasks in Obsidian

Vault: `~/Documents/obsidian/PostHog`

Use this skill for work with several steps, decisions, or handoffs. Skip quick edits and factual questions.

## Start or resume

1. Choose a short sentence-case title.
2. Find or propose the note path:

```bash
~/.claude/skills/tracking-tasks-in-obsidian/scripts/task-file.sh "<Title>" "1 Projects"
```

3. If the script returns `found`, read and append to that note.
4. If it returns `new`, create the note with the template below.
5. Find the related GitHub issue when one is available.
6. Add the full issue URL under **Links**.

Check issue sources in this order:

- An issue supplied by the user.
- A linked or closing issue on the current pull request.
- A verified issue reference in the branch name or commits.
- An issue already named in the task conversation.

Never infer an issue number. If no issue is available, omit the issue link. Add it later when one becomes available.

## Update the note

Append an entry after a decision, direction change, milestone, or handoff. Record why the change happened.

Keep these fields current:

- Status.
- GitHub issue and pull request URLs.
- Branch and key files.
- Decisions and rejected alternatives.
- Remaining questions and next action.

Use `1 Projects` for work with an end state. Use `2 Areas` only for an ongoing responsibility.

When the task finishes, add the outcome. Move the note to `4 Archives` when no follow-up remains.

## Template

```markdown
# <Title>

One-line goal and reason.

- **Status:** In progress
- **Links:**
  - GitHub issue: <full URL, when available>
  - Pull request: <full URL, when available>
  - Branch: `<branch>`
  - Key files: `<paths>`

## Goal / context

## Key decisions
- **Decision** — **Why:** reason. Alternatives: …

## Progress log
- <YYYY-MM-DD> — result and lesson.

## Open questions / follow-ups
- …
```

Use bullet-heavy Markdown and wikilinks. Do not add YAML frontmatter.
