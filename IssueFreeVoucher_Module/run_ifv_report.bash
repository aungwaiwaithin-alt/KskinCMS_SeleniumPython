#!/usr/bin/env bash
set -euo pipefail
AQUA="$HOME/AquaProjects"
REPORT_HTML="$HOME/kskin-web(cms)-automation/reports/KS-CMS-IFV-001_issue_free_vouchers.html"
# Prefer Framework Python 3.8 (has selenium); avoid Homebrew python without deps
export PATH="/Library/Frameworks/Python.framework/Versions/3.8/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"
export PYTHONPATH="$AQUA:$AQUA/MCP_Appium_Server/python"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3.8 || command -v python3)}"
mkdir -p "$(dirname "$REPORT_HTML")"
cd "$AQUA"
echo "========================================"
echo "  Kskin CMS — Issue Free Vouchers"
echo "  Python: $PYTHON_BIN"
echo "========================================"
"$PYTHON_BIN" <<'PY'
from helpers.step_report import StepReporter
from KskinCMS.cms_auth import get_driver, quit_driver
from KskinCMS.IssueFreeVoucher_Module.IFV import (
    open_browser, ifv_search_and_filter, rows_per_page_actions, add_new_ifv,
    check_created_ifv_value,
)
OUT = "/Users/aungwaiwaithin/kskin-web(cms)-automation/reports/KS-CMS-IFV-001_issue_free_vouchers.html"
driver = get_driver()
r = StepReporter()
r.init(
    test_case_id="KS-CMS-IFV-001",
    test_name="Issue Free Vouchers — Selenium regression",
    subtitle="Staging: search, filter, rows, create+publish, view-verify (no edit)",
    environment=[
        ("Test Case ID", "KS-CMS-IFV-001"),
        ("Module", "Issue Free Vouchers (view-only after publish)"),
        ("URL", "https://staging-cms.kskinfacial.com/account/customer-management/issue-free-vouchers"),
        ("Platform", "Web / Selenium / Chrome"),
        ("Screenshots", "Live capture per step"),
    ],
    driver=driver,
)
cases = [
    (1, "Open browser + navigate to IFV", "Login + listing", open_browser),
    (2, "Search + type filter", "Matched/unmatched + $ off", ifv_search_and_filter),
    (3, "Rows per page + pagination", "Change page size", rows_per_page_actions),
    (4, "Create + publish QA IFV", "Form publish + listed", add_new_ifv),
    (5, "View created IFV", "All create fields shown correctly", check_created_ifv_value),
]
failed = False
for num, title, expected, fn in cases:
    try:
        fn(); r.record_step(num, title, expected, "OK — step completed", "pass"); print(f"[PASS] Step {num}")
    except Exception as e:
        r.record_step(num, title, expected, f"FAIL: {e}", "fail"); print(f"[FAIL] Step {num}: {e}"); failed = True; break
r.emit(OUT); print("REPORT:", OUT); quit_driver()
raise SystemExit(1 if failed else 0)
PY
STATUS=$?
open "$REPORT_HTML" || true
read -n 1 -s -p "Press any key to close..." || true
exit "$STATUS"
