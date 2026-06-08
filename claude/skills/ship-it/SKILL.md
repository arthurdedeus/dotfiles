---
name: ship-it
description: Use when you want to ship the current branch end-to-end — get it current with its base, commit outstanding work, open a GitHub PR, and optionally drive it to merge. Triggers on "ship it", "ship this branch", "ship this", "open a PR for this branch".
argument-hint: [base-branch] [--no-rebase]
---

# Ship It

Take the current branch from work-in-progress to PR-open in one flow: rebase
onto the latest base, commit the outstanding diff, open a PR with a generated
description, and optionally hand off to babysitting.

Delegates the heavy lifting to existing skills — do NOT reimplement them:
`/pr-description` (PR body), `/babysit-prs` (drive to merge),
`/resolve-conflicts` (rebase conflicts).

## Arguments

- `[base-branch]` — base to rebase onto and target with the PR. If omitted,
  detect the repo default branch (see Step 1). PostHog repos use `master`;
  most others use `main`.
- `--no-rebase` — skip the rebase (Step 3). Also skip if the user says "don't
  rebase" / "skip the rebase".

## Steps

### Step 1: Preflight

1. Current branch: `git rev-parse --abbrev-ref HEAD`. If it's the base branch
   itself, or HEAD is detached, **stop** — there's nothing to ship.
2. Determine the base: use the argument if given, else detect the default:
   `git symbolic-ref --short refs/remotes/origin/HEAD` → strip the `origin/`
   prefix. Fallback if origin/HEAD is unset:
   `git remote show origin | sed -n '/HEAD branch/s/.*: //p'`.
3. `git status --short` and `git diff` — see what's uncommitted.

### Step 2: Commit the outstanding diff

Committing happens **before** the rebase: git refuses to rebase a dirty tree,
and a real commit is safer than a stash. The end state is identical.

1. Judge whether the uncommitted changes are **one coherent unit of work** (a
   single feature/fix for this branch) or a **mix of unrelated concerns**
   (the branch's work plus stray edits to unrelated config, other products,
   or files you didn't touch this session).
2. **Coherent** → stage and commit all: `git add -A && git commit`. Terse,
   capitalized message per global commit conventions.
3. **Unrelated / mixed** → **STOP and ask** the user which changes belong to
   this PR. Stage only those. Never blindly `git add -A` a mixed tree.
4. Already clean → skip.

### Step 3: Rebase onto the updated base

Skip entirely if `--no-rebase`.

1. `git fetch origin <base>`
2. `git rebase origin/<base>`
3. On conflicts → invoke `/resolve-conflicts`. If a conflict needs human
   judgement, stop and report rather than guessing.

### Step 4: Push

- No upstream yet: `git push -u origin HEAD`
- Rebased (history rewritten): `git push --force-with-lease`
- **Never** plain `git push --force`.

### Step 5: Open the PR

1. Check for an existing PR first: `gh pr view --json url,number,state`. If one
   is already open for this branch, report its URL and skip to Step 6 — do not
   create a duplicate.
2. Generate the body by running `/pr-description <base>`. Capture its output,
   strip the surrounding ```` ```markdown ```` fence, and write it to a temp
   file.
3. Create the PR:
   `gh pr create --base <base> --title "<title>" --body-file <tmpfile>`.
   Derive a terse, capitalized title from the branch name / lead commit. Use
   `--draft` only if the user asked for a draft.
4. Report the PR URL.

### Step 6: Offer to babysit

Ask the user one question: **"Want me to babysit this PR to merge-readiness?"**

- **Yes** → invoke `/babysit-prs <pr-number>`.
- **No** → report the PR URL and stop.

## Quick reference

| Situation | Action |
|-----------|--------|
| On base branch / detached HEAD | Stop — nothing to ship |
| Dirty tree, coherent | Commit all, then rebase |
| Dirty tree, unrelated mix | Ask which changes belong |
| Rebase conflict | `/resolve-conflicts`; defer if ambiguous |
| Pushing after rebase | `--force-with-lease`, never `--force` |
| PR already exists | Report it, skip creation |
| `--no-rebase` given | Skip Step 3 |

## Common mistakes

- **Rebasing before committing** — fails on a dirty tree. Commit (Step 2) first.
- **`git add -A` on a mixed tree** — silently pulls in unrelated changes. Ask.
- **Plain `git push --force`** — clobbers teammates' pushes. Use `--force-with-lease`.
- **Reimplementing description/babysit logic** — call `/pr-description` and `/babysit-prs`.
- **Creating a duplicate PR** — always `gh pr view` before `gh pr create`.

## After completion

If you had to provide significant guidance or corrections, recommend
`/improve-skill` to capture the learnings. If it ran smoothly, offer it.
