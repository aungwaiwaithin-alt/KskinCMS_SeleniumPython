# One-click runners (Mac)

Double-click `.command` files to:

1. Run the suite with **visible paced steps** (not too fast)
2. Emit the dark HTML step report
3. **Open it in Google Chrome**

## Install on your Mac

```bash
# 1) Pull this branch into your AquaProjects CMS tree
cd ~/AquaProjects/KskinCMS   # or wherever the repo lives
git fetch && git checkout cursor/cloud-agent-1785985588759-2j70j
git pull

# 2) Ensure symlink name used by PYTHONPATH
ln -sfn "$(pwd)" ~/AquaProjects/KskinCMS

# 3) Install / refresh Finder one-click pack (backs up working mobile scripts)
bash one_click/install_one_click_commands.sh
# optional explicit destination:
# bash one_click/install_one_click_commands.sh "$HOME/Desktop/One click bash files"
```

## What was wrong

| Issue | Cause | Fix |
|--------|--------|-----|
| CMS `.command` tiny stubs fail / no report in Chrome | `set -e` skipped `open` after failed Python; brittle paths; `open` not Chrome | Shared `scripts/one_click_lib.sh` + always open Chrome after emit |
| Steps too fast to watch | No pause between steps | `STEP_PAUSE_SEC` (default 2.5 CMS / 3 mobile) + banners |
| Mobile signup OK but blur | Same | Pace shim wraps `helpers.step_report` |
| Mobile regression many fails | Usually app/device/locator drift — not the `.command` wrapper | Wrapper restored; use report screenshots; re-smoke signup first |

## Pace controls

```bash
STEP_PAUSE_SEC=4 STEP_PRE_PAUSE_SEC=1 open ~/Desktop/One\ click\ bash\ files/run-kskin-cms-product.command
```

## Files

- `one_click/run-kskin-cms-*.command` — CMS modules
- `one_click/run-*-signup-login.command` etc. — mobile wrappers (need `*.legacy` from installer backup)
- `one_click/python_path_first/helpers/step_report.py` — mobile pace shim
- `scripts/one_click_lib.sh` + `report_runner_util.py` — CMS paced runner
- Module `*_Module/run_*_report.bash` — actual CMS suites (headed browser)
