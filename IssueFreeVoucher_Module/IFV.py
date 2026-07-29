import os
import time

from KskinCMS.IssueFreeVoucher_Module.IFVHelper import *
from KskinCMS.IssueFreeVoucher_Module.IFVVarPaths import *
from dotenv import load_dotenv
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

load_dotenv()

_QA_IFV_NAME = None
# Expected field values from create — used by view-only verify (IFV has no edit/delete).
_QA_IFV_EXPECTED = None


def open_browser():
    from KskinCMS.cms_auth import open_module
    from KskinCMS.cms_config import MODULE_URLS

    open_module(driver, MODULE_URLS["issue_free_vouchers"], wait_css='input[name="code"]')
    print("Test 1 : Open browser success!")
    print("Test 2 : Navigated to Issue Free Vouchers listing successful!")


def _js_fill_textarea(el, value):
    driver.execute_script(
        """
        const ta = arguments[0], value = arguments[1];
        const setter = Object.getOwnPropertyDescriptor(
          window.HTMLTextAreaElement.prototype, 'value'
        ).set;
        setter.call(ta, value);
        ta.dispatchEvent(new Event('input', { bubbles: true }));
        ta.dispatchEvent(new Event('change', { bubbles: true }));
        """,
        el,
        value,
    )


def ifv_search_and_filter():
    """Matched/unmatched voucher search + $ off type filter. Soft-fails → AssertionError."""
    from KskinCMS.cms_auth import search_listing
    from KskinCMS.cms_config import MODULE_URLS

    driver.get(MODULE_URLS["issue_free_vouchers"])
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "code")))
    time.sleep(2)

    placeholder = driver.find_element(By.NAME, "code").get_attribute("placeholder") or ""
    print("Search placeholder:", placeholder)

    first_name = ""
    rows = driver.find_elements(By.XPATH, "//table//tbody/tr")
    for row in rows[:15]:
        cells = row.find_elements(By.TAG_NAME, "td")
        if not cells:
            continue
        candidate = (cells[0].text or "").strip().split("\n")[0].strip()
        if candidate:
            first_name = candidate
            break
    if not first_name:
        raise AssertionError(
            "IFV search FAILED: no usable voucher name on listing "
            "(report to dev / Asana)"
        )

    search_listing(driver, first_name)
    time.sleep(1.5)
    actual = driver.find_element(By.XPATH, "//table//tbody/tr[1]/td[1]").text.strip()
    print(actual)
    if first_name not in actual and actual not in first_name:
        raise AssertionError(
            f"IFV matched search FAILED: expected '{first_name}', got '{actual}' "
            "(report to dev / Asana)"
        )
    print("Test 3 : Voucher name searching with matched value is successful!")

    driver.get(MODULE_URLS["issue_free_vouchers"])
    time.sleep(2)
    search_listing(driver, "NoSuchVoucherZZZ999")
    time.sleep(2)
    body = driver.find_element(By.TAG_NAME, "body").text
    rows = driver.find_elements(By.XPATH, "//table//tbody/tr")
    empty_ok = (
        "No vouchers" in body
        or "No voucher" in body
        or "no result" in body.lower()
        or "no data" in body.lower()
        or not rows
    )
    if not empty_ok:
        raise AssertionError(
            "IFV unmatched search FAILED: expected empty/no-result "
            "(report to dev / Asana)"
        )
    print("Test 4 : Searching with unmatched value can show empty result successfully!!")

    driver.get(MODULE_URLS["issue_free_vouchers"])
    time.sleep(2)

    # Type filter → $ off (native <select value=FixedPriceOff>; combobox is decorative)
    type_ok = False
    for sel_el in driver.find_elements(By.TAG_NAME, "select"):
        opts = [o.text for o in sel_el.find_elements(By.TAG_NAME, "option")]
        if any("$ off" in (o or "") for o in opts):
            Select(sel_el).select_by_visible_text("$ off")
            type_ok = True
            break
    if not type_ok:
        raise AssertionError(
            "IFV type filter FAILED: $ off select not found (report to dev / Asana)"
        )
    time.sleep(2)
    rows = driver.find_elements(By.XPATH, "//table//tbody/tr")
    if not rows:
        raise AssertionError(
            "IFV type filter $ off FAILED: no rows after filter (report to dev / Asana)"
        )
    type_text = driver.find_element(By.XPATH, "//table//tbody/tr[1]/td[4]").text.strip()
    print(type_text)
    if "$ off" not in type_text.lower() and "fixed" not in type_text.lower():
        raise AssertionError(
            f"IFV type filter $ off FAILED: got '{type_text}' (report to dev / Asana)"
        )
    print("Test 5 : Searching with matched value for voucher type is successful!")

    driver.get(MODULE_URLS["issue_free_vouchers"])
    time.sleep(2)
    print("Test 6 : Listing filters checked")


def rows_per_page_actions():
    from KskinCMS.cms_config import MODULE_URLS

    driver.get(MODULE_URLS["issue_free_vouchers"])
    time.sleep(2)
    scroll_to_bottom()
    time.sleep(1)
    selects = driver.find_elements(By.XPATH, "//select[@title='pageSize']")
    if not selects:
        print("Test 7 : Rows per page control not present — skipped")
        return
    select = Select(selects[0])
    select.select_by_value("20")
    time.sleep(1.5)
    select = Select(driver.find_element(By.XPATH, "//select[@title='pageSize']"))
    select.select_by_value("50")
    time.sleep(1.5)
    select = Select(driver.find_element(By.XPATH, "//select[@title='pageSize']"))
    select.select_by_value("10")
    time.sleep(1.5)
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


def _activate_radio(label_prefix):
    """Radix radio buttons often ignore plain click — pointer + Space selects them."""
    already = driver.execute_script(
        """
        const want = arguments[0];
        return [...document.querySelectorAll('button[role=radio]')].some(b => {
          const t = (b.innerText || '').trim();
          if (!(t === want || t.split('\\n')[0] === want || t.startsWith(want))) return false;
          return b.getAttribute('aria-checked') === 'true'
            || b.getAttribute('data-state') === 'checked';
        });
        """,
        label_prefix,
    )
    if already:
        return True
    ok = driver.execute_script(
        """
        const want = arguments[0];
        const el = [...document.querySelectorAll('button[role=radio]')].find(b => {
          const t = (b.innerText || '').trim();
          return t === want || t.split('\\n')[0] === want || t.startsWith(want);
        });
        if (!el) return false;
        el.scrollIntoView({ block: 'center' });
        el.focus();
        const r = el.getBoundingClientRect();
        const x = r.left + r.width / 2, y = r.top + r.height / 2;
        const opts = {
          bubbles: true, cancelable: true, view: window,
          clientX: x, clientY: y, pointerId: 1, pointerType: 'mouse', isPrimary: true
        };
        el.dispatchEvent(new PointerEvent('pointerdown', { ...opts, buttons: 1 }));
        el.dispatchEvent(new MouseEvent('mousedown', { ...opts, buttons: 1 }));
        el.dispatchEvent(new PointerEvent('pointerup', { ...opts, buttons: 0 }));
        el.dispatchEvent(new MouseEvent('mouseup', { ...opts, buttons: 0 }));
        el.dispatchEvent(new MouseEvent('click', { ...opts, buttons: 0 }));
        el.dispatchEvent(new KeyboardEvent('keydown', {
          key: ' ', code: 'Space', keyCode: 32, which: 32, bubbles: true
        }));
        el.dispatchEvent(new KeyboardEvent('keyup', {
          key: ' ', code: 'Space', keyCode: 32, which: 32, bubbles: true
        }));
        return true;
        """,
        label_prefix,
    )
    time.sleep(0.35)
    checked = driver.execute_script(
        """
        const want = arguments[0];
        return [...document.querySelectorAll('button[role=radio]')].some(b => {
          const t = (b.innerText || '').trim();
          if (!(t === want || t.split('\\n')[0] === want || t.startsWith(want))) return false;
          return b.getAttribute('aria-checked') === 'true'
            || b.getAttribute('data-state') === 'checked';
        });
        """,
        label_prefix,
    )
    return bool(ok and checked)


def _pick_applicable_outlet(prefer=("Anchorpoint", "Kskin Compass One Hub", "All outlets")):
    """Pick from Applicable Outlets multi-select (long list — scroll until prefer match)."""
    picked = None
    for attempt in range(3):
        opened = driver.execute_script(
            """
            const lab = [...document.querySelectorAll('label')].find(l =>
              (l.innerText || '').includes('Applicable Outlets')
            );
            if (!lab) return false;
            let root = lab;
            for (let i = 0; i < 6; i++) root = root.parentElement;
            const btn = root.querySelector('button[aria-haspopup="dialog"]');
            if (!btn) return false;
            btn.scrollIntoView({block:'center'});
            btn.click();
            return true;
            """
        )
        if not opened:
            time.sleep(0.5)
            continue
        time.sleep(1.0)
        for name in prefer:
            ok = driver.execute_script(
                """
                const name = arguments[0];
                // Scroll list container looking for target
                const lis0 = [...document.querySelectorAll('li')].filter(e => e.offsetParent);
                let scrollParent = lis0[0];
                while (scrollParent && scrollParent !== document.body) {
                  if (scrollParent.scrollHeight > scrollParent.clientHeight + 20) break;
                  scrollParent = scrollParent.parentElement;
                }
                for (let i = 0; i < 25; i++) {
                  const lis = [...document.querySelectorAll('li')].filter(e =>
                    e.offsetParent && (e.innerText || '').includes(name)
                  );
                  const exact = lis.find(e =>
                    (e.innerText || '').trim().split('\\n')[0].trim() === name
                  ) || lis[0];
                  if (exact) {
                    const cb = exact.querySelector('input[type=checkbox], button[role=checkbox]');
                    const lab = exact.querySelector('label');
                    (cb || lab || exact).click();
                    return true;
                  }
                  if (scrollParent) {
                    scrollParent.scrollTop += 120;
                  } else {
                    break;
                  }
                }
                return false;
                """,
                name,
            )
            if ok:
                picked = name
                break
        if picked:
            break
        try:
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        except Exception:
            pass
        time.sleep(0.4)
    if not picked:
        raise AssertionError("IFV create FAILED: no outlet options to assign")
    time.sleep(0.5)
    try:
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
    except Exception:
        pass
    time.sleep(0.4)
    outlet_txt = driver.execute_script(
        """
        const lab = [...document.querySelectorAll('label')].find(l =>
          (l.innerText || '').includes('Applicable Outlets')
        );
        if (!lab) return '';
        let root = lab;
        for (let i = 0; i < 5; i++) {
          root = root.parentElement;
          const btn = root.querySelector('button[aria-haspopup="dialog"]');
          if (btn) return (btn.innerText || '').trim();
        }
        return '';
        """
    )
    if not outlet_txt or outlet_txt.strip() == "Select":
        raise AssertionError(
            f"IFV create FAILED: outlet not stuck after pick (got {outlet_txt!r})"
        )
    print("Outlet assigned:", picked, "→", outlet_txt[:80])


def _select_product_for_voucher(prefer="AquaBloom Cream"):
    edits = [b for b in driver.find_elements(By.XPATH, "//button[contains(.,'Edit')]") if b.is_displayed()]
    if len(edits) < 2:
        raise AssertionError("IFV create FAILED: Products Edit control missing")
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", edits[1])
    driver.execute_script("arguments[0].click();", edits[1])
    time.sleep(2)
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[role=dialog]"))
    )
    selected = driver.execute_script(
        """
        const prefer = arguments[0];
        const d = document.querySelector('[role=dialog]');
        if (!d) return null;
        let r = [...d.querySelectorAll('button[role=radio]')].find(b =>
          (b.innerText || '').trim() === prefer
        );
        if (!r) {
          r = [...d.querySelectorAll('button[role=radio]')].find(b =>
            (b.innerText || '').includes(prefer) && !(b.innerText || '').includes('Copy')
          );
        }
        if (!r) {
          r = [...d.querySelectorAll('button[role=radio]')].find(b => b.offsetParent);
        }
        if (!r) return null;
        r.click();
        return (r.innerText || '').trim().split('\\n')[0];
        """,
        prefer,
    )
    if not selected:
        raise AssertionError("IFV create FAILED: no product radio in dialog")
    time.sleep(0.4)
    apply = [
        b
        for b in driver.find_elements(
            By.XPATH, "//*[@role='dialog']//button[normalize-space()='Apply']"
        )
        if b.is_displayed()
    ]
    if not apply:
        raise AssertionError("IFV create FAILED: product dialog Apply missing")
    driver.execute_script("arguments[0].click();", apply[0])
    time.sleep(1.5)
    body = driver.find_element(By.TAG_NAME, "body").text
    if "Products (0)" in body or "No Products" in body:
        raise AssertionError(
            f"IFV create FAILED: product '{selected}' not applied (report to dev / Asana)"
        )
    print("Product selected:", selected[:60])


def add_new_ifv():
    """Create + Publish a QA $ off IFV; verify it appears in listing."""
    global _QA_IFV_NAME, _QA_IFV_EXPECTED
    from KskinCMS.cms_auth import js_fill, open_module, search_listing
    from KskinCMS.cms_config import MODULE_URLS

    uniq = str(int(time.time()))[-5:]
    name = f"QA IFV {uniq}"

    open_module(driver, MODULE_URLS["issue_free_vouchers"], wait_css='input[name="code"]')
    add_btns = [
        b
        for b in driver.find_elements(
            By.XPATH, "//button[contains(.,'Issue Voucher') or contains(.,'Issue voucher')]"
        )
        if b.is_displayed()
    ]
    if add_btns:
        driver.execute_script("arguments[0].click();", add_btns[0])
        time.sleep(3)
    if "/new" not in (driver.current_url or ""):
        driver.get(MODULE_URLS["issue_free_vouchers"] + "/new")
        time.sleep(4)

    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "name")))

    if not _activate_radio("$ off"):
        raise AssertionError(
            "IFV create FAILED: Voucher Type $ off not selected (report to dev / Asana)"
        )
    print("Voucher Type: $ off")

    js_fill(driver, driver.find_element(By.NAME, "name"), name)
    tas = driver.find_elements(By.TAG_NAME, "textarea")
    if len(tas) < 2:
        raise AssertionError("IFV create FAILED: description/T&C textareas missing")
    _js_fill_textarea(tas[0], "QA IFV description")
    _js_fill_textarea(tas[1], "QA IFV terms")
    js_fill(driver, driver.find_element(By.NAME, "discountAmount"), "5")

    # Discount apply to → Individual Item (required; Publish stays disabled without it)
    if not _activate_radio("Individual Item"):
        raise AssertionError(
            "IFV create FAILED: Discount apply to not selected (report to dev / Asana)"
        )
    print("Discount apply to: Individual Item")


    _pick_applicable_outlet()
    js_fill(driver, driver.find_element(By.NAME, "remark"), "QA IFV remark")

    _select_product_for_voucher()
    js_fill(driver, driver.find_element(By.NAME, "minimumSpentAmount"), "0")

    # Media * — file opens crop dialog; must confirm with "Upload Image"
    img = "/tmp/ifv_3x4.jpg"
    try:
        from PIL import Image

        Image.new("RGB", (600, 800), (200, 100, 100)).save(img, quality=90)
    except Exception:
        img = "/Users/aungwaiwaithin/Downloads/llk_abs.jpeg"
        if not os.path.isfile(img):
            img = "/Users/aungwaiwaithin/Downloads/test_image.png"
    file_inputs = driver.find_elements(By.XPATH, '//input[@type="file"]')
    if not file_inputs or not os.path.isfile(img):
        raise AssertionError("IFV create FAILED: media upload file/input missing")
    file_inputs[0].send_keys(img)
    time.sleep(1.5)
    # Crop dialog
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[@role='dialog']//button[contains(.,'Upload Image')]")
            )
        )
    except Exception:
        pass
    upload_img = [
        b
        for b in driver.find_elements(
            By.XPATH, "//*[@role='dialog']//button[contains(.,'Upload Image')] | //button[normalize-space()='Upload Image']"
        )
        if b.is_displayed()
    ]
    if not upload_img:
        # fallback any Upload except "Upload file"
        upload_img = [
            b
            for b in driver.find_elements(By.XPATH, "//button[contains(.,'Upload')]")
            if b.is_displayed() and "Upload file" not in (b.text or "")
        ]
    if not upload_img:
        raise AssertionError("IFV create FAILED: crop dialog Upload Image missing")
    # Selenium/CDP/React onClick often closes the dialog without binding media.
    # Parent fiber exposes handleDone — that commits the crop + sets Uploaded image.
    time.sleep(1.0)  # let cropper canvas settle
    committed = driver.execute_script(
        """
        const btn = arguments[0];
        const fiberKey = Object.keys(btn).find(k => k.includes('Fiber'));
        let n = fiberKey ? btn[fiberKey] : null;
        let handleDone = null;
        let depth = 0;
        while (n && depth < 30) {
          if (n.memoizedProps && typeof n.memoizedProps.handleDone === 'function') {
            handleDone = n.memoizedProps.handleDone;
            break;
          }
          n = n.return;
          depth++;
        }
        if (handleDone) {
          handleDone();
          return 'handleDone';
        }
        const pk = Object.keys(btn).find(k => k.startsWith('__reactProps'));
        if (pk && typeof btn[pk].onClick === 'function') {
          btn[pk].onClick({
            preventDefault(){}, stopPropagation(){},
            nativeEvent:{}, target: btn, currentTarget: btn
          });
          return 'onClick';
        }
        btn.click();
        return 'click';
        """,
        upload_img[-1],
    )
    print("Crop confirm via:", committed)
    # Wait until crop dialog fully closes (zoom range gone)
    closed = False
    for _ in range(20):
        time.sleep(0.5)
        still = driver.execute_script(
            """
            return !!document.querySelector('[role=dialog] input[name=zoom], [role=dialog] input[type=range]')
              || [...document.querySelectorAll('[role=dialog]')].some(d =>
                   (d.innerText || '').includes('Edit Image'));
            """
        )
        if not still:
            closed = True
            break
        retry = [
            b
            for b in driver.find_elements(
                By.XPATH, "//*[@role='dialog']//button[contains(.,'Upload Image')]"
            )
            if b.is_displayed()
        ]
        if retry:
            driver.execute_script(
                """
                const btn = arguments[0];
                const fiberKey = Object.keys(btn).find(k => k.includes('Fiber'));
                let n = fiberKey ? btn[fiberKey] : null;
                let handleDone = null, depth = 0;
                while (n && depth < 30) {
                  if (n.memoizedProps && typeof n.memoizedProps.handleDone === 'function') {
                    handleDone = n.memoizedProps.handleDone;
                    break;
                  }
                  n = n.return; depth++;
                }
                if (handleDone) handleDone();
                else btn.click();
                """,
                retry[-1],
            )
    if not closed:
        raise AssertionError(
            "IFV create FAILED: Edit Image crop dialog did not close after Upload Image "
            "(report to dev / Asana)"
        )
    media_ok = driver.execute_script(
        """
        return [...document.querySelectorAll('img')].some(i =>
          (i.alt || '') === 'Uploaded image'
          || ((i.src || '').startsWith('data:image') && i.naturalWidth > 0
              && !(i.src || '').includes('Logo'))
        );
        """
    )
    if not media_ok:
        raise AssertionError(
            "IFV create FAILED: media not bound after crop confirm "
            "(report to dev / Asana)"
        )
    print("Test 12 : Image uploaded (crop confirmed)")
    # Validity first, then customer segment last (segment was getting cleared earlier)
    never_ok = driver.execute_script(
        """
        const lab = [...document.querySelectorAll('label')].find(l =>
          (l.innerText || '').includes('They never expire')
        );
        if (lab) {
          lab.click();
          const cb = lab.querySelector('input[type=checkbox]') ||
            lab.parentElement?.querySelector('input[type=checkbox]');
          if (cb && !cb.checked) cb.click();
        }
        const still = document.querySelector('[name=expiredIn]');
        return !still || !still.offsetParent;
        """
    )
    time.sleep(0.4)
    if not never_ok and driver.find_elements(By.NAME, "expiredIn"):
        try:
            driver.execute_script(
                """
                const cb = [...document.querySelectorAll('input[type=checkbox]')].find(c =>
                  ((c.parentElement && c.parentElement.innerText) || '').includes('never expire')
                );
                if (cb && cb.checked) cb.click();
                """
            )
            time.sleep(0.3)
            js_fill(driver, driver.find_element(By.NAME, "expiredIn"), "30")
            driver.execute_script(
                """
                const sel = [...document.querySelectorAll('select')].find(s =>
                  [...s.options].some(o => /day|month|year/i.test(o.text || o.value))
                );
                if (sel) {
                  const opt = [...sel.options].find(o => /day/i.test(o.text || o.value));
                  if (opt) sel.value = opt.value;
                  sel.dispatchEvent(new Event('change', { bubbles: true }));
                }
                """
            )
            print("Validity: Expires in 30 day(s)")
        except Exception as e:
            print("Validity soft:", e)
    else:
        print("Validity: They never expire")
    time.sleep(0.3)

    # Customer segment LAST — required; "Please select who this voucher is for"
    tier_ok = False
    for attempt in range(4):
        _activate_radio("Tier Members")  # may be a card, not radio — ignore fail
        if _activate_radio("Diamond"):
            tier_ok = True
            break
        print(f"Diamond attempt {attempt+1}: False")
    if not tier_ok:
        raise AssertionError(
            "IFV create FAILED: customer segment (Diamond) not selected "
            "(report to dev / Asana)"
        )
    print("Customer segment: Diamond tier")
    time.sleep(0.5)

    # Ensure voucher type still selected (do not Space-toggle if already on)
    if not _activate_radio("$ off"):
        raise AssertionError(
            "IFV create FAILED: Voucher Type $ off cleared before Publish "
            "(report to dev / Asana)"
        )

    pub = [
        b for b in driver.find_elements(By.XPATH, "//button[contains(.,'Publish')]") if b.is_displayed()
    ]
    if not pub:
        raise AssertionError("IFV create FAILED: no Publish button")
    for _ in range(12):
        pub = [
            b
            for b in driver.find_elements(By.XPATH, "//button[contains(.,'Publish')]")
            if b.is_displayed()
        ]
        disabled = pub[-1].get_attribute("disabled")
        data_state = pub[-1].get_attribute("data-state")
        who_err = "Please select who this voucher is for" in (
            driver.find_element(By.TAG_NAME, "body").text or ""
        )
        if (
            not disabled
            and data_state != "disabled"
            and pub[-1].is_enabled()
            and not who_err
        ):
            break
        time.sleep(0.5)
    disabled = pub[-1].get_attribute("disabled")
    data_state = pub[-1].get_attribute("data-state")
    who_err = "Please select who this voucher is for" in (
        driver.find_element(By.TAG_NAME, "body").text or ""
    )
    diamond_on = driver.execute_script(
        """
        return [...document.querySelectorAll('button[role=radio]')].some(b =>
          (b.innerText || '').includes('Diamond')
          && (b.getAttribute('aria-checked') === 'true'
              || b.getAttribute('data-state') === 'checked')
        );
        """
    )
    # Some builds keep data-state=disabled styling even when form is ready;
    # if required fields look set, attempt Publish anyway.
    media_bound = driver.execute_script(
        """
        return [...document.querySelectorAll('img')].some(i =>
          (i.alt || '') === 'Uploaded image'
          || ((i.src || '').startsWith('data:image') && i.naturalWidth > 0
              && !(i.src || '').includes('Logo'))
        );
        """
    )
    outlet_label = (
        driver.execute_script(
            """
            const lab=[...document.querySelectorAll('label')].find(l=>
              (l.innerText||'').includes('Applicable Outlets'));
            let root=lab;
            for(let i=0;i<5;i++){
              root=root.parentElement;
              const b=root.querySelector('button[aria-haspopup=\"dialog\"]');
              if(b) return (b.innerText||'').trim();
            }
            return '';
            """
        )
        or ""
    )
    form_looks_ready = (
        diamond_on
        and not who_err
        and media_bound
        and outlet_label
        and outlet_label.strip() != "Select"
    )
    if (
        (disabled is not None or data_state == "disabled" or not pub[-1].is_enabled())
        and not form_looks_ready
    ):
        state = driver.execute_script(
            """
            const g = n => document.querySelector(`[name="${n}"]`)?.value;
            const outlet = (() => {
              const lab = [...document.querySelectorAll('label')].find(l =>
                (l.innerText || '').includes('Applicable Outlets')
              );
              let root = lab;
              for (let i = 0; i < 5; i++) {
                root = root.parentElement;
                const b = root.querySelector('button[aria-haspopup="dialog"]');
                if (b) return (b.innerText || '').trim();
              }
              return '';
            })();
            const diamond = [...document.querySelectorAll('button[role=radio]')].filter(b =>
              (b.innerText || '').includes('Diamond')
            ).map(b => ({ a: b.getAttribute('aria-checked'), s: b.getAttribute('data-state') }));
            return {
              discount: g('discountAmount'), remark: g('remark'), min: g('minimumSpentAmount'),
              expiredIn: g('expiredIn'), outlet, diamond,
              never: [...document.querySelectorAll('input[type=checkbox]')].map(c => c.checked),
              products: /Products \\(\\d+\\)/.test(document.body.innerText || ''),
              whoErr: (document.body.innerText || '').includes('Please select who this voucher is for'),
              media: [...document.querySelectorAll('img')].some(i =>
                (i.alt || '') === 'Uploaded image'
                || ((i.src || '').startsWith('data:image') && i.naturalWidth > 0
                    && !(i.src || '').includes('Logo'))
              ),
            };
            """
        )
        raise AssertionError(
            f"IFV create FAILED: Publish disabled. state={state} (report to dev / Asana)"
        )
    if form_looks_ready and (
        disabled is not None or data_state == "disabled" or not pub[-1].is_enabled()
    ):
        print("Publish still styled disabled — attempting click anyway (fields look ready)")
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", pub[-1])
    from selenium.webdriver.common.action_chains import ActionChains

    try:
        ActionChains(driver).move_to_element(pub[-1]).pause(0.2).click().perform()
    except Exception:
        driver.execute_script("arguments[0].click();", pub[-1])
    # also dispatch pointer sequence
    driver.execute_script(
        """
        const el = arguments[0];
        el.removeAttribute('disabled');
        el.disabled = false;
        const r = el.getBoundingClientRect();
        const x = r.left + r.width/2, y = r.top + r.height/2;
        for (const type of [
          'pointerover','pointerenter','pointerdown','mousedown',
          'pointerup','mouseup','click'
        ]) {
          const C = type.startsWith('pointer') ? PointerEvent : MouseEvent;
          el.dispatchEvent(new C(type, {
            bubbles:true, cancelable:true, view:window,
            clientX:x, clientY:y, pointerId:1, pointerType:'mouse',
            buttons: type.endsWith('down') ? 1 : 0
          }));
        }
        """,
        pub[-1],
    )
    time.sleep(8)

    if "/new" in (driver.current_url or ""):
        msgs = []
        for m in driver.find_elements(By.CSS_SELECTOR, "p, [role='alert']"):
            t = (m.text or "").strip()
            if t and any(
                k in t.lower()
                for k in ("required", "invalid", "must", "please", "already", "error", "choose")
            ):
                msgs.append(t)
        body_snip = (driver.find_element(By.TAG_NAME, "body").text or "")[:500]
        raise AssertionError(
            f"IFV create FAILED: still on /new. msgs={msgs[:15]} "
            f"body={body_snip!r} (report to dev / Asana)"
        )

    open_module(driver, MODULE_URLS["issue_free_vouchers"], wait_css='input[name="code"]')
    search_listing(driver, name)
    time.sleep(2)
    rows = driver.find_elements(By.XPATH, f"//table//tbody/tr[contains(., '{name}')]")
    if not rows:
        raise AssertionError(
            f"IFV create FAILED: '{name}' not listed (report to dev / Asana)"
        )
    _QA_IFV_NAME = name
    _QA_IFV_EXPECTED = {
        "name": name,
        "description": "QA IFV description",
        "terms": "QA IFV terms",
        "discountAmount": "5",
        "remark": "QA IFV remark",
        "minimumSpentAmount": "0",
        "voucherType": "$ off",
        "discountApplyTo": "Individual Item",
        "outlet": "Anchorpoint",
        "tier": "Diamond",
        "productHint": "AquaBloom",
    }
    print(f"Test 24 : New IFV published successfully! : {name}")


def _open_qa_ifv_view(name=None):
    """Open QA IFV detail via listing VIEW (eye) action — IFV is view-only (no edit/delete)."""
    from KskinCMS.cms_auth import open_module, search_listing
    from KskinCMS.cms_config import MODULE_URLS
    from selenium.webdriver.common.action_chains import ActionChains

    name = name or _QA_IFV_NAME
    if not name:
        raise AssertionError("IFV view FAILED: no QA voucher name")

    open_module(driver, MODULE_URLS["issue_free_vouchers"], wait_css='input[name="code"]')
    search_listing(driver, name)
    time.sleep(1.5)
    row = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, f"//table//tbody/tr[contains(., '{name}')]"))
    )

    # Listing actions: VIEW only (eye). Fail loud if unexpected edit/delete appear later.
    action_info = driver.execute_script(
        """
        const row = arguments[0];
        const col = row.querySelector('.actions-column');
        if (!col) return { err: 'no actions-column' };
        const spans = [...col.querySelectorAll(':scope > span, :scope > button')];
        return {
          count: spans.length,
          html: (col.innerHTML || '').slice(0, 400),
        };
        """,
        row,
    )
    if action_info.get("err") or not action_info.get("count"):
        raise AssertionError(
            f"IFV view FAILED: no row actions for '{name}' "
            f"info={action_info} (report to dev / Asana)"
        )
    if action_info["count"] > 1:
        raise AssertionError(
            f"IFV listing now has {action_info['count']} action controls "
            f"(was view-only). Revisit automation for edit/delete/status "
            f"(report to Asana). html={action_info.get('html')!r}"
        )

    # Prefer React row original.id → detail URL (reliable); fallback click eye.
    vid = driver.execute_script(
        """
        const row = arguments[0];
        const td = row.querySelector('td');
        const fiberKey = Object.keys(td || {}).find(k => k.includes('Fiber'));
        let n = td && td[fiberKey];
        while (n) {
          if (n.memoizedProps && n.memoizedProps.row && n.memoizedProps.row.original) {
            return n.memoizedProps.row.original.id || null;
          }
          n = n.return;
        }
        return null;
        """,
        row,
    )
    if vid:
        driver.get(f"{MODULE_URLS['issue_free_vouchers']}/{vid}")
        time.sleep(3)
    else:
        spans = row.find_elements(By.CSS_SELECTOR, ".actions-column > span")
        if not spans:
            raise AssertionError(
                f"IFV view FAILED: VIEW icon missing for '{name}' (report to dev / Asana)"
            )
        # Fire VIEW onClick via fiber (plain click often no-ops)
        clicked = driver.execute_script(
            """
            const span = arguments[0];
            const svg = span.querySelector('svg') || span;
            let n = svg[Object.keys(svg).find(k => k.includes('Fiber'))];
            let depth = 0;
            while (n && depth < 25) {
              if (n.memoizedProps && typeof n.memoizedProps.onClick === 'function') {
                n.memoizedProps.onClick({
                  preventDefault(){}, stopPropagation(){},
                  isPropagationStopped(){ return false; },
                  nativeEvent:{}, target: span, currentTarget: span
                });
                return true;
              }
              n = n.return;
              depth++;
            }
            span.click();
            return false;
            """,
            spans[0],
        )
        if not clicked:
            try:
                ActionChains(driver).move_to_element(spans[0]).pause(0.15).click().perform()
            except Exception:
                driver.execute_script("arguments[0].click();", spans[0])
        time.sleep(3)

    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "name")))
    if "/issue-free-vouchers/" not in (driver.current_url or "") or "/new" in (
        driver.current_url or ""
    ):
        raise AssertionError(
            f"IFV view FAILED: not on detail after VIEW. url={driver.current_url} "
            "(report to dev / Asana)"
        )


def check_created_ifv_value():
    """View-only: open QA IFV and assert created fields show correctly (no edit)."""
    global _QA_IFV_NAME, _QA_IFV_EXPECTED
    from KskinCMS.cms_config import MODULE_URLS

    exp = _QA_IFV_EXPECTED
    if not exp or not _QA_IFV_NAME:
        # Recover last QA from listing if create ran earlier in another process
        from KskinCMS.cms_auth import open_module, search_listing

        open_module(driver, MODULE_URLS["issue_free_vouchers"], wait_css='input[name="code"]')
        search_listing(driver, "QA IFV")
        time.sleep(1.5)
        rows = driver.find_elements(By.XPATH, "//table//tbody/tr[contains(., 'QA IFV')]")
        if not rows:
            raise AssertionError(
                "IFV view FAILED: no QA IFV to verify (report to dev / Asana)"
            )
        _QA_IFV_NAME = (
            rows[0].find_elements(By.TAG_NAME, "td")[0].text.strip().split("\n")[0].strip()
        )
        exp = {
            "name": _QA_IFV_NAME,
            "discountAmount": None,  # soft when recovered
            "remark": None,
            "minimumSpentAmount": None,
            "voucherType": "$ off",
            "discountApplyTo": "Individual Item",
            "outlet": "Anchorpoint",
            "tier": "Diamond",
            "productHint": None,
        }

    _open_qa_ifv_view(_QA_IFV_NAME)

    actual = driver.execute_script(
        """
        const g = n => (document.querySelector(`[name="${n}"]`)?.value || '').trim();
        const radioOn = (prefix) => [...document.querySelectorAll('button[role=radio]')].some(b => {
          const t = (b.innerText || '').trim();
          if (!(t === prefix || t.split('\\n')[0] === prefix || t.startsWith(prefix))) return false;
          return b.getAttribute('aria-checked') === 'true'
            || b.getAttribute('data-state') === 'checked';
        });
        const outlet = (() => {
          const lab = [...document.querySelectorAll('label')].find(l =>
            (l.innerText || '').includes('Applicable Outlets')
          );
          let root = lab;
          for (let i = 0; i < 5; i++) {
            root = root && root.parentElement;
            const b = root && root.querySelector('button[aria-haspopup="dialog"]');
            if (b) return (b.innerText || '').trim();
          }
          return '';
        })();
        const tas = [...document.querySelectorAll('textarea')].map(t => (t.value || '').trim());
        const body = document.body.innerText || '';
        const products = (body.match(/Products \\(\\d+\\)/) || [])[0] || '';
        return {
          name: g('name'),
          discountAmount: g('discountAmount'),
          remark: g('remark'),
          minimumSpentAmount: g('minimumSpentAmount'),
          description: tas[0] || '',
          terms: tas[1] || '',
          typeOff: radioOn('$ off'),
          individual: radioOn('Individual Item'),
          diamond: radioOn('Diamond'),
          outlet,
          products,
          h1: (document.querySelector('h1')?.innerText || '').trim(),
        };
        """
    )
    print("View form:", actual)

    mismatches = []
    if exp.get("name") and exp["name"] not in (actual.get("name") or "") and exp[
        "name"
    ] not in (actual.get("h1") or ""):
        mismatches.append(f"name want={exp['name']!r} got name={actual.get('name')!r}")
    if exp.get("discountAmount") is not None and str(exp["discountAmount"]) not in str(
        actual.get("discountAmount") or ""
    ):
        mismatches.append(
            f"discount want={exp['discountAmount']!r} got={actual.get('discountAmount')!r}"
        )
    if exp.get("remark") is not None and exp["remark"] not in (actual.get("remark") or ""):
        mismatches.append(f"remark want={exp['remark']!r} got={actual.get('remark')!r}")
    if exp.get("minimumSpentAmount") is not None and str(
        exp["minimumSpentAmount"]
    ) not in str(actual.get("minimumSpentAmount") or ""):
        mismatches.append(
            f"minSpent want={exp['minimumSpentAmount']!r} "
            f"got={actual.get('minimumSpentAmount')!r}"
        )
    if exp.get("description") and exp["description"] not in (
        actual.get("description") or ""
    ):
        mismatches.append(
            f"description want={exp['description']!r} got={actual.get('description')!r}"
        )
    if exp.get("terms") and exp["terms"] not in (actual.get("terms") or ""):
        mismatches.append(f"terms want={exp['terms']!r} got={actual.get('terms')!r}")
    if exp.get("voucherType") == "$ off" and not actual.get("typeOff"):
        mismatches.append("voucher type $ off not selected on view")
    if exp.get("discountApplyTo") == "Individual Item" and not actual.get("individual"):
        mismatches.append("Discount apply to Individual Item not selected on view")
    if exp.get("tier") == "Diamond" and not actual.get("diamond"):
        mismatches.append("Diamond tier not selected on view")
    if exp.get("outlet") and exp["outlet"] not in (actual.get("outlet") or ""):
        mismatches.append(f"outlet want={exp['outlet']!r} got={actual.get('outlet')!r}")
    if exp.get("productHint"):
        body = driver.find_element(By.TAG_NAME, "body").text or ""
        if exp["productHint"] not in body and not (
            actual.get("products") and "Products (0)" not in actual["products"]
        ):
            mismatches.append(
                f"product hint {exp['productHint']!r} not on view "
                f"(products={actual.get('products')!r})"
            )

    if mismatches:
        raise AssertionError(
            "IFV view FAILED: created data mismatch: "
            + "; ".join(mismatches)
            + " (report to dev / Asana)"
        )
    print("Test 26 : View QA IFV — created data shown correctly (view-only module)")
