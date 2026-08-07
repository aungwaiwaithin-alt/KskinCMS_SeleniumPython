#!/usr/bin/env bash
# One-click: visible paced steps → HTML report → Google Chrome
set -uo pipefail
CMS_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=../scripts/one_click_lib.sh
source "$CMS_ROOT/scripts/one_click_lib.sh"

one_click_setup "KS-CMS-GIFTBUNDLE-001_gift_bundles.html" "Kskin CMS — Gift Bundles (Selenium)" || { one_click_finish 1; exit 1; }
export ONE_CLICK_KEEP_OPEN=1
one_click_run_python - <<'PY'
from helpers.step_report import StepReporter
from KskinCMS.cms_auth import get_driver, quit_driver
from KskinCMS.report_runner_util import run_paced_steps
from KskinCMS.GiftBundle_Module.GiftBundle import (
    open_browser, gift_bundles_search_and_filter, gift_bundle_required_validations,
    add_new_gift_bundle, listing_active_inactive_action, listing_inactive_active_action,
    rows_per_page_actions, check_created_gift_bundle_value, update_old_gift_bundle,
)
import os
OUT = os.environ["CMS_REPORT_HTML"]
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
    (9, "Edit gift bundle", "Rename + Publish Changes searchable", update_old_gift_bundle),
]
raise SystemExit(run_paced_steps(r, cases, quit_driver, OUT))
PY
STATUS=$?
one_click_finish "$STATUS"
exit $?
