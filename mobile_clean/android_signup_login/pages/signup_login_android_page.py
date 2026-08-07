"""Clean Android signup + login page object (text / accessibility first)."""
from __future__ import annotations

import subprocess
import time
from typing import Any, List, Optional, Sequence, Tuple

from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait

from config import EXPLICIT_WAIT


class SignupLoginAndroidPage:
    def __init__(self, driver: Any) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, EXPLICIT_WAIT)

    # ----- primitives -----
    def _pause(self, sec: float = 0.35) -> None:
        time.sleep(sec)

    def _find(self, how: str, value: str):
        return self.driver.find_element(how, value)

    def _exists(self, how: str, value: str) -> bool:
        try:
            self._find(how, value)
            return True
        except Exception:
            return False

    def _tap_labels(self, labels: Sequence[str], timeout: float = 12.0) -> "SignupLoginAndroidPage":
        end = time.time() + timeout
        last: Optional[Exception] = None
        while time.time() < end:
            for text in labels:
                strategies: List[Tuple[str, str]] = [
                    (AppiumBy.ACCESSIBILITY_ID, text),
                    (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{text}")'),
                    (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{text}")'),
                    (AppiumBy.XPATH, f'//*[@text="{text}"]'),
                    (AppiumBy.XPATH, f'//*[contains(@text,"{text}")]'),
                    (AppiumBy.XPATH, f'//*[@content-desc="{text}"]'),
                ]
                for how, val in strategies:
                    try:
                        el = self._find(how, val)
                        el.click()
                        self._pause()
                        return self
                    except Exception as e:
                        last = e
            self._pause(0.4)
        raise NoSuchElementException(f"Could not tap any of {list(labels)}; last={last}")

    def _edit_texts(self) -> List[Any]:
        try:
            return list(self.driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.EditText"))
        except Exception:
            return []

    def _field_by_hint(self, *needles: str):
        needles_l = [n.lower() for n in needles]
        for el in self._edit_texts():
            blob = " ".join(
                str(el.get_attribute(a) or "")
                for a in ("text", "hint", "content-desc", "resource-id")
            ).lower()
            if any(n in blob for n in needles_l):
                return el
        return None

    def _type(self, el: Any, value: str) -> None:
        try:
            el.click()
        except Exception:
            pass
        self._pause(0.2)
        try:
            el.clear()
        except Exception:
            pass
        try:
            el.send_keys(value)
            return
        except Exception:
            pass
        # ADB fallback (helps with '@' on some builds)
        self._adb_type(value)

    def _adb_type(self, text: str) -> None:
        if "@" in text:
            local, _, domain = text.partition("@")
            subprocess.run(["adb", "shell", "input", "text", local], check=False)
            subprocess.run(["adb", "shell", "input", "text", "@"], check=False)
            subprocess.run(["adb", "shell", "input", "text", domain], check=False)
        else:
            safe = text.replace(" ", "%s")
            subprocess.run(["adb", "shell", "input", "text", safe], check=False)
        self._pause(0.25)

    def _hide_keyboard_if_shown(self) -> "SignupLoginAndroidPage":
        try:
            self.driver.hide_keyboard()
        except Exception:
            subprocess.run(["adb", "shell", "input", "keyevent", "4"], check=False)
        self._pause(0.2)
        return self

    def visible_error_text(self) -> str:
        xpaths = [
            '//*[contains(@text,"Please")]',
            '//*[contains(@text,"valid")]',
            '//*[contains(@text,"required") or contains(@text,"Required")]',
            '//*[contains(@resource-id,"error") or contains(@resource-id,"helper")]',
        ]
        chunks: List[str] = []
        for xp in xpaths:
            try:
                for el in self.driver.find_elements(AppiumBy.XPATH, xp):
                    t = (el.text or "").strip()
                    if t:
                        chunks.append(t)
            except Exception:
                pass
        return " | ".join(chunks[:5])

    # ----- flow actions (always return self) -----
    def tap_get_started(self) -> "SignupLoginAndroidPage":
        return self._tap_labels(["Get Started", "GET STARTED"])

    def tap_sign_up(self) -> "SignupLoginAndroidPage":
        # Some builds land on email after Get Started; Sign Up may be optional
        try:
            return self._tap_labels(["Sign Up", "SIGN UP", "Sign up"], timeout=4)
        except Exception:
            return self

    def tap_next(self) -> "SignupLoginAndroidPage":
        self._hide_keyboard_if_shown()
        return self._tap_labels(["Next", "NEXT", "Continue", "CONTINUE"])

    def enter_email(self, email: str) -> "SignupLoginAndroidPage":
        el = self._field_by_hint("email") or (self._edit_texts()[0] if self._edit_texts() else None)
        if el is None:
            raise NoSuchElementException("Email field not found")
        self._type(el, email)
        return self

    def enter_otp(self, otp: str = "111111") -> "SignupLoginAndroidPage":
        code = "".join(ch for ch in str(otp) if ch.isdigit())[:6].ljust(6, "0")
        fields = self._edit_texts()
        # Prefer empty/short boxes (OTP cells)
        cells = []
        for el in fields:
            try:
                t = (el.text or el.get_attribute("text") or "").strip()
            except Exception:
                t = ""
            if len(t) <= 1:
                cells.append(el)
        if len(cells) >= 6:
            for i, ch in enumerate(code):
                self._type(cells[i], ch)
            return self
        if fields:
            self._type(fields[0], code)
            return self
        self._adb_type(code)
        return self

    def enter_first_name(self, value: str) -> "SignupLoginAndroidPage":
        el = self._field_by_hint("first") or (self._edit_texts()[0] if self._edit_texts() else None)
        if el is None:
            raise NoSuchElementException("First name field not found")
        self._type(el, value)
        return self

    def enter_last_name(self, value: str) -> "SignupLoginAndroidPage":
        el = self._field_by_hint("last")
        if el is None:
            edits = self._edit_texts()
            el = edits[1] if len(edits) > 1 else None
        if el is None:
            raise NoSuchElementException("Last name field not found")
        self._type(el, value)
        return self

    def enter_password(self, value: str) -> "SignupLoginAndroidPage":
        el = self._field_by_hint("password")
        if el is None:
            edits = self._edit_texts()
            el = edits[-1] if edits else None
        if el is None:
            raise NoSuchElementException("Password field not found")
        self._type(el, value)
        return self

    def enter_mobile(self, value: str) -> "SignupLoginAndroidPage":
        el = self._field_by_hint("mobile", "phone")
        if el is None:
            raise NoSuchElementException("Mobile field not found")
        self._type(el, value)
        return self

    def pick_dob(self, value: str = "11/04/1998") -> "SignupLoginAndroidPage":
        # Open DOB field
        opened = False
        for label in ("Date of birth", "Date of Birth", "DD/MM/YYYY", "DOB"):
            try:
                self._tap_labels([label], timeout=3)
                opened = True
                break
            except Exception:
                pass
        if not opened:
            for xp in (
                '//*[contains(@resource-id,"dob") or contains(@resource-id,"birth") or contains(@resource-id,"date")]',
            ):
                try:
                    self._find(AppiumBy.XPATH, xp).click()
                    opened = True
                    break
                except Exception:
                    pass
        self._pause(0.4)
        # Prefer text-input mode on Material picker
        for label in (
            "Switch to text input mode",
            "Switch to text input",
            "Edit",
        ):
            try:
                self._tap_labels([label], timeout=2)
                break
            except Exception:
                pass
        edits = self._edit_texts()
        if edits:
            self._type(edits[-1], value.replace("/", ""))
            self._pause(0.2)
            self._type(edits[-1], value)
        # Confirm
        try:
            self._tap_labels(["OK", "Ok", "O.K."], timeout=4)
        except Exception:
            try:
                self._find(AppiumBy.ID, "android:id/button1").click()
            except Exception:
                pass
        return self

    def select_gender(self, value: str = "Female") -> "SignupLoginAndroidPage":
        label = value or "Female"
        for xp in (
            f'//android.widget.RadioButton[@text="{label}"]',
            f'//android.widget.RadioButton[contains(@text,"{label}")]',
            f'//*[@text="{label}"]',
            f'//*[contains(@text,"{label}")]',
        ):
            try:
                self._find(AppiumBy.XPATH, xp).click()
                self._pause()
                return self
            except Exception:
                pass
        raise NoSuchElementException(f"Gender option not found: {label}")

    def tap_create_account(self) -> "SignupLoginAndroidPage":
        self._hide_keyboard_if_shown()
        return self._tap_labels(["Create Account", "CREATE ACCOUNT", "Create account"])

    def handle_permissions(self) -> "SignupLoginAndroidPage":
        # Best-effort OS permission dialogs
        for _ in range(6):
            tapped = False
            for label in (
                "While using the app",
                "Allow",
                "ALLOW",
                "Allow all the time",
                "Only this time",
            ):
                try:
                    self._tap_labels([label], timeout=1.5)
                    tapped = True
                    break
                except Exception:
                    pass
            if not tapped:
                break
        return self

    def tap_log_out(self) -> "SignupLoginAndroidPage":
        # Open account area then logout
        for label in ("Account", "Profile", "Me"):
            try:
                self._tap_labels([label], timeout=3)
                break
            except Exception:
                pass
        self._tap_labels(["Log Out", "Logout", "LOG OUT", "Log out"])
        try:
            self._tap_labels(["Yes", "Confirm", "OK"], timeout=4)
        except Exception:
            pass
        return self

    def tap_log_in(self) -> "SignupLoginAndroidPage":
        return self._tap_labels(["Log In", "Login", "LOG IN", "Sign In", "SIGN IN"])
