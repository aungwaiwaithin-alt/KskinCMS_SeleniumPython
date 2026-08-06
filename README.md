# Kskin CMS Selenium (Python)

Selenium regression for staging CMS (`staging-cms.kskinfacial.com`).

## Setup
1. Copy `cms_config.example.py` → `cms_config.py` and fill email / password / OTP.
2. `pip install selenium python-dotenv` (or project venv).
3. From parent of this package:
   ```bash
   PYTHONPATH=/path/to/AquaProjects python3 KskinCMS/run_regression_sequential.py
   ```

## Rules
- One Chrome / one login (`cms_auth.get_driver`).
- ACTIVE↔INACTIVE only on QA-created items (`toggle_row_status`).

## QA confidence (skip vs manual)
**Canonical** framework: [`qa-confidence/`](qa-confidence/README.md) in this repo.  
Invoke **`/QA_ConfidenceWorkflow`**. Restore the Cursor skill anytime:

```bash
bash qa-confidence/skill/install.sh
python3 scripts/generate_qa_confidence_report.py
```

Optional Mac notes HTML mirror: `bash qa-confidence/skill/sync-to-notes.sh`.  
Handoff: `reports/REGRESSION_PROGRESS.md`.
