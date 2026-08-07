#!/usr/bin/env bash
# FORCE-install reconstructed mobile originals into Desktop one-click .legacy backups.
# Always run AFTER: git stash -u && git pull
# Or simply: bash one_click/fix_pep668_now.sh
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

# Abort if repo originals are still the old non-venv runner
AND_SRC="$CMS/one_click/originals/run-android-signup-login.command"
if ! grep -q 'KSKIN_MOBILE_RUNNER_VENV' "$AND_SRC"; then
  echo "ERROR: $AND_SRC is not the venv-based runner yet." >&2
  echo "Run: cd \"$CMS\" && git stash -u && git pull" >&2
  echo "Or:  bash \"$CMS/one_click/fix_pep668_now.sh\"" >&2
  exit 1
fi

# Ensure dynamic_data exists
if [[ ! -f "$AQUA/MCP_Appium_Server/python/helpers/dynamic_data.py" ]]; then
  echo "Creating helpers/dynamic_data.py stub..."
  python3 "$CMS/one_click/generate_dynamic_data.py" || true
fi

# Refresh wrappers first (may try to "keep" old backups)
bash "$CMS/one_click/install_one_click_commands.sh" "$DEST"

# FORCE originals LAST so they win over any "Kept good backup" logic
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

echo ""
echo "Verify (must show KSKIN_MOBILE_RUNNER_VENV + .venv):"
grep -E 'KSKIN_MOBILE_RUNNER_VENV|\.venv' "$DEST/.legacy/run-android-signup-login.command" | head -10

if grep -q 'KSKIN_MOBILE_RUNNER_VENV' "$DEST/.legacy/run-android-signup-login.command"; then
  echo "OK: Desktop .legacy is updated (venv-based)."
else
  echo "ERROR: Desktop .legacy still old — stop and check paths." >&2
  exit 1
fi

# Confirm wrapper prefers CMS originals
if grep -q 'Prefer CMS repo venv' "$DEST/run-android-signup-login.command" \
  || grep -q 'has_venv_runner' "$DEST/run-android-signup-login.command"; then
  echo "OK: Desktop wrapper prefers CMS venv runner (won't stick on stale .legacy)."
else
  echo "WARNING: wrapper may be stale — re-copy template."
  cp -f "$CMS/one_click/run-mobile-legacy-wrapper.command.template" \
    "$DEST/run-android-signup-login.command"
  cp -f "$CMS/one_click/run-mobile-legacy-wrapper.command.template" \
    "$DEST/run-ios-signup-login.command"
  chmod +x "$DEST/run-android-signup-login.command" "$DEST/run-ios-signup-login.command"
fi

echo ""
echo "Done. Double-click run-android-signup-login.command"
echo "Header MUST show: KSKIN_MOBILE_RUNNER_VENV=android-signup"
echo "Using Python: .../MCP_Appium_Server/python/.venv/bin/python"
echo "First run may create the venv and pip install (can take a minute)."
