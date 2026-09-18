#!/usr/bin/env bash
set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NODE_VERSION="24.13.0"
PI_VERSION="0.84.4"

if [ ! -s "$HOME/.nvm/nvm.sh" ]; then
  curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
fi

export NVM_DIR="$HOME/.nvm"
. "$NVM_DIR/nvm.sh"
nvm install "$NODE_VERSION"
nvm alias default "$NODE_VERSION"
nvm use "$NODE_VERSION"
npm install -g --ignore-scripts "@earendil-works/pi-coding-agent@$PI_VERSION"

mkdir -p "$HOME/.local/bin" "$HOME/.pi/agent" "$HOME/.claude"
for executable in node npm npx pi; do
  ln -sfn "$(command -v "$executable")" "$HOME/.local/bin/$executable"
done

link_config() {
  local source="$1"
  local target="$2"
  mkdir -p "$(dirname "$target")"
  if [ -e "$target" ] && [ ! -L "$target" ]; then
    mv "$target" "$target.backup.$(date +%Y%m%d%H%M%S)"
  fi
  ln -sfn "$source" "$target"
}

link_config "$DOTFILES_DIR/claude/CLAUDE.md" "$HOME/.claude/CLAUDE.md"
link_config "$DOTFILES_DIR/claude/skills" "$HOME/.claude/skills"
link_config "$DOTFILES_DIR/claude/AGENTS.md" "$HOME/.pi/agent/AGENTS.md"
link_config "$DOTFILES_DIR/pi/settings.json" "$HOME/.pi/agent/settings.json"
link_config "$DOTFILES_DIR/pi/models.json" "$HOME/.pi/agent/models.json"
link_config "$DOTFILES_DIR/pi/extensions" "$HOME/.pi/agent/extensions"
link_config "$DOTFILES_DIR/pi/mcp.json" "$HOME/.pi/agent/mcp.json"
link_config "$DOTFILES_DIR/pi/mcp-servers" "$HOME/.pi/agent/mcp-servers"

if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
"$HOME/.local/bin/uv" tool install --force "browser-use==0.13.8"

npm --prefix "$DOTFILES_DIR/pi/mcp-servers/pagecast-patched" ci --omit=optional --ignore-scripts
pi --version
