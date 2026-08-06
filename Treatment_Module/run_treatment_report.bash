#!/usr/bin/env bash
set -euo pipefail
AQUA="$HOME/AquaProjects"
REPORT_HTML="$HOME/kskin-web(cms)-automation/reports/KS-CMS-TREATMENT-001_treatments.html"
export PATH="/Library/Frameworks/Python.framework/Versions/3.8/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"
export PYTHONPATH="$AQUA:$AQUA/MCP_Appium_Server/python"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3.8 || command -v python3)}"
mkdir -p "$(dirname "$REPORT_HTML")"
cd "$AQUA"
echo "========================================"
echo "  Kskin CMS — Treatments"
echo "  Python: $PYTHON_BIN"
echo "========================================"
"$PYTHON_BIN" <<'PY'
from helpers.step_report import StepReporter
from KskinCMS.cms_auth import get_driver, quit_driver
from KskinCMS.Treatment_Module.Treatment import (
    open_browser, treatments_search_and_filter, add_new_treatment,
    listing_active_inactive_action, listing_inactive_active_action,
    rows_per_page_actions, check_created_treatment_value, update_old_treatment,
)
OUT = "/Users/aungwaiwaithin/kskin-web(cms)-automation/reports/KS-CMS-TREATMENT-001_treatments.html"
driver = get_driver()
r = StepReporter()
r.init(
    test_case_id="KS-CMS-TREATMENT-001",
    test_name="Treatments — Selenium regression",
    subtitle="Staging: search, Duplicate Cleanse→draft→active, ACTIVE↔INACTIVE, view, edit (Effect≤100)",
    environment=[
        ("Test Case ID", "KS-CMS-TREATMENT-001"),
        ("Module", "Treatments"),
        ("URL", "https://staging-cms.kskinfacial.com/account/inventory/treatments"),
        ("Platform", "Web / Selenium / Chrome"),
        ("Screenshots", "Live capture per step"),
        ("Actions", "Pencil edit; kebab Duplicate / status"),
        ("Note", "Publish disabled if Effect > 100 chars"),
    ],
    driver=driver,
)
cases = [
    (1, "Open browser + navigate to Treatments", "Login + listing", open_browser),
    (2, "Search + status filter", "Matched/unmatched + Active", treatments_search_and_filter),
    (3, "Duplicate Cleanse → QA active", "Draft then Set as active; Effect≤100", add_new_treatment),
    (4, "ACTIVE → INACTIVE on QA treatment", "Toggle QA item only", listing_active_inactive_action),
    (5, "INACTIVE → ACTIVE on same QA treatment", "Toggle QA item only", listing_inactive_active_action),
    (6, "Rows per page + pagination", "Change page size or N/A", rows_per_page_actions),
    (7, "View created treatment", "Form name readable; Effect capped", check_created_treatment_value),
    (8, "Edit treatment", "Rename searchable", update_old_treatment),
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
