# Agent guardrails — QA Confidence Workflow

Stable pre/post rules for agents updating mappings or answering “can we skip this manual case?”

## Pre (before coding or claiming confidence)

1. Read the case YAML (if any) and linked scenario in `qa-confidence/scenarios/`.
2. Read `trust_policy.yaml` — pick the **cheapest** CMS layer that answers the risk.
3. Check `nearby_tests` / existing KskinCMS helpers (`cms_auth`, `playwright_auth`, module scripts). Match repo patterns; one module / one browser / one login.
4. Soft-fails → treat as **Failed**, not Pass. Do not invent edit actions on view-only modules.

## Post (after automation or mapping change)

1. State **layer** added (`listing_smoke` | `validations` | `qa_crud` | `cross_module_e2e`).
2. Give a **confidence estimate** (`trusted` | `review` | `manual` | …) — slightly pessimistic.
3. List remaining **caveats** that block `trusted`.
4. **Update** the scenario/case YAML — do not leave mapping stale.
5. Do **not** overstate: confidence ≠ “a test exists”; never claim `trusted` with open caveats.
6. Regenerate the report when mappings or run evidence change.

## CMS hard rules (always)

- QA-item status toggles only (Gift Card singleton exception).
- Actions first: inspect listing/detail actions before automating.
- StepReporter HTML under `reports/` is the run report; this confidence report is for skip/manual triage.
