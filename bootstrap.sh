#!/usr/bin/env bash
set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Symlink map (source:target) ─────────────────────────────────────────────
SYMLINKS=(
  # git
  "git/ignore:$HOME/.config/git/ignore"

  # claude
  "claude/CLAUDE.md:$HOME/.claude/CLAUDE.md"
  "claude/disagreement-and-calibration.md:$HOME/.claude/disagreement-and-calibration.md"
  "claude/settings.json:$HOME/.claude/settings.json"
  "claude/skills:$HOME/.claude/skills"
  "claude/knowledge:$HOME/.claude/knowledge"
  "claude/agents:$HOME/.claude/agents"
  "claude/plans:$HOME/.claude/plans"

  # zed
  "zed/settings.json:$HOME/.config/zed/settings.json"

  # gh
  "gh/config.yml:$HOME/.config/gh/config.yml"

  # direnv
  "direnv/direnv.toml:$HOME/.config/direnv/direnv.toml"
)

# ── Helpers ──────────────────────────────────────────────────────────────────
info()  { printf "\033[1;34m▸\033[0m %s\n" "$1"; }
ok()    { printf "\033[1;32m✓\033[0m %s\n" "$1"; }
warn()  { printf "\033[1;33m!\033[0m %s\n" "$1"; }
error() { printf "\033[1;31m✗\033[0m %s\n" "$1"; }

link_file() {
  local src="$1" dst="$2"
  mkdir -p "$(dirname "$dst")"

  if [ -L "$dst" ]; then
    local current_target
    current_target="$(readlink "$dst")"
    if [ "$current_target" = "$src" ]; then
      return 0
    fi
    rm "$dst"
  elif [ -e "$dst" ]; then
    local action="${LINK_ACTION:-}"
    if [ -z "$action" ]; then
      warn "$dst already exists"
      printf "  [s]kip, [o]verwrite, [b]ackup, [S]kip all, [O]verwrite all, [B]ackup all? "
      read -r action </dev/tty
    fi
    case "$action" in
      o|O) [ "$action" = "O" ] && export LINK_ACTION="o"; rm -rf "$dst" ;;
      b|B) [ "$action" = "B" ] && export LINK_ACTION="b"; mv "$dst" "$dst.backup"; warn "backed up $dst → $dst.backup" ;;
      s|S) [ "$action" = "S" ] && export LINK_ACTION="s"; warn "skipped $dst"; return 0 ;;
      *)   warn "skipped $dst"; return 0 ;;
    esac
  fi

  ln -s "$src" "$dst"
  ok "linked $dst → $src"
}

# ── 1. Homebrew ──────────────────────────────────────────────────────────────
if ! command -v brew &>/dev/null; then
  info "Installing Homebrew…"
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  eval "$(/opt/homebrew/bin/brew shellenv)"
else
  ok "Homebrew already installed"
fi

# ── 2. Brewfile ──────────────────────────────────────────────────────────────
info "Installing packages from Brewfile…"
brew bundle --file="$DOTFILES_DIR/Brewfile" || warn "Some Brewfile dependencies failed (may need sudo). Continuing…"

# ── 3. Symlinks ──────────────────────────────────────────────────────────────
info "Creating symlinks…"
for entry in "${SYMLINKS[@]}"; do
  src="$DOTFILES_DIR/${entry%%:*}"
  dst="${entry#*:}"
  link_file "$src" "$dst"
done

echo ""
ok "All done! Open a new terminal to pick up changes."
