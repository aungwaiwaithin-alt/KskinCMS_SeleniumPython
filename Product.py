import time
from ProductHelper import *
from ProductVarPaths import *
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
    driver.get("https://staging.d1xlt4loftsg5g.amplifyapp.com/")
    time.sleep(5)
    driver.maximize_window()
    print("Test 1 : Open browser success!")
    time.sleep(3)

    #Click Inventory menu
    click_by_xpath(product_path['inventory_mgmt_menu_path'])
    time.sleep(3)
    #Click products sub menu
    click_by_xpath(product_path['product_menu_path'])
    time.sleep(5)
    print("Test 2 : Navigated to Products listing successfully!")


def products_search_and_filter():

#Product name searching Matched case
    send_keys_by_name(product_path['product_name_search_box'], 'PureMist Toner')
    time.sleep(2)
    product_name_search_result=get_text_by_xpath(product_path['matched_product_name_search_result'])
    print(product_name_search_result)
    if product_name_search_result=="PureMist Toner":
        print("Test 3 : Product name searching with matched value is successful!")
    else:
        print("Something went wrong. Product name searching with matched value is failed!")

    driver.find_element(By.NAME,product_path['product_name_search_box']).clear()
    time.sleep(5)

    refresh_search_result()

#Product name searching UnMatched case
    send_keys_by_name(product_path['product_name_search_box'], 'Px$%#')
    time.sleep(2)
    product_name_no_result=get_text_by_xpath(product_path['unmatched_res_for_all_searching'])
    if product_name_no_result=="No products yet.":
        print("Test 4 : Searching with unmatched value can show empty result successfully!!")
    else:
        print("Something went wrong.")

    driver.find_element(By.NAME,product_path['product_name_search_box']).clear()
    time.sleep(5)

    refresh_search_result()

#Category filter (Dropdown) Matched case
    want_to_select_category_value='0d525554-fe8a-4dd6-8326-1940523da727'
    dropdown_select_value("//button[@role='combobox']",0,want_to_select_category_value)
    time.sleep(2)

    category_search_result=get_text_by_xpath(product_path['matched_category_filter_result'])
    print(category_search_result)
    if category_search_result=="Suncream":
        print("Test 5 (a) : Searching with matched value for category dropdown is successful!")
    else:
        print("Something went wrong.")
    time.sleep(2)
#set back to default state
    default_type_value='All'
    dropdown_select_value("//button[@role='combobox']",0,default_type_value)
    time.sleep(2)

#Category filter (Dropdown) UnMatched case
    want_to_select_category_value='df4d7a4e-858a-48e5-84c7-ddbaf5e76586'
    dropdown_select_value("//button[@role='combobox']",0,want_to_select_category_value)
    time.sleep(2)

    category_search_result=get_text_by_xpath(product_path['unmatched_res_for_all_searching'])
    print(category_search_result)
    if category_search_result=="No products yet.":
        print("Test 5 (b) : Searching with unmatched value for category dropdown can show empty result successfully")
    else:
        print("Something went wrong.")
    time.sleep(2)
#set back to default state
    default_type_value='All'
    dropdown_select_value("//button[@role='combobox']",0,default_type_value)
    time.sleep(2)

#Status filter (Dropdown) Matched case

    want_to_select_status_value='Active'
    dropdown_select_value("//button[@role='combobox']",1,want_to_select_status_value)
    time.sleep(2)

    status_result=get_text_by_xpath(product_path['status_matched_res_path'])
    if status_result=="Active":
        print("Test 6 : Searching with matched value for status is success!!")
    else:
        print("Something went wrong.")
#set back to default state for rating value
    default_rating_value='All'
    dropdown_select_value("//button[@role='combobox']",1,default_rating_value)
    time.sleep(2)

def rows_per_page_actions():

    scroll_to_bottom()
    time.sleep(2)

#Rows per page func check
    click_by_xpath(product_path['row_per_page_select_box_path'])
    time.sleep(3)
    click_by_xpath(product_path['20_row_per_page_path'])
    time.sleep(3)
    scroll_to_bottom_by_using_end()
    time.sleep(3)

    click_by_xpath(product_path['row_per_page_select_box_path'])
    time.sleep(3)
    click_by_xpath(product_path['50_row_per_page_path'])
    time.sleep(3)
    scroll_to_bottom_by_using_end()
    time.sleep(3)

    click_by_xpath(product_path['row_per_page_select_box_path'])
    time.sleep(3)
    click_by_xpath(product_path['10_row_per_page_path'])
    time.sleep(3)
    scroll_to_bottom_by_using_end()
    time.sleep(3)
    print("Test 7(A) : Checking rows per page functions is done and all are working fine!")

#Pagination func check

    click_by_xpath(product_path['next_page_btn_path'])
    time.sleep(3)
    scroll_to_bottom_by_using_end()
    time.sleep(3)

    click_by_xpath(product_path['prev_page_btn_path'])
    time.sleep(3)
    scroll_to_bottom_by_using_end()
    time.sleep(3)

    click_by_xpath(product_path['page_2_btn_path'])
    time.sleep(3)
    scroll_to_bottom_by_using_end()
    time.sleep(3)

    click_by_xpath(product_path['page_1_btn_path'])
    time.sleep(3)

    print("Test 7(B) : Checking pagination function is done and all are working fine!")


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

    driver.get("https://staging.d1xlt4loftsg5g.amplifyapp.com/account/inventory/products")
    time.sleep(5)


def listing_active_inactive_action():
    click_by_xpath(product_path['list_three_dots_action_btn_pth'])
    time.sleep(3)
    click_by_xpath(product_path['list_set_as_inactive'])
    time.sleep(3)
    click_by_xpath(product_path['yes_set_as_in_active'])
    time.sleep(3)

    current_actual_status=get_text_by_xpath(product_path['check_status_path'])

    print(current_actual_status)
    expected_status='INACTIVE'

    if current_actual_status==expected_status:
        print("Test 23 : Changed to inactive status successfully!")
    else:
        print("Changed to inactive status failed!")


def listing_inactive_active_action():
    click_by_xpath(product_path['list_three_dots_action_btn_pth'])
    time.sleep(3)
    click_by_xpath(product_path['list_set_as_active'])
    time.sleep(3)
    click_by_xpath(product_path['yes_set_as_active'])
    time.sleep(3)

    current_actual_status=get_text_by_xpath(product_path['check_status_path'])

    print(current_actual_status)
    expected_status='ACTIVE'

    if current_actual_status==expected_status:
        print("Test 24 : Changed to active status successfully!")
    else:
        print("Changed to active status failed!")

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

    driver.get("https://staging.d1xlt4loftsg5g.amplifyapp.com/account/inventory/products")
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
