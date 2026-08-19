---
name: auto-sync-dev-branch
description: Poll a tracked branch, fast-forward new commits, run required migrations, and restart the local PostHog stack.
---

# Auto-sync a development branch

Run one safe cycle at a time. Schedule another cycle only when the harness provides a wakeup or loop tool.

## Preconditions

- The branch has an upstream.
- The working tree is clean.
- The branch has no unpushed commits.
- The local PostHog process manager is running when restarts are required.

Stop instead of stashing, resetting, forcing, or merging.

## One cycle

1. Read the current branch, upstream, status, and `HEAD`.
2. Stop on a detached head, missing upstream, dirty tree, or local-ahead state.
3. Fetch the upstream.
4. Fast-forward only:

```bash
git merge --ff-only @{u}
```

5. If `HEAD` did not change, report no change.
6. If commits landed, list them and collect changed paths.
7. Detect Django and ClickHouse migration files from the revision range.
8. Discover the available PostHog process-manager tools. Prefer the configured `phrocs` status, toggle, and log tools.
9. If no process manager is available, report the pulled commits and the missing restart step.
10. Run Postgres migrations before the backend restart when Django migrations changed.
11. Run ClickHouse migrations when ClickHouse migrations changed.
12. Restart the backend, then the frontend.
13. Wait for each process's current readiness signal.
14. Report commits, migrations, restarts, and failures.

## Process safety

Check process state before toggling it. A toggle may stop a running process or start a stopped one.

For a restart:

1. Stop the running process.
2. Confirm it stopped.
3. Start it.
4. Wait for readiness.

Cap each readiness wait. On timeout, show recent logs and leave the process state explicit.

## Continue polling

If the harness supports scheduled wakeups, schedule the next cycle in about 270 seconds.

Do not reschedule after a safety stop. If no scheduler exists, finish the current cycle and state that continuous polling is inactive.

## Migration detection

Treat files under `posthog/clickhouse/migrations/` as ClickHouse migrations. Treat other Python files under a `migrations/` directory as Django migrations.

Do not restart the stack for documentation-only changes unless repository tooling requires it.
