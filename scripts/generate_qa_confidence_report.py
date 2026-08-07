#!/usr/bin/env python3
"""Generate QA confidence HTML + JSON from authored YAML mappings.

Framework Python 3.8+. Requires PyYAML.

  python3 scripts/generate_qa_confidence_report.py
  python3 scripts/generate_qa_confidence_report.py --include-examples
  python3 scripts/generate_qa_confidence_report.py --run-report reports/KS-CMS-….html
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.stderr.write(
        "PyYAML required: pip install pyyaml\n"
        "Documented in qa-confidence/README.md\n"
    )
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parents[1]
QC = ROOT / "qa-confidence"
SCENARIOS_DIR = QC / "scenarios"
CASES_DIR = QC / "cases"
OUT_DIR = QC / "generated"
POLICY_PATH = QC / "trust_policy.yaml"

BUCKET_ORDER = (
    "trusted",
    "review",
    "manual",
    "failed",
    "not-tested",
    "unmapped",
)


def _load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _is_demo_path(path: Path) -> bool:
    return path.name.startswith("_example")


def _is_demo_doc(doc: Dict[str, Any], path: Path) -> bool:
    if doc.get("example") is True:
        return True
    return _is_demo_path(path)


def _expand_docs(path: Path, doc: Any) -> List[Dict[str, Any]]:
    """One file = one mapping, or a list under scenarios:/cases:/items:."""
    if isinstance(doc, list):
        return [d for d in doc if isinstance(d, dict)]
    if not isinstance(doc, dict):
        return []
    for key in ("scenarios", "cases", "items"):
        if isinstance(doc.get(key), list):
            shared_example = doc.get("example")
            shared_module = doc.get("module")
            rows: List[Dict[str, Any]] = []
            for item in doc[key]:
                if not isinstance(item, dict):
                    continue
                row = dict(item)
                if shared_example is not None and "example" not in row:
                    row["example"] = shared_example
                if shared_module and "module" not in row:
                    row["module"] = shared_module
                rows.append(row)
            return rows
    return [doc]


def _iter_yaml(dir_path: Path) -> List[Tuple[Path, Dict[str, Any]]]:
    if not dir_path.is_dir():
        return []
    out: List[Tuple[Path, Dict[str, Any]]] = []
    for path in sorted(dir_path.glob("*.yaml")):
        raw = _load_yaml(path)
        for doc in _expand_docs(path, raw):
            out.append((path, doc))
    return out


def _parse_run_report(path: Optional[Path]) -> Dict[str, Any]:
    """Light parse of StepReporter HTML: total/pass/fail + suite id from title."""
    meta: Dict[str, Any] = {
        "path": str(path) if path else None,
        "suite_id": None,
        "total": None,
        "passed": None,
        "failed": None,
        "overall_fail": None,
    }
    if not path or not path.is_file():
        return meta
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(
        r"<title>\s*(KS-CMS-[A-Z0-9-]+)",
        text,
        re.I,
    )
    if m:
        meta["suite_id"] = m.group(1)
    else:
        m2 = re.search(r"(KS-CMS-[A-Z0-9-]+)", text)
        if m2:
            meta["suite_id"] = m2.group(1)

    def _stat(label: str) -> Optional[int]:
        pat = (
            r'data-filter="[^"]*".*?<div class="k">%s</div>\s*'
            r'<div class="v"[^>]*>\s*(\d+)\s*</div>'
            % re.escape(label)
        )
        mm = re.search(pat, text, re.S | re.I)
        if mm:
            return int(mm.group(1))
        # fallback plain text
        mm = re.search(
            r"%s</div>\s*<div class=\"v\"[^>]*>\s*(\d+)" % re.escape(label),
            text,
            re.S | re.I,
        )
        return int(mm.group(1)) if mm else None

    meta["total"] = _stat("Total Steps")
    meta["passed"] = _stat("Passed")
    meta["failed"] = _stat("Failed")
    if re.search(r'verdict\s+fail|Overall:\s*FAIL', text, re.I):
        meta["overall_fail"] = True
    elif re.search(r'verdict\s+pass|Overall:\s*PASS', text, re.I):
        meta["overall_fail"] = False
    if meta["failed"] is not None:
        meta["overall_fail"] = meta["failed"] > 0
    return meta


def _effective_confidence(
    authored: str,
    scenario: Dict[str, Any],
    run: Dict[str, Any],
) -> str:
    """Adjust authored bucket using optional run report (pessimistic)."""
    conf = (authored or "manual").strip().lower()
    if conf not in BUCKET_ORDER:
        conf = "manual"
    suite = (scenario.get("automation") or {}).get("suite_id")
    if not run.get("path") or not suite:
        return conf
    if run.get("suite_id") and run["suite_id"] != suite:
        # different suite attached — do not force not-tested globally
        return conf
    if run.get("overall_fail") is True:
        return "failed"
    if run.get("total") == 0:
        return "not-tested"
    if run.get("failed") and run["failed"] > 0:
        return "failed"
    return conf


def build_payload(
    include_examples: bool,
    run_report: Optional[Path],
) -> Dict[str, Any]:
    policy = _load_yaml(POLICY_PATH) if POLICY_PATH.is_file() else {}
    run = _parse_run_report(run_report)

    scenarios_raw: List[Dict[str, Any]] = []
    demo_scenario_count = 0
    for path, doc in _iter_yaml(SCENARIOS_DIR):
        demo = _is_demo_doc(doc, path)
        if demo:
            demo_scenario_count += 1
            if not include_examples:
                continue
        sid = doc.get("scenario_id") or path.stem
        authored = str(doc.get("confidence") or "manual")
        effective = _effective_confidence(authored, doc, run)
        scenarios_raw.append(
            {
                "scenario_id": sid,
                "title": doc.get("title") or sid,
                "module": doc.get("module") or "",
                "example": demo,
                "manual_case_ids": list(doc.get("manual_case_ids") or []),
                "automation": doc.get("automation") or {},
                "layer": doc.get("layer") or "",
                "confidence_authored": authored,
                "confidence": effective,
                "caveats": list(doc.get("caveats") or []),
                "recommended_next": doc.get("recommended_next") or "",
                "nearby_tests": list(doc.get("nearby_tests") or []),
                "source": str(path.relative_to(ROOT)),
            }
        )

    cases_raw: List[Dict[str, Any]] = []
    demo_case_count = 0
    linked_case_ids = set()
    for path, doc in _iter_yaml(CASES_DIR):
        demo = _is_demo_doc(doc, path)
        if demo:
            demo_case_count += 1
            if not include_examples:
                continue
        cid = doc.get("case_id") or path.stem
        sid = doc.get("scenario_id") or ""
        if sid:
            linked_case_ids.add(cid)
        cases_raw.append(
            {
                "case_id": cid,
                "title": doc.get("title") or cid,
                "module": doc.get("module") or "",
                "example": demo,
                "scenario_id": sid,
                "notes": doc.get("notes") or "",
                "source": str(path.relative_to(ROOT)),
            }
        )

    scenario_by_id = {s["scenario_id"]: s for s in scenarios_raw}
    buckets: Dict[str, List[Dict[str, Any]]] = {b: [] for b in BUCKET_ORDER}

    for s in scenarios_raw:
        buckets[s["confidence"]].append(
            {"kind": "scenario", **s}
        )

    unmapped_cases = []
    for c in cases_raw:
        if not c["scenario_id"]:
            unmapped_cases.append(c)
            buckets["unmapped"].append({"kind": "case", **c})
        elif c["scenario_id"] not in scenario_by_id:
            # broken link → unmapped
            unmapped_cases.append(c)
            buckets["unmapped"].append(
                {
                    "kind": "case",
                    **c,
                    "notes": (c.get("notes") or "")
                    + " [scenario_id not found in loaded scenarios]",
                }
            )

    demo_mode = bool(
        include_examples
        and (demo_scenario_count or demo_case_count)
        and not any(not s["example"] for s in scenarios_raw)
    )
    # Also demo banner if only examples included
    only_examples = include_examples and scenarios_raw and all(
        s["example"] for s in scenarios_raw
    )

    next_prompts = [
        {
            "title": "Seed a real module",
            "body": (
                "/QA_ConfidenceWorkflow\n"
                "Seed scenario+case YAML for module <Name> from green suite "
                "KS-CMS-… — start review, not trusted."
            ),
        },
        {
            "title": "Skip-manual decision",
            "body": (
                "/QA_ConfidenceWorkflow\n"
                "Manual case: <MC-…>\n"
                "Can we skip? Follow prompts/agent_guardrails.md."
            ),
        },
        {
            "title": "Attach latest run",
            "body": (
                "python3 scripts/generate_qa_confidence_report.py "
                "--run-report reports/KS-CMS-….html"
            ),
        },
    ]

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "demo_banner": only_examples or demo_mode,
        "include_examples": include_examples,
        "demo_files_skipped": (not include_examples)
        and (demo_scenario_count + demo_case_count > 0),
        "demo_scenario_count_on_disk": demo_scenario_count,
        "demo_case_count_on_disk": demo_case_count,
        "policy_version": policy.get("version"),
        "buckets_policy": policy.get("buckets") or {},
        "cms_cheapest_layer_order": policy.get("cms_cheapest_layer_order") or [],
        "run_report": run,
        "scenarios": scenarios_raw,
        "cases": cases_raw,
        "buckets": {k: buckets[k] for k in BUCKET_ORDER},
        "counts": {k: len(buckets[k]) for k in BUCKET_ORDER},
        "next_prompts": next_prompts,
        "unmapped_case_count": len(unmapped_cases),
    }


def _esc(s: Any) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render_html(payload: Dict[str, Any]) -> str:
    counts = payload["counts"]
    banner = ""
    if payload.get("demo_banner"):
        banner = (
            '<div class="banner demo">DEMO / template data only — '
            "not release guidance. Seed real module YAML before skip-manual.</div>"
        )
    elif payload.get("demo_files_skipped"):
        banner = (
            '<div class="banner info">Demo/_example_* files skipped '
            "(pass --include-examples to show them).</div>"
        )

    run = payload.get("run_report") or {}
    run_line = "No run report attached."
    if run.get("path"):
        run_line = (
            "Run report: <code>%s</code> suite=<code>%s</code> "
            "passed=%s failed=%s overall_fail=%s"
            % (
                _esc(run.get("path")),
                _esc(run.get("suite_id") or "?"),
                _esc(run.get("passed")),
                _esc(run.get("failed")),
                _esc(run.get("overall_fail")),
            )
        )

    def items_html(bucket: str) -> str:
        rows = payload["buckets"].get(bucket) or []
        if not rows:
            return '<p class="empty">None</p>'
        parts = ['<ul class="items">']
        for row in rows:
            kind = row.get("kind")
            if kind == "scenario":
                caveats = "".join(
                    "<li>%s</li>" % _esc(c) for c in (row.get("caveats") or [])
                )
                caveats_block = (
                    "<ul class=\"caveats\">%s</ul>" % caveats if caveats else ""
                )
                demo = ' <span class="tag">demo</span>' if row.get("example") else ""
                parts.append(
                    "<li><strong>%s</strong>%s — %s"
                    "<div class=\"meta\">module=%s · layer=%s · authored=%s"
                    " · suite=%s</div>%s"
                    "<div class=\"next\">%s</div></li>"
                    % (
                        _esc(row.get("scenario_id")),
                        demo,
                        _esc(row.get("title")),
                        _esc(row.get("module")),
                        _esc(row.get("layer")),
                        _esc(row.get("confidence_authored")),
                        _esc((row.get("automation") or {}).get("suite_id") or "—"),
                        caveats_block,
                        _esc(row.get("recommended_next") or ""),
                    )
                )
            else:
                demo = ' <span class="tag">demo</span>' if row.get("example") else ""
                parts.append(
                    "<li><strong>%s</strong>%s — %s"
                    "<div class=\"meta\">module=%s · scenario_id=%s</div>"
                    "<div class=\"next\">%s</div></li>"
                    % (
                        _esc(row.get("case_id")),
                        demo,
                        _esc(row.get("title")),
                        _esc(row.get("module")),
                        _esc(row.get("scenario_id") or "(none)"),
                        _esc(row.get("notes") or ""),
                    )
                )
        parts.append("</ul>")
        return "\n".join(parts)

    sections = []
    titles = {
        "trusted": "Trusted",
        "review": "Review",
        "manual": "Manual",
        "failed": "Failed",
        "not-tested": "Not-tested",
        "unmapped": "Unmapped",
    }
    for b in BUCKET_ORDER:
        sections.append(
            '<section class="bucket" id="%s">'
            "<h2>%s <span class=\"count\">%s</span></h2>%s</section>"
            % (_esc(b), _esc(titles[b]), counts.get(b, 0), items_html(b))
        )

    prompts = "".join(
        "<li><strong>%s</strong><pre>%s</pre></li>"
        % (_esc(p["title"]), _esc(p["body"]))
        for p in payload.get("next_prompts") or []
    )

    layers = "".join(
        "<li><code>%s</code> — %s</li>"
        % (_esc(x.get("id")), _esc(x.get("label")))
        for x in payload.get("cms_cheapest_layer_order") or []
    )

    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>QA Confidence Report</title>
<style>
  :root {
    --bg: #0f1419; --card: #1a2332; --text: #e7ecf3; --muted: #9aa7b8;
    --accent: #3b82f6; --warn: #f59e0b; --ok: #22c55e; --bad: #ef4444;
    --border: #2a3548;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; font-family: ui-sans-serif, system-ui, sans-serif;
    background: var(--bg); color: var(--text); line-height: 1.45;
    padding: 24px;
  }
  h1 { font-size: 1.5rem; margin: 0 0 8px; }
  h2 { font-size: 1.1rem; margin: 0 0 12px; }
  .sub { color: var(--muted); margin-bottom: 16px; }
  .banner {
    padding: 12px 14px; border-radius: 8px; margin-bottom: 16px;
    border: 1px solid var(--border);
  }
  .banner.demo { background: #3a2a10; border-color: var(--warn); color: #fde68a; }
  .banner.info { background: #152033; color: var(--muted); }
  .stats {
    display: flex; flex-wrap: wrap; gap: 10px; margin: 16px 0 24px;
  }
  .stat {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 8px; padding: 10px 14px; min-width: 110px;
  }
  .stat .k { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; }
  .stat .v { font-size: 1.4rem; font-weight: 700; }
  .bucket {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; padding: 16px 18px; margin-bottom: 14px;
  }
  .count {
    display: inline-block; background: #243044; border-radius: 999px;
    padding: 2px 10px; font-size: 0.85rem; margin-left: 6px;
  }
  .items { margin: 0; padding-left: 18px; }
  .items li { margin-bottom: 12px; }
  .meta, .next { color: var(--muted); font-size: 0.9rem; margin-top: 4px; }
  .caveats { margin: 6px 0 0; color: #fbbf24; }
  .tag {
    background: #92400e; color: #fde68a; font-size: 0.7rem;
    padding: 1px 6px; border-radius: 4px; vertical-align: middle;
  }
  .empty { color: var(--muted); margin: 0; }
  pre {
    background: #0b1018; border: 1px solid var(--border); padding: 10px;
    border-radius: 6px; overflow: auto; white-space: pre-wrap;
  }
  code { font-family: ui-monospace, monospace; font-size: 0.9em; }
  a { color: var(--accent); }
</style>
</head>
<body>
  <h1>QA Confidence Report</h1>
  <div class="sub">Generated %s · policy v%s · distinct from StepReporter run HTML</div>
  %s
  <p class="sub">%s</p>
  <div class="stats">
    %s
  </div>
  <section class="bucket">
    <h2>CMS cheapest layer order</h2>
    <ol>%s</ol>
  </section>
  %s
  <section class="bucket">
    <h2>Next prompts</h2>
    <ul>%s</ul>
  </section>
</body>
</html>
""" % (
        _esc(payload.get("generated_at")),
        _esc(payload.get("policy_version")),
        banner,
        run_line,
        "".join(
            '<div class="stat"><div class="k">%s</div><div class="v">%s</div></div>'
            % (_esc(k), counts.get(k, 0))
            for k in BUCKET_ORDER
        ),
        layers,
        "\n".join(sections),
        prompts,
    )


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Generate QA confidence report")
    ap.add_argument(
        "--include-examples",
        action="store_true",
        help="Include _example_* / example:true demo mappings",
    )
    ap.add_argument(
        "--run-report",
        type=str,
        default=None,
        help="Optional StepReporter HTML path for light pass/fail adjustment",
    )
    ap.add_argument(
        "--out-dir",
        type=str,
        default=str(OUT_DIR),
        help="Output directory (default: qa-confidence/generated)",
    )
    args = ap.parse_args(argv)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_path = Path(args.run_report) if args.run_report else None
    if run_path and not run_path.is_file():
        sys.stderr.write("Run report not found: %s\n" % run_path)
        return 1

    payload = build_payload(args.include_examples, run_path)
    html_path = out_dir / "qa_confidence_report.html"
    json_path = out_dir / "qa_confidence_report.json"
    html_path.write_text(render_html(payload), encoding="utf-8")
    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    print("Wrote", html_path)
    print("Wrote", json_path)
    print(
        "counts:",
        ", ".join("%s=%s" % (k, payload["counts"][k]) for k in BUCKET_ORDER),
    )
    if payload.get("demo_files_skipped"):
        print(
            "note: demo examples skipped "
            "(%s scenarios, %s cases on disk) — use --include-examples"
            % (
                payload["demo_scenario_count_on_disk"],
                payload["demo_case_count_on_disk"],
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
