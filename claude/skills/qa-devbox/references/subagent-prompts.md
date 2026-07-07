# Subagent prompt templates

Fill `<>` placeholders from the criterion. Every prompt ends by telling the subagent its reply is data for the orchestrator — structured, no prose padding. Spawn via the Agent tool (`subagent_type: general-purpose` unless noted, `model: sonnet` by default).

## Browser driver (sonnet, serialized)

Drive the `mcp__devbox-browser__*` tools directly (load their schemas via ToolSearch if not already in-session). Browser scenarios are serialized, so run them from your orchestrator session rather than delegating.

```text
You are executing one QA acceptance criterion against a PostHog devbox browser.
You have mcp__devbox-browser__* tools (browser_navigate, browser_snapshot, browser_click,
browser_type, browser_evaluate, browser_take_screenshot). The browser runs ON the devbox,
so localhost URLs resolve on the devbox. Use only browser tools.

App: http://localhost:8010 — if you land on a login page, log in with
test@posthog.com / 12345678. If a "Dev login" list is shown, click EXACTLY the
row whose email text is test@posthog.com — not test+N and not any seed/pool
user; read the snapshot before clicking (the list reorders as seeds add users).

IDENTITY GUARD (mandatory when the criterion depends on who is logged in):
after login, run browser_evaluate:
  async () => (await (await fetch("/api/users/@me", {credentials:"include"})).json()).email
It must return test@posthog.com. Wrong user → log out (/logout), retry once,
else stop and report FAIL with the email you got. A QA run was once burned by
the driver silently being logged in as a seed user.

Criterion <AC-id>: <statement>
Steps:
<numbered exact steps>
Expected result: <observable expectation>

Proof: <"take a screenshot named {AC-id}-{desc}.png of the final state"
| "after EACH step take a screenshot named {AC-id}-stepNN.png (zero-padded)"
| "run browser_evaluate with this fetch and record status + body: <fetch snippet>">

Rules:
- Verify against the page snapshot, not assumptions. If an element is missing, say so — do not improvise alternate paths.
- If the page errors or behaves unexpectedly, capture a screenshot of the failure state and the relevant console errors before concluding.

Reply with exactly:
RESULT: PASS | FAIL
EVIDENCE: <2-4 lines: what you observed vs expected>
PROOF_FILES: <comma-separated filenames you created, or none>
NOTES: <anything the orchestrator needs: console errors, suspicious behavior, flakiness>
```

## Log watcher (sonnet, parallel with a browser scenario)

```text
You are watching server logs on a PostHog devbox while a browser scenario runs.
Use Bash with: hogli devbox:exec -n <label> -- bash -lc '<cmd>' 2>/dev/null

For ~<N> seconds, poll the relevant logs (e.g. docker compose logs / process logs for web,
feature-flags, capture — discover with `hogli devbox:exec -n <label> -- bash -lc 'cd ~/posthog && hogli ps'`
or tail the files under /tmp if hogli logs aren't available).
Watch for: exceptions, 4xx/5xx on <relevant endpoints>, warnings mentioning <feature keywords>.

Reply with exactly:
FINDINGS: <bulleted list of anomalies with timestamps and the log lines, or "clean">
```

## API checker (sonnet)

```text
You are verifying a backend behavior on a PostHog devbox.
Use Bash with: hogli devbox:exec -n <label> -- bash -lc '<cmd>' 2>/dev/null
The app is at localhost:8010 ON the box. For authenticated calls either mint a personal API
key via manage.py shell (under flox: flox activate -- bash -c "python manage.py shell -c ...")
or assert via the ORM directly in manage.py shell.

Criterion <AC-id>: <statement>
Check: <exact request(s) or shell snippet>
Expected: <status / payload shape / state>

Save a markdown transcript (request, status, response — REDACT any tokens) to
/tmp/qa-proofs/<AC-id>/<AC-id>-api-transcript.md on the box.

Reply with exactly:
RESULT: PASS | FAIL
EVIDENCE: <status + the decisive part of the response>
PROOF_FILES: <paths written>
```

## DB checker (haiku for a single known query; sonnet if interpretation needed)

```text
You are verifying database state on a PostHog devbox.
Use Bash with: hogli devbox:exec -n <label> -- bash -lc 'psql -h localhost -U posthog posthog -c "<SQL>"' 2>/dev/null

Criterion <AC-id>: <statement>
Query: <SQL>
Expected: <rows / values>

Save query + result as markdown to /tmp/qa-proofs/<AC-id>/<AC-id>-sql.md on the box.

Reply with exactly:
RESULT: PASS | FAIL
EVIDENCE: <the decisive rows/values>
PROOF_FILES: <paths written>
```

## Explore (criteria support)

Use the built-in `Explore` agent type, thoroughness "medium": ask for the feature's surface — routes, components, API endpoints, models touched by the branch diff — to ground the acceptance criteria in what actually changed.
