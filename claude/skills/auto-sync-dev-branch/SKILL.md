---
name: auto-sync-dev-branch
description: Keep a checked-out branch synced with its remote and auto-restart the local PostHog stack (frontend/backend + migrations) when new commits land. Use for "keep pulling and restart on changes" or babysitting a branch an agent pushes to.
---

# auto-sync-dev-branch

## Overview

Poll the current branch's remote on a cadence, fast-forward when new commits land, and bring the running dev stack up to date: restart `frontend` and `backend`, and re-run Postgres/ClickHouse migrations when migration files changed.

- **Pull**: `flox activate -- bash -c "git pull --ff-only"`
- **Restart / migrate**: the **phrocs** MCP (`mcp__phrocs__get_process_status`, `mcp__phrocs__toggle_process`, `mcp__phrocs__get_process_logs`). `toggle_process` stops a running process and starts a stopped one — call it twice to restart.

The loop self-paces: each run does **one** cycle, then schedules the next with `ScheduleWakeup`.

## When to use

- "Keep pulling `<branch>` every few minutes and restart the app when it changes."
- Watching a branch an agent or teammate keeps pushing to while you have the stack running locally.

**Not for:** branches with local commits you haven't pushed (a `--ff-only` pull will refuse — see Edge cases), or when the dev stack isn't running locally.

## Start it

Launch under `/loop` so the skill can self-pace:

```
/loop /auto-sync-dev-branch
```

One invocation = one cycle. The skill self-schedules ~5 min out via `ScheduleWakeup`, so it keeps running hands-off until you interrupt or it hits a fatal condition.

## Process names (phrocs)

| Job | Process |
|-----|---------|
| Backend (Django) | `backend` — ready when logs show `Listening at` |
| Frontend (Vite) | `frontend` — ready when logs show `VITE ... ready` |
| Postgres migrations | `migrate-postgres` — done when logs show `All migrations completed successfully` |
| ClickHouse migrations | `migrate-clickhouse` — same completion line |

`migrate-*` processes run once and exit, so they normally sit **stopped** between runs.

## One cycle

1. **Guard.** Confirm an upstream exists: `git rev-parse --abbrev-ref --symbolic-full-name @{u}`. If it fails (detached HEAD / no tracking branch), report and **stop** — do not reschedule.
2. **Record HEAD:** `before=$(git rev-parse HEAD)`.
3. **Pull:** `flox activate -- bash -c "git pull --ff-only"`. If it exits non-zero, report the output and **stop** (needs a human — diverged history, local commits, or conflicts). Do not force.
4. **Record HEAD again:** `after=$(git rev-parse HEAD)`.
5. **No change?** If `before == after`, nothing landed → go to step 9 (reschedule) and finish.
6. **Diff & detect migrations** between the two revisions:
   ```bash
   changed=$(git diff --name-only "$before" "$after")
   ch_migrations=$(echo "$changed" | grep -E '^posthog/clickhouse/migrations/[^/]+\.py$' || true)
   pg_migrations=$(echo "$changed" | grep -E '/migrations/[^/]+\.py$' \
       | grep -v '^posthog/clickhouse/migrations/' | grep -v '^rust/' || true)
   ```
7. **Bring the stack up to date** (via phrocs — see "Restarting a process" below). If `get_process_status` reports phrocs isn't running, warn that there's nothing to restart and skip to step 9.
   - **If `pg_migrations` is non-empty:** run `migrate-postgres`, then wait for `All migrations completed successfully`.
   - **If `ch_migrations` is non-empty:** run `migrate-clickhouse`, then wait for completion.
   - Always run migrations **before** restarting `backend`, so the backend boots against the new schema.
8. **Restart** `backend`, then `frontend` (restart both on every code change, migrations or not). Wait for each to report ready before moving on.
9. **Report** what happened — commits pulled (`git log --oneline "$before".."$after"`), migrations run, processes restarted.
10. **Reschedule:** call `ScheduleWakeup` with `delaySeconds: 270` (≈5 min, kept just under the 300s prompt-cache window), `prompt: "/auto-sync-dev-branch"`, and a one-line `reason`. Omit this only on the fatal stops in steps 1 and 3.

## Restarting a process

`toggle_process` is stateful (stop↔start), so check first:

- **Restart a running process** (`backend`, `frontend`): `toggle_process(name)` to stop → confirm stopped via `get_process_status` → `toggle_process(name)` to start.
- **Run a stopped migrate process**: a single `toggle_process(name)` starts it. (If `get_process_status` shows it somehow still running, stop-then-start instead.)

**Wait for ready** by polling `get_process_status` for `running && ready`, or `get_process_logs` for the ready/completion line from the table above. Cap the wait (~120s); if it doesn't come up, surface the last ~50 log lines and still reschedule so a transient failure self-heals next cycle.

## Edge cases

| Situation | Do this |
|-----------|---------|
| `--ff-only` pull fails (diverged / local commits / conflict) | Report, **stop the loop** (don't reschedule). Needs a human. |
| Detached HEAD / no upstream | Report, **stop**. |
| phrocs not running ("Start the dev environment with: ./bin/start") | Warn, skip restarts, **still reschedule** — the env may come up later. |
| Process won't reach ready within timeout | Surface recent logs, **reschedule** (likely transient). |
| Commits pulled but no code/migration files changed (e.g. only docs) | Restarting is harmless; the skill restarts `backend`/`frontend` on any new commit. |

## Common mistakes

- **Force-pulling.** Never `git pull` without `--ff-only` here, and never `--force`. A non-ff branch means someone rewrote history or you have unpushed work — stop and let the human decide.
- **Restarting backend before migrations finish.** Run migrations and wait for the completion line first, or the backend boots against a stale schema.
- **Toggling blindly.** `toggle_process` flips state. Always read `get_process_status` first so you know whether a toggle starts or stops it.
- **Picking `delaySeconds: 300`.** Use `270` — it stays inside the prompt-cache window so the next wake is cheap, and "every 5 minutes" doesn't need to be exact.
