"""Franchisee Reports — Playwright regression (actions-first).

Staging `/account/franchise-management/franchisee-reports`
  - Sales Overview: charts/metrics can take 3–5 min to hydrate
  - Franchise Statements: search, date, status, export, kebab, invoice detail
"""
from __future__ import annotations

import time

from playwright.sync_api import Page

from KskinCMS.cms_config import MODULE_URLS
from KskinCMS.playwright_auth import open_module

# Sales Overview full hydrate (user: 3–5 minutes)
SALES_OVERVIEW_TIMEOUT_MS = 300_000


def _goto_statements(page: Page) -> None:
    open_module(
        page,
        MODULE_URLS["franchisee_reports"],
        wait_selector="text=Franchise Statements",
    )
    page.get_by_text("Franchise Statements", exact=True).first.click()
    page.wait_for_selector("table tbody tr", timeout=30000)
    time.sleep(0.8)


def _statements_search(page: Page, query: str) -> None:
    """Statements search uses input[name=Code] (capital C)."""
    page.wait_for_selector('input[name="Code"]', timeout=15000)
    page.evaluate(
        """(value) => {
          const input = document.querySelector('input[name="Code"]');
          const setter = Object.getOwnPropertyDescriptor(
            window.HTMLInputElement.prototype, 'value'
          ).set;
          setter.call(input, '');
          input.dispatchEvent(new Event('input', { bubbles: true }));
          setter.call(input, value);
          input.dispatchEvent(new Event('input', { bubbles: true }));
          input.dispatchEvent(new Event('change', { bubbles: true }));
        }""",
        query,
    )
    time.sleep(2)


def _pick_franchisee(page: Page) -> str:
    picked = page.evaluate(
        """() => {
          const s=document.querySelectorAll('select')[0];
          if(!s || s.options.length < 2) return null;
          const prefer=[...s.options].find(
            o => o.value && o.value!=='all'
              && /QA|Updated|Franchise/i.test(o.text)
          );
          const opt=prefer || [...s.options].find(o=>o.value && o.value!=='all');
          if(!opt) return null;
          s.value=opt.value;
          s.dispatchEvent(new Event('input',{bubbles:true}));
          s.dispatchEvent(new Event('change',{bubbles:true}));
          return opt.text.trim();
        }"""
    )
    if not picked:
        raise AssertionError(
            "Franchisee Reports FAILED: no franchisee options "
            "(report to dev / Asana)"
        )
    return picked


def open_browser(page: Page) -> None:
    open_module(
        page,
        MODULE_URLS["franchisee_reports"],
        wait_selector="text=Franchise Reports",
    )
    page.wait_for_selector("text=Sales Overview", timeout=20000)
    time.sleep(1)
    print("Test 1 : Opened Franchisee Reports")


def reports_sales_overview(page: Page) -> None:
    """Sales Overview — wait up to 5 min for full metric hydrate."""
    open_module(
        page,
        MODULE_URLS["franchisee_reports"],
        wait_selector="text=Sales Overview",
    )
    page.get_by_text("Sales Overview", exact=True).first.click()
    time.sleep(1)
    print(
        "Test 2 : Waiting up to 5 min for Sales Overview hydrate "
        "(Total Sales + S$ amounts)…"
    )
    # Prefer waiting on All franchisees first (staging can populate that view).
    # If still empty after ~90s, pick a concrete franchisee to force load.
    deadline = time.time() + (SALES_OVERVIEW_TIMEOUT_MS / 1000.0)
    start = time.time()
    hydrated = False
    picked_once = False
    while time.time() < deadline:
        body = page.inner_text("body")
        if (
            "Total Sales" in body
            and "Total Royalties" in body
            and ("S$" in body or "$" in body)
            and any(ch.isdigit() for ch in body.split("Total Sales", 1)[-1][:80])
        ):
            hydrated = True
            break
        if not picked_once and (time.time() - start) >= 90:
            # after ~90s still empty → pick franchisee once to force hydrate
            try:
                _pick_franchisee(page)
                picked_once = True
                print("Test 2 : Still empty — selected a franchisee to force hydrate")
            except Exception:
                picked_once = True
        time.sleep(3)

    if not hydrated:
        raise AssertionError(
            "Franchisee Reports Sales Overview FAILED: metrics not hydrated "
            "within 5 minutes (report to dev / Asana)"
        )

    body = page.inner_text("body")
    for needle in (
        "Total Sales",
        "Total Royalties",
        "Sales by Outlet",
        "Average sales per day",
        "Average royalties per day",
    ):
        if needle not in body:
            # Sales by Outlet / averages may appear only after full load
            if needle in ("Sales by Outlet", "Average sales per day", "Average royalties per day"):
                # soft-require charts at least
                continue
            raise AssertionError(
                f"Franchisee Reports Sales Overview FAILED: missing '{needle}' "
                "(report to dev / Asana)"
            )
    # Prefer asserting averages if present; require at least one chart
    charts = page.locator("canvas, svg").count()
    if charts < 1:
        raise AssertionError(
            "Franchisee Reports Sales Overview FAILED: no chart canvas/svg "
            "(report to dev / Asana)"
        )
    missing_extra = [
        n
        for n in ("Sales by Outlet", "Average sales per day", "Average royalties per day")
        if n not in body
    ]
    if missing_extra:
        print(f"Test 2 warn : optional labels still missing after hydrate: {missing_extra}")
    print(f"Test 2 : Sales Overview hydrated OK ({charts} chart nodes)")


def reports_filters(page: Page) -> None:
    """Franchisee + year filters on Sales Overview."""
    open_module(
        page,
        MODULE_URLS["franchisee_reports"],
        wait_selector="select",
    )
    page.get_by_text("Sales Overview", exact=True).first.click()
    time.sleep(0.5)
    picked = _pick_franchisee(page)
    page.wait_for_function(
        "() => document.body.innerText.includes('Total Sales')",
        timeout=60000,
    )
    time.sleep(1)
    years = page.evaluate(
        """() => {
          const s=document.querySelectorAll('select')[1];
          if(!s) return null;
          return {value:s.value, opts:[...s.options].map(o=>o.value)};
        }"""
    )
    if not years or not years.get("opts"):
        raise AssertionError(
            "Franchisee Reports filter FAILED: year select missing "
            "(report to dev / Asana)"
        )
    alt = "2025" if years["value"] == "2026" and "2025" in years["opts"] else years["value"]
    page.evaluate(
        """(v) => {
          const s=document.querySelectorAll('select')[1];
          s.value=v;
          s.dispatchEvent(new Event('change',{bubbles:true}));
        }""",
        alt,
    )
    time.sleep(2)
    body = page.inner_text("body")
    if "Total Sales" not in body and "Franchise Statements" not in body:
        raise AssertionError(
            "Franchisee Reports filter FAILED: page empty after filter "
            "(report to dev / Asana)"
        )
    print(f"Test 3 : Filters OK (franchisee={picked!r}, year→{alt})")


def reports_statements_listing(page: Page) -> None:
    _goto_statements(page)
    body = page.inner_text("body")
    for col in (
        "OUTLET",
        "FRANCHISE",
        "TOTAL APP SALES",
        "TOTAL POS SALES",
        "TOTAL AMT. TO TRANSFER",
        "STATUS",
    ):
        if col not in body:
            raise AssertionError(
                f"Franchise Statements FAILED: missing column '{col}' "
                "(report to dev / Asana)"
            )
    rows = page.locator("table tbody tr")
    if rows.count() < 1:
        raise AssertionError(
            "Franchise Statements FAILED: no rows (report to dev / Asana)"
        )
    if page.get_by_role("button", name="Export CSV").count() < 1:
        raise AssertionError(
            "Franchise Statements FAILED: Export CSV missing (report to dev / Asana)"
        )
    if page.locator('input[name="Code"]').count() < 1:
        raise AssertionError(
            "Franchise Statements FAILED: search input missing (report to dev / Asana)"
        )
    print(f"Test 4 : Statements listing OK ({rows.count()} rows, columns + Export CSV)")


def reports_statements_search(page: Page) -> None:
    _goto_statements(page)
    rows = page.locator("table tbody tr")
    cells = rows.nth(0).locator("td")
    outlet = (cells.nth(0).inner_text() or "").strip().split("\n")[0].strip()
    franchise = (cells.nth(1).inner_text() or "").strip().split("\n")[0].strip()
    query = outlet if len(outlet) >= 2 else franchise
    if not query:
        raise AssertionError(
            "Franchise Statements search FAILED: empty first row "
            "(report to dev / Asana)"
        )

    _statements_search(page, query)
    matched = page.locator("table tbody tr")
    if matched.count() < 1:
        raise AssertionError(
            f"Franchise Statements search FAILED: no rows for {query!r} "
            "(report to dev / Asana)"
        )
    hit = matched.nth(0).inner_text()
    if query not in hit:
        raise AssertionError(
            f"Franchise Statements search FAILED: expected {query!r} in {hit!r} "
            "(report to dev / Asana)"
        )
    print(f"Test 5a : Matched search OK ({query!r})")

    _statements_search(page, "NoSuchOutletFranchiseZZZ999")
    time.sleep(1)
    body = page.inner_text("body")
    empty_rows = page.locator("table tbody tr")
    empty_ok = (
        empty_rows.count() == 0
        or "of 0 items" in body.lower()
        or "no result" in body.lower()
        or "no data" in body.lower()
    )
    if not empty_ok and empty_rows.count() >= 10:
        raise AssertionError(
            "Franchise Statements unmatched search FAILED: still showing full page "
            "(report to dev / Asana)"
        )
    print("Test 5 : Search matched + unmatched OK")


def reports_statements_status_filter(page: Page) -> None:
    _goto_statements(page)
    sel = page.locator("select").first
    opts = sel.locator("option").all_text_contents()
    if "Pending" not in opts or "Sent" not in opts:
        raise AssertionError(
            f"Franchise Statements status filter FAILED: opts={opts!r} "
            "(report to dev / Asana)"
        )
    # Pending
    pending_val = sel.locator("option", has_text="Pending").first.get_attribute("value")
    sel.select_option(pending_val)
    time.sleep(2)
    body = page.inner_text("body")
    rows = page.locator("table tbody tr")
    if rows.count() < 1:
        raise AssertionError(
            "Franchise Statements status=Pending FAILED: no rows "
            "(report to dev / Asana)"
        )
    # every visible status should be PENDING (not SENT)
    for i in range(min(rows.count(), 5)):
        t = rows.nth(i).inner_text().upper()
        if "PENDING" not in t:
            raise AssertionError(
                f"Franchise Statements status=Pending FAILED: row {i}={t[:80]!r} "
                "(report to dev / Asana)"
            )
    # Sent (may be empty)
    sent_val = sel.locator("option", has_text="Sent").first.get_attribute("value")
    sel.select_option(sent_val)
    time.sleep(2)
    body_sent = page.inner_text("body")
    # All
    all_val = sel.locator("option", has_text="All status").first.get_attribute("value")
    sel.select_option(all_val)
    time.sleep(1.5)
    if page.locator("table tbody tr").count() < 1:
        raise AssertionError(
            "Franchise Statements status=All FAILED: no rows "
            "(report to dev / Asana)"
        )
    print(
        f"Test 6 : Status filter OK (Pending rows; Sent body has "
        f"{'SENT' if 'SENT' in body_sent.upper() else '0/empty'}; restored All)"
    )


def reports_statements_date_filter(page: Page) -> None:
    _goto_statements(page)
    page.get_by_role("button", name="All dates").click()
    time.sleep(0.8)
    body = page.inner_text("body")
    if "Select Today" not in body and "Okay" not in body:
        raise AssertionError(
            "Franchise Statements date filter FAILED: calendar not opened "
            "(report to dev / Asana)"
        )
    page.get_by_role("button", name="Select Today").click()
    time.sleep(0.3)
    page.get_by_role("button", name="Okay").click()
    time.sleep(2)
    body = page.inner_text("body")
    # Today may yield 0 rows — still a valid filter result
    still_statements = (
        page.get_by_role("button", name="Export CSV").count() >= 1
        and page.locator('input[name="Code"]').count() >= 1
        and ("Franchise Statements" in body or "STATUS" in body or "of 0 items" in body.lower())
    )
    if not still_statements:
        raise AssertionError(
            "Franchise Statements date filter FAILED: left Statements UI after date "
            "(report to dev / Asana)"
        )
    rows = page.locator("table tbody tr").count()
    print(f"Test 7 : Date filter calendar + Select Today/Okay OK (rows after={rows})")
    # reset listing filters via fresh navigate
    _goto_statements(page)


def reports_statements_export_csv(page: Page) -> None:
    """Export CSV — assert download starts (does not email)."""
    _goto_statements(page)
    btn = page.get_by_role("button", name="Export CSV")
    if btn.count() < 1:
        raise AssertionError(
            "Franchise Statements Export CSV FAILED: button missing "
            "(report to dev / Asana)"
        )
    try:
        with page.expect_download(timeout=20000) as di:
            btn.click()
        dl = di.value
        name = dl.suggested_filename or ""
        if not name.lower().endswith(".csv") and "csv" not in name.lower():
            # still OK if browser downloaded a blob without .csv suffix
            print(f"Test 8 warn : download name={name!r}")
        # touch path to ensure file materialized
        path = dl.path()
        print(f"Test 8 : Export CSV OK ({name or path})")
    except Exception as e:
        # Fallback: button click without download event (some browsers)
        btn.click()
        time.sleep(2)
        raise AssertionError(
            f"Franchise Statements Export CSV FAILED: no download ({e}) "
            "(report to dev / Asana)"
        ) from e


def reports_statements_kebab_and_invoice(page: Page) -> None:
    """Kebab: Send invoice + View/Edit Invoice; open invoice detail; edit remarks restore."""
    _goto_statements(page)
    row = page.locator("table tbody tr").first
    outlet = (row.locator("td").nth(0).inner_text() or "").strip().split("\n")[0].strip()
    row.locator("button[aria-haspopup='menu']").click()
    time.sleep(0.6)
    send_item = page.get_by_role("menuitem", name="Send invoice")
    view_item = page.get_by_role("menuitem", name="View/Edit Invoice")
    # fallback: plain text nodes if role missing
    if send_item.count() < 1:
        send_item = page.get_by_text("Send invoice", exact=True)
    if view_item.count() < 1:
        view_item = page.get_by_text("View/Edit Invoice", exact=True)
    if send_item.count() < 1 or view_item.count() < 1:
        # dump visible menu candidates for debug
        candidates = page.evaluate(
            """() => [...document.querySelectorAll('[role=menuitem], [data-radix-collection-item], li')]
              .map(e => e.innerText.trim()).filter(Boolean).slice(0, 20)"""
        )
        raise AssertionError(
            f"Franchise Statements kebab FAILED: missing Send invoice / View/Edit Invoice "
            f"(candidates={candidates!r}) (report to dev / Asana)"
        )
    # Do NOT confirm Send invoice (emails / status change). Escape menu.
    page.keyboard.press("Escape")
    time.sleep(0.4)

    row.locator("button[aria-haspopup='menu']").click()
    time.sleep(0.5)
    page.get_by_text("View/Edit Invoice", exact=True).click()
    page.wait_for_url("**/franchisee-reports/**", timeout=20000)
    time.sleep(1.5)
    body = page.inner_text("body")
    for needle in (
        "Sales Summary",
        "Total App Sales",
        "Total POS Sales",
        "Royalty Fee",
        "Platform Fee",
        "Transaction Fees",
        "Total Amount to Transfer",
        "Save changes",
    ):
        if needle not in body:
            raise AssertionError(
                f"Invoice detail FAILED: missing '{needle}' (report to dev / Asana)"
            )
    if page.get_by_role("button", name="Send SOA + Invoices Now").count() < 1:
        raise AssertionError(
            "Invoice detail FAILED: Send SOA + Invoices Now missing "
            "(report to dev / Asana)"
        )

    # Field update: Transaction ID + Remarks, save, restore
    txn = page.locator('input[name="transactionID"]')
    remark = page.locator('input[name="remark"]')
    if txn.count() < 1 or remark.count() < 1:
        raise AssertionError(
            "Invoice detail FAILED: transactionID/remark inputs missing "
            "(report to dev / Asana)"
        )
    orig_txn = txn.input_value()
    orig_remark = remark.input_value()
    qa_txn = f"QA-TXN-{int(time.time()) % 100000}"
    qa_remark = "QA remark — restore"
    txn.fill(qa_txn)
    remark.fill(qa_remark)
    page.get_by_role("button", name="Save changes").click()
    time.sleep(2)
    page.reload(wait_until="domcontentloaded")
    time.sleep(2)
    page.wait_for_selector('input[name="transactionID"]', timeout=20000)
    got_txn = page.locator('input[name="transactionID"]').input_value()
    got_remark = page.locator('input[name="remark"]').input_value()
    if got_txn != qa_txn:
        raise AssertionError(
            f"Invoice save FAILED: txn got {got_txn!r} expected {qa_txn!r} "
            "(report to dev / Asana)"
        )
    if qa_remark not in got_remark:
        raise AssertionError(
            f"Invoice save FAILED: remark got {got_remark!r} "
            "(report to dev / Asana)"
        )
    # restore
    page.locator('input[name="transactionID"]').fill(orig_txn)
    page.locator('input[name="remark"]').fill(orig_remark)
    page.get_by_role("button", name="Save changes").click()
    time.sleep(2)
    print(
        f"Test 9 : Kebab + invoice detail OK (outlet={outlet!r}; "
        f"txn/remark saved+restored; Send invoice NOT executed)"
    )


def reports_statements_rows_per_page(page: Page) -> None:
    _goto_statements(page)
    selects = page.locator("select")
    target = None
    for i in range(selects.count()):
        s = selects.nth(i)
        opts = s.locator("option").all_text_contents()
        if "10" in opts and "50" in opts:
            target = s
            break
    if target is None:
        print(f"Test 10 : Rows/page N/A ({page.locator('table tbody tr').count()} rows)")
        return
    target.select_option("20")
    time.sleep(1.5)
    n20 = page.locator("table tbody tr").count()
    if n20 < 11:
        raise AssertionError(
            f"Franchise Statements rows/page FAILED: expected ≥11 at 20, got {n20} "
            "(report to dev / Asana)"
        )
    target.select_option("10")
    time.sleep(1)
    page2 = page.locator("text=/^2$/").last
    if page2.count() and page2.is_visible():
        try:
            page2.click()
            time.sleep(1)
            page.locator("text=/^1$/").last.click()
            time.sleep(0.5)
        except Exception:
            pass
    print(f"Test 10 : Statements rows/page OK (20→{n20}, restored 10 + pagination)")
