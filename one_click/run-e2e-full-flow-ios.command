#!/bin/bash
# Mobile one-click: FRESH run + visible paced steps + open ONLY a new HTML report in Chrome.
# Your previous working script is kept as *.legacy (installer backup).
set -uo pipefail
cd "$(dirname "$0")" || exit 1

AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"
APPIUM_PY="${APPIUM_PY:-$AQUA/MCP_Appium_Server/python}"
SELF_DIR="$(pwd)"
BASE="$(basename "$0")"
RUN_ID="$(date +%Y%m%d_%H%M%S)"
START_EPOCH="$(date +%s)"

PACE_FIRST=""
for d in \
  "$SELF_DIR/python_path_first" \
  "$AQUA/KskinCMS/one_click/python_path_first" \
  "$HOME/AquaProjects/KskinCMS/one_click/python_path_first"
do
  if [[ -f "$d/helpers/step_report.py" ]]; then PACE_FIRST="$d"; break; fi
done

PACE_STARTUP=""
for f in \
  "$SELF_DIR/pace_startup.py" \
  "$AQUA/KskinCMS/one_click/pace_startup.py" \
  "$HOME/AquaProjects/KskinCMS/one_click/pace_startup.py"
do
  if [[ -f "$f" ]]; then PACE_STARTUP="$f"; break; fi
done

export PATH="/Library/Frameworks/Python.framework/Versions/3.8/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
export STEP_PAUSE_SEC="${STEP_PAUSE_SEC:-3}"
export STEP_PRE_PAUSE_SEC="${STEP_PRE_PAUSE_SEC:-1}"
export AQUA_ROOT="$AQUA"
export APPIUM_PY
export ONE_CLICK_KEEP_OPEN=1
# Force unbuffered Python so step banners appear live in Terminal
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

if [[ -n "$PACE_FIRST" ]]; then
  export PYTHONPATH="$PACE_FIRST:$APPIUM_PY:${PYTHONPATH:-}"
else
  export PYTHONPATH="$APPIUM_PY:${PYTHONPATH:-}"
fi
if [[ -n "$PACE_STARTUP" ]]; then
  export PYTHONSTARTUP="$PACE_STARTUP"
fi

# python/python3 shims so legacy scripts cannot drop our pace env
BIN_DIR="$SELF_DIR/.one_click_bin"
mkdir -p "$BIN_DIR"
REAL_PY="$(command -v python3.8 || command -v python3)"
cat > "$BIN_DIR/python3" <<EOF
#!/bin/bash
export PYTHONUNBUFFERED=1
export PYTHONPATH="$PACE_FIRST:$APPIUM_PY:\${PYTHONPATH:-}"
export PYTHONSTARTUP="$PACE_STARTUP"
exec "$REAL_PY" -u "\$@"
EOF
cp "$BIN_DIR/python3" "$BIN_DIR/python"
chmod +x "$BIN_DIR/python3" "$BIN_DIR/python"
export PATH="$BIN_DIR:$PATH"

LEGACY="$SELF_DIR/${BASE}.legacy"
[[ -f "$LEGACY" ]] || LEGACY="$SELF_DIR/.legacy/${BASE}"

HINT="SIGNUP"
case "$BASE" in
  *ios-signup*) HINT="KS-SIGNUP-iOS" ;;
  *android-signup*) HINT="KS-SIGNUP" ;;
  *ios-full*) HINT="KS-REGR-iOS" ;;
  *android-full*) HINT="KS-REGR-AND" ;;
  *e2e*ios*) HINT="E2E" ;;
  *e2e*android*) HINT="E2E" ;;
esac

echo "=============================================================="
echo "  Mobile one-click (FRESH RUN): $BASE"
echo "  Appium reports: $APPIUM_PY/reports"
echo "  Pace: ${STEP_PAUSE_SEC}s between steps — watch the device"
echo "  Run id: $RUN_ID"
echo "  Started: $(date)"
echo "=============================================================="

if [[ ! -d "$APPIUM_PY" ]]; then
  echo "ERROR: Missing $APPIUM_PY" >&2
  read -r -p "Press Enter…" _; exit 1
fi
if [[ ! -f "$LEGACY" ]]; then
  echo "ERROR: Missing legacy runner: $LEGACY" >&2
  echo "Re-run: bash \"\$HOME/AquaProjects/KskinCMS/one_click/install_one_click_commands.sh\"" >&2
  read -r -p "Press Enter…" _; exit 1
fi

# Snapshot existing reports so we only open a NEW file afterward
REPORT_DIR="$APPIUM_PY/reports"
mkdir -p "$REPORT_DIR"
SNAP="$SELF_DIR/.report_snap_${RUN_ID}.txt"
find "$REPORT_DIR" -maxdepth 1 -name '*.html' -type f -printf '%p\t%T@\n' 2>/dev/null \
  | sort > "$SNAP" || true
# macOS find lacks -printf — fallback
if [[ ! -s "$SNAP" ]]; then
  # shellcheck disable=SC2012
  ls -1 "$REPORT_DIR"/*.html 2>/dev/null | while read -r f; do
    stat -f '%N	%m' "$f" 2>/dev/null || stat -c '%n	%Y' "$f" 2>/dev/null
  done | sort > "$SNAP" || true
fi

echo ""
echo "IMPORTANT: Keep Terminal in front. You should see STEP banners while the device moves."
echo "If Chrome opens an OLD report from weeks ago, this wrapper will warn you."
echo ""
sleep 2

# Sanitize legacy: disable auto-open of HTML so we control Chrome at the end,
# and keep the window from eating our flow with nested "Press any key".
CLEAN="$SELF_DIR/.legacy_run_${BASE}_${RUN_ID}.command"
# Remove open of html reports; soften blocking reads
sed -E \
  -e 's/^([[:space:]]*)open[[:space:]]+(-a[[:space:]]+"?Google Chrome"?[[:space:]]+)?["'\'']?[^"'\'']+\.html["'\'']?/echo "[one-click] skipped legacy open: &"/g' \
  -e 's/open[[:space:]]+"\$[A-Z_]*REPORT[^"]*"[[:space:]]*\|\|[[:space:]]*true/echo "[one-click] skipped legacy report open"/g' \
  -e 's/open[[:space:]]+"\$\{?[A-Z_]*REPORT[^"]*"\}?/echo "[one-click] skipped legacy report open"/g' \
  -e 's/read -n 1[^$]*/echo "[one-click] skip nested keypress"; true/g' \
  -e 's/read -r -p "Press Enter[^"]*" _/echo "[one-click] skip nested Enter"; true/g' \
  -e 's/read -r -p '\''Press Enter[^'\'']*'\'' _/echo "[one-click] skip nested Enter"; true/g' \
  "$LEGACY" > "$CLEAN" || cp "$LEGACY" "$CLEAN"
chmod +x "$CLEAN"

echo "[one-click] Launching sanitized legacy runner…"
echo "[one-click] Legacy: $LEGACY"
set +e
bash "$CLEAN"
ST=$?
set -e

# Find a report newer than START_EPOCH matching hint
pick_new_report() {
  local f mtime best="" best_m=0
  shopt -s nullglob
  local files=( "$REPORT_DIR"/*"${HINT}"*.html )
  if [[ ${#files[@]} -eq 0 ]]; then
    files=( "$REPORT_DIR"/*.html )
  fi
  for f in "${files[@]}"; do
    mtime="$(stat -f %m "$f" 2>/dev/null || stat -c %Y "$f" 2>/dev/null || echo 0)"
    if [[ "$mtime" -ge "$START_EPOCH" ]] && [[ "$mtime" -ge "$best_m" ]]; then
      best="$f"; best_m="$mtime"
    fi
  done
  echo "$best"
}

NEW_REPORT="$(pick_new_report)"
echo ""
if [[ -n "$NEW_REPORT" ]]; then
  echo "Fresh report generated: $NEW_REPORT"
  echo "Opening in Google Chrome…"
  if [[ -d "/Applications/Google Chrome.app" ]]; then
    open -a "Google Chrome" "$NEW_REPORT" || open "$NEW_REPORT" || true
  else
    open "$NEW_REPORT" || true
  fi
else
  echo "==============================================================" >&2
  echo "ERROR: No NEW HTML report since this run started ($(date -r "$START_EPOCH" 2>/dev/null || date))." >&2
  echo "The suite likely did NOT re-run (or crashed before emit)." >&2
  echo "NOT opening an old June/July report on purpose." >&2
  echo "" >&2
  echo "Debug:" >&2
  echo "  1) Scroll Terminal above for Python/Appium errors" >&2
  echo "  2) Confirm device/simulator unlocked + Appium running" >&2
  echo "  3) Try legacy directly: bash \"$LEGACY\"" >&2
  echo "==============================================================" >&2
  # Show newest old report path for reference only
  OLD="$(ls -t "$REPORT_DIR"/*.html 2>/dev/null | head -1 || true)"
  [[ -n "$OLD" ]] && echo "Newest OLD report (not opened): $OLD" >&2
fi

rm -f "$CLEAN" "$SNAP" 2>/dev/null || true
echo "Finished: $(date)  (exit $ST)"
read -r -p "Press Enter to close…" _ || true
exit "$ST"
