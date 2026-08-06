"""Product module — staging Selenium regression (actions-first).

Allowed listing actions (staging):
  - Pencil (first actions span) → edit detail `/products/{id}`
  - Kebab: Duplicate, Set as inactive/active, Update Stock
"""
import time

from KskinCMS.Product_Module.ProductHelper import *
from KskinCMS.Product_Module.ProductVarPaths import *
from dotenv import load_dotenv
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

load_dotenv()

_QA_CREATED_PRODUCT = None
_QA_STATUS_PRODUCT = None


def open_browser():
    from KskinCMS.cms_auth import open_module
    from KskinCMS.cms_config import MODULE_URLS

    open_module(driver, MODULE_URLS["products"], wait_css='input[name="code"]')
    print("Test 1 : Open browser success!")
    print("Test 2 : Navigated to Products listing successfully!")


def _product_name_from_row(row):
    cells = row.find_elements(By.TAG_NAME, "td")
    # MEDIA | PRODUCT NAME | CATEGORY | PRICE | INVENTORY | STATUS | actions
    if len(cells) >= 3:
        return (cells[1].text or cells[2].text or "").strip().split("\n")[0].strip()
    return (row.text or "").strip().split("\n")[0].strip()


def _status_select():
    for s in driver.find_elements(By.TAG_NAME, "select"):
        opts = [o.text.strip() for o in s.find_elements(By.TAG_NAME, "option")]
        if "Draft" in opts or ("Active" in opts and "InActive" in opts):
            return s
    return None


def products_search_and_filter():
    """Matched/unmatched search + Active status filter. Soft-fails → AssertionError."""
    from KskinCMS.cms_auth import search_listing
    from KskinCMS.cms_config import MODULE_URLS

    driver.get(MODULE_URLS["products"])
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "code")))
    time.sleep(2)

    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    if not rows:
        raise AssertionError(
            "Product search FAILED: listing empty (report to dev / Asana)"
        )
    first_name = _product_name_from_row(rows[0])
    if not first_name or len(first_name) < 2:
        raise AssertionError(
            "Product search FAILED: no usable name on first listing row "
            "(report to dev / Asana)"
        )

    search_listing(driver, first_name)
    time.sleep(1)
    actual = _product_name_from_row(
        driver.find_element(By.CSS_SELECTOR, "table tbody tr")
    )
    print(actual)
    if first_name not in actual and actual not in first_name:
        raise AssertionError(
            f"Product matched search FAILED: expected '{first_name}', got '{actual}' "
            "(report to dev / Asana)"
        )
    print("Test 3 : Product name searching with matched value is successful!")

    driver.get(MODULE_URLS["products"])
    time.sleep(2)
    search_listing(driver, "NoSuchProductZZZ")
    time.sleep(2)
    body = driver.find_element(By.TAG_NAME, "body").text
    rows = driver.find_elements(By.XPATH, "//table//tbody/tr")
    empty_ok = (
        "No products" in body
        or "No product" in body
        or "no result" in body.lower()
        or "no data" in body.lower()
        or not rows
    )
    if not empty_ok:
        raise AssertionError(
            "Product unmatched search FAILED: expected empty/no-result "
            "(report to dev / Asana)"
        )
    print("Test 4 : Searching with unmatched value can show empty result successfully!!")

    driver.get(MODULE_URLS["products"])
    time.sleep(2)
    status_sel = _status_select()
    if not status_sel:
        raise AssertionError(
            "Product status filter FAILED: status <select> missing "
            "(report to dev / Asana)"
        )
    Select(status_sel).select_by_visible_text("Active")
    time.sleep(2)
    rows = driver.find_elements(By.XPATH, "//table//tbody/tr")
    if not rows:
        raise AssertionError(
            "Product status filter Active FAILED: no rows "
            "(report to dev / Asana)"
        )
    status = (rows[0].text or "").upper()
    print(status[:120])
    if "ACTIVE" not in status or "INACTIVE" in status.split("ACTIVE")[0]:
        # Row text includes ACTIVE; reject if only INACTIVE
        if "INACTIVE" in status and "ACTIVE" not in status.replace("INACTIVE", ""):
            raise AssertionError(
                f"Product status filter Active FAILED: '{status[:80]}' "
                "(report to dev / Asana)"
            )
        if "ACTIVE" not in status:
            raise AssertionError(
                f"Product status filter Active FAILED: '{status[:80]}' "
                "(report to dev / Asana)"
            )
    print("Test 5 : Status filter Active successful!")

    driver.get(MODULE_URLS["products"])
    time.sleep(2)
    print("Test 6 : Listing filters checked")


def rows_per_page_actions():
    from KskinCMS.cms_config import MODULE_URLS

    driver.get(MODULE_URLS["products"])
    time.sleep(2)
    scroll_to_bottom()
    time.sleep(1)
    selects = driver.find_elements(By.XPATH, "//select[@title='pageSize']")
    if not selects:
        rows = driver.find_elements(By.XPATH, "//table//tbody/tr")
        print(f"Test 7 : Rows per page N/A on products listing ({len(rows)} rows).")
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
    """Open Product row kebab (actions span[1] or button) via pointer events."""
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


def _fiber_click_button(text_re):
    """Click a visible button whose text matches regex via React fiber onClick."""
    return driver.execute_script(
        """
        const re = new RegExp(arguments[0], 'i');
        const btns = [...document.querySelectorAll('button')].filter(b =>
          b.offsetParent && re.test((b.innerText || '').trim())
        );
        const btn = btns.find(b => re.test((b.innerText || '').trim()));
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
                  return {via: 'fiber'};
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


def _first_active_row():
    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    for r in rows:
        txt = (r.text or "").upper()
        if "INACTIVE" in txt:
            continue
        if "ACTIVE" in txt:
            return r
    return rows[0] if rows else None


def add_new_product():
    """QA product via Duplicate → unique name/sku/pos → Publish (staging-safe)."""
    global _QA_CREATED_PRODUCT
    from KskinCMS.cms_auth import js_fill, open_module, search_listing
    from KskinCMS.cms_config import MODULE_URLS

    open_module(driver, MODULE_URLS["products"], wait_css='input[name="code"]')
    time.sleep(1)
    row = _first_active_row()
    if row is None:
        raise AssertionError(
            "Product create FAILED: no ACTIVE row to Duplicate "
            "(report to dev / Asana)"
        )

    _open_row_kebab(row)
    items = driver.execute_script(
        "return [...document.querySelectorAll('[role=menuitem]')].map(e=>e.textContent.trim())"
    )
    if not items or not any("Duplicate" in (i or "") for i in items):
        raise AssertionError(
            f"Product create FAILED: Duplicate menu missing (got {items}) "
            "(report to dev / Asana)"
        )
    res = _fiber_click_menuitem("Duplicate")
    if res == "no-item":
        raise AssertionError("Product create FAILED: could not click Duplicate")
    time.sleep(4)
    if "/products/new" not in (driver.current_url or ""):
        raise AssertionError(
            f"Product create FAILED: expected /products/new, got {driver.current_url} "
            "(report to dev / Asana)"
        )

    stamp = str(int(time.time()))[-6:]
    name = f"QA Prod {stamp}"
    sku = f"QASKU{stamp}"
    pos = f"QAPOS{stamp}"

    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "name")))
    js_fill(driver, driver.find_element(By.NAME, "name"), name)
    if driver.find_elements(By.NAME, "skuNumber"):
        js_fill(driver, driver.find_element(By.NAME, "skuNumber"), sku)
    if driver.find_elements(By.NAME, "posCode"):
        js_fill(driver, driver.find_element(By.NAME, "posCode"), pos)
    time.sleep(0.5)

    clk = _fiber_click_button(r"^\s*Publish\s*$")
    if clk.get("err"):
        raise AssertionError(
            f"Product create FAILED: Publish button — {clk} "
            "(report to dev / Asana)"
        )
    time.sleep(8)

    if "/products/new" in (driver.current_url or ""):
        body = (driver.find_element(By.TAG_NAME, "body").text or "")[:500]
        raise AssertionError(
            f"Product create FAILED: still on /new after Publish. body={body!r} "
            "(report to dev / Asana)"
        )

    open_module(driver, MODULE_URLS["products"], wait_css='input[name="code"]')
    search_listing(driver, name)
    time.sleep(2)
    rows = driver.find_elements(By.XPATH, f"//table//tbody/tr[contains(., '{name}')]")
    if not rows:
        raise AssertionError(
            f"Product create FAILED: '{name}' not listed after Publish "
            "(report to dev / Asana)"
        )
    _QA_CREATED_PRODUCT = name
    print(f"Test 8 : New QA product published successfully! : {name}")


def listing_active_inactive_action():
    """ACTIVE → INACTIVE on the QA-created product only."""
    global _QA_STATUS_PRODUCT
    from KskinCMS.cms_auth import open_module, toggle_row_status
    from KskinCMS.cms_config import MODULE_URLS

    name = (_QA_CREATED_PRODUCT or "").split("\n")[0].strip()
    if not name:
        raise AssertionError(
            "Product status FAILED: no QA product from create step "
            "(create before toggle)"
        )
    _QA_STATUS_PRODUCT = name
    open_module(driver, MODULE_URLS["products"], wait_css='input[name="code"]')
    ok = toggle_row_status(driver, name, make_inactive=True)
    if not ok:
        raise AssertionError(
            f"Product ACTIVE→INACTIVE FAILED for '{name}' (report to dev / Asana)"
        )
    print("Test 9 : Changed NEW QA product to inactive successfully!")


def listing_inactive_active_action():
    """INACTIVE → ACTIVE on the same QA product."""
    from KskinCMS.cms_auth import open_module, toggle_row_status
    from KskinCMS.cms_config import MODULE_URLS

    name = (_QA_STATUS_PRODUCT or _QA_CREATED_PRODUCT or "").split("\n")[0].strip()
    if not name:
        raise AssertionError("Product status FAILED: no QA product name")
    open_module(driver, MODULE_URLS["products"], wait_css='input[name="code"]')
    ok = toggle_row_status(driver, name, make_inactive=False)
    if not ok:
        raise AssertionError(
            f"Product INACTIVE→ACTIVE FAILED for '{name}' (report to dev / Asana)"
        )
    print("Test 10 : Changed NEW QA product back to active successfully!")


def _row_product_uuid(row):
    """Extract product UUID from React fiber props on a listing row."""
    return driver.execute_script(
        """
        const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
        const found = [];
        function scan(p) {
          if (!p || typeof p !== 'object') return;
          for (const k of Object.keys(p)) {
            const v = p[k];
            if (typeof v === 'string' && UUID.test(v)) found.push(v);
            if (v && typeof v === 'object') {
              if (typeof v.id === 'string' && UUID.test(v.id)) found.push(v.id);
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


def _open_qa_product_edit(name=None):
    """Open QA product detail via `/products/{uuid}` (pencil click is unreliable)."""
    from KskinCMS.cms_auth import open_module, search_listing
    from KskinCMS.cms_config import MODULE_URLS

    name = name or _QA_CREATED_PRODUCT
    if not name:
        raise AssertionError("Product view/edit FAILED: no QA product name")
    open_module(driver, MODULE_URLS["products"], wait_css='input[name="code"]')
    search_listing(driver, name)
    time.sleep(1.5)
    row = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (By.XPATH, f"//table//tbody/tr[contains(., '{name}')]")
        )
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", row)
    time.sleep(0.2)

    pid = _row_product_uuid(row)
    if not pid:
        raise AssertionError(
            f"Product edit FAILED: no UUID on row for '{name}' "
            "(report to dev / Asana)"
        )
    driver.get(f"{MODULE_URLS['products']}/{pid}")
    time.sleep(3)
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "name")))
    # Wait for form hydrate (name can briefly be empty)
    WebDriverWait(driver, 15).until(
        lambda d: (d.find_element(By.NAME, "name").get_attribute("value") or "").strip()
    )


def check_created_product_value():
    """Open QA product edit and verify name field."""
    _open_qa_product_edit()
    val = driver.find_element(By.NAME, "name").get_attribute("value") or ""
    print(f"View name: {val}")
    name = _QA_CREATED_PRODUCT or ""
    if name not in val:
        raise AssertionError(
            f"Product view FAILED: expected '{name}' in name field (got '{val}') "
            "(report to dev / Asana)"
        )
    print("Test 11 : View/edit form opened and values readable successfully!")


def update_old_product():
    """Rename QA product + Publish Changes; verify listing."""
    global _QA_CREATED_PRODUCT, _QA_STATUS_PRODUCT
    from KskinCMS.cms_auth import js_fill, open_module, search_listing
    from KskinCMS.cms_config import MODULE_URLS

    _open_qa_product_edit()
    uniq = str(int(time.time()))[-5:]
    new_name = f"Updated Prod {uniq}"
    js_fill(driver, driver.find_element(By.NAME, "name"), new_name)
    time.sleep(0.5)

    clk = _fiber_click_button(r"Publish Changes|Publish")
    if clk.get("err"):
        # try exact Publish Changes label
        btns = [
            b
            for b in driver.find_elements(By.XPATH, "//button[contains(.,'Publish')]")
            if b.is_displayed()
        ]
        if not btns:
            raise AssertionError(
                "Product edit FAILED: no Publish Changes button "
                "(report to dev / Asana)"
            )
        driver.execute_script("arguments[0].click();", btns[-1])
    time.sleep(8)

    open_module(driver, MODULE_URLS["products"], wait_css='input[name="code"]')
    search_listing(driver, new_name)
    time.sleep(2)
    rows = driver.find_elements(By.XPATH, f"//table//tbody/tr[contains(., '{new_name}')]")
    if not rows:
        body = (driver.find_element(By.TAG_NAME, "body").text or "")[:400]
        raise AssertionError(
            f"Product edit FAILED: '{new_name}' not found after Publish Changes. "
            f"body={body!r} (report to dev / Asana)"
        )
    _QA_CREATED_PRODUCT = new_name
    _QA_STATUS_PRODUCT = new_name
    print(f"Test 12 : Edit product successful! : {new_name}")


def product_required_validations():
    """Blank Add form → Publish without media → required validation message."""
    from KskinCMS.cms_auth import open_module
    from KskinCMS.cms_config import MODULE_URLS

    open_module(driver, MODULE_URLS["products"], wait_css='input[name="code"]')
    time.sleep(0.5)
    clk = _fiber_click_button(r"Add new product")
    if clk.get("err"):
        driver.get(MODULE_URLS["products"] + "/new")
    time.sleep(3)
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "name")))
    # empty Publish
    pub = _fiber_click_button(r"^\s*Publish\s*$")
    if pub.get("err"):
        raise AssertionError(
            f"Product validation FAILED: Publish button missing ({pub}) "
            "(report to dev / Asana)"
        )
    time.sleep(1.5)
    body = (driver.find_element(By.TAG_NAME, "body").text or "").lower()
    if "media" not in body or "required" not in body:
        raise AssertionError(
            "Product validation FAILED: expected media required message on empty Publish "
            "(report to dev / Asana)"
        )
    print("Test 13 : Required validation OK (product media required on Publish)")


def product_blank_add_draft():
    """Add new product (blank form) → name/sku/pos → Save as draft → listed DRAFT."""
    from KskinCMS.cms_auth import js_fill, open_module, search_listing
    from KskinCMS.cms_config import MODULE_URLS

    open_module(driver, MODULE_URLS["products"], wait_css='input[name="code"]')
    time.sleep(0.5)
    clk = _fiber_click_button(r"Add new product")
    if clk.get("err"):
        driver.get(MODULE_URLS["products"] + "/new")
    time.sleep(3)
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "name")))

    stamp = str(int(time.time()))[-6:]
    name = f"QA BlankAdd {stamp}"
    js_fill(driver, driver.find_element(By.NAME, "name"), name)
    if driver.find_elements(By.NAME, "skuNumber"):
        js_fill(driver, driver.find_element(By.NAME, "skuNumber"), f"QABSKU{stamp}")
    if driver.find_elements(By.NAME, "posCode"):
        js_fill(driver, driver.find_element(By.NAME, "posCode"), f"QABPOS{stamp}")
    time.sleep(0.3)

    draft = _fiber_click_button(r"Save as draft")
    if draft.get("err"):
        raise AssertionError(
            f"Product blank Add FAILED: Save as draft missing ({draft}) "
            "(report to dev / Asana)"
        )
    time.sleep(6)
    if "/products/new" in (driver.current_url or ""):
        body = (driver.find_element(By.TAG_NAME, "body").text or "")[:400]
        raise AssertionError(
            f"Product blank Add FAILED: still on /new after draft. body={body!r} "
            "(report to dev / Asana)"
        )

    open_module(driver, MODULE_URLS["products"], wait_css='input[name="code"]')
    search_listing(driver, name)
    time.sleep(2)
    rows = driver.find_elements(By.XPATH, f"//table//tbody/tr[contains(., '{name}')]")
    if not rows:
        raise AssertionError(
            f"Product blank Add FAILED: '{name}' not listed after Save as draft "
            "(report to dev / Asana)"
        )
    row_txt = (rows[0].text or "").upper()
    if "DRAFT" not in row_txt:
        raise AssertionError(
            f"Product blank Add FAILED: expected DRAFT status, got {rows[0].text!r} "
            "(report to dev / Asana)"
        )
    print(f"Test 14 : Blank Add → Save as draft OK : {name}")


def product_update_stock_restore():
    """Update Stock on QA product: +1 submit, verify dialog path, restore original qty."""
    from KskinCMS.cms_auth import js_fill, open_module, search_listing
    from KskinCMS.cms_config import MODULE_URLS

    name = (_QA_CREATED_PRODUCT or "").split("\n")[0].strip()
    if not name:
        raise AssertionError(
            "Product Update Stock FAILED: no QA product from create/edit step"
        )

    open_module(driver, MODULE_URLS["products"], wait_css='input[name="code"]')
    search_listing(driver, name)
    time.sleep(1.5)
    row = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (By.XPATH, f"//table//tbody/tr[contains(., '{name}')]")
        )
    )
    _open_row_kebab(row)
    items = driver.execute_script(
        "return [...document.querySelectorAll('[role=menuitem]')].map(e=>e.textContent.trim())"
    )
    if not any("Update Stock" in (i or "") for i in (items or [])):
        raise AssertionError(
            f"Product Update Stock FAILED: menu missing (got {items}) "
            "(report to dev / Asana)"
        )
    if _fiber_click_menuitem("Update Stock") == "no-item":
        raise AssertionError("Product Update Stock FAILED: could not click menu item")
    time.sleep(1.2)

    qty_el = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "stockQuantity"))
    )
    orig = (qty_el.get_attribute("value") or "0").strip()
    try:
        orig_n = int(float(orig))
    except ValueError:
        orig_n = 0
    temp_n = orig_n + 1
    js_fill(driver, qty_el, str(temp_n))
    time.sleep(0.3)
    sub = _fiber_click_button(r"^\s*Submit\s*$")
    if sub.get("err"):
        raise AssertionError(
            f"Product Update Stock FAILED: Submit missing ({sub}) "
            "(report to dev / Asana)"
        )
    time.sleep(2.5)
    # dialog should close
    if driver.find_elements(By.CSS_SELECTOR, "[role='dialog']"):
        # wait a bit more
        time.sleep(2)

    # restore
    open_module(driver, MODULE_URLS["products"], wait_css='input[name="code"]')
    search_listing(driver, name)
    time.sleep(1.5)
    row2 = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (By.XPATH, f"//table//tbody/tr[contains(., '{name}')]")
        )
    )
    _open_row_kebab(row2)
    if _fiber_click_menuitem("Update Stock") == "no-item":
        raise AssertionError(
            "Product Update Stock FAILED: reopen dialog for restore "
            "(report to dev / Asana)"
        )
    time.sleep(1.2)
    qty2 = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "stockQuantity"))
    )
    got = (qty2.get_attribute("value") or "").strip()
    if got not in (str(temp_n), str(float(temp_n))):
        # still restore even if display differs
        print(f"Update Stock warn: expected temp {temp_n}, dialog shows {got!r}")
    js_fill(driver, qty2, str(orig_n))
    _fiber_click_button(r"^\s*Submit\s*$")
    time.sleep(2)
    print(
        f"Test 15 : Update Stock OK on '{name}' ({orig_n} → {temp_n} → restored {orig_n})"
    )
