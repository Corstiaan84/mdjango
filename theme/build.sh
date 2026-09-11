#!/usr/bin/env bash
# Build the shipped stylesheets. No Tailwind, no node, no consumer build (docs/adr/0005) — the
# sources are concatenated in order and run through theme/bundle.py, which only strips comments
# and blank lines.
#
#   ./theme/build.sh          # one-shot build
#   ./theme/build.sh --watch  # rebuild whenever a source changes
#
# The compiled output IS committed: it is the artifact a consumer installs.
set -euo pipefail

here="$(cd "$(dirname "$0")/.." && pwd)"   # the mdjango project dir
cd "$here"

src="theme/src"
out="mdjango/static/mdjango"

# Order matters: faces, then the reset, then the house style. One flat sheet, no cascade layers,
# so a later rule beats an earlier one of equal specificity.
sources=("$src/fonts.css" "$src/reset.css" "$src/house.css")

build() {
  python3 theme/bundle.py "${sources[@]}" > "$out/mdjango.css"
  # The faces on their own, for a consumer styling its *own* pages (see the README).
  python3 theme/bundle.py "$src/fonts.css" > "$out/fonts.css"
}

if [[ "${1:-}" == "--watch" ]]; then
  echo "watching $src … (ctrl-c to stop)"
  last=""
  while true; do
    now="$(stat -c '%Y %n' "${sources[@]}" 2>/dev/null || true)"
    if [[ "$now" != "$last" ]]; then
      build
      echo "$(date +%H:%M:%S) rebuilt $out/mdjango.css"
      last="$now"
    fi
    sleep 1
  done
fi

build
echo "wrote $out/mdjango.css + fonts.css"
