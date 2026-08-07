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
        if not config.ANDROID_APP_APK:
            pytest.fail(
                "ANDROID_UNINSTALL_BEFORE=1 requires ANDROID_APP_APK=/path/to/app.apk "
                "(otherwise Appium cannot reinstall the package)."
            )
        subprocess.run(["adb", "uninstall", pkg], check=False, capture_output=True)
        time.sleep(1.0)

    # Confirm package is on device when we are not installing from APK
    if not config.ANDROID_APP_APK:
        check = subprocess.run(
            ["adb", "shell", "pm", "path", pkg],
            capture_output=True,
            text=True,
        )
        if check.returncode != 0 or "package:" not in (check.stdout or ""):
            pytest.fail(
                f"Package {pkg} is not installed on the emulator/device.\n"
                f"Install the UAT build first, or set ANDROID_APP_APK=/path/to.apk"
            )

    activity = _resolve_activity(pkg)
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = config.DEVICE_NAME
    options.udid = devices[0]
    options.app_package = pkg
    options.app_activity = activity
    options.no_reset = config.NO_RESET
    options.new_command_timeout = config.NEW_COMMAND_TIMEOUT
    options.set_capability("autoGrantPermissions", True)
    options.set_capability("ignoreHiddenApiPolicyError", True)
    options.set_capability("dontStopAppOnReset", True)
    if config.ANDROID_APP_APK:
        options.app = config.ANDROID_APP_APK

    driver = webdriver.Remote(config.APPIUM_URL, options=options)
    driver.implicitly_wait(config.IMPLICIT_WAIT)
    try:
        # Ensure app is foreground even when noReset kept it backgrounded
        try:
            driver.activate_app(pkg)
        except Exception:
            pass
        yield driver
    finally:
        try:
            driver.quit()
        except Exception:
            pass
