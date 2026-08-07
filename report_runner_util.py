"""Shared paced step runner for one-click CMS / mobile HTML report suites."""
from __future__ import annotations

import os
import sys
import time
import traceback
from typing import Any, Callable, List, Optional, Sequence, Tuple

Case = Tuple[int, str, str, Callable[[], Any]]


def step_pause_sec() -> float:
    try:
        return max(0.0, float(os.environ.get("STEP_PAUSE_SEC", "2.5")))
    except ValueError:
        return 2.5


def step_pre_pause_sec() -> float:
    try:
        return max(0.0, float(os.environ.get("STEP_PRE_PAUSE_SEC", "0.8")))
    except ValueError:
        return 0.8


def _banner(num: int, total: int, title: str, expected: str) -> None:
    line = "=" * 64
    print(f"\n{line}", flush=True)
    print(f"  STEP {num}/{total}: {title}", flush=True)
    print(f"  Expected : {expected}", flush=True)
    print("  >> Watch the browser / device now (not rushing)…", flush=True)
    print(f"{line}\n", flush=True)


def run_paced_steps(
    reporter: Any,
    cases: Sequence[Case],
    quit_fn: Optional[Callable[[], Any]] = None,
    report_path: Optional[str] = None,
) -> int:
    """
    Run cases with visible banners + pauses. Always emit HTML when possible.
    Returns process exit code (0=all pass).
    """
    out = report_path or os.environ.get("CMS_REPORT_HTML") or os.environ.get("REPORT_HTML")
    if not out:
        raise RuntimeError("CMS_REPORT_HTML / REPORT_HTML not set")

    pause = step_pause_sec()
    pre = step_pre_pause_sec()
    continue_on_fail = os.environ.get("CONTINUE_ON_FAIL", "").strip() in ("1", "true", "yes")
    failed = False
    total = len(cases)

    print(
        f"\nPacing: STEP_PRE_PAUSE_SEC={pre}s, STEP_PAUSE_SEC={pause}s "
        f"(export to change)\n",
        flush=True,
    )

    try:
        for num, title, expected, fn in cases:
            _banner(num, total, title, expected)
            if pre:
                time.sleep(pre)
            try:
                fn()
                reporter.record_step(num, title, expected, "OK — step completed", "pass")
                print(f"[PASS] Step {num}: {title}", flush=True)
            except Exception as e:
                reporter.record_step(num, title, expected, f"FAIL: {e}", "fail")
                print(f"[FAIL] Step {num}: {e}", flush=True)
                traceback.print_exc()
                failed = True
                if not continue_on_fail:
                    if pause:
                        time.sleep(pause)
                    break
            if pause:
                time.sleep(pause)
    finally:
        try:
            os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
            reporter.emit(out)
            print(f"REPORT: {out}", flush=True)
        except Exception as emit_err:
            print(f"REPORT EMIT FAILED: {emit_err}", flush=True)
            failed = True
        if quit_fn is not None:
            try:
                quit_fn()
            except Exception as qe:
                print(f"quit warning: {qe}", flush=True)

    return 1 if failed else 0
