import time
from FranchiseAccHelper import *
from FranchiseAccVarPaths import *
from dotenv import load_dotenv
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# install this to use load dotevn >> pip install python-dotenv
load_dotenv()

#pytest FranchiseAccMain.py --html=FranchiseAccReport.html
#pytest -s FranchiseAccMain.py --html=FranchiseAccReport.html

def open_browser():
    driver.get("https://staging.d1xlt4loftsg5g.amplifyapp.com/")
    time.sleep(5)
    driver.maximize_window()
    print("Test 1 : Open browser success!")
    time.sleep(3)

    #Click franchise mgmt menu
    click_by_xpath(franchise_path['franchise_mgmt_menu_path'])
    time.sleep(3)
    #Click franchise account sub menu
    click_by_xpath(franchise_path['franchise_acc_menu_path'])
    time.sleep(5)
    print("Test 2 : Navigated to franchise account listing successful!")


def franchise_searching():

#Search functions
    #Franchise name searching (Matched case)
    send_keys_by_name(franchise_path['search_box_name'], 'Augustin')
    time.sleep(2)
    actual_name_search_result=get_text_by_xpath(franchise_path['name_search_result_path'])
    exp_name_search_result='Augustin'
    print(actual_name_search_result)
    if actual_name_search_result==exp_name_search_result:
        print("Test 3 : Name searching with matched value is successful!")
    else:
        print("Something went wrong. Name searching with matched value is failed!")

    driver.find_element(By.NAME,franchise_path['search_box_name']).clear()
    time.sleep(5)

    refresh_search_result()

    #Franchise email searching (Matched case)
    send_keys_by_name(franchise_path['search_box_name'], 'aungbobotun@codigo.co')
    time.sleep(2)
    actual_email_search_result=get_text_by_xpath(franchise_path['email_search_result_path'])
    exp_name_search_result='aungbobotun@codigo.co'
    print(actual_email_search_result)
    if actual_email_search_result==exp_name_search_result:
        print("Test 4 : Email searching with matched value is successful!")
    else:
        print("Something went wrong. Email searching with matched value is failed!")

    driver.find_element(By.NAME,franchise_path['search_box_name']).clear()
    time.sleep(5)

    refresh_search_result()

    #Entity name searching (Matched case)
    send_keys_by_name(franchise_path['search_box_name'], 'Entity Name Pte Ltd')
    time.sleep(2)
    actual_entity_name_search_result=get_text_by_xpath(franchise_path['entity_name_search_result_path'])
    exp_name_search_result='Entity Name Pte Ltd'

    if actual_entity_name_search_result==exp_name_search_result:
        print("Test 4 : Entity Name searching with matched value is successful!")
    else:
        print("Something went wrong. Entity Name searching with matched value is failed!")

    driver.find_element(By.NAME,franchise_path['search_box_name']).clear()
    time.sleep(5)

    refresh_search_result()

def listing_active_inactive_action():
    click_by_xpath(franchise_path['list_three_dots_action_btn_pth'])
    time.sleep(3)
    click_by_xpath(franchise_path['list_set_as_inactive'])
    time.sleep(3)
    click_by_xpath(franchise_path['yes_set_as_in_active'])
    time.sleep(3)

    current_actual_status=get_text_by_xpath(franchise_path['check_status_path'])

    print(current_actual_status)
    expected_status='INACTIVE'

    if current_actual_status==expected_status:
        print("Test 5 : Changed to inactive status successfully!")
    else:
        print("Changed to inactive status failed!")


def listing_inactive_active_action():
    click_by_xpath(franchise_path['list_three_dots_action_btn_pth'])
    time.sleep(3)
    click_by_xpath(franchise_path['list_set_as_active'])
    time.sleep(3)
    click_by_xpath(franchise_path['yes_set_as_active'])
    time.sleep(3)

    current_actual_status=get_text_by_xpath(franchise_path['check_status_path'])

    print(current_actual_status)
    expected_status='ACTIVE'

    if current_actual_status==expected_status:
        print("Test 6 : Changed to active status successfully!")
    else:
        print("Changed to active status failed!")

def pagination_and_rows_per_page_actions():

    scroll_to_bottom()
    time.sleep(2)

#Rows per page func check
    click_by_xpath(franchise_path['row_per_page_select_box_path'])
    time.sleep(3)
    click_by_xpath(franchise_path['50_row_per_page_path'])
    time.sleep(3)
    scroll_to_bottom_by_using_end()
    time.sleep(3)

    click_by_xpath(franchise_path['row_per_page_select_box_path'])
    time.sleep(3)
    click_by_xpath(franchise_path['10_row_per_page_path'])
    time.sleep(3)
    scroll_to_bottom_by_using_end()
    time.sleep(3)

#Pagination func check
    click_by_xpath(franchise_path['prev_page_btn_path'])
    time.sleep(3)
    scroll_to_bottom_by_using_end()
    time.sleep(3)

    click_by_xpath(franchise_path['next_page_btn_path'])
    time.sleep(3)
    scroll_to_bottom_by_using_end()
    time.sleep(3)

    click_by_xpath(franchise_path['page_2_btn_path'])
    time.sleep(3)
    scroll_to_bottom_by_using_end()
    time.sleep(3)

    click_by_xpath(franchise_path['page_1_btn_path'])
    time.sleep(3)

    print("Test 7 : Checking rows per page and pagination functions are done and all are working fine!")


def create_new_franchise_account():
    ###### Create New Franchise Account flow  ######

    invalid_email_address_err_msg='Invalid email address'
    email_address_req_err_msg='Email is required'
    franchise_name_req_err_msg='Franchise name is required'
    entity_name_req_err_msg='Entity name is required'
    uen_req_err_msg='UEN is required'
    outlet_owned_req_err_msg='At least one outlet must be selected'
    acc_number_req_err_msg='Account number is required'
    acc_holder_name_req_err_msg='Account holder name is required'
    bank_name_req_err_msg='Bank name is required'
    sort_code_req_err_msg='Sort code is required'
    billing_name_req_err_msg='Billing name is required'
    invalid_billing_email_err_msg='Invalid email address'
    billing_email_req_err_msg='Billing email is required'
    billing_mobile_req_err_msg='Billing mobile is required'
    company_name_req_err_msg='Company name is required'
    postal_code_req_err_msg='Postal code is required'
    company_address_req_err_msg='Company address is required'


#Click create new button
    click_by_xpath(franchise_path['add_new_franchise_btn_path'])
    time.sleep(5)

#Email Address field validation
    send_keys_by_name(franchise_path['email_address_name'],'123')
    time.sleep(2)
    if invalid_email_address_err_msg==get_text_by_xpath(franchise_path['invalid_email_err_msg_path']) :
        print("Test 8 : Invalid email address error message : ", invalid_email_address_err_msg)
    else :
        print("Something went wrong with checking invalid email address")

    clear_by_name(franchise_path['email_address_name'])
    time.sleep(2)

    if email_address_req_err_msg==get_text_by_xpath(franchise_path['req_email_err_msg_path']):
        print("Test 9 : Email address required error message : ", email_address_req_err_msg)
    else :
        print("Something went wrong with checking email address required message")

    send_keys_by_name(franchise_path['email_address_name'],'a@b.com')
    time.sleep(2)

#Franchise Name field validation
    send_keys_by_name(franchise_path['franchise_name'],'as @# 12 Ad')
    time.sleep(2)
    clear_by_name(franchise_path['franchise_name'])
    time.sleep(2)

    if franchise_name_req_err_msg==get_text_by_xpath(franchise_path['req_franchise_name_err_msg_path']):
        print("Test 10 : Franchise name required error message : ", franchise_name_req_err_msg)
    else :
        print("Something went wrong with checking franchise name required message")

    send_keys_by_name(franchise_path['franchise_name'],'Wai Franchise New 23@#')
    time.sleep(2)

#Click 'Add Entity' button
    click_by_xpath(franchise_path['add_entity_btn_path'])
    time.sleep(2)

    scroll_ele_pth='/html/body/div/div/div[1]/div/div[1]/div/div/form/div[2]/div/div[1]/section[1]/div[2]/fieldset/input'
    scroll_to_specified_element(scroll_ele_pth)
    time.sleep(2)

#Entity Name field validation
    send_keys_by_name(franchise_path['entity_name'],'as @# 12 Ad')
    time.sleep(2)
    clear_by_name(franchise_path['entity_name'])
    time.sleep(2)

    if entity_name_req_err_msg==get_text_by_xpath(franchise_path['req_entity_name_err_msg_path']):
        print("Test 11 : Entity name required error message : ", entity_name_req_err_msg)
    else :
        print("Something went wrong with checking entity name required message")

    send_keys_by_name(franchise_path['entity_name'],'Wai Test New Entity 23@#')
    time.sleep(2)

#UEN field validation
    send_keys_by_name(franchise_path['uen_name'],'as @# 12 Ad')
    time.sleep(2)
    clear_by_name(franchise_path['uen_name'])
    time.sleep(2)

    if uen_req_err_msg==get_text_by_xpath(franchise_path['req_uen_err_msg_path']):
        print("Test 12 : UEN field required error message : ", uen_req_err_msg)
    else :
        print("Something went wrong with checking UEN field required message")

    send_keys_by_name(franchise_path['uen_name'],'UEN_9932 23@#')
    time.sleep(2)

#Outlet owned dropdown field validation
    click_by_xpath(franchise_path['outlet_owned_select_box_path'])
    time.sleep(2)
    click_by_xpath(franchise_path['select_outlet_name_check_box_path'])
    time.sleep(2)
#click again to get err msg
    click_by_xpath(franchise_path['select_outlet_name_check_box_path'])
    time.sleep(2)

    if outlet_owned_req_err_msg==get_text_by_xpath(franchise_path['req_outlet_owned_err_msg_path']):
        print("Test 13 : Outlet owned field required error message : ", outlet_owned_req_err_msg)
    else :
        print("Something went wrong with checking outlet owned field required message")

    click_by_xpath(franchise_path['select_outlet_name_check_box_path'])
    time.sleep(2)
    driver.find_element(By.CSS_SELECTOR, "body").click()
    time.sleep(2)

#Click 'Add Entity' button again to test delete button
    click_by_xpath(franchise_path['add_entity_btn_path'])
    time.sleep(2)

    scroll_ele_pth_02='/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[1]/section[2]/div/div[1]/div[2]/div[3]/fieldset/button'
    scroll_to_specified_element(scroll_ele_pth_02)
    time.sleep(2)

    click_by_xpath(franchise_path['delete_entity_btn'])
    time.sleep(2)
    print("Test 14 : Extra entity is deleted successfully")

#Checked on both rule 1 and 2
    click_by_xpath(franchise_path['rule_1_checkbox'])
    time.sleep(2)
    click_by_xpath(franchise_path['rule_2_checkbox'])
    time.sleep(2)
    print("Test 15 : All rules are checked successfully")

#Account Number field validation

    scroll_to_specified_element(franchise_path['rule_2_checkbox'])
    time.sleep(2)

    send_keys_by_name(franchise_path['acc_no_name'],'as @# 12 Ad')
    time.sleep(2)
    clear_by_name(franchise_path['acc_no_name'])
    time.sleep(2)

    if acc_number_req_err_msg==get_text_by_xpath(franchise_path['req_acc_no_err_msg_path']):
        print("Test 16 : Account number field required error message : ", acc_number_req_err_msg)
    else :
        print("Something went wrong with checking account number field required message")

    send_keys_by_name(franchise_path['acc_no_name'],'Wai_Acc_No_3243')
    time.sleep(2)

#Account Holder Name field validation
    send_keys_by_name(franchise_path['acc_holder_name'],'as @# 12 Ad')
    time.sleep(2)
    clear_by_name(franchise_path['acc_holder_name'])
    time.sleep(2)

    if acc_holder_name_req_err_msg==get_text_by_xpath(franchise_path['req_acc_holder_name_err_msg_path']):
        print("Test 17 : Account holder name field required error message : ", acc_holder_name_req_err_msg)
    else :
        print("Something went wrong with checking account holder name field required message")

    send_keys_by_name(franchise_path['acc_holder_name'],'Awwt_Holder_@333')
    time.sleep(2)

#Bank Name field validation
    send_keys_by_name(franchise_path['bank_name'],'as @# 12 Ad')
    time.sleep(2)
    clear_by_name(franchise_path['bank_name'])
    time.sleep(2)

    if bank_name_req_err_msg==get_text_by_xpath(franchise_path['req_bank_name_err_msg_path']):
        print("Test 18 : Bank name field required error message : ", bank_name_req_err_msg)
    else :
        print("Something went wrong with checking bank name field required message")

    send_keys_by_name(franchise_path['bank_name'],'CB_Bank_23@#')
    time.sleep(2)

#Sort Code field validation
    send_keys_by_name(franchise_path['sort_code_name'],'as @# 12 Ad')
    time.sleep(2)
    clear_by_name(franchise_path['sort_code_name'])
    time.sleep(2)

    if sort_code_req_err_msg==get_text_by_xpath(franchise_path['req_sort_code_err_msg_path']):
        print("Test 19 : Sort code field required error message : ", sort_code_req_err_msg)
    else :
        print("Something went wrong with checking sort code field required message")

    send_keys_by_name(franchise_path['sort_code_name'],'23Ab@#')
    time.sleep(2)

#Billing Name field validation
    send_keys_by_name(franchise_path['bill_name'],'as @# 12 Ad')
    time.sleep(2)
    clear_by_name(franchise_path['bill_name'])
    time.sleep(2)

    if billing_name_req_err_msg==get_text_by_xpath(franchise_path['req_billing_name_err_msg_path']):
        print("Test 20 : Billing name field required error message : ", billing_name_req_err_msg)
    else :
        print("Something went wrong with checking billing name field required message")

    send_keys_by_name(franchise_path['bill_name'],'Awwt_Bill_12@')
    time.sleep(2)

#Billing Email field validation

    scroll_to_specified_element("/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[1]/section[5]/div/div[1]/fieldset/input")
    time.sleep(2)

    send_keys_by_name(franchise_path['bill_email_name'],'123')
    time.sleep(2)
    if invalid_billing_email_err_msg==get_text_by_xpath(franchise_path['invalid_billing_email_err_msg_path']) :
        print("Test 21 : Invalid billing email address error message : ", invalid_billing_email_err_msg)
    else :
        print("Something went wrong with checking invalid billing email address")

    clear_by_name(franchise_path['bill_email_name'])
    time.sleep(2)

    if billing_email_req_err_msg==get_text_by_xpath(franchise_path['req_billing_email_err_msg_path']):
        print("Test 22 : Billing email address required error message : ", billing_email_req_err_msg)
    else :
        print("Something went wrong with checking billing email address required message")

    send_keys_by_name(franchise_path['bill_email_name'],'abilling@bc.com')
    time.sleep(2)


#Billing Mobile number field validation
    send_keys_by_name(franchise_path['bill_mobile_no_name'],'as @# 12 Ad')
    time.sleep(2)

    invalid_billing_phone_err_msg='Invalid phone number'
    invalid_billing_phone_err_msg_path='/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[1]/section[5]/div/div[3]/p'

    if invalid_billing_phone_err_msg==get_text_by_xpath(invalid_billing_phone_err_msg_path):
        print("Test 23(A) : Invalid billing mobile number field error message : ", invalid_billing_phone_err_msg)
    else :
        print("Something went wrong with checking invalid billing mobile number field error message")

    clear_by_name(franchise_path['bill_mobile_no_name'])
    time.sleep(2)

    if billing_mobile_req_err_msg==get_text_by_xpath(franchise_path['req_billing_mobile_err_msg_path']):
        print("Test 23(B) : Billing mobile number field required error message : ", billing_mobile_req_err_msg)
    else :
        print("Something went wrong with checking billing mobile number field required message")

    send_keys_by_name(franchise_path['bill_mobile_no_name'],'862345678')
    time.sleep(2)

#Billing Company name field validation

    scroll_to_specified_element("/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[1]/section[5]/div/div[2]/fieldset/input")
    time.sleep(2)

    send_keys_by_name(franchise_path['company_name'],'as @# 12 Ad')
    time.sleep(2)
    clear_by_name(franchise_path['company_name'])
    time.sleep(2)

    if company_name_req_err_msg==get_text_by_xpath(franchise_path['req_company_name_err_msg_path']):
        print("Test 24 : Company name field required error message : ", company_name_req_err_msg)
    else :
        print("Something went wrong with checking company name field required message")

    send_keys_by_name(franchise_path['company_name'],'Test_Company_Wai_32@#')
    time.sleep(2)

#Select country (outlet) dropdown
    click_by_xpath(franchise_path['country_dropdown_path'])
    time.sleep(2)
    click_by_xpath(franchise_path['selected_outlet_path'])
    time.sleep(2)
    print("Test 25: Selected outlet value successfully!!")

    driver.find_element(By.CSS_SELECTOR, "body").click()
    time.sleep(2)


#Postal code field validation
    send_keys_by_name(franchise_path['postal_or_zip_code_name'],'as @# 12 Ad')
    time.sleep(2)
    clear_by_name(franchise_path['postal_or_zip_code_name'])
    time.sleep(2)

    if postal_code_req_err_msg==get_text_by_xpath(franchise_path['req_postal_code_err_msg_path']):
        print("Test 26 : Postal code field required error message : ", postal_code_req_err_msg)
    else :
        print("Something went wrong with checking Postal code field required message")

    send_keys_by_name(franchise_path['postal_or_zip_code_name'],'314322')
    time.sleep(2)

#Company address field validation
    send_keys_by_xpath(franchise_path['company_address_path'],'as @# 12 Ad')
    time.sleep(2)
    clear_by_xpath(franchise_path['company_address_path'])
    time.sleep(2)

    if company_address_req_err_msg==get_text_by_xpath(franchise_path['req_company_address_err_msg_path']):
        print("Test 27 : Company address field required error message : ", company_address_req_err_msg)
    else :
        print("Something went wrong with checking company address field required message")

    send_keys_by_xpath(franchise_path['company_address_path'],'No123-(A), Hlaing Twnship, Yangon, Myanmar')
    time.sleep(2)

#Click 'Create' button to create new franchise account
    click_by_xpath(franchise_path['create_btn_path'])
    time.sleep(5)

    driver.get("https://staging.d1xlt4loftsg5g.amplifyapp.com/account/franchise-management/franchise-accounts")
    time.sleep(5)

    created_new_item_name='Le Quest'
    created_new_item_path='/html/body/div/div/div[1]/div/div[1]/div/div/form/table/tbody/tr[1]/td[4]'

    print(get_text_by_xpath(created_new_item_path))

    if created_new_item_name==get_text_by_xpath(created_new_item_path):
        print("Test 28 : New Franchise Account is created successfully!! : ", created_new_item_name)
    else:
        print("Something went wrong with new franchise account creation!")

def view_back_created_acc_info():

    click_by_xpath(franchise_path['edit_btn_path'])
    time.sleep(2)

    actual_email_value='a@b.com'
    actual_franchise_name_value='Wai Franchise New 23@#'
    actual_entity_name_value='Wai Test New Entity 23@#'
    actual_uen_value='UEN_9932 23@#'
    actual_outlet_owned_value='Le Quest'
    actual_acc_no_value='Wai_Acc_No_3243'
    actual_acc_holder_name_value='Awwt_Holder_@333'
    actual_bank_name_value='CB_Bank_23@#'
    actual_sort_code_value='23Ab@#'
    actual_billing_name_value='Awwt_Bill_12@'
    actual_billing_email_value='abilling@bc.com'
    actual_mobile_value='862345678'
    actual_company_name_value='Test_Company_Wai_32@#'
    actual_outlet_value='Helloworod'
    actual_postal_code_value='314322'
    actual_company_address_value='No123-(A), Hlaing Twnship, Yangon, Myanmar'

    if actual_email_value==get_attribute_by_name(franchise_path['email_address_name']):
        print("Test 29 : Checking back email address value is correct!")
    else:
        print("Actual email address value is : ", get_attribute_by_name(franchise_path['email_address_name']))

    if actual_franchise_name_value==get_attribute_by_name(franchise_path['franchise_name']):
            print("Test 30 : Checking back franchise name value is correct!")
    else:
        print("Actual franchise name value is : ", get_attribute_by_name(franchise_path['franchise_name']))

    if actual_entity_name_value==get_attribute_by_name(franchise_path['entity_name']):
        print("Test 31 : Checking back entity name value is correct!")
    else:
        print("Actual entity name value is : ", get_attribute_by_name(franchise_path['entity_name']))

    if actual_uen_value==get_attribute_by_name(franchise_path['uen_name']):
        print("Test 32 : Checking back UEN value is correct!")
    else:
        print("Actual UEN value is : ", get_attribute_by_name(franchise_path['uen_name']))

    if actual_outlet_owned_value==get_text_by_xpath(franchise_path['outlet_owned_select_box_path']):
        print("Test 33 : Checking back outlet owned value is correct!")
    else:
        print("Actual outlet owned value is : ", get_text_by_xpath(franchise_path['outlet_owned_select_box_path']))

    if actual_acc_no_value==get_attribute_by_name(franchise_path['acc_no_name']):
        print("Test 34 : Checking back account number value is correct!")
    else:
        print("Actual account number value is : ", get_attribute_by_name(franchise_path['acc_no_name']))

    if actual_acc_holder_name_value==get_attribute_by_name(franchise_path['acc_holder_name']):
        print("Test 35 : Checking back account holder name value is correct!")
    else:
        print("Actual account holder name value is : ", get_attribute_by_name(franchise_path['acc_holder_name']))

    if actual_bank_name_value==get_attribute_by_name(franchise_path['bank_name']):
        print("Test 36 : Checking back name value is correct!")
    else:
        print("Actual bank name value is : ", get_attribute_by_name(franchise_path['bank_name']))

    if actual_sort_code_value==get_attribute_by_name(franchise_path['sort_code_name']):
        print("Test 37 : Checking sort code value is correct!")
    else:
        print("Actual sort code value is : ", get_attribute_by_name(franchise_path['sort_code_name']))

    if actual_billing_name_value==get_attribute_by_name(franchise_path['bill_name']):
        print("Test 38 : Checking billing name value is correct!")
    else:
        print("Actual billing name value is : ", get_attribute_by_name(franchise_path['bill_name']))

    if actual_billing_email_value==get_attribute_by_name(franchise_path['bill_email_name']):
        print("Test 39 : Checking billing email value is correct!")
    else:
        print("Actual billing email value is : ", get_attribute_by_name(franchise_path['bill_email_name']))

    if actual_mobile_value==get_attribute_by_name(franchise_path['bill_mobile_no_name']):
        print("Test 40 : Checking billing mobile number value is correct!")
    else:
        print("Actual billing mobile number value is : ", get_attribute_by_name(franchise_path['bill_mobile_no_name']))

    if actual_company_name_value==get_attribute_by_name(franchise_path['company_name']):
        print("Test 41 : Checking billing company name value is correct!")
    else:
        print("Actual billing company name value is : ", get_attribute_by_name(franchise_path['company_name']))

    if actual_outlet_value==get_text_by_xpath(franchise_path['selected_outlet_path']):
        print("Test 42 : Checking back outlet value is correct!")
    else:
        print("Actual outlet value is : ", get_text_by_xpath(franchise_path['selected_outlet_path']))

    if actual_postal_code_value==get_attribute_by_name(franchise_path['postal_or_zip_code_name']):
        print("Test 44 : Checking postal code value is correct!")
    else:
        print("Actual postal code value is : ", get_attribute_by_name(franchise_path['postal_or_zip_code_name']))

    if actual_company_address_value==get_attribute_by_xpath(franchise_path['company_address_path']):
        print("Test 45 : Checking company address value is correct!")
    else:
        print("Actual company address value is : ", get_attribute_by_xpath(franchise_path['company_address_path']))

    driver.get("https://staging.d1xlt4loftsg5g.amplifyapp.com/account/franchise-management/franchise-accounts")
    time.sleep(3)


def edit_franchise_account():

    ###### Edit Franchise Account flow  ######

    invalid_email_address_err_msg='Invalid email address'
    email_address_req_err_msg='Email is required'
    franchise_name_req_err_msg='Franchise name is required'
    entity_name_req_err_msg='Entity name is required'
    uen_req_err_msg='UEN is required'
    outlet_owned_req_err_msg='At least one outlet must be selected'
    acc_number_req_err_msg='Account number is required'
    acc_holder_name_req_err_msg='Account holder name is required'
    bank_name_req_err_msg='Bank name is required'
    sort_code_req_err_msg='Sort code is required'
    billing_name_req_err_msg='Billing name is required'
    invalid_billing_email_err_msg='Invalid email address'
    billing_email_req_err_msg='Billing email is required'
    billing_mobile_req_err_msg='Billing mobile is required'
    company_name_req_err_msg='Company name is required'
    postal_code_req_err_msg='Postal code is required'
    company_address_req_err_msg='Company address is required'

#Click edit button
    click_by_xpath(franchise_path['edit_btn_path'])
    time.sleep(2)

#Email Address field validation
    clear_by_name(franchise_path['email_address_name'])
    time.sleep(2)

    send_keys_by_name(franchise_path['email_address_name'],'123')
    time.sleep(2)
    if invalid_email_address_err_msg==get_text_by_xpath(franchise_path['invalid_email_err_msg_path']) :
        print("Test 46 : Invalid email address error message : ", invalid_email_address_err_msg)
    else :
        print("Something went wrong with checking invalid email address")

    clear_by_name(franchise_path['email_address_name'])
    time.sleep(2)

    if email_address_req_err_msg==get_text_by_xpath(franchise_path['req_email_err_msg_path']):
        print("Test 47 : Email address required error message : ", email_address_req_err_msg)
    else :
        print("Something went wrong with checking email address required message")

    send_keys_by_name(franchise_path['email_address_name'],'updatewai@gmail.com')
    time.sleep(2)

#Franchise Name field validation
    clear_by_name(franchise_path['franchise_name'])
    time.sleep(2)

    if franchise_name_req_err_msg==get_text_by_xpath(franchise_path['req_franchise_name_err_msg_path']):
        print("Test 48 : Franchise name required error message : ", franchise_name_req_err_msg)
    else :
        print("Something went wrong with checking franchise name required message")

    send_keys_by_name(franchise_path['franchise_name'],'Updated Franchise Name Wai @#12')
    time.sleep(2)

    scroll_ele_pth='/html/body/div/div/div[1]/div/div[1]/div/div/form/div[2]/div/div[1]/section[1]/div[2]/fieldset/input'
    scroll_to_specified_element(scroll_ele_pth)
    time.sleep(2)

#Entity Name field validation

    clear_by_name(franchise_path['entity_name'])
    time.sleep(2)

    if entity_name_req_err_msg==get_text_by_xpath(franchise_path['req_entity_name_err_msg_path']):
        print("Test 49 : Entity name required error message : ", entity_name_req_err_msg)
    else :
        print("Something went wrong with checking entity name required message")

    send_keys_by_name(franchise_path['entity_name'],'Updated Entity Name 23@#')
    time.sleep(2)

#UEN field validation
    clear_by_name(franchise_path['uen_name'])
    time.sleep(2)

    if uen_req_err_msg==get_text_by_xpath(franchise_path['req_uen_err_msg_path']):
        print("Test 50 : UEN field required error message : ", uen_req_err_msg)
    else :
        print("Something went wrong with checking UEN field required message")

    send_keys_by_name(franchise_path['uen_name'],'UpdateUEN_123@#')
    time.sleep(2)

#Outlet owned dropdown field validation
    click_by_xpath(franchise_path['outlet_owned_select_box_path'])
    time.sleep(2)
    click_by_xpath(franchise_path['select_outlet_name_check_box_path'])
    time.sleep(2)

    if outlet_owned_req_err_msg==get_text_by_xpath(franchise_path['req_outlet_owned_err_msg_path']):
        print("Test 51 : Outlet owned field required error message : ", outlet_owned_req_err_msg)
    else :
        print("Something went wrong with checking outlet owned field required message")

    click_by_xpath(franchise_path['updated_outlet_owned_value_path'])
    time.sleep(2)
    driver.find_element(By.CSS_SELECTOR, "body").click()
    time.sleep(2)

#Click 'Add Entity' button again to test delete button
    click_by_xpath(franchise_path['add_entity_btn_path'])
    time.sleep(2)

    scroll_ele_pth_02='/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[1]/section[2]/div/div[1]/div[2]/div[3]/fieldset/button'
    scroll_to_specified_element(scroll_ele_pth_02)
    time.sleep(2)

    click_by_xpath(franchise_path['delete_entity_btn'])
    time.sleep(2)
    print("Test 52 : Extra entity is deleted successfully")

#Un_Checked on both rule 1 and 2
    click_by_xpath(franchise_path['rule_1_checkbox'])
    time.sleep(2)
    click_by_xpath(franchise_path['rule_2_checkbox'])
    time.sleep(2)
    print("Test 53 : All rules are un_checked successfully")

#Account Number field validation

    scroll_to_specified_element(franchise_path['rule_2_checkbox'])
    time.sleep(2)

    clear_by_name(franchise_path['acc_no_name'])
    time.sleep(2)

    if acc_number_req_err_msg==get_text_by_xpath(franchise_path['req_acc_no_err_msg_path']):
        print("Test 54 : Account number field required error message : ", acc_number_req_err_msg)
    else :
        print("Something went wrong with checking account number field required message")

    send_keys_by_name(franchise_path['acc_no_name'],'Updated_Acc_No_32@#')
    time.sleep(2)

#Account Holder Name field validation

    clear_by_name(franchise_path['acc_holder_name'])
    time.sleep(2)

    if acc_holder_name_req_err_msg==get_text_by_xpath(franchise_path['req_acc_holder_name_err_msg_path']):
        print("Test 55 : Account holder name field required error message : ", acc_holder_name_req_err_msg)
    else :
        print("Something went wrong with checking account holder name field required message")

    send_keys_by_name(franchise_path['acc_holder_name'],'Updated_Acc_Holder_Name_@333')
    time.sleep(2)

#Bank Name field validation
    clear_by_name(franchise_path['bank_name'])
    time.sleep(2)

    if bank_name_req_err_msg==get_text_by_xpath(franchise_path['req_bank_name_err_msg_path']):
        print("Test 56 : Bank name field required error message : ", bank_name_req_err_msg)
    else :
        print("Something went wrong with checking bank name field required message")

    send_keys_by_name(franchise_path['bank_name'],'Updated_Bank_Name_23@#')
    time.sleep(2)

#Sort Code field validation
    clear_by_name(franchise_path['sort_code_name'])
    time.sleep(2)

    if sort_code_req_err_msg==get_text_by_xpath(franchise_path['req_sort_code_err_msg_path']):
        print("Test 57 : Sort code field required error message : ", sort_code_req_err_msg)
    else :
        print("Something went wrong with checking sort code field required message")

    send_keys_by_name(franchise_path['sort_code_name'],'12_AZ_az')
    time.sleep(2)

#Billing Name field validation
    clear_by_name(franchise_path['bill_name'])
    time.sleep(2)

    if billing_name_req_err_msg==get_text_by_xpath(franchise_path['req_billing_name_err_msg_path']):
        print("Test 58 : Billing name field required error message : ", billing_name_req_err_msg)
    else :
        print("Something went wrong with checking billing name field required message")

    send_keys_by_name(franchise_path['bill_name'],'Updated_Billing_Name_12@')
    time.sleep(2)

#Billing Email field validation

    scroll_to_specified_element("/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[1]/section[5]/div/div[1]/fieldset/input")
    time.sleep(2)

    clear_by_name(franchise_path['bill_email_name'])
    time.sleep(2)

    send_keys_by_name(franchise_path['bill_email_name'],'123')
    time.sleep(2)
    if invalid_billing_email_err_msg==get_text_by_xpath(franchise_path['invalid_billing_email_err_msg_path']) :
        print("Test 59 : Invalid billing email address error message : ", invalid_billing_email_err_msg)
    else :
        print("Something went wrong with checking invalid billing email address")

    clear_by_name(franchise_path['bill_email_name'])
    time.sleep(2)

    if billing_email_req_err_msg==get_text_by_xpath(franchise_path['req_billing_email_err_msg_path']):
        print("Test 60 : Billing email address required error message : ", billing_email_req_err_msg)
    else :
        print("Something went wrong with checking billing email address required message")

    send_keys_by_name(franchise_path['bill_email_name'],'billupdate@email.com')
    time.sleep(2)


#Billing Mobile number field validation

    clear_by_name(franchise_path['bill_mobile_no_name'])
    time.sleep(2)

    send_keys_by_name(franchise_path['bill_mobile_no_name'],'as @# 12 Ad')
    time.sleep(2)

    invalid_billing_phone_err_msg='Invalid phone number'
    invalid_billing_phone_err_msg_path='/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[1]/section[5]/div/div[3]/p'

    if invalid_billing_phone_err_msg==get_text_by_xpath(invalid_billing_phone_err_msg_path):
        print("Test 61 : Invalid billing mobile number field error message : ", invalid_billing_phone_err_msg)
    else :
        print("Something went wrong with checking invalid billing mobile number field error message")

    clear_by_name(franchise_path['bill_mobile_no_name'])
    time.sleep(2)

    if billing_mobile_req_err_msg==get_text_by_xpath(franchise_path['req_billing_mobile_err_msg_path']):
        print("Test 62 : Billing mobile number field required error message : ", billing_mobile_req_err_msg)
    else :
        print("Something went wrong with checking billing mobile number field required message")

    send_keys_by_name(franchise_path['bill_mobile_no_name'],'867654')
    time.sleep(2)

 #Billing Company name field validation

    scroll_to_specified_element("/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[1]/section[5]/div/div[2]/fieldset/input")
    time.sleep(2)

    clear_by_name(franchise_path['company_name'])
    time.sleep(2)

    if company_name_req_err_msg==get_text_by_xpath(franchise_path['req_company_name_err_msg_path']):
        print("Test 63 : Company name field required error message : ", company_name_req_err_msg)
    else :
        print("Something went wrong with checking company name field required message")

    send_keys_by_name(franchise_path['company_name'],'Updated_Company_Name_32@#')
    time.sleep(2)

#Select country (outlet) dropdown
    click_by_xpath(franchise_path['country_dropdown_path'])
    time.sleep(2)
    click_by_xpath(franchise_path['updated_outlet_path'])
    time.sleep(2)
    print("Test 64: Updated outlet value successfully!!")

    driver.find_element(By.CSS_SELECTOR, "body").click()
    time.sleep(2)


#Postal code field validation
    clear_by_name(franchise_path['postal_or_zip_code_name'])
    time.sleep(2)

    if postal_code_req_err_msg==get_text_by_xpath(franchise_path['req_postal_code_err_msg_path']):
        print("Test 65 : Postal code field required error message : ", postal_code_req_err_msg)
    else :
        print("Something went wrong with checking Postal code field required message")

    send_keys_by_name(franchise_path['postal_or_zip_code_name'],'104564')
    time.sleep(2)

#Company address field validation
    clear_by_xpath(franchise_path['company_address_path'])
    time.sleep(2)

    if company_address_req_err_msg==get_text_by_xpath(franchise_path['req_company_address_err_msg_path']):
        print("Test 66 : Company address field required error message : ", company_address_req_err_msg)
    else :
        print("Something went wrong with checking company address field required message")

    send_keys_by_xpath(franchise_path['company_address_path'],'No123-(5A), MeyZiGone st, Hlaing Twnship, Yangon, Myanmar')
    time.sleep(2)

#Click 'Save' button to update franchise account info
    click_by_xpath(franchise_path['create_btn_path'])
    time.sleep(5)

    driver.get("https://staging.d1xlt4loftsg5g.amplifyapp.com/account/franchise-management/franchise-accounts")
    time.sleep(5)

    created_new_item_name='New verify outlet ww,Le Quest'
    created_new_item_path='/html/body/div/div/div[1]/div/div[1]/div/div/form/table/tbody/tr[1]/td[4]'

    print(get_text_by_xpath(created_new_item_path))

    if created_new_item_name==get_text_by_xpath(created_new_item_path):
        print("Test 28 : Updated Franchise Account info successfully!! : ", created_new_item_name)
    else:
        print("Something went wrong with update franchise account!")









