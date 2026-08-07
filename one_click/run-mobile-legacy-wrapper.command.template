#!/bin/bash
# Mobile one-click = thin wrapper around your ORIGINAL runner.
# Prefer CMS repo venv-based originals so a stale Desktop .legacy cannot keep failing (PEP668).
set -uo pipefail
cd "$(dirname "$0")" || exit 1

AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"
APPIUM_PY="${APPIUM_PY:-$AQUA/MCP_Appium_Server/python}"
SELF_DIR="$(pwd)"
BASE="$(basename "$0")"
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
# Do NOT put Framework 3.8 first — Appium client needs >=3.9
export PATH="$BIN_DIR:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
export PYTHONUNBUFFERED=1
export STEP_PAUSE_SEC="${STEP_PAUSE_SEC:-3}"

is_wrapper() {
  local f="$1"
  [[ -f "$f" ]] || return 1
  grep -q 'thin wrapper' "$f" 2>/dev/null && return 0
  grep -q 'run-mobile-legacy-wrapper' "$f" 2>/dev/null && return 0
  grep -q 'suppressed legacy open' "$f" 2>/dev/null && return 0
  grep -q 'FRESH RUN' "$f" 2>/dev/null && return 0
  grep -q 'Missing legacy runner' "$f" 2>/dev/null && return 0
  return 1
}

has_venv_runner() {
  local f="$1"
  [[ -f "$f" ]] || return 1
  grep -q 'KSKIN_MOBILE_RUNNER_VENV' "$f" 2>/dev/null && return 0
  grep -q '\.venv' "$f" 2>/dev/null && return 0
  return 1
}

find_cms() {
  local c
  for c in \
    "$AQUA/KskinCMS" \
    "$AQUA/KskinCMS_SeleniumPython" \
    "$AQUA/kskincms_seleniumpython" \
    "$HOME/AquaProjects/KskinCMS"
  do
    # CMS exists if pack is present — do NOT require this CORE_NAME original
    if [[ -f "$c/one_click/mobile_venv.sh" ]] \
      || [[ -d "$c/one_click/originals" ]] \
      || [[ -f "$c/scripts/one_click_lib.sh" ]]; then
      echo "$c"
      return 0
    fi
  done
  return 1
}

CMS="$(find_cms || true)"
CMS_ORIG=""
if [[ -n "${CMS:-}" ]]; then
  CMS_ORIG="$CMS/one_click/originals/$CORE_NAME"
fi

# Heal Desktop backups from CMS when signup originals are venv-based
heal_from_cms() {
  [[ -n "${CMS_ORIG:-}" && -f "$CMS_ORIG" ]] || return 1
  has_venv_runner "$CMS_ORIG" || return 1
  mkdir -p "$SELF_DIR/.legacy" "$SELF_DIR/_originals"
  cp -f "$CMS_ORIG" "$SELF_DIR/.legacy/$CORE_NAME"
  cp -f "$CMS_ORIG" "$SELF_DIR/${CORE_NAME}.legacy"
  cp -f "$CMS_ORIG" "$SELF_DIR/_originals/$CORE_NAME"
  chmod +x "$SELF_DIR/.legacy/$CORE_NAME" "$SELF_DIR/${CORE_NAME}.legacy" "$SELF_DIR/_originals/$CORE_NAME"
  echo "[one-click] Healed Desktop .legacy from CMS originals (venv runner)."
  return 0
}

pick_runner() {
  local cand

  # 1) Prefer CMS original when it is the venv-based runner (ignores stale Desktop)
  if [[ -n "${CMS_ORIG:-}" ]] && has_venv_runner "$CMS_ORIG"; then
    heal_from_cms || true
    echo "$CMS_ORIG"
    return 0
  fi

  # 2) Desktop copies that already have venv logic
  for cand in \
    "$SELF_DIR/_originals/$CORE_NAME" \
    "$SELF_DIR/.legacy/$CORE_NAME" \
    "$SELF_DIR/${CORE_NAME}.legacy"
  do
    if [[ -f "$cand" ]] && ! is_wrapper "$cand" && has_venv_runner "$cand"; then
      echo "$cand"
      return 0
    fi
  done

  # 3) Any non-wrapper backup (may still be old — last resort)
  for cand in \
    "$SELF_DIR/${CORE_NAME}.legacy" \
    "$SELF_DIR/.legacy/$CORE_NAME" \
    "$SELF_DIR/.legacy/${CORE_NAME}.legacy" \
    "$SELF_DIR/_originals/$CORE_NAME"
  do
    if [[ -f "$cand" ]] && ! is_wrapper "$cand"; then
      echo "$cand"
      return 0
    fi
  done
  return 1
}

LEGACY="$(pick_runner || true)"

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
echo "  CMS: ${CMS:-NOT FOUND}"
echo "  Runner: ${LEGACY:-NOT FOUND}"
if [[ -n "${LEGACY:-}" ]] && has_venv_runner "$LEGACY"; then
  echo "  Runner mark: KSKIN_MOBILE_RUNNER_VENV (ok)"
else
  echo "  Runner mark: MISSING/OLD (PEP668 risk — pull + reinstall)"
fi
echo "  Started: $(date)"
echo "=============================================================="

if [[ -z "${LEGACY:-}" ]]; then
  echo "ERROR: No runner found for $CORE_NAME." >&2
  echo "CMS: ${CMS:-NOT FOUND}" >&2
  if [[ -n "${CMS:-}" ]]; then
    echo "Looked for: $CMS/one_click/originals/$CORE_NAME" >&2
    ls -la "$CMS/one_click/originals/" 2>/dev/null || true
  fi
  echo "In Terminal:" >&2
  echo "  cd ~/AquaProjects/KskinCMS && git stash -u && git pull" >&2
  echo "  bash one_click/fix_pep668_now.sh" >&2
  read -r -p "Press Enter…" _; exit 1
fi

if ! has_venv_runner "$LEGACY"; then
  echo "ERROR: Runner is still the OLD Homebrew-pip script (PEP668)." >&2
  echo "Your Desktop .legacy was not updated. Fix NOW:" >&2
  echo "  cd ~/AquaProjects/KskinCMS && git stash -u && git pull" >&2
  echo "  bash one_click/fix_pep668_now.sh" >&2
  read -r -p "Press Enter…" _; exit 1
fi

HELPERS="$APPIUM_PY/helpers"
if [[ ! -f "$HELPERS/dynamic_data.py" ]]; then
  if [[ -n "${CMS:-}" && -f "$CMS/one_click/generate_dynamic_data.py" ]]; then
    echo "[one-click] Creating helpers/dynamic_data.py stub..."
    python3 "$CMS/one_click/generate_dynamic_data.py" || true
  else
    echo "WARNING: $HELPERS/dynamic_data.py missing — signup may fail collection."
  fi
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
