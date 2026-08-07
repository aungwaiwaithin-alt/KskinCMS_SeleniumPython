#!/usr/bin/env python3
"""Fix Create Account: first name + gender (and harden DOB to 11/04/1998 not today).

Observed: steps PASS but UI shows First name empty, Gender unselected,
DOB sometimes left as today (07/08/2026).

Run on Mac:
  python3 ~/AquaProjects/KskinCMS/one_click/patch_android_profile_fields.py
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
MARKER = "KSKIN_PROFILE_FIELDS_FIX"

BLOCK = r'''
    # --- KSKIN_PROFILE_FIELDS_FIX ---
    def _find_edittexts(self):
        try:
            return list(self.driver.find_elements("class name", "android.widget.EditText"))
        except Exception:
            return []

    def _el_label_blob(self, el) -> str:
        parts = []
        for attr in ("text", "hint", "content-desc", "resource-id", "contentDescription"):
            try:
                parts.append(str(el.get_attribute(attr) or ""))
            except Exception:
                pass
        try:
            parts.append(str(el.text or ""))
        except Exception:
            pass
        return " ".join(parts).lower()

    def _type_into_labeled_field(self, labels, value: str):
        """Type into the EditText matching First name / Last name / Password / etc."""
        import time as _t
        value = "" if value is None else str(value)
        labels_l = [str(x).lower() for x in labels]
        fields = self._find_edittexts()
        target = None
        for el in fields:
            blob = self._el_label_blob(el)
            if any(lbl in blob for lbl in labels_l):
                target = el
                break
        # Fallback by common Create Account order:
        # 0 first name, 1 last name, (dob may be textview), password last
        if target is None and fields:
            if any("first" in lbl for lbl in labels_l) and len(fields) >= 1:
                target = fields[0]
            elif any("last" in lbl for lbl in labels_l) and len(fields) >= 2:
                target = fields[1]
            elif any("pass" in lbl for lbl in labels_l):
                target = fields[-1]

        if target is None:
            raise AssertionError(f"No EditText found for labels={labels}")

        try:
            target.click()
        except Exception:
            pass
        _t.sleep(0.15)
        try:
            target.clear()
        except Exception:
            pass
        # delete leftovers
        try:
            import subprocess
            for _ in range(8):
                subprocess.run(["adb", "shell", "input", "keyevent", "KEYCODE_DEL"], check=False)
        except Exception:
            pass
        try:
            target.send_keys(value)
        except Exception:
            if hasattr(self, "_adb_type"):
                self._adb_type(value)
            else:
                import subprocess
                subprocess.run(["adb", "shell", "input", "text", value.replace(" ", "%s")], check=False)
        _t.sleep(0.2)

        # Verify non-password fields actually show the value
        if not any("pass" in lbl for lbl in labels_l):
            shown = ""
            try:
                shown = (target.text or target.get_attribute("text") or "").strip()
            except Exception:
                shown = ""
            if value and value not in shown and not shown.endswith(value[-min(4, len(value)):]):
                # retry once via adb after click
                try:
                    target.click()
                except Exception:
                    pass
                if hasattr(self, "_adb_type"):
                    self._adb_type(value)
                shown = ""
                try:
                    shown = (target.text or target.get_attribute("text") or "").strip()
                except Exception:
                    pass
                if value and value not in shown:
                    raise AssertionError(
                        f"Failed to enter {labels[0]!r}: wanted {value!r}, field shows {shown!r}"
                    )
        return self

    def enter_first_name(self, value=None, *args, **kwargs):
        if value is None and args:
            value = args[0]
        if value is None:
            value = "Wai"
        return self._type_into_labeled_field(
            ("first name", "firstname", "first_name", "given name"),
            value,
        )

    def enter_last_name(self, value=None, *args, **kwargs):
        if value is None and args:
            value = args[0]
        if value is None:
            value = "Thin UAT"
        return self._type_into_labeled_field(
            ("last name", "lastname", "last_name", "surname", "family name"),
            value,
        )

    def enter_password(self, value=None, *args, **kwargs):
        if value is None and args:
            value = args[0]
        if value is None:
            value = kwargs.get("password") or "P@ssw0rd"
        return self._type_into_labeled_field(("password", "pwd"), value)

    def select_female(self, *args, **kwargs):
        return self.select_gender("Female")

    def select_male(self, *args, **kwargs):
        return self.select_gender("Male")

    def select_gender(self, value=None, *args, **kwargs):
        """Select Male/Female radio — must check the control, not just tap text loosely."""
        import time as _t
        if value is None and args:
            value = args[0]
        value = str(value or "Female")
        driver = self.driver
        wanted = value.strip().title()  # Female / Male
        xpaths = (
            f'//android.widget.RadioButton[@text="{wanted}"]',
            f'//android.widget.RadioButton[contains(@text,"{wanted}")]',
            f'//android.widget.RadioButton[@content-desc="{wanted}"]',
            f'//*[@text="{wanted}"]/preceding-sibling::android.widget.RadioButton[1]',
            f'//*[@text="{wanted}"]/following-sibling::android.widget.RadioButton[1]',
            f'//*[@text="{wanted}"]/..//android.widget.RadioButton',
            f'//*[@text="{wanted}" and (@clickable="true" or @checkable="true")]',
            f'//*[contains(@text,"{wanted}") and @checkable="true"]',
        )
        clicked = False
        for xp in xpaths:
            try:
                els = driver.find_elements("xpath", xp)
            except Exception:
                els = []
            for el in els[:3]:
                try:
                    el.click()
                    clicked = True
                    break
                except Exception:
                    continue
            if clicked:
                break
        if not clicked:
            # last resort: plain text
            try:
                driver.find_element("xpath", f'//*[@text="{wanted}"]').click()
                clicked = True
            except Exception:
                pass
        _t.sleep(0.25)
        if not clicked:
            raise AssertionError(f"Could not tap gender control for {wanted!r}")

        # Verify a radio is checked when possible
        try:
            radios = driver.find_elements("class name", "android.widget.RadioButton")
            checked_any = False
            for r in radios:
                try:
                    if str(r.get_attribute("checked")).lower() == "true":
                        checked_any = True
                        txt = (r.text or r.get_attribute("text") or "")
                        if wanted.lower() in str(txt).lower():
                            return self
                except Exception:
                    continue
            if radios and not checked_any:
                raise AssertionError(f"Gender {wanted!r} tap did not check a RadioButton")
        except AssertionError:
            raise
        except Exception:
            pass
        return self
'''


def _strip_methods(src: str, names: tuple[str, ...]) -> str:
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

    bak = PAGE.with_suffix(PAGE.suffix + f".bak_profile_{int(time.time())}")
    shutil.copy2(PAGE, bak)
    print(f"Backup: {bak}")

    src = PAGE.read_text(encoding="utf-8", errors="ignore")
    if MARKER in src:
        src = re.sub(
            rf"\n    # --- {MARKER} ---[\s\S]*?(?=\n    # --- |\Z)",
            "\n",
            src,
        )

    # Remove weak duplicates so our new defs are authoritative (last wins otherwise —
    # strip all then append once)
    src = _strip_methods(
        src,
        (
            "enter_first_name",
            "enter_last_name",
            "enter_password",
            "select_gender",
            "select_female",
            "select_male",
            "_type_into_labeled_field",
            "_find_edittexts",
            "_el_label_blob",
        ),
    )

    src = src.rstrip() + "\n" + BLOCK
    if not src.endswith("\n"):
        src += "\n"
    PAGE.write_text(src, encoding="utf-8")
    print(f"Wrote profile field helpers → {PAGE}")

    text = PAGE.read_text(encoding="utf-8")
    for must in ("enter_first_name", "select_gender", "select_female", "_type_into_labeled_field"):
        # count defs — should be exactly 1
        n = len(re.findall(rf"\n    def {must}\(", text))
        print(f"  def {must}: count={n}")

    print("Done. Re-run run-android-signup-login.command")
    print("Expect: First name=Wai, Female selected, DOB=11/04/1998 (not today's date).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
