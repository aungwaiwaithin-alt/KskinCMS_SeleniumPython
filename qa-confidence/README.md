# QA Confidence Workflow (Kskin CMS)

Traceability + confidence for **skip vs manual** decisions — not another pass/fail suite.

## Canonical home (single source of truth)

**This CMS automation git repo** owns authored mappings + the skill installer:

| What | Where |
|------|--------|
| Authored YAML / policy / prompts | `qa-confidence/` (this repo) |
| Generator | `scripts/generate_qa_confidence_report.py` |
| Cursor skill (versioned) | `qa-confidence/skill/SKILL.md` |
| Skill install (local Cursor) | `bash qa-confidence/skill/install.sh` |
| StepReporter run HTML | Usually `~/kskin-web(cms)-automation/reports/` on your Mac |

Optional Mac notes mirror (HTML reports folder only — **not** the source of truth):

```bash
bash qa-confidence/skill/sync-to-notes.sh
```

That copies authored YAML one-way into `~/kskin-web(cms)-automation/qa-confidence/` and reinstalls the skill. Edit mappings **here**, then sync if you want the notes tree updated.

## Quick start

```bash
# From this repo root
python3 scripts/generate_qa_confidence_report.py

# Include demo/_example_* mappings (default skips them)
python3 scripts/generate_qa_confidence_report.py --include-examples

# Fold in a StepReporter HTML lightly
python3 scripts/generate_qa_confidence_report.py \
  --run-report /path/to/KS-CMS-PRODUCT-001_products.html

open qa-confidence/generated/qa_confidence_report.html   # or xdg-open
```

Requires Python 3.8+ and PyYAML (`pip install pyyaml`).

## Layout

```
qa-confidence/
  README.md
  trust_policy.yaml
  schema.md
  scenarios/             # real modules + _example_*
  cases/
  prompts/
  skill/                 # versioned Cursor skill + installers
  generated/             # gitignored output
```

## Seeded modules

| Module | Mapping | Confidence |
|--------|---------|------------|
| Products | `scenarios/product.yaml` + `cases/product_cases.yaml` | **trusted** (11 scenarios; suite KS-CMS-PRODUCT-001) |
| (template) | `_example_*` | demo only — skipped unless `--include-examples` |

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

Use **`/QA_ConfidenceWorkflow`**.  
Read `prompts/agent_guardrails.md` before changing mappings or answering skip-manual questions.

Cursor loads skills from `~/.cursor/skills/` **or** this project's `.cursor/skills/`.

Preferred (no Terminal install): open this CMS repo in Cursor — skill is at `.cursor/skills/QA_ConfidenceWorkflow/SKILL.md`.

Fallback (user-global):

```bash
bash qa-confidence/skill/install.sh
```

Then start a **new** chat (or reload the window) so `/QA_ConfidenceWorkflow` appears.
