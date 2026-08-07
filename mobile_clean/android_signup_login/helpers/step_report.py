"""Minimal dark-theme HTML step reporter (self-contained, base64 screenshots)."""
from __future__ import annotations

import base64
import html
import os
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional, Sequence, Tuple


class StepReporter:
    def __init__(self) -> None:
        self.test_case_id = ""
        self.test_name = ""
        self.subtitle = ""
        self.environment: List[Tuple[str, str]] = []
        self.driver: Any = None
        self.steps: List[dict] = []
        self.started = datetime.now()

    def init(
        self,
        test_case_id: str,
        test_name: str,
        subtitle: str = "",
        environment: Optional[Sequence[Tuple[str, str]]] = None,
        driver: Any = None,
    ) -> None:
        self.test_case_id = test_case_id
        self.test_name = test_name
        self.subtitle = subtitle
        self.environment = list(environment or [])
        self.driver = driver
        self.steps = []
        self.started = datetime.now()

    def _shot_b64(self) -> str:
        if self.driver is None:
            return ""
        try:
            raw = self.driver.get_screenshot_as_png()
            return base64.b64encode(raw).decode("ascii")
        except Exception:
            return ""

    def record_step(
        self,
        num: int,
        title: str,
        expected: str,
        actual: str,
        status: str,
    ) -> None:
        status = (status or "").lower()
        if status not in {"pass", "fail", "skip"}:
            status = "fail"
        self.steps.append(
            {
                "num": num,
                "title": title,
                "expected": expected,
                "actual": actual,
                "status": status,
                "shot": self._shot_b64(),
            }
        )

    def emit(self, path: str) -> str:
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        total = len(self.steps)
        passed = sum(1 for s in self.steps if s["status"] == "pass")
        failed = sum(1 for s in self.steps if s["status"] == "fail")
        skipped = sum(1 for s in self.steps if s["status"] == "skip")
        overall = "PASS" if failed == 0 and total > 0 else "FAIL"
        when = self.started.strftime("%Y-%m-%d %H:%M:%S")

        env_rows = "".join(
            f"<tr><th>{html.escape(k)}</th><td>{html.escape(str(v))}</td></tr>"
            for k, v in self.environment
        )
        step_html = []
        for s in self.steps:
            badge = s["status"].upper()
            img = ""
            if s["shot"]:
                img = (
                    f'<img class="shot" alt="step {s["num"]}" '
                    f'src="data:image/png;base64,{s["shot"]}" '
                    f'onclick="openShot(this.src)"/>'
                )
            step_html.append(
                f"""
<article class="step" data-status="{s['status']}">
  <header>
    <span class="num">#{s['num']}</span>
    <span class="badge {s['status']}">{badge}</span>
    <h3>{html.escape(s['title'])}</h3>
  </header>
  <p><b>Expected:</b> {html.escape(s['expected'])}</p>
  <p><b>Actual:</b> {html.escape(s['actual'])}</p>
  {img}
</article>"""
            )

        doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>{html.escape(self.test_case_id)} — {html.escape(self.test_name)}</title>
<style>
:root {{ --bg:#0f1419; --card:#1a222c; --text:#e7ecf1; --muted:#9aa7b5;
  --pass:#3dd68c; --fail:#f07178; --skip:#e6b450; --line:#2a3542; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; font:15px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  background:var(--bg); color:var(--text); }}
.wrap {{ max-width:980px; margin:0 auto; padding:28px 20px 60px; }}
h1 {{ margin:0 0 6px; font-size:1.55rem; }}
.sub {{ color:var(--muted); margin:0 0 18px; }}
.filters button {{ margin:0 8px 12px 0; padding:8px 12px; border-radius:8px;
  border:1px solid var(--line); background:#121820; color:var(--text); cursor:pointer; }}
.filters button.active {{ border-color:#5b9fd4; }}
.summary span {{ display:inline-block; margin-right:14px; padding:4px 10px; border-radius:999px;
  background:#121820; border:1px solid var(--line); }}
.summary .overall.PASS {{ color:var(--pass); }} .summary .overall.FAIL {{ color:var(--fail); }}
table.env {{ width:100%; border-collapse:collapse; margin:16px 0 24px; }}
table.env th, table.env td {{ text-align:left; padding:8px 10px; border-bottom:1px solid var(--line); }}
table.env th {{ width:180px; color:var(--muted); font-weight:600; }}
.step {{ background:var(--card); border:1px solid var(--line); border-radius:12px;
  padding:14px 16px; margin:0 0 14px; }}
.step header {{ display:flex; align-items:center; gap:10px; margin-bottom:8px; }}
.step h3 {{ margin:0; font-size:1.05rem; }}
.num {{ color:var(--muted); }}
.badge {{ font-size:12px; font-weight:700; padding:2px 8px; border-radius:6px; }}
.badge.pass {{ background:rgba(61,214,140,.15); color:var(--pass); }}
.badge.fail {{ background:rgba(240,113,120,.15); color:var(--fail); }}
.badge.skip {{ background:rgba(230,180,80,.15); color:var(--skip); }}
.shot {{ max-width:100%; margin-top:10px; border-radius:8px; border:1px solid var(--line); cursor:zoom-in; }}
#lb {{ display:none; position:fixed; inset:0; background:rgba(0,0,0,.85); align-items:center;
  justify-content:center; z-index:99; }}
#lb.open {{ display:flex; }}
#lb img {{ max-width:92vw; max-height:92vh; border-radius:8px; }}
footer {{ color:var(--muted); margin-top:28px; font-size:13px; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>{html.escape(self.test_case_id)} — {html.escape(self.test_name)}</h1>
  <p class="sub">{html.escape(self.subtitle)}</p>
  <div class="summary">
    <span class="overall {overall}">{overall}</span>
    <span>Total {total}</span>
    <span>Passed {passed}</span>
    <span>Failed {failed}</span>
    <span>Skipped {skipped}</span>
    <span>{when}</span>
  </div>
  <div class="filters">
    <button class="active" data-f="all">Total</button>
    <button data-f="pass">Passed</button>
    <button data-f="fail">Failed</button>
    <button data-f="skip">Skipped</button>
  </div>
  <table class="env">{env_rows}</table>
  {''.join(step_html)}
  <footer>Generated {html.escape(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))} · {html.escape(self.test_case_id)}</footer>
</div>
<div id="lb" onclick="this.classList.remove('open')"><img alt="screenshot"/></div>
<script>
document.querySelectorAll('.filters button').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('.filters button').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const f = btn.dataset.f;
    document.querySelectorAll('.step').forEach(el => {{
      el.style.display = (f === 'all' || el.dataset.status === f) ? '' : 'none';
    }});
  }});
}});
function openShot(src) {{
  const lb = document.getElementById('lb');
  lb.querySelector('img').src = src;
  lb.classList.add('open');
}}
</script>
</body>
</html>"""
        out.write_text(doc, encoding="utf-8")
        print(f"REPORT: {out}", flush=True)
        return str(out)
