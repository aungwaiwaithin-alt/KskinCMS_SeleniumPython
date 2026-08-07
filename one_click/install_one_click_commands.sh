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

# --- CMS ONLY ---
# This installer no longer touches mobile .command files or the Appium tree.
# Mobile is handled separately, after the ORIGINAL Appium tests pass:
#   bash one_click/purge_mobile_one_clicks.sh
#   bash one_click/run_original_mobile_test.sh android-signup
cp -f "$CMS"/one_click/run-kskin-cms-*.command "$DEST/"

# Remove shims that used to shadow python/open for mobile wrappers
rm -rf "$DEST/python_path_first" 2>/dev/null || true
rm -rf "$DEST/.one_click_bin" 2>/dev/null || true

chmod +x "$DEST"/run-kskin-cms-*.command 2>/dev/null || true
chmod +x "$CMS"/scripts/one_click_lib.sh "$CMS"/one_click/*.sh 2>/dev/null || true
chmod +x "$CMS"/*/run_*_report.bash 2>/dev/null || true

# Make sure report bash scripts are executable in repo
find "$CMS" -name 'run_*_report.bash' -exec chmod +x {} \;

cat > "$DEST/README_ONE_CLICK.txt" <<EOF
Kskin CMS one-click runners (installed $(date))

CMS (this installer)
- Paced visible steps → HTML report → opens automatically in Google Chrome
- Files: run-kskin-cms-*.command

Slower / faster pacing
  STEP_PAUSE_SEC=4 bash run-kskin-cms-outlet.command

Requirements
- ~/AquaProjects/KskinCMS → this git repo (installer links if missing)
- cms_config.py present in CMS repo

If CMS fails to start
  bash ~/AquaProjects/KskinCMS/Product_Module/run_product_report.bash
  and read the error (usually missing cms_config.py or wrong Python).

MOBILE is NOT installed here
Mobile one-clicks are generated only after the ORIGINAL Appium tests pass:
  bash ~/AquaProjects/KskinCMS/one_click/purge_mobile_one_clicks.sh
  bash ~/AquaProjects/KskinCMS/one_click/run_original_mobile_test.sh android-signup
EOF

echo ""
echo "Installed CMS one-click commands into:"
echo "  $DEST"
echo "Open that folder in Finder and double-click a run-kskin-cms-*.command file."
echo ""
echo "Mobile is intentionally untouched. Run originals first:"
echo "  bash $CMS/one_click/run_original_mobile_test.sh android-signup"
echo "Done."
