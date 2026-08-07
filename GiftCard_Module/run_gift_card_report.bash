#!/usr/bin/env bash
# One-click: visible paced steps → HTML report → Google Chrome
set -uo pipefail
CMS_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=../scripts/one_click_lib.sh
source "$CMS_ROOT/scripts/one_click_lib.sh"

one_click_setup "KS-CMS-GIFTCARD-001_gift_card.html" "Kskin CMS — Gift Card (Selenium)" || { one_click_finish 1; exit 1; }
export ONE_CLICK_KEEP_OPEN=1
one_click_run_python - <<'PY'
from helpers.step_report import StepReporter
from KskinCMS.cms_auth import get_driver, quit_driver
from KskinCMS.report_runner_util import run_paced_steps
from KskinCMS.GiftCard_Module.GiftCard import (
    open_browser, gift_card_view_page, open_edit_form,
    gift_card_required_validations, update_gift_card,
    listing_active_inactive_action, listing_inactive_active_action,
)
import os
OUT = os.environ["CMS_REPORT_HTML"]
driver = get_driver()
r = StepReporter()
r.init(
    test_case_id="KS-CMS-GIFTCARD-001",
    test_name="Gift Card — Selenium regression",
    subtitle="Staging: view, validations, update+restore, ACTIVE↔INACTIVE",
    environment=[
        ("Test Case ID", "KS-CMS-GIFTCARD-001"),
        ("Module", "Gift Card"),
        ("URL", "https://staging-cms.kskinfacial.com/account/inventory/gift-card"),
        ("Platform", "Web / Selenium / Chrome"),
        ("Screenshots", "Live capture per step"),
    ],
    driver=driver,
)
cases = [
    (1, "Open browser + navigate to Gift Card", "Login + view page", open_browser),
    (2, "View page asserts", "ACTIVE + amounts + description + Edit", gift_card_view_page),
    (3, "Open Edit form (hydrated)", "Publish + fields", open_edit_form),
    (4, "Required + validation messages", "User-facing errs", gift_card_required_validations),
    (5, "Update all fields + Publish + restore", "Verify then restore", update_gift_card),
    (6, "ACTIVE → INACTIVE", "More actions", listing_active_inactive_action),
    (7, "INACTIVE → ACTIVE", "More actions", listing_inactive_active_action),
]
raise SystemExit(run_paced_steps(r, cases, quit_driver, OUT))
PY
STATUS=$?
one_click_finish "$STATUS"
exit "$STATUS"
