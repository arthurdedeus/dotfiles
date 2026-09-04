---
name: devbox-feature-branch
description: Prepare a clean integration branch on a PostHog devbox from several topic branches, then start and verify the remote dev stack. Use when combining branches in a Coder devbox, creating an integration or feature branch from latest master, cherry-picking branch changes, checking whether source branches contain migrations, or diagnosing a devbox stack that is not ready after branch setup.
argument-hint: "[devbox-host] [target-branch] [source-branch...]"
---

# Prepare a devbox integration branch

Use this workflow to combine reviewed topic branches on a clean devbox branch and make the app usable. Read `setting-up-devbox` first when SSH access or the workspace state is unknown.

Do not change a dirty worktree without the user's direction. Preserve it in a named stash before switching branches.

## 1. Establish reusable SSH access

Use an SSH control socket so each command reuses one connection.

```bash
host=dev.<name>.<user>.coder
socket="$HOME/.ssh/cm-dev-<name>"

mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"

if ! [ -S "$socket" ] || ! ssh -S "$socket" -O check "$host" >/dev/null 2>&1; then
  rm -f "$socket"
  ssh -M -S "$socket" -o ControlPersist=yes -fN "$host"
fi

ssh -S "$socket" -O check "$host"
```

A stopped Coder workspace can start when SSH first connects. If the first connection times out during its banner exchange, wait for startup and retry. Verify the checkout before editing it:

```bash
ssh -S "$socket" "$host" 'cd ~/posthog && pwd && git status --short --branch'
```

The persistent connection does not preserve a working directory. Include `cd ~/posthog` in every remote command.

## 2. Create the target branch from current master

Check for uncommitted files and an existing target branch first. If the worktree is dirty, stash tracked and untracked files. Name the stash after the target branch.

```bash
ssh -S "$socket" "$host" 'bash -s' <<'REMOTE'
set -e
cd ~/posthog
target_branch=feat/example

if git show-ref --verify --quiet "refs/heads/$target_branch"; then
  echo "Target branch already exists: $target_branch" >&2
  exit 1
fi

git status --short --branch
git stash push --include-untracked -m "pre-${target_branch} worktree"
git fetch origin master
git switch master
git pull --ff-only origin master
git switch -c "$target_branch"
git status --short --branch
REMOTE
```

Do not apply the stash to the integration branch. It belongs to the source worktree unless the user asks to restore it.

## 3. Inspect source branches before integration

Fetch each source ref explicitly. Then list commits and migration files relative to the target base.

```bash
for branch in "${source_branches[@]}"; do
  git fetch origin "refs/heads/$branch:refs/remotes/origin/$branch"
  echo "=== $branch commits ==="
  git log --reverse --oneline master.."origin/$branch"
  echo "=== $branch migrations ==="
  git diff --name-only master..."origin/$branch" -- \
    '*/migrations/*' 'migrations/*' '*.sql' || true
done
```

If a branch changes a Django or ClickHouse migration, read the matching migration skill before integrating it. Confirm every branch has a sensible commit list. A branch with no commits beyond master needs no action.

Choose a dependency-aware order. Cherry-pick foundational API or query changes before dependent UI changes. Keep generated-type follow-up commits after the code that changes the OpenAPI schema.

## 4. Cherry-pick the commits

Cherry-pick complete commit sequences, not only each branch tip. Keep commit signing disabled only for the remote cherry-pick command when the devbox lacks an SSH signing agent.

```bash
git -c commit.gpgsign=false cherry-pick <commit> [<commit>...]
```

After each source branch, check the worktree and log:

```bash
git status --short --branch
git log --oneline -5
```

If a conflict occurs, inspect both changes and resolve the behavior deliberately. Continue with `git -c commit.gpgsign=false cherry-pick --continue`. Abort with `git cherry-pick --abort` if the source intent cannot be established.

Do not set `commit.gpgsign=false` globally. The devbox may not have a forwarded signing agent, while the local checkout does.

## 5. Start and verify the stack under Flox

The devbox's non-login SSH environment can lack `pnpm` and `sqlx`. Start PostHog through Flox. If a previous detached stack started outside Flox, stop it before restarting.

```bash
cd ~/posthog
flox activate -- bash -c './bin/hogli down -y'
flox activate -- bash -c './bin/hogli up -d -y'
flox activate -- bash -c './bin/hogli services:ready -y && ./bin/hogli wait -y'
```

Check the app and process runner after `hogli wait` succeeds:

```bash
curl -sS -o /dev/null -w '%{http_code}\n' http://localhost:8010/_health
curl -sS -o /dev/null -w '%{http_code}\n' http://localhost:8010/
curl -sS http://localhost:8010/api/projects/@current
phrocs wait --json --timeout 1
```

Success means all required processes are ready, `/_health` returns `200`, `/` returns `200` or `302`, and the unauthenticated API reports `not_authenticated`.

If `pnpm` or `sqlx` is missing, the stack started outside Flox. Restart it under Flox. If migrations fail, read their logs in `.posthog/.generated/logs/` and fix the named failure before calling the stack healthy.

## Report

State the devbox host, target branch, source branches integrated, preserved stash, whether commit signing was unavailable, and health-check results. Do not push or open a pull request unless the user asks.
