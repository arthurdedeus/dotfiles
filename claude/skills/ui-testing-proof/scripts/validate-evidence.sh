#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: validate-evidence.sh <media-file>" >&2
  exit 2
fi

file_path="$1"
if [[ ! -f "$file_path" ]]; then
  echo "Missing evidence file: $file_path" >&2
  exit 1
fi
if [[ ! -s "$file_path" ]]; then
  echo "Evidence file is empty: $file_path" >&2
  exit 1
fi

mime="$(file --brief --mime-type "$file_path")"
bytes="$(stat -f '%z' "$file_path" 2>/dev/null || stat -c '%s' "$file_path")"
echo "path=$file_path"
echo "mime=$mime"
echo "bytes=$bytes"

case "$mime" in
  video/*)
    ffprobe -v error \
      -show_entries format=duration,size:stream=codec_name,width,height,avg_frame_rate \
      -of json "$file_path"
    ;;
  image/*)
    if command -v magick >/dev/null 2>&1; then
      magick identify "$file_path"
    else
      sips -g pixelWidth -g pixelHeight "$file_path" 2>/dev/null || true
    fi
    ;;
  *)
    echo "warning=unrecognized media MIME type" >&2
    ;;
esac
