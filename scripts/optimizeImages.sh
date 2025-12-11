#!/bin/bash

function main {
  local folder="$1"

  if [[ -z "$folder" || ! -d "$folder" ]]; then
    echo "Usage: $0 <folder>"
    exit 1
  fi

  shopt -s nullglob
  for filename in "$folder"/*.{jpg,jpeg,png,webp,JPG,JPEG,PNG,WEBP}; do
    convertImage "$filename"
  done
}

function convertImage {
  local -r input="$1"
  local -r name=${input%.*}
  local -r tmpImage="${name}_tmp.webp"
  local -r output="${name}.webp"
  local quality=85

  local -r COLOR='\033[1;35m'
  local -r NO_COLOR='\033[0m'
  local color="$NO_COLOR"

  magick "$input" "$tmpImage"
  magick "$tmpImage" -strip -quality ${quality}% "$output"

  size=$(wc -c <"$output")
  originalSize=$(wc -c <"$input")
  ratio=$((100 * size / originalSize))

  echo -e "${color}$input -> $output: quality ${quality}: $originalSize -> $size bytes (${ratio}%)"

  if [[ "$input" != "$output" ]]; then
    rm "$input"
  fi
  rm "$tmpImage"
}

main "$1"
