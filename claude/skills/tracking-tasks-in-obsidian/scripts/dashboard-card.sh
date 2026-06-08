#!/usr/bin/env bash
# Ensure a task card sits under a given column of the Obsidian Kanban dashboard.
#
# Usage: dashboard-card.sh "<Task title>" ["<Column>"]
#   <Column> defaults to "In Progress".
#
# Idempotent — pass the column that matches the task's current state:
#   - card absent            -> adds `- [ ] [[<Task title>]]` under <Column>
#   - card in another column -> moves the existing card line (verbatim) to <Column>
#   - card already in <Column> -> no-op
set -euo pipefail

VAULT_DIR="${OBSIDIAN_VAULT_DIR:-$HOME/Documents/obsidian/PostHog}"
DASHBOARD="$VAULT_DIR/Dashboard.md"

title="${1:-}"
column="${2:-In Progress}"

if [[ -z "$title" ]]; then
    echo "error: task title required" >&2
    exit 1
fi
if [[ ! -f "$DASHBOARD" ]]; then
    echo "error: dashboard not found at $DASHBOARD" >&2
    exit 1
fi
# Fail before mutating if the target column doesn't exist, so a move never drops
# the card without re-inserting it.
if ! grep -qxF -- "## $column" "$DASHBOARD"; then
    echo "error: column \"$column\" not found in $DASHBOARD" >&2
    exit 1
fi

needle="[[$title]]"

# Which column (if any) currently holds the card?
current_col="$(awk -v needle="$needle" '
    index($0, "## ") == 1 { c = substr($0, 4) }
    index($0, needle) > 0 { print c; exit }
' "$DASHBOARD")"

if [[ "$current_col" == "$column" ]]; then
    echo "ok: [[$title]] already in \"$column\""
    exit 0
fi

# Preserve the existing card line verbatim (keeps any trailing text / checkbox
# state); fall back to a fresh unchecked card when adding for the first time.
card_line="$(grep -m1 -F -- "$needle" "$DASHBOARD" || true)"
[[ -n "$card_line" ]] || card_line="- [ ] $needle"

tmp="$(mktemp)"
awk -v col="## $column" -v card="$card_line" -v had="${current_col:+1}" '
    # Drop the existing card line from its old column (first match only).
    had && !dropped && $0 == card { dropped = 1; next }
    # Insert under the target column as the first card, after the blank line the
    # Kanban plugin leaves between a heading and its cards.
    armed && /^[[:space:]]*$/ { print; print card; armed = 0; next }
    armed                     { print card; armed = 0; print; next }
    { print }
    $0 == col { armed = 1 }
    END { if (armed) print card }
' "$DASHBOARD" > "$tmp"

if ! grep -qF -- "$card_line" "$tmp"; then
    rm -f "$tmp"
    echo "error: failed to place card under \"$column\"" >&2
    exit 1
fi

mv "$tmp" "$DASHBOARD"
if [[ -n "$current_col" ]]; then
    echo "moved: [[$title]] \"$current_col\" -> \"$column\""
else
    echo "added: $card_line under \"$column\""
fi
