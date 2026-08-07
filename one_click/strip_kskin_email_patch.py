#!/usr/bin/env python3
"""Remove ONLY the KSKIN_EMAIL_TYPE_PATCH junk from signup_login_android_page.py.

That patch imported helpers.android_type, then we deleted android_type.py —
collection dies with ModuleNotFoundError. This restores send_keys and drops
the import. Does not invent page methods.

Run on Mac:
  python3 ~/AquaProjects/KskinCMS/one_click/strip_kskin_email_patch.py
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
MARKER = "KSKIN_EMAIL_TYPE_PATCH"


def main() -> int:
    if not PAGE.is_file():
        print(f"ERROR: missing {PAGE}")
        return 1

    src = PAGE.read_text(encoding="utf-8", errors="ignore")
    if "android_type" not in src and MARKER not in src:
        print(f"OK: no email-patch leftovers in {PAGE}")
        return 0

    bak = PAGE.with_suffix(PAGE.suffix + f".bak_strip_email_{int(time.time())}")
    shutil.copy2(PAGE, bak)
    print(f"Backup: {bak}")

    # Drop import line(s)
    src2 = re.sub(
        r"^from helpers\.android_type import type_email.*\n",
        "",
        src,
        flags=re.M,
    )
    src2 = re.sub(
        r"^from helpers\.android_type import type_text.*\n",
        "",
        src2,
        flags=re.M,
    )

    # Reverse: type_email(getattr(self, 'driver', None), EL, VAL)  # KSKIN...
    #       -> EL.send_keys(VAL)
    src2 = re.sub(
        rf"type_email\(\s*getattr\(\s*self\s*,\s*['\"]driver['\"]\s*,\s*None\s*\)\s*,\s*([^,]+)\s*,\s*([^)]+)\)\s*(?:#\s*{MARKER})?",
        r"\1.send_keys(\2)",
        src2,
    )
    # Simpler leftovers: type_email(self.driver, EL, VAL)
    src2 = re.sub(
        rf"type_email\(\s*(?:self\.driver|driver)\s*,\s*([^,]+)\s*,\s*([^)]+)\)\s*(?:#\s*{MARKER})?",
        r"\1.send_keys(\2)",
        src2,
    )

    # Remove dedicated enter_email_reliable / monkey-patch blocks we appended
    src2 = re.sub(
        rf"\n    # --- {MARKER}[\s\S]*?(?=\n    # --- |\nclass |\Z)",
        "\n",
        src2,
    )
    # Inline marker comments only
    src2 = re.sub(rf"[ \t]*#\s*{MARKER}[^\n]*", "", src2)

    if "android_type" in src2:
        print("WARNING: android_type still referenced after strip — check manually")
        for i, line in enumerate(src2.splitlines(), 1):
            if "android_type" in line or "type_email(" in line:
                print(f"  {i}: {line}")

    PAGE.write_text(src2, encoding="utf-8")
    print(f"Stripped email patch → {PAGE}")

    # Never recreate android_type; ensure junk helper stays gone
    for junk in (
        APPIUM_PY / "helpers" / "android_type.py",
        APPIUM_PY / "helpers" / "patch_email_runtime.py",
    ):
        if junk.is_file():
            junk.unlink()
            print(f"Removed junk helper: {junk}")

    # Quick syntax check
    compile(src2, str(PAGE), "exec")
    print("Syntax OK")
    print("Re-run: bash ~/AquaProjects/KskinCMS/one_click/run_original_mobile_test.sh android-signup")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
