"""Gift Card module — staging Selenium regression (actions-first + full coverage).

Singleton inventory entity (NOT a multi-row listing):
  View  `/account/inventory/gift-card`
  Edit  `/account/inventory/gift-card/{uuid}`

Allowed actions (staging):
  - View: Edit Gift Card
  - Edit: More actions → Set as inactive / Set as active (confirm:
    "Yes, set as inactive" / "Yes, set as active")
  - Edit: Publish Changes (description, T&C, designs, amounts, validity)

Coverage:
  - View asserts, open edit (wait hydration)
  - Required + validation error messages (hard-fail if wrong/missing)
  - Update all editable text/number fields → Publish → verify → restore
  - ACTIVE ↔ INACTIVE on the singleton (leave ACTIVE)

No Duplicate / create — only one Gift Card.
"""
import time

from KskinCMS.GiftCard_Module.GiftCardHelper import *
from dotenv import load_dotenv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

load_dotenv()

_BASE_DESC = (
    "Perfect for all occasions! Customise a giftcard and send it to your loved one."
)
_BASE_TC = "Test1.\nTest2.\nTest3.\nTest4.\nTest5."

# Expected user-facing validation copy (staging). Wrong/raw schema text → Failed.
_EXPECTED_ERR = {
    "desc": "Description is required",
    "tc": "Terms and conditions are required",
    "design": "Design name is required",
    "amount": "Gift card amount is required",
    "amount_gt0": "Amount must be greater than 0",
    "expired": "Expired in is required",
}


def open_browser():
    from KskinCMS.cms_auth import open_module
    from KskinCMS.cms_config import MODULE_URLS

    open_module(driver, MODULE_URLS["gift_card"])
    WebDriverWait(driver, 20).until(
        lambda d: "Edit Gift Card" in (d.find_element(By.TAG_NAME, "body").text or "")
    )
    print("Test 1 : Open browser success!")
    print("Test 2 : Navigated to Gift Card view successfully!")


def _fiber_click_button(text_re):
    return driver.execute_script(
        """
        const re = new RegExp(arguments[0], 'i');
        const btns = [...document.querySelectorAll('button')].filter(b =>
          b.offsetParent && re.test((b.innerText || '').trim())
        );
        const btn = btns[0];
        if (!btn) return {err: 'no-btn'};
        let cur = btn;
        while (cur) {
          const k = Object.keys(cur).find(x => x.startsWith('__reactFiber'));
          if (k) {
            let f = cur[k];
            while (f) {
              const p = f.memoizedProps || {};
              if (typeof p.onClick === 'function') {
                try {
                  p.onClick({preventDefault(){}, stopPropagation(){}, nativeEvent:{}});
                  return {via: 'fiber', text: (btn.innerText || '').trim()};
                } catch (e) {
                  return {err: String(e)};
                }
              }
              f = f.return;
            }
          }
          cur = cur.parentElement;
        }
        btn.click();
        return {via: 'native'};
        """,
        text_re,
    )


def _click_li_exact(label):
    return driver.execute_script(
        """
        const label = arguments[0];
        const matches = [...document.querySelectorAll('li')].filter(
          e => (e.textContent || '').trim() === label
        );
        matches.sort((a, b) => a.outerHTML.length - b.outerHTML.length);
        const el = matches[0];
        if (!el) return {err: 'none'};
        let cur = el;
        while (cur) {
          const k = Object.keys(cur).find(x => x.startsWith('__reactFiber'));
          if (k) {
            let f = cur[k];
            while (f) {
              if (f.memoizedProps && typeof f.memoizedProps.onClick === 'function') {
                f.memoizedProps.onClick({
                  preventDefault() {}, stopPropagation() {}, nativeEvent: {}
                });
                return {via: 'fiber'};
              }
              f = f.return;
            }
          }
          cur = cur.parentElement;
        }
        el.click();
        return {via: 'native'};
        """,
        label,
    )


def _set_val(el, value):
    driver.execute_script(
        """
        const el = arguments[0], value = arguments[1];
        const proto = el.tagName === 'TEXTAREA'
          ? window.HTMLTextAreaElement.prototype
          : window.HTMLInputElement.prototype;
        const setter = Object.getOwnPropertyDescriptor(proto, 'value').set;
        setter.call(el, String(value));
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
        el.blur();
        el.dispatchEvent(new Event('blur', { bubbles: true }));
        """,
        el,
        value,
    )


def _visible_validation_errors():
    return driver.execute_script(
        """
        const out = [];
        for (const el of document.querySelectorAll('p,span')) {
          if (!el.offsetParent) continue;
          const t = (el.textContent || '').trim();
          if (!t || t.length > 220 || el.children.length > 2) continue;
          if (/required|must be|invalid|cannot|NaN|at least|maximum|minimum|too |error|cast from|number type/i.test(t))
            out.push(t);
        }
        return [...new Set(out)];
        """
    )


def _publish_disabled():
    st = driver.execute_script(
        """
        const btn = [...document.querySelectorAll('button')].find(b =>
          /Publish Changes/i.test(b.innerText || '')
        );
        if (!btn) return null;
        return {disabled: !!btn.disabled, aria: btn.getAttribute('aria-disabled')};
        """
    )
    if not st:
        return True
    return bool(st.get("disabled")) or st.get("aria") == "true"


def _assert_err_contains(expected, context):
    errs = _visible_validation_errors()
    if expected not in errs:
        raise AssertionError(
            f"Gift Card validation FAILED ({context}): expected '{expected}', "
            f"got {errs} (report to dev / Asana)"
        )
    if not _publish_disabled():
        raise AssertionError(
            f"Gift Card validation FAILED ({context}): Publish Changes still enabled "
            f"while '{expected}' shown (report to dev / Asana)"
        )


def _view_body_snip():
    body = driver.find_element(By.TAG_NAME, "body").text or ""
    if "Edit Gift Card" in body:
        return body.split("Edit Gift Card")[0][-450:]
    return body[-450:]


def _view_status():
    snip = _view_body_snip()
    if "INACTIVE" in snip:
        return "INACTIVE"
    if "ACTIVE" in snip:
        return "ACTIVE"
    return "UNKNOWN"


def _open_view():
    from KskinCMS.cms_auth import open_module
    from KskinCMS.cms_config import MODULE_URLS

    open_module(driver, MODULE_URLS["gift_card"])
    WebDriverWait(driver, 20).until(
        lambda d: "Edit Gift Card" in (d.find_element(By.TAG_NAME, "body").text or "")
    )
    time.sleep(1)


def _open_edit():
    """Open edit and wait until amounts/designs hydrate (empty form is a false start)."""
    _open_view()
    clk = _fiber_click_button(r"Edit Gift Card")
    if clk.get("err"):
        raise AssertionError(
            f"Gift Card open edit FAILED: {clk} (report to dev / Asana)"
        )
    WebDriverWait(driver, 20).until(
        lambda d: "Publish Changes" in (d.find_element(By.TAG_NAME, "body").text or "")
    )
    WebDriverWait(driver, 20).until(
        lambda d: len(
            d.find_elements(By.CSS_SELECTOR, 'input[name^="giftCardAmounts"]')
        )
        >= 1
    )
    time.sleep(0.8)
    if "/gift-card/" not in (driver.current_url or ""):
        raise AssertionError(
            f"Gift Card open edit FAILED: expected edit URL, got {driver.current_url} "
            "(report to dev / Asana)"
        )


def _edit_fields():
    tas = driver.find_elements(By.CSS_SELECTOR, "textarea")
    designs = driver.find_elements(
        By.CSS_SELECTOR, 'input[name^="giftcardDesigns"][name$=".name"]'
    )
    amounts = driver.find_elements(
        By.CSS_SELECTOR, 'input[name^="giftCardAmounts"][name$=".amount"]'
    )
    exp = driver.find_elements(By.NAME, "expiredIn")
    unit = driver.find_elements(By.CSS_SELECTOR, "select")
    return {
        "tas": tas,
        "designs": designs,
        "amounts": amounts,
        "expired": exp[0] if exp else None,
        "unit": unit[0] if unit else None,
    }


def gift_card_view_page():
    """Assert singleton view: status, amounts, Edit Gift Card."""
    _open_view()
    snip = _view_body_snip()
    body = driver.find_element(By.TAG_NAME, "body").text or ""
    status = _view_status()
    print("View status:", status)
    if status != "ACTIVE":
        raise AssertionError(
            f"Gift Card view FAILED: expected ACTIVE before suite, got {status}. "
            f"snip={snip!r} (report to dev / Asana or re-activate manually)"
        )
    amounts_ok = all(a in body for a in ("$10", "$15", "$30", "$40")) or (
        "Gift Amounts" in body
    )
    if not amounts_ok:
        raise AssertionError(
            "Gift Card view FAILED: gift amounts not visible "
            "(report to dev / Asana)"
        )
    if "Edit Gift Card" not in body:
        raise AssertionError(
            "Gift Card view FAILED: Edit Gift Card button missing "
            "(report to dev / Asana)"
        )
    if _BASE_DESC.split("!")[0] not in body and "Perfect for all occasions" not in body:
        raise AssertionError(
            "Gift Card view FAILED: description not visible "
            "(report to dev / Asana)"
        )
    print("Test 3 : Gift Card view page OK (ACTIVE + amounts + Edit)!")


def open_edit_form():
    """Open Edit (hydrated) and assert core form fields."""
    _open_edit()
    body = driver.find_element(By.TAG_NAME, "body").text or ""
    if "Publish Changes" not in body:
        raise AssertionError(
            "Gift Card edit FAILED: Publish Changes missing (report to dev / Asana)"
        )
    if "More actions" not in body:
        raise AssertionError(
            "Gift Card edit FAILED: More actions missing (report to dev / Asana)"
        )
    f = _edit_fields()
    if len(f["tas"]) < 2:
        raise AssertionError(
            f"Gift Card edit FAILED: expected Description + T&C textareas, got {len(f['tas'])} "
            "(report to dev / Asana)"
        )
    if len(f["amounts"]) < 1:
        raise AssertionError(
            "Gift Card edit FAILED: denomination amount inputs missing "
            "(report to dev / Asana)"
        )
    if len(f["designs"]) < 1:
        raise AssertionError(
            "Gift Card edit FAILED: design name inputs missing "
            "(report to dev / Asana)"
        )
    if f["expired"] is None:
        raise AssertionError(
            "Gift Card edit FAILED: expiredIn missing (report to dev / Asana)"
        )
    print(
        f"Test 4 : Edit form hydrated — {len(f['tas'])} textareas, "
        f"{len(f['designs'])} designs, {len(f['amounts'])} amounts"
    )


def gift_card_required_validations():
    """Clear required fields / invalid amount — assert user-facing errors + Publish off."""
    _open_edit()
    f = _edit_fields()
    orig_desc = f["tas"][0].get_attribute("value") or _BASE_DESC
    orig_tc = f["tas"][1].get_attribute("value") or _BASE_TC
    orig_design = f["designs"][0].get_attribute("value") or "BD event"
    orig_amount = f["amounts"][0].get_attribute("value") or "30"
    orig_exp = f["expired"].get_attribute("value") or "1"

    _set_val(f["tas"][0], "")
    time.sleep(1.0)
    _assert_err_contains(_EXPECTED_ERR["desc"], "description required")
    _set_val(f["tas"][0], orig_desc)
    time.sleep(0.3)

    _set_val(f["tas"][1], "")
    time.sleep(1.0)
    _assert_err_contains(_EXPECTED_ERR["tc"], "T&C required")
    _set_val(f["tas"][1], orig_tc)
    time.sleep(0.3)

    _set_val(f["designs"][0], "")
    time.sleep(1.0)
    _assert_err_contains(_EXPECTED_ERR["design"], "design name required")
    _set_val(f["designs"][0], orig_design)
    time.sleep(0.3)

    _set_val(f["amounts"][0], "")
    time.sleep(1.0)
    _assert_err_contains(_EXPECTED_ERR["amount"], "amount required")
    _set_val(f["amounts"][0], "0")
    time.sleep(1.0)
    _assert_err_contains(_EXPECTED_ERR["amount_gt0"], "amount > 0")
    _set_val(f["amounts"][0], "-1")
    time.sleep(1.0)
    _assert_err_contains(_EXPECTED_ERR["amount_gt0"], "amount negative")
    _set_val(f["amounts"][0], orig_amount)
    time.sleep(0.3)

    _set_val(f["expired"], "")
    time.sleep(1.0)
    _assert_err_contains(_EXPECTED_ERR["expired"], "expired in required")
    _set_val(f["expired"], orig_exp)
    time.sleep(0.3)

    # Combined required set still blocks publish
    _set_val(f["tas"][0], "")
    _set_val(f["tas"][1], "")
    _set_val(f["designs"][0], "")
    _set_val(f["amounts"][0], "")
    _set_val(f["expired"], "")
    time.sleep(1.2)
    errs = _visible_validation_errors()
    for key in ("desc", "tc", "design", "amount", "expired"):
        if _EXPECTED_ERR[key] not in errs:
            raise AssertionError(
                f"Gift Card validation FAILED (combined): missing '{_EXPECTED_ERR[key]}' "
                f"in {errs} (report to dev / Asana)"
            )
    if not _publish_disabled():
        raise AssertionError(
            "Gift Card validation FAILED (combined): Publish enabled with empty requireds "
            "(report to dev / Asana)"
        )

    # Discard by leaving edit without Publish
    _open_view()
    print("Test 5 : Required + amount validations OK (user-facing copy)")


def update_gift_card():
    """Update all editable fields → Publish → verify view/edit → restore originals."""
    _open_edit()
    f = _edit_fields()
    orig = {
        "desc": f["tas"][0].get_attribute("value") or _BASE_DESC,
        "tc": f["tas"][1].get_attribute("value") or _BASE_TC,
        "design": f["designs"][0].get_attribute("value") or "BD event",
        "amount": f["amounts"][0].get_attribute("value") or "30",
        "expired": f["expired"].get_attribute("value") or "1",
        "unit": driver.execute_script(
            "const s=document.querySelector('select'); return s ? s.value : '';"
        )
        or "Years",
    }
    stamp = str(int(time.time()))[-6:]
    marker = f"QA-GC-{stamp}"
    qa_desc = f"{_BASE_DESC} {marker}"
    if len(qa_desc) > 300:
        qa_desc = qa_desc[:300]
    qa_tc = f"{_BASE_TC}\nQA-TC-{stamp}"
    if len(qa_tc) > 1000:
        qa_tc = qa_tc[:1000]
    qa_design = f"QA Design {stamp}"
    # Keep amount unique among the four if possible
    qa_amount = "35"
    qa_expired = "2"
    qa_unit = "Months"

    _set_val(f["tas"][0], qa_desc)
    _set_val(f["tas"][1], qa_tc)
    _set_val(f["designs"][0], qa_design)
    _set_val(f["amounts"][0], qa_amount)
    _set_val(f["expired"], qa_expired)
    if f["unit"] is not None:
        driver.execute_script(
            """
            const sel = arguments[0], value = arguments[1];
            sel.value = value;
            sel.dispatchEvent(new Event('change', { bubbles: true }));
            sel.dispatchEvent(new Event('input', { bubbles: true }));
            """,
            f["unit"],
            qa_unit,
        )
    time.sleep(0.5)

    if _publish_disabled():
        raise AssertionError(
            f"Gift Card update FAILED: Publish disabled after valid fills. "
            f"errors={_visible_validation_errors()} (report to dev / Asana)"
        )
    clk = _fiber_click_button(r"Publish Changes")
    if clk.get("err"):
        raise AssertionError(
            f"Gift Card update FAILED: Publish Changes — {clk} "
            "(report to dev / Asana)"
        )
    time.sleep(6)

    _open_view()
    body = driver.find_element(By.TAG_NAME, "body").text or ""
    if marker not in body:
        raise AssertionError(
            f"Gift Card update FAILED: description marker '{marker}' not on view "
            "(report to dev / Asana)"
        )
    if f"${qa_amount}" not in body and qa_amount not in body:
        raise AssertionError(
            f"Gift Card update FAILED: amount ${qa_amount} not on view "
            "(report to dev / Asana)"
        )
    # Expiration copy on view (e.g. "2 Months from the date of purchase")
    if qa_expired not in body or "Month" not in body:
        raise AssertionError(
            f"Gift Card update FAILED: expiration '{qa_expired} Months' not on view. "
            f"snip={_view_body_snip()!r} (report to dev / Asana)"
        )
    print(f"Test 6 : View verified after Publish ({marker}, ${qa_amount}, {qa_expired} Months)")

    _open_edit()
    f2 = _edit_fields()
    got_tc = f2["tas"][1].get_attribute("value") or ""
    got_design = f2["designs"][0].get_attribute("value") or ""
    got_amount = f2["amounts"][0].get_attribute("value") or ""
    got_exp = f2["expired"].get_attribute("value") or ""
    got_unit = driver.execute_script(
        "const s=document.querySelector('select'); return s ? s.value : '';"
    )
    if f"QA-TC-{stamp}" not in got_tc:
        raise AssertionError(
            f"Gift Card update FAILED: T&C not persisted (got {got_tc!r}) "
            "(report to dev / Asana)"
        )
    if got_design != qa_design:
        raise AssertionError(
            f"Gift Card update FAILED: design name expected {qa_design!r}, got {got_design!r} "
            "(report to dev / Asana)"
        )
    if got_amount != qa_amount:
        raise AssertionError(
            f"Gift Card update FAILED: amount expected {qa_amount}, got {got_amount} "
            "(report to dev / Asana)"
        )
    if got_exp != qa_expired:
        raise AssertionError(
            f"Gift Card update FAILED: expiredIn expected {qa_expired}, got {got_exp} "
            "(report to dev / Asana)"
        )
    if got_unit != qa_unit:
        raise AssertionError(
            f"Gift Card update FAILED: unit expected {qa_unit}, got {got_unit} "
            "(report to dev / Asana)"
        )
    print("Test 7 : Edit form persisted T&C / design / amount / expiry")

    # Restore staging baseline (prefer captured originals)
    _set_val(f2["tas"][0], orig["desc"] or _BASE_DESC)
    _set_val(f2["tas"][1], orig["tc"] or _BASE_TC)
    _set_val(f2["designs"][0], orig["design"])
    _set_val(f2["amounts"][0], orig["amount"])
    _set_val(f2["expired"], orig["expired"])
    if f2["unit"] is not None and orig["unit"]:
        driver.execute_script(
            """
            const sel = arguments[0], value = arguments[1];
            sel.value = value;
            sel.dispatchEvent(new Event('change', { bubbles: true }));
            """,
            f2["unit"],
            orig["unit"],
        )
    time.sleep(0.4)
    clk2 = _fiber_click_button(r"Publish Changes")
    if clk2.get("err"):
        raise AssertionError(
            f"Gift Card update FAILED: restore Publish — {clk2} "
            "(report to dev / Asana)"
        )
    time.sleep(5)
    _open_view()
    body2 = driver.find_element(By.TAG_NAME, "body").text or ""
    if marker in body2:
        raise AssertionError(
            "Gift Card update FAILED: QA marker still on view after restore "
            "(report to dev / Asana)"
        )
    if f"${orig['amount']}" not in body2 and orig["amount"] not in body2:
        raise AssertionError(
            f"Gift Card update FAILED: restored amount ${orig['amount']} missing on view "
            "(report to dev / Asana)"
        )
    print("Test 8 : Fields restored to pre-QA values")


def _set_status(make_inactive=True):
    """Toggle singleton Gift Card status via More actions + confirm."""
    _open_edit()
    more = _fiber_click_button(r"More actions")
    if more.get("err"):
        raise AssertionError(
            f"Gift Card status FAILED: More actions — {more} "
            "(report to dev / Asana)"
        )
    time.sleep(1)
    label = "Set as inactive" if make_inactive else "Set as active"
    li = _click_li_exact(label)
    if li.get("err"):
        raise AssertionError(
            f"Gift Card status FAILED: menu '{label}' — {li} "
            "(report to dev / Asana)"
        )
    time.sleep(1)
    confirm = (
        r"Yes, set as inactive" if make_inactive else r"Yes, set as active"
    )
    conf = _fiber_click_button(confirm)
    if conf.get("err"):
        raise AssertionError(
            f"Gift Card status FAILED: confirm '{confirm}' — {conf} "
            "(report to dev / Asana)"
        )
    time.sleep(4)


def listing_active_inactive_action():
    """ACTIVE → INACTIVE on the singleton Gift Card."""
    _open_view()
    if _view_status() != "ACTIVE":
        raise AssertionError(
            f"Gift Card ACTIVE→INACTIVE FAILED: not ACTIVE before toggle "
            f"(got {_view_status()}) (report to dev / Asana)"
        )
    _set_status(make_inactive=True)
    _open_view()
    st = _view_status()
    if st != "INACTIVE":
        raise AssertionError(
            f"Gift Card ACTIVE→INACTIVE FAILED: expected INACTIVE, got {st} "
            "(report to dev / Asana)"
        )
    print("Test 9 : Gift Card set to INACTIVE successfully!")


def listing_inactive_active_action():
    """INACTIVE → ACTIVE on the singleton Gift Card (must leave ACTIVE)."""
    _open_view()
    if _view_status() != "INACTIVE":
        raise AssertionError(
            f"Gift Card INACTIVE→ACTIVE FAILED: expected INACTIVE before toggle "
            f"(got {_view_status()}) (report to dev / Asana)"
        )
    _set_status(make_inactive=False)
    _open_view()
    st = _view_status()
    if st != "ACTIVE":
        raise AssertionError(
            f"Gift Card INACTIVE→ACTIVE FAILED: expected ACTIVE, got {st} "
            "(report to dev / Asana)"
        )
    print("Test 10 : Gift Card restored to ACTIVE successfully!")
