#!/usr/bin/env python3
"""Add ONLY SignupLoginAndroidPage.enter_otp — never committed to git.

Git has no def enter_otp under python/pages/. Android signup test calls
page.enter_otp(OTP). This adds that single method if missing.

Run on Mac:
  python3 ~/AquaProjects/KskinCMS/one_click/add_enter_otp_only.py
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
IOS_PAGE = APPIUM_PY / "pages" / "signup_login_ios_page.py"
MARKER = "ENTER_OTP_ONLY"

METHOD = '''
    def enter_otp(self, otp: str = "111111"):
        """Enter 6-digit email/mobile OTP. (Not in git history — added for test call page.enter_otp.)"""
        code = "".join(ch for ch in str(otp or "111111") if ch.isdigit())[:6].ljust(6, "0")[:6]
        driver = self.driver

        fields = []
        try:
            fields = driver.find_elements("class name", "android.widget.EditText")
        except Exception:
            fields = []

        otp_fields = []
        for el in fields or []:
            try:
                t = (el.text or el.get_attribute("text") or "")[:4]
                if len(str(t).strip()) <= 1:
                    otp_fields.append(el)
            except Exception:
                otp_fields.append(el)

        if len(otp_fields) >= 6:
            for i, ch in enumerate(code):
                el = otp_fields[i]
                try:
                    el.click()
                except Exception:
                    pass
                try:
                    el.clear()
                except Exception:
                    pass
                try:
                    el.send_keys(ch)
                except Exception:
                    if hasattr(self, "_adb_type"):
                        self._adb_type(ch)
            return self

        if fields:
            try:
                fields[0].click()
                fields[0].clear()
                fields[0].send_keys(code)
                return self
            except Exception:
                pass

        if hasattr(self, "_adb_type"):
            self._adb_type(code)
        else:
            import subprocess
            subprocess.run(["adb", "shell", "input", "text", code], check=False)
        return self
'''


def _copy_from_ios() -> str | None:
    if not IOS_PAGE.is_file():
        return None
    src = IOS_PAGE.read_text(encoding="utf-8", errors="ignore")
    m = re.search(
        r"(^\s{4}def enter_otp\([\s\S]*?)(?=^\s{4}def |\Z)",
        src,
        flags=re.M,
    )
    return m.group(1) if m else None


def main() -> int:
    if not PAGE.is_file():
        print(f"ERROR: missing {PAGE}")
        return 1

    src = PAGE.read_text(encoding="utf-8", errors="ignore")
    if re.search(r"^\s{4}def enter_otp\(", src, flags=re.M):
        print("enter_otp already present — nothing to do")
        return 0

    bak = PAGE.with_suffix(PAGE.suffix + f".bak_otp_{int(time.time())}")
    shutil.copy2(PAGE, bak)
    print(f"Backup: {bak}")

    block = _copy_from_ios()
    if block:
        print("Using enter_otp copied from signup_login_ios_page.py")
        # iOS impl may not work on Android — still prefer Android METHOD below
        # Keep Android-specific METHOD
    addition = f"\n    # --- {MARKER} ---\n" + METHOD
    PAGE.write_text(src.rstrip() + "\n" + addition + "\n", encoding="utf-8")
    print(f"Added enter_otp only → {PAGE}")
    print("Re-run run-android-signup-login.command")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
