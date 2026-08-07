#!/usr/bin/env python3
"""Create a minimal helpers/dynamic_data.py by inspecting signup tests on disk.

Run on Mac:
  python3 ~/AquaProjects/KskinCMS/one_click/generate_dynamic_data.py
"""
from __future__ import annotations

import ast
import os
import random
import re
import time
from pathlib import Path

AQUA = Path(os.environ.get("AQUA_ROOT", Path.home() / "AquaProjects"))
APPIUM_PY = Path(os.environ.get("APPIUM_PY", AQUA / "MCP_Appium_Server" / "python"))
HELPERS = APPIUM_PY / "helpers"
TESTS = [
    APPIUM_PY / "tests" / "test_signup_login_android.py",
    APPIUM_PY / "tests" / "test_signup_login_ios.py",
]


def _stamp() -> str:
    return time.strftime("%y%m%d%H%M%S") + f"{random.randint(10, 99)}"


def _default_bag(platform: str) -> dict:
    s = _stamp()
    # SG-like mobile; suites often accept 8/9-digit local numbers
    mobile = "9" + "".join(str(random.randint(0, 9)) for _ in range(7))
    return {
        "email": f"qa.{platform}.{s}@yopmail.com",
        "password": "P@ssw0rd",
        "first_name": "QA",
        "last_name": f"{platform.title()}{s[-4:]}",
        "full_name": f"QA {platform.title()}{s[-4:]}",
        "mobile": mobile,
        "phone": mobile,
        "otp": "111111",
        "gender": "Female",
        "dob": "01/01/1995",
        "date_of_birth": "01/01/1995",
    }


def _attrs_used(test_path: Path, func_name: str) -> set[str]:
    """Find values.x / values['x'] usages after next_*_run_values()."""
    if not test_path.is_file():
        return set()
    src = test_path.read_text(encoding="utf-8", errors="ignore")
    attrs: set[str] = set()
    # values = next_android_run_values() then values.email / values["email"]
    for m in re.finditer(r"\bvalues\.([A-Za-z_][A-Za-z0-9_]*)", src):
        attrs.add(m.group(1))
    for m in re.finditer(r"\bvalues\[\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]\s*\]", src):
        attrs.add(m.group(1))
    # also direct unpacking patterns
    for m in re.finditer(
        rf"{func_name}\(\)[^\n]*\n(?:.*\n){{0,30}}?", src
    ):
        pass
    # import line confirmation
    if func_name not in src:
        return attrs
    return attrs


def main() -> int:
    HELPERS.mkdir(parents=True, exist_ok=True)
    init = HELPERS / "__init__.py"
    if not init.exists():
        init.write_text("", encoding="utf-8")

    target = HELPERS / "dynamic_data.py"
    if target.exists():
        print(f"OK already exists: {target}")
        return 0

    and_attrs = _attrs_used(TESTS[0], "next_android_run_values")
    ios_attrs = _attrs_used(TESTS[1], "next_ios_run_values")
    print("Android attrs guessed:", sorted(and_attrs) or "(none — using defaults)")
    print("iOS attrs guessed:", sorted(ios_attrs) or "(none — using defaults)")

    # Always include a broad default set so missing keys don't break immediately
    code = '''"""Auto-generated dynamic per-run signup values (restore stub).

Generated because helpers/dynamic_data.py was missing from MCP_Appium_Server.
Replace with your original module from backup/zip when available.
"""
from __future__ import annotations

import random
import time
from types import SimpleNamespace


def _stamp() -> str:
    return time.strftime("%y%m%d%H%M%S") + f"{random.randint(10, 99)}"


def _bag(platform: str) -> SimpleNamespace:
    s = _stamp()
    mobile = "9" + "".join(str(random.randint(0, 9)) for _ in range(7))
    data = {
        "email": f"qa.{platform}.{s}@yopmail.com",
        "password": "P@ssw0rd",
        "first_name": "QA",
        "last_name": f"{platform.title()}{s[-4:]}",
        "full_name": f"QA {platform.title()}{s[-4:]}",
        "name": f"QA {platform.title()}{s[-4:]}",
        "mobile": mobile,
        "phone": mobile,
        "mobile_number": mobile,
        "otp": "111111",
        "gender": "Female",
        "dob": "01/01/1995",
        "date_of_birth": "01/01/1995",
        "platform": platform,
        "run_id": s,
    }
    return SimpleNamespace(**data)


def next_android_run_values():
    return _bag("android")


def next_ios_run_values():
    return _bag("ios")


# aliases some suites use
def get_android_run_values():
    return next_android_run_values()


def get_ios_run_values():
    return next_ios_run_values()
'''
    target.write_text(code, encoding="utf-8")
    print(f"Wrote {target}")

    # verify import
    import sys

    sys.path.insert(0, str(APPIUM_PY))
    import helpers.dynamic_data as d  # noqa: WPS433

    v = d.next_android_run_values()
    print("IMPORT OK android email:", getattr(v, "email", v))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
