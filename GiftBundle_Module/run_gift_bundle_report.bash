#!/usr/bin/env bash
set -euo pipefail
AQUA="$HOME/AquaProjects"
REPORT_HTML="$HOME/kskin-web(cms)-automation/reports/KS-CMS-GIFTBUNDLE-001_gift_bundles.html"
export PATH="/Library/Frameworks/Python.framework/Versions/3.8/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"
export PYTHONPATH="$AQUA:$AQUA/MCP_Appium_Server/python"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3.8 || command -v python3)}"
mkdir -p "$(dirname "$REPORT_HTML")"
cd "$AQUA"
echo "========================================"
echo "  Kskin CMS — Gift Bundles"
echo "  Python: $PYTHON_BIN"
echo "========================================"
"$PYTHON_BIN" <<'PY'
from helpers.step_report import StepReporter
from KskinCMS.cms_auth import get_driver, quit_driver
from KskinCMS.GiftBundle_Module.GiftBundle import (
    open_browser, gift_bundles_search_and_filter, gift_bundle_required_validations,
    add_new_gift_bundle, listing_active_inactive_action, listing_inactive_active_action,
    rows_per_page_actions, check_created_gift_bundle_value, update_old_gift_bundle,
)
OUT = "/Users/aungwaiwaithin/kskin-web(cms)-automation/reports/KS-CMS-GIFTBUNDLE-001_gift_bundles.html"
driver = get_driver()
r = StepReporter()
r.init(
    test_case_id="KS-CMS-GIFTBUNDLE-001",
    test_name="Gift Bundles — Selenium regression",
    subtitle="Staging: search, validations, Duplicate+Publish QA, status, rows, view, edit",
    environment=[
        ("Test Case ID", "KS-CMS-GIFTBUNDLE-001"),
        ("Module", "Gift Bundles"),
        ("URL", "https://staging-cms.kskinfacial.com/account/inventory/gift-bundles"),
        ("Platform", "Web / Selenium / Chrome"),
        ("Screenshots", "Live capture per step"),
        ("Actions", "Add new; kebab Duplicate / status; edit Publish Changes"),
        ("Validations", "Price / max purchase / bundle name required"),
        ("QA source", "Duplicate ComboC+PureMistToner_NewBundle"),
    ],
    driver=driver,
)
cases = [
    (1, "Open browser + navigate to Gift Bundles", "Login + listing", open_browser),
    (2, "Search + status filter", "Matched/unmatched + Active", gift_bundles_search_and_filter),
    (3, "Required validation messages", "Price / MPL / name required", gift_bundle_required_validations),
    (4, "Duplicate → draft → Set as active QA", "Unique name listed ACTIVE", add_new_gift_bundle),
    (5, "ACTIVE → INACTIVE on QA bundle", "Toggle QA item only", listing_active_inactive_action),
    (6, "INACTIVE → ACTIVE on same QA", "Toggle QA item only", listing_inactive_active_action),
    (7, "Rows per page + pagination", "Change page size or N/A", rows_per_page_actions),
    (8, "View created gift bundle", "Edit form name/price readable", check_created_gift_bundle_value),
    (9, "Edit gift bundle", "Rename + price + Publish Changes searchable", update_old_gift_bundle),
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
