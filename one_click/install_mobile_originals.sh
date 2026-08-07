#!/usr/bin/env bash
# Install reconstructed ORIGINAL mobile runners as .legacy backups, then refresh wrappers.
# Use when recover_mobile_legacy.sh says all backups are WRAPPER.
set -euo pipefail

AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"
CMS=""
for c in "$AQUA/KskinCMS" "$AQUA/KskinCMS_SeleniumPython" "$AQUA/kskincms_seleniumpython"; do
  [[ -f "$c/one_click/originals/run-android-signup-login.command" ]] && CMS="$c" && break
done
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
[[ -z "$CMS" && -f "$SCRIPT_DIR/originals/run-android-signup-login.command" ]] && CMS="$(cd "$SCRIPT_DIR/.." && pwd)"

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
mkdir -p "$DEST/.legacy" "$DEST/_originals"

echo "CMS : $CMS"
echo "DEST: $DEST"

# Ensure dynamic_data exists
if [[ ! -f "$AQUA/MCP_Appium_Server/python/helpers/dynamic_data.py" ]]; then
  echo "Creating helpers/dynamic_data.py stub..."
  python3 "$CMS/one_click/generate_dynamic_data.py" || true
fi

install_one() {
  local name="$1"
  local src="$CMS/one_click/originals/$name"
  [[ -f "$src" ]] || { echo "skip missing $src"; return; }
  cp -f "$src" "$DEST/_originals/$name"
  cp -f "$src" "$DEST/.legacy/$name"
  cp -f "$src" "$DEST/${name}.legacy"
  chmod +x "$DEST/_originals/$name" "$DEST/.legacy/$name" "$DEST/${name}.legacy"
  echo "Installed original backup: $name"
}

install_one "run-android-signup-login.command"
install_one "run-ios-signup-login.command"

# Refresh thin wrappers on top
bash "$CMS/one_click/install_one_click_commands.sh" "$DEST"

echo ""
echo "Done. Double-click run-android-signup-login.command"
echo "It should now call the reconstructed original under .legacy/"
