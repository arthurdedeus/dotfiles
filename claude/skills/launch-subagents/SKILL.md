---
name: launch-subagents
description: Launch Pi coding subagents with RPC telemetry, isolated prompts, model selection, and non-blocking status files. Use when parallelizing implementation or review work across Luna and Terra agents.
---

# Launch subagents

Use the bundled launcher instead of detached `pi --print`. RPC mode exposes token usage, active tools, progress timestamps, and completion without blocking the main loop.

## Choose a model

- **Luna:** foundational, cross-cutting, or ambiguous work.
- **Terra:** bounded implementation, review, test, or integration work.

Use full model IDs: `gpt-5.6-luna` or `gpt-5.6-terra` with provider `openai-codex`.

## Prepare the prompt

Keep each agent's ownership narrow. Include:

- Exact repository or worktree path.
- Exact SSH command when work must stay remote.
- Files the agent owns and must not touch.
- Required skills and tests.
- Commit and push rules.
- Expected final report.

For devbox work, write the exact host. Do not say only “Golden” or another nickname.

## Launch

```bash
skill="$HOME/.dotfiles/claude/skills/launch-subagents"
name=backend-task

nohup python3 "$skill/scripts/launch_agent.py" \
  --name "$name" \
  --model gpt-5.6-luna \
  --thinking high \
  --prompt-file /tmp/backend-task.prompt \
  --task-summary "Write skill text" \
  --tools bash \
  > "/tmp/pi-subagents/$name.controller.log" 2>&1 &
```

The launcher writes files named `<name>-<run-id>`:

- `.status.json` - state, task summary, parent session, tokens, context, active tool, and progress age.
- `.rpc.jsonl` - raw RPC events.
- `.stderr.log` - Pi startup and provider errors.
- `.final.txt` - final assistant report.

The launcher reads `PI_SESSION_ID` and `PI_SESSION_FILE` from the parent process. Pass `--parent-session-id` and `--parent-session-file` only when launching outside Pi. Use `--task-summary` for the monitor label. It stores the summary, not the prompt.

Check progress without waiting:

```bash
jq . /tmp/pi-subagents/backend-task-<run-id>.status.json
```

A completed agent reports `state: completed`. A nonzero exit reports `state: failed`. `stalled: true` means token and tool progress have not changed within the warning window.

## Gotchas

- `pi --print` buffers progress. Use this RPC launcher when the main loop needs visibility.
- Subagents cannot push messages into the parent conversation. Poll the status file briefly at natural checkpoints.
- Restrict remote-development agents to `bash` and put the exact SSH command in the prompt. Otherwise they may touch the local checkout or guess the wrong host.
- Worktrees can duplicate Flox, Go, Rust, and package caches. Avoid backend Flox setup in every worktree. Remove clean integrated worktrees promptly.
- Go module caches may contain read-only files. Before removing an abandoned worktree cache, run `chmod -R u+w <worktree>/.flox`.
- If a devbox fills up, inspect disk usage before deleting anything. Safe generated candidates include stale Rust targets and unused Docker images.
- Approval-gated MCP tools need an interactive RPC UI. This launcher cancels extension dialogs by default, so use it for coding tools such as `bash`, not mutations that need explicit approval.
- Parallel agents should not own the same integration files. Land shared foundations first, then branch dependent agents from that commit.
