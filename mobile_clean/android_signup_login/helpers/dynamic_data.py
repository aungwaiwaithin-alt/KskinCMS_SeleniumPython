"""Per-run signup values — short 6-digit uniq (CMS-style). No long datetime stamps."""
from __future__ import annotations

import random
import time
from types import SimpleNamespace


def _uniq() -> str:
    return str(int(time.time()))[-6:]


def next_android_run_values() -> SimpleNamespace:
    u = _uniq()
    email = f"qa.android.{u}@yopmail.com"
    mobile = "9" + "".join(str(random.randint(0, 9)) for _ in range(7))
    password = "P@ssw0rd"
    first = "Wai"
    last = "Thin"
    otp = "111111"
    dob = "11/04/1998"
    gender = "Female"
    return SimpleNamespace(
        run_id=u,
        stamp=u,
        platform="android",
        email=email,
        signup_email=email,
        login_email=email,
        password=password,
        signup_password=password,
        login_password=password,
        first_name=first,
        last_name=last,
        full_name=f"{first} {last}",
        mobile=mobile,
        signup_mobile=mobile,
        otp=otp,
        email_otp=otp,
        mobile_otp=otp,
        dob=dob,
        gender=gender,
    )
