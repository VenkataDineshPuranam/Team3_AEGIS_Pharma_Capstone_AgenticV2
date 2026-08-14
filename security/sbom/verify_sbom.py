"""Verifies the installed environment matches security/sbom/sbom.json -- Stage 21
gap-closure (INJ-070: model/dependency supply-chain compromise).

This is the second half of the SBOM's own claim to be "real, checkable" rather than a
document nobody re-reads: it actually imports the installed package metadata and compares
it against what was recorded, exactly the same shape of check
`packages/domain/kg/ingest.py`'s content-hash verification already does for evidence
documents -- applied here to the dependency supply chain instead.
"""
from __future__ import annotations

import importlib.metadata
import json
from pathlib import Path

SBOM_PATH = Path(__file__).resolve().parent / "sbom.json"


class SBOMMismatch(Exception):
    """Raised when an installed package's version does not match the recorded SBOM."""


def load_sbom() -> dict:
    return json.loads(SBOM_PATH.read_text())


def verify_installed_versions() -> list[dict]:
    """Returns a list of {name, recorded_version, installed_version, match} for every
    component in the SBOM. Raises SBOMMismatch if any component is missing or mismatched
    -- callers that only want the report, not the exception, should catch it."""
    sbom = load_sbom()
    results = []
    mismatches = []

    for component in sbom["components"]:
        name = component["name"]
        recorded = component["version"]
        try:
            installed = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            installed = None

        match = installed == recorded
        results.append({
            "name": name, "recorded_version": recorded, "installed_version": installed, "match": match,
        })
        if not match:
            mismatches.append(f"{name}: recorded {recorded!r}, installed {installed!r}")

    if mismatches:
        raise SBOMMismatch("; ".join(mismatches))
    return results


if __name__ == "__main__":
    try:
        results = verify_installed_versions()
        print(f"SBOM verified: {len(results)}/{len(results)} components match.")
    except SBOMMismatch as exc:
        print(f"SBOM MISMATCH: {exc}")
        raise SystemExit(1)
