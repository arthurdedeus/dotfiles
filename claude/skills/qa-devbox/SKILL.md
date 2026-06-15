---
name: qa-devbox
description: Use when a feature branch needs its QA phase run end-to-end on a fresh devbox — deriving acceptance criteria, provisioning a devbox for the working branch, wiring watchable browser automation (Playwright MCP over an SSH tunnel), seeding demo data, executing every criterion as a browser/API/DB scenario via subagents, fixing failures until all pass, and posting proof artifacts (screenshots, GIFs, API/SQL transcripts) to the PR or issue. Triggers: "run QA on this", "QA this branch/PR", "verify this feature on a devbox", "run the QA phase".
argument-hint: [branch-or-pr] [extra context...]
---

# QA on a devbox

Runs the QA phase of a development task end-to-end: acceptance criteria → fresh devbox with a watchable browser rig → demo data → scenario execution with fix-and-retry → proof artifacts posted to the PR/issue.

**You are the orchestrator.** Subagents do the legwork (browser driving, log watching, API/DB checks); you hold the acceptance criteria, make judgment calls, edit code, and synthesize the verdict. Subagents cannot spawn subagents — all fan-out happens at your level.

**Stop-and-ask rule (applies throughout):** if a criterion contradicts observed intended behavior, a fix requires scope or design changes, or anything stops making sense in the grand scheme of the task — stop and ask the user, presenting what you found. Don't silently reinterpret the task.

## Phase 0 — Intake

1. Resolve the working branch (argument, or current `git branch --show-current`).
2. Find the proof destination, in priority order:
   - Open PR for the branch: `gh pr view --json number,title,body,url` → proofs go to a PR comment.
   - Else a linked/related GitHub issue (from the PR body, branch name, or conversation) → issue comment.
   - Else → local transfer only (`~/Downloads/qa-proofs/<branch>/`).
3. Gather the task description: PR body, issue, and the conversation that led here.
4. Check the branch exists on `origin` (`git ls-remote --heads origin <branch>`). The devbox checks out from origin. If not pushed: ask the user whether to push it, or fall back to `hogli devbox:sync` mirroring (see Phase 5 transport notes).

## Phase 1 — Parallel kickoff

Run these two tracks concurrently — the devbox takes minutes to provision; write the criteria while it builds.

### Track A: acceptance criteria (you, plus an Explore subagent if needed)

Write a numbered list of concrete, executable criteria. Spawn an `Explore` subagent (sonnet) to map the touched code if you lack context. Each criterion needs:

- **ID** (`AC1`, `AC2`, …) and a one-line statement
- **Type**: browser flow / API / DB / mixed
- **Steps**: exact, reproducible (URLs, clicks, payloads, queries)
- **Expected result**: observable and unambiguous
- **Proof type**: screenshot (single UI state) / GIF (multi-step flow) / API transcript / SQL query+result

Cover the happy path, the key edge cases, and at least one regression check on adjacent behavior the change could have broken. Post the list to the user as a checkpoint. If the task is ambiguous enough that criteria could go two ways, ask before proceeding; otherwise continue without blocking.

### Track B: devbox provisioning (background)

```bash
hogli devbox:start -n qa-<slug> --start-app    # slug from the branch name; run in background, takes minutes
```

When it's up, put the branch on it (the AMI ships `~/posthog` on master):

```bash
hogli devbox:exec -n qa-<slug> -- bash -lc 'cd ~/posthog && git fetch origin <branch> && git checkout <branch>'
```

If the branch changes lockfiles or migrations, also run (always under flox — bare `node`/`npx`/`pnpm` are not on the login-shell PATH):

```bash
hogli devbox:exec -n qa-<slug> -- bash -lc 'cd ~/posthog && flox activate -- bash -c "pnpm install --frozen-lockfile"'
hogli devbox:exec -n qa-<slug> -- bash -lc 'cd ~/posthog && flox activate -- bash -c "python manage.py migrate"'
```

## Phase 2 — Browser rig on the fresh box

Follow `references/devbox-browser-rig.md` exactly — it is the full runbook (GUI stack, Playwright Chromium, desktop supervisor, HTTP Playwright MCP server, SSH tunnel, MCP availability check). Summary of the end state:

- Xvfb desktop on `:99`, watchable at `https://6080--dev--<workspace>--<user>.coder.dev.posthog.dev/vnc.html` — give this URL to the user so they can watch live
- `@playwright/mcp` HTTP server on box port 8931, browser profile `~/.cc-chrome-profile`
- Local tunnel `ssh -fN -L 8931:localhost:8931 coder.<workspace>` feeding the user-scope `devbox-browser` MCP registration

**Browser-tool availability decides how scenarios run** (the rig runbook's final step): if `mcp__devbox-browser__*` tools are loaded in your session, browser subagents use them directly. If not (the session started before the tunnel existed), every browser subtask goes through the local headless-Claude bridge instead — same capability, one hop:

```bash
echo "<browser task prompt>" | claude -p --model sonnet --allowedTools "mcp__devbox-browser__*"
```

(Prompt via **stdin** — `--allowedTools` is variadic and swallows a positional prompt.)

## Phase 3 — Verify the rig

Do not start scenarios until all three pass:

1. MCP handshake through the tunnel (curl `initialize` — see runbook) responds.
2. Browser smoke test: open `https://example.com`, expect the title back.
3. App smoke test: open `http://localhost:8010` (the box's localhost — the browser runs there). **Always `localhost:8010`** (dev proxy); never `172.17.0.1:8000` (granian direct → CSRF 403 on `/flags`, no feature flags).

## Phase 4 — App and data

1. Stack up (skip if `--start-app` did it): `hogli devbox:exec -n qa-<slug> -- bash -lc 'cd ~/posthog && hogli up -d && hogli wait'`
2. Demo data: `flox activate -- bash -c "python manage.py generate_demo_data"` → creates the Hedgebox org with login **test@posthog.com / 12345678**.
3. Feature-specific seeds: discover with `ls products/<product>/backend/management/commands/`, check `--help`, then run. Example (customer analytics): `python manage.py seed_customer_analytics_accounts`.
4. First browser login: a fresh box has an empty browser profile. The first browser scenario logs in (test@posthog.com / 12345678); the persistent profile keeps the session for every scenario after.
5. Known transient: right after a backend restart the flags service may briefly 401 ("API key invalid or expired") while HyperCache hydrates — wait and retry, or restart `feature-flags`/`hypercache-server`.

## Phase 5 — Scenario execution loop

Work through criteria one at a time. **Browser scenarios are serialized** — one Chromium, one profile, one driver at a time. Chore subagents run in parallel freely.

### Subagents

Default model: **sonnet**. Use **haiku** only for genuinely trivial single-command chores. Prompt templates in `references/subagent-prompts.md`.

| Role | Model | Tools | Notes |
|---|---|---|---|
| Browser driver | sonnet | `mcp__devbox-browser__*` (or the `claude -p` bridge) | One per scenario, serialized. Executes steps, captures proof files, returns PASS/FAIL + evidence + file paths. |
| Log watcher | sonnet | Bash (`hogli devbox:exec`) | Spawn *before* a browser scenario when failure diagnosis is likely; tails Django/service logs during the flow. |
| API checker | sonnet | Bash (`hogli devbox:exec` + curl / `manage.py shell -c`) | Backend assertions; capture full request/response transcripts. |
| DB checker | haiku ok | Bash (`hogli devbox:exec` + psql) | Single-query checks. Anything needing interpretation → sonnet. |

### Per criterion

1. Spawn the matching subagent(s) with the criterion's steps, expected result, and proof instructions (`references/proofs.md` for capture commands; proof files go to `/tmp/qa-proofs/<AC-id>/` on the box).
2. **PASS** → record evidence and file paths, move on.
3. **FAIL** → diagnose (re-read subagent evidence; spawn a log watcher and re-run the flow if the cause isn't clear). Then fix the code **locally** in the working tree.
4. Get the fix onto the box. Default transport for iteration is mutagen mirroring (seconds per change, no pushes):
   ```bash
   hogli devbox:sync          # run from the local repo root; box must have the SAME branch checked out
   ```
   Django autoreloads and webpack rebuilds on changed files; new migrations need a manual `manage.py migrate` on the box. (`devbox:sync --terminate` when done; first sync may report per-file conflicts for files diverged from the box's checkout — resolve only the paths that matter.)
5. Re-run the criterion. Repeat until it passes — or until the stop-and-ask rule triggers.
6. Commit fixes locally as logical units as you go. **Don't push** unless the user asked or approves (batch at the end).

## Phase 6 — Proofs

Per passed criterion, produce the proof named in the criteria. Full capture recipes (screenshots, GIF assembly via Playwright's bundled ffmpeg, API/SQL transcript formats, redaction rules) are in `references/proofs.md`.

1. Collect everything from `/tmp/qa-proofs/` on the box to local:
   ```bash
   mkdir -p ~/Downloads/qa-proofs/<branch> && scp -r coder.<workspace>:/tmp/qa-proofs/* ~/Downloads/qa-proofs/<branch>/
   ```
   (scp works through the coder SSH host; fallback is base64 over `devbox:exec`.)
2. Post to the destination from Phase 0 — `gh pr comment` / `gh issue comment` with the report template in `references/proofs.md`: a criteria table, text proofs (API/SQL) inline in code blocks, and image/GIF proofs listed by filename with their local path. **`gh` cannot upload images** — state in the comment that visual proofs are at `~/Downloads/qa-proofs/<branch>/` for drag-and-drop, and tell the user the same in chat.
3. No PR and no issue → local transfer only; full report in chat.

## Phase 7 — Wrap-up

Report to the user:

- Criteria table: ID, statement, PASS/FAIL, proof artifact
- Code changes made (commits on the branch, not pushed unless approved)
- The noVNC watch URL and the box name
- Running daemons left on the box (desktop, Playwright MCP server) and the local tunnel
- **Ask whether to stop the box** — it bills while running: `hogli devbox:stop -n qa-<slug>` (disk persists). Don't stop it unprompted; the user may want to poke around.

## Gotchas (hard-won — read before debugging)

- **flox everything**: on the box, `node`/`npx`/`python`/`pnpm` exist only inside `flox activate -- bash -c "..."`. A "command not found" or an MCP server that silently fails to spawn is almost always this.
- **`devbox:exec` needs `bash -lc '...'`** and the Coder banner pollutes output — suppress with `2>/dev/null` on the local side; the real output comes last.
- **Never `pkill -f`/`pgrep -f` with a pattern that appears in your own command line** through `devbox:exec` — it kills your own SSH session (exit 255). Verify daemons with `ss -tln`/`curl`, build patterns from shell variables, and prefer killing by PID from `ss -tlnp`.
- **MCP servers load at session start.** A tunnel opened mid-session doesn't give you the tools — use the `claude -p` stdin bridge (Phase 2). Keep ONE user-scope registration (`devbox-browser` → `localhost:8931`); the tunnel decides which box it reaches. A second simultaneous box needs an alternate local port + its own registration (and a session restart to use it natively).
- **One browser per profile.** Serialize browser drivers. A locked profile (`SingletonLock`) with no live Chromium means a dead process — clear the `Singleton*` files and relaunch.
- **App URL on the box is `localhost:8010`**, login `test@posthog.com / 12345678` (Hedgebox is the only seeded org with a real project).
- **Daemons die with the box** (stop/restart): desktop + MCP server must be re-run (runbook steps 3–4); the tunnel must be re-opened. The browser profile and repo survive on disk.
- **The relay alternative**: if for some reason the direct MCP path is unusable, the AgentAPI relay pattern (interactive Claude on the box fronted by `agentapi server --port 3286`, driven over HTTP) works — but it's strictly slower and only needed when no local session is in the loop at all.
