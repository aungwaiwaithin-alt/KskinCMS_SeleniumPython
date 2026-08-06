# QA Confidence Workflow (Kskin CMS)

Traceability + confidence for **skip vs manual** decisions — not another pass/fail suite.

Authored mappings live here. Generated HTML/JSON under `generated/` (gitignored). Existing StepReporter reports under `reports/` stay the **run** evidence (pass/fail + screenshots).

## Quick start

```bash
# From repo root (this package)
python3 scripts/generate_qa_confidence_report.py

# Include demo/_example_* mappings (default skips them)
python3 scripts/generate_qa_confidence_report.py --include-examples

# Fold in a StepReporter HTML lightly (pass/fail counts → failed / not-tested hints)
python3 scripts/generate_qa_confidence_report.py \
  --run-report reports/KS-CMS-PRODUCT-001_products.html

open qa-confidence/generated/qa_confidence_report.html   # or xdg-open
```

Requires Python 3.8+ and PyYAML (`pip install pyyaml`).

## Layout

```
qa-confidence/
  README.md              # this file
  trust_policy.yaml      # buckets + cheapest CMS layer order
  schema.md              # field meanings
  scenarios/             # automation ↔ risk mappings
  cases/                 # manual cases → scenario_id
  prompts/               # agent guardrails + copyable prompt
  generated/             # output (gitignored)
```

## Confidence buckets (slightly pessimistic)

| Bucket | Meaning |
|--------|---------|
| `trusted` | Strong evidence — usually skip manual |
| `review` | Useful automation — spot-check before skip |
| `manual` | Too weak — run manually |
| `failed` | Mapped run failed — investigate |
| `not-tested` | Mapped but not in latest run |
| `unmapped` | Case with no scenario link |

Hard rule: confidence ≠ “a test exists”. Never claim `trusted` with open caveats.

## CMS cheapest reliable layer

1. Listing / search / pagination smoke  
2. Required-field / validation asserts  
3. CRUD on QA-owned items (create/edit/status + restore)  
4. Cross-module / E2E only when risk needs it  

## Agent invoke

Use **`/QA_ConfidenceWorkflow`** (skill `QA_ConfidenceWorkflow`).  
Read `prompts/agent_guardrails.md` before changing mappings or answering skip-manual questions.

Cursor loads personal skills from `~/.cursor/skills/`, which no repo tracks. The versioned copy lives in `skill/SKILL.md`; install or restore it with:

```bash
bash qa-confidence/skill/install.sh
```

Then reload Cursor so the slash command appears.

## Framework-only note

`_example_*` files are **demo templates**. Seed real modules (Products, Beacons, …) as separate YAML after green suites — do not treat examples as release guidance.
