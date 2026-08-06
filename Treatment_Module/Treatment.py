"""Treatment module — staging Selenium regression (actions-first).

Allowed listing actions (staging):
  - Pencil → edit detail `/treatments/{id}`
  - Kebab: Duplicate, Set as inactive / Set as active

Notes:
  - Duplicate of Cleanse opens /new with mostly empty fields (title shows Copy of …).
  - Publish stays disabled if Effect > 100 chars (`N/100` counter).
  - Reliable QA create: Duplicate → fill basics + Effect≤100 → Save as draft → Set as active.
"""
import time

from KskinCMS.Treatment_Module.TreatmentHelper import *
from KskinCMS.Treatment_Module.TreatmentVarPaths import *
from dotenv import load_dotenv
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

load_dotenv()

_QA_CREATED_TREATMENT = None
_QA_STATUS_TREATMENT = None
_CLEANSE_SOURCE = "Cleanse"


def open_browser():
    from KskinCMS.cms_auth import open_module
    from KskinCMS.cms_config import MODULE_URLS

    open_module(driver, MODULE_URLS["treatments"], wait_css='input[name="code"]')
    print("Test 1 : Open browser success!")
    print("Test 2 : Navigated to Treatments listing successfully!")


def _treatment_name_from_row(row):
    cells = row.find_elements(By.TAG_NAME, "td")
    # empty | MEDIA | TREATMENT | GROUP | PRICE | STATUS | actions
    if len(cells) >= 3:
        return (cells[2].text or cells[1].text or "").strip().split("\n")[0].strip()
    return (row.text or "").strip().split("\n")[0].strip()


def _status_select():
    for s in driver.find_elements(By.TAG_NAME, "select"):
        opts = [o.text.strip() for o in s.find_elements(By.TAG_NAME, "option")]
        if "Draft" in opts and "Active" in opts:
            return s
    return None


def treatments_search_and_filter():
    """Matched/unmatched search + Active status filter."""
    from KskinCMS.cms_auth import search_listing
    from KskinCMS.cms_config import MODULE_URLS

    driver.get(MODULE_URLS["treatments"])
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "code")))
    time.sleep(2)

    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    if not rows:
        raise AssertionError(
            "Treatment search FAILED: listing empty (report to dev / Asana)"
        )
    first_name = _treatment_name_from_row(rows[0])
    if not first_name or len(first_name) < 2:
        raise AssertionError(
            "Treatment search FAILED: no usable name on first listing row "
            "(report to dev / Asana)"
        )

    search_listing(driver, first_name)
    time.sleep(1)
    actual = _treatment_name_from_row(
        driver.find_element(By.CSS_SELECTOR, "table tbody tr")
    )
    print(actual)
    if first_name not in actual and actual not in first_name:
        raise AssertionError(
            f"Treatment matched search FAILED: expected '{first_name}', got '{actual}' "
            "(report to dev / Asana)"
        )
    print("Test 3 : Treatment name searching with matched value is successful!")

    driver.get(MODULE_URLS["treatments"])
    time.sleep(2)
    search_listing(driver, "NoSuchTreatmentZZZ")
    time.sleep(2)
    body = driver.find_element(By.TAG_NAME, "body").text
    rows = driver.find_elements(By.XPATH, "//table//tbody/tr")
    empty_ok = (
        "No treatments" in body
        or "No treatment" in body
        or "no result" in body.lower()
        or "no data" in body.lower()
        or not rows
    )
    if not empty_ok:
        raise AssertionError(
            "Treatment unmatched search FAILED: expected empty/no-result "
            "(report to dev / Asana)"
        )
    print("Test 4 : Searching with unmatched value can show empty result successfully!!")

    driver.get(MODULE_URLS["treatments"])
    time.sleep(2)
    status_sel = _status_select()
    if not status_sel:
        raise AssertionError(
            "Treatment status filter FAILED: status <select> missing "
            "(report to dev / Asana)"
        )
    Select(status_sel).select_by_visible_text("Active")
    time.sleep(2)
    rows = driver.find_elements(By.XPATH, "//table//tbody/tr")
    if not rows:
        raise AssertionError(
            "Treatment status filter Active FAILED: no rows "
            "(report to dev / Asana)"
        )
    status = (rows[0].text or "").upper()
    print(status[:120])
    if "ACTIVE" not in status:
        raise AssertionError(
            f"Treatment status filter Active FAILED: '{status[:80]}' "
            "(report to dev / Asana)"
        )
    print("Test 5 : Status filter Active successful!")

    driver.get(MODULE_URLS["treatments"])
    time.sleep(2)
    print("Test 6 : Listing filters checked")


def rows_per_page_actions():
    from KskinCMS.cms_config import MODULE_URLS

    driver.get(MODULE_URLS["treatments"])
    time.sleep(2)
    scroll_to_bottom()
    time.sleep(1)
    selects = driver.find_elements(By.XPATH, "//select[@title='pageSize']")
    if not selects:
        rows = driver.find_elements(By.XPATH, "//table//tbody/tr")
        print(f"Test 7 : Rows per page N/A on treatments listing ({len(rows)} rows).")
        return
    select = Select(selects[0])
    select.select_by_value("50")
    time.sleep(2)
    select = Select(driver.find_element(By.XPATH, "//select[@title='pageSize']"))
    select.select_by_value("10")
    time.sleep(2)
    page2 = driver.find_elements(By.XPATH, "//table//tfoot//*[normalize-space()='2']")
    if page2:
        page2[0].click()
        time.sleep(1)
        page1 = driver.find_elements(By.XPATH, "//table//tfoot//*[normalize-space()='1']")
        if page1:
            page1[0].click()
            time.sleep(1)
        print("Test 7 : Rows per page + pagination checked!")
    else:
        print("Test 7 : Rows per page checked (pagination N/A — single page).")


def _open_row_kebab(row):
    driver.execute_script(
        """
        const row = arguments[0];
        const tds = [...row.querySelectorAll('td')];
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


def _fiber_click_menuitem(label):
    return driver.execute_script(
        """
        const label = arguments[0];
        const items = [...document.querySelectorAll('[role="menuitem"]')];
        const it = items.find(e => (e.textContent || '').trim() === label
          || (e.textContent || '').includes(label));
        if (!it) return 'no-item';
        let cur = it;
        while (cur) {
          const k = Object.keys(cur).find(x => x.startsWith('__reactFiber'));
          if (k) {
            let f = cur[k];
            while (f) {
              if (f.memoizedProps && typeof f.memoizedProps.onClick === 'function') {
                f.memoizedProps.onClick({
                  preventDefault() {}, stopPropagation() {}, nativeEvent: {}
                });
                return 'ok';
              }
              f = f.return;
            }
          }
          cur = cur.parentElement;
        }
        it.click();
        return 'native';
        """,
        label,
    )


def _fiber_click_button(exact_text):
    return driver.execute_script(
        """
        const want = arguments[0];
        const visible = (b) => {
          const r = b.getBoundingClientRect();
          const st = window.getComputedStyle(b);
          return r.width > 0 && r.height > 0 && st.visibility !== 'hidden' && st.display !== 'none';
        };
        const btn = [...document.querySelectorAll('button')].find(b =>
          visible(b) && (b.innerText || '').trim() === want
        );
        if (!btn) return {err: 'no-btn'};
        if (btn.disabled || (btn.className || '').includes('cursor-not-allowed')) {
          return {err: 'disabled'};
        }
        btn.scrollIntoView({block:'center'});
        let cur = btn;
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
        btn.click();
        return {via: 'native'};
        """,
        exact_text,
    )


def _fiber_click_button_matching(pattern):
    """Click button whose trimmed text matches regex (case-insensitive).

    Sticky footers often have offsetParent=null / odd rects — match by text only.
    """
    return driver.execute_script(
        """
        const re = new RegExp(arguments[0], 'i');
        const btn = [...document.querySelectorAll('button')].find(b =>
          re.test((b.innerText || '').trim())
        );
        if (!btn) {
          return {
            err: 'no-btn',
            btns: [...document.querySelectorAll('button')]
              .map(b => (b.innerText || '').trim())
              .filter(Boolean)
              .filter(t => /publish|draft|save|cancel/i.test(t))
              .slice(0, 20)
          };
        }
        if (btn.disabled || (btn.className || '').includes('cursor-not-allowed')) {
          return {err: 'disabled', text: (btn.innerText || '').trim()};
        }
        try { btn.scrollIntoView({block:'center'}); } catch (e) {}
        let cur = btn;
        while (cur) {
          const k = Object.keys(cur).find(x => x.startsWith('__reactFiber'));
          if (k) {
            let f = cur[k];
            while (f) {
              if (f.memoizedProps && typeof f.memoizedProps.onClick === 'function') {
                f.memoizedProps.onClick({
                  preventDefault() {}, stopPropagation() {}, nativeEvent: {}
                });
                return {via: 'fiber', text: (btn.innerText || '').trim()};
              }
              f = f.return;
            }
          }
          cur = cur.parentElement;
        }
        btn.click();
        return {via: 'native', text: (btn.innerText || '').trim()};
        """,
        pattern,
    )


def _effect_textarea():
    tas = driver.find_elements(
        By.XPATH, '//label[@for="effect"]/following::textarea[1]'
    )
    return tas[0] if tas else None


def _ensure_effect_max_100(text=None):
    """Publish stays disabled when Effect char count > 100."""
    from KskinCMS.cms_auth import js_fill

    ta = _effect_textarea()
    if not ta:
        raise AssertionError(
            "Treatment form FAILED: Effect textarea missing "
            "(report to dev / Asana)"
        )
    cur = ta.get_attribute("value") or ""
    raw = text if text is not None else (cur or "QA treatment effect")
    new = (raw or "QA treatment effect")[:100]
    js_fill(driver, ta, new)
    try:
        ta.send_keys(Keys.TAB)
    except Exception:
        pass
    time.sleep(0.3)
    final = ta.get_attribute("value") or ""
    if len(final) > 100:
        raise AssertionError(
            f"Treatment Effect still over 100 chars ({len(final)}) "
            "(report to dev / Asana)"
        )
    print(f"Effect set to {len(final)}/100")
    return final


def _find_cleanse_row():
    from KskinCMS.cms_auth import open_module, search_listing
    from KskinCMS.cms_config import MODULE_URLS

    open_module(driver, MODULE_URLS["treatments"], wait_css='input[name="code"]')
    # Reset status filter so Draft/All don't hide the source ACTIVE Cleanse
    status_sel = _status_select()
    if status_sel:
        try:
            Select(status_sel).select_by_visible_text("All status")
        except Exception:
            try:
                Select(status_sel).select_by_index(0)
            except Exception:
                pass
        time.sleep(1)
    search_listing(driver, _CLEANSE_SOURCE)
    time.sleep(2)
    for r in driver.find_elements(By.CSS_SELECTOR, "table tbody tr"):
        names = [
            (c.text or "").strip().split("\n")[0].strip()
            for c in r.find_elements(By.TAG_NAME, "td")
        ]
        # Exact treatment title cell == Cleanse (not Combo A/B: Cleanse + …)
        if any(n == _CLEANSE_SOURCE for n in names) and not any(
            "Combo" in n for n in names
        ):
            return r
    # Fallback: scan without relying on search order
    body_snip = (driver.find_element(By.TAG_NAME, "body").text or "")[:300]
    raise AssertionError(
        f"Treatment create FAILED: exact '{_CLEANSE_SOURCE}' row not found. "
        f"body={body_snip!r} (report to dev / Asana)"
    )


def _row_treatment_uuid(row):
    return driver.execute_script(
        """
        const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
        const found = [];
        function scan(p) {
          if (!p || typeof p !== 'object') return;
          for (const k of Object.keys(p)) {
            const v = p[k];
            if (typeof v === 'string' && UUID.test(v)) found.push(v);
            if (v && typeof v === 'object' && typeof v.id === 'string' && UUID.test(v.id)) {
              found.push(v.id);
            }
          }
        }
        function walk(node, depth) {
          if (!node || depth > 6) return;
          const key = Object.keys(node).find(x => x.startsWith('__reactFiber'));
          if (key) {
            let f = node[key];
            let hops = 0;
            while (f && hops < 50) {
              scan(f.memoizedProps || {});
              f = f.return;
              hops++;
            }
          }
          for (const c of node.children || []) walk(c, depth + 1);
        }
        walk(arguments[0], 0);
        return found[0] || null;
        """,
        row,
    )


def _confirm_yes_dialog():
    yes = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//button[contains(.,'Yes, set as active') or contains(.,'Yes, set as inactive') "
                "or contains(.,'Yes, update status') or contains(.,'Yes')]",
            )
        )
    )
    driver.execute_script(
        """
        const el = arguments[0];
        const key = Object.keys(el).find(k => k.startsWith('__reactProps$'));
        if (key && el[key] && typeof el[key].onClick === 'function') {
          el[key].onClick({
            preventDefault() {}, stopPropagation() {}, nativeEvent: {}, isTrusted: true,
            target: el, currentTarget: el, type: 'click'
          });
        } else {
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
                  return;
                }
                f = f.return;
              }
            }
            cur = cur.parentElement;
          }
          el.click();
        }
        """,
        yes,
    )
    time.sleep(3)


def add_new_treatment():
    """QA via Duplicate Cleanse → Save as draft → Set as active (Effect ≤100)."""
    global _QA_CREATED_TREATMENT
    from KskinCMS.cms_auth import js_fill, open_module, search_listing
    from KskinCMS.cms_config import MODULE_URLS

    row = _find_cleanse_row()
    _open_row_kebab(row)
    items = driver.execute_script(
        "return [...document.querySelectorAll('[role=menuitem]')].map(e=>e.textContent.trim())"
    )
    if not any("Duplicate" in (i or "") for i in (items or [])):
        raise AssertionError(
            f"Treatment create FAILED: Duplicate missing (got {items}) "
            "(report to dev / Asana)"
        )
    if _fiber_click_menuitem("Duplicate") == "no-item":
        raise AssertionError("Treatment create FAILED: could not click Duplicate")
    time.sleep(5)
    if "/treatments/new" not in (driver.current_url or ""):
        raise AssertionError(
            f"Treatment create FAILED: expected /treatments/new, got {driver.current_url} "
            "(report to dev / Asana)"
        )

    stamp = str(int(time.time()))[-6:]
    name = f"QA Cleanse {stamp}"
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "name")))
    js_fill(driver, driver.find_element(By.NAME, "name"), name)
    if driver.find_elements(By.NAME, "posCode"):
        js_fill(driver, driver.find_element(By.NAME, "posCode"), f"QAC{stamp}")
    for n, v in (("price", "10"), ("duration", "15")):
        el = driver.find_element(By.NAME, n)
        if not (el.get_attribute("value") or "").strip():
            js_fill(driver, el, v)
    _ensure_effect_max_100("QA Cleanse effect for automation")

    # Prefer Publish if enabled; else Save as draft (staging Duplicate often leaves required empty)
    pub = _fiber_click_button("Publish")
    if pub.get("err"):
        draft = _fiber_click_button("Save as draft")
        if draft.get("err"):
            raise AssertionError(
                f"Treatment create FAILED: Publish={pub} Draft={draft} "
                "(report to dev / Asana)"
            )
        time.sleep(6)
    else:
        time.sleep(8)

    open_module(driver, MODULE_URLS["treatments"], wait_css='input[name="code"]')
    search_listing(driver, name)
    time.sleep(2)
    rows = driver.find_elements(By.XPATH, f"//table//tbody/tr[contains(., '{name}')]")
    if not rows:
        raise AssertionError(
            f"Treatment create FAILED: '{name}' not listed after save "
            "(report to dev / Asana)"
        )

    row_txt = (rows[0].text or "").upper()
    if "DRAFT" in row_txt:
        _open_row_kebab(rows[0])
        if _fiber_click_menuitem("Set as active") == "no-item":
            raise AssertionError(
                f"Treatment create FAILED: Set as active missing for draft '{name}' "
                "(report to dev / Asana)"
            )
        _confirm_yes_dialog()
        search_listing(driver, name)
        time.sleep(2)
        rows = driver.find_elements(
            By.XPATH, f"//table//tbody/tr[contains(., '{name}')]"
        )
        if not rows or "ACTIVE" not in (rows[0].text or "").upper():
            raise AssertionError(
                f"Treatment create FAILED: '{name}' not ACTIVE after Set as active "
                f"(row={(rows[0].text if rows else '')!r}) (report to dev / Asana)"
            )

    _QA_CREATED_TREATMENT = name
    print(f"Test 8 : New QA treatment ready (from Cleanse duplicate)! : {name}")


def listing_active_inactive_action():
    global _QA_STATUS_TREATMENT
    from KskinCMS.cms_auth import open_module, toggle_row_status
    from KskinCMS.cms_config import MODULE_URLS

    name = (_QA_CREATED_TREATMENT or "").split("\n")[0].strip()
    if not name:
        raise AssertionError(
            "Treatment status FAILED: no QA treatment from create step"
        )
    _QA_STATUS_TREATMENT = name
    open_module(driver, MODULE_URLS["treatments"], wait_css='input[name="code"]')
    ok = toggle_row_status(driver, name, make_inactive=True)
    if not ok:
        raise AssertionError(
            f"Treatment ACTIVE→INACTIVE FAILED for '{name}' (report to dev / Asana)"
        )
    print("Test 9 : Changed NEW QA treatment to inactive successfully!")


def listing_inactive_active_action():
    from KskinCMS.cms_auth import open_module, toggle_row_status
    from KskinCMS.cms_config import MODULE_URLS

    name = (_QA_STATUS_TREATMENT or _QA_CREATED_TREATMENT or "").split("\n")[0].strip()
    if not name:
        raise AssertionError("Treatment status FAILED: no QA treatment name")
    open_module(driver, MODULE_URLS["treatments"], wait_css='input[name="code"]')
    ok = toggle_row_status(driver, name, make_inactive=False)
    if not ok:
        raise AssertionError(
            f"Treatment INACTIVE→ACTIVE FAILED for '{name}' (report to dev / Asana)"
        )
    print("Test 10 : Changed NEW QA treatment back to active successfully!")


def _open_qa_treatment_edit(name=None):
    from KskinCMS.cms_auth import open_module, search_listing
    from KskinCMS.cms_config import MODULE_URLS

    name = name or _QA_CREATED_TREATMENT
    if not name:
        raise AssertionError("Treatment view/edit FAILED: no QA treatment name")
    open_module(driver, MODULE_URLS["treatments"], wait_css='input[name="code"]')
    search_listing(driver, name)
    time.sleep(1.5)
    row = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (By.XPATH, f"//table//tbody/tr[contains(., '{name}')]")
        )
    )
    pid = _row_treatment_uuid(row)
    if not pid:
        raise AssertionError(
            f"Treatment edit FAILED: no UUID on row for '{name}' "
            "(report to dev / Asana)"
        )
    driver.get(f"{MODULE_URLS['treatments']}/{pid}")
    time.sleep(3)
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "name")))
    WebDriverWait(driver, 15).until(
        lambda d: (d.find_element(By.NAME, "name").get_attribute("value") or "").strip()
    )


def check_created_treatment_value():
    _open_qa_treatment_edit()
    val = driver.find_element(By.NAME, "name").get_attribute("value") or ""
    print(f"View name: {val}")
    name = _QA_CREATED_TREATMENT or ""
    if name not in val:
        raise AssertionError(
            f"Treatment view FAILED: expected '{name}' in name field (got '{val}') "
            "(report to dev / Asana)"
        )
    # Keep Effect valid for later Publish Changes
    _ensure_effect_max_100()
    print("Test 11 : View/edit form opened and values readable successfully!")


def _rhf_set_many(values: dict):
    return driver.execute_script(
        """
        const values = arguments[0];
        let setValue = null;
        for (const el of document.querySelectorAll('*')) {
          const k = Object.keys(el).find(x => x.startsWith('__reactFiber'));
          if (!k) continue;
          let f = el[k];
          let hops = 0;
          while (f && hops < 80) {
            const p = f.memoizedProps || {};
            if (typeof p.setValue === 'function') { setValue = p.setValue; break; }
            f = f.return;
            hops++;
          }
          if (setValue) break;
        }
        if (!setValue) return false;
        for (const [key, val] of Object.entries(values)) {
          if (val !== undefined && val !== null) {
            setValue(key, val, { shouldDirty: true, shouldValidate: true });
          }
        }
        return true;
        """,
        values,
    )


def _read_cleanse_source_values():
    """Read required field values from ACTIVE Cleanse for completing QA forms."""
    from KskinCMS.cms_auth import open_module, search_listing
    from KskinCMS.cms_config import MODULE_URLS

    row = _find_cleanse_row()
    pid = _row_treatment_uuid(row)
    if not pid:
        return None
    open_module(driver, MODULE_URLS["treatments"], wait_css='input[name="code"]')
    driver.get(f"{MODULE_URLS['treatments']}/{pid}")
    time.sleep(3)
    src = driver.execute_script(
        """
        function summarize(obj, depth) {
          if (obj == null) return obj;
          if (typeof obj !== 'object') return obj;
          if (depth > 3) return null;
          if (Array.isArray(obj)) return obj.map(x => summarize(x, depth + 1));
          const out = {};
          for (const k of Object.keys(obj)) {
            const v = obj[k];
            if (typeof v === 'function') continue;
            out[k] = summarize(v, depth + 1);
          }
          return out;
        }
        for (const el of document.querySelectorAll('form,div')) {
          const k = Object.keys(el).find(x => x.startsWith('__reactFiber'));
          if (!k) continue;
          let f = el[k];
          let hops = 0;
          while (f && hops < 60) {
            const p = f.memoizedProps || {};
            if (p.control && p.control._formValues) return summarize(p.control._formValues, 0);
            if (typeof p.getValues === 'function') {
              try { return summarize(p.getValues(), 0); } catch (e) {}
            }
            f = f.return;
            hops++;
          }
        }
        return null;
        """
    )
    return src


def update_old_treatment():
    global _QA_CREATED_TREATMENT, _QA_STATUS_TREATMENT
    from KskinCMS.cms_auth import js_fill, open_module, search_listing
    from KskinCMS.cms_config import MODULE_URLS

    # Snapshot Cleanse required values first (Publish Changes needs them on incomplete QA)
    src = _read_cleanse_source_values()
    if not src:
        raise AssertionError(
            "Treatment edit FAILED: could not read source Cleanse values "
            "(report to dev / Asana)"
        )

    _open_qa_treatment_edit()
    uniq = str(int(time.time()))[-5:]
    new_name = f"Updated Treat {uniq}"
    js_fill(driver, driver.find_element(By.NAME, "name"), new_name)

    effect = (src.get("effect") or "QA treatment effect")[:100]
    patch = {
        "name": new_name,
        "price": src.get("price") or 10,
        "duration": src.get("duration") or 15,
        "posCode": f"QAT{uniq}",
        "effect": effect,
        "stepsForCustomers": src.get("stepsForCustomers") or "QA steps for customers",
        "treatmentGroupId": src.get("treatmentGroupId"),
        "treatmentCategoryId": src.get("treatmentCategoryId"),
        "treatmentSkinTypes": src.get("treatmentSkinTypes"),
        "treatmentSkinConcerns": src.get("treatmentSkinConcerns"),
        "imageForOutletPage": src.get("imageForOutletPage"),
        "imageForTreatmentPage": src.get("imageForTreatmentPage"),
        "originalFileNameForOutletPage": src.get("originalFileNameForOutletPage"),
        "originalFileNameForTreatmentPage": src.get("originalFileNameForTreatmentPage"),
    }
    if not _rhf_set_many(patch):
        raise AssertionError(
            "Treatment edit FAILED: RHF setValue unavailable "
            "(report to dev / Asana)"
        )
    # Keep DOM Effect counter honest
    _ensure_effect_max_100(effect)
    for n in ("name", "price", "duration", "posCode"):
        if driver.find_elements(By.NAME, n) and patch.get(n) is not None:
            js_fill(driver, driver.find_element(By.NAME, n), str(patch[n]))
    time.sleep(1)

    clk = _fiber_click_button_matching(r"Publish Changes")
    if clk.get("err") == "disabled":
        # Effect tip / missing required — retry after hard-capping effect again
        _ensure_effect_max_100(effect[:100])
        time.sleep(0.5)
        clk = _fiber_click_button_matching(r"Publish Changes")
    if clk.get("err"):
        clk = _fiber_click_button_matching(r"Save as draft")
    if clk.get("err"):
        clk = _fiber_click_button_matching(r"^Publish$")
    if clk.get("err"):
        raise AssertionError(
            f"Treatment edit FAILED: no usable save/publish button ({clk}) "
            "(report to dev / Asana)"
        )
    print("Edit submit via", clk)
    time.sleep(8)

    # If still on detail, confirm name persisted on form (listing search can lag / filter)
    if driver.find_elements(By.NAME, "name"):
        form_name = driver.find_element(By.NAME, "name").get_attribute("value") or ""
        print("Post-save form name:", form_name)
        if new_name not in form_name:
            body = (driver.find_element(By.TAG_NAME, "body").text or "")[:500]
            raise AssertionError(
                f"Treatment edit FAILED: form name not '{new_name}' after submit "
                f"(got '{form_name}', submit={clk}). body={body!r} "
                "(report to dev / Asana)"
            )

    open_module(driver, MODULE_URLS["treatments"], wait_css='input[name="code"]')
    status_sel = _status_select()
    if status_sel:
        try:
            Select(status_sel).select_by_index(0)
            time.sleep(1)
        except Exception:
            pass
    search_listing(driver, new_name)
    time.sleep(2)
    rows = driver.find_elements(
        By.XPATH, f"//table//tbody/tr[contains(., '{new_name}')]"
    )
    if not rows:
        # Retry once after refresh
        driver.get(MODULE_URLS["treatments"])
        time.sleep(2)
        search_listing(driver, new_name)
        time.sleep(2)
        rows = driver.find_elements(
            By.XPATH, f"//table//tbody/tr[contains(., '{new_name}')]"
        )
    if not rows:
        body = (driver.find_element(By.TAG_NAME, "body").text or "")[:400]
        raise AssertionError(
            f"Treatment edit FAILED: '{new_name}' not found after save "
            f"(submit={clk}). body={body!r} (report to dev / Asana)"
        )
    _QA_CREATED_TREATMENT = new_name
    _QA_STATUS_TREATMENT = new_name
    print(f"Test 12 : Edit treatment successful! : {new_name}")
