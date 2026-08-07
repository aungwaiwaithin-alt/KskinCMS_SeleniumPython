"""Appium driver fixture for clean Android signup suite."""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options

# Allow `import config` / `from pages...` when pytest root is this package
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import config  # noqa: E402


def _adb_devices() -> list[str]:
    try:
        out = subprocess.check_output(["adb", "devices"], text=True)
    except Exception:
        return []
    devices = []
    for line in out.splitlines()[1:]:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            devices.append(parts[0])
    return devices


def _resolve_activity(package: str) -> str:
    if config.ANDROID_ACTIVITY:
        return config.ANDROID_ACTIVITY
    try:
        out = subprocess.check_output(
            ["adb", "shell", "cmd", "package", "resolve-activity", "--brief", package],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        # last non-empty line often "package/activity"
        lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
        if lines:
            last = lines[-1]
            if "/" in last:
                return last.split("/", 1)[1]
    except Exception:
        pass
    return ".MainActivity"


@pytest.fixture(scope="session")
def android_driver():
    devices = _adb_devices()
    if not devices:
        pytest.skip("No Android device/emulator (adb devices empty)")

    pkg = config.ANDROID_PACKAGE
    if config.UNINSTALL_BEFORE_RUN:
        subprocess.run(["adb", "uninstall", pkg], check=False, capture_output=True)
        time.sleep(1.0)

    activity = _resolve_activity(pkg)
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = config.DEVICE_NAME
    options.udid = devices[0]
    options.app_package = pkg
    options.app_activity = activity
    options.no_reset = False
    options.new_command_timeout = config.NEW_COMMAND_TIMEOUT
    options.set_capability("autoGrantPermissions", True)
    options.set_capability("ignoreHiddenApiPolicyError", True)

    driver = webdriver.Remote(config.APPIUM_URL, options=options)
    driver.implicitly_wait(config.IMPLICIT_WAIT)
    try:
        yield driver
    finally:
        try:
            driver.quit()
        except Exception:
            pass
