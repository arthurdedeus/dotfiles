#!/bin/bash

if [ "${_DEFAULTS_SOURCED}" = "1" ]; then
  return
fi

export LANG="en_US.UTF-8"
export DOTFILES_DIR="${HOME}/.dotfiles"

if [ -d "/opt/homebrew/bin" ]; then
  export PATH=/opt/homebrew/bin:${PATH}
fi

if [ -d "/opt/homebrew/sbin" ]; then
  export PATH=/opt/homebrew/sbin:${PATH}
fi

if [ -d "${HOME}/.local/bin" ]; then
  export PATH=${HOME}/.local/bin:${PATH}
fi

if [ -d "${HOME}/.bin" ]; then
  export PATH=${HOME}/.bin:${PATH}
fi


function bootstrap() { (
  set -e
  cd "${DOTFILES_DIR}"
  git pull origin main || true
  bash "${DOTFILES_DIR}/bootstrap.sh" "${@}" || return 1 
}

export _DEFAULTS_SOURCED="1"
