"""Fee Management — Playwright regression (actions-first).

Staging `/account/franchise-management/fee-management`
  - Listing: Platform / Transaction / Royalty / A&P fees + eye view
  - Detail: default % + outlet overrides; Edit default / Override dialogs
  - Always restore fee values after QA edits
"""
from __future__ import annotations

import re
import time

from playwright.sync_api import Page

from KskinCMS.cms_config import MODULE_URLS
from KskinCMS.playwright_auth import open_module

FEE_TYPES = ("Platform Fee", "Transaction Fee", "Royalty Fee", "A&P Fee")


def _dialog(page: Page):
    dlg = page.locator("[role='dialog']").last
    dlg.wait_for(state="visible", timeout=15000)
    return dlg


def _click_edit_default(page: Page) -> None:
    """Open Edit default percentage dialog (robust against overlay / naming)."""
    page.wait_for_selector("text=Default percentage", timeout=20000)
    time.sleep(0.3)
    candidates = [
        page.get_by_role("button", name=re.compile(r"edit\s*default\s*percentage", re.I)),
        page.get_by_role("button", name=re.compile(r"edit\s*default", re.I)),
        page.locator("button", has_text=re.compile(r"edit\s*default\s*percentage", re.I)),
        page.locator("button", has_text=re.compile(r"edit\s*default", re.I)),
        page.get_by_text(re.compile(r"edit\s*default\s*percentage", re.I)),
    ]
    last_err = None
    for loc in candidates:
        try:
            target = loc.first
            if target.count() < 1:
                continue
            target.scroll_into_view_if_needed(timeout=5000)
            time.sleep(0.2)
            try:
                target.click(timeout=8000)
            except Exception:
                target.click(timeout=8000, force=True)
            _dialog(page)
            return
        except Exception as e:
            last_err = e
            continue
    # JS fallback — click first matching button text
    clicked = page.evaluate(
        """() => {
          const re = /edit\\s*default/i;
          const nodes = [...document.querySelectorAll('button, a, [role="button"]')];
          const el = nodes.find(n => re.test((n.innerText || n.textContent || '').trim()));
          if (!el) return false;
          el.scrollIntoView({block:'center'});
          el.click();
          return true;
        }"""
    )
    if clicked:
        _dialog(page)
        return
    raise AssertionError(
        "Fee edit default FAILED: cannot click Edit default percentage "
        f"({last_err!r}) (report to dev / Asana)"
    )


def _fill_named(dlg, name: str, value: str) -> None:
    inp = dlg.locator(f'input[name="{name}"]').first
    inp.click()
    inp.fill("")
    inp.fill(value)
    # React-friendly events
    inp.evaluate(
        """(el, v) => {
          const setter = Object.getOwnPropertyDescriptor(
            window.HTMLInputElement.prototype, 'value'
          ).set;
          setter.call(el, v);
          el.dispatchEvent(new Event('input', { bubbles: true }));
          el.dispatchEvent(new Event('change', { bubbles: true }));
        }""",
        value,
    )


def _dialog_save(page: Page, dlg=None) -> None:
    """Click dialog Save (Playwright role click is flaky on this modal)."""
    root = dlg if dlg is not None else page.locator("[role='dialog']").last
    btn = root.locator("button[type='submit']").filter(
        has_text=re.compile(r"^\s*save\s*$", re.I)
    )
    if btn.count() < 1:
        btn = root.locator("button").filter(has_text=re.compile(r"^\s*save\s*$", re.I))
    if btn.count() >= 1:
        try:
            btn.first.click(timeout=5000)
            return
        except Exception:
            try:
                btn.first.click(timeout=5000, force=True)
                return
            except Exception:
                pass
    clicked = page.evaluate(
        """() => {
          const dlg = [...document.querySelectorAll('[role=dialog]')].pop();
          if (!dlg) return false;
          const btn = [...dlg.querySelectorAll('button')].find(b =>
            /^\\s*save\\s*$/i.test((b.innerText || '').trim())
          );
          if (!btn) return false;
          btn.click();
          return true;
        }"""
    )
    if not clicked:
        raise AssertionError(
            "Fee dialog FAILED: Save button not clickable (report to dev / Asana)"
        )


def _dialog_cancel(page: Page, dlg=None) -> None:
    root = dlg if dlg is not None else page.locator("[role='dialog']").last
    cancel = root.locator("button").filter(has_text=re.compile(r"^\s*cancel\s*$", re.I))
    if cancel.count() >= 1:
        try:
            cancel.first.click(timeout=5000)
        except Exception:
            cancel.first.click(timeout=5000, force=True)
    else:
        page.keyboard.press("Escape")
    time.sleep(0.3)


def _open_platform_fee(page: Page) -> None:
    open_module(
        page,
        MODULE_URLS["fee_management"],
        wait_selector="text=Fee Management",
    )
    page.wait_for_selector("table tbody tr", timeout=30000)
    time.sleep(0.5)
    # first row = Platform Fee
    page.locator("table tbody tr").first.locator(".actions-column span").first.click()
    page.wait_for_url("**/fee-management/**", timeout=20000)
    page.wait_for_selector("text=Default percentage", timeout=20000)
    time.sleep(0.8)


def open_browser(page: Page) -> None:
    open_module(
        page,
        MODULE_URLS["fee_management"],
        wait_selector="text=Fee Management",
    )
    page.wait_for_selector("table tbody tr", timeout=30000)
    time.sleep(0.5)
    print("Test 1 : Opened Fee Management listing")


def fee_listing_asserts(page: Page) -> None:
    open_module(
        page,
        MODULE_URLS["fee_management"],
        wait_selector="table tbody tr",
    )
    time.sleep(0.5)
    body = page.inner_text("body")
    for fee in FEE_TYPES:
        if fee not in body:
            raise AssertionError(
                f"Fee Management listing FAILED: missing '{fee}' "
                "(report to dev / Asana)"
            )
    for col in ("FEES", "DEFAULT PERCENTAGE/FEE", "LAST UPDATED"):
        if col not in body:
            raise AssertionError(
                f"Fee Management listing FAILED: missing column '{col}' "
                "(report to dev / Asana)"
            )
    rows = page.locator("table tbody tr")
    if rows.count() < 4:
        raise AssertionError(
            f"Fee Management listing FAILED: expected ≥4 fee rows, got {rows.count()} "
            "(report to dev / Asana)"
        )
    eyes = page.locator("table tbody tr .actions-column svg").count()
    if eyes < 1:
        raise AssertionError(
            "Fee Management listing FAILED: no view (eye) actions "
            "(report to dev / Asana)"
        )
    print(f"Test 2 : Listing OK — {rows.count()} fees, eye actions present")


def fee_view_detail(page: Page) -> None:
    _open_platform_fee(page)
    body = page.inner_text("body")
    if "Platform Fee" not in body:
        raise AssertionError(
            "Fee detail FAILED: not Platform Fee (report to dev / Asana)"
        )
    if "Default percentage" not in body:
        raise AssertionError(
            "Fee detail FAILED: missing Default percentage (report to dev / Asana)"
        )
    edit_btn = page.locator("button", has_text=re.compile(r"edit\s*default", re.I))
    if edit_btn.count() < 1:
        raise AssertionError(
            "Fee detail FAILED: Edit default percentage missing "
            "(report to dev / Asana)"
        )
    rows = page.locator("table tbody tr")
    if rows.count() < 1:
        raise AssertionError(
            "Fee detail FAILED: no outlet rows (report to dev / Asana)"
        )
    for col in ("OUTLET", "PERCENTAGE", "LAST UPDATED"):
        if col not in body:
            raise AssertionError(
                f"Fee detail FAILED: missing column '{col}' (report to dev / Asana)"
            )
    print(f"Test 3 : Platform Fee detail OK ({rows.count()} outlet rows on page)")


def _read_default_pct(page: Page) -> str:
    orig_pct = page.evaluate(
        """() => {
          const t = document.body.innerText;
          const m = t.match(/Default percentage\\s*([\\d.]+)\\s*%/i);
          return m ? m[1] : null;
        }"""
    )
    if not orig_pct:
        raise AssertionError(
            "Fee edit default FAILED: cannot read Default percentage "
            "(report to dev / Asana)"
        )
    return orig_pct


def _read_dialog_min_fee(dlg) -> str:
    inp = dlg.locator('input[name="minimumFee"]').first
    if inp.count() < 1:
        raise AssertionError(
            "Fee Minimum Fee FAILED: input[name=minimumFee] missing in "
            "Edit default percentage dialog (report to dev / Asana)"
        )
    # assert label present
    text = dlg.inner_text()
    if "Minimum Fee" not in text:
        raise AssertionError(
            "Fee Minimum Fee FAILED: label 'Minimum Fee (If applicable)' "
            "missing in dialog (report to dev / Asana)"
        )
    return inp.input_value() or "0"


def fee_edit_default_required_validation(page: Page) -> None:
    """Empty-state required validation on Edit default percentage dialog."""
    _open_platform_fee(page)
    orig_pct = _read_default_pct(page)

    _click_edit_default(page)
    dlg = _dialog(page)
    time.sleep(0.4)
    orig_min = _read_dialog_min_fee(dlg)

    # 1) Percentage empty
    _fill_named(dlg, "feeAmount", "")
    _fill_named(dlg, "minimumFee", orig_min or "3")
    _dialog_save(page, dlg)
    time.sleep(0.7)
    dlg = _dialog(page)
    text = dlg.inner_text()
    if "Percentage is required" not in text:
        raise AssertionError(
            "Fee validation FAILED: expected 'Percentage is required' when "
            f"Percentage empty; got {text[:200]!r} (report to dev / Asana)"
        )
    print("Test 4a : Empty Percentage → 'Percentage is required'")

    # 2) Minimum Fee empty
    _fill_named(dlg, "feeAmount", orig_pct)
    _fill_named(dlg, "minimumFee", "")
    _dialog_save(page, dlg)
    time.sleep(0.7)
    dlg = _dialog(page)
    text = dlg.inner_text()
    if "Minimum fee is required" not in text:
        raise AssertionError(
            "Fee validation FAILED: expected 'Minimum fee is required' when "
            f"Minimum Fee empty; got {text[:200]!r} (report to dev / Asana)"
        )
    print("Test 4b : Empty Minimum Fee → 'Minimum fee is required'")

    # 3) Both empty
    _fill_named(dlg, "feeAmount", "")
    _fill_named(dlg, "minimumFee", "")
    _dialog_save(page, dlg)
    time.sleep(0.7)
    dlg = _dialog(page)
    text = dlg.inner_text()
    missing = []
    if "Percentage is required" not in text:
        missing.append("Percentage is required")
    if "Minimum fee is required" not in text:
        missing.append("Minimum fee is required")
    if missing:
        raise AssertionError(
            f"Fee validation FAILED: both-empty missing {missing}; "
            f"got {text[:240]!r} (report to dev / Asana)"
        )
    # must not persist empties — cancel out
    _dialog_cancel(page, dlg)
    time.sleep(0.4)
    # confirm defaults unchanged on page
    still = _read_default_pct(page)
    if abs(float(still) - float(orig_pct)) > 0.01:
        raise AssertionError(
            f"Fee validation FAILED: Cancel after empty save mutated default "
            f"% {orig_pct} → {still} (report to dev / Asana)"
        )
    print("Test 4 : Required empty validation OK (pct + min fee + both)")


def fee_edit_default_restore(page: Page) -> None:
    """Edit default %, verify on detail, restore (keep Minimum Fee unchanged)."""
    _open_platform_fee(page)
    orig_pct = _read_default_pct(page)
    try:
        base = float(orig_pct)
    except ValueError:
        base = 5.0
    temp = "5.1" if abs(base - 5.1) > 0.01 else "5.2"

    _click_edit_default(page)
    dlg = _dialog(page)
    time.sleep(0.4)
    orig_min = _read_dialog_min_fee(dlg)
    _fill_named(dlg, "feeAmount", temp)
    _fill_named(dlg, "minimumFee", orig_min)
    _dialog_save(page, dlg)
    temp_re = temp.replace(".", r"\.")
    page.wait_for_function(
        "(re) => new RegExp('Default percentage\\\\s*' + re + '\\\\s*%', 'i').test(document.body.innerText)",
        arg=temp_re,
        timeout=20000,
    )
    time.sleep(0.8)
    body = page.inner_text("body")
    if temp not in body:
        raise AssertionError(
            f"Fee edit default FAILED: saved '{temp}' not shown (report to dev / Asana)"
        )
    print(f"Test 5a : Default % updated {orig_pct} → {temp}")

    # restore
    _click_edit_default(page)
    dlg = _dialog(page)
    time.sleep(0.4)
    _fill_named(dlg, "feeAmount", orig_pct)
    _fill_named(dlg, "minimumFee", orig_min)
    _dialog_save(page, dlg)
    orig_re = orig_pct.replace(".", r"\.")
    page.wait_for_function(
        "(re) => new RegExp('Default percentage\\\\s*' + re + '\\\\s*%', 'i').test(document.body.innerText)",
        arg=orig_re,
        timeout=20000,
    )
    time.sleep(0.5)
    body = page.inner_text("body")
    if orig_pct not in body:
        raise AssertionError(
            f"Fee edit default FAILED: restore to '{orig_pct}' not shown "
            "(report to dev / Asana)"
        )
    print(f"Test 5 : Default percentage edit + restore OK ({orig_pct}%)")


def fee_edit_minimum_fee_restore(page: Page) -> None:
    """Edit default Minimum Fee (If applicable), verify in dialog, restore."""
    _open_platform_fee(page)
    orig_pct = _read_default_pct(page)

    _click_edit_default(page)
    dlg = _dialog(page)
    time.sleep(0.4)
    orig_min = _read_dialog_min_fee(dlg)
    try:
        base_min = float(orig_min)
    except ValueError:
        base_min = 3.0
    # stay in a small safe band; prefer integer S$ values
    temp_min = "4" if abs(base_min - 4.0) > 0.01 else "5"
    _fill_named(dlg, "feeAmount", orig_pct)
    _fill_named(dlg, "minimumFee", temp_min)
    _dialog_save(page, dlg)
    time.sleep(1.2)

    # Minimum Fee is dialog-only — re-open and assert saved value
    _click_edit_default(page)
    dlg = _dialog(page)
    time.sleep(0.4)
    saved_min = _read_dialog_min_fee(dlg)
    if abs(float(saved_min) - float(temp_min)) > 0.01:
        raise AssertionError(
            f"Fee Minimum Fee FAILED: expected saved '{temp_min}', got '{saved_min}' "
            "(report to dev / Asana)"
        )
    print(f"Test 6a : Minimum Fee updated {orig_min} → {temp_min}")

    # restore
    _fill_named(dlg, "feeAmount", orig_pct)
    _fill_named(dlg, "minimumFee", orig_min)
    _dialog_save(page, dlg)
    time.sleep(1.2)

    _click_edit_default(page)
    dlg = _dialog(page)
    time.sleep(0.4)
    restored = _read_dialog_min_fee(dlg)
    if abs(float(restored) - float(orig_min)) > 0.01:
        raise AssertionError(
            f"Fee Minimum Fee FAILED: restore expected '{orig_min}', got '{restored}' "
            "(report to dev / Asana)"
        )
    _dialog_cancel(page, dlg)
    print(f"Test 6 : Minimum Fee edit + restore OK (S${orig_min})")


def fee_override_outlet_restore(page: Page) -> None:
    """Override a QA outlet percentage, verify, restore to default."""
    _open_platform_fee(page)
    rows = page.locator("table tbody tr")
    target_idx = None
    outlet_name = None
    for i in range(min(rows.count(), 10)):
        text = rows.nth(i).inner_text()
        if "QA Fran Outlet" in text or "QA " in text.split("\n")[0]:
            target_idx = i
            outlet_name = text.split("\n")[0].strip()
            break
    if target_idx is None:
        # fallback first row
        target_idx = 0
        outlet_name = rows.nth(0).inner_text().split("\n")[0].strip()

    row = rows.nth(target_idx)
    # read current %
    cells = row.locator("td")
    pct_text = cells.nth(1).inner_text() if cells.count() > 1 else ""
    orig = page.evaluate(
        """(t) => {
          const m = String(t).match(/([\\d.]+)\\s*%/);
          return m ? m[1] : '5';
        }""",
        pct_text,
    )
    temp = "5.3" if orig != "5.3" else "5.4"

    row.locator(".actions-column span").first.click()
    dlg = _dialog(page)
    time.sleep(0.4)
    title = dlg.inner_text()
    if "Override" not in title and "Percentage" not in title:
        raise AssertionError(
            f"Fee outlet override FAILED: unexpected dialog {title[:120]!r} "
            "(report to dev / Asana)"
        )
    min_val = dlg.locator('input[name="minimumFee"]').first.input_value() or "3"
    _fill_named(dlg, "feeAmount", temp)
    _fill_named(dlg, "minimumFee", min_val)
    _dialog_save(page, dlg)
    time.sleep(2)
    # re-find row and assert temp %
    page.wait_for_timeout(500)
    body = page.inner_text("body")
    # outlet row should show temp
    row2 = page.locator("table tbody tr", has_text=outlet_name[:20]).first
    row_txt = row2.inner_text() if row2.count() else body
    if temp not in row_txt and f"{temp} %" not in body:
        # soft check — maybe formatted without trailing zero
        raise AssertionError(
            f"Fee outlet override FAILED: '{temp}' not on row {outlet_name!r} "
            f"got {row_txt[:80]!r} (report to dev / Asana)"
        )
    print(f"Test 7a : Outlet override {outlet_name!r} → {temp}%")

    # restore to original
    row2.locator(".actions-column span").first.click()
    dlg = _dialog(page)
    time.sleep(0.4)
    _fill_named(dlg, "feeAmount", orig)
    _fill_named(dlg, "minimumFee", min_val)
    _dialog_save(page, dlg)
    time.sleep(2)
    row3 = page.locator("table tbody tr", has_text=outlet_name[:20]).first
    row_txt = row3.inner_text() if row3.count() else ""
    if orig not in row_txt:
        raise AssertionError(
            f"Fee outlet override FAILED: restore '{orig}' not on row "
            f"{row_txt[:80]!r} (report to dev / Asana)"
        )
    print(f"Test 7 : Outlet override + restore OK ({outlet_name!r})")


def fee_detail_rows_per_page(page: Page) -> None:
    _open_platform_fee(page)
    selects = page.locator("select")
    target = None
    for i in range(selects.count()):
        s = selects.nth(i)
        opts = s.locator("option").all_text_contents()
        if "10" in opts and "50" in opts:
            target = s
            break
    if target is None:
        print(f"Test 8 : Rows/page N/A ({page.locator('table tbody tr').count()} rows)")
        return
    target.select_option("20")
    time.sleep(1.5)
    n20 = page.locator("table tbody tr").count()
    if n20 < 11:
        raise AssertionError(
            f"Fee detail rows/page FAILED: expected more rows at 20, got {n20} "
            "(report to dev / Asana)"
        )
    target.select_option("10")
    time.sleep(1)
    # page 2 if present
    page2 = page.locator("text=/^2$/").last
    if page2.count() and page2.is_visible():
        try:
            page2.click()
            time.sleep(1)
            page.locator("text=/^1$/").last.click()
            time.sleep(0.5)
        except Exception:
            pass
    print(f"Test 8 : Detail rows/page OK (20→{n20} rows, restored 10)")
