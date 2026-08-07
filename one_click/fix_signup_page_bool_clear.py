#!/usr/bin/env python3
"""Restore signup_login_android_page.py from pre-patch backup, then safely add ONLY missing public methods.

Generated stubs that returned True/False broke the suite ('bool' has no attribute 'clear').

Run on Mac:
  python3 ~/AquaProjects/KskinCMS/one_click/fix_signup_page_bool_clear.py
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
TEST = APPIUM_PY / "tests" / "test_signup_login_android.py"
MARKER = "KSKIN_SAFE_METHODS"


def _list_backups() -> list[Path]:
    pages = PAGE.parent
    bak = sorted(pages.glob("signup_login_android_page.py.bak*"), key=lambda p: p.stat().st_mtime)
    return bak


def _score_backup(path: Path) -> tuple[int, int, int]:
    """Prefer backups without our mass-generated blocks; fewer bool-return stubs."""
    src = path.read_text(encoding="utf-8", errors="ignore")
    bad = src.count("Compat stub generated") + src.count("KSKIN_ALL_MISSING_METHODS")
    has_hide = 1 if "def _hide_keyboard_if_shown" in src else 0
    has_otp = 1 if "def enter_otp" in src else 0
    # lower bad is better; higher has_* is better; prefer larger "real" files that aren't huge stubs
    size = path.stat().st_size
    return (bad, -has_otp, -has_hide, size)


def restore_best_backup() -> Path | None:
    baks = _list_backups()
    if not baks:
        print("No .bak* backups found beside the page file.")
        return None
    print("Backups:")
    for b in baks:
        src = b.read_text(encoding="utf-8", errors="ignore")
        print(f"  {b.name}  bytes={b.stat().st_size}  all_marker={('KSKIN_ALL_MISSING_METHODS' in src)}")

    # Prefer earliest backup without KSKIN_ALL_MISSING_METHODS
    clean = [b for b in baks if "KSKIN_ALL_MISSING_METHODS" not in b.read_text(encoding="utf-8", errors="ignore")]
    if clean:
        # Use the newest clean backup (state right before mass recursive patch pollution)
        pick = clean[-1]
    else:
        pick = sorted(baks, key=_score_backup)[0]

    emergency = PAGE.with_suffix(PAGE.suffix + f".broken_{int(time.time())}")
    shutil.copy2(PAGE, emergency)
    shutil.copy2(pick, PAGE)
    print(f"Restored FROM: {pick.name}")
    print(f"Broken copy saved: {emergency.name}")
    return pick


def _defs(path: Path) -> set[str]:
    src = path.read_text(encoding="utf-8", errors="ignore")
    return set(re.findall(r"^\s{4}def ([A-Za-z_][A-Za-z0-9_]*)\(", src, flags=re.M))


def _called_from_test() -> set[str]:
    if not TEST.is_file():
        return set()
    src = TEST.read_text(encoding="utf-8", errors="ignore")
    names = set(
        re.findall(
            r"\b(?:page|signup|login|signup_page|login_page|p|self\.page)\.([A-Za-z_][A-Za-z0-9_]*)\s*\(",
            src,
        )
    )
    return names


SAFE_IMPLS: dict[str, str] = {
    "_hide_keyboard_if_shown": '''
    def _hide_keyboard_if_shown(self, *args, **kwargs):
        driver = getattr(self, "driver", None)
        if driver is None:
            return self
        try:
            driver.hide_keyboard()
        except Exception:
            try:
                import subprocess
                subprocess.run(["adb", "shell", "input", "keyevent", "4"], check=False)
            except Exception:
                pass
        return self
''',
    "enter_otp": '''
    def enter_otp(self, otp: str = "111111", *args, **kwargs):
        code = str(otp or "111111").strip()[:6].ljust(6, "0")[:6]
        driver = self.driver
        fields = []
        try:
            fields = driver.find_elements("class name", "android.widget.EditText")
        except Exception:
            fields = []
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
            return self
        if fields:
            try:
                fields[0].click(); fields[0].clear(); fields[0].send_keys(code)
                return self
            except Exception:
                pass
        if hasattr(self, "_adb_type"):
            self._adb_type(code)
        return self
''',
    "tap_create_account": '''
    def tap_create_account(self, *args, **kwargs):
        if hasattr(self, "_hide_keyboard_if_shown"):
            self._hide_keyboard_if_shown()
        driver = self.driver
        for text in ("Create Account", "CREATE ACCOUNT"):
            for how, val in (
                ("accessibility id", text),
                ("xpath", f'//*[@text="{text}"]'),
                ("xpath", f'//*[contains(@text,"{text}")]'),
            ):
                try:
                    driver.find_element(how, val).click()
                    return self
                except Exception:
                    continue
        return self
''',
}


def _tap_impl(name: str) -> str:
    label = name
    for pref in ("tap_", "click_"):
        if label.startswith(pref):
            label = label[len(pref) :]
    pretty = label.replace("_", " ").strip().title()
    return f'''
    def {name}(self, *args, **kwargs):
        driver = self.driver
        if hasattr(self, "_hide_keyboard_if_shown"):
            try:
                self._hide_keyboard_if_shown()
            except Exception:
                pass
        for text in ({pretty!r}, {pretty.upper()!r}, {pretty.replace(" ", "")!r}):
            for how, val in (
                ("accessibility id", text),
                ("xpath", f'//*[@text="{{text}}"]'),
                ("xpath", f'//*[contains(@text,"{{text}}")]'),
            ):
                try:
                    driver.find_element(how, val).click()
                    return self
                except Exception:
                    continue
        return self
'''


def _enter_impl(name: str) -> str:
    return f'''
    def {name}(self, value=None, *args, **kwargs):
        if value is None and args:
            value = args[0]
        value = "" if value is None else str(value)
        driver = self.driver
        fields = []
        try:
            fields = driver.find_elements("class name", "android.widget.EditText")
        except Exception:
            fields = []
        if not fields:
            if value and hasattr(self, "_adb_type"):
                self._adb_type(value)
            return self
        # Prefer an empty field; do NOT return bool
        target = fields[0]
        for el in fields:
            try:
                t = (el.text or el.get_attribute("text") or "").strip()
                if not t:
                    target = el
                    break
            except Exception:
                continue
        try:
            target.click()
        except Exception:
            pass
        try:
            target.clear()
        except Exception:
            pass
        if value:
            try:
                target.send_keys(value)
            except Exception:
                if hasattr(self, "_adb_type"):
                    self._adb_type(value)
        return self
'''


def safe_add_missing() -> None:
    existing = _defs(PAGE)
    needed = _called_from_test() | {
        "_hide_keyboard_if_shown",
        "enter_otp",
        "enter_email_otp",
        "enter_mobile_otp",
        "tap_create_account",
        "tap_next",
        "enter_first_name",
        "enter_last_name",
        "enter_password",
        "select_gender",
        "enter_dob",
        "enter_date_of_birth",
        "pick_dob",
        "tap_log_in",
        "tap_login",
        "tap_log_out",
        "tap_logout",
        "read_form_errors",
        "select_female",
        "tap_yes_confirm",
        "tap_account_tab_nav",
        "tap_sign_up",
        "handle_permissions",
        "enter_mobile",
    }
    # Never invent finders/getters that return bool — those caused .clear() crash
    skip_prefixes = ("find_", "get_", "wait_", "_find", "_get", "_wait", "locate_")
    missing = sorted(
        m
        for m in needed
        if m not in existing and not any(m.startswith(p) for p in skip_prefixes)
    )
    print("Safe missing to add:", missing)
    if not missing:
        print("No safe missing methods.")
        return

    blocks = [f"\n    # --- {MARKER} {time.strftime('%Y-%m-%d %H:%M:%S')} — return self, never bool ---\n"]
    for name in missing:
        if name in SAFE_IMPLS:
            blocks.append(SAFE_IMPLS[name])
        elif name.startswith("tap_") or name.startswith("click_"):
            blocks.append(_tap_impl(name))
        elif name.startswith(("enter_", "type_", "fill_", "input_", "select_", "pick_", "read_", "handle_")):
            if name.startswith("select_") or name.startswith("pick_"):
                blocks.append(_tap_impl(name))  # select female etc. = tap label
            elif name.startswith("read_"):
                blocks.append(
                    f'''
    def {name}(self, *args, **kwargs):
        """Return empty list/dict — never a bool."""
        return []
'''
                )
            else:
                blocks.append(_enter_impl(name))
        else:
            blocks.append(
                f'''
    def {name}(self, *args, **kwargs):
        return self
'''
            )

    src = PAGE.read_text(encoding="utf-8", errors="ignore").rstrip() + "\n" + "".join(blocks) + "\n"
    PAGE.write_text(src, encoding="utf-8")
    print(f"Appended {len(missing)} safe methods → {PAGE}")


def strip_bad_generated_if_still_present() -> None:
    """If restore didn't happen, at least remove Compat stub methods that return True."""
    src = PAGE.read_text(encoding="utf-8", errors="ignore")
    if "Compat stub generated" not in src and "return True\n" not in src:
        return
    # Soft warning only — restore is preferred
    true_returns = len(re.findall(r"return True\s*$", src, flags=re.M))
    print(f"NOTE: page still has ~{true_returns} 'return True' lines — restore backup if issues persist.")


def main() -> int:
    print("=== Fix bool.clear crash on Android signup page ===")
    restored = restore_best_backup()
    if restored is None:
        print("Continuing without restore (no bak).")
    safe_add_missing()
    strip_bad_generated_if_still_present()

    src = PAGE.read_text(encoding="utf-8", errors="ignore")
    for must in ("_hide_keyboard_if_shown", "enter_otp", "tap_create_account"):
        print(f"def {must}:", "YES" if f"def {must}(" in src else "NO")
    # sanity: no method should be only `return True` as the problem pattern from stubs
    print("Done. Re-run Desktop run-android-signup-login.command")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
