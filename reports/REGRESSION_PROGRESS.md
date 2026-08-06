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
- Fee Management seeded: **6 scenarios trusted** (`scenarios/fee_management.yaml`)

`~/.cursor/skills/` is outside git. On any machine:

```bash
bash qa-confidence/skill/install.sh
# optional if you still use the Mac notes reports folder:
bash qa-confidence/skill/sync-to-notes.sh
python3 scripts/generate_qa_confidence_report.py
```

Do **not** edit a notes-folder copy as the source of truth — edit here, then sync.

## Status
| Module | Suite | Result |
|--------|-------|--------|
| Products (Selenium) | KS-CMS-PRODUCT-001 | 11/11 green · trusted |
| Fee Management (Playwright) | KS-CMS-FEE-MGMT-001 | **6/6 green** · trusted |
| Beacons / Franchisee Reports | (prior Mac notes) | previously green |
| Queue | — | skipped (empty without therapist InQ) |

### Fee Management notes
- Login: React native value setters (`playwright_auth.py`) — plain `fill()` leaves Login disabled.
- Dialog Save: `_dialog_save` JS click fallback (role click flaky).
- Cloud runner: `FeeManagement_Module/run_fee_cloud.py` → `reports/KS-CMS-FEE-MGMT-001.html`
- Always restores default % and outlet override after temp edits.

## Next
1. Continue Playwright franchise/outlet order (next module after Fee Management).
2. Seed more modules into `qa-confidence/scenarios/` after each green suite (Beacons, Franchisee Reports, …).
3. Keep Products + Fee Management trusted only while their suites stay green.
