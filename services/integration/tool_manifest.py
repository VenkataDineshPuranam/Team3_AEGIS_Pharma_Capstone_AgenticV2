"""Tool-manifest integrity check -- Stage 21 gap-closure (INJ-066: a newly registered
tool requesting write access and silently changing a disposition).

`tool_inventory.md` already argues every tool in this system is read-only by design
(scope fixed at server-binding time, no tool contract exposes a write-capable operation).
What that document did not have until this module: a way to *detect* if a tool contract
file were tampered with or a new one registered that violates the pattern -- the same gap
`packages/domain/kg/ingest.py`'s content-hash check closes for evidence documents, applied
here to the tool contracts themselves.

`verify_manifest()` is deliberately NOT wired into every request (that would mean hashing
every schema file on every graph invocation, pure overhead with no benefit -- the schema
files do not change at runtime). It is meant to run at process startup and in CI, the same
cadence `verify_sbom.py` runs at.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_DIR = REPO_ROOT / "packages" / "contracts" / "tool_contracts"
MANIFEST_PATH = Path(__file__).resolve().parent / "tool_manifest.json"


class ToolManifestViolation(Exception):
    """Raised when a tool contract is missing from the manifest, its hash has changed
    without a corresponding manifest update, or -- the specific INJ-066 case -- it
    declares a write capability the manifest does not expect."""


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text())


def verify_manifest() -> list[dict]:
    """Checks every *.schema.json file in packages/contracts/tool_contracts/ against the
    recorded manifest: present, hash matches, and `read_only` is still true. A tool
    matching none of those three is exactly a manifest-poisoning attempt -- registered
    without going through this file, or tampered with after registration, or silently
    flipped to request write access."""
    manifest = load_manifest()
    recorded = {c["name"]: c for c in manifest["tools"]}
    on_disk = {p.name: p for p in CONTRACTS_DIR.glob("*.schema.json")}

    violations = []
    results = []

    for name, path in sorted(on_disk.items()):
        contract = json.loads(path.read_text())
        actual_hash = _hash_file(path)
        actual_read_only = contract.get("read_only")

        entry = recorded.get(name)
        if entry is None:
            violations.append(f"{name}: not present in the recorded manifest -- unregistered tool")
            results.append({"name": name, "status": "unregistered"})
            continue

        if entry["sha256"] != actual_hash:
            violations.append(f"{name}: hash mismatch (recorded {entry['sha256'][:12]}..., actual {actual_hash[:12]}...)")
            results.append({"name": name, "status": "hash_mismatch"})
            continue

        if actual_read_only is not True:
            violations.append(f"{name}: read_only is {actual_read_only!r}, not True -- write-capability escalation")
            results.append({"name": name, "status": "write_capability_escalation"})
            continue

        results.append({"name": name, "status": "ok"})

    missing = set(recorded) - set(on_disk)
    for name in missing:
        violations.append(f"{name}: recorded in manifest but no longer present on disk")

    if violations:
        raise ToolManifestViolation("; ".join(violations))
    return results


def regenerate_manifest() -> dict:
    """Recomputes the manifest from the current on-disk contracts. Run by hand
    (`python -m services.integration.tool_manifest`) after a genuine, reviewed tool
    contract change -- never automatically, since that would defeat the point of a
    tamper-evident manifest."""
    tools = []
    for path in sorted(CONTRACTS_DIR.glob("*.schema.json")):
        contract = json.loads(path.read_text())
        tools.append({
            "name": path.name,
            "sha256": _hash_file(path),
            "read_only": contract.get("read_only"),
            "owning_context": contract.get("owning_context"),
        })
    return {"tools": tools}


if __name__ == "__main__":
    MANIFEST_PATH.write_text(json.dumps(regenerate_manifest(), indent=2) + "\n")
    print(f"Regenerated {MANIFEST_PATH} from {CONTRACTS_DIR}.")
