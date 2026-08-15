# sbom

Two bills of materials, because this system has two supply chains and only one of them
has version numbers.

| File | Answers | Verified by |
|---|---|---|
| [`sbom.json`](sbom.json) | Which library versions is this running on? | [`verify_sbom.py`](verify_sbom.py) — compares against `importlib.metadata` |
| [`ai_sbom.json`](ai_sbom.json) | Which models, prompts, guard rules and policy files determine how it behaves? | [`verify_ai_sbom.py`](verify_ai_sbom.py) — recomputes every content hash |

## Why the second one exists

Every component in `sbom.json` has a version an installer can check, which is exactly
what makes it trustworthy. The things that actually govern this system's behaviour have
no version number at all:

- **the model** — a hosted endpoint that can change under a stable alias
- **the system prompts** — string literals in `packages/config/llm_client.py`
- **the prohibition contract** — JSON in `security/policies/`
- **the PI/PG guard's pattern set** — regexes in `services/integration/prompt_guard.py`

Change any one of them and the governance properties this repository claims can change
while `pip freeze` stays byte-identical. `ai_sbom.json` closes that gap by recording a
SHA-256 of each, and `verify_ai_sbom.py` recomputes all of them and exits non-zero on
drift.

The practical effect: **an edit that weakens a governance instruction in a system prompt
fails CI.** `tests/security/test_ai_sbom_verification.py` proves this by actually making
such an edit and asserting the build goes red.

## Usage

```sh
# Dependency SBOM
python3 security/sbom/verify_sbom.py

# AI-BOM -- regenerate after an intended prompt / guard / policy change, then review the diff
python3 security/sbom/generate_ai_sbom.py
python3 security/sbom/verify_ai_sbom.py

# --strict also fails on a model-identifier change (for a release pipeline with pinned model config)
python3 security/sbom/verify_ai_sbom.py --strict
```

Both run in CI (`.github/workflows/ci.yml`, the `governance` job) and at API container
startup (`deploy/containers/Dockerfile.api`).

## What the AI-BOM deliberately does not claim

`ai_sbom.json` records model identifiers such as `claude-sonnet-4-5` and marks each with
`aegis:identifier_is_mutable_alias: "true"`. **A matching model id proves nothing about
the weights actually serving the request.** Verification reports an id change as a finding
rather than a failure, and says so in its output, because pretending an alias is a pin
would invite the reader to stop asking the question that matters.

ADR-009's revisit trigger — if the served model changes, Stage 14's eval baselines must be
re-run — applies here and cannot be detected by this file.

## Format

`ai_sbom.json` is CycloneDX 1.6, using the `machine-learning-model` component type and
`modelCard` from the ML-BOM extension, so it can be ingested by tooling a customer's
security team already runs. `sbom.json` predates that choice and keeps its own simpler
shape; it is hashed *into* the AI-BOM so the two cannot drift apart unnoticed.
