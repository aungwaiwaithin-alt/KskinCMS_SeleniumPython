#!/usr/bin/env bash
set -euo pipefail
AQUA="$HOME/AquaProjects"
REPORT_HTML="$HOME/kskin-web(cms)-automation/reports/KS-CMS-THERAPISTS-001_therapists.html"
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
export PYTHONPATH="$AQUA:$AQUA/MCP_Appium_Server/python"
mkdir -p "$(dirname "$REPORT_HTML")"
cd "$AQUA"
echo "========================================"
echo "  Kskin CMS — Therapists"
echo "========================================"
python3 <<'PY'
from helpers.step_report import StepReporter
from KskinCMS.cms_auth import get_driver, quit_driver
from KskinCMS.Therapists_Module.Therapist import (
    open_browser, therapist_search_and_filter, add_new_therapist,
    listing_active_inactive_action, listing_inactive_active_action,
    rows_per_page_actions, check_created_therapist_value, update_old_therapist,
)
OUT = "/Users/aungwaiwaithin/kskin-web(cms)-automation/reports/KS-CMS-THERAPISTS-001_therapists.html"
driver = get_driver()
r = StepReporter()
r.init(
    test_case_id="KS-CMS-THERAPISTS-001",
    test_name="Therapists — Selenium regression",
    subtitle="Staging: search, create QA, ACTIVE↔INACTIVE, rows, view, edit",
    environment=[
        ("Test Case ID", "KS-CMS-THERAPISTS-001"),
        ("Module", "Therapists"),
        ("URL", "https://staging-cms.kskinfacial.com/account/therapist-management/therapists"),
        ("Platform", "Web / Selenium / Chrome"),
        ("Screenshots", "Live capture per step"),
    ],
    driver=driver,
)
cases = [
    (1, "Open browser + navigate to Therapists", "Login + listing", open_browser),
    (2, "Search + status filter", "Matched/unmatched + Active", therapist_search_and_filter),
    (3, "Create new QA therapist", "Form create + listed", add_new_therapist),
    (4, "ACTIVE → INACTIVE on QA therapist", "Toggle QA item only", listing_active_inactive_action),
    (5, "INACTIVE → ACTIVE on same QA therapist", "Toggle QA item only", listing_inactive_active_action),
    (6, "Rows per page + pagination", "Change page size", rows_per_page_actions),
    (7, "View created therapist", "Form values readable", check_created_therapist_value),
    (8, "Edit therapist", "Rename searchable", update_old_therapist),
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
