#!/usr/bin/env python3
"""Rebuild helpers/dynamic_data.py so attributes match signup tests.

The test uses run.signup_email etc. Our earlier stub only had .email → AttributeError.

Run on Mac (overwrites stub):
  FORCE=1 python3 ~/AquaProjects/KskinCMS/one_click/generate_dynamic_data.py
"""
from __future__ import annotations

import os
import random
import re
import time
from pathlib import Path

AQUA = Path(os.environ.get("AQUA_ROOT", Path.home() / "AquaProjects"))
APPIUM_PY = Path(os.environ.get("APPIUM_PY", AQUA / "MCP_Appium_Server" / "python"))
HELPERS = APPIUM_PY / "helpers"
TARGET = HELPERS / "dynamic_data.py"
FORCE = os.environ.get("FORCE", "").strip() in {"1", "true", "yes"}

TESTS = [
    APPIUM_PY / "tests" / "test_signup_login_android.py",
    APPIUM_PY / "tests" / "test_signup_login_ios.py",
]


def _stamp() -> str:
    return time.strftime("%y%m%d%H%M%S") + f"{random.randint(10, 99)}"


def _attrs_from_tests() -> set[str]:
    attrs: set[str] = set()
    for path in TESTS:
        if not path.is_file():
            continue
        src = path.read_text(encoding="utf-8", errors="ignore")
        # run.signup_email / values.email / data["signup_email"]
        for m in re.finditer(r"\b(?:run|values|data|creds|user)\.([A-Za-z_][A-Za-z0-9_]*)", src):
            attrs.add(m.group(1))
        for m in re.finditer(
            r"\b(?:run|values|data|creds|user)\[\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]\s*\]",
            src,
        ):
            attrs.add(m.group(1))
        # also getattr(run, "signup_email")
        for m in re.finditer(
            r"getattr\(\s*(?:run|values|data)\s*,\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]",
            src,
        ):
            attrs.add(m.group(1))
    # drop obvious non-fields
    ignore = {
        "get",
        "items",
        "keys",
        "values",
        "copy",
        "update",
        "pop",
        "driver",
        "page",
    }
    return {a for a in attrs if a not in ignore and not a.startswith("_")}


def _bag_dict(platform: str, attrs: set[str]) -> dict:
    s = _stamp()
    mobile = "9" + "".join(str(random.randint(0, 9)) for _ in range(7))
    email = f"qa.{platform}.{s}@yopmail.com"
    password = "P@ssw0rd"
    first = "QA"
    last = f"{platform.title()}{s[-4:]}"
    full = f"{first} {last}"
    otp = "111111"
    dob = "01/01/1995"
    gender = "Female"

    # Core + every alias the suites tend to use
    base = {
        "email": email,
        "signup_email": email,
        "login_email": email,
        "user_email": email,
        "password": password,
        "signup_password": password,
        "login_password": password,
        "user_password": password,
        "first_name": first,
        "signup_first_name": first,
        "last_name": last,
        "signup_last_name": last,
        "full_name": full,
        "name": full,
        "signup_name": full,
        "mobile": mobile,
        "phone": mobile,
        "mobile_number": mobile,
        "signup_mobile": mobile,
        "signup_phone": mobile,
        "otp": otp,
        "email_otp": otp,
        "mobile_otp": otp,
        "sms_otp": otp,
        "signup_otp": otp,
        "gender": gender,
        "signup_gender": gender,
        "dob": dob,
        "date_of_birth": dob,
        "signup_dob": dob,
        "signup_date_of_birth": dob,
        "platform": platform,
        "run_id": s,
        "stamp": s,
    }

    # Ensure every attr seen in tests exists (string fallback)
    for a in attrs:
        if a not in base:
            al = a.lower()
            if "email" in al:
                base[a] = email
            elif "pass" in al:
                base[a] = password
            elif "otp" in al:
                base[a] = otp
            elif "mobile" in al or "phone" in al:
                base[a] = mobile
            elif "first" in al:
                base[a] = first
            elif "last" in al:
                base[a] = last
            elif "name" in al:
                base[a] = full
            elif "gender" in al:
                base[a] = gender
            elif "dob" in al or "birth" in al:
                base[a] = dob
            else:
                base[a] = f"qa-{a}-{s}"
    return base


def main() -> int:
    HELPERS.mkdir(parents=True, exist_ok=True)
    (HELPERS / "__init__.py").touch(exist_ok=True)

    attrs = _attrs_from_tests()
    print("Attrs from tests:", sorted(attrs) or "(none — using defaults)")

    if TARGET.exists() and not FORCE:
        # Upgrade in place if signup_email missing
        src = TARGET.read_text(encoding="utf-8", errors="ignore")
        if "signup_email" in src and "next_android_run_values" in src:
            print(f"OK already has signup_email: {TARGET}")
            print("Re-run with FORCE=1 to regenerate from tests.")
            return 0

    code = '''"""Auto-generated dynamic per-run signup values (compat stub).

Regenerated to include signup_email / signup_password aliases expected by
test_signup_login_*.py. Replace with original helpers/dynamic_data.py when recovered.
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
    email = f"qa.{platform}.{s}@yopmail.com"
    password = "P@ssw0rd"
    first = "QA"
    last = f"{platform.title()}{s[-4:]}"
    full = f"{first} {last}"
    otp = "111111"
    dob = "01/01/1995"
    gender = "Female"
    data = {
'''
    # embed a representative bag including discovered attrs
    sample = _bag_dict("android", attrs)
    for k in sorted(sample):
        # write as Python literals using the variable names where possible
        if k in {
            "email",
            "signup_email",
            "login_email",
            "user_email",
        }:
            code += f'        "{k}": email,\n'
        elif k in {
            "password",
            "signup_password",
            "login_password",
            "user_password",
        }:
            code += f'        "{k}": password,\n'
        elif k in {"first_name", "signup_first_name"}:
            code += f'        "{k}": first,\n'
        elif k in {"last_name", "signup_last_name"}:
            code += f'        "{k}": last,\n'
        elif k in {"full_name", "name", "signup_name"}:
            code += f'        "{k}": full,\n'
        elif k in {
            "mobile",
            "phone",
            "mobile_number",
            "signup_mobile",
            "signup_phone",
        }:
            code += f'        "{k}": mobile,\n'
        elif k in {"otp", "email_otp", "mobile_otp", "sms_otp", "signup_otp"}:
            code += f'        "{k}": otp,\n'
        elif k in {"gender", "signup_gender"}:
            code += f'        "{k}": gender,\n'
        elif k in {"dob", "date_of_birth", "signup_dob", "signup_date_of_birth"}:
            code += f'        "{k}": dob,\n'
        elif k == "platform":
            code += f'        "{k}": platform,\n'
        elif k in {"run_id", "stamp"}:
            code += f'        "{k}": s,\n'
        else:
            # keep discovered extras as computed strings
            val = sample[k]
            code += f'        "{k}": {val!r} if False else '  # noqa — force pattern
            # simpler: always use runtime heuristic
            code = code.rsplit(f'        "{k}":', 1)[0]
            al = k.lower()
            if "email" in al:
                code += f'        "{k}": email,\n'
            elif "pass" in al:
                code += f'        "{k}": password,\n'
            elif "otp" in al:
                code += f'        "{k}": otp,\n'
            elif "mobile" in al or "phone" in al:
                code += f'        "{k}": mobile,\n'
            elif "first" in al:
                code += f'        "{k}": first,\n'
            elif "last" in al:
                code += f'        "{k}": last,\n'
            elif "name" in al:
                code += f'        "{k}": full,\n'
            elif "gender" in al:
                code += f'        "{k}": gender,\n'
            elif "dob" in al or "birth" in al:
                code += f'        "{k}": dob,\n'
            else:
                code += f'        "{k}": f"qa-{k}-{{s}}",\n'

    code += '''    }
    return SimpleNamespace(**data)


def next_android_run_values():
    return _bag("android")


def next_ios_run_values():
    return _bag("ios")


def get_android_run_values():
    return next_android_run_values()


def get_ios_run_values():
    return next_ios_run_values()
'''

    TARGET.write_text(code, encoding="utf-8")
    print(f"Wrote {TARGET}")

    import sys

    sys.path.insert(0, str(APPIUM_PY))
    # clear cached module
    sys.modules.pop("helpers.dynamic_data", None)
    sys.modules.pop("helpers", None)
    from helpers.dynamic_data import next_android_run_values  # noqa: WPS433

    v = next_android_run_values()
    print("IMPORT OK signup_email:", getattr(v, "signup_email", None))
    print("IMPORT OK email:", getattr(v, "email", None))
    missing = [a for a in sorted(attrs) if not hasattr(v, a)]
    if missing:
        print("WARNING still missing:", missing)
    else:
        print("All discovered attrs present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
