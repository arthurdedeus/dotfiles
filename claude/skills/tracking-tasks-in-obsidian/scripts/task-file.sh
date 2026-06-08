#!/usr/bin/env bash
# Find an existing task-tracking note by title, or print where a new one would go.
#
# Usage: task-file.sh "<Task title>" ["<PARA folder>"]
#   <PARA folder> defaults to "1 Projects".
# Output (tab-separated): <found|new>\t<absolute path>
#
# The title doubles as the filename AND the [[wikilink]] used on the dashboard,
# so keep it identical everywhere.
set -euo pipefail

# Root that holds the PARA folders (1 Projects, 2 Areas, 3 Resources, 4 Archives).
VAULT_DIR="${OBSIDIAN_VAULT_DIR:-$HOME/Documents/obsidian/PostHog}"

title="${1:-}"
para_folder="${2:-1 Projects}"

if [[ -z "$title" ]]; then
    echo "error: task title required" >&2
    exit 1
fi
if [[ ! -d "$VAULT_DIR" ]]; then
    echo "error: vault not found at $VAULT_DIR (set OBSIDIAN_VAULT_DIR to override)" >&2
    exit 1
fi

# Reuse an existing note with this exact filename anywhere in the vault, so we
# update rather than duplicate.
matches="$(find "$VAULT_DIR" -type f -iname "${title}.md" 2>/dev/null | sort)"
count="$(printf '%s' "$matches" | grep -c . || true)"

if [[ "$count" -gt 1 ]]; then
    {
        echo "warning: ${count} notes named \"${title}.md\" exist — [[${title}]] is ambiguous in Obsidian. Pick one and consolidate:"
        printf '%s\n' "$matches" | sed 's/^/  - /'
    } >&2
fi

if [[ "$count" -ge 1 ]]; then
    printf 'found\t%s\n' "$(printf '%s\n' "$matches" | head -n 1)"
    exit 0
fi

printf 'new\t%s\n' "$VAULT_DIR/$para_folder/$title.md"
