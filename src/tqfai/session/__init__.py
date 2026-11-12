"""Session state and the session-only reflection log.

Privacy by design (ROADMAP milestones 0 & 3): nothing here is written to disk or
sent anywhere. A session holds a random id, the chosen companion, world state and
the path taken. No names, ages, free text or device identifiers.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field


@dataclass
class ReflectionEntry:
    scene_id: str
    choice_id: str
    choice_text: str
    perspectives: list[str]
    companion_note: str
    uncertain: bool

    def to_dict(self) -> dict:
        return dict(self.__dict__)


@dataclass
class Session:
    scenario_id: str
    scenario_version: str
    companion_id: str
    current: str
    state: dict[str, int]
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    history: list[ReflectionEntry] = field(default_factory=list)
    finished: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "scenario_id": self.scenario_id,
            "scenario_version": self.scenario_version,
            "companion_id": self.companion_id,
            "current": self.current,
            "state": dict(self.state),
            "finished": self.finished,
            "history": [h.to_dict() for h in self.history],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Session":
        s = cls(
            scenario_id=d["scenario_id"],
            scenario_version=d["scenario_version"],
            companion_id=d["companion_id"],
            current=d["current"],
            state=dict(d["state"]),
            id=d["id"],
            finished=d.get("finished", False),
        )
        s.history = [ReflectionEntry(**h) for h in d.get("history", [])]
        return s

    def perspective_summary(self) -> dict[str, int]:
        """How often each perspective came up. For the end-of-game reflection screen only."""
        counts: dict[str, int] = {}
        for h in self.history:
            for p in h.perspectives:
                counts[p] = counts.get(p, 0) + 1
        return counts


__all__ = ["ReflectionEntry", "Session"]
