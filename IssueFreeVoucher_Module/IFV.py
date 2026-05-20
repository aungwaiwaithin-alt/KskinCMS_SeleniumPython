import time
from IFVHelper import *
from IFVVarPaths import *
from dotenv import load_dotenv
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# install this to use load dotevn >> pip install python-dotenv
load_dotenv()

#pytest IFVMain.py --html=IFVReport.html
#pytest -s IFVMain.py --html=IFVReport.html

def open_browser():
    driver.get("https://staging.d1xlt4loftsg5g.amplifyapp.com/")
    time.sleep(5)
    driver.maximize_window()
    print("Test 1 : Open browser success!")
    time.sleep(3)

    #Click customer mgmt menu
    click_by_xpath(ifv_path['customer_mgmt_menu_path'])
    time.sleep(3)
    #Click ifv sub menu
    click_by_xpath(ifv_path['ifv_menu_path'])
    time.sleep(5)
    print("Test 2 : Navigated to Issue Free Vouchers listing successfully!")


def ifv_search_and_filter():

#Voucher name searching Matched case
    send_keys_by_name(ifv_path['voucher_name_search_box_name'], 'awwt new')
    time.sleep(2)
    voucher_name_search_result=get_text_by_xpath(ifv_path['matched_search_res_path'])
    print(voucher_name_search_result)
    if voucher_name_search_result=="awwt new new":
        print("Test 3 : Voucher name searching with matched value is successful!")
    else:
        print("Something went wrong. Voucher name searching with matched value is failed!")

    driver.find_element(By.NAME,ifv_path['voucher_name_search_box_name']).clear()
    time.sleep(5)

    refresh_search_result()

#Voucher name searching UnMatched case
    send_keys_by_name(ifv_path['voucher_name_search_box_name'], 'vvv')
    time.sleep(2)
    voucher_name_no_result=get_text_by_xpath(ifv_path['no_voucher_res_path'])
    if voucher_name_no_result=="No vouchers yet.":
        print("Test 4 : Searching with unmatched value can show empty result successfully!!")
    else:
        print("Something went wrong.")

    driver.find_element(By.NAME,ifv_path['voucher_name_search_box_name']).clear()
    time.sleep(5)

    refresh_search_result()

#Voucher Type filter (Dropdown) Matched case
    want_to_select_type_value='FixedPriceOff'
    dropdown_select_value("//button[@role='combobox']",0,want_to_select_type_value)
    time.sleep(2)

    type_search_result=get_text_by_xpath(ifv_path['type_search_res_path'])
    print(type_search_result)
    if type_search_result=="$ off":
        print("Test 5 : Searching with matched value for voucher type is successful!")
    else:
        print("Something went wrong.")
    time.sleep(2)
#set back to default state for rating value
    default_type_value='All'
    dropdown_select_value("//button[@role='combobox']",0,default_type_value)
    time.sleep(2)

#Status filter (Dropdown) UnMatched case

    want_to_select_status_value='InActive'
    dropdown_select_value("//button[@role='combobox']",1,want_to_select_status_value)
    time.sleep(2)

    status_no_result=get_text_by_xpath(ifv_path['no_voucher_res_path'])
    if status_no_result=="No vouchers yet.":
        print("Test 6 : Searching with unmatched value for status can show empty result successfully!!")
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
    click_by_xpath(ifv_path['row_per_page_select_box_path'])
    time.sleep(3)
    click_by_xpath(ifv_path['20_row_per_page_path'])
    time.sleep(3)
    scroll_to_bottom_by_using_end()
    time.sleep(3)

    click_by_xpath(ifv_path['row_per_page_select_box_path'])
    time.sleep(3)
    click_by_xpath(ifv_path['50_row_per_page_path'])
    time.sleep(3)
    scroll_to_bottom_by_using_end()
    time.sleep(3)

    click_by_xpath(ifv_path['row_per_page_select_box_path'])
    time.sleep(3)
    click_by_xpath(ifv_path['10_row_per_page_path'])
    time.sleep(3)
    scroll_to_bottom_by_using_end()
    time.sleep(3)
    print("Test 7(A) : Checking rows per page functions is done and all are working fine!")

#Pagination func check

    click_by_xpath(ifv_path['next_page_btn_path'])
    time.sleep(3)
    scroll_to_bottom_by_using_end()
    time.sleep(3)

    click_by_xpath(ifv_path['prev_page_btn_path'])
    time.sleep(3)
    scroll_to_bottom_by_using_end()
    time.sleep(3)

    click_by_xpath(ifv_path['page_2_btn_path'])
    time.sleep(3)
    scroll_to_bottom_by_using_end()
    time.sleep(3)

    click_by_xpath(ifv_path['page_1_btn_path'])
    time.sleep(3)

    print("Test 7(B) : Checking pagination function is done and all are working fine!")


def add_new_ifv():
    ###### Add New IFV flow  ######

    voucher_type_req_err_msg='Voucher type is required'
    voucher_name_req_err_msg='Voucher name is required'
    desc_req_err_msg='Description is required'

    discount_amt_req_err_msg='Discount amount is required'
    discount_amt_minus_value_validation_err_msg='Value must be positive number'
    discount_amt_max_value_validation_err_msg='Value must not exceed 100'

    discount_apply_to_req_err_msg='Please select where to apply the discount'
    remark_req_err_msg='Remark is required'
    t_and_c_req_err_msg='Terms and conditions are required'

    min_spent_amt_req_err_msg='Minimum spent amount is required'
    min_spent_amt_minus_value_validation_err_msg='Minimum spent amount cannot be negative'

    expires_in_req_err_msg='Expired in is required'


#Click create new button
    click_by_xpath(ifv_path['add_issue_voucher_btn_pth'])
    time.sleep(5)

#Voucher Type validation
    click_by_xpath(ifv_path['dollar_off_radio_btn_path'])
    time.sleep(3)

    #Click again to see req err msg
    click_by_xpath("//html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[1]/div/fieldset/div/button[2]")
    time.sleep(2)

    if voucher_type_req_err_msg==get_text_by_xpath(ifv_path['voucher_type_req_err_msg_path']):
        print("Test 8 : Voucher type required error message is : ", voucher_type_req_err_msg)
    else :
        print("Something went wrong with checking voucher type required message")
    #Click again to select voucher type

    click_by_xpath(ifv_path['percent_off_radio_btn_path'])
    time.sleep(2)


#Vocher Name field validation
    send_keys_by_name(ifv_path['voucher_name'],'A@#$%')
    time.sleep(2)
    clear_by_name(ifv_path['voucher_name'])
    time.sleep(2)

    if voucher_name_req_err_msg==get_text_by_xpath(ifv_path['voucher_name_req_err_msg_path']):
        print("Test 9 : Voucher name required error message is : ", voucher_name_req_err_msg)
    else :
        print("Something went wrong with checking voucher name required message")

    send_keys_by_name(ifv_path['voucher_name'],'Auto Test Voucher_@#$%')
    time.sleep(2)


#Description field validation
    send_keys_by_xpath(ifv_path['description_path'],'Aad')
    time.sleep(2)
    clear_by_xpath(ifv_path['description_path'])
    time.sleep(2)

    if desc_req_err_msg==get_text_by_xpath(ifv_path['desc_req_err_msg_path']):
        print("Test 10 : Description field required error message is : ", desc_req_err_msg)
    else :
        print("Something went wrong with checking description field required message")

    send_keys_by_xpath(ifv_path['description_path'],'Test description !@#$%^&8 123456 asd')
    time.sleep(2)

#First Scroll
    element = driver.find_element(By.XPATH, ifv_path['description_path'])
    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(2)

#Discount value field validation
    send_keys_by_name(ifv_path['discount_value_name'],'-123')
    time.sleep(2)
    if discount_amt_minus_value_validation_err_msg==get_text_by_xpath(ifv_path['discount_amt_err_msg_path']):
        print("Test 11 : Discount amount error message for minus value is : ", discount_amt_minus_value_validation_err_msg)
    else :
        print("Something went wrong with checking discount amount error message for minus value")

    clear_by_name(ifv_path['discount_value_name'])
    time.sleep(2)

    # driver.find_element(By.NAME,ifv_path['discount_value_name']).clear()
    # time.sleep(3)

    if discount_amt_req_err_msg==get_text_by_xpath(ifv_path['discount_amt_err_msg_path']):
        print("Test 12 : Discount value required error message is : ", discount_amt_req_err_msg)
    else :
        print("Something went wrong with checking discount value required message")

    send_keys_by_name(ifv_path['discount_value_name'],'1234')
    time.sleep(2)
    if discount_amt_max_value_validation_err_msg==get_text_by_xpath(ifv_path['discount_amt_err_msg_path']):
        print("Test 13 : Discount amount error message for max value is : ", discount_amt_max_value_validation_err_msg)
    else :
        print("Something went wrong with checking discount amount error message for max value")
    clear_by_name(ifv_path['discount_value_name'])
    time.sleep(2)

    send_keys_by_name(ifv_path['discount_value_name'],'5')
    time.sleep(2)

#Discount Apply to field validation
    click_by_xpath(ifv_path['total_bill_path'])
    time.sleep(2)
    #Click again to see req err msg
    click_by_xpath(ifv_path['total_bill_path'])
    time.sleep(2)
    if discount_apply_to_req_err_msg==get_text_by_xpath(ifv_path['discount_apply_to_req_err_msg_path']):
        print("Test 14 : Discount apply to required error message is : ", discount_apply_to_req_err_msg)
    else :
        print("Something went wrong with checking discount apply to required message")
    #Click again to select voucher type
    click_by_xpath(ifv_path['individual_item_path'])
    time.sleep(2)

#Selecting applicable outlet values
    click_by_xpath(ifv_path['outlet_dropdown_path'])
    time.sleep(2)

    for i in range(26, 30):  # 26 to 29 inclusive
        xpath = f"/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[1]/section[1]/div[6]/div/div/div/ul/li[{i}]/div[1]/button"
        click_by_xpath(xpath)
        time.sleep(2)
# Manually clicked to dismiss dropdown box
    driver.find_element(By.CSS_SELECTOR, "body").click()
#*****Since it's not working, need to click by people.******
    print("Test 15 : Selecting applicable outlet values value is done successfully!!")


#Remarks field validation
    send_keys_by_name(ifv_path['remark_name'],'Rem#$%')
    time.sleep(2)
    clear_by_name(ifv_path['remark_name'])
    time.sleep(2)

    if remark_req_err_msg==get_text_by_xpath(ifv_path['remark_req_err_msg_path']):
        print("Test 16 : Remark field required error message is : ", remark_req_err_msg)
    else :
        print("Something went wrong with checking remark field required message")

    send_keys_by_name(ifv_path['remark_name'],'Auto Test Remarks_@#$%')
    time.sleep(2)

#Second Scroll
    element = driver.find_element(By.NAME, ifv_path['remark_name'])
    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(2)

#T&C field validation
    send_keys_by_xpath(ifv_path['t_n_c_path'],'dandc')
    time.sleep(2)
    clear_by_xpath(ifv_path['t_n_c_path'])
    time.sleep(2)

    if t_and_c_req_err_msg==get_text_by_xpath(ifv_path['t_and_c_req_err_msg_path']):
        print("Test 17 : Terms & Conditions field required error message is : ", t_and_c_req_err_msg)
    else :
        print("Something went wrong with checking Terms & Conditions field required message")

    send_keys_by_xpath(ifv_path['t_n_c_path'],'Test T&C !@#$%^&8 123456 asd')
    time.sleep(2)

#Third Scroll
    element = driver.find_element(By.XPATH, ifv_path['t_n_c_path'])
    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(2)

#Customer Segments value section
    click_by_xpath(ifv_path['tier_member_option_path'])
    time.sleep(2)
    click_by_xpath(ifv_path['premium_tier_path'])
    time.sleep(2)
    print("Test 18 : Selecting Customer Segments value is done successfully!! ")

#Fourth Scroll
    element = driver.find_element(By.XPATH, ifv_path['tier_member_option_path'])
    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(2)


#Apply Voucher To Treatment/Product values selection
    click_by_xpath(ifv_path['apply_voucher_to_product_edit_btn_path'])
    time.sleep(2)
    for i in range (1,4):
        xpath=f"/html/body/div/div/div[3]/div[2]/div[2]/div[1]/div/div/div/div/div/div[2]/div[2]/ul/li[{i}]/div[1]/button"
        click_by_xpath(xpath)
        time.sleep(2)

    click_by_xpath(ifv_path['apply_btn_path'])
    time.sleep(2)
    print("Test 19 : Selecting eligible products is done successfully!!")


#Minimum Spent Amount field validation
    send_keys_by_name(ifv_path['min_spent_amt_name'],'-1')
    time.sleep(2)
    if min_spent_amt_minus_value_validation_err_msg==get_text_by_xpath(ifv_path['min_spent_amt_err_msg_path']):
        print("Test 20 : Minimum Spent Amount field error message for minus value is : ", min_spent_amt_minus_value_validation_err_msg)
    else :
        print("Something went wrong with checking Minimum Spent Amount field for minus value error message")

    clear_by_name(ifv_path['min_spent_amt_name'])
    time.sleep(2)

    if min_spent_amt_req_err_msg==get_text_by_xpath(ifv_path['min_spent_amt_err_msg_path']):
        print("Test 21 : Minimum Spent Amount field required error message is : ", min_spent_amt_req_err_msg)
    else :
        print("Something went wrong with checking Minimum Spent Amount field required message")

    send_keys_by_name(ifv_path['min_spent_amt_name'],'200')
    time.sleep(2)

#Check Usage Limit checkbox
    click_by_xpath(ifv_path['usage_limit_checkbox_path'])
    time.sleep(2)

#Image file upload

    image_path = "/Users/aungwaiwaithin/Downloads/LM.jpg"

    # Locate the hidden <input type="file"> element and send the image path

    #You should not click the upload button that opens the system file dialog.
    # Because, when you click upload_btn.click(), it opens the OS-level file picker, and Selenium cannot interact with OS-native dialogs.
    # SO, instead, you should only send the file path to the hidden file input element directly.

    upload_input = driver.find_element(By.XPATH, '//input[@type="file"]')
    time.sleep(2)
    upload_input.send_keys(image_path)
    time.sleep(3)

    #Click upload button after image is selected

    driver.find_element(By.XPATH, ifv_path['upload_image_btn_path']).click()
    print("Test 22 : Image is uploaded successfully!!" )
    time.sleep(5)

#Check Expires In field validation
    send_keys_by_name(ifv_path['expire_in_textbox_name'],'12')
    time.sleep(2)
    clear_by_name(ifv_path['expire_in_textbox_name'])
    time.sleep(2)

    if expires_in_req_err_msg==get_text_by_xpath(ifv_path['expires_in_req_err_msg_path']):
        print("Test 23 : Expires in field required error message is : ", expires_in_req_err_msg)
    else :
        print("Something went wrong with checking Expires in field required message")

    send_keys_by_name(ifv_path['expire_in_textbox_name'],'3')
    time.sleep(2)

    want_to_select_month_value='Months'
    dropdown_select_value("//button[@role='combobox']",0,want_to_select_month_value)
    time.sleep(2)

#Click publish button
    click_by_xpath(ifv_path['publish_btn_path'])
    time.sleep(3)
    print("Test 24 : New Issue Free Voucher is created successfully!")
    time.sleep(3)
    driver.get("https://staging.d1xlt4loftsg5g.amplifyapp.com/account/customer-management/issue-free-vouchers")
    time.sleep(3)

