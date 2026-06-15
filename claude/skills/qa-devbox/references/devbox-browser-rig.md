# Devbox browser rig — fresh-box runbook

Sets up a watchable browser that local Claude sessions can drive over MCP. Derived from Arthur's doc *Running "Claude in Chrome" on a PostHog devbox* (Obsidian, `1 Projects/DevEx/`) plus operational fixes. All `devbox:exec` commands below assume `-n <label>` for the target box; `<workspace>` is the full Coder workspace name from `hogli devbox:list` (e.g. `devbox-arthur-qa-foo`).

Environment facts that drive the choices:

| Fact | Consequence |
|---|---|
| Devbox is **aarch64 Linux** | No Google Chrome build — use Playwright's Chromium only |
| The **flox apt repo has a broken GPG key** | Disable it around every `apt` call, restore after |
| **node/npx live in the flox env** | Every node-ish command runs via `flox activate -- bash -c "..."` |
| Coder proxies any port | noVNC on 6080 becomes a laptop-viewable URL |
| Box ports are localhost-bound | Local access via `ssh -L` tunnel through the `coder.<workspace>` SSH host |

## 1. GUI stack

`scrot` ships here too (desktop screenshot capture for browser-liveness proof — see §4), so it's installed once up front rather than mid-run:

```bash
hogli devbox:exec -n <label> -- bash -lc 'sudo mv /etc/apt/sources.list.d/flox.list /tmp/flox.list.bak
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq xvfb x11vnc novnc websockify fluxbox scrot
sudo mv /tmp/flox.list.bak /etc/apt/sources.list.d/flox.list' 2>/dev/null
```

## 2. Playwright Chromium + system deps

```bash
hogli devbox:exec -n <label> -- bash -lc 'cd ~/posthog && flox activate -- bash -c "npx playwright install chromium"
sudo mv /etc/apt/sources.list.d/flox.list /tmp/flox.list.bak
cd ~/posthog && flox activate -- bash -c "npx playwright install-deps chromium"
sudo mv /tmp/flox.list.bak /etc/apt/sources.list.d/flox.list' 2>/dev/null
```

The versioned binary path changes with Playwright releases — always resolve it dynamically:

```bash
CHROME=$(ls ~/.cache/ms-playwright/chromium-*/chrome-linux/chrome | head -1)
```

## 3. Desktop supervisor

Write `~/start-desktop.sh` on the box with exactly this content (heredoc via `devbox:exec`), then `chmod +x`:

```bash
#!/usr/bin/env bash
# Supervisor: launches a watchable headless desktop and stays in foreground.
set -u

pkill -f "Xvfb :99" 2>/dev/null
pkill x11vnc 2>/dev/null
pkill -f "websockify.*6080" 2>/dev/null
pkill fluxbox 2>/dev/null
sleep 1
rm -f /tmp/.X99-lock

export DISPLAY=:99

Xvfb :99 -screen 0 1440x900x24 -ac >/tmp/desktop-xvfb.log 2>&1 &
XVFB_PID=$!
sleep 2
fluxbox >/tmp/desktop-fluxbox.log 2>&1 &
sleep 1
x11vnc -display :99 -forever -shared -nopw -rfbport 5900 -localhost >/tmp/desktop-x11vnc.log 2>&1 &
sleep 2
websockify --web /usr/share/novnc 6080 localhost:5900 >/tmp/desktop-novnc.log 2>&1 &
sleep 2

echo "DESKTOP_UP display=:99 novnc=6080"
wait $XVFB_PID
```

Launch it **detached from any Claude session** so it survives session churn (this differs from the original doc, which launched it from inside a Claude session where it dies with the session):

```bash
hogli devbox:exec -n <label> -- bash -lc 'setsid nohup bash ~/start-desktop.sh >/tmp/desktop-supervisor.log 2>&1 < /dev/null & sleep 8; ss -tln | grep -E ":6080|:5900"' 2>/dev/null
```

Both ports listening = desktop up. Watch URL (derive on the box — never hardcode):

```bash
hogli devbox:exec -n <label> -- bash -lc 'echo "${VSCODE_PROXY_URI/\{\{port\}\}/6080}/vnc.html"' 2>/dev/null
```

## 4. Playwright MCP HTTP server

One server per box, port 8931, headed on `:99`, persistent profile (keeps logins between scenarios):

```bash
hogli devbox:exec -n <label> -- bash -lc 'CHROME=$(ls ~/.cache/ms-playwright/chromium-*/chrome-linux/chrome | head -1)
mkdir -p /tmp/qa-proofs/raw
cd ~/posthog
setsid nohup env DISPLAY=:99 flox activate -- bash -c "npx -y @playwright/mcp@latest --port 8931 --shared-browser-context --executable-path $CHROME --no-sandbox --viewport-size 1440x900 --user-data-dir \$HOME/.cc-chrome-profile --output-dir /tmp/qa-proofs/raw" >/tmp/pw-mcp-http.log 2>&1 < /dev/null &
sleep 15; ss -tln | grep ":8931" && tail -3 /tmp/pw-mcp-http.log' 2>/dev/null
```

**The scenario browser is ephemeral by design**: the server launches it lazily per client session and closes it when the last client disconnects — each `claude -p` bridge call is a short-lived client, so the noVNC desktop looks empty between tasks (a bare SSE "holder" connection does NOT prevent this; tested). For an always-visible window the user can watch and use, launch a separate **viewer Chromium** with its own profile (no lock conflict with the MCP browser):

```bash
hogli devbox:exec -n <label> -- bash -lc 'CHROME=$(ls ~/.cache/ms-playwright/chromium-*/chrome-linux/chrome | head -1)
setsid nohup env DISPLAY=:99 "$CHROME" --user-data-dir="$HOME/.view-profile" --no-sandbox --no-first-run --disable-dev-shm-usage --start-maximized http://localhost:8010 >/tmp/view-chrome.log 2>&1 < /dev/null &' 2>/dev/null
```

The MCP scenario browser appears alongside it while a scenario runs and vanishes after — that's normal.

Notes:
- `--output-dir` is where `browser_take_screenshot` writes files.
- The browser launches lazily on the first tool call, not at server start.
- **Verifying browser liveness:** don't `pgrep` for the profile path — the MCP server's own command line contains it (false positive). Check for real renderer processes (`pgrep -fc "type=renderer"`) or screenshot the desktop with `DISPLAY=:99 scrot -o /tmp/desktop.png` (scrot is installed in §1) — Playwright's bundled ffmpeg has no x11grab, so scrot is the desktop-proof tool.
- The stdio variant of this server may also exist in `~/posthog/.mcp.json` (`browser` entry) for Claude sessions running *on* the box — they coexist only if not used simultaneously (one profile, one browser).

## 5. SSH tunnel (local machine)

```bash
ssh -fN -L 8931:localhost:8931 coder.<workspace>
```

- The `coder.*` SSH host pattern is written by `hogli devbox:setup` (ProxyCommand through the coder CLI).
- Local port 8931 feeds the existing user-scope MCP registration. If 8931 is already tunneling another box, pick the next free port — but that needs its own registration (`claude mcp add --scope user --transport http devbox-browser-2 http://localhost:<port>/mcp`) and a session restart to load natively.
- Kill a stale tunnel by PID: `lsof -nP -iTCP:8931 -sTCP:LISTEN` → `kill <pid>`.

## 6. Local MCP registration (one-time, already done)

```bash
claude mcp add --scope user --transport http devbox-browser http://localhost:8931/mcp
```

Already registered in the posthog-code config. The registration is box-agnostic — the tunnel decides which devbox `localhost:8931` reaches.

## 7. Verify

```bash
# a) Handshake through the tunnel
curl -s --max-time 10 -X POST http://localhost:8931/mcp \
  -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"probe","version":"1.0"}}}'
# expect: serverInfo name "Playwright"

# b) Tool availability in the current session
# ToolSearch for "browser_navigate" — present → drive directly; absent → use the claude -p bridge:
echo "Use the devbox-browser MCP tools to open https://example.com and reply with exactly TITLE=<page title>." \
  | claude -p --model sonnet --allowedTools "mcp__devbox-browser__*"
# expect: TITLE=Example Domain
```

## Teardown / restart notes

- Box stop/start kills the desktop, the MCP server, and (locally) orphans the tunnel: re-run steps 3–5. The repo, browser profile, and installed packages survive on disk.
- Stop the box when QA is done (billing): `hogli devbox:stop -n <label>`.
