---
name: plan-day
description: Create today's Obsidian daily note and carry unfinished work forward with a #spillover tag.
---

# Plan the day

Daily notes live in `~/Documents/obsidian/PostHog/2 Areas/Daily notes/` as `YYYY-MM-DD.md`.

Use this exact structure:

```markdown
# PostHog

# Personal

# For tomorrow
```

## Procedure

1. Use the current date for the new filename.
2. If today's note exists, read it and ask before replacing it.
3. Find the latest older daily note.
4. Read each section and its nested bullets.
5. Copy each unfinished `- [ ]` task into the same section.
6. Append `#spillover` to copied task lines. Preserve tags, links, and nested bullets.
7. Convert plain bullets under `# For tomorrow` into unchecked PostHog tasks.
8. Do not add `#spillover` to planned tasks from `# For tomorrow`.
9. Leave today's `# For tomorrow` section empty.
10. Leave the source note unchanged.

Do not copy completed tasks. Do not invent or rewrite task text.

Report today's PostHog and Personal tasks. Mark spilled tasks clearly.
