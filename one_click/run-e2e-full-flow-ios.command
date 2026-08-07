#!/bin/bash
# Mobile one-click = thin wrapper around your ORIGINAL runner.
# Never treat another wrapper copy as the legacy script.
set -uo pipefail
cd "$(dirname "$0")" || exit 1

AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"
APPIUM_PY="${APPIUM_PY:-$AQUA/MCP_Appium_Server/python}"
SELF_DIR="$(pwd)"
BASE="$(basename "$0")"
# If someone executes a *.command.legacy that is itself a wrapper, normalize name
CORE_NAME="$BASE"
CORE_NAME="${CORE_NAME%.legacy}"
START_EPOCH="$(date +%s)"

REAL_OPEN="$(command -v open || echo /usr/bin/open)"
BIN_DIR="$SELF_DIR/.one_click_bin"
mkdir -p "$BIN_DIR"
rm -f "$BIN_DIR/python" "$BIN_DIR/python3" "$BIN_DIR/pytest" "$BIN_DIR/_kskin_py_shim.py" 2>/dev/null || true
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

is_wrapper() {
  local f="$1"
  [[ -f "$f" ]] || return 1
  # Our wrappers contain this marker; real Claude-era runners do not
  grep -q 'thin wrapper' "$f" 2>/dev/null && return 0
  grep -q 'run-mobile-legacy-wrapper' "$f" 2>/dev/null && return 0
  grep -q 'suppressed legacy open' "$f" 2>/dev/null && return 0
  grep -q 'FRESH RUN' "$f" 2>/dev/null && return 0
  grep -q 'Missing legacy runner' "$f" 2>/dev/null && return 0
  return 1
}

pick_legacy() {
  local cand
  for cand in \
    "$SELF_DIR/${CORE_NAME}.legacy" \
    "$SELF_DIR/.legacy/${CORE_NAME}" \
    "$SELF_DIR/.legacy/${CORE_NAME}.legacy" \
    "$SELF_DIR/_originals/${CORE_NAME}" \
    "$SELF_DIR/_originals/${CORE_NAME}.legacy"
  do
    if [[ -f "$cand" ]] && ! is_wrapper "$cand"; then
      echo "$cand"
      return 0
    fi
  done
  return 1
}

LEGACY="$(pick_legacy || true)"

HINT="SIGNUP"
case "$CORE_NAME" in
  *ios-signup*) HINT="KS-SIGNUP-iOS" ;;
  *android-signup*) HINT="KS-SIGNUP" ;;
  *ios-full*) HINT="KS-REGR-iOS" ;;
  *android-full*) HINT="KS-REGR-AND" ;;
  *e2e*ios*) HINT="E2E" ;;
  *e2e*android*) HINT="E2E" ;;
esac

echo "=============================================================="
echo "  $CORE_NAME  (thin wrapper → original runner)"
echo "  Legacy: ${LEGACY:-NOT FOUND}"
echo "  Started: $(date)"
echo "=============================================================="

if [[ -z "${LEGACY:-}" ]]; then
  echo "ERROR: Original runner backup not found (or only wrapper copies remain)." >&2
  echo "Looked for non-wrapper files:" >&2
  echo "  $SELF_DIR/${CORE_NAME}.legacy" >&2
  echo "  $SELF_DIR/.legacy/${CORE_NAME}" >&2
  echo "" >&2
  echo "Recover NOW (Terminal):" >&2
  echo "  ls -la \"$SELF_DIR/.legacy\"" >&2
  echo "  ls -la \"$SELF_DIR\"/*.legacy 2>/dev/null" >&2
  echo "" >&2
  echo "If empty, restore from Time Machine or re-copy the old working" >&2
  echo ".command that Claude used into:" >&2
  echo "  $SELF_DIR/.legacy/$CORE_NAME" >&2
  read -r -p "Press Enter…" _; exit 1
fi

HELPERS="$APPIUM_PY/helpers"
if [[ ! -f "$HELPERS/dynamic_data.py" ]]; then
  echo "WARNING: $HELPERS/dynamic_data.py missing — signup may fail collection."
  echo "Create it first (see Cursor chat), then re-run."
fi

REPORT_DIR="$APPIUM_PY/reports"
mkdir -p "$REPORT_DIR"

set +e
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
  echo "No new HTML report since start."
fi

echo "Finished: $(date)  (exit $ST)"
read -r -p "Press Enter to close…" _ || true
exit "$ST"
