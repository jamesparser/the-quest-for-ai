"""The Quest for AI (TQFAI) / The Agency of Mushrooms core package.

Layers (kept separate on purpose, see docs/ARCHITECTURE.md):

    scenario/    data model, JSON loader, validator      (content contract)
    companions/  AI partner archetype registry            (character contract)
    reasoning/   pluggable interpreters: rules baseline, MeTTa adapter
    engine/      deterministic narrative engine
    session/     session-only reflection log (no persistence)
    api/         stdlib JSON HTTP server for web / VR clients
"""

from pathlib import Path

__version__ = "0.1.0"

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTENT_DIR = REPO_ROOT / "content"
SCENARIO_DIR = CONTENT_DIR / "scenarios"
LOGIC_DIR = REPO_ROOT / "src" / "logic"
