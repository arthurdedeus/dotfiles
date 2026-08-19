---
name: babysit-prs
description: Drive a pull request to merge-readiness by fixing clear CI failures, triaging review threads, and keeping its branch current.
argument-hint: "[pr-number-or-url] [--no-stamphog]"
---

# Babysit pull requests

Act on clear cases. Defer decisions. Never merge, enable auto-merge, or submit to a merge queue.

Use `orwell-writing` for comments and user-facing summaries.

## Done state

Report **merge-ready** only when:

- Every required CI check is green.
- Every review thread is resolved.
- The branch is conflict-free and current with its base.

Report **deferred-to-user** when unresolved work needs a human decision.

Stop if the pull request is merged, closed, or interrupted.

## Comment header

Start every GitHub comment with:

```markdown
> 🤖 Automated comment written by R2
```

## One pass

### 1. Resolve the pull request

Use the argument or the current branch's pull request. Record:

- Repository and pull request number.
- Head and base branches.
- Head SHA.
- State and draft status.
- Merge state.
- Graphite stack membership.

Do not hardcode the base branch. If no pull request exists, ask for a number or permission to open one.

### 2. Update the branch

If the branch is behind or conflicting:

- Use Graphite for a tracked stack.
- Use an ordinary rebase for an ordinary branch.
- Delegate migration numbering conflicts to `fix-migrations`.
- Delegate other conflicts to `resolve-conflicts`.
- Stop when both sides changed the same behavior with different intent.

Refresh the head SHA after any update.

### 3. Triage review threads

Read threads through GraphQL `reviewThreads`. REST review comments do not expose resolution state.

Skip resolved and outdated threads.

For each open thread:

- **Clear bot finding:** fix it, verify it, reply with the fix SHA, then resolve.
- **Wrong or out of scope bot finding:** post a short reason, then resolve.
- **Ambiguous bot finding:** leave open and defer.
- **PR author on a draft:** treat the comment as a requested change.
- **Any other human comment:** leave it for the human unless they explicitly delegated it.

Reply before resolving. Never resolve a thread without addressing it.

### 4. Fix CI

Read current checks with:

```bash
gh pr checks <number> --json name,state,bucket,link
```

For each failed required check:

1. Compare it with recent base-branch runs when flakiness is plausible.
2. Rerun a confirmed flake.
3. Use `fix-ci` for a genuine failure.
4. Defer after three failed flake reruns or one unresolved genuine diagnosis.

A flaky red check still blocks merge-readiness.

### 5. Request Stamphog approval

Skip with `--no-stamphog`.

Add the `stamphog` label only when:

- No review thread remains open.
- No CI check is red.
- The label exists.
- The pull request lacks the label.
- Stamphog has not approved already.
- A human did not remove the label earlier.

Do not wait for Stamphog approval. Handle any new threads in the next pass.

### 6. Push

- Use Graphite submission for a tracked stack.
- Use `git push` for an ordinary branch.
- Batch related changes before pushing.

Do not install missing tools without asking.

### 7. Continue or stop

Re-read checks, threads, and merge state.

- If done, report **merge-ready** and stop.
- If only deferred work remains, report **deferred-to-user** and stop.
- If CI is pending, schedule another pass when the harness supports wakeups.
- If no scheduler exists, report the pending state and stop without busy-waiting.

## Pass summary

Use one status line:

```text
[babysit] sha=<short> ci=<pass:N pending:N fail:N> threads=<open:N deferred:N> branch=<current|updated|conflict> → <merge-ready|waiting|deferred-to-user>
```

List each deferred thread, conflict, or check with one reason.
