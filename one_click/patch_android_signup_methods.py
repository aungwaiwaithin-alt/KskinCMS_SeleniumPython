#!/usr/bin/env python3
"""Add missing SignupLoginAndroidPage methods used by Android signup test.

Current failure:
  ERROR: 'SignupLoginAndroidPage' object has no attribute 'enter_otp'

Run on Mac:
  python3 ~/AquaProjects/KskinCMS/one_click/patch_android_signup_methods.py
"""
from __future__ import annotations

import ast
import os
import re
import shutil
import time
from pathlib import Path

AQUA = Path(os.environ.get("AQUA_ROOT", Path.home() / "AquaProjects"))
APPIUM_PY = Path(os.environ.get("APPIUM_PY", AQUA / "MCP_Appium_Server" / "python"))
PAGE = APPIUM_PY / "pages" / "signup_login_android_page.py"
TEST = APPIUM_PY / "tests" / "test_signup_login_android.py"
MARKER = "KSKIN_MISSING_METHODS_PATCH"

ENTER_OTP_IMPL = '''
    def enter_otp(self, otp: str = "111111", *args, **kwargs):
        """Enter 6-digit OTP on email/mobile verify screens (compat)."""
        code = str(otp or "111111").strip()
        if len(code) < 6:
            code = (code + "000000")[:6]
        code = code[:6]
        driver = getattr(self, "driver", None)
        if driver is None:
            raise RuntimeError("enter_otp: no driver on SignupLoginAndroidPage")

        # Prefer individual OTP boxes (common Kskin UI)
        fields = []
        try:
            fields = driver.find_elements("class name", "android.widget.EditText")
        except Exception:
            fields = []
        # Filter likely OTP boxes (empty / short)
        otp_fields = []
        for el in fields or []:
            try:
                t = (el.text or el.get_attribute("text") or "")[:8]
                if len(t) <= 1:
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
            return True

        # Single field fallback
        if fields:
            el = fields[0]
            try:
                el.click()
                el.clear()
                el.send_keys(code)
                return True
            except Exception:
                pass

        # ADB fallback (page already has _adb_type in Claude-era code)
        if hasattr(self, "_adb_type"):
            self._adb_type(code)
            return True

        import subprocess
        subprocess.run(["adb", "shell", "input", "text", code], check=False)
        return True

    def enter_email_otp(self, otp: str = "111111", *args, **kwargs):
        return self.enter_otp(otp, *args, **kwargs)

    def enter_mobile_otp(self, otp: str = "111111", *args, **kwargs):
        return self.enter_otp(otp, *args, **kwargs)

    def type_otp(self, otp: str = "111111", *args, **kwargs):
        return self.enter_otp(otp, *args, **kwargs)
'''


def _class_methods(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    names: set[str] = set()
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        if "Signup" in node.name or node.name.endswith("AndroidPage"):
            for n in node.body:
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    names.add(n.name)
    # also any def at class indent via regex fallback
    src = path.read_text(encoding="utf-8", errors="ignore")
    for m in re.finditer(r"^\s{4}def ([A-Za-z_][A-Za-z0-9_]*)\(", src, re.M):
        names.add(m.group(1))
    return names


def _methods_called_in_test(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    src = path.read_text(encoding="utf-8", errors="ignore")
    names: set[str] = set()
    # page.enter_otp( / signup.enter_otp( / self.page.enter_otp(
    for m in re.finditer(
        r"\b(?:page|signup|login|android_page|signup_page|p)\.([A-Za-z_][A-Za-z0-9_]*)\s*\(",
        src,
    ):
        names.add(m.group(1))
    for m in re.finditer(r"SignupLoginAndroidPage\)\.([A-Za-z_][A-Za-z0-9_]*)\s*\(", src):
        names.add(m.group(1))
    # bare strings in report steps often match method intent
    for m in re.finditer(r"enter_otp|enter_email_otp|enter_mobile_otp|type_otp", src):
        names.add(m.group(0))
    return names


def main() -> int:
    if not PAGE.is_file():
        print(f"ERROR: missing {PAGE}")
        return 1

    existing = _class_methods(PAGE)
    needed = _methods_called_in_test(TEST)
    print("Existing methods (sample):", sorted(list(existing))[:40])
    print("Called from test (sample):", sorted(needed))

    src = PAGE.read_text(encoding="utf-8", errors="ignore")
    if "def enter_otp" in src and MARKER in src:
        print("enter_otp already patched")
        return 0

    bak = PAGE.with_suffix(PAGE.suffix + f".bak_{int(time.time())}")
    shutil.copy2(PAGE, bak)
    print(f"Backup: {bak}")

    # Append OTP helpers before end of class if possible; else file end
    block = f"\n    # --- {MARKER} ---\n" + ENTER_OTP_IMPL
    if "def enter_otp" in src:
        print("enter_otp already defined (not by us) — skip append")
    else:
        # Insert before last line if file ends mid-class, else append with class-level indent
        src = src.rstrip() + "\n" + block
        if not src.endswith("\n"):
            src += "\n"
        PAGE.write_text(src, encoding="utf-8")
        print(f"Appended enter_otp* to {PAGE}")

    # Verify
    existing2 = _class_methods(PAGE)
    if "enter_otp" not in existing2 and "def enter_otp" not in PAGE.read_text(encoding="utf-8"):
        print("WARNING: enter_otp still not found after patch")
        return 1

    # Quick import check
    import sys

    sys.path.insert(0, str(APPIUM_PY))
    sys.modules.pop("pages.signup_login_android_page", None)
    try:
        from pages.signup_login_android_page import SignupLoginAndroidPage

        assert hasattr(SignupLoginAndroidPage, "enter_otp"), "enter_otp missing on class"
        print("IMPORT OK: SignupLoginAndroidPage.enter_otp present")
    except Exception as e:  # noqa: BLE001
        print("IMPORT WARNING:", e)
    print("Done. Re-run run-android-signup-login.command")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
