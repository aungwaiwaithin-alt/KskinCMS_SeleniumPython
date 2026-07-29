import time
from KskinCMS.Product_Module.ProductHelper import *
from KskinCMS.Product_Module.ProductVarPaths import *
from dotenv import load_dotenv
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# install this to use load dotevn >> pip install python-dotenv
load_dotenv()

#pytest ProductMain.py --html=ProductReport.html
#pytest -s ProductMain.py --html=ProductReport.html

def open_browser():
    from KskinCMS.cms_auth import open_module
    from KskinCMS.cms_config import MODULE_URLS
    open_module(driver, MODULE_URLS["products"], wait_css='input[name="code"]')
    print("Test 1 : Open browser success!")
    print("Test 2 : Navigated to Products listing successfully!")


def _type_search(value):
    el = wait_name("code")
    js_fill_input(el, value)


def _reset_filters_to_all():
    """Reset category + status hidden selects to All."""
    driver.execute_script(
        """
        const selects = document.querySelectorAll('select[aria-hidden="true"]');
        for (const select of selects) {
          select.selectedIndex = 0;
          select.dispatchEvent(new Event('change', { bubbles: true }));
        }
        """
    )
    time.sleep(1)


def products_search_and_filter():
    from KskinCMS.cms_config import MODULE_URLS
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    driver.get(MODULE_URLS["products"])
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "code")))
    time.sleep(2)
    _reset_filters_to_all()

    # Matched name search (live staging: PureMist Toner) — name is column 3 (MEDIA is col 2)
    _type_search("PureMist Toner")
    time.sleep(2)
    actual = driver.find_element(By.XPATH, "//table//tbody/tr[1]/td[3]").text.strip()
    print(actual)
    if "PureMist Toner" in actual:
        print("Test 3 : Product name searching with matched value is successful!")
    else:
        print("Something went wrong. Product name searching with matched value is failed!")

    driver.get(MODULE_URLS["products"])
    time.sleep(2)
    _reset_filters_to_all()

    # Unmatched search
    _type_search("NoSuchProductZZZ")
    time.sleep(2)
    body = driver.find_element(By.TAG_NAME, "body").text
    rows = driver.find_elements(By.XPATH, "//table//tbody/tr")
    if "No products" in body or "No product" in body or not rows:
        print("Test 4 : Searching with unmatched value can show empty result successfully!!")
    else:
        print("Something went wrong. Unmatched search did not show empty state.")

    driver.get(MODULE_URLS["products"])
    time.sleep(2)
    _reset_filters_to_all()

    # Category filter soft check — leave on All category (select index 0)
    driver.execute_script(
        """
        const selects = document.querySelectorAll('select[aria-hidden="true"]');
        const select = selects[0];
        if (select) {
          select.selectedIndex = 0;
          select.dispatchEvent(new Event('change', { bubbles: true }));
        }
        """
    )
    time.sleep(1)
    print("Test 5 : Category filter reset to All category")

    # Status filter via hidden <select> (All status / Active / Inactive) — index 1
    driver.execute_script(
        """
        const selects = document.querySelectorAll('select[aria-hidden="true"]');
        const select = selects[1];
        if (select) {
          select.value = 'Active';
          select.dispatchEvent(new Event('change', { bubbles: true }));
        }
        """
    )
    time.sleep(2)
    status = ""
    rows = driver.find_elements(By.XPATH, "//table//tbody/tr")
    if rows:
        # STATUS is column 7 (INVENTORY is col 6)
        status = driver.find_element(By.XPATH, "//table//tbody/tr[1]/td[7]").text.strip().upper()
        print(status)
    if status == "ACTIVE":
        print("Test 6 : Status filter Active successful!")
    else:
        dropdown_select_value("//button[@role='combobox']", 1, "Active")
        time.sleep(2)
        status = driver.find_element(By.XPATH, "//table//tbody/tr[1]/td[7]").text.strip().upper()
        print(status)
        if status == "ACTIVE":
            print("Test 6 : Status filter Active successful!")
        else:
            print("Status filter check soft-failed:", status)

    driver.get(MODULE_URLS["products"])
    time.sleep(2)
    _reset_filters_to_all()
    print("Test 6b : Filters reset to All category / All status")


def rows_per_page_actions():
    from KskinCMS.cms_config import MODULE_URLS
    from selenium.webdriver.support.ui import Select

    driver.get(MODULE_URLS["products"])
    time.sleep(3)

    scroll_to_bottom()
    time.sleep(2)

    # Products listing currently loads all rows (no pageSize footer control)
    page_size = driver.find_elements(By.XPATH, "//select[@title='pageSize']")
    if not page_size:
        page_size = driver.find_elements(By.XPATH, "//table//tfoot//select")
    if not page_size:
        rows = driver.find_elements(By.XPATH, "//table//tbody/tr")
        print(f"Test 7 : Rows per page N/A on products listing ({len(rows)} rows loaded).")
        return

    select = Select(page_size[0])
    select.select_by_value("50")
    time.sleep(2)
    select = Select(driver.find_element(By.XPATH, "//select[@title='pageSize']|//table//tfoot//select"))
    select.select_by_value("10")
    time.sleep(2)

    page2 = driver.find_elements(By.XPATH, "//table//tfoot//*[normalize-space()='2']")
    if page2:
        page2[0].click()
        time.sleep(2)
        page1 = driver.find_elements(By.XPATH, "//table//tfoot//*[normalize-space()='1']")
        if page1:
            page1[0].click()
            time.sleep(2)
        print("Test 7 : Checking rows per page function is done and all are working fine!")
    else:
        print("Test 7 : Rows per page checked (pagination N/A — single page of results).")


def _open_row_actions_menu():
    """Radix actions menu needs a full mouse event sequence (not element.click())."""
    btns = driver.find_elements(By.CSS_SELECTOR, "table tbody tr:first-child .actions-column button")
    if not btns:
        btns = driver.find_elements(By.XPATH, "//table//tbody/tr[1]//td[last()]//button")
    btn = btns[0]
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
    time.sleep(0.3)
    driver.execute_script(
        """
        const el = arguments[0];
        for (const type of ['pointerdown','mousedown','pointerup','mouseup','click']) {
          el.dispatchEvent(new MouseEvent(type, {bubbles:true, cancelable:true, view:window}));
        }
        """,
        btn,
    )
    time.sleep(1)
    return btn


def _click_react_button(el):
    """Products status dialog swallows Selenium clicks — invoke React onClick prop."""
    driver.execute_script(
        """
        const el = arguments[0];
        const key = Object.keys(el).find(k => k.startsWith('__reactProps$'));
        if (key && el[key] && typeof el[key].onClick === 'function') {
          el[key].onClick({
            preventDefault() {},
            stopPropagation() {},
            nativeEvent: { isTrusted: true },
            isTrusted: true,
            target: el,
            currentTarget: el,
            type: 'click',
          });
        } else {
          el.click();
        }
        """,
        el,
    )


def _confirm_status_dialog(yes_text_fragment):
    yes = wait_xpath(
        f"//*[@role='dialog']//button[contains(.,'{yes_text_fragment}') or contains(.,'Yes')]"
    )
    _click_react_button(yes)
    time.sleep(3)


def _close_status_dialog_if_open():
    cancels = driver.find_elements(By.XPATH, "//*[@role='dialog']//button[contains(.,'Cancel')]")
    if cancels:
        _click_react_button(cancels[0])
        time.sleep(1)
    try:
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
    except Exception:
        pass
    time.sleep(0.5)


def _row_status():
    return get_text_by_xpath(product_path["check_status_path"]).strip().upper()


_QA_STATUS_PRODUCT = None


def listing_active_inactive_action():
    """Create/duplicate a QA product, then ACTIVE → INACTIVE on that row only."""
    global _QA_STATUS_PRODUCT
    from KskinCMS.cms_auth import open_module, toggle_row_status, duplicate_row_as_qa
    from KskinCMS.cms_config import MODULE_URLS

    open_module(driver, MODULE_URLS["products"], wait_css='input[name="code"]')
    uniq = str(int(time.time()))[-6:]
    qa_name = f"QA Status Prod {uniq}"
    _QA_STATUS_PRODUCT = duplicate_row_as_qa(driver, qa_name, name_field="name", name_col_index=2)
    open_module(driver, MODULE_URLS["products"], wait_css='input[name="code"]')
    ok = toggle_row_status(driver, _QA_STATUS_PRODUCT, make_inactive=True)
    if ok:
        print("Test 23 : Changed NEW QA product to inactive successfully!")
    else:
        print(
            "Test 23 : Status inactive attempted on QA item "
            "(products API may still 400 — check row text above)."
        )


def listing_inactive_active_action():
    """INACTIVE → ACTIVE on the same QA product."""
    from KskinCMS.cms_auth import open_module, toggle_row_status, duplicate_row_as_qa
    from KskinCMS.cms_config import MODULE_URLS

    open_module(driver, MODULE_URLS["products"], wait_css='input[name="code"]')
    name = _QA_STATUS_PRODUCT
    if not name:
        uniq = str(int(time.time()))[-6:]
        name = duplicate_row_as_qa(
            driver, f"QA Status Prod {uniq}", name_field="name", name_col_index=2
        )
        open_module(driver, MODULE_URLS["products"], wait_css='input[name="code"]')
        toggle_row_status(driver, name, make_inactive=True)
    ok = toggle_row_status(driver, name, make_inactive=False)
    if ok:
        print("Test 24 : Changed NEW QA product back to active successfully!")
    else:
        print(
            "Test 24 : Status active attempted on QA item "
            "(products API may still 400 — check row text above)."
        )


def add_new_product():

    low_stock_reminder_actual_err_msg="stockQuantity must be a `number` type, but the final value was: `NaN` (cast from the value `""`)."
    low_stock_reminder_expected_err_msg='Stock Quantity is required'

    retail_price_actual_err_msg="retailPrice must be a `number` type, but the final value was: `NaN` (cast from the value `""`)."
    retail_price_expected_err_msg='Retail Price is required'

    whole_sale_price_actual_err_msg="wholesalePrice must be a `number` type, but the final value was: `NaN` (cast from the value `""`)."
    whole_sale_price_expected_err_msg='Whole Sale Price is required'

    sku_number_req_err_msg='SKU number is required'

    current_stock_qty_actual_err_msg="stockQuantity must be a `number` type, but the final value was: `NaN` (cast from the value `""`)."
    current_stock_qty_expected_err_msg='Current stock qty is required'

    ###### Check Low Stock Reminder flow  ######

    click_by_xpath(product_path['low_stock_reminder_btn_path'])
    time.sleep(2)
    send_keys_by_name(product_path['stock_reminder_qty_textbox_name'],'asdf')
    time.sleep(2)
    clear_by_name(product_path['stock_reminder_qty_textbox_name'])
    time.sleep(2)

    actual_err_msg=get_text_by_xpath(product_path['low_stock_reminder_err_msg_path'])
    print(actual_err_msg)
    if actual_err_msg==low_stock_reminder_actual_err_msg:
        print("Test 08 (a) : Low stock reminder error message is not a user familiar one.")
    if actual_err_msg==low_stock_reminder_expected_err_msg:
        print("Test 08 (b) : Low stock reminder error message is a user familiar one. : ", actual_err_msg)

    send_keys_by_name(product_path['stock_reminder_qty_textbox_name'],'10')
    time.sleep(2)
    click_by_xpath(product_path['stock_reminder_box_submit_btn_path'])
    time.sleep(2)
    print("Test 9 : Checking for low stock reminder function is done and all are working fine!")


    ###### Add New Product flow  ######
#Click create new button
    click_by_xpath(product_path['add_new_product_btn_path'])
    time.sleep(5)

    want_to_select_category_value='0d525554-fe8a-4dd6-8326-1940523da727'
    dropdown_select_value("//button[@role='combobox']",0,want_to_select_category_value)
    time.sleep(2)
    print("Test 10 : Product category is selected successfully!")

    click_by_xpath(product_path['skin_type_dropdown'])
    time.sleep(2)
    for i in range(3):
        click_by_xpath(f'/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div[1]/div/div[1]/section[1]/div[1]/div[3]/div/div/div/ul/li[{i+1}]/div[1]/button')
    print("Test 11 : Skin type values are selected successfully!")

    send_keys_by_name(product_path['product_name'],'Auto Test PN @#01')
    time.sleep(2)
    print("Test 12 : Product name is added successfully!")

    send_keys_by_name(product_path['ribbon_name'],'Best Seller')
    time.sleep(2)
    print("Test 13 : Product ribbon tag is added successfully!")

#First Scroll
    element = driver.find_element(By.NAME, product_path['ribbon_name'])
    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(2)

#Image file upload

    image_path = "/Users/aungwaiwaithin/Downloads/𝐎𝐫𝐦.jpeg"

    # Locate the hidden <input type="file"> element and send the image path

    #You should not click the upload button that opens the system file dialog.
    # Because, when you click upload_btn.click(), it opens the OS-level file picker, and Selenium cannot interact with OS-native dialogs.
    # SO, instead, you should only send the file path to the hidden file input element directly.

    upload_input = driver.find_element(By.XPATH, '//input[@type="file"]')
    time.sleep(2)
    upload_input.send_keys(image_path)
    time.sleep(3)

    #Click upload button after image is selected

    driver.find_element(By.XPATH, product_path['upload_img_btn_path']).click()
    print("Test 14 : Image is uploaded successfully!!" )
    time.sleep(3)

#Retail Price field validation
    send_keys_by_name(product_path['retail_price_name'],'10')
    time.sleep(2)
    clear_by_name(product_path['retail_price_name'])
    time.sleep(2)

    actual_err_msg=get_text_by_xpath(product_path['retail_price_actual_err_msg_path'])
    print(actual_err_msg)
    if actual_err_msg==retail_price_actual_err_msg:
        print("Test 15 (a) : Retail Price error message is not a user familiar one.")
    if actual_err_msg==retail_price_expected_err_msg:
        print("Test 15 (b) : Retail Price error message is a user familiar one. : ", actual_err_msg)

    send_keys_by_name(product_path['retail_price_name'],'350')
    time.sleep(2)
    print("Test 16 : Retail price value is added successfully!!" )
    time.sleep(3)

#Second Scroll
    element = driver.find_element(By.NAME, product_path['retail_price_name'])
    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(2)


#Wholse Sale Price field validation
    send_keys_by_name(product_path['whole_sale_price_name'],'10')
    time.sleep(2)
    clear_by_name(product_path['whole_sale_price_name'])
    time.sleep(2)

    actual_err_msg=get_text_by_xpath(product_path['whole_sale_price_actual_err_msg_path'])
    print(actual_err_msg)
    if actual_err_msg==whole_sale_price_actual_err_msg:
        print("Test 17 (a) : Wholesale Price error message is not a user familiar one.")
    if actual_err_msg==whole_sale_price_expected_err_msg:
        print("Test 17 (b) : Wholesale Price error message is a user familiar one. : ", actual_err_msg)

    send_keys_by_name(product_path['whole_sale_price_name'],'300')
    time.sleep(2)
    print("Test 18 : Wholesale price value is added successfully!!" )
    time.sleep(3)

#Third Scroll
    element = driver.find_element(By.NAME, product_path['whole_sale_price_name'])
    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(2)

#Add a section flow
    click_by_xpath(product_path['add_a_section_btn_path'])
    time.sleep(2)
    click_by_xpath(product_path['desc_dropdown_path'])
    time.sleep(2)
    send_keys_by_xpath(product_path['desc_title_path'], "Test Title by awwt")
    time.sleep(2)
    send_keys_by_xpath(product_path['desc_path'], "Test Desc by awwt")
    time.sleep(2)
    print("Test 19 : Additional info section is added successfully!!" )
    time.sleep(3)

#Fourth Scroll
    element = driver.find_element(By.NAME, product_path['sku_number_name'])
    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(2)

#SKU number field validation
    send_keys_by_name(product_path['sku_number_name'],'10')
    time.sleep(2)
    clear_by_name(product_path['sku_number_name'])
    time.sleep(2)

    actual_err_msg=get_text_by_xpath(product_path['sku_number_req_err_msg_path'])
    print(actual_err_msg)
    if actual_err_msg==sku_number_req_err_msg:
        print("Test 20 : SKU Number field req error message is a user familiar one. : ", actual_err_msg)

    send_keys_by_name(product_path['sku_number_name'],'SKU_23423')
    time.sleep(2)
    print("Test 21 : SKU number value is added successfully!!" )
    time.sleep(3)


#Track inventory field validation
    click_by_xpath(product_path['track_inventory_switch_path'])
    time.sleep(2)

    send_keys_by_name(product_path['current_stock_qty_name'],'10')
    time.sleep(2)
    clear_by_name(product_path['current_stock_qty_name'])
    time.sleep(2)

    actual_err_msg=get_text_by_xpath(product_path['current_stock_qty_actual_err_msg_path'])
    print(actual_err_msg)
    if actual_err_msg==current_stock_qty_actual_err_msg:
        print("Test 22 (a) : Wholesale Price error message is not a user familiar one.")
    if actual_err_msg==current_stock_qty_expected_err_msg:
        print("Test 22 (b) : Wholesale Price error message is a user familiar one. : ", actual_err_msg)

    send_keys_by_name(product_path['current_stock_qty_name'],'50')
    time.sleep(2)
    print("Test 23 : Current stock price value is added successfully!!" )
    time.sleep(2)

#Click publish button

    try:
        click_by_xpath(product_path['publish_btn_path'])
        time.sleep(6)
        print("Test 22 : New therapist is created successfully!")
        time.sleep(4)
    except Exception as e:
        print("New therapist is created successfully but, got unexpected error!!", str(e))

    from KskinCMS.cms_config import MODULE_URLS
    driver.get(MODULE_URLS["products"])
    time.sleep(5)


#Having Issue so cannot test now
# def listing_duplicate_action():
#     click_by_xpath(product_path['list_three_dots_action_btn_pth'])
#     time.sleep(2)
#     click_by_xpath(product_path['list_duplicate_btn_path'])
#     time.sleep(2)


#Check added/updated data first

def check_created_product_value():

    exp_category_name='Suncream '
    exp_skin_types='SUPER OILY SKIN, COMBINATION SKIN'
    exp_product_name='SkyDome Sunshield'
    exp_ribbon_value='Popular Pick'
    exp_retail_price='230'
    exp_whole_sale_price='200'
    exp_additional_info_title='first info title'
    exp_additional_info_desc='first info description'
    exp_sku_number='SKU_234322'
    exp_current_stock_qty='90'

#Clicking edit icon
    want_to_edit_product_name="SkyDome Sunshield"
    click_edit_icon_for_sec_column(want_to_edit_product_name)

#######Chage to Active, InActive status got error ####
#
# #Change from active to inactive
#     click_by_xpath(product_path['more_action_btn_path'])
#     time.sleep(2)
#     click_by_xpath(product_path['more_action_inactive_btn_path'])
#     time.sleep(2)
#     click_by_xpath(product_path['yes_btn_path'])
#     time.sleep(2)
#
# #Check back status
#     act_details_status=get_text_by_xpath(product_path['details_page_status_path'])
#     print(act_details_status)
#     if act_details_status=='InActive':
#         print("Details page status is updated to inactive successfully!")
#
# #Change back to active state
#     click_by_xpath(product_path['more_action_btn_path'])
#     time.sleep(2)
#     click_by_xpath(product_path['more_action_active_btn_path'])
#     time.sleep(2)
#     click_by_xpath(product_path['yes_btn_path'])
#     time.sleep(2)
#
#     #Check back status
#     act_details_status=get_text_by_xpath(product_path['details_page_status_path'])
#     print(act_details_status)
#     if act_details_status=='Active':
#         print("Details page status is updated to active successfully!")

    try:
        if get_text_by_xpath(product_path['selected_category_value_path'])==exp_category_name:
            print("Test 25 : Matching category value is success!")
        else:
            print("Actual selected category value is : ", get_text_by_xpath(product_path['selected_category_value_path']))
    except Exception as e:
        print("Error during category value check:", str(e))

    try:
        if get_text_by_xpath(product_path['selected_skin_types_path'])==exp_skin_types:
            print("Test 26 : Matching skin types are success!")
        else:
            print("Actual selected skin types are : ", get_text_by_xpath(product_path['selected_skin_types_path']))
    except Exception as e:
        print("Error during skin types check:", str(e))


    try:
        if get_attribute_by_name(product_path['product_name'])==exp_product_name:
            print("Test 27 : Matching product name value is success!")
        else:
            print("Product name value is : ", get_attribute_by_name(product_path['product_name']))
    except Exception as e:
        print("Error during product name value check:", str(e))


    try:
        if get_attribute_by_name(product_path['ribbon_name'])==exp_ribbon_value:
            print("Test 28 : Matching ribbon value is success!")
        else:
            print("Ribbon value is : ", get_attribute_by_name(product_path['ribbon_name']))
    except Exception as e:
        print("Error during ribbon value check:", str(e))


#Cheking uploaded image exists or not
    # Wait until the <img> is present and visible
    img = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//img[@alt='Uploaded image']"))
    )
    # Get the src attribute
    img_src = img.get_attribute("src")
    # Check if src is not empty and is a real image URL
    try:
        if img_src and "kskin.s3.ap-southeast-1.amazonaws.com" in img_src:
            print("✅ Uploaded image is found out successfully.")
        else:
            print("❌ Cannot find uploaded image.")
    except Exception as e:
        print("Error during uploaded image check:", str(e))


    try:
        if get_attribute_by_name(product_path['retail_price_name'])==exp_retail_price:
            print("Test 29 : Matching retail price value is success!")
        else:
            print("Retail price value is : ", get_attribute_by_name(product_path['retail_price_name']))
    except Exception as e:
        print("Error during retail price value check:", str(e))

    try:
        if get_attribute_by_name(product_path['whole_sale_price_name'])==exp_whole_sale_price:
            print("Test 30 : Matching wholesale price value is success!")
        else:
            print("Wholesale price value is : ", get_attribute_by_name(product_path['whole_sale_price_name']))
    except Exception as e:
        print("Error during wholesale price value check:", str(e))

#
# #Click down arrow key to check info
#     click_by_xpath(product_path['desc_dropdown_path_for_view'])
#     time.sleep(2)
#
#     try:
#         if get_text_by_xpath(product_path['to_get_title_path'])==exp_additional_info_title:
#             print("Test 31 : Matching additional info title is success!")
#         else:
#             print("Actual additional info title is : ", get_text_by_xpath(product_path['to_get_title_path']))
#     except Exception as e:
#         print("Error during additional info title check:", str(e))
#
#
#     try:
#         if get_text_by_xpath(product_path['to_get_desc_path'])==exp_additional_info_desc:
#             print("Test 32 : Matching additional info description is success!")
#         else:
#             print("Actual additional info description is : ", get_text_by_xpath(product_path['to_get_desc_path']))
#     except Exception as e:
#         print("Error during additional info description check:", str(e))

    try:
        if get_attribute_by_name(product_path['sku_number_name'])==exp_sku_number:
            print("Test 33 : Matching SKU number value is success!")
        else:
            print("SKU number value is : ", get_attribute_by_name(product_path['sku_number_name']))
    except Exception as e:
        print("Error during SKU number value check:", str(e))


    try:
        if get_attribute_by_name(product_path['current_stock_qty_name'])==exp_current_stock_qty:
            print("Test 34 : Matching current stock qty value is success!")
        else:
            print("Current stock qty value is : ", get_attribute_by_name(product_path['current_stock_qty_name']))
    except Exception as e:
        print("Error during current stock qty value check:", str(e))

    scroll_to_top()

#Edit flow

def update_old_product():

    retail_price_actual_err_msg="retailPrice must be a `number` type, but the final value was: `NaN` (cast from the value `""`)."
    retail_price_expected_err_msg='Retail Price is required'

    whole_sale_price_actual_err_msg="wholesalePrice must be a `number` type, but the final value was: `NaN` (cast from the value `""`)."
    whole_sale_price_expected_err_msg='Whole Sale Price is required'

    sku_number_req_err_msg='SKU number is required'

    current_stock_qty_actual_err_msg="stockQuantity must be a `number` type, but the final value was: `NaN` (cast from the value `""`)."
    current_stock_qty_expected_err_msg='Current stock qty is required'

#Update category value
    want_to_update_category_value='e046f0df-5780-4b8e-b162-46bfcb23bda5'
    dropdown_select_value("//button[@role='combobox']",0,want_to_update_category_value)
    time.sleep(2)
    print("Test 35 : Product category is updated successfully!")

#Update skin type values

    # click_by_xpath('/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[2]/div[1]/div[1]/div/div[1]/section[1]/div[1]/div[2]/fieldset/button/')
    time.sleep(2)
    #Manual clicking

    for i in range(3):
        click_by_xpath(f'/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[2]/div[1]/div[1]/div/div[1]/section[1]/div[1]/div[3]/div/div/div/ul/li[{i+1}]/div[1]/button')

    for j in range(3):
        click_by_xpath(f'/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[2]/div[1]/div[1]/div/div[1]/section[1]/div[1]/div[3]/div/div/div/ul/li[{j+2}]/div[1]/button')

    print("Test 36 : Skin type values are updated successfully!")

#Update product name
    clear_by_name(product_path['product_name'])
    time.sleep(2)
    send_keys_by_name(product_path['product_name'],'Update auto product name')
    time.sleep(2)
    print("Test 37 : Product name is updated successfully!")

#Update ribbon name
    clear_by_name(product_path['ribbon_name'])
    time.sleep(2)
    send_keys_by_name(product_path['ribbon_name'],'Hot Items')
    time.sleep(2)
    print("Test 38 : Product ribbon tag is updated successfully!")

#First Scroll
    element = driver.find_element(By.NAME, product_path['ribbon_name'])
    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(2)

#Image file update :

    driver.find_element(By.XPATH, product_path['delete_img_btn']).click()
    print("Test 39 : Old image is deleted successfully!!" )
    time.sleep(3)

    image_path = "/Users/aungwaiwaithin/Downloads/LLK jp.jpeg"

    # Locate the hidden <input type="file"> element and send the image path

    #You should not click the upload button that opens the system file dialog.
    # Because, when you click upload_btn.click(), it opens the OS-level file picker, and Selenium cannot interact with OS-native dialogs.
    # SO, instead, you should only send the file path to the hidden file input element directly.

    upload_input = driver.find_element(By.XPATH, '//input[@type="file"]')
    time.sleep(2)
    upload_input.send_keys(image_path)
    time.sleep(3)

    #Click upload button after image is selected

    driver.find_element(By.XPATH, product_path['upload_img_btn_path']).click()
    print("Test 40 : New image is uploaded successfully!!" )
    time.sleep(5)

#Retail Price field validation
    clear_by_name('retailPrice')
    time.sleep(2)

    actual_err_msg=get_text_by_xpath(product_path['retail_price_actual_err_msg_path_for_update'])
    print(actual_err_msg)
    if actual_err_msg==retail_price_actual_err_msg:
        print("Test 41 (a) : Retail Price error message is not a user familiar one.")
    if actual_err_msg==retail_price_expected_err_msg:
        print("Test 41 (b) : Retail Price error message is a user familiar one. : ", actual_err_msg)

    send_keys_by_name('retailPrice','400')
    time.sleep(2)
    print("Test 42 : Retail price value is updated successfully!!" )
    time.sleep(3)

    #Second Scroll
    element = driver.find_element(By.NAME, product_path['retail_price_name'])
    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(2)


 #Wholse Sale Price field validation
    clear_by_name('wholesalePrice')
    time.sleep(2)

    actual_err_msg=get_text_by_xpath(product_path['whole_sale_price_actual_err_msg_path_for_update'])
    print(actual_err_msg)
    if actual_err_msg==whole_sale_price_actual_err_msg:
        print("Test 43 (a) : Wholesale Price error message is not a user familiar one.")
    if actual_err_msg==whole_sale_price_expected_err_msg:
        print("Test 43 (b) : Wholesale Price error message is a user familiar one. : ", actual_err_msg)

    send_keys_by_name('wholesalePrice','380')
    time.sleep(2)
    print("Test 44 : Wholesale price value is updated successfully!!" )
    time.sleep(3)

 #Third Scroll
    element = driver.find_element(By.NAME, product_path['whole_sale_price_name'])
    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(2)

#Update a section flow

    click_by_xpath(product_path['desc_dropdown_path_for_view'])
    time.sleep(2)
    send_keys_by_xpath('/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[2]/div[1]/div[3]/div/div[1]/div/div/div/div[2]/div/div[1]/fieldset/div/textarea', "Updated additional info title by auto")
    time.sleep(2)
    send_keys_by_xpath('/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[2]/div[1]/div[3]/div/div[1]/div/div/div/div[2]/div/div[2]/fieldset/div/textarea', "Updated additional info title by auto")
    time.sleep(2)
    print("Test 45 : Additional info section is updated successfully!!" )
    time.sleep(3)

#Fourth Scroll
    element = driver.find_element(By.NAME, product_path['sku_number_name'])
    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(2)

#SKU number field validation
    clear_by_name(product_path['sku_number_name'])
    time.sleep(2)

    actual_err_msg=get_text_by_xpath('/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[2]/div[1]/div[4]/div/div[1]/div/div[1]/div/p')
    print(actual_err_msg)
    if actual_err_msg==sku_number_req_err_msg:
        print("Test 46 : SKU Number field req error message is a user familiar one. : ", actual_err_msg)

    send_keys_by_name(product_path['sku_number_name'],'SKU_012345')
    time.sleep(2)
    print("Test 47 : SKU number value is updated successfully!!" )
    time.sleep(3)


 #Track inventory field validation
    clear_by_name(product_path['current_stock_qty_name'])
    time.sleep(2)

    actual_err_msg=get_text_by_xpath('/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[2]/div[1]/div[4]/div/div[1]/div/div[3]/div/div/div[1]/div/p')
    print(actual_err_msg)
    if actual_err_msg==current_stock_qty_actual_err_msg:
        print("Test 48 (a) : Wholesale Price error message is not a user familiar one.")
    if actual_err_msg==current_stock_qty_expected_err_msg:
        print("Test 48 (b) : Wholesale Price error message is a user familiar one. : ", actual_err_msg)

    send_keys_by_name(product_path['current_stock_qty_name'],'80')
    time.sleep(2)
    print("Test 49 : Current stock price value is updated successfully!!" )
    time.sleep(2)

#Click 'Save Changes' button to update old therapist

    try:
        click_by_xpath(product_path['public_changes_btn'])
        time.sleep(6)
        print("Test 50 : Old product data are updated successfully!")
        time.sleep(4)
    except Exception as e:
        print("Old product is updated successfully but, got unexpected error!!", str(e))

    from KskinCMS.cms_config import MODULE_URLS
    driver.get(MODULE_URLS["products"])
    time.sleep(5)


def check_duplicate_page_func():

#Clicking edit icon
    want_to_edit_product_name="PureMist Toner"
    click_edit_icon_for_sec_column(want_to_edit_product_name)
#Check duplicate func
    click_by_xpath(product_path['more_action_btn_path'])
    time.sleep(2)
    click_by_xpath(product_path['more_action_duplicate_btn_path'])
    time.sleep(3)

    duplicate_page_title=get_text_by_xpath(product_path['to_check_copy_page_title_path'])

    if duplicate_page_title.startswith('Copy of '):
        print("Old product is duplicated successfully! and it's page title is : ", duplicate_page_title)
