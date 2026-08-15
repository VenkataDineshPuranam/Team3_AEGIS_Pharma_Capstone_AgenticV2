"""Stage 23 -- the AI-BOM (security/sbom/ai_sbom.json) as a control, not a document.

The dependency SBOM's own test file already makes this argument for package versions.
The AI-BOM's claim is harder and worth testing harder: it says a change to a system
prompt, a prohibition contract or the PI/PG pattern set cannot reach a deployment without
appearing as a reviewable hash diff. That claim is only true if the verifier actually
fails on drift, so the tests below induce each kind of drift and assert it is caught.

The most important one is `test_weakening_a_governance_prompt_fails_verification`: it
edits a real system prompt to remove its prohibition instruction and asserts CI would go
red. Everything else in this repository's AI-governance story assumes those prompt strings
are what the review said they were.
"""
import json

import pytest

from security.sbom import generate_ai_sbom, verify_ai_sbom


def test_the_committed_ai_sbom_matches_the_live_repository():
    failures, _findings = verify_ai_sbom.verify()
    assert failures == [], f"AI-BOM is stale -- regenerate it. Drift: {failures}"


def test_every_system_prompt_the_system_can_send_is_recorded():
    """A prompt that exists but is unrecorded is the gap this artifact exists to close,
    so absence is a failure rather than something the generator quietly skips."""
    sbom = json.loads(generate_ai_sbom.AI_SBOM_PATH.read_text())
    recorded = {c["name"] for c in sbom["components"] if c["bom-ref"].startswith("prompt/")}
    live = {p["constant"] for p in generate_ai_sbom.collect_prompts()}

    assert live, "no system prompts were collected -- the collector is broken, not the repo"
    assert live == recorded


def test_the_record_assistant_prompt_is_covered():
    """The Record Assistant's prompt reaches a human without a graph or critic in between,
    which makes it the prompt whose unreviewed edit matters most."""
    roles = {p["role"] for p in generate_ai_sbom.collect_prompts()}
    assert {"synthesize", "critic", "record_assistant"} <= roles


def test_the_pi_pg_ruleset_is_recorded_with_its_version():
    sbom = json.loads(generate_ai_sbom.AI_SBOM_PATH.read_text())
    guard = next(c for c in sbom["components"] if c["bom-ref"] == "guard/prompt-guard-ruleset")
    live = generate_ai_sbom.collect_guard_ruleset()

    assert guard["version"] == live["version"]
    assert live["input_pattern_count"] > 0
    assert live["output_pattern_count"] > 0


def test_the_ai_sbom_is_valid_cyclonedx_with_a_dependency_graph():
    """Format matters here for a practical reason: a security team ingests CycloneDX with
    tooling they already have. An in-house JSON shape would be a document nobody scans."""
    sbom = json.loads(generate_ai_sbom.AI_SBOM_PATH.read_text())

    assert sbom["bomFormat"] == "CycloneDX"
    assert sbom["specVersion"] == "1.6"
    assert {c["type"] for c in sbom["components"]} >= {"machine-learning-model", "data", "library"}

    refs = {c["bom-ref"] for c in sbom["components"]}
    depends_on = set(sbom["dependencies"][0]["dependsOn"])
    assert depends_on == refs, "the dependency graph and the component list disagree"


def test_models_are_recorded_as_mutable_aliases():
    """The honest half of the artifact. Recording `claude-sonnet-4-5` and implying it
    pins anything would be worse than not recording it, because it invites the reader to
    stop asking which weights are actually serving."""
    sbom = json.loads(generate_ai_sbom.AI_SBOM_PATH.read_text())
    models = [c for c in sbom["components"] if c["type"] == "machine-learning-model"]

    assert models
    for model in models:
        flag = next(
            p["value"] for p in model["properties"]
            if p["name"] == "aegis:identifier_is_mutable_alias"
        )
        assert flag == "true"


# --- drift detection ---------------------------------------------------------


def test_weakening_a_governance_prompt_fails_verification(monkeypatch):
    """The control this whole artifact exists for: an edit that removes a prohibition
    instruction from a system prompt turns CI red."""
    from packages.config import llm_client

    weakened = llm_client._BATCH_SYNTHESIZE_SYSTEM.replace(
        "You must NEVER recommend, suggest, or imply a release",
        "You may recommend a release",
    )
    assert weakened != llm_client._BATCH_SYNTHESIZE_SYSTEM, "the prompt text moved; update this test"
    monkeypatch.setattr(llm_client, "_BATCH_SYNTHESIZE_SYSTEM", weakened)

    failures, _ = verify_ai_sbom.verify()
    assert any("_BATCH_SYNTHESIZE_SYSTEM" in f for f in failures)


def test_removing_a_guard_pattern_fails_verification(monkeypatch):
    """Deleting a detection pattern is a control change. Without this it would be an
    invisible one -- no test breaks when a regex that never matched in CI disappears."""
    from services.integration import prompt_guard

    monkeypatch.setattr(prompt_guard, "_INPUT_PATTERNS", prompt_guard._INPUT_PATTERNS[:-1])

    failures, _ = verify_ai_sbom.verify()
    assert any("input_ruleset_sha256" in f for f in failures)


def test_changing_a_pattern_severity_fails_verification(monkeypatch):
    """A severity downgrade from `high` to `medium` turns a refusal into a pass-through
    without touching a single regex. It is a control change and is hashed as one."""
    from services.integration import prompt_guard

    pid, category, _severity, pattern = prompt_guard._INPUT_PATTERNS[0]
    downgraded = ((pid, category, "low", pattern),) + prompt_guard._INPUT_PATTERNS[1:]
    monkeypatch.setattr(prompt_guard, "_INPUT_PATTERNS", downgraded)

    failures, _ = verify_ai_sbom.verify()
    assert any("input_ruleset_sha256" in f for f in failures)


def test_tampering_with_the_prohibition_contract_fails_verification(monkeypatch, tmp_path):
    """The policy contract is hashed from disk, so editing which phrases are banned --
    the file ADR-004 layer 3 reads at runtime -- cannot pass unnoticed."""
    tampered = tmp_path / "policy_contract.v1.json"
    tampered.write_text('{"version": "v1", "prohibition_contracts": {}}')

    real_collect = generate_ai_sbom.collect_governance_artifacts

    def _with_tampered_contract():
        artifacts = real_collect()
        for artifact in artifacts:
            if artifact["name"] == "policy_contract":
                artifact["sha256"] = generate_ai_sbom.sha256_file(tampered)
        return artifacts

    monkeypatch.setattr(verify_ai_sbom, "collect_governance_artifacts", _with_tampered_contract)

    failures, _ = verify_ai_sbom.verify()
    assert any("policy_contract" in f for f in failures)


def test_a_model_alias_change_is_reported_but_does_not_fail_the_build(monkeypatch):
    """Model ids come from the environment, so failing on them would break CI for anyone
    running a different provider config -- and matching them proves nothing anyway."""
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-something-else")

    failures, findings = verify_ai_sbom.verify()
    assert failures == []
    assert any("claude-something-else" in f for f in findings)


def test_strict_mode_promotes_a_model_alias_change_to_a_failure(monkeypatch):
    """A release pipeline that pins its model config can opt into the stricter reading."""
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-something-else")

    failures, _ = verify_ai_sbom.verify(strict=True)
    assert any("claude-something-else" in f for f in failures)


def test_generation_is_deterministic_apart_from_its_timestamp():
    """Two runs must differ only in `metadata.timestamp`, or every regeneration produces
    review noise and reviewers stop reading the diff -- which is the only mechanism that
    makes this artifact work."""
    first = generate_ai_sbom.build_ai_sbom()
    second = generate_ai_sbom.build_ai_sbom()
    first["metadata"]["timestamp"] = second["metadata"]["timestamp"] = "fixed"

    assert first == second


@pytest.mark.parametrize("name", ["anthropic", "openai", "langgraph"])
def test_ai_library_versions_are_quoted_from_the_dependency_sbom(name):
    """One source of truth for versions. `verify_sbom.py` proves those against the
    installed environment; this proves the AI-BOM quotes them faithfully rather than
    carrying a second, independently-drifting copy."""
    dep_sbom = json.loads(generate_ai_sbom.DEP_SBOM_PATH.read_text())
    recorded = {c["name"]: c["version"] for c in dep_sbom["components"]}
    quoted = {lib["name"]: lib["version"] for lib in generate_ai_sbom.collect_ai_libraries()}

    assert quoted[name] == recorded[name]
