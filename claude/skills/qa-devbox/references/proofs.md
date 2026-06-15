# Proof capture, transfer, and posting

Every passed criterion produces a proof artifact. Layout on the box: `/tmp/qa-proofs/<AC-id>/` (e.g. `/tmp/qa-proofs/AC3/`). Name files descriptively: `AC3-filtered-list.png`, `AC5-flow.gif`, `AC7-api-transcript.md`.

## Screenshot (single UI state)

The browser driver calls `browser_take_screenshot` with a `filename` — it lands in the MCP server's `--output-dir` (`/tmp/qa-proofs/raw/`). Move it into the criterion folder:

```bash
hogli devbox:exec -n <label> -- bash -lc 'mkdir -p /tmp/qa-proofs/AC3 && mv /tmp/qa-proofs/raw/<file>.png /tmp/qa-proofs/AC3/AC3-<desc>.png' 2>/dev/null
```

Have the driver screenshot the *meaningful* state: after the action, with the relevant element visible. Full-page when layout matters.

## GIF (multi-step flow)

Playwright MCP has no video flag, and **Playwright's bundled ffmpeg cannot do this** — it's a minimal build (no gif encoder, no x11grab; tested and failed). The dependable proof for a multi-step flow is **numbered per-step screenshots**: the driver takes `AC5-step01.png`, `AC5-step02.png`, … after each step — they read as a storyboard and post fine individually.

If an actual GIF is wanted, assemble it on the box with imagemagick (install via the flox.list dance):

```bash
hogli devbox:exec -n <label> -- bash -lc 'sudo mv /etc/apt/sources.list.d/flox.list /tmp/flox.list.bak
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq imagemagick
sudo mv /tmp/flox.list.bak /etc/apt/sources.list.d/flox.list
cd /tmp/qa-proofs/AC5 && convert -delay 150 -loop 0 AC5-step*.png -resize 960x AC5-flow.gif' 2>/dev/null
```

Keep GIFs under ~10 MB (GitHub comment limit) — scale down or drop frames if needed.

**Screenshot naming caveat:** drivers sometimes ignore the `filename` instruction and screenshots land as `page-<timestamp>.png` in `--output-dir`. After each scenario, check the named file actually exists; if not, match by timestamp and rename (or have the orchestrator view candidates and pick). Emphasize the exact filename in the driver prompt.

## API transcript (backend changes)

Capture the full request and response. Two routes:

- **As the logged-in user** — the browser driver runs `browser_evaluate` with a `fetch` against the app (session cookies apply), returning status + JSON.
- **Direct on the box** — `hogli devbox:exec -n <label> -- bash -lc 'curl -s -i http://localhost:8010/api/... -H "Authorization: Bearer <key>"'`. Mint a personal API key via `manage.py shell -c` if needed.

Write as markdown into `/tmp/qa-proofs/<AC-id>/<AC-id>-api-transcript.md`:

````markdown
### AC7 — <statement>
**Request:** `GET /api/projects/1/...`
**Response:** `200 OK`
```json
{ ... }
```
````

**Redact** any tokens, API keys, or cookies before saving.

## SQL (database changes)

```bash
hogli devbox:exec -n <label> -- bash -lc 'psql -h localhost -U posthog posthog -c "SELECT ... ;"' 2>/dev/null
```

Save query + result table as markdown (code-fenced) into the criterion folder. Same redaction rule.

## Backend state via Django

For assertions that are awkward as SQL (ORM properties, computed state):

```bash
hogli devbox:exec -n <label> -- bash -lc 'cd ~/posthog && flox activate -- bash -c "python manage.py shell -c \"...\""' 2>/dev/null
```

Save the snippet + output as the proof.

## Transfer to local

```bash
mkdir -p ~/Downloads/qa-proofs/<branch>
scp -r coder.<workspace>:/tmp/qa-proofs/AC* ~/Downloads/qa-proofs/<branch>/
```

Fallback if scp misbehaves through the ProxyCommand: base64 over exec, decoded locally:

```bash
hogli devbox:exec -n <label> -- bash -lc 'base64 < /tmp/qa-proofs/AC3/AC3-x.png' 2>/dev/null > /tmp/x.b64 && base64 --decode < /tmp/x.b64 > ~/Downloads/qa-proofs/<branch>/AC3-x.png
```

## Posting the report

Destination from Phase 0: PR comment → issue comment → chat-only. Pass the body via stdin (`--body-file -`), never a temp file.

**`gh` cannot attach images.** Inline what is text (API/SQL proofs in code blocks); list visual proofs by filename and state where they are locally so the user can drag-and-drop them in. Say the same in chat.

Template:

```markdown
## 🧪 QA report — <branch>

Ran on a fresh devbox (`<workspace>`) against this branch. Watch URL was <noVNC url>.

| # | Criterion | Result | Proof |
|---|---|---|---|
| AC1 | <statement> | ✅ | screenshot `AC1-<desc>.png` |
| AC2 | <statement> | ✅ | GIF `AC2-flow.gif` |
| AC3 | <statement> | ✅ | API transcript below |
| AC4 | <statement> | ❌ → fixed in <sha> → ✅ | SQL below |

### AC3 — API transcript
<inline markdown transcript>

### AC4 — SQL
<inline query + result>

> 📎 Visual proofs (screenshots/GIFs) are at `~/Downloads/qa-proofs/<branch>/` on <user>'s machine — drag-and-drop into this thread to attach.

### Fixes made during QA
- <sha> <message> (what failed, why, what changed)
```

For criteria that failed and were fixed: keep the failure visible in the table (`❌ → fixed in <sha> → ✅`) — the fix history is part of the QA value.
