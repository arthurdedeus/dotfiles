---
name: note
description: Capture a complex technical discovery as a reusable, repository-scoped note.
argument-hint: "[find|<slug>]"
---

# Technical discovery note

Store durable technical knowledge under `~/.claude/notes/<org>/<repo>/`.

Use a lowercase kebab-case slug. Let the scripts derive the repository and path.

## Find notes

For `/note find`, run:

```bash
~/.claude/skills/note/scripts/note-list.sh
```

For `/note find <slug>`, run:

```bash
~/.claude/skills/note/scripts/note-find.sh <slug>
```

Show matching titles and paths. Read a requested note. Do not create files in find mode.

## Create or update a note

1. If the slug is missing, propose one from the current discovery and ask for confirmation.
2. Run:

```bash
~/.claude/skills/note/scripts/note-find-or-create.sh <slug>
```

3. If the note exists, read it before editing.
4. If the note is new, use `templates/discovery-note.md` and today's date.
5. Add verified findings from the current session.
6. Preserve useful existing material and remove superseded claims.

Never build note paths by hand.

## Content standard

A note should let another engineer avoid the same investigation. Include:

- The behavior and why it matters.
- The mechanism that causes it.
- How the finding was verified.
- Practical checks, commands, or examples.
- Links to files, commits, issues, or pull requests.
- Limits, unknowns, and stale assumptions to recheck.

Do not store a session transcript. Keep the conclusion and the evidence needed to trust it.
