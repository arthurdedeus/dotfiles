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

1. Find the proof destination, in priority order:
   - Open PR for the branch: `gh pr view --json number,title,body,url` → fill the **"How did you test this code?"** section of the PR body (edit the description in place — no separate over-the-top comment).
   - Else a linked/related GitHub issue (from the PR body, branch name, or conversation) → issue comment.
   - Else → local transfer only (`~/Downloads/qa-proofs/<branch>/`).
2. Gather the task description: PR body, issue, and the conversation that led here.

Branch resolution and the not-pushed-to-origin fallback are handled by `setup-devbox` (Phase 1, Track B).

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

Once the criteria exist, stand up a **live progress page** (see "Progress page" below) and give the user its URL alongside the watch URL — that's the single place they glance at to follow the run.

### Track B: devbox provisioning + data (background)

Provision the box and seed data by **following the `setup-devbox` skill**, passing the working branch and name `qa-<slug>` (slug from the branch). It starts the box, checks out the branch, brings up the stack, runs `generate_demo_data`, seeds product accounts, syncs feature flags, and restarts the backend.

**Overlap the rig with the data setup.** When `setup-devbox` reaches its **box-up milestone** (end of its Phase 1 — box running, branch checked out), start the browser rig (Phase 2 below) concurrently with `setup-devbox`'s remaining data/flag/restart steps. The rig install (apt + Playwright) and `generate_demo_data` are the two slowest things in the run; never serialize them.

## Phase 2 — Browser rig

This runs in parallel with `setup-devbox`'s data phase (per Phase 1 Track B), starting at the box-up milestone. `setup-devbox` owns the app stack and data; this skill owns only the watchable browser.

Follow `references/devbox-browser-rig.md` exactly — it is the full runbook (GUI stack, Playwright Chromium, desktop supervisor, HTTP Playwright MCP server, SSH tunnel, MCP availability check). The runbook installs `scrot` (desktop screenshot capture) as part of setup, so the tool is ready before any scenario runs. Summary of the end state:

- Xvfb desktop on `:99`, watchable at `https://6080--dev--<workspace>--<user>.coder.dev.posthog.dev/vnc.html` — **always give this URL to the user immediately** so they can watch the browser live, plus a viewer Chromium pointed at the app (runbook step 4).
- `@playwright/mcp` HTTP server on box port 8931, browser profile `~/.cc-chrome-profile`
- Local tunnel `ssh -fN -L 8931:localhost:8931 coder.<workspace>` feeding the user-scope `devbox-browser` MCP registration

**Browser scenarios drive the `mcp__devbox-browser__*` tools directly from your orchestrator session.** The user-scope `devbox-browser` registration points at `localhost:8931`, which the tunnel routes to the current box. If the tools aren't loaded in your session, load their schemas via ToolSearch (they're available as deferred tools once the registration + tunnel exist); if that fails, restart the session so it picks them up. Browser scenarios are serialized anyway, so there's nothing to gain from delegating them.

## Phase 3 — Verify the rig

Do not start scenarios until all of these pass:

1. MCP handshake through the tunnel (curl `initialize` — see runbook) responds.
2. Browser smoke test: open `https://example.com`, expect the title back.
3. App smoke test: open `http://localhost:8010` (the box's localhost — the browser runs there). **Always `localhost:8010`** (dev proxy); never `172.17.0.1:8000` (granian direct → CSRF 403 on `/flags`, no feature flags).
4. **App-is-your-branch reaffirm.** `setup-devbox` (its Phase 3) already confirmed the running app serves your checkout, not a stale prebuild — re-load your feature's branch-unique route/element here before scenarios to be sure. If it doesn't match your branch, fix it now — see the prebuild-pollution gotcha in `setup-devbox`. Catching this avoids QA'ing the wrong code.

## Phase 4 — Login & known transients

1. First browser login: a fresh box has an empty browser profile. The first browser scenario logs in (test@posthog.com / 12345678); the persistent profile keeps the session for every scenario after.
2. Known transient: right after a backend restart the flags service may briefly 401 ("API key invalid or expired") while HyperCache hydrates — wait and retry, or restart `feature-flags`/`hypercache-server`.
3. Flag-gated routes can redirect or 404 on a **direct deep-link** because the client-side flag gate evaluates before posthog-js flags hydrate. Verify `posthog.isFeatureEnabled('<key>')` in the browser; if the gate still misses it, `posthog.featureFlags.override({'<key>': true})` or navigate *into* the tab after the app loads rather than deep-linking. After `sync_feature_flags`, the local flags service may need a moment (or a restart) before the frontend sees new flags.
4. **Stale in-process flag cache (flag enabled true everywhere but the gated UI still won't render).** Signature: the server `/flags` endpoint returns the flag `true` AND `posthog.isFeatureEnabled('<key>')` returns `true` in the browser, yet the kea-gated scene/tab still shows the intro/NotFound. Cause: in `SELF_CAPTURE` dev the web process loads its **own** flag definitions once at startup; a flag flipped *after* the app started never reaches the server-rendered bootstrap, so the gate stays false regardless of client-side state. This is the same staleness `setup-devbox` Phase 3 restarts the backend to clear — if it resurfaces during QA (e.g. after flipping a flag yourself), re-apply that fix: enable the flag in PG (active + 100% rollout), `touch posthog/urls.py` to reload the web worker, then a fresh full page load. Don't keep poking the client (`override`/`reloadFeatureFlags`) — the staleness is server-side.

## Progress page

A single HTML page on the box, served on a Coder-proxied port, that mirrors the criteria checklist **and embeds each proof as it's captured** — the single place the user glances at to follow the run. Stand it up at the end of Phase 1 (as soon as the criteria exist) and rewrite it whenever a criterion's status or proof changes.

Serve `/tmp` so the page can reference proof files directly (proofs live under `/tmp/qa-proofs/<AC-id>/`). Use system `python3` — the progress server needs no Django/flox, and a flox-wrapped `python` is not on PATH (it fails silently):

```bash
hogli devbox:exec -n qa-<slug> -- bash -lc 'cd /tmp && setsid nohup python3 -m http.server 7800 >/tmp/qa-progress-http.log 2>&1 < /dev/null & sleep 2; ss -tln | grep ":7800"' 2>/dev/null
```

Write `/tmp/qa-progress.html` with a row per criterion: ID, statement, status badge (⏳ pending / 🟡 running / ✅ pass / ❌ fail→fixed), and a **Proof** cell. The proof cell stays empty until capture; once a criterion's screenshot lands under `/tmp/qa-proofs/<AC-id>/`, embed it as a clickable thumbnail referenced by **server-relative** path (the server roots at `/tmp`):

```html
<a href="qa-proofs/AC3/AC3-assigned-to.png" target="_blank"><img src="qa-proofs/AC3/AC3-assigned-to.png" style="max-height:90px;border:1px solid #ddd"></a>
```

The server always serves the latest file on disk, so updating the page (a status flip or a newly-embedded proof) is just overwriting `/tmp/qa-progress.html` — no restart. URL (derive on the box, never hardcode): `hogli devbox:exec -n qa-<slug> -- bash -lc 'echo "${VSCODE_PROXY_URI/\{\{port\}\}/7800}/qa-progress.html"'`. Give the user this URL next to the watch URL.

## Phase 5 — Scenario execution loop

Work through criteria one at a time. **Browser scenarios are serialized** — one Chromium, one profile, one driver at a time. Chore subagents run in parallel freely.

### Subagents

Default model: **sonnet**. Use **haiku** only for genuinely trivial single-command chores. Prompt templates in `references/subagent-prompts.md`.

| Role | Model | Tools | Notes |
|---|---|---|---|
| Browser driver | sonnet | `mcp__devbox-browser__*` (driven directly) | One per scenario, serialized. Executes steps, captures proof files, returns PASS/FAIL + evidence + file paths. |
| Log watcher | sonnet | Bash (`hogli devbox:exec`) | Spawn *before* a browser scenario when failure diagnosis is likely; tails Django/service logs during the flow. |
| API checker | sonnet | Bash (`hogli devbox:exec` + curl / `manage.py shell -c`) | Backend assertions; capture full request/response transcripts. |
| DB checker | haiku ok | Bash (`hogli devbox:exec` + psql) | Single-query checks. Anything needing interpretation → sonnet. |

### Per criterion

1. Spawn the matching subagent(s) with the criterion's steps, expected result, and proof instructions (`references/proofs.md` for capture commands; proof files go to `/tmp/qa-proofs/<AC-id>/` on the box). Flip the criterion to 🟡 on the progress page when you start it.
2. **PASS** → record evidence; move/rename the captured screenshot into `/tmp/qa-proofs/<AC-id>/` (bridge/driver runs sometimes save `page-<timestamp>.png` in the MCP output dir instead of the requested name — match by timestamp). Then flip the row to ✅ **and embed that proof's thumbnail** on the progress page (server-relative `qa-proofs/<AC-id>/<file>.png`) so the user sees it live. Move on.
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

**Final proofs must reflect committed code.** Iteration fixes reach the box via `devbox:sync` (Phase 5), so the box drifts from origin to your working tree as you go. Before capturing the proofs you post, reconcile that drift: commit all fixes as logical units, `hogli devbox:sync` once more, and confirm both sides are clean (`git status` locally and `hogli devbox:exec -n qa-<slug> -- bash -lc 'cd ~/posthog && git status'`). If a proof was captured against uncommitted state, recapture it after committing — otherwise the artifacts you post won't match what merges.

1. Collect everything from `/tmp/qa-proofs/` on the box to local:
   ```bash
   mkdir -p ~/Downloads/qa-proofs/<branch> && scp -r coder.<workspace>:/tmp/qa-proofs/* ~/Downloads/qa-proofs/<branch>/
   ```
   (scp works through the coder SSH host; fallback is base64 over `devbox:exec`.)
2. Write the proof block to the destination from Phase 0 (template in `references/proofs.md`): a criteria table, text proofs (API/SQL) inline in code blocks, and image/GIF proofs listed by filename with their local path.
   - **PR** → `gh pr edit --body-file -`: replace the contents of the **"How did you test this code?"** section with the block, leaving the rest of the description intact. Keep it tight — it lives in the description, not a wall-of-text comment.
   - **Issue** → `gh issue comment`.
   - **`gh` cannot upload images** — state that visual proofs are at `~/Downloads/qa-proofs/<branch>/` for drag-and-drop, and tell the user the same in chat.
3. No PR and no issue → local transfer only; full report in chat.

## Phase 7 — Wrap-up

Report to the user:

- Criteria table: ID, statement, PASS/FAIL, proof artifact
- Code changes made (commits on the branch, not pushed unless approved)
- The noVNC watch URL, the progress-page URL, and the box name
- Running daemons left on the box (desktop, Playwright MCP server) and the local tunnel
- **Ask whether to stop the box** — it bills while running: `hogli devbox:stop -n qa-<slug>` (disk persists). Don't stop it unprompted; the user may want to poke around.

## Gotchas (hard-won — read before debugging)

> **Box/provisioning gotchas live in `setup-devbox`** and apply equally here: flox-everything (`node`/`npx`/`python`/`pnpm` only inside `flox activate -- bash -c "..."`), `devbox:exec` needs `bash -lc '...'`, env-sourcing for management commands, app URL `localhost:8010` + login `test@posthog.com / 12345678`, and polluted warm prebuild (destroy & reprovision). The QA/browser-specific ones below are on top of those.

- **Never `pkill -f`/`pgrep -f` with a pattern that appears in your own command line** through `devbox:exec` — it kills your own SSH session (exit 255). Verify daemons with `ss -tln`/`curl`, build patterns from shell variables, and prefer killing by PID from `ss -tlnp`. When writing a script whose *body* contains such patterns (e.g. the desktop supervisor's `pkill -f "Xvfb :99"`), write the file and launch it in **separate** `devbox:exec` calls — doing both in one call puts the patterns in the launching command's argv, so the script's own `pkill` kills your session.
- **MCP servers load at session start.** A tunnel opened mid-session may not surface the tools immediately — load their schemas via ToolSearch (deferred tools) or restart the session. Keep ONE user-scope registration (`devbox-browser` → `localhost:8931`); the tunnel decides which box it reaches. A second simultaneous box needs an alternate local port + its own registration (and a session restart to use it natively).
- **One browser per profile.** Serialize browser drivers. A locked profile (`SingletonLock`) with no live Chromium means a dead process — clear the `Singleton*` files and relaunch.
- **Browser-rig daemons die with the box** (stop/restart): desktop + MCP server must be re-run (runbook steps 3–4); the tunnel must be re-opened. The browser profile and repo survive on disk. (The app stack is `setup-devbox`'s concern.)
- **Polluted prebuild can make browser QA not worth it:** CH-independent Postgres+frontend features are already covered by jest/typecheck/backend tests, so if the box won't serve your branch and needs a reprovision (see `setup-devbox`), weigh whether browser QA earns the cost.
- **The relay alternative**: if for some reason the direct MCP path is unusable, the AgentAPI relay pattern (interactive Claude on the box fronted by `agentapi server --port 3286`, driven over HTTP) works — but it's strictly slower and only needed when no local session is in the loop at all.
