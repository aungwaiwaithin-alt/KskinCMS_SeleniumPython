#!/bin/bash
# Mobile one-click = your original *.legacy, almost untouched.
# We only suppress mid-run HTML open + open Chrome if a NEW report appears.
set -uo pipefail
cd "$(dirname "$0")" || exit 1

AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"
APPIUM_PY="${APPIUM_PY:-$AQUA/MCP_Appium_Server/python}"
SELF_DIR="$(pwd)"
BASE="$(basename "$0")"
START_EPOCH="$(date +%s)"

REAL_OPEN="$(command -v open || echo /usr/bin/open)"
BIN_DIR="$SELF_DIR/.one_click_bin"
mkdir -p "$BIN_DIR"
# Always remove old broken shims
rm -f "$BIN_DIR/python" "$BIN_DIR/python3" "$BIN_DIR/pytest" "$BIN_DIR/_kskin_py_shim.py" 2>/dev/null || true
# Clear leftover shadow path vars from older installs
unset KSKIN_PACE_FIRST KSKIN_PACE_STARTUP PYTHONSTARTUP
if [[ -n "${PYTHONPATH:-}" ]]; then
  export PYTHONPATH="$(echo "$PYTHONPATH" | tr ':' '\n' | grep -v 'python_path_first' | grep -v '^$' | paste -sd: - || true)"
fi

cat > "$BIN_DIR/open" <<EOF
#!/bin/bash
for a in "\$@"; do
  case "\$a" in
    *.html|*.htm) echo "[one-click] suppressed legacy open of \$a"; exit 0 ;;
  esac
done
exec "$REAL_OPEN" "\$@"
EOF
chmod +x "$BIN_DIR/open"
export PATH="$BIN_DIR:/Library/Frameworks/Python.framework/Versions/3.8/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
export PYTHONUNBUFFERED=1
export STEP_PAUSE_SEC="${STEP_PAUSE_SEC:-3}"

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
echo "  $BASE  (thin wrapper → your original .legacy)"
echo "  Legacy: $LEGACY"
echo "  Started: $(date)"
echo "=============================================================="

if [[ ! -f "$LEGACY" ]]; then
  echo "ERROR: missing $LEGACY" >&2
  read -r -p "Press Enter…" _; exit 1
fi

# Warn-only if helpers look incomplete (do NOT block — Claude-style just run)
HELPERS="$APPIUM_PY/helpers"
if [[ -d "$HELPERS" ]] && [[ ! -f "$HELPERS/dynamic_data.py" ]]; then
  echo "WARNING: $HELPERS/dynamic_data.py is missing."
  echo "         helpers currently has: $(ls "$HELPERS" | tr '\n' ' ')"
  echo "         If pytest fails on helpers.dynamic_data, restore Appium helpers:"
  echo "           bash \"\$HOME/AquaProjects/KskinCMS/one_click/restore_appium_helpers.sh\""
  echo ""
fi

REPORT_DIR="$APPIUM_PY/reports"
mkdir -p "$REPORT_DIR"

set +e
# Same as double-clicking your old working file
bash "$LEGACY"
ST=$?
set -e

pick_new_report() {
  local f mtime best="" best_m=0
  local files=()
  while IFS= read -r f; do files+=("$f"); done < <(ls -1 "$REPORT_DIR"/*"${HINT}"*.html 2>/dev/null || true)
  if [[ ${#files[@]} -eq 0 ]]; then
    while IFS= read -r f; do files+=("$f"); done < <(ls -1 "$REPORT_DIR"/*.html 2>/dev/null || true)
  fi
  for f in "${files[@]}"; do
    [[ -f "$f" ]] || continue
    mtime="$(stat -f %m "$f" 2>/dev/null || stat -c %Y "$f" 2>/dev/null || echo 0)"
    if [[ "$mtime" -ge "$START_EPOCH" ]] && [[ "$mtime" -ge "$best_m" ]]; then
      best="$f"; best_m="$mtime"
    fi
  done
  printf '%s' "$best"
}

NEW_REPORT="$(pick_new_report)"
if [[ -n "$NEW_REPORT" ]]; then
  echo "Fresh report → Chrome: $NEW_REPORT"
  if [[ -d "/Applications/Google Chrome.app" ]]; then
    "$REAL_OPEN" -a "Google Chrome" "$NEW_REPORT" || "$REAL_OPEN" "$NEW_REPORT" || true
  else
    "$REAL_OPEN" "$NEW_REPORT" || true
  fi
else
  echo "No new HTML report since start (suite may have failed before emit)."
fi

echo "Finished: $(date)  (exit $ST)"
read -r -p "Press Enter to close…" _ || true
exit "$ST"
