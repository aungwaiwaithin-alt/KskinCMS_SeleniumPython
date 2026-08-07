#!/usr/bin/env python3
"""Replace weak DOB helpers on SignupLoginAndroidPage with pencil→clear→digits→OK flow.

Symptom: step "Set Date of Birth ..." PASSes but UI still shows DD/MM/YYYY, so
Create Account never advances.

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
OTHER = APPIUM_PY / "pages" / "full_regression_android_page.py"
MARKER = "KSKIN_DOB_PICKER_FIX"

DOB_BLOCK = '''
    # --- KSKIN_DOB_PICKER_FIX ---
    def _dob_digits(self, value=None, *args, **kwargs) -> str:
        if value is None and args:
            value = args[0]
        if value is None:
            value = kwargs.get("dob") or kwargs.get("digits") or "11041998"
        raw = str(value)
        digits = "".join(ch for ch in raw if ch.isdigit())
        # Accept DDMMYYYY or DD/MM/YYYY
        if len(digits) >= 8:
            return digits[:8]
        return digits.ljust(8, "0")[:8]

    def _tap_by_texts(self, texts) -> bool:
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

    def _open_dob_editor(self) -> bool:
        """Open DOB editor: field, pencil icon, or 'Date of birth' row."""
        driver = self.driver
        # 1) Direct field / placeholder
        if self._tap_by_texts(("DD/MM/YYYY", "Date of birth", "Date of Birth", "DOB")):
            return True
        # 2) Pencil / edit affordances near DOB
        for xp in (
            '//*[contains(@text,"Date of birth") or contains(@text,"Date of Birth") or @text="DD/MM/YYYY"]/..//*[@clickable="true"]',
            '//*[contains(@content-desc,"edit") or contains(@content-desc,"Edit") or contains(@content-desc,"pencil") or contains(@content-desc,"Pencil")]',
            '//*[contains(@resource-id,"dob") or contains(@resource-id,"birth") or contains(@resource-id,"date")]',
            '//android.widget.ImageButton[@clickable="true"]',
            '//android.widget.ImageView[@clickable="true"]',
        ):
            try:
                els = driver.find_elements("xpath", xp)
            except Exception:
                els = []
            for el in els[:8]:
                try:
                    el.click()
                    return True
                except Exception:
                    continue
        # 3) Any EditText showing placeholder
        try:
            for el in driver.find_elements("class name", "android.widget.EditText"):
                t = (el.text or el.get_attribute("text") or el.get_attribute("hint") or "")
                if "DD/MM" in t or "birth" in t.lower() or not str(t).strip():
                    try:
                        el.click()
                        return True
                    except Exception:
                        continue
        except Exception:
            pass
        return False

    def _clear_dob_input(self) -> None:
        driver = self.driver
        # Prefer focused/visible EditText
        try:
            fields = driver.find_elements("class name", "android.widget.EditText")
        except Exception:
            fields = []
        for el in fields or []:
            try:
                el.click()
            except Exception:
                pass
            try:
                el.clear()
            except Exception:
                pass
            # select-all + delete via adb as fallback
            try:
                import subprocess
                subprocess.run(["adb", "shell", "input", "keyevent", "KEYCODE_MOVE_END"], check=False)
                for _ in range(12):
                    subprocess.run(["adb", "shell", "input", "keyevent", "KEYCODE_DEL"], check=False)
            except Exception:
                pass
            break

    def _type_dob_digits(self, digits: str) -> None:
        driver = self.driver
        typed = False
        try:
            fields = driver.find_elements("class name", "android.widget.EditText")
        except Exception:
            fields = []
        if fields:
            el = fields[0]
            try:
                el.click()
                el.send_keys(digits)
                typed = True
            except Exception:
                typed = False
        if not typed and hasattr(self, "_adb_type"):
            self._adb_type(digits)
            typed = True
        if not typed:
            import subprocess
            subprocess.run(["adb", "shell", "input", "text", digits], check=False)

    def _confirm_dob_picker(self) -> None:
        # Common Android date-picker / dialog confirms
        if self._tap_by_texts(("OK", "Ok", "Done", "SET", "Set", "Confirm", "Save")):
            return
        # Material positive button
        for xp in (
            '//*[@resource-id="android:id/button1"]',
            '//android.widget.Button[contains(@text,"OK") or contains(@text,"Ok") or contains(@text,"Done")]',
        ):
            try:
                self.driver.find_element("xpath", xp).click()
                return
            except Exception:
                continue

    def _dob_value_on_screen(self) -> str:
        driver = self.driver
        try:
            for el in driver.find_elements("class name", "android.widget.EditText"):
                t = (el.text or el.get_attribute("text") or "").strip()
                if t and "DD/MM" not in t:
                    return t
        except Exception:
            pass
        try:
            # sometimes shown as TextView after set
            for el in driver.find_elements("xpath", '//*[contains(@text,"/") and string-length(@text)>=8 and string-length(@text)<=10]'):
                t = (el.text or "").strip()
                if t and "DD/MM" not in t:
                    return t
        except Exception:
            pass
        return ""

    def pick_dob(self, value=None, *args, **kwargs):
        """Pencil/field -> clear -> type DDMMYYYY -> OK. Returns self (never bool)."""
        digits = self._dob_digits(value, *args, **kwargs)
        self._open_dob_editor()
        self._clear_dob_input()
        self._type_dob_digits(digits)
        self._confirm_dob_picker()
        # If still empty, one more hard attempt via adb only
        if not self._dob_value_on_screen():
            self._open_dob_editor()
            self._clear_dob_input()
            if hasattr(self, "_adb_type"):
                self._adb_type(digits)
            else:
                import subprocess
                subprocess.run(["adb", "shell", "input", "text", digits], check=False)
            self._confirm_dob_picker()
        return self

    def enter_dob(self, value=None, *args, **kwargs):
        return self.pick_dob(value, *args, **kwargs)

    def enter_date_of_birth(self, value=None, *args, **kwargs):
        return self.pick_dob(value, *args, **kwargs)

    def set_dob(self, value=None, *args, **kwargs):
        return self.pick_dob(value, *args, **kwargs)
'''


def _strip_old_dob_methods(src: str) -> str:
    """Remove previously generated weak DOB methods so our new ones win cleanly."""
    names = ("pick_dob", "enter_dob", "enter_date_of_birth", "set_dob", "_dob_digits", "_open_dob_editor", "_clear_dob_input", "_type_dob_digits", "_confirm_dob_picker", "_dob_value_on_screen", "_tap_by_texts")
    for name in names:
        # only strip blocks we previously generated (SAFE / ALL / DOB markers nearby) — safer: strip ALL defs of these names at class indent
        src = re.sub(
            rf"\n    def {name}\([\s\S]*?(?=\n    def |\nclass |\Z)",
            "\n",
            src,
            count=1,
        )
        # may appear more than once after repeated patches
        while re.search(rf"\n    def {name}\(", src):
            src = re.sub(
                rf"\n    def {name}\([\s\S]*?(?=\n    def |\nclass |\Z)",
                "\n",
                src,
                count=1,
            )
    # also remove old KSKIN_DOB block marker comments leftovers
    return src


def _try_copy_from_full_regression() -> str | None:
    if not OTHER.is_file():
        return None
    src = OTHER.read_text(encoding="utf-8", errors="ignore")
    for name in ("pick_dob", "enter_dob", "enter_date_of_birth", "set_date_of_birth", "set_dob"):
        m = re.search(
            rf"(^\s{{4}}def {name}\([\s\S]*?)(?=^\s{{4}}def |\Z)",
            src,
            flags=re.M,
        )
        if m:
            print(f"Also found donor method in full_regression: {name}")
    return None  # we use our dedicated picker impl which matches the report step text


def main() -> int:
    if not PAGE.is_file():
        print(f"ERROR: missing {PAGE}")
        return 1

    bak = PAGE.with_suffix(PAGE.suffix + f".bak_dob_{int(time.time())}")
    shutil.copy2(PAGE, bak)
    print(f"Backup: {bak}")

    _try_copy_from_full_regression()

    src = PAGE.read_text(encoding="utf-8", errors="ignore")
    if MARKER in src:
        # replace existing fix block
        src = re.sub(
            rf"\n    # --- {MARKER} ---[\s\S]*?(?=\n    # --- |\Z)",
            "\n",
            src,
        )
    src = _strip_old_dob_methods(src)
    src = src.rstrip() + "\n" + DOB_BLOCK
    if not src.endswith("\n"):
        src += "\n"
    PAGE.write_text(src, encoding="utf-8")
    print(f"Wrote DOB picker helpers → {PAGE}")

    for must in ("pick_dob", "enter_dob", "enter_date_of_birth", "_open_dob_editor"):
        ok = f"def {must}(" in PAGE.read_text(encoding="utf-8")
        print(f"  def {must}:", "YES" if ok else "NO")

    print("Done. Re-run run-android-signup-login.command")
    print("Watch DOB field: should show 11/04/1998 (not DD/MM/YYYY) before Create Account.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
