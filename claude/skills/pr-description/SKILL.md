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

### Step 2: Look for linked issues

Search commit messages and branch name for issue references (e.g., `#1234`, `ISSUE-1234`). If found, include them in the Problem section.

### Step 3: Detect change type

Based on the diff, determine:
- Are there frontend changes? (look for `.tsx`, `.ts`, `.scss` files under `frontend/`)
- Are there backend changes? (look for `.py` files)
- Are there migration changes?
- Are there test changes?

### Step 4: Write the PR description

Generate a PR description using this exact template structure:

```markdown
## Problem

_Explain who we're building for, what their needs are, and why this is important. Be concise but specific._

<!-- Closes #ISSUE_ID -->

## Changes

_Describe what was changed and why. If there are frontend changes, mention that screenshots should be added. If a design was involved, mention Figma._

- Bullet point summary of key changes

## How did you test this code?

_Describe testing approach: automated tests added/modified, manual testing steps._
```

### Guidelines

- The Problem section should explain the "why" - what user need or bug this addresses
- The Changes section should be a concise summary of what was done, not a file-by-file changelog
- Infer the purpose from commit messages, branch name, and the actual code changes
- If the branch name follows a pattern like `fix/...`, `feat/...`, `chore/...`, use that to inform the description
- For the test section, check if test files were modified/added and mention them specifically
- Do NOT include the changelog section or coding conventions reminder - those are already in the template
- Output ONLY the markdown content (Problem, Changes, Test sections), ready to paste into a PR
- CRITICAL: Output the final PR description inside a fenced code block (triple backticks with `markdown` language tag) so the user sees raw markdown they can copy-paste directly. Do NOT render it.
