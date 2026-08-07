#!/usr/bin/env python3
"""Add signup_* aliases to an EXISTING helpers/dynamic_data.py without changing email format.

Does NOT rewrite stamp/email generation. Safe to run on Claude originals.
"""
from __future__ import annotations

import ast
import os
import re
from pathlib import Path

AQUA = Path(os.environ.get("AQUA_ROOT", Path.home() / "AquaProjects"))
APPIUM_PY = Path(os.environ.get("APPIUM_PY", AQUA / "MCP_Appium_Server" / "python"))
TARGET = APPIUM_PY / "helpers" / "dynamic_data.py"

ALIASES = {
    "signup_email": "email",
    "login_email": "email",
    "user_email": "email",
    "signup_password": "password",
    "login_password": "password",
    "user_password": "password",
    "signup_mobile": "mobile",
    "signup_phone": "mobile",
    "phone": "mobile",
    "mobile_number": "mobile",
    "signup_otp": "otp",
    "email_otp": "otp",
    "mobile_otp": "otp",
    "sms_otp": "otp",
    "signup_first_name": "first_name",
    "signup_last_name": "last_name",
    "signup_name": "full_name",
    "name": "full_name",
    "signup_gender": "gender",
    "signup_dob": "dob",
    "date_of_birth": "dob",
    "signup_date_of_birth": "dob",
}

WRAPPER = '''

def _with_signup_aliases(ns):
    """Thin aliases for test attribute names — does not change email generation."""
    try:
        data = dict(vars(ns))
    except TypeError:
        return ns
    # Map aliases only when target exists and alias missing
    pairs = {
        "signup_email": ("email", "signup_email", "user_email", "login_email"),
        "signup_password": ("password", "signup_password", "login_password"),
        "signup_mobile": ("mobile", "phone", "mobile_number", "signup_phone"),
        "signup_otp": ("otp", "email_otp", "mobile_otp", "sms_otp"),
        "signup_first_name": ("first_name", "signup_first_name"),
        "signup_last_name": ("last_name", "signup_last_name"),
        "signup_name": ("full_name", "name", "signup_name"),
        "signup_gender": ("gender", "signup_gender"),
        "signup_dob": ("dob", "date_of_birth", "signup_dob", "signup_date_of_birth"),
    }
    for canon, keys in pairs.items():
        val = None
        for k in keys:
            if k in data and data[k] not in (None, ""):
                val = data[k]
                break
        if val is None:
            continue
        for k in keys:
            data.setdefault(k, val)
        data.setdefault(canon, val)
    from types import SimpleNamespace
    return SimpleNamespace(**data)
'''


def _has_signup_email(src: str) -> bool:
    return bool(re.search(r"signup_email", src))


def _wrap_return(src: str, fn: str) -> str:
    """Wrap `return X` in next_* functions with _with_signup_aliases(X) once."""
    pattern = rf"(def {fn}\(\)[^\n]*:\n(?:.*?\n)*?)(\s+)return ([^\n]+)"
    m = re.search(pattern, src)
    if not m:
        return src
    indent, expr = m.group(2), m.group(3).strip()
    if "_with_signup_aliases" in expr:
        return src
    return src[: m.start(2)] + f"{indent}return _with_signup_aliases({expr})\n" + src[m.end() :]


def main() -> int:
    if not TARGET.is_file():
        print(f"skip: missing {TARGET}")
        return 0

    src = TARGET.read_text(encoding="utf-8", errors="ignore")
    if "Auto-generated" in src or "compat stub" in src:
        print("skip: file is still our stub — restore originals first")
        return 0

    if _has_signup_email(src) and "def next_android_run_values" in src:
        # Already has signup_email in source — likely complete
        print(f"OK: {TARGET} already references signup_email")
        return 0

    if "_with_signup_aliases" not in src:
        src = src.rstrip() + "\n" + WRAPPER + "\n"

    for fn in (
        "next_android_run_values",
        "next_ios_run_values",
        "get_android_run_values",
        "get_ios_run_values",
    ):
        if f"def {fn}" in src:
            src = _wrap_return(src, fn)

    # Validate syntax
    try:
        ast.parse(src)
    except SyntaxError as e:
        print(f"ERROR: alias wrap would break syntax: {e}")
        return 1

    TARGET.write_text(src, encoding="utf-8")
    print(f"Added signup_* aliases (email format unchanged) → {TARGET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
