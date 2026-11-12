"""AI partner archetype registry, loaded from content/companions.json."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .. import CONTENT_DIR


@dataclass(frozen=True)
class Companion:
    id: str
    name: str
    title: str
    style: str
    mechanic: str
    greeting: str
    question_style: str
    weights: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id, "name": self.name, "title": self.title, "style": self.style,
            "mechanic": self.mechanic, "greeting": self.greeting, "weights": dict(self.weights),
        }


class CompanionRegistry:
    def __init__(self, companions: list[Companion], guide: dict):
        self._by_id = {c.id: c for c in companions}
        self.guide = guide

    @classmethod
    def load(cls, path: str | Path | None = None) -> "CompanionRegistry":
        path = Path(path) if path else CONTENT_DIR / "companions.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        comps = [
            Companion(
                id=c["id"], name=c["name"], title=c["title"], style=c["style"],
                mechanic=c["mechanic"], greeting=c["greeting"],
                question_style=c.get("question_style", ""), weights=c.get("weights", {}),
            )
            for c in data["companions"]
        ]
        return cls(comps, data.get("guide", {}))

    def get(self, companion_id: str) -> Companion:
        try:
            return self._by_id[companion_id]
        except KeyError:
            raise KeyError(
                f"Unknown companion '{companion_id}'. Choose one of: {', '.join(self._by_id)}"
            ) from None

    def ids(self) -> set[str]:
        return set(self._by_id)

    def all(self) -> list[Companion]:
        return list(self._by_id.values())


__all__ = ["Companion", "CompanionRegistry"]
