#!/usr/bin/env bash
# Remove ALL mobile one-click wrappers/generated commands from the Finder folder.
# Nothing mobile is left to interfere while we run the ORIGINAL Appium tests.
# CMS run-kskin-cms-*.command files are left untouched.
#
# Run:
#   bash ~/AquaProjects/KskinCMS/one_click/purge_mobile_one_clicks.sh
set -euo pipefail

DEST=""
for d in \
  "$HOME/Desktop/One click bash files" \
  "$HOME/One click bash files" \
  "$HOME/Documents/One click bash files" \
  "$HOME/Desktop/One Click bash files"
do
  [[ -d "$d" ]] && DEST="$d" && break
done
DEST="${1:-${DEST:-$HOME/Desktop/One click bash files}}"

if [[ ! -d "$DEST" ]]; then
  echo "ERROR: folder not found: $DEST"
  exit 1
fi

BAK="$DEST/.purged_mobile_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BAK"

echo "Folder : $DEST"
echo "Backup : $BAK"
echo ""

moved=0
move_it() {
  local f="$1"
  [[ -e "$f" ]] || return 0
  mv -f "$f" "$BAK"/ 2>/dev/null || return 0
  echo "  moved: $(basename "$f")"
  moved=$((moved + 1))
}

# Mobile runners + every wrapper artifact we ever created
for pat in \
  'run-ios-*.command' \
  'run-android-*.command' \
  'run-e2e-*.command' \
  'run-mobile-*.command*' \
  'run-*.command.legacy' \
  'run-*.legacy' \
  'mobile_lib.sh' \
  'mobile_common.inc.sh' \
  'mobile_venv.sh' \
  'pace_startup.py' \
  'restore_appium_helpers.sh' \
  'generate_dynamic_data.py'
do
  while IFS= read -r -d '' f; do
    move_it "$f"
  done < <(find "$DEST" -maxdepth 1 -name "$pat" -print0 2>/dev/null)
done

# Wrapper support dirs
for d in "$DEST/python_path_first" "$DEST/.one_click_bin" "$DEST/.legacy"; do
  if [[ -e "$d" ]]; then
    mv -f "$d" "$BAK"/ 2>/dev/null || true
    echo "  moved dir: $(basename "$d")"
    moved=$((moved + 1))
  fi
done

echo ""
echo "Purged $moved mobile item(s) → $BAK"
echo ""
echo "Remaining .command files:"
ls -1 "$DEST"/*.command 2>/dev/null || echo "  (none)"
echo ""
echo "Next: run the ORIGINAL Appium test directly:"
echo "  bash ~/AquaProjects/KskinCMS/one_click/run_original_mobile_test.sh android-signup"
