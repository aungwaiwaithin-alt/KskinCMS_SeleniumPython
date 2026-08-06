# Kskin CMS regression handoff

Continue from here next session. Code: this repo (`KskinCMS` / `kskincms_seleniumpython`).

## Environment
| Item | Value |
|------|--------|
| URL | `https://staging-cms.kskinfacial.com` |
| Creds | `cms_config.py` (from `cms_config.example.py`) |
| OTP | Staging digit via JS native setter |
| Viewport | **1920×1080** |
| Selenium / Playwright | Framework Python **3.8** |

## Hard rules
1. QA-item status toggles only (Gift Card singleton exception)
2. One browser, one login
3. One module at a time
4. Actions first → all doable testing (fields + validations; hard Failed)
5. View-only modules → listing/search/pagination asserts only (no invent edit)

## QA confidence workflow
Authored framework: [`qa-confidence/`](../qa-confidence/README.md)  
Skill: **`/QA_ConfidenceWorkflow`** (`~/.cursor/skills/QA_ConfidenceWorkflow/SKILL.md`)

Framework-only right now — `_example_*` templates only (not release guidance). Seed real modules after green suites.

```bash
python3 scripts/generate_qa_confidence_report.py
python3 scripts/generate_qa_confidence_report.py --include-examples
open qa-confidence/generated/qa_confidence_report.html
```

## Next
1. Finish **Fee Management** Playwright suite to green (existing fail was Edit default % click timeout).
2. Seed real `qa-confidence/scenarios/` for green modules (start Products / Beacons) — keep slightly pessimistic.
3. Continue remaining Playwright modules per actions-first rules.

## Note
Older “Tomorrow” scratch lists are retired — use this file + `qa-confidence/` for skip/manual triage.
