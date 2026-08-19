---
name: setup-devbox
description: Provision one focused PostHog devbox for a branch with only the services, flags, and seed data required by its test criteria.
argument-hint: "[branch-or-pr] [name]"
---

# Set up a focused PostHog devbox

Treat each devbox as one feature test environment. Do not build an all-purpose box.

Read the repository's `.agents/skills/setting-up-devbox/SKILL.md` first. Use `bin/hogli devbox:*` as the supported control interface.

## 1. Define the test needs

Before starting the box, list:

- Feature and acceptance criteria.
- UI routes and APIs under test.
- Required databases and background jobs.
- Required feature flags.
- Smallest useful fixture set.

Every service and fixture must support one criterion. Remove anything without a named use.

## 2. Resolve the target

1. Resolve the branch or pull request.
2. Derive a short feature-specific box label.
3. Detect the repository base branch.
4. Check whether the branch exists on `origin`.
5. If it does not exist, ask before pushing.
6. Run `bin/hogli devbox:doctor` before changing authentication or network settings.

An expired Coder session needs user authentication. Do not loop on authentication failures.

## 3. Start without the default app profile

Start or create the box without launching every configured process:

```bash
bin/hogli devbox:start -n <label> --no-start-app
```

Check out the target branch:

```bash
bin/hogli devbox:exec -n <label> -- bash -lc 'cd ~/posthog && git fetch origin <branch> && git checkout <branch>'
```

Install changed dependencies and run required migrations before starting the app.

Do not fake migrations to bypass unexplained schema drift.

## 4. Select only required services

Use the repository's intent tooling on the box:

```bash
bin/hogli dev:intents
bin/hogli dev:explain <intent>
bin/hogli dev:apply <intent> [--include <unit>] [--exclude <unit>] [--skip-autostart <unit>]
```

Choose the closest intent, then remove units that no acceptance criterion needs. Inspect the generated plan before startup.

For a basic customer analytics account or settings test, keep the web app, required databases, migrations, feature flags, and HyperCache. Do not add ingestion, Temporal, LLM, or integration services by default.

Add services only when the criterion needs them:

| Feature under test | Additional capability |
| --- | --- |
| Dashboard metrics, activity, or usage | ClickHouse data and completed ClickHouse migrations |
| New captured events | Capture and ingestion pipeline |
| Calendar, workflows, scheduled jobs | Matching Temporal or worker processes |
| Max or AI behavior | LLM gateway and its approved test key |
| External integration | Only that integration's worker, fixture, and tunnel |

Start the selected profile detached:

```bash
bin/hogli up -d -y
bin/hogli services:ready -y
```

Check readiness for `backend`, `frontend`, `feature-flags`, `hypercache-server`, and each criterion-specific unit. Do not chase unrelated stopped units.

## 5. Run Django commands safely

Use Flox and `.env.services`:

```bash
flox activate -- bash -c 'set -a; source .env.services 2>/dev/null; set +a; .flox/cache/venv/bin/python manage.py <command>'
```

`Unknown table 'person'` usually means `.env.services` was not loaded. Confirm the target ClickHouse database before changing schema state.

## 6. Seed only required data

Reuse a suitable test project when one exists.

The default `generate_demo_data` dataset with 500 clusters is acceptable. Use it when creating the standard Hedgebox project.

Do not generate more data unless the acceptance criteria need more groups than the database contains. In that case, rerun `generate_demo_data` with a larger `--n-clusters` value.

Wait for ClickHouse backfill only when a criterion reads event data.

## 7. Seed customer analytics accounts

Customer analytics accounts come from group analytics at group type index `0`.

1. Confirm the target team ID.
2. Count index-0 groups in the persons database:

Set `team_id` to the target team before running this through `manage.py shell`:

```python
from posthog.persons_db import persons_db_connection

team_id = 1

with persons_db_connection(writer=False) as connection, connection.cursor() as cursor:
    cursor.execute(
        "SELECT count(*) FROM posthog_group WHERE team_id = %s AND group_type_index = 0",
        [team_id],
    )
    print(cursor.fetchone()[0])
```

Use the environment from section 5.

3. If the count is too small, generate demo data with a larger `--n-clusters` value and count again.
4. Run the account seed once the database contains enough groups:

```bash
python manage.py seed_customer_analytics_accounts \
  --team-id <team-id> \
  --limit <accounts-needed> \
  --users <role-users-needed> \
  --accounts-with-notes <accounts-needing-notes> \
  --notes-per-account <notes-needed>
```

The command:

- Creates accounts from index-0 groups.
- Sets `account_group_type_index = 0`.
- Creates only the requested role-user pool.
- Adds notes only to the requested accounts.
- Is safe to rerun.

Use zero for users or notes when the criterion does not need them. Use `--limit` instead of converting every demo group.

The command does not create support tickets, email threads, calendar meetings, workflows, or external integration data. Seed one invented fixture through that feature's real write path only when its criterion needs it.

## 8. Configure customer analytics flags

Run:

```bash
python manage.py sync_feature_flags
```

Do not substitute `sync_feature_flags_from_api`. It does not create the local `customer-analytics-roadmap` gate.

Always enable `customer-analytics-roadmap` for customer analytics tests. Enable only the optional gate needed by the feature:

- `customer-analytics-csp` for accounts, account tabs, feed, announcements, and account settings.
- `customer-analytics-feature-requests` for feature requests.
- `customer-analytics-journeys` for journeys.
- `customer-profile-config-button` only when testing that control.

Inspect `frontend/src/lib/constants.tsx` and the feature route before choosing flags. Disable unrelated customer analytics gates on the fresh box so hidden features do not affect the scenario.

## 9. Refresh flag caches

After changing flags, restart these processes in order:

1. `hypercache-server`.
2. `feature-flags`.
3. `backend`.

Use the available phrocs status and toggle tools. For each process:

1. Read its current state.
2. Stop it if running.
3. Confirm it stopped.
4. Start it.
5. Wait for its readiness signal.

Restart only these processes. Do not restart the full stack.

Then hard-refresh the browser. Verify each required flag through the page's feature-flag client or `/flags` response before testing the route.

## 10. Verify the focused environment

1. Open `http://localhost:8010` from the box.
2. Confirm a branch-specific route or element.
3. Log in with the seeded test account.
4. Verify exact fixture counts.
5. Verify required flags are true and unrelated optional gates are false.
6. Verify only required processes are running.

If the box serves a stale prebuild after one clean restart, stop and reprovision. Do not spend repeated cycles clearing caches.

## 11. Return the environment

Report:

- Box label, workspace, branch, and revision.
- Acceptance criteria supported by the setup.
- Running services and why each is needed.
- Seed commands and resulting counts.
- Enabled and disabled customer analytics flags.
- App URL and login.
- Stop command: `bin/hogli devbox:stop -n <label>`.

Do not stop the box without asking when the user may still need it.
