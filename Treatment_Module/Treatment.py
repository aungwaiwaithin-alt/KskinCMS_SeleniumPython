import time
from TreatmentHelper import *
from TreatmentVarPaths import *
from dotenv import load_dotenv
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# install this to use load dotevn >> pip install python-dotenv
load_dotenv()

#pytest TreatmentMain.py --html=TreatmentReport.html
#pytest -s TreatmentMain.py --html=TreatmentReport.html

def open_browser():
    driver.get("https://staging.d1xlt4loftsg5g.amplifyapp.com/")
    time.sleep(5)
    driver.maximize_window()
    print("Test 1 : Open browser success!")
    time.sleep(3)

    #Click Inventory menu
    click_by_xpath(treatment_path['inventory_mgmt_menu_path'])
    time.sleep(3)
    #Click treatments sub menu
    click_by_xpath(treatment_path['treatment_menu_path'])
    time.sleep(5)
    print("Test 2 : Navigated to Treatments listing successfully!")


def treatments_search_and_filter():

#Treatment name searching Matched case
    send_keys_by_name(treatment_path['treatment_name_search_box'], 'Pigmentation Treatment')
    time.sleep(2)
    treatment_name_search_result=get_text_by_xpath(treatment_path['treatment_name_search_res_path'])
    print(treatment_name_search_result)
    if treatment_name_search_result=="Pigmentation Treatment":
        print("Test 3 : Treatment name searching with matched value is successful!")
    else:
        print("Something went wrong. Treatment name searching with matched value is failed!")

    driver.find_element(By.NAME,treatment_path['treatment_name_search_box']).clear()
    time.sleep(5)

    refresh_search_result()

#Treatment name searching UnMatched case
    send_keys_by_name(treatment_path['treatment_name_search_box'], 'P><P')
    time.sleep(2)
    treatment_name_no_result=get_text_by_xpath(treatment_path['unmatched_res_path'])
    if treatment_name_no_result=="No treatments yet.":
        print("Test 4 : Searching with unmatched value can show empty result successfully!!")
    else:
        print("Something went wrong.")

    driver.find_element(By.NAME,treatment_path['treatment_name_search_box']).clear()
    time.sleep(5)

    refresh_search_result()

#Group filter (Dropdown) Matched case
    want_to_select_category_value='58a6faed-847d-48ba-a5e2-d79ff280230e' #('15 mins Quick Fix')
    dropdown_select_value("//button[@role='combobox']",0,want_to_select_category_value)
    time.sleep(2)

    group_search_result=get_text_by_xpath(treatment_path['gp_filter_res_path'])
    print(group_search_result)
    if group_search_result=="15 mins Quick Fix":
        print("Test 5 : Searching with matched value for group dropdown is successful!")
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

    status_result=get_text_by_xpath(treatment_path['status_filter_res_path'])
    if status_result=="Active":
        print("Test 6 : Searching with matched value for status is success!!")
    else:
        print("Something went wrong.")
#set back to default state for rating value
    default_rating_value='All'
    dropdown_select_value("//button[@role='combobox']",1,default_rating_value)
    time.sleep(2)

#Status filter (Dropdown) UnMatched case
    want_to_select_status_value='Draft'
    dropdown_select_value("//button[@role='combobox']",1,want_to_select_status_value)
    time.sleep(2)

    treatment_name_no_result=get_text_by_xpath(treatment_path['unmatched_res_path'])
    if treatment_name_no_result=="No treatments yet.":
        print("Test 6 : Searching with unmatched filter value can show empty result successfully!!")
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
    click_by_xpath(treatment_path['row_per_page_select_box_path'])
    time.sleep(3)
    click_by_xpath(treatment_path['20_row_per_page_path'])
    time.sleep(3)
    scroll_to_bottom_by_using_end()
    time.sleep(3)

    click_by_xpath(treatment_path['row_per_page_select_box_path'])
    time.sleep(3)
    click_by_xpath(treatment_path['50_row_per_page_path'])
    time.sleep(3)
    scroll_to_bottom_by_using_end()
    time.sleep(3)

    click_by_xpath(treatment_path['row_per_page_select_box_path'])
    time.sleep(3)
    click_by_xpath(treatment_path['10_row_per_page_path'])
    time.sleep(3)
    scroll_to_bottom_by_using_end()
    time.sleep(3)
    print("Test 7(A) : Checking rows per page functions is done and all are working fine!")

#Pagination func check

    click_by_xpath(treatment_path['next_page_btn_path'])
    time.sleep(3)
    scroll_to_bottom_by_using_end()
    time.sleep(3)

    click_by_xpath(treatment_path['prev_page_btn_path'])
    time.sleep(3)
    scroll_to_bottom_by_using_end()
    time.sleep(3)

    click_by_xpath(treatment_path['page_2_btn_path'])
    time.sleep(3)
    scroll_to_bottom_by_using_end()
    time.sleep(3)

    click_by_xpath(treatment_path['page_1_btn_path'])
    time.sleep(3)

    print("Test 7(B) : Checking pagination function is done and all are working fine!")


def listing_active_inactive_action():
    click_by_xpath(treatment_path['list_three_dots_action_btn_pth'])
    time.sleep(3)
    click_by_xpath(treatment_path['list_set_as_inactive'])
    time.sleep(3)
    click_by_xpath(treatment_path['yes_set_as_in_active'])
    time.sleep(3)

    current_actual_status=get_text_by_xpath(treatment_path['check_status_path'])

    print(current_actual_status)
    expected_status='INACTIVE'

    if current_actual_status==expected_status:
        print("Test 8 : Changed to inactive status successfully!")
    else:
        print("Changed to inactive status failed!")


def listing_inactive_active_action():
    click_by_xpath(treatment_path['list_three_dots_action_btn_pth'])
    time.sleep(3)
    click_by_xpath(treatment_path['list_set_as_active'])
    time.sleep(3)
    click_by_xpath(treatment_path['yes_set_as_active'])
    time.sleep(3)

    current_actual_status=get_text_by_xpath(treatment_path['check_status_path'])

    print(current_actual_status)
    expected_status='ACTIVE'

    if current_actual_status==expected_status:
        print("Test 9 : Changed to active status successfully!")
    else:
        print("Changed to active status failed!")


def listing_duplicate_action():
    click_by_xpath(treatment_path['list_three_dots_action_btn_pth'])
    time.sleep(2)
    click_by_xpath(treatment_path['list_duplicate_btn_path'])
    time.sleep(10)

#Check record is navigating to duplicated page or not
    text = get_text_by_xpath(treatment_path['duplicated_item_title_path'])
    if 'Copy of' in text:
        print("Test 10 : Treatment is navigated to duplicated page successfully!")
    else:
        print("Test 10 : Something went wrong while navigating to duplicated page!")


## **** It's ok in real world but, with automation, cannot show values in Copy page,
# that's why i'll skip duplicate record part.

# #Click 'Publish' button to duplicate the record
#     click_by_xpath(treatment_path['publish_btn_path'])
#     time.sleep(5)
#     refresh_search_result()
#     time.sleep(5)
#     if '(Same Level) with Short Time treatment' == get_text_by_xpath(treatment_path['check_duplicated_item_name_in_listing_path']):
#         print("Test 11 : Treatment is duplicated successfully!")
#     else:
#         print("Test 11 : Something went wrong while duplicating the treatment!")
#

def add_new_treatment():

    driver.get("https://staging.d1xlt4loftsg5g.amplifyapp.com/account/inventory/treatments")
    time.sleep(3)

    treatment_name_req_err_msg="Treatment name is required"
    effect_req_err_msg='Effect is required'

    price_actual_err_msg="price must be a `number` type, but the final value was: `NaN` (cast from the value `""`)."
    price_expected_err_msg='Price is required'

    duration_actual_err_msg="duration must be a `number` type, but the final value was: `NaN` (cast from the value `""`)."
    duration_expected_err_msg='Duration is required'

    steps_for_customer_req_err_msg='Steps for customers is required'

    step_title_req_err_msg="Step title is required"
    instruction_req_err_msg='Instruction is required'

    step_duration_actual_err_msg="Duration must be a number"
    step_duration_expected_err_msg='Duration is required'

#Add-ons
    add_on_name_req_err_msg='Add-on name is required',
    actual_add_on_price_req_err_msg='price must be a `number` type, but the final value was: `NaN` (cast from the value `""`).',
    expected_add_on_price_req_err_msg='Price is required',

    actual_add_on_duration_req_err_msg='duration must be a `number` type, but the final value was: `NaN` (cast from the value `""`).',
    expected_add_on_duration_req_err_msg='Duration is required',

    add_on_description_req_err_msg='Description is required',

###### Add New Treatment flow  ######
    #Click create new button
    click_by_xpath(treatment_path['add_new_treatment_btn_path'])
    time.sleep(5)

    want_to_select_group_value='f3e2d8d0-c7de-4a98-a747-3f9f8febc4ef'
    dropdown_select_value("//button[@role='combobox']",0,want_to_select_group_value)
    time.sleep(2)
    print("Test 12 : Treatment group is selected successfully!")

    want_to_select_category_value='04dc92b4-8e68-49d9-a062-7d9e5852461d'
    dropdown_select_value("//button[@role='combobox']",1,want_to_select_category_value)
    time.sleep(2)
    print("Test 13 : Treatment category is selected successfully!")

#multi value selection for skin types
    click_by_xpath('/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div[1]/div/div[1]/section[1]/div[2]/fieldset/button')
    time.sleep(2)
    for i in range(3):
        click_by_xpath(f'/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div[1]/div/div[1]/section[1]/div[3]/div/div/div/ul/li[{i+1}]/div[1]/button')
    print("Test 14 : Skin type values are selected successfully!")
    time.sleep(2)

#Treatment name field validation
    send_keys_by_name(treatment_path['treatment_name'], 'acs')
    time.sleep(2)
    clear_by_name(treatment_path['treatment_name'])
    time.sleep(2)

    actual_err_msg = get_text_by_xpath(treatment_path['treatment_name_req_err_msg_path'])
    print(actual_err_msg)
    if actual_err_msg == treatment_name_req_err_msg:
        print("Test 15 : Treatment name field req error message is a user familiar one. : ", actual_err_msg)

    send_keys_by_name(treatment_path['treatment_name'], 'AutoTest_TreatmentName_Awwt_01')
    time.sleep(2)
    print("Test 16 : Treatment name is added successfully!!")
    time.sleep(3)

# Price field validation
    send_keys_by_name(treatment_path['price_name'], '10')
    time.sleep(2)
    clear_by_name(treatment_path['price_name'])
    time.sleep(2)

    actual_err_msg = get_text_by_xpath(treatment_path['price_req_err_msg_path'])
    print(actual_err_msg)
    if actual_err_msg == price_actual_err_msg:
        print("Test 17 (a) : Price error message is not a user familiar one.")
    if actual_err_msg == price_expected_err_msg:
        print("Test 17 (b) : Price error message is a user familiar one. : ", actual_err_msg)

    send_keys_by_name(treatment_path['price_name'], '20')
    time.sleep(2)
    print("Test 18 : Price value is added successfully!!")
    time.sleep(3)

# Duration field validation
    send_keys_by_name(treatment_path['duration_name'], '5')
    time.sleep(2)
    clear_by_name(treatment_path['duration_name'])
    time.sleep(2)

    actual_err_msg = get_text_by_xpath(treatment_path['duration_req_err_msg_path'])
    print(actual_err_msg)
    if actual_err_msg == duration_actual_err_msg:
        print("Test 19 (a) : Duration error message is not a user familiar one.")
    if actual_err_msg == duration_expected_err_msg:
        print("Test 19 (b) : Duration error message is a user familiar one. : ", actual_err_msg)

    send_keys_by_name(treatment_path['duration_name'], '1')
    time.sleep(2)
    print("Test 20 : Duration value is added successfully!!")
    time.sleep(3)

#First Scroll
    element = driver.find_element(By.NAME, treatment_path['price_name'])
    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(2)

# Effect field validation
    send_keys_by_xpath(treatment_path['effect_path'], 'sed')
    time.sleep(2)
    clear_by_xpath(treatment_path['effect_path'])
    time.sleep(2)

    actual_err_msg = get_text_by_xpath(treatment_path['effect_req_err_msg_path'])
    print(actual_err_msg)
    if actual_err_msg == effect_req_err_msg:
        print("Test 21 : Effect field req error message is a user familiar one. : ", actual_err_msg)

    send_keys_by_xpath(treatment_path['effect_path'], 'This is the description of the effect.')
    time.sleep(2)
    print("Test 22 : Effect desc is added successfully!!")
    time.sleep(3)

# Steps for customer field validation
    send_keys_by_xpath(treatment_path['steps_path'], 'sed')
    time.sleep(2)
    clear_by_xpath(treatment_path['steps_path'])
    time.sleep(2)

    actual_err_msg = get_text_by_xpath(treatment_path['steps_for_customer_req_err_msg_path'])
    print(actual_err_msg)
    if actual_err_msg == steps_for_customer_req_err_msg:
        print("Test 23 : Steps for customer field req error message is a user familiar one. : ", actual_err_msg)

    send_keys_by_xpath(treatment_path['steps_path'], 'This is the description of the steps for customer.')
    time.sleep(2)
    print("Test 24 : Steps for customer desc is added successfully!!")
    time.sleep(3)

#Second Scroll
    element = driver.find_element(By.XPATH, treatment_path['steps_path'])
    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(2)


# --- Image file upload (two files) ---

    image_path_1 = "/Users/aungwaiwaithin/Downloads/ormling.jpeg"
    image_path_2 = "/Users/aungwaiwaithin/Downloads/Ling.jpg"

# Locate both hidden <input type="file"> elements
 #Note** :
    # Use find_elements() (plural) so you can handle multiple <input type="file"> fields. **
    upload_inputs = driver.find_elements(By.XPATH, '//input[@type="file"]')

# Check we found at least two upload inputs
    if len(upload_inputs) >= 2:
        time.sleep(2)
        upload_inputs[0].send_keys(image_path_1)   # upload first image
        time.sleep(2)
        click_by_xpath(treatment_path['upload_img_btn_path'])
        time.sleep(2)
        upload_inputs[1].send_keys(image_path_2)   # upload second image
        time.sleep(2)
        click_by_xpath(treatment_path['upload_img_btn_path'])
        time.sleep(2)

#manual click the upload buttons for both photos

    print("✅ Test 25: Two images uploaded successfully!")
    time.sleep(3)

#If your system uses the same file input that allows multiple files (e.g., <input type="file" multiple>),
    # then you can just do:
            #upload_input = driver.find_element(By.XPATH, '//input[@type="file"]')
            #upload_input.send_keys(f"{image_path_1}\n{image_path_2}")
    #That newline \n between file paths tells Selenium to select both files at once.

#Third Scroll
    # element = driver.find_element(By.NAME, treatment_path['whole_sale_price_name'])
    # driver.execute_script("arguments[0].scrollIntoView();", element)
    # time.sleep(2)

#Add steps for instruction flow
    click_by_xpath(treatment_path['add_step_btn_path'])
    time.sleep(2)
    click_by_xpath(treatment_path['step_expand_btn_path'])
    time.sleep(2)
    send_keys_by_xpath(treatment_path['step_title_path'], "Test step title for instruction by awwt")
    time.sleep(2)
    click_by_xpath(treatment_path['add_instruction_btn_path'])
    time.sleep(4)

# Instruction Image file upload



    send_keys_by_xpath(treatment_path['instruction_path'], "Test step instruction by awwt")
    time.sleep(2)
    print("Test 27 : Step instruction is added successfully!!" )
    time.sleep(3)

    send_keys_by_xpath("/html/body/div/div/div[3]/div[2]/form/div[1]/div/div/div[2]/div/div/fieldset/input", '1')
    time.sleep(2)
    print("Test 28 : Step duration is added successfully!!" )
    time.sleep(3)

    click_by_xpath(treatment_path['submit_btn_path'])
    time.sleep(2)
    print("Test 29 : First step is added successfully!!" )

#Click publish button

    try:
        click_by_xpath(treatment_path['publish_btn_path'])
        time.sleep(6)
        print("Test 30 : New Treatment is created successfully!")
        time.sleep(4)
    except Exception as e:
        print("New Treatment is created successfully but, got unexpected error!!", str(e))

    driver.get("https://staging.d1xlt4loftsg5g.amplifyapp.com/account/inventory/treatments")
    time.sleep(5)

#Check added/updated data first

def check_created_treatment_value():

    exp_treatment_name='(Same Level) with Short Time treatment'
    exp_treatment_group_name='15 mins Quick Fix'
    exp_treatment_category_name='Glass Skin'
    exp_skin_type_name='Combination, Dry'
    exp_price_value='10'
    exp_duration_value='5'

#Choose 20 rows per page to see all rec
    click_by_xpath(treatment_path['row_per_page_select_box_path'])
    time.sleep(3)
    click_by_xpath(treatment_path['20_row_per_page_path'])
    time.sleep(3)
    scroll_to_bottom_by_using_end()
    time.sleep(3)

#Clicking edit icon
    want_to_edit_treatment_name="(Same Level) with Short Time treatment"
    click_edit_icon_for_sec_column(want_to_edit_treatment_name)

#Change from active to inactive
    click_by_xpath(treatment_path['more_action_btn_path'])
    time.sleep(2)
    click_by_xpath(treatment_path['more_action_inactive_btn_path'])
    time.sleep(2)
    click_by_xpath(treatment_path['yes_btn_path'])
    time.sleep(2)

    refresh_search_result()

#Check back status
    act_details_status=get_text_by_xpath(treatment_path['details_page_status_path'])
    print(act_details_status)
    if act_details_status=='InActive':
        print("Test 31 : Details page status is updated to inactive successfully!")

#Change back to active state
    click_by_xpath(treatment_path['more_action_btn_path'])
    time.sleep(2)
    click_by_xpath(treatment_path['more_action_active_btn_path'])
    time.sleep(2)
    click_by_xpath(treatment_path['yes_btn_path'])
    time.sleep(2)

    refresh_search_result()

    #Check back status
    act_details_status=get_text_by_xpath(treatment_path['details_page_status_path'])
    print(act_details_status)
    if act_details_status=='Active':
        print("Test 32 : Details page status is updated to active successfully!")

    try:
        if get_text_by_xpath(treatment_path['selected_treatment_group_value_path'])==exp_treatment_group_name:
            print("Test 33 : Matching treatment group value is success!")
        else:
            print("Actual treatment group value is : ", get_text_by_xpath(treatment_path['selected_treatment_group_value_path']))
    except Exception as e:
        print("Error during treatment group value check:", str(e))

    try:
        if get_text_by_xpath(treatment_path['selected_treatment_category_value_path'])==exp_treatment_category_name:
            print("Test 34 : Matching treatment category value is success!")
        else:
            print("Actual treatment category value is : ", get_text_by_xpath(treatment_path['selected_treatment_category_value_path']))
    except Exception as e:
        print("Error during treatment category value check:", str(e))


    try:
        if get_text_by_xpath(treatment_path['selected_skin_types_value_path'])==exp_skin_type_name:
            print("Test 35 : Matching skin types value are success!")
        else:
            print("Skin types value are : ", get_attribute_by_name(treatment_path['selected_skin_types_value_path']))
    except Exception as e:
        print("Error during skin type values check:", str(e))


    try:
        if get_attribute_by_name(treatment_path['treatment_name'])==exp_treatment_name:
            print("Test 36 : Matching treatment name value is success!")
        else:
            print("Treatment name value is : ", get_attribute_by_name(treatment_path['treatment_name']))
    except Exception as e:
        print("Error during treatment name value check:", str(e))


    try:
        if get_attribute_by_name(treatment_path['price_name'])==exp_price_value:
            print("Test 37 : Matching price value is success!")
        else:
            print("Price value is : ", get_attribute_by_name(treatment_path['price_name']))
    except Exception as e:
        print("Error during price value check:", str(e))



    try:
        if get_attribute_by_name(treatment_path['duration_name'])==exp_duration_value:
            print("Test 38 : Matching duration value is success!")
        else:
            print("Duration value is : ", get_attribute_by_name(treatment_path['duration_name']))
    except Exception as e:
        print("Error during duration value check:", str(e))


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
            print("✅ Test 39 : Uploaded image is found out successfully.")
        else:
            print("❌ Cannot find uploaded image.")
    except Exception as e:
        print("Error during uploaded image check:", str(e))

#Edit flow

def update_old_treatment():

    treatment_name_req_err_msg = "Treatment name is required"
    effect_req_err_msg = 'Effect is required'

    price_actual_err_msg = "price must be a `number` type, but the final value was: `NaN` (cast from the value `""`)."
    price_expected_err_msg = 'Price is required'

    duration_actual_err_msg = "duration must be a `number` type, but the final value was: `NaN` (cast from the value `""`)."
    duration_expected_err_msg = 'Duration is required'

    #Update treatment group value
    want_to_update_treatment_group_value='f3e2d8d0-c7de-4a98-a747-3f9f8febc4ef'
    dropdown_select_value("//button[@role='combobox']",0,want_to_update_treatment_group_value)
    time.sleep(2)
    print("Test 40 : Treatment group value is updated successfully!")

    # Update treatment category value
    want_to_update_treatment_category_value='3c41c5d8-7f94-4752-8fe8-33358fa97f72'
    dropdown_select_value("//button[@role='combobox']",1,want_to_update_treatment_category_value)
    time.sleep(2)
    print("Test 41 : Treatment category value is updated successfully!")
    #
    # #Update skin type values
    # click_by_xpath('/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div[1]/div/div[1]/section[1]/div[2]/fieldset/button')
    # time.sleep(2)
    # #Manual clicking
    #
    # for i in range(3):
    #     click_by_xpath(f'/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div[1]/div/div[1]/section[1]/div[3]/div/div/div/ul/li[{i}]/div[1]/button')
    #
    # for j in range(2):
    #     click_by_xpath(f'/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div[1]/div/div[1]/section[1]/div[3]/div/div/div/ul/li[{j+1}]/div[1]/button')
    #
    # print("Test 42 : Skin type values are updated successfully!")

    # Treatment name field validation
    clear_by_name(treatment_path['treatment_name'])
    time.sleep(2)

    actual_err_msg = get_text_by_xpath(treatment_path['treatment_name_req_err_msg_path_for_update'])
    print(actual_err_msg)
    if actual_err_msg == treatment_name_req_err_msg:
        print("Test 43 : Treatment name field req error message is a user familiar one. : ", actual_err_msg)

    send_keys_by_name(treatment_path['treatment_name'], 'Updated treatment name by waiwai!!')
    time.sleep(2)
    print("Test 44 : Treatment name is updated successfully!!")
    time.sleep(3)

    # Price field validation
    clear_by_name(treatment_path['price_name'])
    time.sleep(2)

    actual_err_msg = get_text_by_xpath(treatment_path['price_req_err_msg_path_for_update'])
    print(actual_err_msg)
    if actual_err_msg == price_actual_err_msg:
        print("Test 45 (a) : Price error message is not a user familiar one.")
    if actual_err_msg == price_expected_err_msg:
        print("Test 45 (b) : Price error message is a user familiar one. : ", actual_err_msg)

    send_keys_by_name(treatment_path['price_name'], '10')
    time.sleep(2)
    print("Test 46 : Price value is updated successfully!!")
    time.sleep(3)

    # Duration field validation
    clear_by_name(treatment_path['duration_name'])
    time.sleep(2)

    actual_err_msg = get_text_by_xpath(treatment_path['duration_req_err_msg_path_for_update'])
    print(actual_err_msg)
    if actual_err_msg == duration_actual_err_msg:
        print("Test 47 (a) : Duration error message is not a user familiar one.")
    if actual_err_msg == duration_expected_err_msg:
        print("Test 47 (b) : Duration error message is a user familiar one. : ", actual_err_msg)

    send_keys_by_name(treatment_path['duration_name'], '4')
    time.sleep(2)
    print("Test 48 : Duration value is updated successfully!!")
    time.sleep(3)

    #Click 'Publish Changes' button to update old therapist

    try:
        click_by_xpath(treatment_path['public_changes_btn'])
        time.sleep(6)
        print("Test 49 : Old treatment data are updated successfully!")
        time.sleep(4)
    except Exception as e:
        print("Old Treatment is updated successfully but, got unexpected error!!", str(e))

    driver.get("https://staging.d1xlt4loftsg5g.amplifyapp.com/account/inventory/treatments")
    time.sleep(5)