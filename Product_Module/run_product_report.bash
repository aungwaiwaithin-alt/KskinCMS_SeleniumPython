#!/usr/bin/env bash
set -euo pipefail
AQUA="$HOME/AquaProjects"
REPORT_HTML="$HOME/kskin-web(cms)-automation/reports/KS-CMS-PRODUCT-001_products.html"
# Prefer Framework Python 3.8 (has selenium); avoid Homebrew python without deps
export PATH="/Library/Frameworks/Python.framework/Versions/3.8/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"
export PYTHONPATH="$AQUA:$AQUA/MCP_Appium_Server/python"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3.8 || command -v python3)}"
mkdir -p "$(dirname "$REPORT_HTML")"
cd "$AQUA"
echo "========================================"
echo "  Kskin CMS — Products"
echo "  Python: $PYTHON_BIN"
echo "========================================"
"$PYTHON_BIN" <<'PY'
from helpers.step_report import StepReporter
from KskinCMS.cms_auth import get_driver, quit_driver
from KskinCMS.Product_Module.Product import (
    open_browser, products_search_and_filter, add_new_product,
    listing_active_inactive_action, listing_inactive_active_action,
    rows_per_page_actions, check_created_product_value, update_old_product,
    product_required_validations, product_blank_add_draft, product_update_stock_restore,
)
OUT = "/Users/aungwaiwaithin/kskin-web(cms)-automation/reports/KS-CMS-PRODUCT-001_products.html"
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
        ("Actions", "Pencil/kebab Duplicate/status/Update Stock; Add new product; validations"),
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
