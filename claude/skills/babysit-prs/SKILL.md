---
name: babysit-prs
description: Drive a PR to merge-readiness hands-off — self-loops over CI, review threads, and branch currency, acting on clear cases and deferring ambiguous ones. Orchestrates /fix-ci, /fix-migrations, /resolve-conflicts. Stops when CI is green and no threads or conflicts remain.
argument-hint: [pr-number-or-url]
---

# Babysit PRs

Self-looping skill that babysits a PR until it is ready to merge. Each
pass keeps CI green, the branch current with its base, and review
discussions triaged. Acts autonomously on clear cases; defers anything
that needs human judgement. Delegates the heavy lifting to existing
skills (`/fix-ci`, `/fix-migrations`, `/resolve-conflicts`).

Distinct from `pr-shepherd`: this skill is generic (no qa-swarm /
stamphog machinery), self-loops on its own rather than running one
iteration per invocation, and orchestrates the other skills instead of
inlining their logic.

## Done state — terminate the loop

Stop and report when **all** of:

- CI is green, or the only red checks are known-flaky (see Step 4).
- No open **actionable** review threads remain (ambiguous ones are
  deferred, not blocking).
- The branch is conflict-free and current with its base.

Also terminate immediately if the PR is `MERGED` or `CLOSED`, if a
conflict needs a human decision, or if the user interrupts.

## Comment header — REQUIRED on every posted comment

Every comment this skill posts to GitHub (thread replies, pushback,
status) must begin with this header so a human can tell it was
automated:

```markdown
> 🤖 Automated comment written by Arthur robots
```

Put it as the first line of the body, before anything else. No
exceptions — including for pushback and short replies.

## Narration — keep the user in the loop

Skills run silently unless text is printed between tool calls. Before
each step, emit a terse one-line narration. A silent 30+ second gap is
the failure mode — err toward more lines.

Format: `[babysit] <step> — <what and why>`

```
[babysit] step 1 — resolving PR via gh pr view, base=master draft=false stacked=yes
[babysit] step 2 — branch BEHIND, restacking onto refreshed master via graphite
[babysit] step 3 — 3 unresolved threads: 1 bot-actionable, 1 nit, 1 ambiguous
[babysit] step 4 — check "Backend tests" red; also red on recent master → flaky, not gating
[babysit] step 5 — pushing fix via graphite (stacked branch)
[babysit] done — CI green, 0 actionable threads, branch current → merge-ready
```

## Workflow — one pass

### Step 1: Resolve PR and capture baseline

If `$ARGUMENTS` is a PR number or URL, use it. Otherwise:

```bash
gh pr view --json number,headRefName,baseRefName,url,headRefOid,state,isDraft,mergeable,mergeStateStatus
gh repo view --json owner,name
```

Record: PR number, owner/repo, **base branch (from `baseRefName` — never
hardcode `master`)**, HEAD SHA, state, `isDraft`.

**Detect graphite-stack membership now** and remember it for the whole
loop — it decides how every push happens (Step 5):

```bash
gt log short 2>/dev/null   # or `gt ls`; if gt is missing, install it (see Dependencies)
```

The branch is "stacked" if `gt` tracks it with a parent other than the
trunk, or with children. When in doubt, treat it as stacked and use
graphite for pushes — a wrong plain `git push` detaches the stack and is
painful to recover.

If PR state is `MERGED` or `CLOSED` → **terminate** with a final
summary.

If no PR exists for the current branch, ask the user (via
`AskUserQuestion`) whether to supply a PR number/URL, open one with
`gh pr create`, or cancel. Only proceed once they choose.

### Step 2: Keep the branch current with its base

From the Step 1 JSON, if `mergeable == "CONFLICTING"` or
`mergeStateStatus` in {`DIRTY`, `BEHIND`}:

1. Fast-forward the local base branch (`git fetch origin <base>` +
   `git branch -f <base> origin/<base>`), then restack/rebase the PR
   branch onto it — **graphite when stacked**, plain rebase otherwise.
2. On conflicts, route by type:
   - **Django migration conflicts** → invoke `/fix-migrations`.
   - **Any other conflict** → invoke `/resolve-conflicts`.
   - If either skill reports a conflict that **needs a human decision**
     (both sides changed the same logical lines with different intent,
     competing fixes, refactor-boundary collisions) → abort the restack
     cleanly, surface the file list with a one-line reason each, and
     **terminate**. Do not guess.
3. On success the HEAD SHA changes — carry the new SHA into the
   remaining steps.

### Step 3: Triage review threads

**Hard rule — read thread state via GraphQL, never REST.** The REST
`pulls/{n}/comments` endpoint does **not** expose `isResolved`, so
triaging off it re-opens already-resolved threads and posts noise.
Always use the GraphQL `reviewThreads` query and skip
`isResolved == true` and `isOutdated == true` threads as out of scope.

```bash
gh api graphql -f query='
  query($owner:String!, $repo:String!, $num:Int!) {
    repository(owner:$owner, name:$repo) {
      pullRequest(number:$num) {
        reviewThreads(first:100) {
          nodes {
            id
            isResolved
            isOutdated
            comments(first:20) {
              nodes { databaseId author { login __typename } body path line }
            }
          }
        }
      }
    }
  }' -F owner=<owner> -F repo=<repo> -F num=<pr_number>
```

For each thread with `isResolved=false` and `isOutdated=false`, classify
by the first comment's author:

- **Bot author** (`author.__typename == "Bot"` or `login` ends with
  `[bot]`):
  - **Actionable & clear** (severity high, concrete localized single-file
    fix, no new design decisions) → apply the edit, push (Step 5),
    reply with the fix SHA, resolve the thread.
  - **Disagree / not applicable** → reply with a one-line pushback
    reason ("intentional — …" / "out of scope — …" / "disagree — …")
    and resolve.
  - **Ambiguous** (architectural, broad scope, needs a decision) →
    leave unresolved, add to the deferred list, surface in the summary.
    Never terminate on it.
- **PR author, when the PR is a draft** (`isDraft == true`): treat the
  comment as a directive to update the code. Apply it, push, reply with
  the SHA, resolve.
- **PR author on a non-draft PR**: leave for the human — do not act.

Replies + resolves use the header from above. Reply then resolve:

```bash
gh api graphql -f query='mutation($t:ID!,$b:String!){addPullRequestReviewThreadReply(input:{pullRequestReviewThreadId:$t,body:$b}){comment{id}}}' -F t=<id> -F b=<body>
gh api graphql -f query='mutation($t:ID!){resolveReviewThread(input:{threadId:$t}){thread{id}}}' -F t=<id>
```

### Step 4: Check CI, fix genuine failures, ignore flake

```bash
gh pr checks <pr_number> --json name,state,bucket,link
```

For each `bucket == "fail"` check, decide flaky vs genuine before
acting:

- **Flaky** — the same check is also failing on recent base-branch
  history. Confirm cheaply:
  ```bash
  gh run list --branch <base> --workflow "<check>" -L 10 --json conclusion,headSha
  ```
  If it's red on recent base commits too, treat as flaky: note it, do
  **not** gate the done-state on it, and if a fix PR is obvious link it
  — but do not dig.
- **Genuine** — failing on this PR but green on base. Invoke `/fix-ci`,
  then push (Step 5). If `/fix-ci` cannot resolve it, add to the
  deferred list and surface it; do not loop on it.

### Step 5: Push

- **Stacked branch** → push via graphite (`gt submit --no-interactive
  --no-edit --publish`, or the Graphite MCP). Never plain `git push` on
  a stacked branch.
- **Not stacked** → `git push`.

If `gt submit` refuses with "trunk branch is out of date", sync/restack
trunk first then retry once; if only the current head ref moved, fall
back to `git push origin <branch>`. Don't loop on `gt submit` retries.

### Step 6: Loop or terminate

Re-evaluate the done-state:

- **Met** → print the final summary and **terminate**.
- **Not met** (CI still pending, deferred items the user must handle, or
  more autonomous work expected on the next pass) → schedule the next
  pass with `ScheduleWakeup` and stop this turn. Pick the delay by what
  you're waiting on: ~120–270s while polling pending CI (keeps the cache
  warm), longer if idle. Do not busy-wait inline.

When the only thing left is deferred (ambiguous threads, a `/fix-ci`
failure, a needs-decision conflict), terminate — there is nothing
autonomous left to do, and the human decides.

## Summary format

End-of-pass / final summary, one line plus detail:

```
[babysit] pass done — sha=<short> ci=<pass=N pending=N fail=N> threads=<resolved=N deferred=N> branch=<current|restacked|conflict> → <merge-ready|looping|deferred-to-user>
```

If anything is deferred, list each item (file:line or check name) with a
one-line reason underneath.

## Defers to the user

- Ambiguous review threads (architectural / broad / needs a decision).
- Merge or rebase conflicts that need a human decision.
- Genuine CI failures `/fix-ci` cannot resolve.

## Dependencies

- `gh` CLI (repo, pr, api, run, checks).
- Skills: `/fix-ci`, `/fix-migrations`, `/resolve-conflicts`.
- Graphite CLI (`gt`) for stacked branches. If missing, install it
  (`brew install withgraphite/tap/graphite` or `npm i -g @withgraphite/graphite-cli`)
  — this is acceptable to do autonomously.
- `ScheduleWakeup` for pacing the loop between passes.

## Graceful degradation

- **A delegated skill is missing** → warn and continue with the
  remaining steps; the loop still provides value.
- **No PR detected** → prompt the user (Step 1). Only stop if they
  cancel.
- **User interrupts mid-pass** → stop at the next natural checkpoint and
  print the summary.
