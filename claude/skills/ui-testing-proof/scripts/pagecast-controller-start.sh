#!/usr/bin/env bash
set -euo pipefail

socket="${PAGECAST_CONTROLLER_SOCKET:-$HOME/.pi/agent/pagecast-controller.sock}"
pidfile="$socket.pid"
controller="$HOME/.pi/agent/tools/pagecast-controller.mjs"
log="$HOME/.pi/agent/pagecast-controller.log"

if [[ ! -f "$controller" ]]; then
  echo "Missing Pagecast controller: $controller" >&2
  exit 1
fi

if [[ -S "$socket" ]] && curl -fsS --unix-socket "$socket" http://localhost/health >/dev/null 2>&1; then
  curl -fsS --unix-socket "$socket" http://localhost/health
  echo
  exit 0
fi

if [[ -f "$pidfile" ]]; then
  old_pid="$(cat "$pidfile")"
  kill "$old_pid" 2>/dev/null || true
  sleep 1
fi
rm -f "$socket" "$pidfile"

nohup /opt/homebrew/bin/node "$controller" >"$log" 2>&1 &

for _ in $(seq 1 100); do
  if [[ -S "$socket" ]] && curl -fsS --unix-socket "$socket" http://localhost/health >/dev/null 2>&1; then
    curl -fsS --unix-socket "$socket" http://localhost/health
    echo
    exit 0
  fi
  sleep 0.2
done

echo "Pagecast controller failed to start. Log:" >&2
cat "$log" >&2 || true
exit 1
