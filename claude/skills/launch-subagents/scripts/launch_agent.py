#!/usr/bin/env python3

import argparse
import json
import os
import re
import signal
import subprocess
import threading
import time
import uuid
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch a Pi subagent with RPC progress telemetry.")
    parser.add_argument("--name", required=True)
    parser.add_argument("--prompt-file", required=True, type=Path)
    parser.add_argument("--model", default="gpt-5.6-terra")
    parser.add_argument("--provider", default="openai-codex")
    parser.add_argument("--thinking", default="high")
    parser.add_argument("--tools", default="bash")
    parser.add_argument("--status-dir", type=Path, default=Path("/tmp/pi-subagents"))
    parser.add_argument("--stats-interval", type=int, default=30)
    parser.add_argument("--idle-warning", type=int, default=180)
    parser.add_argument("--cwd", type=Path, default=Path("/tmp"))
    parser.add_argument("--run-id", default=os.environ.get("PI_SUBAGENT_RUN_ID") or uuid.uuid4().hex)
    parser.add_argument("--parent-session-id", default=os.environ.get("PI_SESSION_ID"))
    parser.add_argument("--parent-session-file", default=os.environ.get("PI_SESSION_FILE"))
    parser.add_argument("--task-summary")
    return parser.parse_args()


def safe_file_component(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip(".-") or "agent"


args = parse_args()
args.status_dir.mkdir(parents=True, exist_ok=True)

file_prefix = f"{safe_file_component(args.name)}-{safe_file_component(args.run_id)}"
status_path = args.status_dir / f"{file_prefix}.status.json"
raw_log_path = args.status_dir / f"{file_prefix}.rpc.jsonl"
stderr_path = args.status_dir / f"{file_prefix}.stderr.log"
final_path = args.status_dir / f"{file_prefix}.final.txt"
prompt = args.prompt_file.read_text()

state: dict[str, Any] = {
    "name": args.name,
    "runId": args.run_id,
    "parentSessionId": args.parent_session_id,
    "parentSessionFile": args.parent_session_file,
    "taskSummary": args.task_summary or args.name,
    "state": "starting",
    "model": args.model,
    "thinking": args.thinking,
    "controllerPid": os.getpid(),
    "agentPid": None,
    "startedAt": time.time(),
    "heartbeatAt": time.time(),
    "lastProgressAt": time.time(),
    "stalled": False,
    "currentTool": None,
    "toolCalls": 0,
    "lastToolError": False,
    "tokens": None,
    "contextUsage": None,
    "lastText": None,
    "exitCode": None,
}
state_lock = threading.Lock()
stdin_lock = threading.Lock()
settled = threading.Event()
last_token_total = 0
session_stats_received = False


def write_state() -> None:
    with state_lock:
        snapshot = dict(state)
        snapshot["heartbeatAt"] = time.time()
        snapshot["progressAgeSeconds"] = round(snapshot["heartbeatAt"] - snapshot["lastProgressAt"], 1)
        snapshot["stalled"] = (
            snapshot["state"] in {"starting", "prompted", "running"}
            and snapshot["progressAgeSeconds"] >= args.idle_warning
        )
        state.update(snapshot)
    temp_path = status_path.with_suffix(".tmp")
    temp_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True))
    temp_path.replace(status_path)


def update(*, progress: bool = False, **values: Any) -> None:
    with state_lock:
        state.update(values)
        if progress:
            state["lastProgressAt"] = time.time()
    write_state()


stderr_file = stderr_path.open("w")
raw_log = raw_log_path.open("w")
proc = subprocess.Popen(
    [
        "pi",
        "--mode",
        "rpc",
        "--provider",
        args.provider,
        "--model",
        args.model,
        "--thinking",
        args.thinking,
        "--no-session",
        "--no-extensions",
        "--no-skills",
        "--no-context-files",
        "--tools",
        args.tools,
    ],
    cwd=args.cwd,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=stderr_file,
    text=True,
    bufsize=1,
)
assert proc.stdin is not None
assert proc.stdout is not None
update(agentPid=proc.pid)


def send(payload: dict[str, Any]) -> None:
    with stdin_lock:
        proc.stdin.write(json.dumps(payload) + "\n")
        proc.stdin.flush()


def token_total(tokens: Any) -> int:
    if not isinstance(tokens, dict):
        return 0
    for key in ("total", "totalTokens"):
        if isinstance(tokens.get(key), int):
            return tokens[key]
    return sum(tokens.get(key, 0) or 0 for key in ("input", "output", "cacheRead", "cacheWrite"))


def reader() -> None:
    global last_token_total, session_stats_received
    try:
        for line in proc.stdout:
            raw_log.write(line)
            raw_log.flush()
            event = json.loads(line)
            event_type = event.get("type")

            if event_type == "agent_start":
                update(state="running", progress=True)
            elif event_type == "tool_execution_start":
                update(
                    state="running",
                    currentTool=event.get("toolName"),
                    toolCalls=int(state.get("toolCalls") or 0) + 1,
                    progress=True,
                )
            elif event_type == "tool_execution_update":
                update(currentTool=event.get("toolName"), progress=True)
            elif event_type == "tool_execution_end":
                update(currentTool=None, lastToolError=bool(event.get("isError")), progress=True)
            elif event_type == "message_update":
                usage = event.get("usage")
                total = token_total(usage)
                if total > 0 and not session_stats_received:
                    update(tokens=usage, progress=total > last_token_total)
                    last_token_total = max(last_token_total, total)
            elif event_type == "message_end" and event.get("message", {}).get("role") == "assistant":
                message = event.get("message", {})
                usage = message.get("usage")
                total = token_total(usage)
                if total > 0 and not session_stats_received:
                    update(tokens=usage, progress=total > last_token_total)
                    last_token_total = max(last_token_total, total)
                content = message.get("content", [])
                texts = [part.get("text") for part in content if part.get("type") == "text" and part.get("text")]
                if texts:
                    text = "\n".join(texts)
                    final_path.write_text(text)
                    update(lastText=text[-4000:], progress=True)
            elif event_type == "response" and event.get("command") == "get_session_stats" and event.get("success"):
                data = event.get("data") or {}
                tokens = data.get("tokens")
                total = token_total(tokens)
                if total > 0:
                    session_stats_received = True
                    update(tokens=tokens, contextUsage=data.get("contextUsage"), progress=total > last_token_total)
                    last_token_total = max(last_token_total, total)
            elif event_type == "extension_ui_request":
                request_id = event.get("id")
                if request_id:
                    send({"type": "extension_ui_response", "id": request_id, "cancelled": True})
                update(blockedDialog=event.get("method"), progress=True)
            elif event_type == "agent_settled":
                update(state="settled", currentTool=None, progress=True)
                settled.set()
    except Exception as error:
        update(state="reader_failed", readerError=str(error))
        settled.set()
    finally:
        settled.set()


def stop_agent(_signum: int, _frame: Any) -> None:
    update(state="stopping")
    if proc.poll() is None:
        proc.terminate()
    settled.set()


signal.signal(signal.SIGTERM, stop_agent)
signal.signal(signal.SIGINT, stop_agent)
threading.Thread(target=reader, daemon=True).start()
send({"id": "prompt", "type": "prompt", "message": prompt})
update(state="prompted", progress=True)

stats_counter = 0
while not settled.wait(args.stats_interval):
    stats_counter += 1
    try:
        send({"id": f"stats-{stats_counter}", "type": "get_session_stats"})
    except BrokenPipeError:
        break
    write_state()

if proc.poll() is None:
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)

final_state = "completed" if proc.returncode == 0 else "failed"
update(state=final_state, exitCode=proc.returncode, currentTool=None)
raw_log.close()
stderr_file.close()
