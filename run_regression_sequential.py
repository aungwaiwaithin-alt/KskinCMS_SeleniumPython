"""
Run Kskin CMS Selenium modules sequentially on ONE shared Chrome + ONE login.

  cd /Users/aungwaiwaithin/AquaProjects
  PYTHONPATH=/Users/aungwaiwaithin/AquaProjects python3 KskinCMS/run_regression_sequential.py

Do NOT launch parallel agents/processes — that opens many Chromes and re-logins.
"""

import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest
from KskinCMS.cms_auth import get_driver, quit_driver, login_cms


# Order: listing-focused modules first
MODULES = [
    "KskinCMS/Franchise_Account_Module/FranchiseAccMain.py",
    "KskinCMS/Outlet_Module/OutletMain.py",
    "KskinCMS/Regions_Module/RegionMain.py",
    "KskinCMS/Therapists_Module/TherapistMain.py",
    "KskinCMS/IssueFreeVoucher_Module/IFVMain.py",
    "KskinCMS/Product_Module/ProductMain.py",
    "KskinCMS/Treatment_Module/TreatmentMain.py",
    "KskinCMS/GiftCard_Module/GiftCardMain.py",
    "KskinCMS/GiftBundle_Module/GiftBundleMain.py",
]


def main():
    # Warm shared browser + login once before any module import creates work
    driver = get_driver()
    login_cms(driver)
    print("=== Shared session ready — running modules one by one ===\n")

    failures = []
    try:
        for mod in MODULES:
            print(f"\n######## {mod} ########")
            code = pytest.main(["-s", "--tb=line", "-q", mod])
            if code != 0:
                failures.append((mod, code))
    finally:
        quit_driver()

    print("\n=== DONE ===")
    if failures:
        print("Failed modules:")
        for m, c in failures:
            print(f"  {m} (exit {c})")
        sys.exit(1)
    print("All module suites finished.")


if __name__ == "__main__":
    main()
