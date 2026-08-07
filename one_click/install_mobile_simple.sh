#!/usr/bin/env bash
# Simple install: copy Claude-style self-contained mobile .command files to Desktop.
# No wrappers. No .legacy. Just the runners.
#
#   cd ~/AquaProjects/KskinCMS && bash one_click/install_mobile_simple.sh
set -euo pipefail

AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"
CMS=""
for c in "$AQUA/KskinCMS" "$AQUA/KskinCMS_SeleniumPython" "$AQUA/kskincms_seleniumpython"; do
  [[ -f "$c/one_click/run-android-signup-login.command" ]] && CMS="$c" && break
done
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
[[ -z "$CMS" ]] && CMS="$(cd "$SCRIPT_DIR/.." && pwd)"

DEST="${1:-}"
if [[ -z "$DEST" ]]; then
  for d in \
    "$HOME/Desktop/One click bash files" \
    "$HOME/One click bash files" \
    "$HOME/Documents/One click bash files"
  do
    [[ -d "$d" ]] && DEST="$d" && break
  done
fi
DEST="${DEST:-$HOME/Desktop/One click bash files}"
mkdir -p "$DEST"

echo "CMS : $CMS"
echo "DEST: $DEST"

# Refuse to install wrappers
if grep -q 'thin wrapper' "$CMS/one_click/run-android-full-regression.command"; then
  echo "ERROR: repo still has thin-wrapper mobile commands. Pull latest first." >&2
  exit 1
fi
if ! grep -q 'Claude-style, self-contained' "$CMS/one_click/run-android-full-regression.command"; then
  echo "ERROR: expected self-contained Claude-style runners. git pull first." >&2
  exit 1
fi

NAMES=(
  run-android-signup-login.command
  run-ios-signup-login.command
  run-android-full-regression.command
  run-ios-full-regression.command
  run-e2e-full-flow-android.command
  run-e2e-full-flow-ios.command
)

for name in "${NAMES[@]}"; do
  src="$CMS/one_click/$name"
  [[ -f "$src" ]] || { echo "skip $name"; continue; }
  cp -f "$src" "$DEST/$name"
  chmod +x "$DEST/$name"
  echo "Installed $name ($(wc -c < "$DEST/$name") bytes)"
done

# Also refresh CMS one-clicks if present
if [[ -f "$CMS/one_click/install_one_click_commands.sh" ]]; then
  # Copy CMS commands only (skip mobile wrapper section by copying cms files)
  cp -f "$CMS"/one_click/run-kskin-cms-*.command "$DEST/" 2>/dev/null || true
  chmod +x "$DEST"/run-kskin-cms-*.command 2>/dev/null || true
fi

echo ""
echo "OK. Double-click any of:"
printf '  %s\n' "${NAMES[@]}"
echo ""
echo "First line of full regression should say: Claude-style, self-contained"
head -2 "$DEST/run-android-full-regression.command"
