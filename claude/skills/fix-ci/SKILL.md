---
name: fix-ci
description: Diagnose and fix failing checks on the current pull request.
---

# Fix CI

## 1. Capture the current failures

```bash
gh pr checks --json name,state,bucket,link
```

Work from current failures, not an earlier report.

## 2. Read the authoritative workflow

For PostHog repositories, load `.agents/skills/debugging-ci-failures/SKILL.md` when present. Read the failing workflow and its local commands.

Do not rely on remembered job names or commands.

## 3. Inspect focused logs

Extract the run or job identifier from the check link. Start with failed logs:

```bash
gh run view <run-id> --log-failed
```

Find the first causal error. Later failures may be fallout.

Classify the failure as:

- Product code or test failure.
- Type or lint failure.
- Migration conflict or safety check.
- Generated artifact drift.
- Visual Review change or unstable story.
- Infrastructure or flaky failure.

## 4. Fix the cause

Use a repository skill when one covers the failure. Examples include Django migrations, CI debugging, and Visual Review triage.

Keep the change local to the cause. Do not weaken assertions, skip checks, or update baselines without evidence.

For Kea-related type failures, run typegen before the frontend type check:

```bash
pnpm --filter=@posthog/frontend typegen:write
pnpm --filter=@posthog/frontend typescript:check
```

For Visual Review, inspect the changed story and review output. Do not edit snapshot PNGs or `frontend/snapshots.yml` by hand.

## 5. Verify

Run the smallest local command that reproduces the failing check. Then run any required broader check.

If local reproduction is impossible, push only with existing authorization and verify the rerun in CI.

## Flakes

A retry is evidence of a flake only when the same code passes without a fix. Compare recent base-branch runs when practical.

Do not declare a red required check acceptable. Rerun it or report it as unresolved.

## Publishing

A standalone invocation does not commit or push. Follow explicit user permission or the calling skill's publish rules.

Report the cause, changed files, local verification, and current CI state.
