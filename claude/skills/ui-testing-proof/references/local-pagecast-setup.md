# Local Pagecast setup

Use the installed patched Pagecast build. Do not replace it with the published package without revalidating cursor and redaction behavior.

## Installed paths

- Source: `~/.pi/agent/tools/pagecast-patched`
- Controller: `~/.pi/agent/tools/pagecast-controller.mjs`
- Socket: `~/.pi/agent/pagecast-controller.sock`
- Log: `~/.pi/agent/pagecast-controller.log`
- Output: `~/Desktop/Pagecast`
- Pi MCP config: `~/.pi/agent/mcp.json`

The patch restores the visible cursor after navigation and redacts sensitive typed values from tool output and timelines.

## Controller

From the skill directory:

```bash
./scripts/pagecast-controller-start.sh
./scripts/pagecast-call.py --health
```

Use `record_page`, `interact_page`, and `stop_recording` through `pagecast-call.py`. Keep the exact session ID.

Do not kill the controller while a recording is finalizing.

## Direct MCP

When Pagecast is configured in the current Pi session, discover and call it through the generic MCP proxy.

Keep Pagecast tools deferred instead of loading every schema into context.

## Authentication

Pagecast uses an isolated browser context and does not share local Chrome cookies.

1. Open the protected page in Pagecast.
2. Ask the user to complete protected authentication.
3. Keep the same session alive.
4. Trim authentication from final media when needed.

Stopping the recording closes the browser context.

Never automate personal passwords, MFA, consent, or ambiguous account selection. Video may still contain visible account data.

## Cursor checks

Pagecast records a DOM cursor, not the native OS pointer.

If the cursor is missing:

1. Confirm MCP uses the patched source path.
2. Confirm actions ran through `interact_page`.
3. Confirm each target had a selector or bounding box.
4. Inspect finalized media, not a growing WebM file.

## Artifact delivery

Cloud tasks may provide `upload_artifact`. Copy files into the session workspace and use the correct MIME type.

Local scratch sessions may not support upload. In that case, report the local path and do not imply it is downloadable.
