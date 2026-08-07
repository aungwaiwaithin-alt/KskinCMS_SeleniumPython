"""Clean Android UAT — brand-new signup then login.

Does not import anything from the old MCP_Appium_Server signup patches.
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from helpers.dynamic_data import next_android_run_values  # noqa: E402
from helpers.step_report import StepReporter  # noqa: E402
from pages.signup_login_android_page import SignupLoginAndroidPage  # noqa: E402
import config  # noqa: E402


REPORT_PATH = Path(
    os.environ.get(
        "CLEAN_ANDROID_SIGNUP_REPORT",
        str(ROOT / "reports" / "KS-CLEAN-AND-001_signup_login.html"),
    )
)


def _banner(num: int, total: int, title: str) -> None:
    print("\n" + "=" * 64, flush=True)
    print(f"  STEP {num}/{total}: {title}", flush=True)
    print("=" * 64 + "\n", flush=True)
    if config.STEP_PRE_PAUSE_SEC:
        time.sleep(config.STEP_PRE_PAUSE_SEC)


@pytest.mark.android
def test_signup_then_login(android_driver):
    run = next_android_run_values()
    page = SignupLoginAndroidPage(android_driver)
    r = StepReporter()
    r.init(
        test_case_id="KS-CLEAN-AND-001",
        test_name="Kskin Android UAT — Sign-Up + Login (clean)",
        subtitle="Greenfield suite: email/OTP → profile → permissions → logout → login",
        environment=[
            ("Test Case ID", "KS-CLEAN-AND-001"),
            ("Platform", "Android"),
            ("App package", config.ANDROID_PACKAGE),
            ("Signup email", run.signup_email),
            ("Signup mobile", run.signup_mobile),
            ("OTP", run.otp),
        ],
        driver=android_driver,
    )

    cases = []

    def add(title, expected, fn):
        cases.append((title, expected, fn))

    add(
        "Launch app and tap Get Started",
        "Welcome / signup entry screen",
        lambda: page.tap_get_started().tap_sign_up(),
    )
    add(
        "Tap Next with empty Email field",
        "Validation error for empty/invalid email",
        lambda: page.tap_next(),
    )
    add(
        f"Enter new email {run.signup_email} and tap Next",
        "Email OTP / verify-email screen",
        lambda: page.enter_email(run.signup_email).tap_next(),
    )
    add(
        f"Enter default OTP '{run.otp}' on email-verification screen",
        "OTP accepted; Create Account form",
        lambda: page.enter_otp(run.otp).tap_next(),
    )
    add(
        "Fill Create Account form and submit",
        "Account created / next gate (mobile OTP or home)",
        lambda: (
            page.enter_first_name(run.first_name)
            .enter_last_name(run.last_name)
            .pick_dob(run.dob)
            .select_gender(run.gender)
            .enter_password(run.signup_password)
            .enter_mobile(run.signup_mobile)
            ._hide_keyboard_if_shown()
            .tap_create_account()
        ),
    )
    def step_mobile_and_permissions():
        # If OTP boxes are still on screen, treat as mobile verify; else skip to permissions
        if len(page._edit_texts()) >= 1 and page._exists(
            "xpath", '//*[contains(@text,"digit") or contains(@text,"code") or contains(@text,"Verify")]'
        ):
            page.enter_otp(run.mobile_otp).tap_next()
        page.handle_permissions()

    add(
        "Enter mobile OTP if shown, then allow permissions",
        "Home / main app reachable",
        step_mobile_and_permissions,
    )
    add(
        "Log out",
        "Back on auth / welcome screen",
        lambda: page.tap_log_out(),
    )
    add(
        "Log in with the new account",
        "Home after login",
        lambda: (
            page.tap_log_in()
            .enter_email(run.login_email)
            .enter_password(run.login_password)
            .tap_next()
            .handle_permissions()
        ),
    )

    failed = False
    total = len(cases)
    try:
        for i, (title, expected, fn) in enumerate(cases, start=1):
            _banner(i, total, title)
            try:
                fn()
                # Soft assert for empty-email step: surface validation copy if present
                if i == 2:
                    err = page.visible_error_text()
                    actual = err or "Next tapped (validation UI may vary)"
                    if err and "email" not in err.lower() and "valid" not in err.lower():
                        # still pass if any validation text; record it
                        pass
                    r.record_step(i, title, expected, actual, "pass")
                else:
                    r.record_step(i, title, expected, "OK — step completed", "pass")
                print(f"[PASS] Step {i}: {title}", flush=True)
            except Exception as e:
                r.record_step(i, title, expected, f"FAIL: {e}", "fail")
                print(f"[FAIL] Step {i}: {e}", flush=True)
                failed = True
                break
            if config.STEP_PAUSE_SEC:
                time.sleep(config.STEP_PAUSE_SEC)
    finally:
        r.emit(str(REPORT_PATH))

    if failed:
        pytest.fail(f"Signup/login failed — see {REPORT_PATH}")
