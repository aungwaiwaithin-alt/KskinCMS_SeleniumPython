#!/usr/bin/env python3
"""Fix Android Create-Account DOB for Material 'Select date' picker.

Observed failure: calendar opens on today (e.g. Aug 7, 2026) and stays open;
form DOB remains empty / wrong so Create Account cannot continue.

Real flow (matches suite step + screenshots):
  1) Tap DOB field (DD/MM/YYYY)
  2) In 'Select date' dialog tap pencil = Switch to text input mode
  3) Clear → type 11041998 or 11/04/1998
  4) Tap OK
  5) Assert form no longer shows DD/MM/YYYY

Run on Mac:
  python3 ~/AquaProjects/KskinCMS/one_click/patch_android_dob.py
"""
from __future__ import annotations

import os
import re
import shutil
import time
from pathlib import Path

AQUA = Path(os.environ.get("AQUA_ROOT", Path.home() / "AquaProjects"))
APPIUM_PY = Path(os.environ.get("APPIUM_PY", AQUA / "MCP_Appium_Server" / "python"))
PAGE = APPIUM_PY / "pages" / "signup_login_android_page.py"
MARKER = "KSKIN_DOB_PICKER_FIX"

DOB_BLOCK = r'''
    # --- KSKIN_DOB_PICKER_FIX ---
    def _dob_digits(self, value=None, *args, **kwargs) -> str:
        if value is None and args:
            value = args[0]
        if value is None:
            value = kwargs.get("dob") or kwargs.get("digits") or "11041998"
        digits = "".join(ch for ch in str(value) if ch.isdigit())
        return (digits[:8] if len(digits) >= 8 else digits.ljust(8, "0")[:8])

    def _dob_formatted(self, digits: str) -> str:
        d = self._dob_digits(digits)
        return f"{d[0:2]}/{d[2:4]}/{d[4:8]}"

    def _tap_texts(self, texts, timeout_s: float = 0.2) -> bool:
        driver = self.driver
        for text in texts:
            for how, val in (
                ("accessibility id", text),
                ("xpath", f'//*[@text="{text}"]'),
                ("xpath", f'//*[contains(@text,"{text}")]'),
                ("xpath", f'//*[@content-desc="{text}"]'),
                ("xpath", f'//*[contains(@content-desc,"{text}")]'),
            ):
                try:
                    driver.find_element(how, val).click()
                    return True
                except Exception:
                    continue
        return False

    def _open_dob_dialog(self) -> bool:
        """Open Material Select-date dialog from Create Account form."""
        if self._tap_texts(("DD/MM/YYYY", "Date of birth", "Date of Birth")):
            return True
        # clickable parent/row
        for xp in (
            '//*[contains(@text,"Date of birth") or @text="DD/MM/YYYY"]',
            '//*[contains(@resource-id,"dob") or contains(@resource-id,"birth") or contains(@resource-id,"date")]',
        ):
            try:
                els = self.driver.find_elements("xpath", xp)
            except Exception:
                els = []
            for el in els[:5]:
                try:
                    el.click()
                    return True
                except Exception:
                    continue
        return False

    def _switch_datepicker_to_text_mode(self) -> bool:
        """Tap pencil in Material DatePicker: 'Switch to text input mode'."""
        driver = self.driver
        # Exact Material content-descs (English)
        descs = (
            "Switch to text input mode",
            "Switch to text input",
            "Edit",
            "edit",
            "Pencil",
            "pencil",
        )
        if self._tap_texts(descs):
            return True
        for xp in (
            '//*[contains(@content-desc,"text input") or contains(@content-desc,"Text input")]',
            '//*[contains(@content-desc,"Switch to text")]',
            '//*[contains(@resource-id,"text_input_mode") or contains(@resource-id,"mtrl_picker")]',
            '//android.widget.ImageButton[@clickable="true"]',
            '//android.widget.Button[@clickable="true" and (contains(@content-desc,"edit") or contains(@content-desc,"Edit"))]',
        ):
            try:
                for el in driver.find_elements("xpath", xp)[:6]:
                    try:
                        el.click()
                        return True
                    except Exception:
                        continue
            except Exception:
                continue
        return False

    def _fill_datepicker_text(self, digits: str) -> bool:
        """Type into date picker text field (after pencil)."""
        import time as _t
        driver = self.driver
        formatted = self._dob_formatted(digits)
        plain = self._dob_digits(digits)
        _t.sleep(0.3)
        fields = []
        try:
            fields = driver.find_elements("class name", "android.widget.EditText")
        except Exception:
            fields = []
        if not fields:
            # sometimes TextInputEditText still classifies as EditText; try xpath
            try:
                fields = driver.find_elements("xpath", "//android.widget.EditText|//android.widget.AutoCompleteTextView")
            except Exception:
                fields = []
        if not fields:
            return False
        el = fields[-1]  # dialog field is usually last / topmost
        try:
            el.click()
        except Exception:
            pass
        try:
            el.clear()
        except Exception:
            pass
        # delete leftovers
        try:
            import subprocess
            for _ in range(10):
                subprocess.run(["adb", "shell", "input", "keyevent", "KEYCODE_DEL"], check=False)
        except Exception:
            pass
        # Prefer typed with slashes (Material text mode often expects localized pattern)
        for candidate in (formatted, plain):
            try:
                el.click()
                el.clear()
            except Exception:
                pass
            try:
                el.send_keys(candidate)
                return True
            except Exception:
                if hasattr(self, "_adb_type"):
                    try:
                        self._adb_type(candidate)
                        return True
                    except Exception:
                        pass
        return False

    def _confirm_datepicker(self) -> bool:
        if self._tap_texts(("OK", "Ok", "O.K.")):
            return True
        for xp in (
            '//*[@resource-id="android:id/button1"]',
            '//android.widget.Button[@text="OK" or @text="Ok"]',
            '//*[contains(@resource-id,"confirm_button") or contains(@resource-id,"ok")]',
        ):
            try:
                self.driver.find_element("xpath", xp).click()
                return True
            except Exception:
                continue
        return False

    def _dismiss_datepicker_if_open(self) -> None:
        # if still on Select date, cancel so we don't block later steps
        try:
            if self.driver.find_elements("xpath", '//*[contains(@text,"Select date") or contains(@text,"Select Date")]'):
                self._tap_texts(("Cancel", "CANCEL"))
        except Exception:
            pass

    def _form_dob_text(self) -> str:
        try:
            for el in self.driver.find_elements("class name", "android.widget.EditText"):
                t = (el.text or el.get_attribute("text") or "").strip()
                if not t:
                    continue
                if "DD/MM" in t:
                    return ""
                if "/" in t and any(ch.isdigit() for ch in t):
                    return t
        except Exception:
            pass
        try:
            for el in self.driver.find_elements(
                "xpath",
                '//*[contains(@text,"/") and string-length(@text)>=8 and string-length(@text)<=10]',
            ):
                t = (el.text or "").strip()
                if t and "DD/MM" not in t:
                    return t
        except Exception:
            pass
        return ""

    def pick_dob(self, value=None, *args, **kwargs):
        """Material Select-date: open → pencil(text mode) → type DOB → OK. Returns self."""
        import time as _t
        digits = self._dob_digits(value, *args, **kwargs)
        # Ensure no stale dialog
        self._dismiss_datepicker_if_open()
        self._open_dob_dialog()
        _t.sleep(0.4)
        # Must switch to text input — calendar mode alone leaves "today" selected
        self._switch_datepicker_to_text_mode()
        _t.sleep(0.3)
        self._fill_datepicker_text(digits)
        _t.sleep(0.2)
        self._confirm_datepicker()
        _t.sleep(0.4)
        shown = self._form_dob_text()
        if not shown:
            # Retry once: open → pencil → formatted type → OK
            self._dismiss_datepicker_if_open()
            self._open_dob_dialog()
            _t.sleep(0.3)
            self._switch_datepicker_to_text_mode()
            _t.sleep(0.3)
            self._fill_datepicker_text(digits)
            self._confirm_datepicker()
            _t.sleep(0.4)
            shown = self._form_dob_text()
        if not shown:
            # Last resort: year grid navigation for 11 Apr 1998
            self._dismiss_datepicker_if_open()
            self._open_dob_dialog()
            _t.sleep(0.3)
            # tap year header then 1998 if visible
            self._tap_texts(("1998", "98"))
            # try navigate months — best-effort
            self._tap_texts(("11", "11"))
            self._confirm_datepicker()
            shown = self._form_dob_text()
        if not shown:
            # Don't leave dialog open for later steps
            self._dismiss_datepicker_if_open()
            raise AssertionError(
                f"DOB not set on form after picker (wanted {self._dob_formatted(digits)})"
            )
        return self

    def enter_dob(self, value=None, *args, **kwargs):
        return self.pick_dob(value, *args, **kwargs)

    def enter_date_of_birth(self, value=None, *args, **kwargs):
        return self.pick_dob(value, *args, **kwargs)

    def set_dob(self, value=None, *args, **kwargs):
        return self.pick_dob(value, *args, **kwargs)
'''


def _remove_prior_dob_fix(src: str) -> str:
    if MARKER in src:
        src = re.sub(
            rf"\n    # --- {MARKER} ---[\s\S]*?(?=\n    # --- |\Z)",
            "\n",
            src,
        )
    names = (
        "pick_dob",
        "enter_dob",
        "enter_date_of_birth",
        "set_dob",
        "_dob_digits",
        "_dob_formatted",
        "_tap_texts",
        "_open_dob_dialog",
        "_switch_datepicker_to_text_mode",
        "_fill_datepicker_text",
        "_confirm_datepicker",
        "_dismiss_datepicker_if_open",
        "_form_dob_text",
        "_open_dob_editor",
        "_clear_dob_input",
        "_type_dob_digits",
        "_confirm_dob_picker",
        "_dob_value_on_screen",
        "_tap_by_texts",
    )
    for name in names:
        while re.search(rf"\n    def {name}\(", src):
            src = re.sub(
                rf"\n    def {name}\([\s\S]*?(?=\n    def |\nclass |\Z)",
                "\n",
                src,
                count=1,
            )
    return src


def main() -> int:
    if not PAGE.is_file():
        print(f"ERROR: missing {PAGE}")
        return 1
    bak = PAGE.with_suffix(PAGE.suffix + f".bak_dob2_{int(time.time())}")
    shutil.copy2(PAGE, bak)
    print(f"Backup: {bak}")

    src = _remove_prior_dob_fix(PAGE.read_text(encoding="utf-8", errors="ignore"))
    src = src.rstrip() + "\n" + DOB_BLOCK
    if not src.endswith("\n"):
        src += "\n"
    PAGE.write_text(src, encoding="utf-8")
    print(f"Wrote Material DOB picker fix → {PAGE}")
    text = PAGE.read_text(encoding="utf-8")
    for must in ("_switch_datepicker_to_text_mode", "pick_dob", "_fill_datepicker_text"):
        print(f"  def {must}:", "YES" if f"def {must}(" in text else "NO")
    print("Done. Re-run one-click.")
    print("Expect: Select date → pencil → 11/04/1998 → OK; form shows 11/04/1998 (not today).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
