#!/usr/bin/env bash
# Shared mobile one-click launcher: pace shim + run target + open Chrome report
set -uo pipefail

AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"
APPIUM_PY="${APPIUM_PY:-$AQUA/MCP_Appium_Server/python}"
ONE_CLICK_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PACE_FIRST="$ONE_CLICK_ROOT/python_path_first"

export PATH="/Library/Frameworks/Python.framework/Versions/3.8/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3.8 || command -v python3)}"
export STEP_PAUSE_SEC="${STEP_PAUSE_SEC:-3}"
export STEP_PRE_PAUSE_SEC="${STEP_PRE_PAUSE_SEC:-0.8}"
export ONE_CLICK_KEEP_OPEN=1
export AQUA_ROOT="$AQUA"
export APPIUM_PY

# Prefer pace shim, then Appium python (real helpers + suites)
export PYTHONPATH="$PACE_FIRST:$APPIUM_PY:${PYTHONPATH:-}"

open_chrome_report() {
  local html="$1"
  if [[ -z "$html" || ! -f "$html" ]]; then
    echo "WARNING: report not found: ${html:-<empty>}" >&2
    # try newest html in reports/
    local newest
    newest="$(ls -t "$APPIUM_PY"/reports/*.html 2>/dev/null | head -1 || true)"
    if [[ -n "$newest" ]]; then
      html="$newest"
      echo "Using newest report: $html"
    else
      return 1
    fi
  fi
  echo "Opening report in Google Chrome: $html"
  if [[ -d "/Applications/Google Chrome.app" ]]; then
    open -a "Google Chrome" "$html" || open "$html" || true
  else
    open "$html" || true
  fi
}

run_mobile_target() {
  # $1 = human title, $2 = preferred report glob/name, remaining = command
  local title="$1"
  local report_hint="$2"
  shift 2

  echo "=============================================================="
  echo "  $title"
  echo "  Appium  : $APPIUM_PY"
  echo "  Python  : $PYTHON_BIN"
  echo "  Pace    : pre ${STEP_PRE_PAUSE_SEC}s / between ${STEP_PAUSE_SEC}s"
  echo "  Started : $(date)"
  echo "=============================================================="

  if [[ ! -d "$APPIUM_PY" ]]; then
    echo "ERROR: Appium python tree missing: $APPIUM_PY" >&2
    read -r -p "Press Enter…" _
    exit 1
  fi

  cd "$APPIUM_PY" || exit 1
  set +e
  "$@"
  local st=$?
  set -e

  local report=""
  if [[ -f "$APPIUM_PY/reports/$report_hint" ]]; then
    report="$APPIUM_PY/reports/$report_hint"
  else
    report="$(ls -t "$APPIUM_PY"/reports/*"${report_hint}"* 2>/dev/null | head -1 || true)"
  fi
  open_chrome_report "$report" || true

  echo "Finished: $(date)  (exit $st)"
  read -r -p "Press Enter to close…" _ || true
  exit "$st"
}
