"""Load scenarios from JSON files into the immutable data model."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .model import Choice, Condition, Ending, Scenario, Scene


class ScenarioFormatError(ValueError):
    """Raised when a scenario file is missing required fields."""


def _req(obj: dict[str, Any], key: str, where: str) -> Any:
    if key not in obj:
        raise ScenarioFormatError(f"{where}: missing required field '{key}'")
    return obj[key]


def scenario_from_dict(data: dict[str, Any]) -> Scenario:
    sid = _req(data, "id", "scenario")
    scenes: dict[str, Scene] = {}
    for scene_id, s in _req(data, "scenes", sid).items():
        where = f"{sid}.scenes.{scene_id}"
        choices = []
        for i, c in enumerate(s.get("choices", [])):
            cw = f"{where}.choices[{i}]"
            cond = c.get("condition")
            choices.append(
                Choice(
                    id=_req(c, "id", cw),
                    text=_req(c, "text", cw),
                    next=_req(c, "next", cw),
                    perspectives=tuple(c.get("perspectives", [])),
                    effects=dict(c.get("effects", {})),
                    condition=Condition(cond.get("min", {}), cond.get("max", {})) if cond else None,
                    reaction=c.get("reaction", ""),
                )
            )
        scenes[scene_id] = Scene(
            id=scene_id,
            text=_req(s, "text", where),
            speaker=s.get("speaker", "narrator"),
            choices=tuple(choices),
            companion_lines=dict(s.get("companion_lines", {})),
            background=s.get("background", ""),
        )

    endings = {
        eid: Ending(
            id=eid,
            title=_req(e, "title", f"{sid}.endings.{eid}"),
            text=_req(e, "text", f"{sid}.endings.{eid}"),
            reflection_questions=tuple(e.get("reflection_questions", [])),
            tone=e.get("tone", "neutral"),
        )
        for eid, e in _req(data, "endings", sid).items()
    }

    return Scenario(
        id=sid,
        version=_req(data, "version", sid),
        title=_req(data, "title", sid),
        summary=data.get("summary", ""),
        start=_req(data, "start", sid),
        scenes=scenes,
        endings=endings,
        initial_state=dict(data.get("initial_state", {})),
        audience=dict(data.get("audience", {})),
        learning_goals=tuple(data.get("learning_goals", [])),
    )


def load_scenario(path: str | Path) -> Scenario:
    with open(path, encoding="utf-8") as f:
        return scenario_from_dict(json.load(f))


def load_all(directory: str | Path) -> dict[str, Scenario]:
    out: dict[str, Scenario] = {}
    for p in sorted(Path(directory).glob("*.json")):
        sc = load_scenario(p)
        out[sc.id] = sc
    return out
