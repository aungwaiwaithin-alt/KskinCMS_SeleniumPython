#!/usr/bin/env bash
# Shared helpers for Claude-style mobile one-clicks (sourced from same folder).
# Copied to Desktop "One click bash files" beside the .command files.

open_fresh_report_only() {
  # $1 = start epoch, $2+ = globs relative to cwd (usually reports/)
  local start_epoch="$1"
  shift
  local best="" best_m=0 f m
  local matches=()
  local g
  for g in "$@"; do
    # shellcheck disable=SC2086
    for f in $g; do
      [[ -f "$f" ]] || continue
      matches+=("$f")
    done
  done
  for f in "${matches[@]:-}"; do
    [[ -f "$f" ]] || continue
    m="$(stat -f %m "$f" 2>/dev/null || stat -c %Y "$f" 2>/dev/null || echo 0)"
    if [[ "$m" -ge "$start_epoch" && "$m" -ge "$best_m" ]]; then
      best="$f"
      best_m="$m"
    fi
  done
  if [[ -n "$best" ]]; then
    echo "Fresh report → Chrome: $best"
    if [[ -d "/Applications/Google Chrome.app" ]]; then
      open -a "Google Chrome" "$best" || open "$best" || true
    else
      open "$best" || true
    fi
    return 0
  fi
  echo "ERROR: No NEW HTML report from this run — not opening any old report."
  return 1
}

ensure_appium_venv() {
  # sets PY, uses APPIUM_PY
  local base="" c
  for c in /usr/local/bin/python3 /opt/homebrew/bin/python3.12 /opt/homebrew/bin/python3; do
    [[ -x "$c" ]] || continue
    "$c" -c 'import sys; raise SystemExit(0 if sys.version_info>=(3,9) else 1)' 2>/dev/null && base="$c" && break
  done
  [[ -n "$base" ]] || { echo "ERROR: need Python >= 3.9"; return 1; }
  local venv="$APPIUM_PY/.venv"
  PY="$venv/bin/python"
  [[ -x "$PY" ]] || "$base" -m venv "$venv" || { echo "ERROR: venv failed"; return 1; }
  export PATH="$venv/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"
  export PYTHONPATH="$APPIUM_PY${PYTHONPATH:+:$PYTHONPATH}"
  export PYTHONUNBUFFERED=1
  "$PY" -c 'import pytest,appium' 2>/dev/null || "$PY" -m pip install -U pytest Appium-Python-Client selenium
  echo "Python: $PY ($("$PY" -V))"
}

preflight_android_pages() {
  cd "$APPIUM_PY" || return 1
  if [[ ! -d pages ]]; then
    echo "ERROR: missing $APPIUM_PY/pages/ (Appium page objects)."
    echo "Restore from MCP_Appium_Server.zip or Time Machine, then re-run."
    return 1
  fi
  if [[ ! -f pages/permissions_android_page.py ]]; then
    echo "ERROR: missing pages/permissions_android_page.py"
    echo "pages/ currently has:"
    ls -la pages/ | head -40
    echo ""
    echo "Try: bash ~/AquaProjects/KskinCMS/one_click/restore_appium_pages.sh"
    return 1
  fi
  if ! "$PY" -c 'from pages.permissions_android_page import PermissionsAndroidPage' 2>/dev/null; then
    echo "ERROR: cannot import pages.permissions_android_page"
    "$PY" -c 'from pages.permissions_android_page import PermissionsAndroidPage' || true
    return 1
  fi
  return 0
}
