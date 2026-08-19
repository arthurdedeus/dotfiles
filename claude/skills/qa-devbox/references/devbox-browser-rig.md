# Devbox browser rig

Use this rig when the browser must run inside the ARM64 devbox. Prefer a simpler local browser against the Coder proxy when it meets the test needs.

All `bin/hogli devbox:exec` commands need `-n <label>`. Obtain the full workspace name from `bin/hogli devbox:list`.

## 1. Install the desktop and browser

The box uses Playwright Chromium. Google Chrome has no supported ARM64 Linux build.

Install Xvfb, x11vnc, noVNC, websockify, fluxbox, and scrot. Preserve the Flox apt source and restore it with a shell trap if package installation fails.

Then run from `~/posthog`:

```bash
flox activate -- bash -c 'npx playwright install chromium'
```

Install Playwright's system dependencies with the same apt-source protection.

Resolve the browser path at runtime:

```bash
CHROME=$(find ~/.cache/ms-playwright -path '*/chrome-linux/chrome' -type f | sort | tail -1)
test -x "$CHROME"
```

## 2. Start the desktop

Run these services on display `:99`:

- `Xvfb` at 1440×900×24.
- `fluxbox`.
- `x11vnc` on localhost port 5900.
- `websockify` with noVNC on port 6080.

Start the supervisor with `setsid nohup`. Verify ports 5900 and 6080 with `ss -tln`.

Do not use `pkill -f` with a pattern present in the launching command. It can kill the SSH session. Kill known PIDs instead.

Get the watch URL from the box:

```bash
echo "${VSCODE_PROXY_URI/\{\{port\}\}/6080}/vnc.html"
```

Give this URL to the user.

## 3. Start Playwright MCP

Start one headed HTTP MCP server on box port 8931 with:

- `DISPLAY=:99`.
- The resolved Chromium executable.
- A persistent user-data directory.
- `/tmp/qa-proofs/raw` as the output directory.
- `setsid nohup` so it survives the SSH command.

Use the current `@playwright/mcp` CLI syntax. Record the resolved package version in the QA report when using `@latest`.

Verify port 8931 and inspect the server log before opening a tunnel.

A separate viewer Chromium may remain open on the noVNC desktop. Use a different browser profile from the MCP server.

## 4. Open the tunnel

```bash
ssh -fN \
  -o ServerAliveInterval=30 \
  -o ServerAliveCountMax=3 \
  -o ExitOnForwardFailure=yes \
  -L 8931:localhost:8931 \
  coder.<workspace>
```

If port 8931 is occupied, choose another local port. Record the selected port.

On a connection failure, check the box server first. Then replace only the stale local tunnel.

## 5. Register the MCP server

Register `http://localhost:<local-port>/mcp` in the active harness.

- Claude Code can use `claude mcp add --scope user --transport http <name> <url>`.
- Pi can use its configured MCP adapter and `~/.pi/agent/mcp.json`.

Use a unique name when more than one devbox browser exists. Most harnesses load MCP registrations at session start. Restart the session when the new server is not discoverable.

Do not claim the server is already registered without checking the current config.

## 6. Verify

Send an MCP `initialize` request through the tunnel and confirm the Playwright server response.

Then use the active harness to:

1. List browser tools.
2. Open `https://example.com`.
3. Verify its title.
4. Open `http://localhost:8010` from the box browser.
5. Verify the branch-specific app state.

## Teardown

Stopping the box ends the desktop and MCP server. Reopen both and the tunnel after a restart.

The browser profile and installed packages remain on disk. Stop the billable box after user approval.
