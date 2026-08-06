---
name: QA_ConfidenceWorkflow
description: >-
  Map Kskin CMS manual cases to automation scenarios, estimate skip-vs-manual
  confidence (slightly pessimistic), and update qa-confidence YAML + generated
  report. Invoke with /QA_ConfidenceWorkflow, when asked “can we skip this
  manual case?”, or when seeding/updating confidence mappings after a green run.
---

# QA Confidence Workflow

Use this skill for **traceability + confidence** (skip vs manual), not for inventing extra pass/fail suites.

## When to invoke

- User says **`/QA_ConfidenceWorkflow`**
- “Can we skip this manual case?” / “how confident are we?”
- Seeding or updating `qa-confidence/scenarios/` or `cases/` after automation work
- Attaching a StepReporter HTML to refresh failed / not-tested hints

## Canonical paths

**Single source of truth = this CMS automation git repo** (`qa-confidence/` next to module scripts).

- Authored: `qa-confidence/`
- Generator: `scripts/generate_qa_confidence_report.py`
- Versioned skill: `qa-confidence/skill/SKILL.md`
- Install to Cursor: `bash qa-confidence/skill/install.sh`
- Optional Mac notes mirror: `bash qa-confidence/skill/sync-to-notes.sh` (one-way copy for people who keep HTML under `~/kskin-web(cms)-automation/reports/`)

Read first: `qa-confidence/README.md`, `prompts/agent_guardrails.md`, `trust_policy.yaml`, `schema.md`.

## Pre

- Load the case + linked scenario (if any).
- Choose the **cheapest** CMS layer: listing smoke → validations → QA CRUD → cross-module E2E.
- Reuse existing helpers (`cms_auth` / `playwright_auth` / module scripts). One module, one browser, one login.
- Soft-fails → Failed. No invented edits on view-only modules.

## Post

- State layer added, confidence estimate, remaining caveats.
- **Update** scenario/case YAML **in this repo** — do not leave mapping stale; do not treat a notes-folder copy as canonical.
- Never claim `trusted` with open caveats; stay slightly pessimistic.
- Regenerate:

```bash
python3 scripts/generate_qa_confidence_report.py
python3 scripts/generate_qa_confidence_report.py --include-examples
python3 scripts/generate_qa_confidence_report.py --run-report reports/KS-CMS-….html
```

## Report separation

| Report | Purpose |
|--------|---------|
| StepReporter `reports/KS-CMS-*.html` | Run pass/fail + screenshots |
| `qa-confidence/generated/qa_confidence_report.html` | Skip / review / manual decisions |

## Seeded today

- **Products** — 11 scenarios `trusted` (suite `KS-CMS-PRODUCT-001`). Re-check if the suite goes red.
- `_example_*` — demo only.
