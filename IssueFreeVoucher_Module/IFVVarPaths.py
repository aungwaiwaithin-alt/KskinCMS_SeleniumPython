"""Stable locators for Issue Free Vouchers (staging 2026-07-24). Prefer CSS/text over absolute XPath."""

ifv_path = {
    "voucher_name_search_box_name": "code",
    "search_box_css": 'input[name="code"][placeholder*="Find by voucher name"]',

    "matched_search_res_path": "//table//tbody/tr[1]/td[1]",
    "type_search_res_path": "//table//tbody/tr[1]/td[4]",
    "no_voucher_res_path": "//*[contains(normalize-space(.),'No vouchers yet')]",

    "type_filter_combobox": "//button[@role='combobox']",
    "type_filter_select": 'select[aria-hidden="true"]',

    "row_per_page_select_box_path": "//select[@title='pageSize']",
    "10_row_per_page_path": "//select[@title='pageSize']/option[@value='10']",
    "20_row_per_page_path": "//select[@title='pageSize']/option[@value='20']",
    "50_row_per_page_path": "//select[@title='pageSize']/option[@value='50']",

    "next_page_btn_path": "//table//tfoot//*[normalize-space()='2' or normalize-space()='>']",
    "prev_page_btn_path": "//table//tfoot//*[normalize-space()='1']",
    "page_1_btn_path": "//table//tfoot//*[normalize-space()='1']",
    "page_2_btn_path": "//table//tfoot//*[normalize-space()='2']",

    "add_issue_voucher_btn_pth": "//button[contains(.,'Issue Voucher')]",

    # create form (brittle — kept for optional create flow)
    "voucher_type_req_err_msg_path": "//p[contains(.,'Voucher type is required')]",
    "voucher_name_req_err_msg_path": "//p[contains(.,'Voucher name is required')]",
    "desc_req_err_msg_path": "//p[contains(.,'Description is required')]",
    "discount_amt_err_msg_path": "//p[contains(.,'Discount') or contains(.,'Value must')]",
    "discount_apply_to_req_err_msg_path": "//p[contains(.,'Please select where to apply')]",
    "remark_req_err_msg_path": "//p[contains(.,'Remark is required')]",
    "t_and_c_req_err_msg_path": "//p[contains(.,'Terms and conditions')]",
    "min_spent_amt_err_msg_path": "//p[contains(.,'Minimum spent')]",
    "expires_in_req_err_msg_path": "//p[contains(.,'Expired in is required') or contains(.,'Expires')]",

    "1for1_radio_btn_path": "//button[contains(.,'1 for 1')]",
    "dollar_off_radio_btn_path": "//button[contains(.,'$ off')]",
    "percent_off_radio_btn_path": "//button[contains(.,'% off')]",

    "voucher_name": "name",
    "description_path": "//textarea[contains(@name,'description') or @name='description'] | //label[contains(.,'Description')]/following::textarea[1]",
    "discount_value_name": "discountAmount",

    "individual_item_path": "//button[contains(.,'Individual')]",
    "total_bill_path": "//button[contains(.,'Total bill') or contains(.,'Total Bill')]",

    "outlet_dropdown_path": "//label[contains(.,'Outlet')]/following::button[@role='combobox'][1]",
    "remark_name": "remark",
    "t_n_c_path": "//label[contains(.,'Terms')]/following::textarea[1]",
    "tier_member_option_path": "//button[contains(.,'Tier')]",
    "premium_tier_path": "//button[contains(.,'Premium')]",

    "apply_voucher_to_product_edit_btn_path": "//button[contains(.,'Edit') or contains(.,'Select')][1]",
    "apply_btn_path": "//button[contains(.,'Apply')]",

    "min_spent_amt_name": "minimumSpentAmount",
    "usage_limit_checkbox_path": "//button[@role='checkbox']",
    "upload_image_btn_path": "//button[contains(.,'Upload')]",
    "expire_in_textbox_name": "expiredIn",
    "publish_btn_path": "//button[contains(.,'Publish')]",
}
