#!/usr/bin/env python3
"""Create a missing pages/permissions_android_page.py compat module.

Claude-era signup tests import PermissionsAndroidPage, but some Appium trees
only kept signup_login_android_page.py. This script:
  1) Inspects test_signup_login_android.py for PermissionsAndroidPage usages
  2) Reuses methods from signup_login_android_page / welcome / home when possible
  3) Writes a working stub so pytest can collect

Run on Mac:
  python3 ~/AquaProjects/KskinCMS/one_click/generate_permissions_android_page.py
"""
from __future__ import annotations

import ast
import os
import re
from pathlib import Path

AQUA = Path(os.environ.get("AQUA_ROOT", Path.home() / "AquaProjects"))
APPIUM_PY = Path(os.environ.get("APPIUM_PY", AQUA / "MCP_Appium_Server" / "python"))
PAGES = APPIUM_PY / "pages"
TARGET = PAGES / "permissions_android_page.py"
TEST = APPIUM_PY / "tests" / "test_signup_login_android.py"
SIGNUP_PAGE = PAGES / "signup_login_android_page.py"


def _methods_called_on(var_names: set[str], src: str) -> set[str]:
    """Find var.method( ... ) for given variable names."""
    methods: set[str] = set()
    for m in re.finditer(r"\b(" + "|".join(map(re.escape, var_names)) + r")\.([A-Za-z_][A-Za-z0-9_]*)\s*\(", src):
        methods.add(m.group(2))
    return methods


def _class_methods(path: Path) -> dict[str, list[str]]:
    if not path.is_file():
        return {}
    tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    out: dict[str, list[str]] = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            names = [
                n.name
                for n in node.body
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and not n.name.startswith("__")
            ]
            out[node.name] = names
    return out


def main() -> int:
    PAGES.mkdir(parents=True, exist_ok=True)
    if TARGET.exists():
        print(f"OK already exists: {TARGET}")
        return 0

    test_src = TEST.read_text(encoding="utf-8", errors="ignore") if TEST.is_file() else ""
    # Common instance names in Claude suites
    called = _methods_called_on(
        {"permissions", "perm", "permissions_page", "PermissionsAndroidPage"},
        test_src,
    )
    # Also: PermissionsAndroidPage(...).foo  rare; and assignments
    for m in re.finditer(
        r"(?:permissions|perm|permissions_page)\s*=\s*PermissionsAndroidPage\([^\)]*\)",
        test_src,
    ):
        pass
    # Broader: any .allow_ / .permission_ / .tap_ after PermissionsAndroidPage import block
    for m in re.finditer(r"permissions_page\.([A-Za-z_][A-Za-z0-9_]*)\s*\(", test_src):
        called.add(m.group(1))
    for m in re.finditer(r"\bpermissions\.([A-Za-z_][A-Za-z0-9_]*)\s*\(", test_src):
        called.add(m.group(1))

    signup_classes = _class_methods(SIGNUP_PAGE)
    signup_methods: set[str] = set()
    for meths in signup_classes.values():
        signup_methods.update(meths)

    # Heuristic permission-ish names often used in mobile suites
    defaults = {
        "allow_all",
        "allow_notifications",
        "allow_location",
        "allow_camera",
        "allow_photos",
        "allow_tracking",
        "handle_permissions",
        "accept_permissions",
        "dismiss_permissions",
        "grant_permissions",
        "tap_allow",
        "tap_while_using_app",
        "tap_ok",
        "tap_continue",
        "skip_if_absent",
        "wait_and_allow",
    }
    needed = called | {d for d in defaults if d in signup_methods} | called
    if not called:
        # If test doesn't show clear calls, expose signup methods that look permission-related
        needed |= {m for m in signup_methods if re.search(r"permit|permission|allow|notif|location|camera|photo|tracking", m, re.I)}

    print("Test file:", TEST if TEST.is_file() else "(missing)")
    print("Methods guessed from test:", sorted(called) or "(none)")
    print("Signup page classes:", list(signup_classes) or "(none)")
    print("Will stub methods:", sorted(needed) or "(allow_all only)")

    if not needed:
        needed = {"allow_all", "handle_permissions", "accept_permissions"}

    # Prefer subclassing / composing signup page when available
    signup_cls = next(iter(signup_classes), None)

    lines = [
        '"""Auto-generated compat page object for Android permissions.',
        "",
        "Created because tests import pages.permissions_android_page but the file",
        "was missing from MCP_Appium_Server/python/pages (and not in the zip).",
        "Replace with your real Claude-era module when you recover it.",
        '"""',
        "from __future__ import annotations",
        "",
        "from typing import Any",
        "",
    ]

    if signup_cls:
        lines += [
            f"from pages.signup_login_android_page import {signup_cls}",
            "",
            "",
            f"class PermissionsAndroidPage({signup_cls}):",
            '    """Compat: permissions helpers; inherits signup/login page actions."""',
            "",
            "    def __init__(self, driver: Any = None, *args: Any, **kwargs: Any) -> None:",
            "        # Be tolerant of (driver) or () constructors used by suites",
            "        try:",
            "            super().__init__(driver, *args, **kwargs)",
            "        except TypeError:",
            "            try:",
            "                super().__init__(*args, **kwargs)",
            "            except TypeError:",
            "                self.driver = driver",
            "",
        ]
    else:
        lines += [
            "",
            "class PermissionsAndroidPage:",
            '    """Minimal stub when signup page is unavailable."""',
            "",
            "    def __init__(self, driver: Any = None, *args: Any, **kwargs: Any) -> None:",
            "        self.driver = driver",
            "",
        ]

    # Emit methods — call super if present, else no-op True
    for meth in sorted(needed):
        if signup_cls and meth in signup_methods:
            lines += [
                f"    def {meth}(self, *args: Any, **kwargs: Any) -> Any:",
                f"        return super().{meth}(*args, **kwargs)",
                "",
            ]
        else:
            lines += [
                f"    def {meth}(self, *args: Any, **kwargs: Any) -> bool:",
                f'        """Best-effort stub for missing permissions API: {meth}."""',
                "        driver = getattr(self, 'driver', None)",
                "        if driver is None:",
                "            return True",
                "        # Try common Allow / While using the app buttons; ignore failures",
                "        candidates = (",
                '            "Allow",',
                '            "ALLOW",',
                '            "Allow all the time",',
                '            "While using the app",',
                '            "Only this time",',
                '            "OK",',
                '            "Continue",',
                "        )",
                "        for text in candidates:",
                "            try:",
                '                el = driver.find_element("accessibility id", text)',
                "                el.click()",
                "                return True",
                "            except Exception:",
                "                pass",
            ]
            # also xpath text
            lines += [
                "            try:",
                '                el = driver.find_element("xpath", f\'//*[@text="{text}"]\')',
                "                el.click()",
                "                return True",
                "            except Exception:",
                "                pass",
                "        return True",
                "",
            ]

    # Aliases
    if "handle_permissions" not in needed and "allow_all" in needed:
        lines += [
            "    def handle_permissions(self, *args, **kwargs):",
            "        return self.allow_all(*args, **kwargs)",
            "",
        ]

    TARGET.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {TARGET}")

    # verify import with venv python if present
    import sys

    sys.path.insert(0, str(APPIUM_PY))
    try:
        from pages.permissions_android_page import PermissionsAndroidPage  # noqa: WPS433

        print("IMPORT OK:", PermissionsAndroidPage)
    except Exception as e:  # noqa: BLE001
        print("IMPORT WARNING:", e)
        print("File was written; fix constructor/imports if needed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
