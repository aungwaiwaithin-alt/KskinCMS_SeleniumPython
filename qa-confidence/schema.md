# QA Confidence schema

Field meanings for authored scenario and case YAML. Keep mappings honest and slightly pessimistic.

## Scenario (`scenarios/*.yaml`)

One file may be a **single** scenario document, or a batch:

```yaml
module: Products
scenarios:
  - scenario_id: SC-…
    title: …
```

| Field | Required | Meaning |
|-------|----------|---------|
| `scenario_id` | yes | Stable id, e.g. `SC-CMS-PRODUCT-LIST-001` |
| `title` | yes | Short human title |
| `module` | yes | CMS module name (Products, Beacons, …) — may be set once on the batch root |
| `example` | no | If `true`, demo/template only — not release guidance |
| `manual_case_ids` | no | List of linked manual case ids |
| `automation.suite_id` | no | StepReporter / suite id, e.g. `KS-CMS-PRODUCT-001` |
| `automation.script` | no | Path to module script relative to repo |
| `automation.steps` | no | List of step numbers or labels covered |
| `layer` | yes | One of: `listing_smoke`, `validations`, `qa_crud`, `cross_module_e2e` |
| `confidence` | yes | Authored bucket: `trusted` \| `review` \| `manual` \| `failed` \| `not-tested` |
| `caveats` | no | List of remaining risks / gaps |
| `recommended_next` | no | What to automate or spot-check next |
| `nearby_tests` | no | Related suites/scripts to mirror |

### Rules

- Confidence is an **authored judgment**, optionally adjusted by latest run pass/fail.
- Do not set `trusted` while caveats remain that block skip-manual.
- Prefer the cheapest layer from `trust_policy.yaml` that covers the risk.

## Case (`cases/*.yaml`)

One file may be a single case, or:

```yaml
module: Products
cases:
  - case_id: MC-…
    scenario_id: SC-…
```

| Field | Required | Meaning |
|-------|----------|---------|
| `case_id` | yes | Manual / sheet case id |
| `title` | yes | Case title |
| `module` | no | Module name — may be set once on the batch root |
| `example` | no | Demo stub if `true` |
| `scenario_id` | no | Link to a scenario; empty → **unmapped** |
| `notes` | no | Free text |

## Generator behavior

- Files named `_example_*` or with `example: true` are **demo**.
- Default generation skips demo unless `--include-examples`.
- Optional `--run-report path.html` lightly parses StepReporter pass/fail and may move mapped scenarios to `failed` / `not-tested`.
