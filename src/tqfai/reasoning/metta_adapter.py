"""MeTTa / AtomSpace reasoner (proof of concept) - OWNED BY WORKSTREAM 4.

Status: scaffold. It loads the existing ``src/logic/*.metta`` files into a Hyperon
MeTTa runner when the optional ``hyperon`` package is installed, and otherwise
falls back to the rules baseline so the game always works.

TODO (Workstream 4):
  1. Encode scene/choice perspectives as atoms, e.g. ``(Perspective c_ask_pip curiosity)``.
  2. Write a MeTTa query that returns the companion's interpretation + uncertainty.
  3. Run ``python -m tqfai eval`` and compare against the baseline (decision gate).
"""

from __future__ import annotations

from pathlib import Path

from .. import LOGIC_DIR
from ..companions import Companion
from ..scenario import Choice, Scene
from .base import Interpretation
from .rules_baseline import RulesBaseline

try:  # optional dependency
    from hyperon import MeTTa  # type: ignore

    HYPERON_AVAILABLE = True
except Exception:  # pragma: no cover - depends on environment
    MeTTa = None
    HYPERON_AVAILABLE = False


class MettaReasoner:
    name = "metta"

    def __init__(self, logic_dir: str | Path | None = None):
        self.logic_dir = Path(logic_dir) if logic_dir else LOGIC_DIR
        self.fallback = RulesBaseline()
        self.metta = None
        if HYPERON_AVAILABLE:
            self.metta = MeTTa()
            for f in sorted(self.logic_dir.glob("*.metta")):
                self.metta.run(f.read_text(encoding="utf-8"))

    @property
    def active(self) -> bool:
        return self.metta is not None

    def interpret(
        self, scene: Scene, choice: Choice, state: dict[str, int], companion: Companion
    ) -> Interpretation:
        result = self.fallback.interpret(scene, choice, state, companion)
        # TODO(Workstream 4): replace with a real AtomSpace query, e.g.
        #   self.metta.run(f"!(interpret {choice.id} {companion.id})")
        result.source = "metta" if self.active else "metta(fallback:baseline)"
        return result
