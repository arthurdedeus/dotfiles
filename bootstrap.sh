#!/bin/bash

set -e

echo "Bootstrapping..."


BASE_DIR=$(dirname "${0}")
BIN_DIR="${HOME}/bin"
FONTS_DIR="${HOME}/Library/Fonts"
NVIM_CONFIG_DIR="${HOME}/.config/nvim"

source "${BASE_DIR}/utils.sh"

info "Utils sourced"

BREW_PACKAGES=(
  certifi
  coreutils
  curl
  gdal
  gh
  git
  gitui
  httpie
  node
  openssl
  openssl@1.1
  orbstack
  postgis
  postgresql
  pyenv
  python-certifi
  python-packaging
  sqlite
  tree-sitter
  wget
  yarn
  zsh
)

SYMLINKS=(
  # "${BASE_DIR}/git/gitattributes" "${HOME}/.gitattributes"
  # "${BASE_DIR}/git/gitconfig" "${HOME}/.gitconfig"
  # "${BASE_DIR}/git/gitignore" "${HOME}/.gitignore"
  # "${BASE_DIR}/nvim" "${HOME}/.config/nvim"
  # "${BASE_DIR}/zsh/zshrc" "${HOME}/.zshrc"
)

[ -d "${BASE_DIR}" ] || exit 1
mkdir -p "${BIN_DIR}"
mkdir -p "${FONTS_DIR}"

function _install_brew_packages {
  info "Installing brew packages"
  if ! which brew >/dev/null 2>&1; then
    info "Installing homebrew"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  fi

  brew install "${BREW_PACKAGES[@]}"
  brew update
  brew upgrade
  brew autoremove
  brew cleanup
}

function _create_symlinks {
  info "Creating symlinks"
  for FILE in "${SYMLINKS[@]}"; do
    create_symlink ${FILE}
  done
}

function _install_fonts {
  info "Installing fonts"

  download_file "${FONTS_DIR}/Hack Regular Nerd Font.ttf" \
    https://github.com/ryanoasis/nerd-fonts/blob/master/patched-fonts/Hack/Regular/HackNerdFont-Regular.ttf?raw=true

  download_file "${FONTS_DIR}/Hack Bold Nerd Font.ttf" \
    https://github.com/ryanoasis/nerd-fonts/blob/master/patched-fonts/Hack/Bold/HackNerdFont-Bold.ttf?raw=true

  download_file "${FONTS_DIR}/Hack Italic Nerd Font.ttf" \
    https://github.com/ryanoasis/nerd-fonts/blob/master/patched-fonts/Hack/Italic/HackNerdFont-Italic.ttf?raw=true
}

function _install_github_copilot {
  info "Installing GitHub Copilot"
  gh extension install github/gh-copilot
  gh extension upgrade --all
}

function _install_nvim {
  info "Installing neovim"
  brew install --HEAD neovim
  brew upgrade neovim --fetch-HEAD
  
  info "Installing vim-spell"
  if [ ! -f "${NVIM_CONFIG_DIR}/spell/.done" ]; then
    (
      mkdir -p "${NVIM_CONFIG_DIR}/spell"
      cd "${NVIM_CONFIG_DIR}/spell"
      wget -N -nv ftp://ftp.vim.org/pub/vim/runtime/spell/en.* --timeout=5 || exit 1
      wget -N -nv ftp://ftp.vim.org/pub/vim/runtime/spell/pt.* --timeout=5 || exit 1
      touch .done
    )
  fi
}

function _ {
  (
    cd "${HOME}"
    _install_brew_packages
    _create_symlinks
    _install_fonts
    _install_github_copilot
    _install_nvim
  )
}

echo
set -x
"_${1}" "$@"
