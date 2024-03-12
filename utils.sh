#!/bin/bash

function info {
  set +x
  echo
  echo "=== ${1} ==="
  echo
  set -x
}

function download_file {
  set +x
  DEST=${1}
  URL=${2}
  set -x

  TMP=$(mktemp)
  curl -4 -sSL -o "${TMP}" "${URL}"

  if [ -f "${DEST}" ]; then
    OLD_MD5=$(md5sum "${DEST}" | cut -d ' ' -f 1)
    NEW_MD5=$(md5sum "${TMP}" | cut -d ' ' -f 1)
    if [ "${OLD_MD5}" != "${NEW_MD5}" ]; then
      TMP2=$(mktemp)
      mv "${DEST}" "${TMP2}"
    fi
  fi

  mv "${TMP}" "${DEST}"
}

function create_symlink {
  set +x
  SOURCE_FILE=${1}
  DEST_FILE=${2}

  if [ "$(readlink -f "$DEST_FILE")" != "$SOURCE_FILE" ]; then
    debug "updating symlink ${DEST_FILE} -> ${SOURCE_FILE}"
    ln -f -s "$SOURCE_FILE" "$DEST_FILE"
  fi
  set -x
}
