#!/usr/bin/env python3
"""Show the COMPLETE gap between the signup test and the page object — once.

Stops the one-error-per-run loop. Also checks git for a commit whose page file
actually satisfies the test, so we can restore instead of hand-adding methods.

Run on Mac:
  python3 ~/AquaProjects/KskinCMS/one_click/report_signup_gap.py
"""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

AQUA = Path(os.environ.get("AQUA_ROOT", Path.home() / "AquaProjects"))
APPIUM = AQUA / "MCP_Appium_Server"
APPIUM_PY = Path(os.environ.get("APPIUM_PY", APPIUM / "python"))
PAGE_REL = "python/pages/signup_login_android_page.py"
PAGE = APPIUM_PY / "pages" / "signup_login_android_page.py"
TEST = APPIUM_PY / "tests" / "test_signup_login_android.py"


def page_methods(text: str) -> set[str]:
    return set(re.findall(r"^\s{4}def ([A-Za-z_][A-Za-z0-9_]*)\(", text, flags=re.M))


def test_calls(text: str) -> set[str]:
    names: set[str] = set()
    for m in re.finditer(r"\bpage\.([A-Za-z_][A-Za-z0-9_]*)\s*\(", text):
        names.add(m.group(1))
    for m in re.finditer(
        r"\b(?:signup|login|signup_page|login_page|android_page)\.([A-Za-z_][A-Za-z0-9_]*)\s*\(",
        text,
    ):
        names.add(m.group(1))
    return names


def git(*args: str) -> str:
    try:
        r = subprocess.run(
            ["git", *args], cwd=str(APPIUM), capture_output=True, text=True, check=False
        )
        return r.stdout
    except Exception:
        return ""


def main() -> int:
    if not TEST.is_file():
        print(f"ERROR missing test: {TEST}")
        return 1
    if not PAGE.is_file():
        print(f"ERROR missing page: {PAGE}")
        return 1

    tsrc = TEST.read_text(encoding="utf-8", errors="ignore")
    psrc = PAGE.read_text(encoding="utf-8", errors="ignore")

    called = test_calls(tsrc)
    have = page_methods(psrc)
    missing = sorted(called - have)

    print("=" * 70)
    print("SIGNUP GAP REPORT")
    print("=" * 70)
    print(f"test:  {TEST}")
    print(f"page:  {PAGE}  ({PAGE.stat().st_size} bytes)")
    print(f"methods called by test : {len(called)}")
    print(f"methods on page object : {len(have)}")
    print(f"MISSING ({len(missing)}):")
    for m in missing:
        print(f"  - {m}")
    if not missing:
        print("  (none — page satisfies the test)")

    # Also inherited base methods may cover some names
    print("")
    print("NOTE: inherited methods (FullRegressionAndroidPage etc.) are not counted above.")
    parent = APPIUM_PY / "pages" / "full_regression_android_page.py"
    if parent.is_file():
        pm = page_methods(parent.read_text(encoding="utf-8", errors="ignore"))
        covered = sorted(set(missing) & pm)
        print(f"Of the missing, provided by full_regression_android_page: {len(covered)}")
        for c in covered:
            print(f"  ~ {c} (inherited, so not a real failure)")
        real = sorted(set(missing) - pm)
        print(f"REAL missing after inheritance ({len(real)}):")
        for r in real:
            print(f"  * {r}")

    # Git search: which commit's page version satisfies most of the test?
    print("")
    print("=" * 70)
    print("GIT: page versions vs test requirements")
    print("=" * 70)
    log = git("log", "--format=%H %ad %s", "--date=short", "--", PAGE_REL)
    lines = [l for l in log.splitlines() if l.strip()]
    if not lines:
        print("No git history for the page file.")
    best = None
    for line in lines[:40]:
        sha = line.split()[0]
        blob = git("show", f"{sha}:{PAGE_REL}")
        if not blob:
            continue
        pmeth = page_methods(blob)
        miss = sorted(called - pmeth)
        print(f"{sha[:9]}  {line[41:80]:<40} missing={len(miss)}")
        if best is None or len(miss) < best[1]:
            best = (sha, len(miss), miss)
    if best:
        print("")
        print(f"BEST commit for the page: {best[0][:9]} (missing {best[1]})")
        if best[2]:
            print("  still missing:", ", ".join(best[2][:15]))
        print("")
        print("Restore that version with:")
        print(f"  cd {APPIUM}")
        print(f"  git checkout {best[0]} -- {PAGE_REL}")

    # Was the TEST changed after the page? (mismatch cause)
    print("")
    tlog = git("log", "--format=%h %ad %s", "--date=short", "--", "python/tests/test_signup_login_android.py")
    print("Test file history (newest first):")
    for l in tlog.splitlines()[:8]:
        print("  " + l)
    print("Page file history (newest first):")
    for l in log.splitlines()[:8]:
        print("  " + l[:9] + l[40:])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
