#!/usr/bin/env bash
# Idempotently add a task card under a column of the Obsidian Kanban dashboard.
#
# Usage: dashboard-card.sh "<Task title>" ["<Column>"]
#   <Column> defaults to "In Progress".
# Inserts `- [ ] [[<Task title>]]` as the first card under "## <Column>".
# No-op if a card linking to this task already exists anywhere on the board
# (so it is safe to call on every run, and it never moves an existing card).
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

# Idempotency: bail if a wikilink to this task already exists on the board.
if grep -qF -- "[[$title]]" "$DASHBOARD"; then
    echo "exists: [[$title]] already on the board"
    exit 0
fi

card="- [ ] [[$title]]"
tmp="$(mktemp)"

# Insert the card as the first item under the target column heading, keeping the
# blank line the Kanban plugin writes between a heading and its cards.
awk -v col="## $column" -v card="$card" '
    armed && /^[[:space:]]*$/ { print; print card; armed = 0; next }
    armed                     { print card; armed = 0; print; next }
    { print }
    $0 == col { armed = 1 }
    END { if (armed) print card }
' "$DASHBOARD" > "$tmp"

if ! grep -qF -- "$card" "$tmp"; then
    rm -f "$tmp"
    echo "error: column \"$column\" not found in $DASHBOARD" >&2
    exit 1
fi

mv "$tmp" "$DASHBOARD"
echo "added: $card under \"$column\""
