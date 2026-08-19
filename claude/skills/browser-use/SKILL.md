---
name: browser-use
description: Control a browser through CDP for interaction, scraping, testing, screenshots, and recordings.
---

# Browser Use

Use a direct fetch for public static content. Use a browser for interaction, JavaScript rendering, protected pages, or the user's signed-in session.

## Preflight

Check the command before planning around it:

```bash
command -v browser-use
browser-use --doctor
```

If the command is missing, use an available browser MCP or report the installation gap. Do not invent helper APIs.

For setup and connection problems, read:

`https://github.com/browser-use/browser-harness/blob/main/install.md`

## Basic use

```bash
browser-use <<'PY'
print(page_info())
PY
```

Helpers are pre-imported. Use `new_tab(url)` for the first navigation and `wait_for_load()` after navigation.

## Interaction workflow

1. Inspect `page_info()` and the accessibility tree.
2. Find elements by role, name, stable test attribute, or stable link.
3. Click through the accessibility node's box or a stable selector.
4. Verify the resulting URL, text, state, or request.
5. Use JavaScript for inspection when the accessibility tree is insufficient.
6. Use screenshots when layout or imagery matters.

Avoid generated classes, stale node IDs, and coordinate guesses without inspection.

## Authentication

Use an existing signed-in browser session when the account is unambiguous.

Stop for passwords, MFA, consent, personal data entry, or ambiguous account selection. Ask the user to complete those steps.

## Local Chrome

If Chrome asks for remote-debugging permission, ask the user to approve it once. Do not retry in a loop.

If the current tab is internal or stale, use `ensure_real_tab()` before acting.

## Remote browsers

Use an isolated remote browser for parallel tasks or when the user requests isolation. Get approval before starting a billable session.

Keep the selected daemon name in `BU_NAME`. Ask before leaving a remote browser running, then stop it when approved.

## Recordings

Record only when the user asks for a demo or proof.

1. Start recording before the real workflow.
2. Keep the exact returned recording path.
3. Perform and verify the workflow.
4. Stop recording before reporting.
5. Validate the final media.

Do not reenact completed work only to create proof.

## Safety

- Do not expose secrets or personal data in output or media.
- Do not perform destructive or production mutations without explicit approval.
- Close billable remote sessions after approval.
- Prefer repository or domain instructions over generic browser tactics.
