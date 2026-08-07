#!/bin/bash
# Wraps your existing working signup/regression .command with visible pacing + Chrome.
cd "$(dirname "$0")" || exit 1

AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"
APPIUM_PY="${APPIUM_PY:-$AQUA/MCP_Appium_Server/python}"
SELF_DIR="$(pwd)"

# Pace shim lives in CMS one_click pack (copied here by installer) or repo
PACE_FIRST=""
for d in \
  "$SELF_DIR/python_path_first" \
  "$AQUA/KskinCMS/one_click/python_path_first" \
  "$HOME/AquaProjects/KskinCMS/one_click/python_path_first"
do
  if [[ -f "$d/helpers/step_report.py" ]]; then PACE_FIRST="$d"; break; fi
done

export PATH="/Library/Frameworks/Python.framework/Versions/3.8/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
export STEP_PAUSE_SEC="${STEP_PAUSE_SEC:-3}"
export STEP_PRE_PAUSE_SEC="${STEP_PRE_PAUSE_SEC:-0.8}"
export AQUA_ROOT="$AQUA"
export APPIUM_PY
export ONE_CLICK_KEEP_OPEN=1

if [[ -n "$PACE_FIRST" ]]; then
  export PYTHONPATH="$PACE_FIRST:$APPIUM_PY:${PYTHONPATH:-}"
  echo "[pace] Using shim: $PACE_FIRST (STEP_PAUSE_SEC=$STEP_PAUSE_SEC)"
else
  export PYTHONPATH="$APPIUM_PY:${PYTHONPATH:-}"
  echo "[pace] WARNING: pace shim not found — steps may still look too fast"
fi

BASE="$(basename "$0")"
LEGACY="$SELF_DIR/${BASE}.legacy"
# Also accept installer backup name
[[ -f "$LEGACY" ]] || LEGACY="$SELF_DIR/.legacy/${BASE}"

open_chrome_newest() {
  local hint="$1"
  local html=""
  html="$(ls -t "$APPIUM_PY"/reports/*"${hint}"*.html 2>/dev/null | head -1 || true)"
  [[ -n "$html" ]] || html="$(ls -t "$APPIUM_PY"/reports/*.html 2>/dev/null | head -1 || true)"
  if [[ -n "$html" && -f "$html" ]]; then
    echo "Opening report in Google Chrome: $html"
    if [[ -d "/Applications/Google Chrome.app" ]]; then
      open -a "Google Chrome" "$html" || open "$html" || true
    else
      open "$html" || true
    fi
  else
    echo "WARNING: No HTML report found under $APPIUM_PY/reports" >&2
  fi
}

HINT="SIGNUP"
case "$BASE" in
  *ios-signup*) HINT="SIGNUP-iOS" ;;
  *android-signup*) HINT="SIGNUP" ;;
  *ios-full*) HINT="REGR-iOS" ;;
  *android-full*) HINT="REGR" ;;
  *e2e*ios*) HINT="E2E" ;;
  *e2e*android*) HINT="E2E" ;;
esac

echo "=============================================================="
echo "  Mobile one-click: $BASE"
echo "  Pace: ${STEP_PAUSE_SEC}s between steps (watch the device)"
echo "  Started: $(date)"
echo "=============================================================="

if [[ ! -f "$LEGACY" ]]; then
  echo "ERROR: Missing legacy runner: $LEGACY" >&2
  echo "Installer should have saved your previous working .command as .legacy" >&2
  echo "Re-run: bash \"\$HOME/AquaProjects/KskinCMS/one_click/install_one_click_commands.sh\"" >&2
  read -r -p "Press Enter…" _
  exit 1
fi

chmod +x "$LEGACY" 2>/dev/null || true
set +e
# Run legacy in a subshell so our env (PYTHONPATH pace) is inherited
bash "$LEGACY"
ST=$?
set -e

open_chrome_newest "$HINT"
echo "Finished: $(date)  (exit $ST)"
read -r -p "Press Enter to close…" _ || true
exit "$ST"
