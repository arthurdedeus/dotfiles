---
name: qa-devbox
description: Run acceptance tests for a branch on a fresh PostHog devbox and collect browser, API, and database evidence.
argument-hint: "[branch-or-pr] [context]"
---

# QA on a devbox

Test explicit acceptance criteria against the target branch. Fix clear defects only within the requested scope.

## 1. Define the test contract

Read the pull request, linked issue, branch diff, and repository instructions.

Write numbered criteria. Each criterion needs:

- An ID.
- A user-visible or system outcome.
- Setup and exact steps.
- An observable expected result.
- A proof type.

Cover the happy path, the main edge case, permissions when relevant, and one adjacent regression risk.

If product intent is ambiguous, ask before provisioning. Otherwise show the criteria and continue.

## 2. Provision in parallel

Start independent setup work concurrently when the harness supports it:

- Use `setup-devbox` for the branch, app, seed data, and feature flags.
- Prepare the browser rig from `references/devbox-browser-rig.md`.
- Prepare API or database checks that do not need the browser.

Give the user the noVNC watch URL as soon as it works.

## 3. Verify the environment

Before testing:

1. Confirm the browser MCP handshake.
2. Load `http://localhost:8010` from the box.
3. Confirm the app serves the target branch.
4. Confirm the seeded user identity.
5. Confirm required feature flags and fixtures.

Do not test a stale build or the wrong seeded user.

## 4. Run each criterion

Run browser scenarios one at a time. API, database, and log checks may run in parallel.

For each criterion:

1. Capture the starting state.
2. Perform the documented steps.
3. Assert each expected result.
4. Capture the requested proof.
5. Record PASS, FAIL, or BLOCKED.

A successful click or request is not proof. Verify the resulting UI, response, or database state.

Use `references/proofs.md` for evidence formats and redaction.

## 5. Handle failures

For a failure:

1. Save the failure state and decisive logs.
2. Identify the first causal error.
3. Fix only a clear in-scope defect.
4. Mirror the local change with `bin/hogli devbox:sync` when appropriate.
5. Rerun the failed criterion and affected regression criteria.

Stop and ask when a fix changes product intent, data design, permissions, or scope.

Do not commit or push unless the user or calling workflow authorized it.

## 6. Finalize proof

Make the tested Git state explicit. If proof covers uncommitted changes, say so or recapture after the authorized commit.

Collect artifacts under `~/Downloads/qa-proofs/<branch>/` or upload them when an artifact tool exists.

Before changing a pull request or issue, show the proof block unless the user already approved posting.

Use `bin/hogli pr:upload-image <file>` only for public-safe images. Never upload customer data, secrets, or internal information.

## 7. Report

Return:

- Criteria with PASS, FAIL, or BLOCKED.
- Evidence for each criterion.
- Fixes and tested revision.
- Untested areas.
- Watch URL, box name, and running services.
- The box stop command.

Ask before stopping the box.
