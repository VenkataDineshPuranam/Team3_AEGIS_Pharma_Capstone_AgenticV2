"""Verifies security/sbom/ai_sbom.json against the live repository.

This is the half that makes the AI-BOM a control instead of a document. `verify_sbom.py`
proves installed package versions match what was recorded; this proves the things that
have no version number still hash to what was recorded:

  - every system prompt in packages/config/llm_client.py
  - the PI/PG guard's pattern set and its declared version
  - the policy contract, tool manifest and dependency SBOM files
  - the AI-relevant library versions this document quotes from sbom.json

WHAT FAILS THE BUILD, AND WHAT DELIBERATELY DOES NOT
-----------------------------------------------------
FAILS: any content hash drifting from what is recorded, a prompt appearing or
disappearing, or the guard's declared version not matching the module. Each of those is a
change to how the AI system behaves, made without the AI-BOM being regenerated and
reviewed. Regenerating is one command -- the friction is the point, because it forces the
diff to appear in a pull request where someone reads it.

DOES NOT FAIL: a model identifier differing from what was recorded. Model ids come from
the environment (ANTHROPIC_MODEL / GROQ_MODEL), so failing on them would break CI for
anyone running a different provider config, and -- more importantly -- it would be
security theatre: the alias matching proves nothing, because the weights behind a stable
alias can change without the string moving. Differences are REPORTED as findings so a
human sees them, and `--strict` promotes them to failures for a release pipeline that
pins its model config.

Run:  python3 security/sbom/verify_ai_sbom.py [--strict]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from security.sbom.generate_ai_sbom import (  # noqa: E402 -- sys.path must be set first
    AI_SBOM_PATH,
    collect_ai_libraries,
    collect_governance_artifacts,
    collect_guard_ruleset,
    collect_models,
    collect_prompts,
)


class AISBOMMismatch(Exception):
    """Recorded AI-BOM content does not match the live repository."""


def _recorded_components(sbom: dict, component_type: str) -> dict[str, dict]:
    return {c["bom-ref"]: c for c in sbom["components"] if c["type"] == component_type}


def _hash_of(component: dict) -> str | None:
    for entry in component.get("hashes", []):
        if entry["alg"] == "SHA-256":
            return entry["content"]
    return None


def _property(component: dict, name: str) -> str | None:
    for prop in component.get("properties", []):
        if prop["name"] == name:
            return prop["value"]
    return None


def verify(strict: bool = False) -> tuple[list[str], list[str]]:
    """Returns (failures, findings). Raises nothing -- callers decide what an empty
    failure list with non-empty findings means for them."""
    if not AI_SBOM_PATH.exists():
        raise AISBOMMismatch(
            f"{AI_SBOM_PATH.relative_to(REPO_ROOT)} does not exist. "
            "Run: python3 security/sbom/generate_ai_sbom.py"
        )
    sbom = json.loads(AI_SBOM_PATH.read_text())
    failures: list[str] = []
    findings: list[str] = []

    # --- prompts ------------------------------------------------------------
    recorded_data = _recorded_components(sbom, "data")
    live_prompts = {f"prompt/{p['constant'].strip('_').lower()}": p for p in collect_prompts()}
    recorded_prompts = {ref: c for ref, c in recorded_data.items() if ref.startswith("prompt/")}

    for ref, prompt in live_prompts.items():
        recorded = recorded_prompts.get(ref)
        if recorded is None:
            failures.append(
                f"prompt {prompt['constant']} exists in llm_client.py but is not recorded in the AI-BOM"
            )
        elif _hash_of(recorded) != prompt["sha256"]:
            failures.append(
                f"prompt {prompt['constant']} changed: recorded {_hash_of(recorded)[:12]}…, "
                f"live {prompt['sha256'][:12]}…"
            )
    for ref, recorded in recorded_prompts.items():
        if ref not in live_prompts:
            failures.append(f"prompt {recorded['name']} is recorded in the AI-BOM but no longer exists")

    # --- PI/PG guard ruleset ------------------------------------------------
    guard_recorded = recorded_data.get("guard/prompt-guard-ruleset")
    guard_live = collect_guard_ruleset()
    if guard_recorded is None:
        failures.append("the prompt_guard ruleset is not recorded in the AI-BOM")
    else:
        if guard_recorded.get("version") != guard_live["version"]:
            failures.append(
                f"prompt_guard version changed: recorded {guard_recorded.get('version')!r}, "
                f"live {guard_live['version']!r}"
            )
        for prop, key in (
            ("aegis:input_ruleset_sha256", "input_ruleset_sha256"),
            ("aegis:output_ruleset_sha256", "output_ruleset_sha256"),
            ("aegis:system_prompt_markers_sha256", "system_prompt_markers_sha256"),
        ):
            if _property(guard_recorded, prop) != guard_live[key]:
                failures.append(
                    f"prompt_guard {prop} changed: recorded {_property(guard_recorded, prop)}, "
                    f"live {guard_live[key]}. If this is an intended control change, regenerate "
                    "the AI-BOM and bump PROMPT_GUARD_VERSION."
                )

    # --- governance artifacts on disk ---------------------------------------
    for artifact in collect_governance_artifacts():
        recorded = recorded_data.get(f"governance/{artifact['name']}")
        if recorded is None:
            failures.append(f"governance artifact {artifact['name']} is not recorded in the AI-BOM")
        elif _hash_of(recorded) != artifact["sha256"]:
            failures.append(
                f"{artifact['path']} changed: recorded {_hash_of(recorded)[:12]}…, "
                f"live {artifact['sha256'][:12]}…"
            )

    # --- quoted library versions --------------------------------------------
    recorded_libs = {c["name"]: c.get("version") for c in _recorded_components(sbom, "library").values()}
    for library in collect_ai_libraries():
        if recorded_libs.get(library["name"]) != library["version"]:
            failures.append(
                f"library {library['name']}: AI-BOM quotes {recorded_libs.get(library['name'])!r}, "
                f"sbom.json records {library['version']!r}"
            )

    # --- models: reported, not enforced (see module docstring) ---------------
    recorded_models = {c["bom-ref"]: c for c in _recorded_components(sbom, "machine-learning-model").values()}
    for model in collect_models():
        recorded = recorded_models.get(model["bom-ref"])
        if recorded is None:
            findings.append(f"model {model['bom-ref']} is not recorded in the AI-BOM")
        elif recorded["name"] != model["name"]:
            findings.append(
                f"model {model['bom-ref']}: AI-BOM records {recorded['name']!r}, environment "
                f"selects {model['name']!r}"
            )
    findings.append(
        "Model identifiers are mutable aliases -- a matching id does NOT prove the weights "
        "behind it are unchanged. ADR-009's revisit trigger (re-run Stage 14 eval baselines) "
        "applies whenever the served model changes, and this file cannot detect that."
    )

    if strict:
        failures.extend(f"[strict] {f}" for f in findings[:-1])

    return failures, findings


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict", action="store_true",
        help="Promote model-identifier findings to failures (for a release pipeline with pinned model config).",
    )
    args = parser.parse_args()

    try:
        failures, findings = verify(strict=args.strict)
    except AISBOMMismatch as exc:
        print(f"AI-SBOM ERROR: {exc}")
        raise SystemExit(1) from exc

    for finding in findings:
        print(f"  note: {finding}")

    if failures:
        print(f"\nAI-SBOM MISMATCH ({len(failures)}):")
        for failure in failures:
            print(f"  - {failure}")
        print("\nIf these changes are intended, review them and run: python3 security/sbom/generate_ai_sbom.py")
        raise SystemExit(1)

    print("\nAI-SBOM verified: prompts, PI/PG ruleset, governance artifacts and library versions all match.")


if __name__ == "__main__":
    main()
