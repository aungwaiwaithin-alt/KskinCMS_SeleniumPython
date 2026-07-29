#!/usr/bin/env bash
# One-click: Franchisee Accounts regression + QA HTML report (with live screenshots)
# Double-click in Finder, or:  ./run_franchise_acc_report.bash

set -euo pipefail

AQUA="/Users/aungwaiwaithin/AquaProjects"
REPORT_DIR="/Users/aungwaiwaithin/kskin-web(cms)-automation/reports"
REPORT_HTML="${REPORT_DIR}/KS-CMS-FRANCHISE-001_franchisee_accounts.html"
STAMP="$(date +%Y%m%d_%H%M)"
LOG="${REPORT_DIR}/Franchise_report_${STAMP}.log"

mkdir -p "${REPORT_DIR}"
cd "${AQUA}"
export PYTHONPATH="${AQUA}:${AQUA}/MCP_Appium_Server/python"

echo "=============================================="
echo " Franchisee Accounts — run + HTML report"
echo " Started: $(date)"
echo " Log: ${LOG}"
echo "=============================================="

python3 <<'PY' 2>&1 | tee "${LOG}"
from helpers.step_report import StepReporter
from KskinCMS.cms_auth import get_driver, quit_driver
from KskinCMS.Franchise_Account_Module.FranchiseAcc import (
    open_browser,
    franchise_searching,
    listing_active_inactive_action,
    listing_inactive_active_action,
    pagination_and_rows_per_page_actions,
    create_new_franchise_account,
    view_back_created_acc_info,
    edit_franchise_account,
)

OUT = "/Users/aungwaiwaithin/kskin-web(cms)-automation/reports/KS-CMS-FRANCHISE-001_franchisee_accounts.html"
driver = get_driver()
r = StepReporter()
r.init(
    test_case_id="KS-CMS-FRANCHISE-001",
    test_name="Franchisee Accounts — Selenium regression",
    subtitle="Staging CMS: search, ACTIVE↔INACTIVE on QA item, pagination, create (via new outlet), view, edit",
    environment=[
        ("Test Case ID", "KS-CMS-FRANCHISE-001"),
        ("Module", "Franchisee Accounts"),
        ("URL", "https://staging-cms.kskinfacial.com/account/franchise-management/franchisee-accounts"),
        ("Platform", "Web / Selenium / Chrome"),
        ("Account", "aungwaiwaithin@codigo.co"),
        ("Viewport", "1920×1080"),
        ("Screenshots", "Live capture per step"),
    ],
    driver=driver,
)

cases = [
    (1, "Open browser + navigate to Franchisee Accounts",
     "Login + OTP; listing loads with search", open_browser),
    (2, "Search — franchise name / email / entity",
     "Matched name, email, and entity return correct rows", franchise_searching),
    (3, "ACTIVE → INACTIVE on new QA franchise",
     "Create unassigned outlet → create QA franchise → Set as inactive",
     listing_active_inactive_action),
    (4, "INACTIVE → ACTIVE on same QA franchise",
     "Set as active on the same QA item", listing_inactive_active_action),
    (5, "Rows per page + pagination",
     "Change page size; pagination when available",
     pagination_and_rows_per_page_actions),
    (6, "Create new franchise account",
     "Validations + create with newly published unassigned outlet",
     create_new_franchise_account),
    (7, "View created franchise",
     "Open edit/view form; email and name readable", view_back_created_acc_info),
    (8, "Edit franchise account",
     "Rename and save; searchable under new name", edit_franchise_account),
]

failed = False
for num, title, expected, fn in cases:
    try:
        fn()
        r.record_step(num, title, expected, "OK — step completed", "pass")
        print(f"[PASS] Step {num}: {title}")
    except Exception as e:
        r.record_step(num, title, expected, f"FAIL: {e}", "fail")
        print(f"[FAIL] Step {num}: {e}")
        failed = True
        break

r.emit(OUT)
print("REPORT:", OUT)
quit_driver()
raise SystemExit(1 if failed else 0)
PY
STATUS=$?

echo ""
echo "Opening report: ${REPORT_HTML}"
open "${REPORT_HTML}" || true

echo "Finished: $(date)  (exit ${STATUS})"
# Keep Terminal open when launched from Finder
if [[ -t 0 ]]; then
  read -r -p "Press Enter to close…"
fi
exit "${STATUS}"
