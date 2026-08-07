#!/usr/bin/env bash
# Install / refresh all one-click .command files into your Mac "One click bash files" folder.
# Run on your Mac Terminal (not cloud):
#   bash ~/AquaProjects/KskinCMS/one_click/install_one_click_commands.sh
set -euo pipefail

AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"
CMS=""
for c in "$AQUA/KskinCMS" "$AQUA/KskinCMS_SeleniumPython" "$AQUA/kskincms_seleniumpython"; do
  if [[ -f "$c/scripts/one_click_lib.sh" ]]; then CMS="$c"; break; fi
done
# Allow running from inside the repo
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [[ -z "$CMS" && -f "$SCRIPT_DIR/../scripts/one_click_lib.sh" ]]; then
  CMS="$(cd "$SCRIPT_DIR/.." && pwd)"
fi
if [[ -z "$CMS" ]]; then
  echo "ERROR: KskinCMS repo with one_click pack not found." >&2
  echo "cd to the repo and run: bash one_click/install_one_click_commands.sh" >&2
  exit 1
fi

# Destination: prefer existing Finder folder, else Desktop
DEST=""
for d in \
  "$HOME/Desktop/One click bash files" \
  "$HOME/One click bash files" \
  "$HOME/Documents/One click bash files" \
  "$HOME/Desktop/One Click bash files"
do
  if [[ -d "$d" ]]; then DEST="$d"; break; fi
done
DEST="${1:-${DEST:-$HOME/Desktop/One click bash files}}"
mkdir -p "$DEST" "$DEST/.legacy" "$DEST/python_path_first/helpers"

echo "CMS repo : $CMS"
echo "Install → : $DEST"

# Ensure AquaProjects/KskinCMS points at this repo
mkdir -p "$AQUA"
if [[ ! -e "$AQUA/KskinCMS" ]]; then
  ln -sfn "$CMS" "$AQUA/KskinCMS"
  echo "Linked $AQUA/KskinCMS → $CMS"
elif [[ ! -f "$AQUA/KskinCMS/scripts/one_click_lib.sh" ]]; then
  echo "NOTE: $AQUA/KskinCMS exists but missing one_click pack — update/pull that tree."
fi

# --- Backup working mobile .command files, then install wrappers ---
MOBILE_NAMES=(
  run-ios-signup-login.command
  run-android-signup-login.command
  run-ios-full-regression.command
  run-android-full-regression.command
  run-e2e-full-flow-ios.command
  run-e2e-full-flow-android.command
)
for name in "${MOBILE_NAMES[@]}"; do
  src="$DEST/$name"
  if [[ -f "$src" ]]; then
    # Only backup if not already our thin wrapper (legacy must stay the real runner)
    if ! grep -q 'Missing legacy runner' "$src" 2>/dev/null; then
      cp -f "$src" "$DEST/.legacy/$name"
      cp -f "$src" "$DEST/${name}.legacy"
      echo "Backed up mobile runner → .legacy/$name"
    fi
  elif [[ -f "$DEST/.legacy/$name" ]]; then
    cp -f "$DEST/.legacy/$name" "$DEST/${name}.legacy"
  fi
done

# --- Copy CMS + mobile commands from repo pack ---
cp -f "$CMS"/one_click/run-kskin-cms-*.command "$DEST/"
cp -f "$CMS"/one_click/run-ios-*.command "$DEST/" 2>/dev/null || true
cp -f "$CMS"/one_click/run-android-*.command "$DEST/" 2>/dev/null || true
cp -f "$CMS"/one_click/run-e2e-*.command "$DEST/" 2>/dev/null || true
cp -f "$CMS"/one_click/mobile_lib.sh "$DEST/" 2>/dev/null || true

# Thin mobile wrappers (keep *.legacy intact). Remove broken shims/shadow helpers.
rm -rf "$DEST/python_path_first"
rm -rf "$DEST/.one_click_bin" 2>/dev/null || true
cp -f "$CMS/one_click/pace_startup.py" "$DEST/pace_startup.py" 2>/dev/null || true
cp -f "$CMS/one_click/restore_appium_helpers.sh" "$DEST/restore_appium_helpers.sh" 2>/dev/null || true

for name in "${MOBILE_NAMES[@]}"; do
  cp -f "$CMS/one_click/run-mobile-legacy-wrapper.command.template" "$DEST/$name"
  chmod +x "$DEST/$name"
done

cp -f "$CMS/one_click/run-mobile-legacy-wrapper.command.template" \
  "$DEST/run-mobile-legacy-wrapper.command.template" 2>/dev/null || true

chmod +x "$DEST"/*.command "$DEST"/*.sh 2>/dev/null || true
chmod +x "$CMS"/scripts/one_click_lib.sh "$CMS"/one_click/*.sh 2>/dev/null || true
chmod +x "$CMS"/*/run_*_report.bash 2>/dev/null || true

# If Appium helpers lost dynamic_data, restore/generate now
if [[ ! -f "$AQUA/MCP_Appium_Server/python/helpers/dynamic_data.py" ]]; then
  echo "NOTE: helpers.dynamic_data.py missing — restoring/generating…"
  bash "$CMS/one_click/restore_appium_helpers.sh" || true
fi
cp -f "$CMS/one_click/generate_dynamic_data.py" "$DEST/generate_dynamic_data.py" 2>/dev/null || true

# Make sure report bash scripts are executable in repo
find "$CMS" -name 'run_*_report.bash' -exec chmod +x {} \;

cat > "$DEST/README_ONE_CLICK.txt" <<EOF
Kskin one-click runners (installed $(date))

What you get
- CMS: paced visible steps → HTML report → opens in Google Chrome
- Mobile: your previous working .command saved as *.legacy, wrapped with
  pace shim (STEP_PAUSE_SEC=3) + Chrome open at the end

Slower / faster
  STEP_PAUSE_SEC=4 open run-ios-signup-login.command
  (or export in Terminal before double-click via a tiny wrapper)

Requirements
- ~/AquaProjects/KskinCMS → this git repo (installer links if missing)
- cms_config.py present in CMS repo
- helpers.step_report available via MCP_Appium_Server/python
- Mobile: Appium + device/simulator as before

If CMS still fails to start
  open Terminal and run:
  bash ~/AquaProjects/KskinCMS/Product_Module/run_product_report.bash
  and read the error (usually missing cms_config.py or wrong Python).

If mobile most steps fail (but used to pass)
  - Confirm correct app build / bundle id
  - Device unlocked, Appium server running
  - Re-run signup first (environment smoke)
  - Check the HTML report failure screenshots
EOF

echo ""
echo "Installed one-click commands into:"
echo "  $DEST"
echo "Open that folder in Finder and double-click a .command file."
echo "Done."
