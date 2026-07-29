"""Shared staging CMS config for Selenium modules (updated 2026-07-24)."""

BASE_URL = "https://staging-cms.kskinfacial.com"
LOGIN_URL = f"{BASE_URL}/login"

# Staging QA account
CMS_EMAIL = 'YOUR_EMAIL@example.com'
CMS_PASSWORD = 'YOUR_PASSWORD'
CMS_OTP_DIGIT = '1'  # staging accepts 111111

# Desktop viewport — narrow view collapses sidebar to icons and breaks xpath nav
VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 1080

MODULE_URLS = {
    "outlets": f"{BASE_URL}/account/outlet-management/outlets",
    "regions": f"{BASE_URL}/account/outlet-management/regions",
    "franchisee_accounts": f"{BASE_URL}/account/franchise-management/franchisee-accounts",
    "therapists": f"{BASE_URL}/account/therapist-management/therapists",
    "issue_free_vouchers": f"{BASE_URL}/account/customer-management/issue-free-vouchers",
    "products": f"{BASE_URL}/account/inventory/products",
    "treatments": f"{BASE_URL}/account/inventory/treatments",
    "gift_card": f"{BASE_URL}/account/inventory/gift-card",
    "gift_bundles": f"{BASE_URL}/account/inventory/gift-bundles",
    "transactions": f"{BASE_URL}/account/sales/transactions",
}
