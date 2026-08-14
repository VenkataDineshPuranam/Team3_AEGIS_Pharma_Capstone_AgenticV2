"""Stage 21 gap-closure -- INJ-070: model/dependency supply-chain compromise.

Verifies security/sbom/verify_sbom.py actually catches a real mismatch, and that the
recorded SBOM matches the environment this test suite is running in right now.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "security" / "sbom"))

from verify_sbom import SBOMMismatch, load_sbom, verify_installed_versions  # noqa: E402


def test_recorded_sbom_matches_the_actual_installed_environment():
    results = verify_installed_versions()
    assert all(r["match"] for r in results)
    assert len(results) == len(load_sbom()["components"])


def test_a_real_version_drift_is_actually_caught(monkeypatch):
    """Structural check: this isn't a document nobody re-reads -- it fails loudly on a
    genuine mismatch, the same way a compromised/substituted package version would."""
    import importlib.metadata

    real_version = importlib.metadata.version

    def _lying_version(name):
        if name == "fastapi":
            return "0.0.0-compromised"
        return real_version(name)

    monkeypatch.setattr(importlib.metadata, "version", _lying_version)
    with pytest.raises(SBOMMismatch, match="fastapi"):
        verify_installed_versions()
