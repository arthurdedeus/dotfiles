#!/usr/bin/env python3
"""Call the persistent local Pagecast MCP controller over its Unix socket.

Usage:
  pagecast-call.py --health
  pagecast-call.py record_page '{"url":"https://example.com","platform":"github"}'
  pagecast-call.py interact_page '{"sessionId":"abc123","actions":[...]}'
  pagecast-call.py stop_recording '{"sessionId":"abc123"}'
"""

from __future__ import annotations

import argparse
import http.client
import json
import os
import socket
import sys
from typing import Any


DEFAULT_SOCKET = os.path.expanduser("~/.pi/agent/pagecast-controller.sock")


class UnixHTTPConnection(http.client.HTTPConnection):
    def __init__(self, socket_path: str, timeout: float = 920.0) -> None:
        super().__init__("localhost", timeout=timeout)
        self.socket_path = socket_path

    def connect(self) -> None:
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect(self.socket_path)


def request(socket_path: str, method: str, path: str, payload: Any | None = None) -> Any:
    connection = UnixHTTPConnection(socket_path)
    body = None if payload is None else json.dumps(payload)
    headers = {} if body is None else {"Content-Type": "application/json"}
    connection.request(method, path, body=body, headers=headers)
    response = connection.getresponse()
    raw = response.read().decode("utf-8")
    connection.close()
    try:
        decoded = json.loads(raw)
    except json.JSONDecodeError:
        decoded = {"error": raw or f"HTTP {response.status}"}
    if response.status >= 400:
        raise RuntimeError(json.dumps(decoded, indent=2))
    return decoded


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tool", nargs="?", help="Pagecast MCP tool name")
    parser.add_argument("arguments", nargs="?", default="{}", help="JSON object passed to the tool")
    parser.add_argument("--socket", default=os.environ.get("PAGECAST_CONTROLLER_SOCKET", DEFAULT_SOCKET))
    parser.add_argument("--health", action="store_true")
    args = parser.parse_args()

    if not os.path.exists(args.socket):
        print(f"Pagecast controller socket not found: {args.socket}", file=sys.stderr)
        print("Run scripts/pagecast-controller-start.sh first.", file=sys.stderr)
        return 2

    try:
        if args.health:
            result = request(args.socket, "GET", "/health")
        else:
            if not args.tool:
                parser.error("tool is required unless --health is used")
            tool_args = json.loads(args.arguments)
            if not isinstance(tool_args, dict):
                raise ValueError("arguments must decode to a JSON object")
            result = request(args.socket, "POST", "/call", {"name": args.tool, "arguments": tool_args})
        print(json.dumps(result, indent=2))
        return 0 if not result.get("isError") and not result.get("error") else 1
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(f"pagecast-call failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
