#!/bin/bash
# Double-click one-click runner — paced steps + HTML report in Google Chrome
cd "$(dirname "$0")" || exit 1
AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"
CMS=""
for c in "$AQUA/KskinCMS" "$AQUA/KskinCMS_SeleniumPython" "$AQUA/kskincms_seleniumpython"; do
  if [[ -f "$c/FranchiseeReports_Module/run_franchisee_reports_report.bash" ]]; then CMS="$c"; break; fi
done
if [[ -z "$CMS" ]]; then
  echo "ERROR: Cannot find FranchiseeReports_Module/run_franchisee_reports_report.bash under $AQUA" >&2
  echo "Pull/sync CMS repo and: ln -sfn /path/to/repo \"$AQUA/KskinCMS\"" >&2
  read -r -p "Press Enter…" _
  exit 1
fi
export STEP_PAUSE_SEC="${STEP_PAUSE_SEC:-2.5}"
export STEP_PRE_PAUSE_SEC="${STEP_PRE_PAUSE_SEC:-0.8}"
export ONE_CLICK_KEEP_OPEN=1
REPORT="${REPORT_DIR:-$HOME/kskin-web(cms)-automation/reports}/KS-CMS-FRANCHISEE-REPORTS-001.html"
chmod +x "$CMS/FranchiseeReports_Module/run_franchisee_reports_report.bash" 2>/dev/null || true
# Do not exec — always open Chrome after the module runner (pass or fail).
set +e
bash "$CMS/FranchiseeReports_Module/run_franchisee_reports_report.bash"
STATUS=$?
set +e
# Always open HTML in Google Chrome after the run (pass or fail).
# Module runner also opens via one_click_finish; opening twice just focuses Chrome.
if [[ -f "$REPORT" ]]; then
  echo ""
  echo "Opening report in Google Chrome:"
  echo "  $REPORT"
  if [[ -d "/Applications/Google Chrome.app" ]]; then
    open -a "Google Chrome" "$REPORT" 2>/dev/null || open "$REPORT" 2>/dev/null || true
  else
    open "$REPORT" 2>/dev/null || true
  fi
else
  echo "WARNING: Report not found: $REPORT" >&2
fi
exit "$STATUS"
