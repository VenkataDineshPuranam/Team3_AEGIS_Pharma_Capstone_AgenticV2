# unit

Unit tests.

[graders/](graders/) — Stage 14 pytest wrapper around `eval-ai-cache/graders/run_eval_dataset.py`.
`python3 -m pytest tests/unit/graders/ -q` → 60 passed, 4 skipped (each skip carries an honest
reason: `NOT_APPLICABLE`, `THRESHOLD_NOT_DEFINED`, or `BLOCKED_BY_ENVIRONMENT` — never silent).
