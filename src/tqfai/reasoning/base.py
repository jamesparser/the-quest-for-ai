"""Reasoner interface.

The engine asks a Reasoner to *interpret* a choice so the companion can reflect it
back to the player. Implementations:

* ``RulesBaseline``  - simple, transparent, always available (default)
* ``MettaReasoner``  - MeTTa / AtomSpace proof of concept (Workstream 4)

ROADMAP decision gate: MeTTa is adopted only if it beats the baseline on the
fixed evaluation set (tests/eval_cases.json). Both must satisfy this interface.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from ..companions import Companion
from ..scenario import Choice, Scene


@dataclass
class Interpretation:
    companion_note: str                       # what the companion says back
    perspectives: list[str] = field(default_factory=list)
    uncertain: bool = False                   # show "I might be wrong" in the UI
    source: str = "baseline"                  # which reasoner produced it

    def to_dict(self) -> dict:
        return {
            "companion_note": self.companion_note,
            "perspectives": list(self.perspectives),
            "uncertain": self.uncertain,
            "source": self.source,
        }


class Reasoner(Protocol):
    name: str

    def interpret(
        self, scene: Scene, choice: Choice, state: dict[str, int], companion: Companion
    ) -> Interpretation: ...
