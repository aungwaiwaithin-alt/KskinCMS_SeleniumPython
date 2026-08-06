#!/usr/bin/env bash
set -euo pipefail
AQUA="$HOME/AquaProjects"
REPORT_HTML="$HOME/kskin-web(cms)-automation/reports/KS-CMS-FEE-MGMT-001.html"
export PATH="/Library/Frameworks/Python.framework/Versions/3.8/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"
export PYTHONPATH="$AQUA:$AQUA/MCP_Appium_Server/python"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3.8 || command -v python3)}"
mkdir -p "$(dirname "$REPORT_HTML")"
cd "$AQUA"
echo "========================================"
echo "  Kskin CMS — Fee Management (Playwright)"
echo "========================================"
"$PYTHON_BIN" <<'PY'
from helpers.step_report import StepReporter
from KskinCMS.playwright_auth import get_page, quit_page, PlaywrightShotAdapter
from KskinCMS.FeeManagement_Module.FeeManagement import (
    open_browser,
    fee_listing_asserts,
    fee_view_detail,
    fee_edit_default_required_validation,
    fee_edit_default_restore,
    fee_edit_minimum_fee_restore,
    fee_override_outlet_restore,
    fee_detail_rows_per_page,
)
OUT = "/Users/aungwaiwaithin/kskin-web(cms)-automation/reports/KS-CMS-FEE-MGMT-001.html"
page = get_page()
r = StepReporter()
r.init(
    test_case_id="KS-CMS-FEE-MGMT-001",
    test_name="Fee Management — Playwright regression",
    subtitle=(
        "Staging: listing, view, empty required validation, edit default % + "
        "Minimum Fee + outlet override (restore), rows/page"
    ),
    environment=[
        ("Test Case ID", "KS-CMS-FEE-MGMT-001"),
        ("Module", "Fee Management"),
        ("URL", "https://staging-cms.kskinfacial.com/account/franchise-management/fee-management"),
        ("Platform", "Web / Playwright / Chromium"),
        ("Screenshots", "Live capture per step"),
        (
            "Actions",
            "View + required validation + Edit default % + Minimum Fee + "
            "Override outlet % (always restore)",
        ),
    ],
    driver=PlaywrightShotAdapter(page),
)
cases = [
    (1, "Open Fee Management", "Login + listing", lambda: open_browser(page)),
    (2, "Listing fee types + eye", "4 fees + view actions", lambda: fee_listing_asserts(page)),
    (3, "View Platform Fee detail", "Default % + outlet table", lambda: fee_view_detail(page)),
    (4, "Edit default required validation", "Empty Percentage / Minimum Fee / both",
     lambda: fee_edit_default_required_validation(page)),
    (5, "Edit default % + restore", "Save temp then restore", lambda: fee_edit_default_restore(page)),
    (6, "Edit Minimum Fee + restore", "Dialog S$ min fee round-trip",
     lambda: fee_edit_minimum_fee_restore(page)),
    (7, "Outlet override + restore", "QA outlet % round-trip", lambda: fee_override_outlet_restore(page)),
    (8, "Detail rows/page", "Change page size", lambda: fee_detail_rows_per_page(page)),
]
failed = False
for num, title, expected, fn in cases:
    try:
        fn(); r.record_step(num, title, expected, "OK — step completed", "pass"); print(f"[PASS] Step {num}")
    except Exception as e:
        r.record_step(num, title, expected, f"FAIL: {e}", "fail"); print(f"[FAIL] Step {num}: {e}"); failed = True; break
r.emit(OUT); print("REPORT:", OUT); quit_page()
raise SystemExit(1 if failed else 0)
PY
STATUS=$?
open "$REPORT_HTML" || true
read -n 1 -s -p "Press any key to close..." || true
exit "$STATUS"
