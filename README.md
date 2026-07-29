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
