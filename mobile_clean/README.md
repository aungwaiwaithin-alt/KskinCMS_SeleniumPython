# Kskin Customer App — Clean Mobile Suites

Greenfield Appium suites. **Do not** run `one_click/patch_*.py`, `add_*.py`, or
`restore_claude_*` against these files. The old MCP_Appium_Server signup tree is frozen.

## Android signup + login

```bash
# once
cd ~/AquaProjects/KskinCMS
git pull
bash mobile_clean/android_signup_login/install_desktop_command.sh

# every run (Appium + emulator already up)
# double-click Desktop: run-android-signup-login-CLEAN.command
# or:
bash mobile_clean/android_signup_login/run_android_signup_login.command
```

Package: `com.kskinfacial.customer.uat` (override with `ANDROID_UAT_PACKAGE`).
