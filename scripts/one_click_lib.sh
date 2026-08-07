#!/usr/bin/env bash
# Shared helpers for Kskin one-click .command / report.bash runners (macOS).
# Usage: source "$CMS_ROOT/scripts/one_click_lib.sh"

one_click_resolve_paths() {
  export AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"
  export REPORT_DIR="${REPORT_DIR:-$HOME/kskin-web(cms)-automation/reports}"
  export APPIUM_PY="${APPIUM_PY:-$AQUA/MCP_Appium_Server/python}"

  # Prefer Framework Python 3.8 (Selenium stack), then Homebrew, then python3
  export PATH="/Library/Frameworks/Python.framework/Versions/3.8/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
  PYTHON_BIN="${PYTHON_BIN:-$(command -v python3.8 || command -v python3)}"
  export PYTHON_BIN

  # Locate CMS package root (folder that contains cms_auth.py / Product_Module)
  local candidates=(
    "${CMS_ROOT:-}"
    "$AQUA/KskinCMS"
    "$AQUA/KskinCMS_SeleniumPython"
    "$AQUA/kskincms_seleniumpython"
    "$HOME/AquaProjects/KskinCMS"
  )
  CMS_ROOT=""
  local c
  for c in "${candidates[@]}"; do
    [[ -z "$c" ]] && continue
    if [[ -f "$c/cms_auth.py" || -f "$c/playwright_auth.py" ]]; then
      CMS_ROOT="$(cd "$c" && pwd)"
      break
    fi
  done
  if [[ -z "$CMS_ROOT" ]]; then
    echo "ERROR: Cannot find KskinCMS under $AQUA" >&2
    echo "Expected e.g. $AQUA/KskinCMS with cms_auth.py" >&2
    echo "Fix: ln -sfn /path/to/this/repo \"$AQUA/KskinCMS\"" >&2
    return 1
  fi
  export CMS_ROOT

  # Ensure import name KskinCMS works (AquaProjects/KskinCMS → package)
  if [[ ! -e "$AQUA/KskinCMS" ]]; then
    ln -sfn "$CMS_ROOT" "$AQUA/KskinCMS" 2>/dev/null || true
  fi

  export PYTHONPATH="$AQUA:$APPIUM_PY:${CMS_ROOT}${PYTHONPATH:+:$PYTHONPATH}"
  # One-click = headed browser so you can watch steps
  unset PLAYWRIGHT_HEADLESS
  export PLAYWRIGHT_HEADLESS=0
  export STEP_PAUSE_SEC="${STEP_PAUSE_SEC:-2.5}"
  export STEP_PRE_PAUSE_SEC="${STEP_PRE_PAUSE_SEC:-0.8}"
}

one_click_require_cms_config() {
  if [[ ! -f "$CMS_ROOT/cms_config.py" ]]; then
    echo "ERROR: Missing $CMS_ROOT/cms_config.py" >&2
    echo "Copy cms_config.example.py → cms_config.py and fill staging creds." >&2
    return 1
  fi
}

one_click_setup() {
  # $1 = report html basename or full path, $2 = title
  local report_arg="$1"
  local title="${2:-Kskin CMS}"
  one_click_resolve_paths || return 1
  one_click_require_cms_config || return 1
  mkdir -p "$REPORT_DIR"
  if [[ "$report_arg" = /* ]]; then
    export CMS_REPORT_HTML="$report_arg"
  else
    export CMS_REPORT_HTML="$REPORT_DIR/$report_arg"
  fi
  export REPORT_HTML="$CMS_REPORT_HTML"
  unset ONE_CLICK_CHROME_OPENED
  cd "$AQUA" || return 1
  # Safety net: always open HTML in Chrome if the shell exits early (e.g. set -e).
  trap 'one_click_open_chrome "${CMS_REPORT_HTML:-${REPORT_HTML:-}}" || true' EXIT
  echo "=============================================================="
  echo "  $title"
  echo "  CMS_ROOT : $CMS_ROOT"
  echo "  Python   : $PYTHON_BIN"
  echo "  Report   : $CMS_REPORT_HTML"
  echo "  Pace     : pre ${STEP_PRE_PAUSE_SEC}s / between ${STEP_PAUSE_SEC}s"
  echo "  Started  : $(date)"
  echo "=============================================================="
}

one_click_open_chrome() {
  local html="${1:-${CMS_REPORT_HTML:-${REPORT_HTML:-}}}"
  if [[ -z "$html" || ! -f "$html" ]]; then
    echo "WARNING: Report HTML not found: ${html:-<empty>}" >&2
    return 1
  fi
  # Idempotent — safe if finish + EXIT trap both call us
  if [[ "${ONE_CLICK_CHROME_OPENED:-}" == "$html" ]]; then
    return 0
  fi
  echo ""
  echo "Opening report in Google Chrome:"
  echo "  $html"
  # Prefer Chrome explicitly (user request). Quote path (reports dir may contain parentheses).
  if [[ -d "/Applications/Google Chrome.app" ]]; then
    open -a "Google Chrome" "$html" 2>/dev/null || open "$html" 2>/dev/null || true
  else
    open "$html" 2>/dev/null || true
  fi
  export ONE_CLICK_CHROME_OPENED="$html"
}

one_click_finish() {
  local status="${1:-0}"
  # Clear EXIT trap so we don't double-run after an intentional finish
  trap - EXIT 2>/dev/null || true
  one_click_open_chrome "${CMS_REPORT_HTML:-${REPORT_HTML:-}}" || true
  echo ""
  echo "Finished: $(date)  (exit ${status})"
  echo "Tip: slower watch → STEP_PAUSE_SEC=4 double-click again"
  # Keep Terminal open when launched from Finder (.command)
  if [[ -t 0 ]] || [[ "${ONE_CLICK_KEEP_OPEN:-1}" == "1" ]]; then
    read -r -p "Press Enter to close…" _ || true
  fi
  # Always succeed from the caller's perspective so set -e cannot skip exit handling
  return 0
}

one_click_run_python() {
  # Runs python heredoc/file. NEVER leave set -e on — a failed test must still
  # reach one_click_finish so the HTML report opens in Google Chrome.
  set +e
  "$PYTHON_BIN" "$@"
  local st=$?
  # Do not re-enable set -e here (that used to abort runners before Chrome open).
  return "$st"
}
