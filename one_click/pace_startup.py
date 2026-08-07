# Force-visible pacing for Appium one-click runs.
# Loaded via PYTHONSTARTUP so it still works when a legacy .command resets PYTHONPATH.
import atexit
import os
import sys
import time


def _log(msg: str) -> None:
    print(f"[one-click pace] {msg}", flush=True)


def _pause() -> float:
    try:
        return max(0.0, float(os.environ.get("STEP_PAUSE_SEC", "3")))
    except ValueError:
        return 3.0


def _install_patch() -> None:
    if getattr(sys, "_kskin_pace_patched", False):
        return
    try:
        import helpers.step_report as sr  # noqa: WPS433
    except Exception as exc:
        _log(f"helpers.step_report not importable yet ({exc}); will retry on exit/hooks")
        return

    if getattr(sr.StepReporter.record_step, "_kskin_paced", False):
        sys._kskin_pace_patched = True  # type: ignore[attr-defined]
        return

    orig = sr.StepReporter.record_step

    def paced(self, num, title, expected, actual, status):  # noqa: ANN001
        line = "=" * 64
        print(f"\n{line}", flush=True)
        print(f"  STEP {num}: {title}", flush=True)
        print(f"  Expected : {expected}", flush=True)
        print(f"  Actual   : {str(actual)[:200]}", flush=True)
        print(f"  Status   : {status}", flush=True)
        print("  >> Watch the iPhone / Android device now…", flush=True)
        print(f"{line}\n", flush=True)
        orig(self, num, title, expected, actual, status)
        p = _pause()
        if p:
            time.sleep(p)

    paced._kskin_paced = True  # type: ignore[attr-defined]
    sr.StepReporter.record_step = paced  # type: ignore[assignment]
    sys._kskin_pace_patched = True  # type: ignore[attr-defined]
    _log(f"patched StepReporter.record_step (STEP_PAUSE_SEC={_pause()})")


# Patch now (if helpers already importable) and again right before process exit
_install_patch()
atexit.register(_install_patch)

# Wrap import so the first helpers.step_report import gets patched
try:
    import builtins as _builtins_mod
except ImportError:  # pragma: no cover
    _builtins_mod = __builtins__  # type: ignore

_orig_import = _builtins_mod.__import__


def _import(name, globals=None, locals=None, fromlist=(), level=0):  # noqa: A002,ANN001
    mod = _orig_import(name, globals, locals, fromlist, level)
    if name == "helpers.step_report" or (
        name == "helpers" and fromlist and "step_report" in fromlist
    ):
        _install_patch()
    return mod


_builtins_mod.__import__ = _import  # type: ignore[attr-defined]
_log("pace bootstrap active — waiting for StepReporter…")
