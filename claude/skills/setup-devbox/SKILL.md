---
name: setup-devbox
description: Use when you need a working PostHog environment on a devbox for a branch — "spin up a devbox for this branch", "provision a PostHog devbox with demo data", "get a working PostHog environment on a branch", "seed a devbox and sync flags", or any task that needs a running app stack with the Hedgebox demo org, seeded product accounts, and feature flags enabled before doing further work.
argument-hint: [branch-or-pr] [name]
---

# Set up a PostHog devbox

Provisions a devbox for a branch and leaves you with a running PostHog app stack: demo data seeded, product accounts seeded, feature flags synced and enabled, backend restarted so it all reflects your branch. Standalone — run it on its own to get a working environment, or invoke it from another skill (e.g. `qa-devbox`) as the provisioning step.

**Stop-and-ask rule:** if provisioning keeps failing in a way that suggests the box or branch is fundamentally wrong (unwinnable prebuild pollution, missing branch, repeated migration corruption) — stop and tell the user what you found rather than burning hours.

## Phase 0 — Resolve branch & box

1. Resolve the working branch (argument, or current `git branch --show-current`).
2. Derive the box label `<label>` — argument, or a slug from the branch name. (A caller may pass an explicit name, e.g. `qa-<slug>`.)
3. Check the branch exists on `origin` (`git ls-remote --heads origin <branch>`). The devbox checks out from origin. If it isn't pushed: ask the user whether to push it, or fall back to `hogli devbox:sync` mirroring (mutagen — seconds per change, no pushes; box must have the same branch checked out).

## Phase 1 — Provision (milestone: BOX UP)

```bash
hogli devbox:start -n <label> --start-app    # run in background, takes minutes
```

When it's up, put the branch on it (the AMI ships `~/posthog` on master):

```bash
hogli devbox:exec -n <label> -- bash -lc 'cd ~/posthog && git fetch origin <branch> && git checkout <branch>'
```

If the branch changes lockfiles or migrations, also run (always under flox — bare `node`/`npx`/`pnpm` are not on the login-shell PATH):

```bash
hogli devbox:exec -n <label> -- bash -lc 'cd ~/posthog && flox activate -- bash -c "pnpm install --frozen-lockfile"'
hogli devbox:exec -n <label> -- bash -lc 'cd ~/posthog && flox activate -- bash -c "python manage.py migrate"'
```

**Box-up milestone.** At this point the box is running and the branch is checked out. A caller that has other slow setup to do (e.g. installing a browser rig) can start it now, in parallel with Phase 2 below — Phase 2's `generate_demo_data` is one of the slowest steps in the run, so overlap anything you can with it.

## Phase 2 — App stack + data

> **Run management commands with the app env sourced**, or they default to `CLICKHOUSE_DATABASE=default` and fail with `Unknown table 'person'` on anything touching ClickHouse (incl. `generate_demo_data`). Canonical form on the box:
> `flox activate -- bash -c "set -a; source .env.services 2>/dev/null; set +a; .flox/cache/venv/bin/python manage.py <cmd>"`
> The Django interpreter is the flox venv at `.flox/cache/venv/bin/python` (a bare `python` may not be on PATH; `python3` is the system one, without Django). For multi-step setup, orchestrate via Python `call_command` to avoid shell-quoting hell. Many seed commands also need `--team-id` (discover the seeded team first) and depend on `generate_demo_data` having completed (groups/persons).

1. Stack up (skip if `--start-app` already did it): `hogli devbox:exec -n <label> -- bash -lc 'cd ~/posthog && hogli up -d && hogli wait'`
2. Demo data: run `generate_demo_data` (env-sourced form above) → creates the Hedgebox org with login **test@posthog.com / 12345678**. This populates **Postgres** (org, project, feature flags) and *then* backfills events into **ClickHouse** asynchronously.
3. **Don't wait for ClickHouse.** The seed and flag-sync commands only need the Postgres objects — fire them in **parallel** as soon as `generate_demo_data` returns; the CH event backfill keeps running in the background. Gate *only* CH-dependent work (event-based insights, counts) on the backfill settling.
   - **Seed accounts**: discover the command with `ls products/<product>/backend/management/commands/`, check `--help`, then run (env-sourced form above). For the `--team-id` these commands usually need, discover the seeded team first — `generate_demo_data` creates one project under the Hedgebox org: `hogli devbox:exec -n <label> -- bash -lc 'psql -h localhost -U posthog posthog -c "SELECT id, name FROM posthog_team ORDER BY id;"' 2>/dev/null` (the Hedgebox/Hogflix team is the one with a real project). Example (customer analytics): `seed_customer_analytics_accounts --team-id <team>`.
   - **Sync feature flags**: `flox activate -- bash -c "python manage.py sync_feature_flags"` — adds and enables every flag from `frontend/src/lib/constants.tsx` across all projects, so the feature you care about is actually on.

If either step hits a **DB error** (`relation ... does not exist`, `column ... does not exist`, `InconsistentMigrationHistory`), the box's schema is behind the branch — run migrations and retry:

```bash
hogli devbox:exec -n <label> -- bash -lc 'cd ~/posthog && flox activate -- bash -c "set -a; source .env.services 2>/dev/null; set +a; .flox/cache/venv/bin/python manage.py migrate"'
```

**`Unknown table 'person'` (or other unknown-CH-table errors) is NOT a broken ClickHouse** — it means the command ran without `.env.services`, so `CLICKHOUSE_DATABASE` defaulted to `default` instead of `posthog`. Re-run with the env sourced (above) and confirm tables exist in the `posthog` CH DB (`system.tables`) before reaching for `migrate_clickhouse` or recreating the box.

## Phase 3 — Restart backend & verify

1. **Restart the backend** so freshly-synced flags and seeded data are actually live. A flag created or flipped *after* the web process started never reaches the server-rendered bootstrap until the worker reloads — `touch posthog/urls.py` triggers granian autoreload to re-read flag definitions. If the flags service itself is stale (briefly 401s with "API key invalid or expired" while HyperCache hydrates), restart `feature-flags`/`hypercache-server`.
2. **App-is-your-branch check.** Confirm the running app actually serves your checkout, not a stale prebuild build: load a branch-unique route/element and confirm it renders (the DEBUG-banner git rev can be a stale cached value, so don't trust it alone). If it doesn't match your branch, fix it now — see the polluted-warm-prebuild gotcha.
3. App smoke test: `http://localhost:8010` loads (the box's localhost). **Always `localhost:8010`** (dev proxy); never `172.17.0.1:8000` (granian direct → CSRF 403 on `/flags`, no feature flags).

The box now serves your branch with demo data, seeded accounts, and flags enabled, logged-in-ready as **test@posthog.com / 12345678**.

## Gotchas (hard-won — read before debugging)

- **flox everything**: on the box, `node`/`npx`/`python`/`pnpm` exist only inside `flox activate -- bash -c "..."`. A "command not found" or a process that silently fails to spawn is almost always this.
- **`devbox:exec` needs `bash -lc '...'`** and the Coder banner pollutes output — suppress with `2>/dev/null` on the local side; the real output comes last.
- **Env-sourcing / `CLICKHOUSE_DATABASE`**: management commands touching ClickHouse must source `.env.services` (Phase 2 callout) or they hit the `default` CH DB.
- **`Unknown table 'person'`** = env not sourced, not a broken ClickHouse (Phase 2).
- **DB error → migrate** (Phase 2): `relation/column does not exist` or `InconsistentMigrationHistory` means the box schema is behind the branch.
- **App URL on the box is `localhost:8010`**, login `test@posthog.com / 12345678` (Hedgebox is the only seeded org with a real project).
- **Polluted warm prebuild (serves the wrong branch).** A warm box can be snapshotted from another box that was *running* a different branch's app, so it serves that stale frontend (and reports its git rev in the DEBUG banner) even after `git checkout`. This survives `hogli down/up`, Vite/turbo cache clears, and browser cache clears. If the app won't reflect your branch after a clean rebuild, the prebuild is unwinnable in place — destroy and reprovision (or use a different pool / local `bin/start`). Don't sink hours clearing caches. (See the Phase 3 app-is-your-branch check — catch this early.)
- **Stale in-process flag cache (flag enabled everywhere but the gated UI still won't render).** In `SELF_CAPTURE` dev the web process loads its **own** flag definitions once at startup; a flag created/flipped after the app started never reaches the server-rendered bootstrap. Fix: enable the flag in PG (active + 100% rollout), then reload the web worker (`touch posthog/urls.py`), then a fresh full page load — not client-side `override`/`reloadFeatureFlags`, the staleness is server-side (Phase 3).
- **Never `pkill -f`/`pgrep -f` with a pattern that appears in your own command line** through `devbox:exec` — it kills your own SSH session (exit 255). Verify daemons with `ss -tln`/`curl`, build patterns from shell variables, and prefer killing by PID from `ss -tlnp`.
- **Daemons die with the box** (stop/restart): the app stack must be re-upped. The repo, installed packages, and any persistent browser profile survive on disk.
- **Stop the box when done** (it bills while running): `hogli devbox:stop -n <label>` (disk persists).
