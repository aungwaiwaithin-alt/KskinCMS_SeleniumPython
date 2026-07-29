"""Stable locators for Therapists (staging 2026-07-24). Prefer CSS/text over absolute XPath."""

therapist_path = {
    "search_box_name": "code",
    "search_box_css": 'input[name="code"]',
    "name_search_res_path": "//table//tbody/tr[1]/td[1]",
    "mobile_search_res_path": "//table//tbody/tr[1]/td[1]",
    "rate_search_res_path": "//table//tbody/tr[1]/td[2]",
    "no_match_search_res_path": "//*[contains(.,'No therapists') or contains(.,'No therapist')]",

    # listing actions — first data row
    "list_three_dots_action_btn_pth": "//table//tbody/tr[1]//td[last()]//div[contains(@class,'actions-column')]//button | //table//tbody/tr[1]//td[last()]//button",
    "list_set_as_inactive": "//*[@role='menuitem' and contains(.,'Set as inactive')]",
    "yes_set_as_in_active": "//button[contains(.,'Yes, update status') or contains(.,'Yes, set as inactive')]",
    "check_status_path": "//table//tbody/tr[1]/td[5]",
    "list_set_as_active": "//*[@role='menuitem' and contains(.,'Set as active')]",
    "yes_set_as_active": "//button[contains(.,'Yes, update status') or contains(.,'Yes, set as active')]",

    "row_per_page_select_box_path": "//select[@title='pageSize']",
    "10_row_per_page_path": "//select[@title='pageSize']/option[@value='10']",
    "20_row_per_page_path": "//select[@title='pageSize']/option[@value='20']",
    "50_row_per_page_path": "//select[@title='pageSize']/option[@value='50']",

    "add_new_therapist_btn_pth": "//button[contains(.,'Add') or contains(.,'Create') or contains(.,'New therapist')]",

    "more_action_btn_path": "//header//button[.//svg or contains(.,'More')]",
    "more_action_inactive_btn_path": "//*[contains(normalize-space(.),'Set as inactive')]",
    "more_action_active_btn_path": "//*[contains(normalize-space(.),'Set as active')]",

    "upload_file_btn_path": "//button[contains(.,'Upload')]",
    "upload_img_btn_path": "//button[contains(.,'Upload') or contains(.,'Confirm') or contains(.,'Save')]",

    "full_name": "fullName",
    "req_full_name_err_msg_path": "//p[contains(.,'Full Name is required')]",
    "req_full_name_err_msg_path_for_update": "//p[contains(.,'Full Name is required')]",

    "display_name": "displayName",
    "req_display_name_err_msg_path": "//p[contains(.,'Display Name is required')]",
    "req_display_name_err_msg_path_for_update": "//p[contains(.,'Display Name is required')]",

    "dob_path": "//label[@for='dob']/following::button[1]",
    "dob_path_for_update": "//label[@for='dob']/following::button[1]",

    "invalid_selected_dob_value_path": "/html/body/div[2]/div/div/div/div/table/tbody/tr[1]/td[6]/button",
    "valid_selected_dob_value_path": "/html/body/div[2]/div/div/div/div/table/tbody/tr[1]/td[1]/button",
    "dob_ok_btn_path": "/html/body/div[2]/div/div/div/div/table/tfoot/tr/td/div/button[2]",

    "req_dob_err_msg_path": "//p[contains(.,'Date of Birth is required')]",
    "delete_dob_btn": "//label[@for='dob']/following-sibling::fieldset[1]//*[name()='svg']",
    "dob_validation_err_msg_path": "//p[contains(.,'Date of birth cannot be in the future')]",
    "dob_validation_err_msg_path_for_create": "//p[contains(.,'Date of birth cannot be in the future')]",
    "to_get_dob_value_path": "//label[@for='dob']/following::button[1]//span",

    "email_name": "email",
    "invalid_email_err_msg_path": "//p[contains(.,'Invalid email')]",
    "invalid_email_err_msg_path_for_update": "//p[contains(.,'Invalid email')]",
    "req_email_err_msg_path": "//p[contains(.,'Email is required')]",
    "req_email_err_msg_path_for_update": "//p[contains(.,'Email is required')]",

    "gender_select_box_path": "//button[@role='combobox']",
    "gender_selected_value_path": "//button[@role='combobox'][1]/span",

    "country_code_dropdown_path": "//button[@role='combobox'][contains(.,'+') or contains(.,'65')]",
    "selected_country_code_path": "//*[contains(.,'+65')]",
    "mobile_no_name": "mobile",
    "req_mobile_no_err_msg_path": "//p[contains(.,'Mobile No. is required')]",
    "req_mobile_no_err_msg_path_for_update": "//p[contains(.,'Mobile No. is required')]",

    # create/update date/time pickers — still brittle; left for future hardening
    "start_datebox_path": "/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[2]/div[1]/div/div/div[1]/section[2]/div[1]/div[1]/fieldset/button",
    "start_datebox_path_for_create": "/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[1]/div/div/div[1]/section[2]/div[1]/div[1]/fieldset/button",
    "start_date_value_path": "/html/body/div[2]/div/div/div/div/table/tbody/tr[1]/td[5]/button",
    "start_date_Ok_btn_path": "/html/body/div[2]/div/div/div/div/table/tfoot/tr/td/div/button[2]",
    "start_timebox_path": "/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[2]/div[1]/div/div/div[1]/section[2]/div[1]/div[2]/fieldset/button",
    "start_timebox_path_for_create": "/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[1]/div/div/div[1]/section[2]/div[1]/div[2]/fieldset/button",
    "hour_path": "/html/body/div/div/div[1]/div/div[1]/div/div/form/div[2]/div/div[2]/div[1]/div/div/div[1]/section[2]/div[1]/div[2]/fieldset/div/div/div/div[1]/div[1]/div/div/div/button[20]",
    "hour_path_for_create": "/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[1]/div/div/div[1]/section[2]/div[1]/div[2]/fieldset/div/div/div/div[1]/div[1]/div/div/div/button[13]",
    "minute_path": "/html/body/div/div/div[1]/div/div[1]/div/div/form/div[2]/div/div[2]/div[1]/div/div/div[1]/section[2]/div[1]/div[2]/fieldset/div/div/div/div[1]/div[2]/div/div/div/button[16]",
    "minute_path_for_create": "/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[1]/div/div/div[1]/section[2]/div[1]/div[2]/fieldset/div/div/div/div[1]/div[2]/div/div/div/button[51]",
    "Ok_btn_path_for_create": "/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[1]/div/div/div[1]/section[2]/div[1]/div[2]/fieldset/div/div/div/div[2]/button[2]/p/span",
    "Ok_btn_path": "//html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[2]/div[1]/div/div/div[1]/section[2]/div[1]/div[2]/fieldset/div/div/div/div[2]/button[2]/p/span",
    "end_datebox_path": "/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[2]/div[1]/div/div/div[1]/section[2]/div[2]/div[1]/fieldset/button",
    "end_datebox_path_for_create": "/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[1]/div/div/div[1]/section[2]/div[2]/div[1]/fieldset/button",
    "end_date_value_path": "/html/body/div[2]/div/div/div/div/table/tbody/tr[4]/td[4]/button",
    "end_date_Ok_btn_path": "/html/body/div[2]/div/div/div/div/table/tfoot/tr/td/div/button[2]",
    "end_timebox_path": "/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[2]/div[1]/div/div/div[1]/section[2]/div[2]/div[2]/fieldset/button",
    "end_timebox_path_for_create": "/html/body/div/div/div[1]/div/div[1]/div/div/form/div[2]/div/div[1]/div/div/div[1]/section[2]/div[2]/div[2]/fieldset/button",
    "end_hour_path": "/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[2]/div[1]/div/div/div[1]/section[2]/div[2]/div[2]/fieldset/div/div/div/div[1]/div[1]/div/div/div/button[22]",
    "end_hour_path_for_create": "/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[1]/div/div/div[1]/section[2]/div[2]/div[2]/fieldset/div/div/div/div[1]/div[1]/div/div/div/button[13]",
    "end_minute_path": "/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[2]/div[1]/div/div/div[1]/section[2]/div[2]/div[2]/fieldset/div/div/div/div[1]/div[2]/div/div/div/button[45]",
    "end_minute_path_for_create": "/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[1]/div/div/div[1]/section[2]/div[2]/div[2]/fieldset/div/div/div/div[1]/div[2]/div/div/div/button[51]",
    "end_Ok_btn_path": "/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[2]/div[1]/div/div/div[1]/section[2]/div[2]/div[2]/fieldset/div/div/div/div[2]/button[2]/p/span",
    "end_Ok_btn_path_for_create": "/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[1]/div/div/div[1]/section[2]/div[2]/div[2]/fieldset/div/div/div/div[2]/button[2]/p/span",

    "save_btn_path": "//footer//button[contains(.,'Save') or contains(.,'Create')]",
    "selected_start_from_date_value_path": "/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[2]/div[1]/div/div/div[1]/section[2]/div[1]/div[1]/fieldset/button/span",
    "selected_start_from_time_value_path": "/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[2]/div[1]/div/div/div[1]/section[2]/div[1]/div[2]/fieldset/button/span",
    "selected_end_on_date_value_path": "/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[2]/div[1]/div/div/div[1]/section[2]/div[2]/div[1]/fieldset/button/span",
    "selected_end_on_time_value_path": "/html/body/div/div/div[1]/div/div/div/div/form/div[2]/div/div[2]/div[1]/div/div/div[1]/section[2]/div[2]/div[2]/fieldset/button/span",
    "delete_img_btn": "//button[contains(.,'Delete') or contains(@aria-label,'Delete')]",
    "save_changes_btn_path": "//footer//button[contains(.,'Save')]",
}
