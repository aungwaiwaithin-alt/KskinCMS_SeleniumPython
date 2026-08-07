#!/usr/bin/env bash
# One-click: visible paced steps → HTML report → Google Chrome
set -uo pipefail
CMS_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=../scripts/one_click_lib.sh
source "$CMS_ROOT/scripts/one_click_lib.sh"

one_click_setup "KS-CMS-PRODUCT-001_products.html" "Kskin CMS — Products (Selenium)" || { one_click_finish 1; exit 1; }
export ONE_CLICK_KEEP_OPEN=1
one_click_run_python - <<'PY'
from helpers.step_report import StepReporter
from KskinCMS.cms_auth import get_driver, quit_driver
from KskinCMS.report_runner_util import run_paced_steps
from KskinCMS.Product_Module.Product import (
    open_browser, products_search_and_filter, add_new_product,
    listing_active_inactive_action, listing_inactive_active_action,
    rows_per_page_actions, check_created_product_value, update_old_product,
    product_required_validations, product_blank_add_draft, product_update_stock_restore,
)
import os
OUT = os.environ["CMS_REPORT_HTML"]
driver = get_driver()
r = StepReporter()
r.init(
    test_case_id="KS-CMS-PRODUCT-001",
    test_name="Products — Selenium regression",
    subtitle="Staging: search, Duplicate+Publish QA, status, view/edit, validations, blank Add draft, Update Stock",
    environment=[
        ("Test Case ID", "KS-CMS-PRODUCT-001"),
        ("Module", "Products"),
        ("URL", "https://staging-cms.kskinfacial.com/account/inventory/products"),
        ("Platform", "Web / Selenium / Chrome"),
        ("Screenshots", "Live capture per step"),
    ],
    driver=driver,
)
cases = [
    (1, "Open browser + navigate to Products", "Login + listing", open_browser),
    (2, "Search + status filter", "Matched/unmatched + Active", products_search_and_filter),
    (3, "Duplicate + Publish QA product", "Unique name/sku/pos listed", add_new_product),
    (4, "ACTIVE → INACTIVE on QA product", "Toggle QA item only", listing_active_inactive_action),
    (5, "INACTIVE → ACTIVE on same QA product", "Toggle QA item only", listing_inactive_active_action),
    (6, "Rows per page + pagination", "Change page size or N/A", rows_per_page_actions),
    (7, "View created product", "Form name readable", check_created_product_value),
    (8, "Edit product", "Rename + Publish Changes searchable", update_old_product),
    (9, "Required validations on blank Add", "Media required on empty Publish", product_required_validations),
    (10, "Blank Add → Save as draft", "Draft listed with name/sku/pos", product_blank_add_draft),
    (11, "Update Stock + restore on QA product", "Qty +1 then restore", product_update_stock_restore),
]
raise SystemExit(run_paced_steps(r, cases, quit_driver, OUT))
PY
STATUS=$?
one_click_finish "$STATUS"
exit $?
