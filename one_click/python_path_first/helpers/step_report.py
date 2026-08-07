"""
Pace shim for Appium / shared helpers.step_report.

Put this package FIRST on PYTHONPATH so `from helpers.step_report import StepReporter`
loads a wrapped reporter that:
  - prints a clear STEP banner
  - pauses after each recorded step (STEP_PAUSE_SEC, default 2.5)

Real implementation is loaded from:
  $APPIUM_PY/helpers/step_report.py  (or AQUA/MCP_Appium_Server/python/...)
"""
from __future__ import annotations

import importlib.util
import os
import sys
import time
from pathlib import Path


def _load_real():
    roots = []
    if os.environ.get("APPIUM_PY"):
        roots.append(Path(os.environ["APPIUM_PY"]))
    aqua = Path(os.environ.get("AQUA_ROOT", Path.home() / "AquaProjects"))
    roots.append(aqua / "MCP_Appium_Server" / "python")
    # Also allow explicit override
    if os.environ.get("REAL_STEP_REPORT"):
        roots.insert(0, Path(os.environ["REAL_STEP_REPORT"]).parent.parent)

    last_err = None
    for root in roots:
        path = root / "helpers" / "step_report.py"
        if not path.is_file():
            continue
        try:
            spec = importlib.util.spec_from_file_location(
                "_kskin_real_step_report", str(path)
            )
            mod = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(mod)
            return mod
        except Exception as e:
            last_err = e
            continue
    raise ImportError(
        "Cannot load real helpers/step_report.py from Appium python tree. "
        f"Tried {[str(r) for r in roots]}. Last error: {last_err!r}"
    )


_real = _load_real()
StepReporter = _real.StepReporter  # type: ignore

# Re-export anything else the real module exposes
for _name in dir(_real):
    if _name.startswith("_"):
        continue
    if _name == "StepReporter":
        continue
    globals()[_name] = getattr(_real, _name)

_orig_record = StepReporter.record_step
_orig_init = StepReporter.init


def _pause() -> float:
    try:
        return max(0.0, float(os.environ.get("STEP_PAUSE_SEC", "2.5")))
    except ValueError:
        return 2.5


def _pre() -> float:
    try:
        return max(0.0, float(os.environ.get("STEP_PRE_PAUSE_SEC", "0.5")))
    except ValueError:
        return 0.5


def init(self, *args, **kwargs):  # noqa: N802 — bound later
    _orig_init(self, *args, **kwargs)
    self._kskin_total_hint = 0
    print(
        f"\n[one-click pace] STEP_PAUSE_SEC={_pause()}s "
        f"(watch device/simulator between steps)\n",
        flush=True,
    )


def record_step(self, num, title, expected, actual, status):  # noqa: N802
    line = "=" * 64
    print(f"\n{line}", flush=True)
    print(f"  STEP {num}: {title}", flush=True)
    print(f"  Expected : {expected}", flush=True)
    print(f"  Actual   : {actual}", flush=True)
    print(f"  Status   : {status}", flush=True)
    print("  >> Look at the device / simulator now…", flush=True)
    print(f"{line}\n", flush=True)
    if _pre():
        time.sleep(_pre())
    _orig_record(self, num, title, expected, actual, status)
    p = _pause()
    if p:
        time.sleep(p)


StepReporter.init = init  # type: ignore
StepReporter.record_step = record_step  # type: ignore
