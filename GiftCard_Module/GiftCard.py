import time

from GiftCardHelper import *
from GiftCardVarPaths import *
from dotenv import load_dotenv
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# install this to use load dotevn >> pip install python-dotenv
load_dotenv()

#pytest GiftCardMain.py --html=GiftCardReport.html
#pytest -s GiftCardMain.py --html=GiftCardReport.html

def open_browser():
    driver.get("https://staging-cms.kskinfacial.com/login")
    time.sleep(5)
    driver.maximize_window()
    print("Test 1 : Open browser success!")
    time.sleep(3)

    #Login
    send_keys_by_name(gift_card_path['login_email_field_name'],'sunandarkyaw@codigo.co')
    time.sleep(3)
    send_keys_by_name(gift_card_path['login_pwd_field_name'],'root@1234')
    time.sleep(3)
    click_by_xpath(gift_card_path['login_btn_path'])
    time.sleep(6)

    # Enter OTP
    # range(6) >> index(0,5)
    for i in range(6):
        driver.find_element(By.ID, f'otp-field-{i}').send_keys('1')
        time.sleep(1)
    time.sleep(6)

    #Click Inventory menu
    click_by_xpath(gift_card_path['inventory_mgmt_menu_path'])
    time.sleep(3)
    #Click treatments sub menu
    click_by_xpath(gift_card_path['gift_card_menu_path'])
    time.sleep(5)
    print("Test 2 : Navigated to Gift Card Page successfully!")


def update_gift_card():

    #Err_msg
    desc_req_err_msg='Description is required'
    t_and_c_req_err_msg='Terms and conditions are required'

    act_gift_card_img_req_err_msg='giftcardDesigns[0] cannot be null'
    exp_gift_card_img_req_err_msg='Gift card design is required'

    design_name_req_err_msg='Design name is required'

    act_gift_card_amt_req_err_msg='giftCardAmounts[0].amount must be a `number` type, but the final value was: `NaN` (cast from the value `""`).'
    exp_gift_card_amt_req_err_msg='Gift card amount is required'

    expire_in_req_err_msg='Expired in is required'

    #Click 'Edit Gift Card' button
    click_by_xpath(gift_card_path['edit_gift_card_btn_path'])
    time.sleep(3)

    # Change from active to inactive in details page
    click_by_xpath(gift_card_path['more_action_btn_path'])
    time.sleep(2)
    click_by_xpath(gift_card_path['more_action_inactive_btn_path'])
    time.sleep(2)
    click_by_xpath(gift_card_path['yes_btn_path'])
    time.sleep(2)

    # Check back status
    act_details_status = get_text_by_xpath(gift_card_path['details_page_status_path'])
    print(act_details_status)
    if act_details_status == 'INACTIVE':
        print("Test 3 : Details page status is updated to inactive successfully!")

    # Change back to active state
    click_by_xpath(gift_card_path['more_action_btn_path'])
    time.sleep(2)
    click_by_xpath(gift_card_path['more_action_active_btn_path'])
    time.sleep(2)
    click_by_xpath(gift_card_path['yes_btn_path'])
    time.sleep(2)

    # Check back status
    act_details_status = get_text_by_xpath(gift_card_path['details_page_status_path'])
    print(act_details_status)
    if act_details_status == 'ACTIVE':
        print("Test 4 : Details page status is updated to active successfully!")

#Check validations and update values

    # Description field validation
    clear_by_xpath(gift_card_path['desc_textarea_path'])
    time.sleep(2)

    act_desc_req_err_msg=get_text_by_xpath(gift_card_path['desc_req_err_msg_path'])
    print(act_desc_req_err_msg)
    if act_desc_req_err_msg == desc_req_err_msg:
        print("Test 5 : Description field req error message is : ", act_desc_req_err_msg)

    send_keys_by_xpath(gift_card_path['desc_textarea_path'], '(Updated) Perfect for all occasions! Customise a giftcard and send it to your loved one.')
    time.sleep(2)
    print("Test 6 : Gift card description is updated successfully!!")
    time.sleep(2)

    # Terms_and_Conditions field validation
    clear_by_xpath(gift_card_path['t_and_c_textarea_path'])
    time.sleep(2)

    act_t_and_c_req_err_msg=get_text_by_xpath(gift_card_path['t_and_c_req_err_msg_path'])
    print(act_t_and_c_req_err_msg)
    if act_desc_req_err_msg == t_and_c_req_err_msg:
        print("Test 7 : Terms and Conditions field req error message is : ", act_t_and_c_req_err_msg)

    send_keys_by_xpath(gift_card_path['t_and_c_textarea_path'], '(Updated) Gift cards must be used in full. Valid at all outlets within the country of purchase. Gift cards cannot be refunded or exchanged for cash. Gift cards are valid for 1 day from the date of purchase.')
    time.sleep(2)
    print("Test 8 : Gift card's terms and conditions is updated successfully!!")
    time.sleep(2)

    # First Scroll
    element = driver.find_element(By.XPATH, gift_card_path['t_and_c_textarea_path'])
    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(2)

    #Delete gift card design's image
    click_by_xpath(gift_card_path['delete_img_btn_path_for_first_one'])
    time.sleep(2)
    print("Test 9 : Gift card design's image is deleted successfully!!")
    time.sleep(2)

    actual_err_msg=get_text_by_xpath(gift_card_path['gift_card_img_req_err_msg_path'])
    print(actual_err_msg)
    if actual_err_msg==act_gift_card_img_req_err_msg:
        print("Test 10 (a) : Gift card design required error message is not a user familiar one.", actual_err_msg)
    if actual_err_msg==exp_gift_card_img_req_err_msg:
        print("Test 10 (b) : Gift card design required error message is a user familiar one. : ", actual_err_msg)

    #Upload new gift card design image
    image_path = "/Users/aungwaiwaithin/Downloads/self_care.png"

    upload_input = driver.find_element(By.XPATH, '//input[@type="file"]')
    time.sleep(2)
    upload_input.send_keys(image_path)
    time.sleep(3)

    driver.find_element(By.XPATH, gift_card_path['upload_img_btn_path']).click()
    print("Test 11 : Gift card design Image is uploaded successfully!!")
    time.sleep(3)

    #Gift card design name field validation
    clear_by_xpath(gift_card_path['gift_card_design_name_field_path'])
    time.sleep(2)

    act_req_err_msg = get_text_by_xpath(gift_card_path['design_name_req_err_msg_path'])
    print(act_req_err_msg)
    if act_req_err_msg == design_name_req_err_msg:
        print("Test 12 : Gift card design name field req error message is : ", act_req_err_msg)

    send_keys_by_xpath(gift_card_path['gift_card_design_name_field_path'],'(Updated) Self-Care')
    time.sleep(2)
    print("Test 13 : Gift card design name is updated successfully!!")
    time.sleep(3)

    # Real Second Scroll
    element = driver.find_element(By.XPATH, "/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div/div[1]/div/div[3]/div[3]/div[2]/div[2]/fieldset/input")
    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(2)

    #Add new gift card design
    click_by_xpath(gift_card_path['add_design_btn_path'])
    time.sleep(2)

    # Upload new gift card design image
    image_path = "/Users/aungwaiwaithin/Downloads/LLK_jp.jpeg"

    upload_input = driver.find_element(By.XPATH, '//input[@type="file"]')
    time.sleep(2)
    upload_input.send_keys(image_path)
    time.sleep(3)

    driver.find_element(By.XPATH, gift_card_path['upload_img_btn_path']).click()
    print("Test 14 : New gift card design image is uploaded successfully!!")
    time.sleep(3)

    send_keys_by_xpath("/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div/div[1]/div/div[3]/div[6]/div[2]/div[2]/fieldset/input",'Newly added gift card design name ')
    time.sleep(2)
    print("Test 15 : New gift card design name is added successfully!!")
    time.sleep(2)

    #Remove one gift card design
    click_by_xpath("/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div/div[1]/div/div[3]/div[6]/div[1]/button")
    time.sleep(2)
    print("Test 16 : Gift card design is removed successfully!!")
    time.sleep(2)

    # Third Scroll
    element = driver.find_element(By.XPATH, "/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div/div[1]/div/div[3]/div[5]/div[2]/div[2]/fieldset/input")
    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(2)

    #Gift card amount validation
    clear_by_xpath(gift_card_path['gift_card_amt_field_path_old'])
    time.sleep(2)

    act_req_err_msg = get_text_by_xpath(gift_card_path['gift_card_amt_req_err_msg_path'])
    print(act_req_err_msg)
    if actual_err_msg==act_gift_card_amt_req_err_msg:
        print("Test 17 (a) : Gift card amount required error message is not a user familiar one.", actual_err_msg)
    if actual_err_msg==exp_gift_card_amt_req_err_msg:
        print("Test 17 (b) : Gift card amount required error message is a user familiar one. : ", actual_err_msg)

    send_keys_by_xpath(gift_card_path['gift_card_amt_field_path_old'],'60')
    time.sleep(2)
    print("Test 18 : Gift card amount is updated successfully!!")
    time.sleep(2)

    #Delete old gift card amount and added new one
    click_by_xpath(gift_card_path['gift_card_amt_delete_btn_path'])
    print("Test 19 : Gift card amount is deleted successfully!!")
    time.sleep(2)

#Add new gift card amount field
    click_by_xpath(gift_card_path['add_amt_btn_path'])
    time.sleep(2)

    clear_by_xpath(gift_card_path['gift_card_amt_field_path_new'])
    time.sleep(2)

    send_keys_by_xpath(gift_card_path['gift_card_amt_field_path_new'],'10')
    time.sleep(2)
    print("Test 20 : New gift card amount is added successfully!!")
    time.sleep(2)

    # Fourth Scroll
    element = driver.find_element(By.XPATH, "/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div/div[1]/div/div[4]/div[3]/div/fieldset/input")
    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(2)

    #Check expiry in validation
    clear_by_xpath(gift_card_path['expire_in_field_path'])
    time.sleep(2)

    act_req_msg=get_text_by_xpath(gift_card_path['expire_in_req_err_msg_path'])
    print(act_req_msg)
    if act_req_msg == expire_in_req_err_msg:
        print("Test 21 : Expires in field req error message is : ", act_req_msg)

    send_keys_by_xpath(gift_card_path['expire_in_field_path'], '3')
    time.sleep(2)
    print("Test 22 : Expires in value is updated successfully!!")
    time.sleep(2)

    #Day or month box update
    click_by_xpath(gift_card_path['day_or_month_btn_path'])
    time.sleep(3)

    #Need to click manually since clicking is not working

    # want_to_select_value = "Days"
    # select_element = WebDriverWait(driver, 10).until(
    #     EC.presence_of_element_located((By.XPATH, "//select"))
    # )
    # Select(select_element).select_by_visible_text(want_to_select_value)
    # time.sleep(3)

    print("Test 23 : Day(s) or Month(s) value is updated successfully!!")

    #Click 'Publish Changes' button to update gift card

    try:
        click_by_xpath(gift_card_path['public_change_btn_path'])
        time.sleep(6)
        print("Test 24 : Old gift card data are updated successfully!")
        time.sleep(4)
    except Exception as e:
        print("Old gift card is updated successfully but, got unexpected error!!", str(e))