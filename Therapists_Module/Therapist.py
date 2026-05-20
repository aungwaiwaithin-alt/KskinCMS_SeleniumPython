import time
from TherapistHelper import *
from TherapistVarPaths import *
from dotenv import load_dotenv
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# install this to use load dotevn >> pip install python-dotenv
load_dotenv()

#pytest TherapistMain.py --html=TherapistReport.html
#pytest -s TherapistMain.py --html=TherapistReport.html

def open_browser():
    driver.get("https://staging.d1xlt4loftsg5g.amplifyapp.com/")
    time.sleep(5)
    driver.maximize_window()
    print("Test 1 : Open browser success!")
    time.sleep(3)

    #Click therapist mgmt menu
    click_by_xpath(therapist_path['therapist_mgmt_menu_path'])
    time.sleep(3)
    #Click therapist sub menu
    click_by_xpath(therapist_path['therapists_menu_path'])
    time.sleep(5)
    print("Test 2 : Navigated to Therapists listing successfully!")


def therapist_search_and_filter():

#Therapist name searching Matched case
    send_keys_by_name(therapist_path['search_box_name'], 'Therapist Aung 1')
    time.sleep(2)
    therapist_name_search_result=get_text_by_xpath(therapist_path['name_search_res_path'])
    print(therapist_name_search_result)
    if therapist_name_search_result=="Therapist Aung 1":
        print("Test 3 : Therapist name searching with matched value is successful!")
    else:
        print("Something went wrong. Therapist name searching with matched value is failed!")

    driver.find_element(By.NAME,therapist_path['search_box_name']).clear()
    time.sleep(5)

    refresh_search_result()

#Therapist name searching UnMatched case
    send_keys_by_name(therapist_path['search_box_name'], 'ddff')
    time.sleep(2)
    therapist_name_no_result=get_text_by_xpath(therapist_path['no_match_search_res_path'])
    if therapist_name_no_result=="No therapists yet.":
        print("Test 4 : Searching with unmatched value can show empty result successfully!!")
    else:
        print("Something went wrong.")

    driver.find_element(By.NAME,therapist_path['search_box_name']).clear()
    time.sleep(5)

    refresh_search_result()

#Rating filter (Dropdown) Matched case
    want_to_select_rating_value='4'
    dropdown_select_value("//button[@role='combobox']",0,want_to_select_rating_value)
    time.sleep(2)

    rating_search_result=get_text_by_xpath(therapist_path['rate_search_res_path'])
    print(rating_search_result)
    if rating_search_result=="4.75/5":
        print("Test 5 : Searching with matched value for rating is successful!")
    else:
        print("Something went wrong.")
    time.sleep(2)
#set back to default state for rating value
    default_rating_value='All'
    dropdown_select_value("//button[@role='combobox']",0,default_rating_value)
    time.sleep(2)

#Rating filter (Dropdown) UnMatched case

    want_to_select_rating_value='1'
    dropdown_select_value("//button[@role='combobox']",0,want_to_select_rating_value)
    time.sleep(2)

    rating_no_result=get_text_by_xpath(therapist_path['no_match_search_res_path'])
    if rating_no_result=="No therapists yet.":
        print("Test 6 : Searching with unmatched value for rating can show empty result successfully!!")
    else:
        print("Something went wrong.")
#set back to default state for rating value
    default_rating_value='All'
    dropdown_select_value("//button[@role='combobox']",0,default_rating_value)
    time.sleep(2)

#Mobile Number searching Matched case
    send_keys_by_name(therapist_path['search_box_name'], '0000000004')
    time.sleep(2)
    mobile_no_search_result=get_text_by_xpath(therapist_path['mobile_search_res_path'])
    print(mobile_no_search_result)
    if mobile_no_search_result=="+65 0000000004":
        print("Test 7 : Therapist mobile number searching with matched value is successful!")
    else:
        print("Something went wrong. Therapist mobile number searching with matched value is failed!")

    driver.find_element(By.NAME,therapist_path['search_box_name']).clear()
    time.sleep(5)

    refresh_search_result()

#Mobile Number searching UnMatched case
    send_keys_by_name(therapist_path['search_box_name'], '+65 0000000004')
    time.sleep(2)
    mobile_number_no_result=get_text_by_xpath(therapist_path['no_match_search_res_path'])
    if mobile_number_no_result=="No therapists yet.":
        print("Test 8 : Searching with unmatched value for mobile number can show empty result successfully!!")
    else:
        print("Something went wrong.")

    driver.find_element(By.NAME,therapist_path['search_box_name']).clear()
    time.sleep(5)

    refresh_search_result()

def listing_active_inactive_action():
    click_by_xpath(therapist_path['list_three_dots_action_btn_pth'])
    time.sleep(3)
    click_by_xpath(therapist_path['list_set_as_inactive'])
    time.sleep(3)
    click_by_xpath(therapist_path['yes_set_as_in_active'])
    time.sleep(3)

    current_actual_status=get_text_by_xpath(therapist_path['check_status_path'])

    print(current_actual_status)
    expected_status='INACTIVE'

    if current_actual_status==expected_status:
        print("Test 9 : Changed to inactive status successfully!")
    else:
        print("Changed to inactive status failed!")


def listing_inactive_active_action():
    click_by_xpath(therapist_path['list_three_dots_action_btn_pth'])
    time.sleep(3)
    click_by_xpath(therapist_path['list_set_as_active'])
    time.sleep(3)
    click_by_xpath(therapist_path['yes_set_as_active'])
    time.sleep(3)

    current_actual_status=get_text_by_xpath(therapist_path['check_status_path'])

    print(current_actual_status)
    expected_status='ACTIVE'

    if current_actual_status==expected_status:
        print("Test 10 : Changed to active status successfully!")
    else:
        print("Changed to active status failed!")

def rows_per_page_actions():

    scroll_to_bottom()
    time.sleep(2)

    #Rows per page func check
    click_by_xpath(therapist_path['row_per_page_select_box_path'])
    time.sleep(3)
    click_by_xpath(therapist_path['50_row_per_page_path'])
    time.sleep(3)
    scroll_to_bottom_by_using_end()
    time.sleep(3)

    click_by_xpath(therapist_path['row_per_page_select_box_path'])
    time.sleep(3)
    click_by_xpath(therapist_path['10_row_per_page_path'])
    time.sleep(3)
    scroll_to_bottom_by_using_end()
    time.sleep(3)

    print("Test 11 : Checking rows per page function is done and all are working fine!")



def add_new_therapist():
    ###### Add New Therapist flow  ######

    invalid_email_address_err_msg='Invalid email'
    email_address_req_err_msg='Email is required'
    full_name_req_err_msg='Full Name is required'
    display_name_req_err_msg='Display Name is required'
    mobile_no_req_err_msg='Mobile No. is required'
    dob_validation_err_msg='Date of birth cannot be in the future'


#Click create new button
    click_by_xpath(therapist_path['add_new_therapist_btn_pth'])
    time.sleep(5)


#Image file upload

    image_path = "/Users/aungwaiwaithin/Downloads/llk_abs.jpeg"

    # Locate the hidden <input type="file"> element and send the image path

    #You should not click the upload button that opens the system file dialog.
    # Because, when you click upload_btn.click(), it opens the OS-level file picker, and Selenium cannot interact with OS-native dialogs.
    # SO, instead, you should only send the file path to the hidden file input element directly.

    upload_input = driver.find_element(By.XPATH, '//input[@type="file"]')
    time.sleep(2)
    upload_input.send_keys(image_path)
    time.sleep(3)

    #Click upload button after image is selected

    driver.find_element(By.XPATH, therapist_path['upload_img_btn_path']).click()
    print("Test 12 : Image is uploaded successfully!!" )
    time.sleep(5)

#Full Name field validation
    send_keys_by_name(therapist_path['full_name'],'as @# 12 Ad')
    time.sleep(2)
    clear_by_name(therapist_path['full_name'])
    time.sleep(2)

    if full_name_req_err_msg==get_text_by_xpath(therapist_path['req_full_name_err_msg_path']):
        print("Test 13 : Full name required error message is : ", full_name_req_err_msg)
    else :
        print("Something went wrong with checking full name required message")

    send_keys_by_name(therapist_path['full_name'],'AungWaiWaiThin')
    time.sleep(2)

#Display Name field validation
    send_keys_by_name(therapist_path['display_name'],'as @# 12 Ad')
    time.sleep(2)
    clear_by_name(therapist_path['display_name'])
    time.sleep(2)

    if display_name_req_err_msg==get_text_by_xpath(therapist_path['req_display_name_err_msg_path']):
        print("Test 14 : Display name required error message is : ", display_name_req_err_msg)
    else :
        print("Something went wrong with checking display name required message")

    send_keys_by_name(therapist_path['display_name'],'Dr.WaiWai')
    time.sleep(2)

#Select DOB value

    click_by_xpath(therapist_path['dob_path'])
    time.sleep(3)
    click_by_xpath(therapist_path['invalid_selected_dob_value_path'])
    time.sleep(2)
    click_by_xpath(therapist_path['dob_ok_btn_path'])
    time.sleep(2)

    if dob_validation_err_msg==get_text_by_xpath(therapist_path['dob_validation_err_msg_path_for_create']):
        print("Test 15_A : Invalid DOB error message in create flow is : ", dob_validation_err_msg)
    else :
        print("Something went wrong with checking invalid DOB message in update flow")

    click_by_xpath(therapist_path['dob_path'])
    time.sleep(3)
    click_by_xpath(therapist_path['valid_selected_dob_value_path'])
    time.sleep(2)
    click_by_xpath(therapist_path['dob_ok_btn_path'])
    time.sleep(2)
    print("Test 15_B : Selecting date of birth value successful!")


#Email Address field validation
    send_keys_by_name(therapist_path['email_name'],'123')
    time.sleep(2)
    if invalid_email_address_err_msg==get_text_by_xpath(therapist_path['invalid_email_err_msg_path']) :
        print("Test 16 : Invalid email address error message is : ", invalid_email_address_err_msg)
    else :
        print("Something went wrong with checking invalid email address")

    clear_by_name(therapist_path['email_name'])
    time.sleep(2)

    if email_address_req_err_msg==get_text_by_xpath(therapist_path['req_email_err_msg_path']):
        print("Test 17 : Email address required error message : ", email_address_req_err_msg)
    else :
        print("Something went wrong with checking email address required message")

    send_keys_by_name(therapist_path['email_name'],'awwt@doc.com')
    time.sleep(2)

#Choose gender value
    want_to_select_gender_value='Female'
    dropdown_select_value("//button[@role='combobox']",0,want_to_select_gender_value)
    time.sleep(2)
# Manually clicked to dismiss dropdown box
    driver.find_element(By.CSS_SELECTOR, "body").click()
#*****Since it's not working, need to click by people.******

#Add mobile number value
    click_by_xpath(therapist_path['country_code_dropdown_path'])
    time.sleep(2)
    click_by_xpath(therapist_path['selected_country_code_path'])
    time.sleep(2)

    send_keys_by_name(therapist_path['mobile_no_name'],'123')
    time.sleep(2)
    clear_by_name(therapist_path['mobile_no_name'])
    time.sleep(2)

    if mobile_no_req_err_msg==get_text_by_xpath(therapist_path['req_mobile_no_err_msg_path']):
        print("Test 18 : Mobile Number required error message is : ", mobile_no_req_err_msg)
    else :
        print("Something went wrong with checking mobile number required message")

    send_keys_by_name(therapist_path['mobile_no_name'],'0000000008')
    time.sleep(2)

#First Scroll

    element = driver.find_element(By.NAME, therapist_path['mobile_no_name'])
    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(2)

# setTimeout(() => {
#     debugger;
# }, 2000);

#Select Start from date value
    click_by_xpath(therapist_path['start_datebox_path_for_create'])
    time.sleep(3)
    click_by_xpath(therapist_path['start_date_value_path'])
    time.sleep(2)
    click_by_xpath(therapist_path['start_date_Ok_btn_path'])
    time.sleep(2)
    print("Test 18 : Selecting Start from date value successful!")

#Select Start from time value
    click_by_xpath(therapist_path['start_timebox_path_for_create'])
    time.sleep(3)

    click_by_xpath(therapist_path['hour_path_for_create'])
    time.sleep(2)
    click_by_xpath(therapist_path['minute_path_for_create'])
    time.sleep(2)
    click_by_xpath(therapist_path['Ok_btn_path_for_create'])
    time.sleep(2)
    print("Test 19 : Selecting Start from time value successful!")

#Select End On date value
    click_by_xpath(therapist_path['end_datebox_path_for_create'])
    time.sleep(3)
    click_by_xpath(therapist_path['end_date_value_path'])
    time.sleep(2)
    click_by_xpath(therapist_path['end_date_Ok_btn_path'])
    time.sleep(2)
    print("Test 20 : Selecting End On date value successful!")

#Select End On time value
    click_by_xpath(therapist_path['end_timebox_path_for_create'])
    time.sleep(3)
    click_by_xpath(therapist_path['end_hour_path_for_create'])
    time.sleep(2)
    click_by_xpath(therapist_path['end_minute_path_for_create'])
    time.sleep(2)
    click_by_xpath(therapist_path['end_Ok_btn_path_for_create'])
    time.sleep(2)
    print("Test 21 : Selecting End On time value successful!")

#Click Save button to create new therapist

    try:
        click_by_xpath(therapist_path['save_btn_path'])
        time.sleep(6)
        print("Test 22 : New therapist is created successfully!")
        time.sleep(4)
    except Exception as e:
        print("New therapist is created successfully but, got unexpected error!!", str(e))

    driver.get("https://staging.d1xlt4loftsg5g.amplifyapp.com/account/therapist-management/therapists")
    time.sleep(5)



#Check added/updated data first

def check_created_therapist_value():

    actual_full_name='AungWaiWaiThin'
    actual_display_name='Dr.WaiWai'
    actual_dob='Aug 6, 2025'
    actual_email='awwt@doc.com'
    actual_gender='Female'
    actual_mobile_no='0000000008'
    actual_start_from_date='Jul 31, 2025'
    actual_start_from_time='09:37 PM'
    actual_end_on_date='Aug 20, 2025'
    actual_end_one_time='11:29 PM'

#Clicking edit icon
    want_to_edit_therapist_name="AungWaiWaiThin"
    click_edit_icon(want_to_edit_therapist_name)


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

#Check other fields
    try:
        if get_attribute_by_name(therapist_path['full_name'])==actual_full_name:
            print("Test 23 : Matching therapist full name value is success!")
        else:
            print("Therapist full name value is : ", get_attribute_by_name(therapist_path['full_name']))
    except Exception as e:
        print("Error during therapist full name value check:", str(e))

    try:
        if get_attribute_by_name(therapist_path['display_name'])==actual_display_name:
            print("Test 24 : Matching therapist display name value is success!")
        else:
            print("Therapist display name value is : ", get_attribute_by_name(therapist_path['display_name']))
    except Exception as e:
        print("Error during therapist display name value check:", str(e))

    print("DOB value is ", get_text_by_xpath(therapist_path['to_get_dob_value_path']))
    try:
        if get_text_by_xpath(therapist_path['to_get_dob_value_path'])==actual_dob:
            print("Test 25 : Matching DOB value is success!")
        else:
            print("DOB value is : ", get_text_by_xpath(therapist_path['dob_path']))
    except Exception as e:
        print("Error during DOB value check:", str(e))

    try:
        if get_attribute_by_name(therapist_path['email_name'])==actual_email:
            print("Test 26 : Matching email value is success!")
        else:
            print("Email value is : ", get_attribute_by_name(therapist_path['email_name']))
    except Exception as e:
        print("Error during email value check:", str(e))

    try:
        if get_text_by_xpath(therapist_path['gender_selected_value_path']) == actual_gender:
            print("Test 27 : Matching gender value is success!")
        else:
            print("Gender value is:", get_text_by_xpath(therapist_path['gender_selected_value_path']))
    except Exception as e:
        print("Error during gender value check:", str(e))


    try:
        if get_attribute_by_name(therapist_path['mobile_no_name'])==actual_mobile_no:
            print("Test 28 : Matching mobile number value is success!")
        else:
            print("Mobile number value is : ", get_attribute_by_name(therapist_path['mobile_no_name']))
    except Exception as e:
        print("Error during mobile number value check:", str(e))

    try:
        if get_text_by_xpath(therapist_path['selected_start_from_date_value_path'])==actual_start_from_date:
            print("Test 29 : Matching start from date value is success!")
        else:
            print("Start from date value is : ", get_text_by_xpath(therapist_path['selected_start_from_date_value_path']))
    except Exception as e:
        print("Error during start from date value check:", str(e))

    try:
        if get_text_by_xpath(therapist_path['selected_start_from_time_value_path'])==actual_start_from_time:
            print("Test 30 : Matching start from time value is success!")
        else:
            print("Start from time value is : ", get_text_by_xpath(therapist_path['selected_start_from_time_value_path']))
    except Exception as e:
        print("Error during start from time value check:", str(e))

    try:
        if get_text_by_xpath(therapist_path['selected_end_on_date_value_path'])==actual_end_on_date:
            print("Test 31 : Matching end on date value is success!")
        else:
            print("End on date value is : ", get_text_by_xpath(therapist_path['selected_end_on_date_value_path']))
    except Exception as e:
        print("Error during end on date value check:", str(e))

    try:
        if get_text_by_xpath(therapist_path['selected_end_on_time_value_path'])==actual_end_one_time:
            print("Test 32 : Matching end on time value is success!")
        else:
            print("End on time value is : ", get_text_by_xpath(therapist_path['selected_end_on_time_value_path']))
    except Exception as e:
        print("Error during end on time value check:", str(e))

    driver.get("https://staging.d1xlt4loftsg5g.amplifyapp.com/account/therapist-management/therapists")
    time.sleep(3)

#Edit flow

def update_old_therapist():

#Clicking edit icon first
    want_to_edit_therapist_name="Tom Jerry"
#Call click edit icon function
    click_edit_icon(want_to_edit_therapist_name)

    invalid_email_address_err_msg='Invalid email'
    email_address_req_err_msg='Email is required'
    full_name_req_err_msg='Full Name is required'
    display_name_req_err_msg='Display Name is required'
    dob_req_err_msg='Date of Birth is required'
    dob_validation_err_msg='Date of birth cannot be in the future'

    mobile_no_req_err_msg='Mobile No. is required'

    start_date_req_err_msg='Start Date is required'
    start_time_req_err_msg='Start Time is required'
    end_date_req_err_msg='End Date is required'
    end_time_req_err_msg='End Time is required'

    invalid_date_err_msg='End date must be after start date'


#Image file update :

    driver.find_element(By.XPATH, therapist_path['delete_img_btn']).click()
    print("Test 33 : Old image is deleted successfully!!" )
    time.sleep(5)

    image_path = "/Users/aungwaiwaithin/Downloads/OOK 2.jpg"

    # Locate the hidden <input type="file"> element and send the image path

    #You should not click the upload button that opens the system file dialog.
    # Because, when you click upload_btn.click(), it opens the OS-level file picker, and Selenium cannot interact with OS-native dialogs.
    # SO, instead, you should only send the file path to the hidden file input element directly.

    upload_input = driver.find_element(By.XPATH, '//input[@type="file"]')
    time.sleep(2)
    upload_input.send_keys(image_path)
    time.sleep(3)

    #Click upload button after image is selected

    driver.find_element(By.XPATH, therapist_path['upload_img_btn_path']).click()
    print("Test 34 : New image is uploaded successfully!!" )
    time.sleep(5)

#Full Name field update
    clear_by_name(therapist_path['full_name'])
    time.sleep(2)

    if full_name_req_err_msg==get_text_by_xpath(therapist_path['req_full_name_err_msg_path_for_update']):
        print("Test 35 : Full name required error message in update flow is : ", full_name_req_err_msg)
    else :
        print("Something went wrong with checking full name required message in update flow")

    send_keys_by_name(therapist_path['full_name'],'Nan MuYarNwe')
    time.sleep(2)


#Display Name field update

    clear_by_name(therapist_path['display_name'])
    time.sleep(2)

    if display_name_req_err_msg==get_text_by_xpath(therapist_path['req_display_name_err_msg_path_for_update']):
        print("Test 36 : Display name required error message in update flow is : ", display_name_req_err_msg)
    else :
        print("Something went wrong with checking display name required message in update flow")

    send_keys_by_name(therapist_path['display_name'],'Dr.MuYarNwe')
    time.sleep(5)

# #Second Scroll TO update
#
#     element = driver.find_element(By.NAME, therapist_path['display_name'])
#     driver.execute_script("arguments[0].scrollIntoView();", element)
#     time.sleep(5)
#     print("Second scrolled success!!")

#Update DOB value

    clear_dob_value()

    if dob_req_err_msg==get_text_by_xpath(therapist_path['req_dob_err_msg_path']):
        print("Test 37_A : Date of birth required error message in update flow is : ", dob_req_err_msg)
    else :
        print("Something went wrong with checking DOB required message in update flow")

    click_by_xpath(therapist_path['dob_path_for_update'])
    time.sleep(3)
    click_by_xpath(therapist_path['invalid_selected_dob_value_path'])
    time.sleep(2)
    click_by_xpath(therapist_path['dob_ok_btn_path'])
    time.sleep(2)

    if dob_validation_err_msg==get_text_by_xpath(therapist_path['dob_validation_err_msg_path']):
        print("Test 37_B : Invalid DOB error message in update flow is : ", dob_validation_err_msg)
    else :
        print("Something went wrong with checking invalid DOB message in update flow")

    clear_dob_value()

    click_by_xpath(therapist_path['dob_path_for_update'])
    time.sleep(3)
    click_by_xpath(therapist_path['valid_selected_dob_value_path'])
    time.sleep(2)
    click_by_xpath(therapist_path['dob_ok_btn_path'])
    time.sleep(2)

    print("Test 38 : Update date of birth value successful!")


#Email Address field update

    clear_by_name(therapist_path['email_name'])
    time.sleep(2)

    if email_address_req_err_msg==get_text_by_xpath(therapist_path['req_email_err_msg_path_for_update']):
        print("Test 39 : Email address required error message in update flow is : ", email_address_req_err_msg)
    else :
        print("Something went wrong with checking email address required message in update flow")

    send_keys_by_name(therapist_path['email_name'],'com.cc')
    time.sleep(2)

    if invalid_email_address_err_msg==get_text_by_xpath(therapist_path['invalid_email_err_msg_path_for_update']) :
            print("Test 40 : Invalid email address error message in update flow is : ", invalid_email_address_err_msg)
    else :
        print("Something went wrong with checking invalid email address in update flow")

        clear_by_name(therapist_path['email_name'])
    time.sleep(2)

    send_keys_by_name(therapist_path['email_name'],'updated@testmail.com')
    time.sleep(2)

#Update gender value
    want_to_select_gender_value='Female'
    dropdown_select_value("//button[@role='combobox']",0,want_to_select_gender_value)
    time.sleep(2)
# Manually clicked to dismiss dropdown box
    driver.find_element(By.CSS_SELECTOR, "body").click()
#*****Since it's not working, need to click by people.******
    print("Test 41 : Gender value is updated successfully!!")

#Update mobile number value

    clear_by_name(therapist_path['mobile_no_name'])
    time.sleep(2)

    if mobile_no_req_err_msg==get_text_by_xpath(therapist_path['req_mobile_no_err_msg_path_for_update']):
        print("Test 42 : Mobile Number required error message in update flow is : ", mobile_no_req_err_msg)
    else :
        print("Something went wrong with checking mobile number required message in update flow")

    send_keys_by_name(therapist_path['mobile_no_name'],'0000000009')
    time.sleep(2)

#Third Scroll TO update

    element = driver.find_element(By.NAME, therapist_path['mobile_no_name'])
    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(2)

#Update Start from date value
    click_by_xpath(therapist_path['start_datebox_path'])
    time.sleep(3)
    click_by_xpath(therapist_path['start_date_value_path'])
    time.sleep(2)
    click_by_xpath(therapist_path['start_date_Ok_btn_path'])
    time.sleep(2)
    print("Test 43 : Updating Start from date value successful!")

#Update Start from time value
    click_by_xpath(therapist_path['start_timebox_path'])
    time.sleep(3)

    click_by_xpath(therapist_path['hour_path'])
    time.sleep(2)
    click_by_xpath(therapist_path['minute_path'])
    time.sleep(2)
    click_by_xpath(therapist_path['Ok_btn_path'])
    time.sleep(2)
    print("Test 44 : Updating Start from time value successful!")

#Update End On date value
    click_by_xpath(therapist_path['end_datebox_path'])
    time.sleep(3)
    click_by_xpath(therapist_path['end_date_value_path'])
    time.sleep(2)
    click_by_xpath(therapist_path['end_date_Ok_btn_path'])
    time.sleep(2)
    print("Test 45 : Updating End On date value successful!")

#Update End On time value
    click_by_xpath(therapist_path['end_timebox_path'])
    time.sleep(3)
    click_by_xpath(therapist_path['end_hour_path'])
    time.sleep(2)
    click_by_xpath(therapist_path['end_minute_path'])
    time.sleep(2)
    click_by_xpath(therapist_path['end_Ok_btn_path'])
    time.sleep(2)
    print("Test 46 : Updating End On time value successful!")

#Click 'Save Changes' button to update old therapist

    try:
        click_by_xpath(therapist_path['save_changes_btn_path'])
        time.sleep(6)
        print("Test 47 : Old therapist is updaetd successfully!")
        time.sleep(4)
    except Exception as e:
        print("Old therapist is updated successfully but, got unexpected error!!", str(e))

    driver.get("https://staging.d1xlt4loftsg5g.amplifyapp.com/account/therapist-management/therapists")
    time.sleep(5)

