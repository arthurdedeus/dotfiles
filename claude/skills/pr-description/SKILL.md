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

Read the file `.github/pull_request_template.md` from the repo root. This is the source of truth for the PR description structure. Parse its sections (headings and HTML comments) to understand what to fill in.

### Step 3: Look for linked issues

Search commit messages and branch name for issue references (e.g., `#1234`, `ISSUE-1234`). If found, include them in the Problem section.

### Step 4: Detect change type

Based on the diff, determine:
- Are there frontend changes? (look for `.tsx`, `.ts`, `.scss` files under `frontend/`)
- Are there backend changes? (look for `.py` files)
- Are there migration changes?
- Are there test changes?

### Step 5: Write the PR description

Fill in the template sections from Step 2 with content derived from the diff:

- **Problem**: Explain the "why" — what user need or bug this addresses. Be concise but specific.
- **Changes**: Concise summary of what was done, not a file-by-file changelog. If there are frontend changes, mention that screenshots should be added. If a design was involved, mention Figma.
- **How did you test this code?**: Describe testing approach. If you are an agent, state that clearly and only list code-based tests you actually ran — do NOT claim manual testing you didn't do.
- **Publish to changelog?**: Write "no" unless the user says otherwise.
- **Docs update**: Leave empty (just keep the section).
- **LLM context**: Uncomment this section and note that Claude Code authored the PR description.

### Guidelines

- The Problem section should explain the "why" — what user need or bug this addresses
- The Changes section should be a concise summary of what was done, not a file-by-file changelog
- Infer the purpose from commit messages, branch name, and the actual code changes
- If the branch name follows a pattern like `fix/...`, `feat/...`, `chore/...`, use that to inform the description
- For the test section, check if test files were modified/added and mention them specifically
- Output ONLY the filled-in template content, ready to paste into a PR
- CRITICAL: Output the final PR description inside a fenced code block (triple backticks with `markdown` language tag) so the user sees raw markdown they can copy-paste directly. Do NOT render it.

## After completion

Assess how this skill performed:
- If the user had to provide significant guidance, corrections, or workarounds to get the task done, recommend running `/improve-skill` to capture those learnings. Explain briefly what could be improved.
- If the skill ran smoothly with minimal intervention, offer it as an option: "Would you like to run `/improve-skill` to refine this skill based on this session?"
