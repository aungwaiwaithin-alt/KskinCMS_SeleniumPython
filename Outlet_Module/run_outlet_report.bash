#!/usr/bin/env bash
# One-click: Outlets regression + QA HTML report (live screenshots)
set -euo pipefail
AQUA="$HOME/AquaProjects"
REPORT_DIR="$HOME/kskin-web(cms)-automation/reports"
REPORT_HTML="$REPORT_DIR/KS-CMS-OUTLET-001_outlets.html"
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
export PYTHONPATH="$AQUA:$AQUA/MCP_Appium_Server/python"
mkdir -p "$REPORT_DIR"
cd "$AQUA"
echo "========================================"
echo "  Kskin CMS — Outlets"
echo "========================================"
python3 <<'PY'
from helpers.step_report import StepReporter
from KskinCMS.cms_auth import get_driver, quit_driver
from KskinCMS.Outlet_Module.Outlets import (
    open_browser, outlets_search_and_filters, create_new_outlet,
    change_outlet_status_from_listing, check_created_outlet_value, update_old_outlet,
)
OUT = "/Users/aungwaiwaithin/kskin-web(cms)-automation/reports/KS-CMS-OUTLET-001_outlets.html"
driver = get_driver()
r = StepReporter()
r.init(
    test_case_id="KS-CMS-OUTLET-001",
    test_name="Outlets — Selenium regression",
    subtitle="Staging: search/filters, create, ACTIVE↔INACTIVE, view, edit",
    environment=[
        ("Test Case ID", "KS-CMS-OUTLET-001"),
        ("Module", "Outlets"),
        ("URL", "https://staging-cms.kskinfacial.com/account/outlet-management/outlets"),
        ("Platform", "Web / Selenium / Chrome"),
        ("Screenshots", "Live capture per step"),
    ],
    driver=driver,
)
cases = [
    (1, "Open browser + navigate to Outlets", "Login + listing", open_browser),
    (2, "Search + region/status filters", "Matched/unmatched + filters", outlets_search_and_filters),
    (3, "Create new QA outlet (Publish)", "Published QA outlet listed", create_new_outlet),
    (4, "ACTIVE → INACTIVE → ACTIVE on QA outlet", "Toggle QA item only", change_outlet_status_from_listing),
    (5, "View created outlet", "Name/code readable", check_created_outlet_value),
    (6, "Edit outlet name", "Rename searchable", update_old_outlet),
]
failed=False
for num, title, expected, fn in cases:
    try:
        fn(); r.record_step(num, title, expected, "OK — step completed", "pass"); print(f"[PASS] Step {num}")
    except Exception as e:
        r.record_step(num, title, expected, f"FAIL: {e}", "fail"); print(f"[FAIL] Step {num}: {e}"); failed=True; break
r.emit(OUT); print("REPORT:", OUT); quit_driver()
raise SystemExit(1 if failed else 0)
PY
STATUS=$?
open "$REPORT_HTML" || true
echo "Finished exit $STATUS"
read -n 1 -s -p "Press any key to close..." || true
exit "$STATUS"

