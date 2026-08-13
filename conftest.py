"""Repo-root conftest -- makes `packages.*` / `services.*` importable from anywhere
under tests/, without requiring an installed package or per-test sys.path hacks."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def pytest_configure(config):
    config.addinivalue_line("markers", "stub: graph tests using StubLLM, no API key required")
    config.addinivalue_line("markers", "live: graph tests requiring a real LLM provider (ANTHROPIC_API_KEY or GROQ_API_KEY)")
