#!/usr/bin/env bash
# FORCE-install reconstructed mobile originals into Desktop one-click .legacy backups.
# Always run AFTER: git stash -u && git pull
# Or simply: bash one_click/fix_pep668_now.sh
set -euo pipefail

AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"
CMS=""
for c in "$AQUA/KskinCMS" "$AQUA/KskinCMS_SeleniumPython" "$AQUA/kskincms_seleniumpython"; do
  [[ -f "$c/one_click/mobile_venv.sh" ]] && CMS="$c" && break
  [[ -f "$c/one_click/originals/run-android-signup-login.command" ]] && CMS="$c" && break
done
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
[[ -z "$CMS" && -f "$SCRIPT_DIR/mobile_venv.sh" ]] && CMS="$(cd "$SCRIPT_DIR/.." && pwd)"

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

AND_SRC="$CMS/one_click/originals/run-android-full-regression.command"
if ! grep -q 'KSKIN_MOBILE_RUNNER_VENV' "$AND_SRC" 2>/dev/null; then
  echo "ERROR: full-regression original missing/old in repo." >&2
  echo "Run: cd \"$CMS\" && git stash -u && git pull" >&2
  exit 1
fi
if [[ ! -f "$CMS/one_click/mobile_venv.sh" ]]; then
  echo "ERROR: missing $CMS/one_click/mobile_venv.sh" >&2
  exit 1
fi

if [[ ! -f "$AQUA/MCP_Appium_Server/python/helpers/dynamic_data.py" ]]; then
  echo "Creating helpers/dynamic_data.py stub..."
  python3 "$CMS/one_click/generate_dynamic_data.py" || true
fi

bash "$CMS/one_click/install_one_click_commands.sh" "$DEST"

# Shared venv helper must sit next to Desktop pack (originals source it)
cp -f "$CMS/one_click/mobile_venv.sh" "$DEST/mobile_venv.sh"
chmod +x "$DEST/mobile_venv.sh"

install_one() {
  local name="$1"
  local src="$CMS/one_click/originals/$name"
  [[ -f "$src" ]] || { echo "skip missing $src"; return; }
  cp -f "$src" "$DEST/_originals/$name"
  cp -f "$src" "$DEST/.legacy/$name"
  cp -f "$src" "$DEST/${name}.legacy"
  chmod +x "$DEST/_originals/$name" "$DEST/.legacy/$name" "$DEST/${name}.legacy"
  echo "FORCE installed original: $name"
}

install_one "run-android-signup-login.command"
install_one "run-ios-signup-login.command"
install_one "run-android-full-regression.command"
install_one "run-ios-full-regression.command"
install_one "run-e2e-full-flow-android.command"
install_one "run-e2e-full-flow-ios.command"

echo ""
echo "Verify Android full regression (must show KSKIN_MOBILE_RUNNER_VENV):"
grep -E 'KSKIN_MOBILE_RUNNER_VENV|\.venv' "$DEST/.legacy/run-android-full-regression.command" | head -8

if grep -q 'KSKIN_MOBILE_RUNNER_VENV' "$DEST/.legacy/run-android-full-regression.command"; then
  echo "OK: Desktop .legacy full-regression is updated."
else
  echo "ERROR: Desktop .legacy full-regression still missing." >&2
  exit 1
fi

# Refresh thin wrappers from template
for name in \
  run-android-signup-login.command \
  run-ios-signup-login.command \
  run-android-full-regression.command \
  run-ios-full-regression.command \
  run-e2e-full-flow-android.command \
  run-e2e-full-flow-ios.command
do
  cp -f "$CMS/one_click/run-mobile-legacy-wrapper.command.template" "$DEST/$name"
  chmod +x "$DEST/$name"
done

echo ""
echo "Done. Try: run-android-full-regression.command"
echo "Header MUST show: KSKIN_MOBILE_RUNNER_VENV=android-full-regression"
echo "CMS line should NOT say NOT FOUND."
