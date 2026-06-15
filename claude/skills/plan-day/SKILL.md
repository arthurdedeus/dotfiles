---
name: plan-day
description: Use when Arthur wants to plan his day, do his daily standup setup, or "roll over" / "spill over" yesterday's daily note — creates today's daily note in the Obsidian vault, carrying unfinished tasks forward with a #spillover tag.
---

# Plan day

Roll the most recent daily note forward into a new one for the current day: carry unfinished tasks over (tagged `#spillover`), fold the previous note's "For tomorrow" list into today's plan, and leave the old note as the record of that day.

Daily notes live in: `~/Documents/obsidian/PostHog/2 Areas/Daily notes/` named `YYYY-MM-DD.md`.

## Template

Every daily note uses exactly these three sections:

```markdown
# PostHog

# Personal

# For tomorrow
```

## Procedure

1. **Find the target date.** Today's date is in context (`currentDate`). The new note is `<today>.md`. If it already exists, ask whether to overwrite before doing anything.
2. **Find the source note.** The most recent existing note in the folder (highest date < today). `ls` the folder and pick it.
3. **Read the source note.** Identify, per section:
   - **Unfinished tasks** = any `- [ ]` line (and its indented sub-bullets). These carry over.
   - **Completed tasks** = `- [x]`. These do NOT carry over — they stay as the day's record.
   - **"For tomorrow" bullets** = plain `-` bullets under that heading. These become today's planned work.
4. **Write the new note** using the template:
   - Carry each unfinished `[ ]` item into the same section (PostHog → PostHog, Personal → Personal), appending ` #spillover` to the task line. Keep `#task` and `[[wikilinks]]` intact. Keep indented sub-bullets.
   - Fold the source's **"For tomorrow"** bullets into the new **# PostHog** section as fresh `- [ ]` tasks. These are planned, not spilled over — do **not** tag them `#spillover`. Preserve any links/sub-bullets (e.g. metabase URLs).
   - Leave the new **# For tomorrow** section empty (end-of-day capture).
   - A section with nothing to carry stays empty (just its heading).
5. **Leave the source note untouched.**
6. **Report** the new plan back to Arthur grouped by section, noting which items are `#spillover`.

## Notes

- `#spillover` marks work pulled from a prior day; "For tomorrow" items were already planned, so they don't get the tag.
- Don't invent or reword tasks — carry the exact text. The only edits are appending `#spillover` and converting "For tomorrow" bullets to `[ ]` checkboxes.
- If Personal has no unfinished items, that's normal — leave it empty.
