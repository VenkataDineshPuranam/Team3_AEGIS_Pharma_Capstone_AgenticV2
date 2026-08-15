"""Generates security/sbom/ai_sbom.json -- the AI Bill of Materials (AI-BOM/ML-BOM).

WHY A SECOND SBOM RATHER THAN MORE ROWS IN THE FIRST ONE
--------------------------------------------------------
`sbom.json` answers "which library versions is this running on?". Every one of its
components has a version number an installer can check. That is the whole reason
`verify_sbom.py` can be trusted: `importlib.metadata.version()` is ground truth.

The things that actually determine how this AI system behaves have no version number:

  - the model, which is a remotely hosted endpoint that can change under a stable alias
  - the system prompts, which are string literals in a Python file
  - the prohibition contract, which is JSON on disk
  - the prompt-injection guard's pattern set, which is regexes in a module

Change any one of those and every governance property this repo claims can change, while
`pip freeze` stays byte-identical. That is the supply-chain gap an AI-BOM exists to close,
and it is not a subset of the dependency SBOM's job -- it is a different question with a
different verification method (content hashes, not installed versions).

WHAT MAKES THIS ARTIFACT REAL RATHER THAN DECORATIVE
-----------------------------------------------------
Everything recorded here is COMPUTED from the live repository by this script -- prompts
are hashed from the actual module attributes, not transcribed by hand; the guard's pattern
set is hashed from the compiled patterns; the policy contract and tool manifest are hashed
from disk. `verify_ai_sbom.py` recomputes all of it and fails loudly on any drift, which
is what makes an unreviewed prompt edit a CI failure instead of an invisible one.

The same honesty the dependency SBOM's note claims applies here: this file is a promise
that can be checked, and the check is the point.

Format: CycloneDX 1.6, using the `machine-learning-model` component type and `modelCard`
from the ML-BOM extension. Chosen because it is the format a customer's security team
will already have a scanner for -- an in-house JSON shape nobody can ingest is a document,
not a bill of materials.

Regenerate:  python3 security/sbom/generate_ai_sbom.py
Verify:      python3 security/sbom/verify_ai_sbom.py
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

AI_SBOM_PATH = Path(__file__).resolve().parent / "ai_sbom.json"
DEP_SBOM_PATH = Path(__file__).resolve().parent / "sbom.json"

#: Recorded as the AI-BOM's own version. Bump when the SHAPE of this document changes,
#: not when a hash inside it does -- a hash change is drift, and drift is the verifier's
#: business, not a new revision of the format.
AI_SBOM_SCHEMA_REVISION = "1.0.0"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Collectors -- each reads live state, none accepts hand-written input
# ---------------------------------------------------------------------------


def collect_prompts() -> list[dict]:
    """Hash every system prompt the running system can send.

    Imported rather than regex-scraped from the source file: a scrape would silently miss
    a prompt built by concatenation or moved to another module, and "the SBOM didn't
    notice" is the exact failure this artifact exists to prevent. Importing
    `packages.config.llm_client` is safe with no API key -- both provider SDKs are
    imported lazily inside their constructors.
    """
    from packages.config import llm_client

    prompts = []
    for name in sorted(dir(llm_client)):
        if not (name.startswith("_") and ("SYSTEM" in name)):
            continue
        value = getattr(llm_client, name)
        if not isinstance(value, str):
            continue
        role = (
            "critic" if "CRITIC" in name
            else "record_assistant" if "RECORD_CHAT" in name
            else "synthesize"
        )
        prompts.append({
            "constant": name,
            "role": role,
            "sha256": sha256_text(value),
            "chars": len(value),
        })
    return prompts


def collect_guard_ruleset() -> dict:
    """Hash the PI/PG pattern set.

    Hashes the pattern SOURCES (`.pattern`), not the module file, so a comment or
    docstring edit does not register as a control change while an actual regex edit
    always does. Categories and severities are included in the hashed payload because
    changing a pattern's severity from `high` to `medium` changes what gets refused --
    that is a control change even though the regex is untouched.
    """
    from services.integration import prompt_guard

    def digest(patterns) -> tuple[str, list[dict]]:
        entries = [
            {"pattern_id": pid, "category": cat, "severity": sev, "regex_sha256": sha256_text(pat.pattern)}
            for pid, cat, sev, pat in patterns
        ]
        return sha256_text(json.dumps(entries, sort_keys=True)), entries

    input_hash, input_entries = digest(prompt_guard._INPUT_PATTERNS)
    output_hash, output_entries = digest(prompt_guard._OUTPUT_PATTERNS)
    markers_hash = sha256_text(json.dumps(sorted(prompt_guard._SYSTEM_PROMPT_MARKERS)))

    return {
        "version": prompt_guard.PROMPT_GUARD_VERSION,
        "input_pattern_count": len(input_entries),
        "output_pattern_count": len(output_entries),
        "input_ruleset_sha256": input_hash,
        "output_ruleset_sha256": output_hash,
        "system_prompt_markers_sha256": markers_hash,
        "patterns": input_entries + output_entries,
    }


def collect_governance_artifacts() -> list[dict]:
    """Hash the on-disk files that constrain model behaviour at runtime."""
    targets = [
        ("policy_contract", REPO_ROOT / "security" / "policies" / "policy_contract.v1.json",
         "Per-workflow prohibition contracts (ADR-004 layer 3). Determines which generated "
         "phrases block a run, and which the Record Assistant's output guard refuses."),
        ("tool_manifest", REPO_ROOT / "services" / "integration" / "tool_manifest.json",
         "Recorded hashes and read-only status of every tool contract (INJ-066)."),
        ("dependency_sbom", DEP_SBOM_PATH,
         "The runtime-dependency SBOM this AI-BOM complements. Hashed so the two cannot "
         "drift apart unnoticed."),
    ]
    return [
        {"name": name, "path": str(path.relative_to(REPO_ROOT)), "sha256": sha256_file(path), "purpose": purpose}
        for name, path, purpose in targets
        if path.exists()
    ]


def collect_models() -> list[dict]:
    """The inference endpoints this system can call.

    Versions here are ALIASES, not immutable identifiers, and the record says so. A model
    alias resolving to new weights is the single most under-recorded change in an AI
    supply chain: nothing in the repository changes, no test necessarily fails, and every
    eval baseline measured against the old weights silently stops being a measurement of
    what is running. ADR-009's revisit trigger ("if the model-hosting route changes,
    Stage 14's eval baselines must be re-run") applies to this just as much as to a
    Route A/B switch, which is why it is recorded rather than assumed stable.
    """
    return [
        {
            "bom-ref": "model/anthropic-claude",
            "name": os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5"),
            "provider": "Anthropic",
            "route": "ADR-009 Route A",
            "hosting": "Anthropic API directly in development; Azure AI Foundry is the "
                       "deployment binding behind the same packages/config/llm_client.py interface.",
            "status": "authoritative",
            "used_for": ["synthesize", "critic_verify", "record_assistant"],
            "identifier_is_mutable_alias": True,
        },
        {
            "bom-ref": "model/groq-llama",
            "name": os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant"),
            "provider": "Groq (Meta Llama weights)",
            "route": "dev-only substitute, ADR-009",
            "hosting": "Groq OpenAI-compatible endpoint.",
            "status": "provisional -- output from this provider does not count toward any "
                      "interim-assumption exit criterion (.env.example, LLM_PROVIDER)",
            "used_for": ["synthesize", "critic_verify", "record_assistant"],
            "identifier_is_mutable_alias": True,
        },
    ]


def collect_ai_libraries() -> list[dict]:
    """The subset of the dependency SBOM that is AI/agentic infrastructure.

    Deliberately references the dependency SBOM's recorded versions rather than
    re-reading the installed environment: two files claiming independently-sourced
    versions is how they end up disagreeing. `verify_sbom.py` already proves those
    versions against the installed environment; this one proves it is quoting them
    faithfully.
    """
    if not DEP_SBOM_PATH.exists():
        return []
    dep_sbom = json.loads(DEP_SBOM_PATH.read_text())
    ai_relevant = {"anthropic", "groq", "openai", "langgraph", "langgraph-checkpoint", "neo4j"}
    return [
        {"name": c["name"], "version": c["version"], "purpose": c["purpose"]}
        for c in dep_sbom["components"]
        if c["name"] in ai_relevant
    ]


# ---------------------------------------------------------------------------
# CycloneDX assembly
# ---------------------------------------------------------------------------


def build_ai_sbom() -> dict:
    models = collect_models()
    prompts = collect_prompts()
    guard = collect_guard_ruleset()
    governance = collect_governance_artifacts()
    libraries = collect_ai_libraries()

    components: list[dict] = []

    for model in models:
        components.append({
            "type": "machine-learning-model",
            "bom-ref": model["bom-ref"],
            "name": model["name"],
            "version": model["name"],
            "publisher": model["provider"],
            "description": model["hosting"],
            "modelCard": {
                "modelParameters": {"task": "text-generation"},
                "considerations": {
                    "useCases": model["used_for"],
                    "ethicalConsiderations": [{
                        "name": "no-terminal-decision",
                        "mitigationStrategy": (
                            "This model never makes a terminal safety, release, allocation or "
                            "reportability decision. Prohibited outputs are structurally "
                            "unrepresentable (ADR-004 layers 1-2), pattern-blocked at runtime "
                            "(layer 3), and every generated answer is re-scanned by "
                            "services/integration/prompt_guard.py before a human sees it."
                        ),
                    }],
                },
            },
            "properties": [
                {"name": "aegis:route", "value": model["route"]},
                {"name": "aegis:status", "value": model["status"]},
                {"name": "aegis:identifier_is_mutable_alias", "value": str(model["identifier_is_mutable_alias"]).lower()},
            ],
        })

    for prompt in prompts:
        components.append({
            "type": "data",
            "bom-ref": f"prompt/{prompt['constant'].strip('_').lower()}",
            "name": prompt["constant"],
            "description": f"System prompt ({prompt['role']}), packages/config/llm_client.py",
            "hashes": [{"alg": "SHA-256", "content": prompt["sha256"]}],
            "properties": [
                {"name": "aegis:prompt_role", "value": prompt["role"]},
                {"name": "aegis:chars", "value": str(prompt["chars"])},
            ],
        })

    components.append({
        "type": "data",
        "bom-ref": "guard/prompt-guard-ruleset",
        "name": "prompt_guard ruleset (PI/PG)",
        "version": guard["version"],
        "description": (
            "Prompt-injection detection and prompt-guarding pattern set, "
            "services/integration/prompt_guard.py. Layer 0 (input) and layer 4 (output) "
            "around ADR-004's three structural layers -- attack visibility, never the sole control."
        ),
        "hashes": [
            {"alg": "SHA-256", "content": guard["input_ruleset_sha256"]},
        ],
        "properties": [
            {"name": "aegis:input_pattern_count", "value": str(guard["input_pattern_count"])},
            {"name": "aegis:output_pattern_count", "value": str(guard["output_pattern_count"])},
            {"name": "aegis:input_ruleset_sha256", "value": guard["input_ruleset_sha256"]},
            {"name": "aegis:output_ruleset_sha256", "value": guard["output_ruleset_sha256"]},
            {"name": "aegis:system_prompt_markers_sha256", "value": guard["system_prompt_markers_sha256"]},
        ],
    })

    for artifact in governance:
        components.append({
            "type": "data",
            "bom-ref": f"governance/{artifact['name']}",
            "name": artifact["name"],
            "description": artifact["purpose"],
            "hashes": [{"alg": "SHA-256", "content": artifact["sha256"]}],
            "properties": [{"name": "aegis:path", "value": artifact["path"]}],
        })

    for library in libraries:
        components.append({
            "type": "library",
            "bom-ref": f"library/{library['name']}",
            "name": library["name"],
            "version": library["version"],
            "description": library["purpose"],
            "properties": [{"name": "aegis:version_source", "value": "security/sbom/sbom.json"}],
        })

    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "version": 1,
        "metadata": {
            "timestamp": datetime.now(UTC).isoformat(),
            "component": {
                "type": "application",
                "bom-ref": "aegis-pharma-v3",
                "name": "AEGIS Control Center",
                "description": (
                    "Governed multi-agent decision-support system for six pharmaceutical "
                    "workflows. Decision support only -- no agent makes a terminal safety, "
                    "release, allocation or reportability decision."
                ),
            },
            "properties": [
                {"name": "aegis:ai_sbom_schema_revision", "value": AI_SBOM_SCHEMA_REVISION},
                {"name": "aegis:generator", "value": "security/sbom/generate_ai_sbom.py"},
                {
                    "name": "aegis:verification",
                    "value": (
                        "Every hash in this document is recomputed from the live repository by "
                        "security/sbom/verify_ai_sbom.py, which exits non-zero on drift. Model "
                        "identifiers are mutable aliases and are NOT verifiable this way -- see "
                        "each model component's aegis:identifier_is_mutable_alias property."
                    ),
                },
                {
                    "name": "aegis:eu_ai_act_note",
                    "value": (
                        "Supports the transparency and record-keeping expectations recorded in "
                        "docs/governance/compliance/eu_ai_act_risk_classification.md. This is an "
                        "engineering artifact, not a legal conformity assessment."
                    ),
                },
            ],
        },
        "components": components,
        "dependencies": [
            {
                "ref": "aegis-pharma-v3",
                "dependsOn": [c["bom-ref"] for c in components],
            },
        ],
    }


def main() -> None:
    sbom = build_ai_sbom()
    AI_SBOM_PATH.write_text(json.dumps(sbom, indent=2) + "\n")
    counts: dict[str, int] = {}
    for component in sbom["components"]:
        counts[component["type"]] = counts.get(component["type"], 0) + 1
    summary = ", ".join(f"{n} {t}" for t, n in sorted(counts.items()))
    print(f"Wrote {AI_SBOM_PATH.relative_to(REPO_ROOT)}: {len(sbom['components'])} components ({summary}).")


if __name__ == "__main__":
    main()
