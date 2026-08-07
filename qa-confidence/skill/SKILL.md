---
name: QA_ConfidenceWorkflow
description: >-
  Map manual QA cases to automation scenarios and estimate skip-vs-manual
  confidence (slightly pessimistic) for Kskin CMS web, mobile, or other
  AquaProjects suites. Invoke with /QA_ConfidenceWorkflow, when asked “can we
  skip this manual case?”, or after a green run when updating mappings.
---

# QA Confidence Workflow (AquaProjects-wide)

Use for **traceability + confidence** (skip vs manual) across projects under
`/Users/aungwaiwaithin/AquaProjects` — CMS web, mobile, etc.
Not for inventing extra pass/fail suites.

## When to invoke

- User says **`/QA_ConfidenceWorkflow`**
- “Can we skip this manual case?” / “how confident are we?”
- Seeding or updating `qa-confidence/scenarios/` or `cases/` after automation
- Attaching a StepReporter / mobile HTML report to refresh failed / not-tested

## Where things live

| Piece | Location |
|--------|----------|
| This skill (shared source) | `AquaProjects/QA_ConfidenceWorkflow/SKILL.md` |
| Cursor global install | `~/.cursor/skills/QA_ConfidenceWorkflow/SKILL.md` |
| Per-project mappings | `<project>/qa-confidence/` (e.g. `KskinCMS/qa-confidence/`) |
| Generator | `<project>/scripts/generate_qa_confidence_report.py` if present |
| Run HTML | project `reports/` or `~/kskin-web(cms)-automation/reports/` |

**Resolve `qa-confidence/` from the open project first.** If missing, create it there (copy structure from `KskinCMS/qa-confidence/`) — do not invent a second conflicting tree.

Read first in that folder: `README.md`, `prompts/agent_guardrails.md`, `trust_policy.yaml`, `schema.md`.

## Pre

1. Identify platform: **CMS web** vs **mobile** (Appium) vs other.
2. Load case + linked scenario YAML if they exist.
3. Prefer the **cheapest reliable layer**:
   - **CMS web:** listing smoke → validations → QA-item CRUD → cross-module E2E
   - **Mobile:** smoke (launch/login) → single-screen flow → multi-screen / back-press / dialogs → true E2E only if risk needs it
4. Match that project’s helpers (e.g. `cms_auth` / `playwright_auth` / Appium MCP). One session / one login / one module at a time for CMS.
5. Soft-fails → **Failed**. No invented edits on view-only screens.

## Post

1. State **layer** added and **confidence** (`trusted` / `review` / `manual` / …) — slightly pessimistic.
2. List remaining **caveats** that block `trusted`.
3. **Update** that project’s scenario/case YAML — keep mappings in the project that owns the automation.
4. Never claim `trusted` with open caveats.
5. Regenerate if the project has the generator:

```bash
python3 scripts/generate_qa_confidence_report.py
python3 scripts/generate_qa_confidence_report.py --include-examples
python3 scripts/generate_qa_confidence_report.py --run-report reports/<suite>.html
```

## Report separation

| Report | Purpose |
|--------|---------|
| StepReporter / mobile HTML under `reports/` | Run pass/fail + screenshots |
| `qa-confidence/generated/qa_confidence_report.html` | Skip / review / manual decisions |

## CMS hard rules (when in KskinCMS)

- QA-item status toggles only (Gift Card singleton exception).
- Actions first before automating.
- Products are seeded **trusted** (11 scenarios, `KS-CMS-PRODUCT-001`) while that suite stays green.
