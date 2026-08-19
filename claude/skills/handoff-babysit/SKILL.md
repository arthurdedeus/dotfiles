---
name: handoff-babysit
description: Start a PostHog Code cloud task that drives a pull request to merge-readiness after the local session ends.
argument-hint: "[pr-number-or-url]"
---

# Hand off pull request babysitting

Create one cloud task, start it, return its URL, and stop. The cloud agent must not merge or enter a queue.

## 1. Resolve the pull request

Use the argument or current branch. Read:

```bash
gh pr view [<argument>] --json number,title,url,headRefName,baseRefName,state,isDraft
gh repo view --json owner,name
```

Stop if the pull request is missing, merged, or closed. Record whether Graphite tracks the branch.

## 2. Get the API key

Try the environment, then approved local secret stores:

```bash
KEY="${POSTHOG_PERSONAL_API_KEY:-$(op read 'op://Private/PostHog personal API key/credential' 2>/dev/null)}"
KEY="${KEY:-$(security find-generic-password -s posthog-personal-api-key -w 2>/dev/null)}"
```

If no key exists, ask the user to create one with the `task` scope. Do not print, log, or place the key in command history.

## 3. Create the task

POST to `https://us.posthog.com/api/projects/2/tasks/` with the bearer key.

Set:

- `title`: `Babysit PR #<number>: <title>`
- `repository`: `<owner>/<repo>`
- `description`: the prompt below

```markdown
Drive <pr-url> to merge-readiness. Do not merge, enable auto-merge, or submit it to a queue.

Context: head `<head>`, base `<base>`, draft `<draft>`, Graphite stack `<stacked>`.

Done only when every required CI check is green, every review thread is resolved, and the branch is current and conflict-free.

Each pass:
1. Refresh PR state. Stop if it is merged or closed.
2. Update the branch safely. Use repository conflict and stack instructions. Defer intent conflicts.
3. Read review threads through GraphQL. Skip resolved or outdated threads.
4. Fix clear bot findings. Push back on incorrect findings. Defer human or architectural decisions.
5. Diagnose genuine CI failures with repository skills. Rerun confirmed flakes, but do not waive red checks.
6. Batch verified fixes before pushing.

Every posted comment starts with:
> 🤖 Automated comment written by Arthur robots

Post a final summary with checks, threads, branch state, fixes, and deferred items. Follow repository commit and public-data rules.
```

For a Graphite stack, tell the cloud agent not to rebase or force-push without stack-aware tooling.

## 4. Start and verify

POST to `/api/projects/2/tasks/<task-id>/run/` with the head branch.

Verify that `latest_run.environment` is `cloud` and status is `queued` or `in_progress`. Report rate limits or API errors without retry loops.

## 5. Return

```text
[handoff] PR #<number> → cloud task <slug> queued — https://us.posthog.com/project/2/tasks/<task-id>
```
