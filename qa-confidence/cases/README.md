# Manual cases → scenarios

Import or author one YAML per manual test case (or a small batch file). Link each case to a `scenario_id` in `../scenarios/`.

## Workflow

1. Copy `_example_case.yaml` → `MC-<module>-<n>.yaml` (no leading underscore for real cases).
2. Set `case_id`, `title`, `module`.
3. Set `scenario_id` when automation exists; leave empty for **unmapped**.
4. Regenerate: `python3 scripts/generate_qa_confidence_report.py`

## Later (out of scope for framework-only)

- Asana / Google Sheet import pipeline
- Bulk CSV → YAML

Keep case files small and reviewable in PRs.
