---
name: pr-description
description: Generate a PR description for the current branch following the PostHog PR template
argument-hint: [base-branch]
---

Write a PR description for the current branch following the PostHog PR template.

**Arguments:**

- `<base-branch>` - (optional) The base branch to compare against. Defaults to `master`.

## Steps

### Step 1: Gather branch context

Run these git commands to understand the changes:

1. Get the current branch name: `git rev-parse --abbrev-ref HEAD`
2. Determine the base branch: use `$ARGUMENTS` if provided, otherwise `master`
3. Get the list of commits: `git log --oneline <base>..HEAD`
4. Get the full diff: `git diff <base>...HEAD`
5. Get the diff stat: `git diff --stat <base>...HEAD`
6. Check for any uncommitted changes: `git status --short`

### Step 2: Read the PR template

Read the file `.github/pull_request_template.md` from the repo root. This is the source of truth for the PR description structure.

**Preserve the template's HTML comments verbatim in your output.** They are prompts for the human author and future editors, not scaffolding to discard. Place your content next to the comment it relates to — typically your content first, then the original comments below it, untouched.

### Step 3: Look for linked issues

Search commit messages and branch name for issue references (e.g., `#1234`, `posthog#1234`, `closes #1234`). If found, format as a full GitHub URL on its own line in the Problem section, placed **after** the template comments:

```
Closes https://github.com/PostHog/posthog/issues/1234
```

If no issue reference is found anywhere in commits or the branch name, leave a placeholder for the human to fill in:

```
Closes #
```

Do not invent issue numbers.

### Step 4: Detect change type

Based on the diff, determine:
- Are there frontend changes? (look for `.tsx`, `.ts`, `.scss` files under `frontend/`)
- Are there backend changes? (look for `.py` files)
- Are there migration changes?
- Are there test changes?

### Step 5: Write the PR description

**Tone: terse, direct, telegraphic.** Fragments are fine. The reviewer can read the diff — don't restate it. Avoid prose paragraphs anywhere. If you're tempted to add context, framework, or motivation, cut it. The PR description is a pointer to the diff, not a summary of it.

Fill in the template sections, keeping all HTML comments in place:

- **Problem**: 1 short declarative sentence stating the bare need or bug. Not a paragraph. Not "We're building X for users who…". Just "There is no way to review account notes." style. Place the `Closes` line from Step 3 below the template's comments.
- **Changes**: 3–6 short imperative bullets, **one line each**, present tense. Examples: "Make accounts rows expandable", "Display X in the expanded state", "Fix Y where Z was happening". Not a file-by-file changelog. Do not decorate with technical detail unless it's the actual point of the change. Do **not** add a "screenshots to be added" sentence — the template's existing comment already prompts for that and the human author pastes the image.
- **How did you test this code?**: One short line. As an agent, list only what you actually ran. If you ran the unit test suite, write `Unit tests`. **Never claim manual UI testing you didn't do** — even if the user typically does it, you didn't.
- **Publish to changelog?**: `No` (capitalized), unless the user says otherwise.
- **Docs update**: `No` (capitalized), unless docs were changed in this PR.
- **🤖 Agent context**: Add **one short line** at the top of the section, e.g. `Authored by Claude Code.` Keep all the template comments below it. Do not write paragraphs of decisions, summaries, or rationale — the commits and diff already cover that. If there's a genuinely non-obvious tradeoff the reviewer would otherwise miss, one extra short sentence is OK.

### Style reference (gold standard)

The following is the desired terseness and structure. Mirror it.

```markdown
## Problem
There is no way to do X.
<!-- Who are we building for, what are their needs, why is this important? -->

<!-- Does this fix an issue? Uncomment the line below with the issue ID to automatically close it when merged -->
<!-- Closes #ISSUE_ID -->

Closes https://github.com/<org>/<repo>/issues/<id>

## Changes
- Make rows expandable
- Display child items in the expanded state
- Clicking the item opens its detail view
- Fix creation via API, where we were only setting `text_content` but not `content` (the body looked empty in the editor)
<!-- If there are frontend changes, please include screenshots. -->
<!-- If a reference design was involved, include a link to the relevant Figma frame! -->

## How did you test this code?
Unit tests
<!-- ...template comments preserved... -->

## Publish to changelog?
No
<!-- ...template comments preserved... -->

## Docs update
No
<!-- ...template comments preserved... -->

## 🤖 Agent context
Authored by Claude Code.
<!-- ...template comments preserved... -->
```

### Output rules

- Output ONLY the filled-in template content, ready to paste into a PR
- CRITICAL: Output the final PR description inside a fenced code block (triple backticks with `markdown` language tag) so the user sees raw markdown they can copy-paste directly. Do NOT render it.
- Infer the purpose from commit messages, branch name, and actual code changes. Branch prefixes like `fix/`, `feat/`, `chore/` are signal.

## After completion

Assess how this skill performed:
- If the user had to provide significant guidance, corrections, or workarounds to get the task done, recommend running `/improve-skill` to capture those learnings. Explain briefly what could be improved.
- If the skill ran smoothly with minimal intervention, offer it as an option: "Would you like to run `/improve-skill` to refine this skill based on this session?"
