---
name: ship-it
description: Commit the current branch, update it safely, push it, and open or update a pull request.
argument-hint: "[base-branch] [--no-rebase]"
---

# Ship the branch

This skill opens or updates a pull request. It does not merge, enable auto-merge, or enter a merge queue.

## 1. Preflight

1. Read repository instructions and the current status.
2. Stop on the base branch or a detached `HEAD`.
3. Detect the base from the argument or `origin/HEAD`.
4. Check whether Graphite tracks the branch.
5. Check for an existing pull request.
6. Inspect all staged, unstaged, and untracked changes.

## 2. Commit

If the tree is dirty:

- Stage only files that belong to the branch's change.
- If ownership is unclear, show the groups and ask.
- Never use `git add -A` on a mixed tree.
- Write a terse commit message that follows repository rules.

Commit before rebasing. Do not hide work in a stash unless the user requests it.

## 3. Update the branch

Skip when `--no-rebase` is set.

Fetch the base first.

- For a Graphite stack, follow the repository's stacking skill and use Graphite to restack.
- For an ordinary branch, rebase onto `origin/<base>`.
- On conflicts, use `resolve-conflicts`.
- Stop when a conflict requires a product or design decision.

## 4. Verify

Run the checks required by the repository and the changed files. Do not claim checks that did not run.

## 5. Push

- Use Graphite submission for a tracked stack.
- Use `git push -u origin HEAD` for a new ordinary branch.
- After an ordinary rebase, use `git push --force-with-lease`.
- Never use plain `--force`.

## 6. Open or update the pull request

If a pull request exists, report it and update it only when needed.

Otherwise:

1. Generate the body with `pr-description`.
2. Follow the repository's current title and draft rules.
3. Open a draft when the repository defaults to drafts.
4. Set labels and assignee only when repository rules or the user require them.
5. Return the pull request URL.

## 7. Optional babysitting

Ask whether to run `babysit-prs` for merge-readiness. Babysitting still does not merge or enter a queue.

Before any Trunk submission, ask exactly:

> Do you want me to submit PR #<number> to the Trunk merge queue?

Wait for explicit confirmation naming that pull request.
