---
name: ui-testing-proof
description: Test interactive web UI scenarios with Browser Use, record polished proof with Pagecast, validate pass/fail assertions, and deliver screenshots/GIFs/MP4s as artifacts. Use when asked to test a UI, verify a browser workflow, record a demo, or provide visual proof that behavior works or fails.
compatibility: Requires Browser Use, patched Pagecast, Playwright Chromium, and ffmpeg. Local Chrome requires remote-debugging approval.
---

# UI testing with visual proof

Use **Browser Use for inspection and assertions** and **Pagecast for the final recorded run**. A successful tool call is not proof. Verify observable state, capture the actual run, validate the media, and report pass or fail without hiding failures.

Before using this skill, read the installed `browser-use` skill completely. If Pagecast setup, authentication, cursor behavior, or artifact delivery matters, also read [references/local-pagecast-setup.md](references/local-pagecast-setup.md).

## Non-negotiable rules

1. Test every user step and every expected result explicitly.
2. Record the real test run; never reenact a completed test solely to manufacture proof.
3. Use stable selectors and verify state after every consequential interaction.
4. Never claim PASS from “clicked,” “typed,” or HTTP success alone.
5. Capture failure evidence when a step fails; do not continue as if it passed.
6. Do not enter personal passwords, MFA, consent, or choose an ambiguous account. Ask the user.
7. Do not expose secrets in output, filenames, timelines, screenshots, or videos.
8. Upload non-code deliverables with `upload_artifact` when that tool is available.
9. Never claim a local Markdown path is a downloadable artifact.
10. Stop/finalize recordings before presenting them. Validate finalized media, not a growing `page@*.webm` file.

## Understand the two browsers

Browser Use and Pagecast control different browser sessions:

- **Browser Use** attaches to the user's Chrome through CDP. Use it to inspect accessibility state, discover selectors, diagnose failures, and capture targeted screenshots.
- **Pagecast** launches an isolated Playwright Chromium context. Use it to reproduce the verified workflow and produce WebM/GIF/MP4 evidence with a visible red cursor and click ripples.

They do not share tabs, cookies, or login state. Do not assume that authenticating Browser Use authenticates Pagecast.

## Workflow

### 1. Turn the scenario into an assertion matrix

Before interacting, list each step with its observable evidence:

| Step | Action | Assertion | Proof frame |
|---|---|---|---|
| 1 | Open feature | Correct route/title, no error UI | Initial loaded state |
| 2 | View data | Existing rows/items visible | Data list |
| 3 | Change filter | Filter label/query/count changes | Filtered state |
| 4 | Clear filter | Default/unfiltered state returns | Cleared state |
| 5 | Open item | Detail route/title appears | Detail header |
| 6 | Load history | Existing messages/events visible | History content |

Identify what counts as failure: alert/error text, empty data when fixtures are expected, timeout, wrong URL, unchanged count, missing message history, console exception, or failed request.

### 2. Preflight Browser Use

```bash
browser-use --doctor
```

For local Chrome, all required local checks should pass. Cloud authentication is optional. If Chrome requests remote-debugging permission, stop and ask the user to approve it; do not retry in a loop.

Inspect the current state before acting:

```bash
browser-use <<'PY'
print(page_info())
print(js("document.body.innerText.slice(0,12000)"))
PY
```

Prefer the accessibility tree for element discovery:

```bash
browser-use <<'PY'
nodes = cdp("Accessibility.getFullAXTree")["nodes"]
for n in nodes:
    role = ((n.get("role") or {}).get("value") or "")
    name = ((n.get("name") or {}).get("value") or "")
    if role in {"button", "link", "textbox", "row", "cell", "tab"} and name.strip():
        print({"role": role, "name": name[:240], "backendDOMNodeId": n.get("backendDOMNodeId")})
PY
```

Use Browser Use to learn robust selectors and expected state. Prefer `data-testid`, `data-attr`, semantic roles/names, stable hrefs, and labeled fields. Avoid generated classes and stale backend node IDs in the Pagecast reproduction.

### 3. Start Pagecast before the final test run

Preferred: use Pagecast through MCP if it was loaded at session startup. Search for `pagecast record`, connect the server, and call the discovered tools.

Fallback for local sessions: resolve these scripts relative to this skill directory:

```bash
./scripts/pagecast-controller-start.sh
./scripts/pagecast-call.py --health
```

Start a headed 16:9 recording:

```bash
./scripts/pagecast-call.py record_page '{
  "url": "https://app.example.test/start",
  "platform": "github"
}'
```

Retain the exact Pagecast session ID. Do not substitute “latest.”

### 4. Authenticate safely

Pagecast is isolated from Browser Use. For SSO/password/MFA:

1. Open the protected URL with `record_page`.
2. Ask the user to authenticate manually in the visible Pagecast browser.
3. Keep the same Pagecast session alive.
4. If an explicitly authorized test account remains, use stable selectors to enter it.
5. Keep authentication out of the final clip by trimming the beginning after finalization.

The local Pagecast patch redacts password-like inputs from MCP responses and timelines. Still avoid production credentials and remember that visible account information can appear in video.

### 5. Run each action and assert its result

Use short Pagecast action batches so a failure is attributable:

```bash
./scripts/pagecast-call.py interact_page '{
  "sessionId": "SESSION_ID",
  "actions": [
    {"type": "waitForSelector", "selector": "[data-testid=ticket-list]"},
    {"type": "hover", "selector": "button[data-testid=status-filter]"},
    {"type": "click", "selector": "button[data-testid=status-filter]"},
    {"type": "click", "selector": "[role=option][data-value=new]"},
    {"type": "wait", "ms": 1500}
  ]
}'
```

After each batch, verify observable state with Browser Use or a Pagecast selector wait. Useful checks:

- URL and document title changed as expected.
- Required text/rows/messages are visible.
- Counts changed after filtering and returned after clearing.
- Error banners and `[role=alert]` are absent.
- Controls are enabled and selected state is correct.
- The detail page contains real history, not only a shell/loading state.

For slow development builds, use explicit waits and then verify. Do not confuse “still compiling” with either PASS or FAIL.

### 6. Capture complementary screenshots

Videos prove the flow; screenshots make key states easy to review. Save evidence inside the session workspace:

```text
test-evidence/<scenario-slug>/
  01-loaded.png
  02-filtered.png
  03-cleared.png
  04-detail-history.png
  scenario.webm
  scenario.mp4
  scenario.gif
  result.md
```

Capture the exact state immediately. Do not overwrite one temporary screenshot before copying it to its final evidence name.

### 7. Finalize and export Pagecast media

Stop the exact session:

```bash
./scripts/pagecast-call.py stop_recording '{"sessionId":"SESSION_ID"}'
```

Do not kill the controller while a large recording is flushing. Derive the timeline path from the WebM when needed:

```text
/path/recording-SESSION.webm
/path/recording-SESSION-timeline.json
```

For QA proof, MP4 is the default:

```bash
./scripts/pagecast-call.py convert_to_mp4 '{
  "webmPath": "/absolute/path/recording-SESSION.webm",
  "crf": 23
}'
```

Use `smart_export` for full-context tooltip closeups or `cinematic_export` for a polished camera-following demo. Preserve the original WebM and timeline until the exported media has been validated.

### 8. Validate evidence before reporting

```bash
./scripts/validate-evidence.sh /path/to/scenario.mp4
./scripts/validate-evidence.sh /path/to/scenario.gif
```

Validation must confirm:

- File exists and is non-empty.
- Duration is plausible for the scenario.
- Resolution and codec are expected.
- The first useful frame is not a login/loading/blank screen.
- The important final state is held long enough to inspect.
- The red Pagecast cursor and click feedback are visible during interactions.
- No password, token, unrelated tab, notification, or sensitive personal data is exposed.

If cursor proof matters, inspect sampled frames. The native OS cursor is not recorded; the patched Pagecast DOM cursor must be visible. See [references/local-pagecast-setup.md](references/local-pagecast-setup.md) for diagnostics.

### 9. Decide PASS or FAIL

**PASS** only when every required assertion succeeds and evidence opens correctly.

**FAIL** when any required assertion fails, even if later steps happen to work. Record:

- First failing step.
- Expected versus observed state.
- URL/title and visible error.
- Screenshot/video segment.
- Any relevant console/network error.
- Whether remaining steps were skipped or separately investigated.

Use **BLOCKED** rather than FAIL when completion requires unavailable credentials, MFA, consent, an ambiguous account choice, missing fixtures, or an inaccessible environment.

### 10. Deliver artifacts

When `upload_artifact` exists, upload every final non-code deliverable from inside the session workspace:

- `video/mp4` for MP4
- `video/webm` for WebM
- `image/gif` for GIF
- `image/png` for screenshots
- `text/markdown` for the result summary

Keep each artifact below the platform limit. Mention the returned download URL in the final response.

When artifact upload is unavailable in a local scratch session, state that explicitly. Do not provide a relative link and imply the user can download it. Offer to open the local file or rerun the work as a cloud task.

## Reporting template

```markdown
## <Scenario> — PASS | FAIL | BLOCKED

### Assertions
- [x] Page loaded without an error
- [x] Existing items appeared
- [x] Filter changed the result set
- [x] Clearing restored the result set
- [x] Detail history loaded

### Evidence
- MP4 artifact: <artifact URL or explicit local-only status>
- GIF artifact: <artifact URL or explicit local-only status>
- Screenshot 1: <artifact URL>
- Screenshot 2: <artifact URL>

### Observed values
- Initial count: 2
- Filtered count: 1
- Restored count: 2
- Opened item: #2
- Loaded history: “…”

### Notes
- No visible error banner or alert.
- Recording validated at 1280×720, H.264, <duration>s.
```

## Cleanup

- Keep an authenticated Pagecast session open only when more scenarios are imminent.
- Otherwise call `stop_recording` and allow finalization to finish.
- Close Browser Use cloud browsers after asking the user; cloud sessions can continue billing.
- Remove temporary live snapshots and test fixtures, but retain final evidence and source timelines until delivery is confirmed.
