"""Scenario data model.

A scenario is a small directed graph of scenes. Each choice points at another
scene or at an ending. World state (``entropy``, ``connection`` ...) describes the
*game world*, never the player: TQFAI does not score a child's character.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# World-state keys a scenario may change. Add new keys here (and in docs/SCENARIO_FORMAT.md).
WORLD_STATE_KEYS = ("entropy", "connection", "shade")

# Perspective tags a choice can carry. They prompt reflection; they are not grades.
PERSPECTIVES = (
    "empathy",        # considering how someone else feels
    "boundaries",     # protecting your own / others' limits
    "fairness",       # sharing, taking turns, rules applied equally
    "curiosity",      # asking before assuming
    "repair",         # fixing harm, apologising, reconnecting
    "self_care",      # stepping back, cooling down (The Shade)
    "escalation",     # a choice that raises conflict; allowed, never punished
)


@dataclass(frozen=True)
class Condition:
    """Optional gate on a choice: all listed bounds must hold for the choice to show."""

    min: dict[str, int] = field(default_factory=dict)
    max: dict[str, int] = field(default_factory=dict)

    def holds(self, state: dict[str, int]) -> bool:
        return all(state.get(k, 0) >= v for k, v in self.min.items()) and all(
            state.get(k, 0) <= v for k, v in self.max.items()
        )


@dataclass(frozen=True)
class Choice:
    id: str
    text: str
    next: str
    perspectives: tuple[str, ...] = ()
    effects: dict[str, int] = field(default_factory=dict)
    condition: Condition | None = None
    reaction: str = ""  # what the other characters say/do right after this choice


@dataclass(frozen=True)
class Scene:
    id: str
    text: str
    speaker: str = "narrator"
    choices: tuple[Choice, ...] = ()
    # Companion lines keyed by companion id, with "default" as fallback.
    companion_lines: dict[str, str] = field(default_factory=dict)
    background: str = ""  # art / VR environment hint for clients


@dataclass(frozen=True)
class Ending:
    id: str
    title: str
    text: str
    reflection_questions: tuple[str, ...] = ()
    tone: str = "neutral"  # "warm" | "neutral" | "bittersweet" ; endings are never "bad"


@dataclass(frozen=True)
class Scenario:
    id: str
    version: str
    title: str
    summary: str
    start: str
    scenes: dict[str, Scene]
    endings: dict[str, Ending]
    initial_state: dict[str, int] = field(default_factory=dict)
    audience: dict[str, Any] = field(default_factory=dict)
    learning_goals: tuple[str, ...] = ()

    def node(self, node_id: str) -> Scene | Ending | None:
        return self.scenes.get(node_id) or self.endings.get(node_id)

    def is_ending(self, node_id: str) -> bool:
        return node_id in self.endings
