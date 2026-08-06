# Kskin CMS regression handoff

Continue from here next session. Code + **canonical QA confidence**: this repo.

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

## QA confidence workflow (canonical = this repo)
- Authored: [`qa-confidence/`](../qa-confidence/README.md)
- Skill: **`/QA_ConfidenceWorkflow`** — `qa-confidence/skill/SKILL.md`
- Products seeded: **11 scenarios trusted** (`scenarios/product.yaml`)

`~/.cursor/skills/` is outside git. On any machine:

```bash
bash qa-confidence/skill/install.sh
# optional if you still use the Mac notes reports folder:
bash qa-confidence/skill/sync-to-notes.sh
python3 scripts/generate_qa_confidence_report.py
```

Do **not** edit a notes-folder copy as the source of truth — edit here, then sync.

## Next
1. Finish **Fee Management** Playwright suite to green (prior fail: Edit default % click timeout).
2. Seed more modules into `qa-confidence/scenarios/` after each green suite (Beacons, Franchisee Reports, …).
3. Keep Products trusted only while `KS-CMS-PRODUCT-001` stays green.
