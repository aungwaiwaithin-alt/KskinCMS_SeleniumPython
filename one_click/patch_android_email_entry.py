#!/usr/bin/env python3
"""Patch Android signup page to type email reliably (Material EditText).

Symptom: report stops ~4 steps at EMPTY EMAIL / "Please enter a valid email address"
even though dynamic_data has signup_email — field often stays blank after set_value.

Run on Mac:
  python3 ~/AquaProjects/KskinCMS/one_click/patch_android_email_entry.py
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
HELPER = APPIUM_PY / "helpers" / "android_type.py"

HELPER_SRC = '''"""Reliable Android text input for Material/React fields."""
from __future__ import annotations

import subprocess
import time
from typing import Any


def _adb(*args: str) -> None:
    subprocess.run(["adb", *args], check=False, capture_output=True)


def type_text(driver: Any, element: Any, text: str, *, clear: bool = True) -> None:
    """Tap field, clear, then type. Falls back to adb shell input text for '@'."""
    try:
        element.click()
    except Exception:
        pass
    time.sleep(0.25)
    if clear:
        try:
            element.clear()
        except Exception:
            pass
        try:
            # Some Material fields ignore clear(); select-all delete
            element.send_keys("\\u0001")  # CTRL-A may not work; best-effort
        except Exception:
            pass
    # Primary: Appium send_keys
    try:
        element.send_keys(text)
        time.sleep(0.2)
        got = (element.text or element.get_attribute("text") or "").strip()
        if text.split("@")[0] in got or got.endswith(text[-6:]):
            return
    except Exception:
        pass
    # Fallback: adb (escape special chars)
    try:
        element.click()
    except Exception:
        pass
    time.sleep(0.15)
    if "@" in text:
        local, _, domain = text.partition("@")
        _adb("shell", "input", "text", local)
        time.sleep(0.1)
        # @ often needs keyevent or quoted form
        _adb("shell", "input", "text", "@")
        time.sleep(0.1)
        _adb("shell", "input", "text", domain.replace(" ", "%s"))
    else:
        safe = text.replace(" ", "%s")
        _adb("shell", "input", "text", safe)
    time.sleep(0.2)


def type_email(driver: Any, element: Any, email: str) -> None:
    type_text(driver, element, email, clear=True)
'''

PATCH_MARKER = "KSKIN_EMAIL_TYPE_PATCH"


def main() -> int:
    if not PAGE.is_file():
        print(f"ERROR: missing {PAGE}")
        return 1

    HELPER.parent.mkdir(parents=True, exist_ok=True)
    HELPER.write_text(HELPER_SRC, encoding="utf-8")
    print(f"Wrote {HELPER}")

    src = PAGE.read_text(encoding="utf-8", errors="ignore")
    if PATCH_MARKER in src:
        print(f"Already patched: {PAGE}")
        return 0

    bak = PAGE.with_suffix(PAGE.suffix + f".bak_{int(time.time())}")
    shutil.copy2(PAGE, bak)
    print(f"Backup: {bak}")

    # Ensure import
    if "from helpers.android_type import type_email" not in src:
        # after future annotations / top imports
        lines = src.splitlines()
        insert_at = 0
        for i, line in enumerate(lines[:40]):
            if line.startswith("import ") or line.startswith("from "):
                insert_at = i + 1
        lines.insert(insert_at, f"from helpers.android_type import type_email  # {PATCH_MARKER}")
        src = "\n".join(lines) + ("\n" if src.endswith("\n") else "")

    # Replace common email send_keys patterns inside methods that mention email
    # el.send_keys(email) / element.send_keys(self.email) etc.
    def repl_send_keys(m: re.Match[str]) -> str:
        target = m.group(1)
        value = m.group(2)
        return f"type_email(getattr(self, 'driver', None), {target}, {value})  # {PATCH_MARKER}"

    new_src, n1 = re.subn(
        r"([A-Za-z_][A-Za-z0-9_]*)\.send_keys\(\s*([^\)]*(?:email|Email)[^\)]*)\s*\)",
        repl_send_keys,
        src,
    )
    # also set_value
    new_src, n2 = re.subn(
        r"([A-Za-z_][A-Za-z0-9_]*)\.set_value\(\s*([^\)]*(?:email|Email)[^\)]*)\s*\)",
        repl_send_keys,
        new_src,
    )

    # If no send_keys(email) found, append helper method for suites to call
    if n1 + n2 == 0:
        print("NOTE: no send_keys(email) pattern found — appending helper method enter_email_reliable")
        if "def enter_email_reliable" not in new_src:
            new_src += f"""

    # --- {PATCH_MARKER} ---
    def enter_email_reliable(self, email, element=None):
        \"\"\"Reliable email entry; use when field stays empty after send_keys.\"\"\"
        el = element
        if el is None:
            for name in ("email_field", "email_input", "txt_email", "email"):
                el = getattr(self, name, None)
                if el is not None and not callable(el):
                    break
                meth = getattr(self, name, None)
                if callable(meth):
                    try:
                        el = meth()
                        break
                    except Exception:
                        pass
        if el is None:
            # last resort: focused field via adb only
            from helpers.android_type import type_text
            type_text(getattr(self, "driver", None), type("E", (), {{"click": lambda s: None, "clear": lambda s: None, "send_keys": lambda s, t: None, "text": "", "get_attribute": lambda s, a: ""}})(), email)
            return
        type_email(getattr(self, "driver", None), el, email)
"""

    # Monkey-patch: wrap methods named like enter_email / type_email / input_email
    method_wrap = f"""

# --- {PATCH_MARKER} method wraps ---
try:
    import pages.signup_login_android_page as _sl_mod
    from helpers.android_type import type_email as _kskin_type_email
    _cls = getattr(_sl_mod, "SignupLoginAndroidPage", None)
    if _cls is not None:
        for _name in list(vars(_cls).keys()):
            if not re_match_email_method(_name):
                continue
            _orig = getattr(_cls, _name)
            if not callable(_orig):
                continue
            def _make(orig):
                def _wrapped(self, *args, **kwargs):
                    # If first arg looks like email, also force-type into focused/email field after orig
                    result = orig(self, *args, **kwargs)
                    email = None
                    if args and isinstance(args[0], str) and "@" in args[0]:
                        email = args[0]
                    email = kwargs.get("email", email)
                    if email:
                        el = None
                        for attr in ("email_field", "email_input", "txt_email"):
                            cand = getattr(self, attr, None)
                            if callable(cand):
                                try:
                                    cand = cand()
                                except Exception:
                                    cand = None
                            if cand is not None:
                                el = cand
                                break
                        if el is not None:
                            _kskin_type_email(getattr(self, "driver", None), el, email)
                    return result
                return _wrapped
            setattr(_cls, _name, _make(_orig))
except Exception:
    pass
"""
    # Don't append the broken wrap that references undefined re_match — instead do wrap in this patcher file at import time via a small helper module
    PAGE.write_text(new_src if new_src.endswith("\n") else new_src + "\n", encoding="utf-8")
    print(f"Patched {PAGE} (send_keys replacements: {n1}, set_value: {n2})")

    # Write runtime wrap module imported from conftest if present
    wrap_path = APPIUM_PY / "helpers" / "patch_email_runtime.py"
    wrap_path.write_text(
        f'''"""Runtime wrap for SignupLoginAndroidPage email methods. {PATCH_MARKER}"""
from __future__ import annotations

import re

def apply() -> None:
    try:
        from pages.signup_login_android_page import SignupLoginAndroidPage
        from helpers.android_type import type_email
    except Exception as e:
        print("patch_email_runtime: import failed", e)
        return
    for name, orig in list(vars(SignupLoginAndroidPage).items()):
        if not re.search(r"email", name, re.I):
            continue
        if not callable(orig) or name.startswith("_"):
            continue
        def make(o):
            def wrapped(self, *args, **kwargs):
                result = o(self, *args, **kwargs)
                email = kwargs.get("email")
                if email is None and args and isinstance(args[0], str) and "@" in args[0]:
                    email = args[0]
                if not email:
                    return result
                el = None
                for attr in ("email_field", "email_input", "txt_email", "email"):
                    cand = getattr(self, attr, None)
                    if callable(cand):
                        try:
                            cand = cand()
                        except Exception:
                            cand = None
                    if cand is not None and not callable(cand):
                        el = cand
                        break
                if el is not None:
                    type_email(getattr(self, "driver", None), el, email)
                return result
            return wrapped
        try:
            setattr(SignupLoginAndroidPage, name, make(orig))
        except Exception:
            pass
    print("patch_email_runtime: applied")
''',
        encoding="utf-8",
    )
    print(f"Wrote {wrap_path}")

    # Ensure conftest applies it
    conftest = APPIUM_PY / "conftest.py"
    needle = "helpers.patch_email_runtime"
    if conftest.is_file():
        csrc = conftest.read_text(encoding="utf-8", errors="ignore")
        if needle not in csrc:
            shutil.copy2(conftest, conftest.with_suffix(f".py.bak_{int(time.time())}"))
            conftest.write_text(
                csrc
                + f"\n\n# {PATCH_MARKER}\ntry:\n    from helpers.patch_email_runtime import apply as _kskin_email_patch\n    _kskin_email_patch()\nexcept Exception as _e:\n    print('email patch skipped', _e)\n",
                encoding="utf-8",
            )
            print(f"Updated {conftest}")
        else:
            print("conftest already applies email patch")
    else:
        conftest.write_text(
            f'''# {PATCH_MARKER}
try:
    from helpers.patch_email_runtime import apply as _kskin_email_patch
    _kskin_email_patch()
except Exception as _e:
    print("email patch skipped", _e)
''',
            encoding="utf-8",
        )
        print(f"Created {conftest}")

    print("Done. Re-run run-android-signup-login.command")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
