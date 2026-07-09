---
name: handoff-babysit
description: Hand off babysitting the current PR to a PostHog Code cloud task so it keeps running after the laptop closes. Use when a PR is opened/reviewed and you want it driven to merge-readiness independently — "hand this off", "babysit in the cloud", "keep this PR green while I'm away".
argument-hint: [pr-number-or-url]
---

# Handoff babysit to a cloud task

Creates a PostHog Code **cloud** task (runs in PostHog's sandbox,
independent of this machine) that babysits a PR to merge-readiness:
CI green, review threads triaged, branch current with base. The cloud
agent does NOT merge.

Unlike `/babysit-prs` (which loops locally), this skill only creates and
starts the task, prints its URL, and terminates.

## Step 1: Resolve the PR

If `$ARGUMENTS` is a PR number or URL, use it; otherwise the current
branch's PR:

```bash
gh pr view [<arg>] --json number,title,url,headRefName,baseRefName,state,isDraft
gh repo view --json owner,name
```

- `MERGED`/`CLOSED` → abort, nothing to babysit.
- No PR → abort and tell the user to open one first (or use `/ship-it`).
- Detect stack membership (`gt log short`): remember whether the branch
  has a parent other than trunk or has children — it goes into the
  prompt below.

## Step 2: Get the API key

Try in order — env var, 1Password, macOS Keychain:

```bash
KEY="${POSTHOG_PERSONAL_API_KEY:-$(op read 'op://Private/PostHog personal API key/credential' 2>/dev/null)}"
KEY="${KEY:-$(security find-generic-password -s posthog-personal-api-key -w 2>/dev/null)}"
```

The 1Password read may pop a biometric prompt; in a headless session it
fails silently and the Keychain fallback covers it.

All empty → abort and tell the user to create a personal API key with
the `task` scope and store it in either place:

```bash
op item create --category "API Credential" --title "PostHog personal API key" --vault Private credential='<key>'
security add-generic-password -a "$USER" -s posthog-personal-api-key -w '<key>' -U
```

## Step 3: Create the task

`POST https://us.posthog.com/api/projects/2/tasks/` with
`Authorization: Bearer $KEY`, body:

- `title`: `Babysit PR #<number>: <pr title>`
- `repository`: `<owner>/<repo>`
- `description`: the prompt below, with placeholders filled in.

The cloud agent has the repo's skills (`/debugging-ci-failures`, ...)
but NOT this machine's personal skills, so the prompt is self-contained:

```markdown
Babysit <pr_url> (branch `<headRefName>`, base `<baseRefName>`, draft: <isDraft>, stacked: <yes/no>) until it is merge-ready. Loop: check state, act on clear cases, wait for CI, repeat. Do NOT merge the PR.

Done when ALL hold — then post a summary comment on the PR and finish:
- CI green, or the only red checks also fail on recent base-branch runs (flaky — note them, don't gate on them).
- No open actionable review threads (ambiguous ones deferred, listed in the summary).
- Branch conflict-free and current with base.
Terminate immediately if the PR gets merged or closed.

Each pass:
1. **Branch currency**: if GitHub reports CONFLICTING/DIRTY/BEHIND, rebase onto latest base. Resolve mechanical conflicts; if both sides changed the same logical lines with different intent, stop and report — don't guess.
2. **Review threads**: read via GraphQL `reviewThreads` (REST lacks `isResolved`); skip resolved/outdated. Bot-authored + clear localized fix → apply, push, reply with the SHA, resolve the thread. Bot-authored but wrong/out-of-scope → reply one-line pushback, resolve. Ambiguous/architectural → leave unresolved, list in summary. Author comments on a draft PR are directives — apply them; on a non-draft PR leave them for the human.
3. **CI**: for each failing check, compare against recent base-branch runs of the same workflow. Red on base too → flaky, skip. Genuine → diagnose with the repo's /debugging-ci-failures skill, fix, push. If unfixable after a real attempt, defer and list it.
4. Push fixes to the PR branch. <if stacked: "This branch is part of a Graphite stack — do NOT force-push or rebase it yourself; if it needs a restack, stop and report instead.">

Every comment you post must start with this exact line:
> 🤖 Automated comment written by Arthur robots

Follow the repo's CLAUDE.md commit conventions. Batch commits before pushing — each push burns CI credits.
```

## Step 4: Start a cloud run

```bash
curl -sS -X POST https://us.posthog.com/api/projects/2/tasks/<task_id>/run/ \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"branch": "<headRefName>"}'
```

Verify the response's `latest_run` has `environment: "cloud"` and status
`queued` or `in_progress`. A 429 means the team is over its posthog_code
usage limit — report and stop.

## Step 5: Report and terminate

Print one line and stop — no polling, the whole point is that it runs
without this session:

```
[handoff] PR #<n> → cloud task <slug> queued — https://us.posthog.com/project/2/tasks/<task_id>
```
