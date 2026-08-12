# Local Pagecast setup

This machine uses a patched Pagecast build because the published npm `0.2.1` package does not contain the cursor-overlay implementation advertised by the repository, and the repository implementation originally lost its overlay after navigation.

## Installed components

- Patched source: `~/.pi/agent/tools/pagecast-patched`
- Patch branch: `local/cursor-reinjection`
- Patch commits:
  - `8a26c71` — re-inject overlay after navigation and redact sensitive typed values
  - `bf0ef9d` — explicitly position the DOM cursor for every target interaction
- Persistent MCP controller: `~/.pi/agent/tools/pagecast-controller.mjs`
- Controller socket: `~/.pi/agent/pagecast-controller.sock`
- Controller log: `~/.pi/agent/pagecast-controller.log`
- Recording output: `~/Desktop/Pagecast`
- Pi MCP config: `~/.pi/agent/mcp.json`
- Node: `/opt/homebrew/bin/node`
- ffmpeg/ffprobe: Homebrew binaries under `/opt/homebrew/bin`

The controller allows a local agent session that did not load Pagecast at startup to keep one Pagecast MCP process and authenticated browser context alive across shell calls.

## Start and call the controller

Resolve these paths relative to this skill directory:

```bash
./scripts/pagecast-controller-start.sh
./scripts/pagecast-call.py --health
```

Start a headed recording:

```bash
./scripts/pagecast-call.py record_page '{
  "url": "https://example.com",
  "platform": "github"
}'
```

Retain the exact session ID returned by `record_page`.

Interact:

```bash
./scripts/pagecast-call.py interact_page '{
  "sessionId": "SESSION_ID",
  "actions": [
    {"type": "waitForSelector", "selector": "button[data-testid=save]"},
    {"type": "hover", "selector": "button[data-testid=save]"},
    {"type": "click", "selector": "button[data-testid=save]"},
    {"type": "wait", "ms": 1500}
  ]
}'
```

Stop and finalize:

```bash
./scripts/pagecast-call.py stop_recording '{"sessionId":"SESSION_ID"}'
```

The controller allows up to 15 minutes for long finalization/export requests. Do not kill it while `stop_recording` is flushing a large WebM.

## Direct MCP usage

In a new Pi session, Pagecast can be discovered through the generic `mcp` proxy. Search for `pagecast record`, connect the `pagecast` server, then call the discovered Pagecast tools. Keep `directTools: false` to avoid placing every schema in context.

## Authentication limitation

Pagecast creates an isolated Playwright browser context. It does not share Browser Use's Chrome cookies.

For protected apps:

1. Call `record_page` on the protected URL.
2. Ask the user to complete SSO/password/MFA manually in the visible Pagecast window.
3. Keep the same Pagecast `sessionId` alive.
4. Perform the test scenario.
5. Trim the authentication portion during export if needed.

Stopping the recording closes that context and discards its session cookies. A subsequent recording requires authentication again.

Never automate personal passwords, MFA, consent, or ambiguous account selection. Test credentials may be entered only when the user has authorized their use. The patched recorder redacts password/secret fields from MCP output and timeline JSON, but the browser video can still contain visible email addresses and other account data.

## Cursor behavior

Playwright video does not capture the native OS pointer. Pagecast supplies a red DOM cursor and click ripple. The local patch:

- Re-injects the overlay after `DOMContentLoaded` and before every action.
- Restores the cursor if an SPA replaces body contents.
- Explicitly sets cursor coordinates from each target bounding box.
- Uses the maximum practical z-index and Pagecast's overlay styling.

The patch was validated after a hard navigation on a page that blocked synthetic `mousemove`; the final frame contained the expected red cursor at the target.

If a video has no cursor:

1. Confirm MCP is using `~/.pi/agent/tools/pagecast-patched/src/index.js`, not `/opt/homebrew/bin/pagecast` or `npx @mcpware/pagecast@0.2.1`.
2. Confirm interactions went through `interact_page`; manual user movement is not represented by Pagecast's synthetic cursor.
3. Confirm the interaction had a selector/bounding box, or use coordinate hover before an action.
4. Validate the finalized video, not an unflushed live `page@*.webm` copy.

## Artifact delivery

PostHog's `upload_artifact` tool is enabled only for cloud task runs with task and run IDs. When available:

- Copy deliverables into the session workspace.
- Keep each file under 30 MB.
- Upload MP4 with `video/mp4`, GIF with `image/gif`, PNG with `image/png`.
- Reference the returned artifact URL.

In local scratch sessions, artifact upload is unavailable. Do not pretend a local Markdown path is downloadable. State the limitation and open/copy the local file only if the user asks.
