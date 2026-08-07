"""Runtime config for clean Android signup+login suite."""
from __future__ import annotations

import os

APPIUM_URL = os.environ.get("APPIUM_URL", "http://127.0.0.1:4723")
ANDROID_PACKAGE = os.environ.get("ANDROID_UAT_PACKAGE", "com.kskinfacial.customer.uat")
# Optional; if empty, conftest resolves via adb
ANDROID_ACTIVITY = os.environ.get("ANDROID_UAT_ACTIVITY", "").strip()
DEVICE_NAME = os.environ.get("ANDROID_DEVICE_NAME", "Android Emulator")
NEW_COMMAND_TIMEOUT = int(os.environ.get("APPIUM_NEW_COMMAND_TIMEOUT", "300"))
IMPLICIT_WAIT = float(os.environ.get("APPIUM_IMPLICIT_WAIT", "0.5"))
EXPLICIT_WAIT = float(os.environ.get("APPIUM_EXPLICIT_WAIT", "20"))
STEP_PAUSE_SEC = float(os.environ.get("STEP_PAUSE_SEC", "2.0"))
STEP_PRE_PAUSE_SEC = float(os.environ.get("STEP_PRE_PAUSE_SEC", "0.6"))
UNINSTALL_BEFORE_RUN = os.environ.get("ANDROID_UNINSTALL_BEFORE", "1").strip() not in {
    "0",
    "false",
    "no",
}
