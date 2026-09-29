---
name: setting-up-customer-analytics-devbox
description: Creates and seeds a new PostHog devbox for testing Customer analytics, then hands over the Coder URL of the Accounts page. Use when asked to set up, seed, or validate a Customer analytics devbox. Covers migrations, Hedgebox demo data, accounts, roles, notes, feature flags, the dev CSP, and which steps run in parallel.
---

# Setting up a Customer analytics devbox

Read `setting-up-devbox` for access and Coder basics. This skill covers the order, the parallel steps, and the known failures.

The result:

- team 1 (Hedgebox) with events, persons, and account groups at group type index `0`
- Customer analytics accounts, role assignments, and notes
- every `customer-analytics-*` flag active
- the Accounts page rendering at its Coder URL

## Checklist

```text
- [ ] 0. GH_TOKEN secret exists (before creating the box)
- [ ] 1. New box with its own label
- [ ] 2. Dev CSP fix present on the box
- [ ] 3. Migrations (two processes in parallel)
- [ ] 4. Stack up, in parallel with demo data
- [ ] 5. Accounts seed and flag sync, in parallel
- [ ] 6. Validate the data
- [ ] 7. Hand over the Coder URL
```

## Run commands on the box

A login shell on the box has no toolchain, so wrap every command in flox.
Base64 avoids quoting trouble through `devbox:exec`:

```bash
bx() {
  local b64; b64=$(printf '%s' "$1" | base64)
  hogli devbox:exec -n <label> -- bash -lc "cd ~/posthog && echo $b64 | base64 -d > /tmp/bx.sh && flox activate -- bash /tmp/bx.sh"
}
```

`devbox:exec` prints output only when the command exits.
Run any step over a few minutes as `nohup ... > ~/ca-<step>.log 2>&1 &`, then poll the log.

Personal dotfiles can print a `bootstrap.sh` /dev/tty error and a "workspace may be incomplete" warning. Ignore both.

## 0. Before creating the box

`gh` is not signed in on a new box. If `hogli devbox:secret:list` has no `GH_TOKEN`, ask the user to run `hogli devbox:secret:set GH_TOKEN`.
A secret reaches only boxes started after it is set.

## 1. Create the box

```bash
hogli devbox:start -n <label>
```

- Use a new label. Never drive a box another session uses. Check with `pgrep -af manage.py` on the box.
- The box pulls `master` on boot. Record the SHA and skip any pull.
- Docker services already run. Skip `hogli docker:services:up`.
- Skip `hogli dev:reset`. The prewarmed schema has 0 teams, so there is nothing to reset.

## 2. Make sure the dev CSP fix is on the box

In DEBUG, the enforced CSP must allow the `JS_URL` host, or the Coder page renders blank.
[PostHog#108447](https://github.com/PostHog/posthog/pull/108447) adds it.

```bash
bx 'grep -qF "\"http://localhost:8234\", bundle_origin" posthog/csp_middleware.py && echo present || echo missing'
```

If missing and the PR is still open:

```bash
bx 'git fetch -q origin fix/csp-dev-js-url && git checkout FETCH_HEAD -- posthog/csp_middleware.py'
```

If the PR has merged, the box already has the fix. Delete this step once it has.

## 3. Migrate

The prewarmed database trails `master` by hundreds of migrations. This is the slowest step.
`bin/migrate` already runs ClickHouse beside Postgres, but it runs persons after Postgres. Start persons as its own process:

```bash
bx 'nohup bin/migrate --scope=postgres --scope=clickhouse > ~/ca-migrate.log 2>&1 &
nohup bin/migrate --scope=persons > ~/ca-persons.log 2>&1 &'
```

Poll until both processes exit, then check both logs for errors.

## 4. Start the stack and generate demo data in parallel

Demo generation needs only the migrated databases.
Starting the stack at the same time warms Vite and the Rust services.
It also brings up personhog and capture, which removes the personhog traceback and the capture 502 warnings the seeds print when the stack is down.

```bash
bx 'nohup ./bin/hogli up -d -y > ~/ca-up.log 2>&1 &
nohup python manage.py generate_demo_data --seed customer-analytics-devbox --n-clusters 30 --days-past 120 --days-future 30 > ~/ca-demo.log 2>&1 &'
```

After `hogli up` returns, rerun the etcd init. `hogli up` recreates etcd while `personhog-etcd-init` runs, so the init often fails:

```bash
bx 'docker exec posthog-etcd-1 etcdctl put /personhog/config/total_partitions 4'
```

`hogli wait` may still report `crashed` for `personhog-etcd-init`. Ignore it.
Judge health by `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8010/` returning `200` or `302`.

The saved dev config starts `product_analytics` only. That is enough for the Accounts page.

Never rerun a finished `generate_demo_data` against the same team. It duplicates analytics data.
If it created team 1 and then failed, fix the cause and rerun with `--team-id 1`.

## 5. Seed accounts and sync flags in parallel

Both need only team 1 and its groups. Wait for `generate_demo_data` to finish first.

```bash
bx 'nohup python manage.py seed_customer_analytics_accounts --team-id 1 --users 5 --accounts-with-notes 5 --notes-per-account 1 > ~/ca-seed.log 2>&1 &
nohup python manage.py sync_feature_flags > ~/ca-flags.log 2>&1 &'
```

The seed is safe to rerun. It creates accounts for the group type index `0` keys, three role definitions, org-member users, role assignments, and notes.

Take the flag list from `frontend/src/lib/constants.tsx` (`customer-analytics-*` keys). Do not hardcode it.

## 6. Validate

`psql` waits forever for a password over `devbox:exec`, so always pass `PGPASSWORD`.

```bash
bx 'q() { PGPASSWORD=posthog psql -h localhost -U posthog -d "$1" -Atc "$2"; }
q posthog "select count(*) from customer_analytics_account where team_id = 1"
q posthog "select count(*) from customer_analytics_accountrelationship where team_id = 1 and ended_at is null"
q posthog "select key, active from posthog_featureflag where team_id = 1 and key like '"'"'customer-analytics-%'"'"' order by key"
q posthog_persons "select group_type_index, count(*) from posthog_group where team_id = 1 group by 1"
docker exec posthog-clickhouse-1 clickhouse-client -d posthog -q "SELECT count(), uniqExact(person_id) FROM events WHERE team_id = 1"'
```

Expect about 10 accounts, 30 active relationships, 10 groups at index `0`, and a few thousand events.

## 7. Hand over the Coder URL

Never forward ports to give the user a URL. `devbox:forward` tunnels only Django, and the page also needs Vite.
The flox shell on the box has the Coder host in `SITE_URL`:

```bash
bx 'echo "$SITE_URL/project/1/customer_analytics/accounts"'
```

The URL goes through Coder sign-in, which a Playwright browser cannot pass.
Ask the user to open it, or use Claude in Chrome with their signed-in profile.
The page must show account rows, notes, and the three relationship columns.

If the page is blank, check the enforced `Content-Security-Policy` header for the `JS_URL` host (step 2).
`JS_URL` must stay the Coder frontend host. Do not unset it or point it at `localhost`.

## Timings (new box, September 2026)

| Step | Time |
| --- | --- |
| Create the box | ~1 min |
| Migrations (sequential run) | ~14 min |
| `generate_demo_data` | ~1.5 min |
| Accounts seed | ~25 s |
| Flag sync | ~40 s |
| `hogli up` to `302` | ~1 min |
