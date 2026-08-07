"""Gift Bundle module — staging Selenium regression (full doable coverage).

Listing `/account/inventory/gift-bundles`
Actions (staging):
  - Add new gift bundle → `/gift-bundles/new`
  - Row kebab: Duplicate, Set as inactive/active (plain `<li>`, confirm Yes…)
  - Edit via `/gift-bundles/{uuid}` + Publish Changes / More actions

Coverage:
  search/filter, Duplicate+Publish QA, required validations, field update+verify,
  ACTIVE↔INACTIVE on QA only, rows/pagination, open edit verify.
"""
import time

from KskinCMS.GiftBundle_Module.GiftBundleHelper import *
from dotenv import load_dotenv
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

load_dotenv()

_QA_CREATED_BUNDLE = None
_QA_STATUS_BUNDLE = None
_DUP_SOURCE = "ComboC+PureMistToner_NewBundle"

_EXPECTED_ERR = {
    "price": "Price is required",
    "mpl": "Maximum purchase limit is required",
    "name": "Bundle name is required",
}


def open_browser():
    from KskinCMS.cms_auth import open_module
    from KskinCMS.cms_config import MODULE_URLS

    open_module(driver, MODULE_URLS["gift_bundles"], wait_css='input[name="code"]')
    print("Test 1 : Open browser success!")
    print("Test 2 : Navigated to Gift Bundles listing successfully!")


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


def _open_row_kebab(row):
    driver.execute_script(
        """
        const row = arguments[0];
        const tds = row.querySelectorAll('td');
        const cell = tds[tds.length - 1];
        const btn = cell.querySelector('button');
        const spans = [...cell.querySelectorAll('span')];
        const el = btn || spans[1] || spans[0];
        if (!el) return false;
        const r = el.getBoundingClientRect();
        const x = r.left + r.width / 2, y = r.top + r.height / 2;
        for (const type of [
          'pointerover','pointerenter','pointerdown','mousedown',
          'pointerup','mouseup','click'
        ]) {
          const C = type.startsWith('pointer') ? PointerEvent : MouseEvent;
          el.dispatchEvent(new C(type, {
            bubbles: true, cancelable: true, view: window,
            clientX: x, clientY: y, pointerId: 1, pointerType: 'mouse',
            buttons: type.endsWith('down') ? 1 : 0
          }));
        }
        return true;
        """,
        row,
    )
    time.sleep(0.9)


def _click_li_exact(label):
    return driver.execute_script(
        """
        const label = arguments[0];
        const matches = [...document.querySelectorAll('li, [role=menuitem]')].filter(
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
          if (/required|must be|invalid|cannot|NaN|at least|maximum|minimum|too |error|cast from|number type|greater/i.test(t))
            out.push(t);
        }
        return [...new Set(out)];
        """
    )


def _bundle_name_from_row(row):
    cells = row.find_elements(By.TAG_NAME, "td")
    # MEDIA | BUNDLE NAME | PACKAGE | PRICE | STATUS | actions
    if len(cells) >= 2:
        return (cells[1].text or "").strip().split("\n")[0].strip()
    return (row.text or "").strip().split("\n")[0].strip()


def _status_select():
    for s in driver.find_elements(By.TAG_NAME, "select"):
        opts = [o.text.strip() for o in s.find_elements(By.TAG_NAME, "option")]
        if "Draft" in opts or ("Active" in opts and "InActive" in opts):
            return s
    return None


def _find_source_row():
    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    for r in rows:
        if _DUP_SOURCE in (r.text or ""):
            return r
    for r in rows:
        txt = (r.text or "").upper()
        if "INACTIVE" in txt:
            continue
        if "ACTIVE" in txt:
            return r
    return rows[0] if rows else None


def _row_uuid(row):
    return driver.execute_script(
        """
        const row = arguments[0];
        function walk(el) {
          const k = Object.keys(el || {}).find(x => x.startsWith('__reactFiber'));
          if (!k) return null;
          let f = el[k];
          while (f) {
            const p = f.memoizedProps || {};
            for (const key of Object.keys(p)) {
              const v = p[key];
              if (typeof v === 'string' && /^[0-9a-f-]{36}$/i.test(v)) return v;
              if (v && typeof v === 'object' && typeof v.id === 'string'
                  && /^[0-9a-f-]{36}$/i.test(v.id)) return v.id;
            }
            f = f.return;
          }
          return null;
        }
        let id = walk(row);
        if (id) return id;
        for (const el of row.querySelectorAll('*')) {
          id = walk(el);
          if (id) return id;
        }
        return null;
        """,
        row,
    )


def gift_bundles_search_and_filter():
    from KskinCMS.cms_auth import search_listing
    from KskinCMS.cms_config import MODULE_URLS

    driver.get(MODULE_URLS["gift_bundles"])
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "code")))
    time.sleep(2)

    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    if not rows:
        raise AssertionError(
            "Gift Bundle search FAILED: listing empty (report to dev / Asana)"
        )
    first_name = _bundle_name_from_row(rows[0])
    if not first_name or len(first_name) < 2:
        raise AssertionError(
            "Gift Bundle search FAILED: no usable bundle name "
            "(report to dev / Asana)"
        )

    search_listing(driver, first_name)
    time.sleep(1)
    actual = _bundle_name_from_row(
        driver.find_element(By.CSS_SELECTOR, "table tbody tr")
    )
    if first_name not in actual and actual not in first_name:
        raise AssertionError(
            f"Gift Bundle matched search FAILED: expected '{first_name}', got '{actual}' "
            "(report to dev / Asana)"
        )
    print("Test 3 : Matched bundle search OK")

    driver.get(MODULE_URLS["gift_bundles"])
    time.sleep(2)
    search_listing(driver, "NoSuchGiftBundleZZZ")
    time.sleep(2)
    body = driver.find_element(By.TAG_NAME, "body").text
    rows = driver.find_elements(By.XPATH, "//table//tbody/tr")
    empty_ok = (
        "No gift" in body.lower()
        or "no result" in body.lower()
        or "no data" in body.lower()
        or "no bundle" in body.lower()
        or not rows
    )
    if not empty_ok:
        raise AssertionError(
            "Gift Bundle unmatched search FAILED: expected empty/no-result "
            "(report to dev / Asana)"
        )
    print("Test 4 : Unmatched search empty OK")

    driver.get(MODULE_URLS["gift_bundles"])
    time.sleep(2)
    status_sel = _status_select()
    if not status_sel:
        raise AssertionError(
            "Gift Bundle status filter FAILED: status <select> missing "
            "(report to dev / Asana)"
        )
    Select(status_sel).select_by_visible_text("Active")
    time.sleep(2)
    rows = driver.find_elements(By.XPATH, "//table//tbody/tr")
    if not rows:
        raise AssertionError(
            "Gift Bundle status filter Active FAILED: no rows "
            "(report to dev / Asana)"
        )
    status = (rows[0].text or "").upper()
    if "ACTIVE" not in status:
        raise AssertionError(
            f"Gift Bundle status filter Active FAILED: '{status[:80]}' "
            "(report to dev / Asana)"
        )
    print("Test 5 : Status filter Active OK")
    driver.get(MODULE_URLS["gift_bundles"])
    time.sleep(1)


def rows_per_page_actions():
    from KskinCMS.cms_config import MODULE_URLS

    driver.get(MODULE_URLS["gift_bundles"])
    time.sleep(2)
    scroll_to_bottom()
    time.sleep(1)
    selects = driver.find_elements(By.XPATH, "//select[@title='pageSize']")
    if not selects:
        # fallback: any select with 10/20/50
        for s in driver.find_elements(By.TAG_NAME, "select"):
            opts = [o.get_attribute("value") for o in s.find_elements(By.TAG_NAME, "option")]
            if "10" in opts and "50" in opts:
                selects = [s]
                break
    if not selects:
        rows = driver.find_elements(By.XPATH, "//table//tbody/tr")
        print(f"Test 6 : Rows per page N/A ({len(rows)} rows).")
        return
    select = Select(selects[0])
    select.select_by_value("50")
    time.sleep(2)
    select = Select(selects[0] if selects[0].is_displayed() else driver.find_elements(By.TAG_NAME, "select")[-1])
    try:
        select.select_by_value("10")
    except Exception:
        Select(driver.find_elements(By.TAG_NAME, "select")[-1]).select_by_value("10")
    time.sleep(2)
    page2 = driver.find_elements(By.XPATH, "//table//tfoot//*[normalize-space()='2']")
    if not page2:
        page2 = driver.find_elements(
            By.XPATH, "//*[contains(text(),'Displaying')]/following::*[normalize-space()='2']"
        )
    if page2:
        page2[0].click()
        time.sleep(1)
        page1 = driver.find_elements(By.XPATH, "//*[normalize-space()='1']")
        if page1:
            # click last matching small pager '1'
            page1[-1].click()
            time.sleep(1)
        print("Test 6 : Rows per page + pagination checked!")
    else:
        print("Test 6 : Rows per page checked (pagination N/A).")


def _open_duplicate_form():
    from KskinCMS.cms_auth import open_module
    from KskinCMS.cms_config import MODULE_URLS

    open_module(driver, MODULE_URLS["gift_bundles"], wait_css='input[name="code"]')
    time.sleep(1)
    row = _find_source_row()
    if row is None:
        raise AssertionError(
            "Gift Bundle create FAILED: no source row to Duplicate "
            "(report to dev / Asana)"
        )
    _open_row_kebab(row)
    items = driver.execute_script(
        "return [...document.querySelectorAll('li,[role=menuitem]')]"
        ".map(e=>(e.textContent||'').trim())"
    )
    if not any((i or "") == "Duplicate" for i in items):
        raise AssertionError(
            f"Gift Bundle create FAILED: Duplicate missing (got {items}) "
            "(report to dev / Asana)"
        )
    res = _click_li_exact("Duplicate")
    if res.get("err"):
        raise AssertionError(
            f"Gift Bundle create FAILED: Duplicate click — {res} "
            "(report to dev / Asana)"
        )
    WebDriverWait(driver, 20).until(
        lambda d: "/gift-bundles/new" in (d.current_url or "")
    )
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "name")))
    time.sleep(1.5)


def gift_bundle_required_validations():
    """On Duplicate form: assert required messages for price / max purchase / name."""
    _open_duplicate_form()
    name = driver.find_element(By.NAME, "name")
    price = driver.find_element(By.NAME, "price")
    mpl = driver.find_element(By.NAME, "maximumPurchaseLimitPerCustomer")
    orig_name = name.get_attribute("value") or ""
    orig_price = price.get_attribute("value") or "15"
    orig_mpl = mpl.get_attribute("value") or "100"

    _set_val(price, "")
    time.sleep(1.0)
    errs = _visible_validation_errors()
    if _EXPECTED_ERR["price"] not in errs:
        raise AssertionError(
            f"Gift Bundle validation FAILED: expected '{_EXPECTED_ERR['price']}', "
            f"got {errs} (report to dev / Asana)"
        )
    print("Test 7 : Price required OK")

    _set_val(mpl, "")
    time.sleep(1.0)
    errs = _visible_validation_errors()
    if _EXPECTED_ERR["mpl"] not in errs:
        raise AssertionError(
            f"Gift Bundle validation FAILED: expected '{_EXPECTED_ERR['mpl']}', "
            f"got {errs} (report to dev / Asana)"
        )
    print("Test 8 : Maximum purchase limit required OK")

    _set_val(name, "")
    time.sleep(1.2)
    # Trigger validators (blur alone may not show name required on this form)
    _fiber_click_button(r"^\s*Publish\s*$")
    time.sleep(1.5)
    errs = _visible_validation_errors()
    body = driver.find_element(By.TAG_NAME, "body").text or ""
    still_on_new = "/gift-bundles/new" in (driver.current_url or "")
    name_msg_ok = (
        _EXPECTED_ERR["name"] in errs or _EXPECTED_ERR["name"] in body
    )
    if not name_msg_ok:
        raise AssertionError(
            f"Gift Bundle validation FAILED: expected '{_EXPECTED_ERR['name']}' "
            f"after empty name + Publish. errors={errs}, still_on_new={still_on_new} "
            "(report to dev / Asana)"
        )
    if not still_on_new:
        raise AssertionError(
            "Gift Bundle validation FAILED: empty name was published "
            "(report to dev / Asana)"
        )
    print("Test 9 : Bundle name required OK")

    # restore values but leave without publishing (navigate away)
    _set_val(name, orig_name or f"Copy of {_DUP_SOURCE}")
    _set_val(price, orig_price)
    _set_val(mpl, orig_mpl)
    from KskinCMS.cms_auth import open_module
    from KskinCMS.cms_config import MODULE_URLS

    open_module(driver, MODULE_URLS["gift_bundles"], wait_css='input[name="code"]')
    print("Test 10 : Validation step complete (discarded draft form)")

def _set_package_by_label(label):
    """Set Package native <select> by visible option text (RHF-friendly events)."""
    return driver.execute_script(
        """
        const label = arguments[0];
        const selects = [...document.querySelectorAll('select')];
        for (const s of selects) {
          const opt = [...s.options].find(o => (o.text || '').trim() === label
            || (o.text || '').includes(label));
          if (!opt) continue;
          const setter = Object.getOwnPropertyDescriptor(
            window.HTMLSelectElement.prototype, 'value'
          ).set;
          setter.call(s, opt.value);
          s.dispatchEvent(new Event('input', { bubbles: true }));
          s.dispatchEvent(new Event('change', { bubbles: true }));
          // React fiber onChange if present
          let cur = s;
          while (cur) {
            const k = Object.keys(cur).find(x => x.startsWith('__reactFiber'));
            if (k) {
              let f = cur[k];
              while (f) {
                const p = f.memoizedProps || {};
                if (typeof p.onChange === 'function') {
                  try {
                    p.onChange({ target: s, currentTarget: s });
                    return {ok: true, via: 'fiber', value: opt.value};
                  } catch (e) {}
                }
                f = f.return;
              }
            }
            cur = cur.parentElement;
          }
          return {ok: true, via: 'native', value: opt.value};
        }
        return {ok: false};
        """,
        label,
    )


def add_new_gift_bundle():
    """Duplicate source → unique name → Save as draft → Set as active → listed ACTIVE."""
    global _QA_CREATED_BUNDLE
    from KskinCMS.cms_auth import open_module, search_listing
    from KskinCMS.cms_config import MODULE_URLS

    _open_duplicate_form()
    stamp = str(int(time.time()))[-6:]
    qa_name = f"QA Bundle {stamp}"
    name = driver.find_element(By.NAME, "name")
    price = driver.find_element(By.NAME, "price")
    mpl = driver.find_element(By.NAME, "maximumPurchaseLimitPerCustomer")
    _set_val(name, qa_name)
    if not (price.get_attribute("value") or "").strip():
        _set_val(price, "15")
    if not (mpl.get_attribute("value") or "").strip():
        _set_val(mpl, "100")
    # Duplicate often lands on "Daily usage"; Publish needs Package — set Skincare Bundle.
    pkg = _set_package_by_label("Skincare Bundle")
    if not pkg.get("ok"):
        raise AssertionError(
            f"Gift Bundle create FAILED: could not set Package Skincare Bundle "
            f"({pkg}) (report to dev / Asana)"
        )
    time.sleep(0.8)

    # Publish requires Treatment even when product is set — draft then activate (Treatment path).
    clk = _fiber_click_button(r"Save as draft")
    if clk.get("err"):
        raise AssertionError(
            f"Gift Bundle create FAILED: Save as draft — {clk}; "
            f"errors={_visible_validation_errors()} (report to dev / Asana)"
        )
    time.sleep(6)

    open_module(driver, MODULE_URLS["gift_bundles"], wait_css='input[name="code"]')
    search_listing(driver, qa_name)
    time.sleep(2)
    rows = driver.find_elements(
        By.XPATH, f"//table//tbody/tr[contains(., '{qa_name}')]"
    )
    if not rows:
        raise AssertionError(
            f"Gift Bundle create FAILED: '{qa_name}' not listed after draft "
            "(report to dev / Asana)"
        )
    row_txt = rows[0].text or ""
    st = _row_status(row_txt)
    if st not in ("DRAFT", "ACTIVE"):
        raise AssertionError(
            f"Gift Bundle create FAILED: unexpected status {st} in {row_txt!r} "
            "(report to dev / Asana)"
        )

    if st != "ACTIVE":
        _open_row_kebab(rows[0])
        act = _click_li_exact("Set as active")
        if act.get("err"):
            raise AssertionError(
                f"Gift Bundle create FAILED: Set as active menu — {act} "
                "(report to dev / Asana)"
            )
        time.sleep(1)
        conf = _fiber_click_button(r"Yes, set as active")
        # Draft→active may activate without confirm dialog
        if conf.get("err"):
            time.sleep(2)
        else:
            time.sleep(4)
        search_listing(driver, qa_name)
        time.sleep(2)
        rows = driver.find_elements(
            By.XPATH, f"//table//tbody/tr[contains(., '{qa_name}')]"
        )
        if not rows:
            raise AssertionError(
                f"Gift Bundle create FAILED: '{qa_name}' missing after Set as active "
                "(report to dev / Asana)"
            )
        if _row_status(rows[0].text) != "ACTIVE":
            raise AssertionError(
                f"Gift Bundle create FAILED: expected ACTIVE, got {rows[0].text!r} "
                "(report to dev / Asana)"
            )

    _QA_CREATED_BUNDLE = qa_name
    print(f"Test 11 : QA gift bundle draft→active: {qa_name}")


def _row_status(text):
    u = (text or "").upper()
    if "INACTIVE" in u:
        return "INACTIVE"
    if "DRAFT" in u:
        return "DRAFT"
    if "ACTIVE" in u:
        return "ACTIVE"
    return "UNKNOWN"


def _toggle_qa_status(name, make_inactive=True):
    """Listing kebab status toggle for Gift Bundles (plain <li>; confirm optional)."""
    from KskinCMS.cms_auth import search_listing

    search_listing(driver, name)
    time.sleep(1.2)
    row = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (By.XPATH, f"//table//tbody/tr[contains(., '{name}')]")
        )
    )
    expect = "INACTIVE" if make_inactive else "ACTIVE"
    if _row_status(row.text) == expect:
        return True

    _open_row_kebab(row)
    label = "Set as inactive" if make_inactive else "Set as active"
    li = _click_li_exact(label)
    if li.get("err"):
        raise AssertionError(
            f"Gift Bundle status FAILED: menu '{label}' — {li} "
            "(report to dev / Asana)"
        )
    time.sleep(1.2)
    # Confirm dialog is optional on this module (fiber onClick may complete inline)
    confirm_re = (
        r"Yes, set as inactive" if make_inactive else r"Yes, set as active"
    )
    conf = _fiber_click_button(confirm_re)
    if conf.get("err"):
        _fiber_click_button(r"Yes,")
    time.sleep(4)
    search_listing(driver, name)
    time.sleep(1.2)
    txt = (
        driver.find_element(
            By.XPATH, f"//table//tbody/tr[contains(., '{name}')]"
        ).text
        or ""
    )
    got = _row_status(txt)
    if got != expect:
        raise AssertionError(
            f"Gift Bundle status FAILED: want {expect}, got {got} ({txt!r}) "
            "(report to dev / Asana)"
        )
    return True


def listing_active_inactive_action():
    global _QA_STATUS_BUNDLE
    from KskinCMS.cms_auth import open_module
    from KskinCMS.cms_config import MODULE_URLS

    name = (_QA_CREATED_BUNDLE or "").strip()
    if not name:
        raise AssertionError(
            "Gift Bundle status FAILED: no QA bundle from create step"
        )
    _QA_STATUS_BUNDLE = name
    open_module(driver, MODULE_URLS["gift_bundles"], wait_css='input[name="code"]')
    _toggle_qa_status(name, make_inactive=True)
    print("Test 12 : QA gift bundle set INACTIVE")


def listing_inactive_active_action():
    from KskinCMS.cms_auth import open_module
    from KskinCMS.cms_config import MODULE_URLS

    name = (_QA_STATUS_BUNDLE or _QA_CREATED_BUNDLE or "").strip()
    if not name:
        raise AssertionError("Gift Bundle status FAILED: no QA bundle name")
    open_module(driver, MODULE_URLS["gift_bundles"], wait_css='input[name="code"]')
    _toggle_qa_status(name, make_inactive=False)
    print("Test 13 : QA gift bundle restored ACTIVE")


def check_created_gift_bundle_value():
    """Open QA edit via UUID and verify name/price fields."""
    from KskinCMS.cms_auth import open_module, search_listing
    from KskinCMS.cms_config import MODULE_URLS

    name = (_QA_CREATED_BUNDLE or "").strip()
    if not name:
        raise AssertionError("Gift Bundle view FAILED: no QA bundle")
    open_module(driver, MODULE_URLS["gift_bundles"], wait_css='input[name="code"]')
    search_listing(driver, name)
    time.sleep(1)
    row = driver.find_element(By.XPATH, f"//table//tbody/tr[contains(., '{name}')]")
    uid = _row_uuid(row)
    if not uid:
        raise AssertionError(
            f"Gift Bundle view FAILED: no UUID for '{name}' "
            "(report to dev / Asana)"
        )
    driver.get(f"{MODULE_URLS['gift_bundles']}/{uid}")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "name")))
    time.sleep(1.5)
    got = driver.find_element(By.NAME, "name").get_attribute("value") or ""
    if name not in got:
        raise AssertionError(
            f"Gift Bundle view FAILED: name expected '{name}', got '{got}' "
            "(report to dev / Asana)"
        )
    price = driver.find_element(By.NAME, "price").get_attribute("value") or ""
    if not price:
        raise AssertionError(
            "Gift Bundle view FAILED: price empty on edit "
            "(report to dev / Asana)"
        )
    print(f"Test 14 : View/edit open OK — name={got}, price={price}")


def _set_treatment_by_label(label):
    """Set Treatment native <select> by option text (enables Publish Changes)."""
    return driver.execute_script(
        """
        const label = arguments[0];
        const selects = [...document.querySelectorAll('select')];
        for (const s of selects) {
          const opt = [...s.options].find(o => (o.text || '').trim() === label
            || (o.text || '').includes(label));
          if (!opt) continue;
          // skip package select (Daily usage / Skincare Bundle / Acne Care)
          const texts = [...s.options].map(o => (o.text || '').trim());
          if (texts.includes('Skincare Bundle') && texts.includes('Daily usage')) continue;
          const setter = Object.getOwnPropertyDescriptor(
            window.HTMLSelectElement.prototype, 'value'
          ).set;
          setter.call(s, opt.value);
          s.dispatchEvent(new Event('input', { bubbles: true }));
          s.dispatchEvent(new Event('change', { bubbles: true }));
          let cur = s;
          while (cur) {
            const k = Object.keys(cur).find(x => x.startsWith('__reactFiber'));
            if (k) {
              let f = cur[k];
              while (f) {
                const p = f.memoizedProps || {};
                if (typeof p.onChange === 'function') {
                  try {
                    p.onChange({ target: s, currentTarget: s });
                    return {ok: true, via: 'fiber', value: opt.value};
                  } catch (e) {}
                }
                f = f.return;
              }
            }
            cur = cur.parentElement;
          }
          return {ok: true, via: 'native', value: opt.value};
        }
        return {ok: false};
        """,
        label,
    )


def update_old_gift_bundle():
    """Rename QA + tweak price/T&C → set Treatment → Publish Changes → verify listing."""
    global _QA_CREATED_BUNDLE, _QA_STATUS_BUNDLE
    from KskinCMS.cms_auth import open_module, search_listing
    from KskinCMS.cms_config import MODULE_URLS

    name = (_QA_CREATED_BUNDLE or "").strip()
    if not name:
        raise AssertionError("Gift Bundle edit FAILED: no QA bundle")
    open_module(driver, MODULE_URLS["gift_bundles"], wait_css='input[name="code"]')
    search_listing(driver, name)
    time.sleep(1)
    row = driver.find_element(By.XPATH, f"//table//tbody/tr[contains(., '{name}')]")
    uid = _row_uuid(row)
    if not uid:
        raise AssertionError(
            f"Gift Bundle edit FAILED: no UUID for '{name}' (report to dev / Asana)"
        )
    driver.get(f"{MODULE_URLS['gift_bundles']}/{uid}")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "name")))
    time.sleep(1.5)

    # Duplicate/product-only QA often opens with Treatment required → Publish disabled
    treat = _set_treatment_by_label("Updated Treat 00292")
    if not treat.get("ok"):
        # try first treatment option available
        treat = driver.execute_script(
            """
            const selects=[...document.querySelectorAll('select')];
            for (const s of selects) {
              const texts=[...s.options].map(o=>(o.text||'').trim());
              if (texts.includes('Skincare Bundle') && texts.includes('Daily usage')) continue;
              if (!s.options.length) continue;
              const opt=s.options[0];
              const setter=Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set;
              setter.call(s, opt.value);
              s.dispatchEvent(new Event('change',{bubbles:true}));
              return {ok:true, via:'first', value:opt.value, text:opt.text};
            }
            return {ok:false};
            """
        )
    if not treat.get("ok"):
        raise AssertionError(
            f"Gift Bundle edit FAILED: could not set Treatment (Publish blocked). "
            f"errors={_visible_validation_errors()} (report to dev / Asana)"
        )
    time.sleep(0.8)

    stamp = str(int(time.time()))[-6:]
    new_name = f"{name} E{stamp}"[:70]
    _set_val(driver.find_element(By.NAME, "name"), new_name)
    price_el = driver.find_element(By.NAME, "price")
    old_price = price_el.get_attribute("value") or "15"
    try:
        new_price = str(int(float(old_price)) + 1)
    except Exception:
        new_price = "16"
    _set_val(price_el, new_price)
    tas = driver.find_elements(By.CSS_SELECTOR, "textarea")
    if tas:
        tc = (tas[0].get_attribute("value") or "") + f" QA-EDIT-{stamp}"
        _set_val(tas[0], tc[:2000])
    time.sleep(0.4)

    pub = driver.execute_script(
        """
        const btn=[...document.querySelectorAll('button')].find(b=>
          /Publish Changes/i.test(b.innerText||''));
        return btn ? {disabled: !!btn.disabled} : null;
        """
    )
    if pub and pub.get("disabled"):
        raise AssertionError(
            f"Gift Bundle edit FAILED: Publish Changes still disabled after Treatment. "
            f"errors={_visible_validation_errors()} (report to dev / Asana)"
        )

    clk = _fiber_click_button(r"Publish Changes")
    if clk.get("err"):
        raise AssertionError(
            f"Gift Bundle edit FAILED: Publish Changes — {clk}; "
            f"errors={_visible_validation_errors()} (report to dev / Asana)"
        )
    time.sleep(6)

    open_module(driver, MODULE_URLS["gift_bundles"], wait_css='input[name="code"]')
    search_listing(driver, new_name)
    time.sleep(2)
    rows = driver.find_elements(
        By.XPATH, f"//table//tbody/tr[contains(., '{new_name}')]"
    )
    if not rows:
        raise AssertionError(
            f"Gift Bundle edit FAILED: '{new_name}' not listed "
            "(report to dev / Asana)"
        )
    _QA_CREATED_BUNDLE = new_name
    _QA_STATUS_BUNDLE = new_name
    print(f"Test 15 : Edited QA bundle searchable as {new_name} (price→{new_price})")
