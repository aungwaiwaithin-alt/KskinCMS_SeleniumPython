#!/usr/bin/env python3
"""LAST-RESORT short-uniq fallback for helpers/dynamic_data.py.

Prefer: bash one_click/restore_claude_mobile_originals.sh
This does NOT invent the long YYMMDDHHMMSS## email (that was a bad Cursor stub).
Fallback email shape matches CMS style: qa.android.<6digits>@yopmail.com

Run on Mac only when original is truly missing:
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
FORCE = os.environ.get("FORCE", "").strip().lower() in {"1", "true", "yes"}

TESTS = [
    APPIUM_PY / "tests" / "test_signup_login_android.py",
    APPIUM_PY / "tests" / "test_signup_login_ios.py",
]

# Always include these aliases (Claude suites use signup_* names)
ALWAYS = {
    "email",
    "signup_email",
    "login_email",
    "user_email",
    "password",
    "signup_password",
    "login_password",
    "user_password",
    "first_name",
    "signup_first_name",
    "last_name",
    "signup_last_name",
    "full_name",
    "name",
    "signup_name",
    "mobile",
    "phone",
    "mobile_number",
    "signup_mobile",
    "signup_phone",
    "otp",
    "email_otp",
    "mobile_otp",
    "sms_otp",
    "signup_otp",
    "gender",
    "signup_gender",
    "dob",
    "date_of_birth",
    "signup_dob",
    "signup_date_of_birth",
    "platform",
    "run_id",
    "stamp",
}


def _attrs_from_tests() -> set[str]:
    attrs: set[str] = set()
    for path in TESTS:
        if not path.is_file():
            continue
        src = path.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r"\b(?:run|values|data|creds|user)\.([A-Za-z_][A-Za-z0-9_]*)", src):
            attrs.add(m.group(1))
        for m in re.finditer(
            r"\b(?:run|values|data|creds|user)\[\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]\s*\]",
            src,
        ):
            attrs.add(m.group(1))
        for m in re.finditer(
            r"getattr\(\s*(?:run|values|data)\s*,\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]",
            src,
        ):
            attrs.add(m.group(1))
    ignore = {"get", "items", "keys", "values", "copy", "update", "pop", "driver", "page"}
    return {a for a in attrs if a not in ignore and not a.startswith("_")}


def _expr_for(attr: str) -> str:
    al = attr.lower()
    if "email" in al:
        return "email"
    if "pass" in al:
        return "password"
    if "otp" in al:
        return "otp"
    if "mobile" in al or "phone" in al:
        return "mobile"
    if "first" in al:
        return "first"
    if "last" in al:
        return "last"
    if "name" in al:
        return "full"
    if "gender" in al:
        return "gender"
    if "dob" in al or "birth" in al:
        return "dob"
    if attr == "platform":
        return "platform"
    if attr in {"run_id", "stamp"}:
        return "s"
    return f'f"qa-{attr}-{{s}}"'


def main() -> int:
    HELPERS.mkdir(parents=True, exist_ok=True)
    (HELPERS / "__init__.py").touch(exist_ok=True)

    attrs = ALWAYS | _attrs_from_tests()
    print("Attrs:", sorted(attrs))

    if TARGET.exists() and not FORCE:
        src = TARGET.read_text(encoding="utf-8", errors="ignore")
        # Never clobber a real Claude/original file
        if "Auto-generated" not in src and "compat stub" not in src and "short uniq fallback" not in src:
            if "next_android_run_values" in src:
                print(f"REFUSING to overwrite original: {TARGET}")
                print("Use restore_claude_mobile_originals.sh or Local History instead.")
                return 0
        if "signup_email" in src and "next_android_run_values" in src:
            print(f"OK already has signup_email: {TARGET}")
            print("Re-run with FORCE=1 only if you intentionally want the short-uniq fallback.")
            return 0

    lines = [
        '"""Short-uniq fallback for per-run signup values (CMS-style 6 digits).',
        "",
        "NOT the long YYMMDDHHMMSS stub. Prefer Claude helpers/dynamic_data.py",
        "from Local History / Appium git when available.",
        '"""',
        "from __future__ import annotations",
        "",
        "import random",
        "import time",
        "from types import SimpleNamespace",
        "",
        "",
        "def _stamp() -> str:",
        "    # CMS-style short suffix — never 14-digit datetime",
        '    return str(int(time.time()))[-6:]',
        "",
        "",
        "def _bag(platform: str) -> SimpleNamespace:",
        "    s = _stamp()",
        '    mobile = "9" + "".join(str(random.randint(0, 9)) for _ in range(7))',
        '    email = f"qa.{platform}.{s}@yopmail.com"',
        '    password = "P@ssw0rd"',
        '    first = "QA"',
        '    last = f"{platform.title()}{s[-4:]}"',
        "    full = f\"{first} {last}\"",
        '    otp = "111111"',
        '    dob = "01/01/1995"',
        '    gender = "Female"',
        "    data = {",
    ]
    for a in sorted(attrs):
        lines.append(f'        "{a}": {_expr_for(a)},')
    lines += [
        "    }",
        "    return SimpleNamespace(**data)",
        "",
        "",
        "def next_android_run_values():",
        '    return _bag("android")',
        "",
        "",
        "def next_ios_run_values():",
        '    return _bag("ios")',
        "",
        "",
        "def get_android_run_values():",
        "    return next_android_run_values()",
        "",
        "",
        "def get_ios_run_values():",
        "    return next_ios_run_values()",
        "",
    ]
    TARGET.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {TARGET}")

    import sys

    sys.path.insert(0, str(APPIUM_PY))
    sys.modules.pop("helpers.dynamic_data", None)
    sys.modules.pop("helpers", None)
    from helpers.dynamic_data import next_android_run_values  # noqa: WPS433

    v = next_android_run_values()
    print("IMPORT OK signup_email:", getattr(v, "signup_email", None))
    missing = [a for a in sorted(attrs) if not hasattr(v, a)]
    if missing:
        print("WARNING still missing:", missing)
        return 1
    print("All attrs present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
