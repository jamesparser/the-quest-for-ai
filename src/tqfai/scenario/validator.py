"""Automated checks for scenario content (ROADMAP milestone 2).

Run on every scenario in CI:  ``python -m tqfai validate``
"""

from __future__ import annotations

import re
from collections import deque
from dataclasses import dataclass

from .model import PERSPECTIVES, WORLD_STATE_KEYS, Scenario

MAX_SCENE_CHARS = 700     # keep reading load reasonable for 9-12 year olds
MAX_CHOICE_CHARS = 120

# Very small safety lint: the experience must never ask a child for identifying info.
PERSONAL_INFO_PATTERNS = re.compile(
    r"\b(your (real |full )?name|home address|where do you live|phone number|password|"
    r"what school|your school|your age|send (a )?(photo|pic|selfie))\b",
    re.IGNORECASE,
)


@dataclass
class Issue:
    level: str  # "error" | "warning"
    where: str
    message: str

    def __str__(self) -> str:
        return f"[{self.level.upper()}] {self.where}: {self.message}"


def validate(scenario: Scenario, known_companions: set[str] | None = None) -> list[Issue]:
    issues: list[Issue] = []
    err = lambda w, m: issues.append(Issue("error", w, m))  # noqa: E731
    warn = lambda w, m: issues.append(Issue("warning", w, m))  # noqa: E731
    sid = scenario.id

    # --- references -------------------------------------------------------
    overlap = set(scenario.scenes) & set(scenario.endings)
    if overlap:
        err(sid, f"ids used for both scenes and endings: {sorted(overlap)}")
    if scenario.start not in scenario.scenes:
        err(sid, f"start '{scenario.start}' is not a scene")
    if len(scenario.endings) < 2:
        err(sid, "needs at least two distinct endings (roadmap milestone 1)")

    for key in scenario.initial_state:
        if key not in WORLD_STATE_KEYS:
            err(f"{sid}.initial_state", f"unknown world-state key '{key}'")

    for scene in scenario.scenes.values():
        w = f"{sid}.{scene.id}"
        if not scene.choices:
            err(w, "scene has no choices (only endings may be terminal)")
        if len(scene.text) > MAX_SCENE_CHARS:
            warn(w, f"text is {len(scene.text)} chars (> {MAX_SCENE_CHARS}); consider splitting")
        if "default" not in scene.companion_lines and scene.companion_lines:
            warn(w, "companion_lines has no 'default' fallback")
        if known_companions:
            for cid in scene.companion_lines:
                if cid != "default" and cid not in known_companions:
                    err(w, f"companion_lines references unknown companion '{cid}'")
        seen: set[str] = set()
        for ch in scene.choices:
            cw = f"{w}.{ch.id}"
            if ch.id in seen:
                err(cw, "duplicate choice id in scene")
            seen.add(ch.id)
            if scenario.node(ch.next) is None:
                err(cw, f"next '{ch.next}' does not exist")
            for p in ch.perspectives:
                if p not in PERSPECTIVES:
                    err(cw, f"unknown perspective '{p}'")
            for k in ch.effects:
                if k not in WORLD_STATE_KEYS:
                    err(cw, f"unknown effect key '{k}'")
            if len(ch.text) > MAX_CHOICE_CHARS:
                warn(cw, f"choice text is {len(ch.text)} chars (> {MAX_CHOICE_CHARS})")
        if scene.choices and all(c.condition for c in scene.choices):
            warn(w, "every choice is conditional; player could get stuck")

    # --- safety lint ------------------------------------------------------
    texts = [(f"{sid}.{s.id}", s.text) for s in scenario.scenes.values()]
    texts += [(f"{sid}.{s.id}.{c.id}", c.text) for s in scenario.scenes.values() for c in s.choices]
    texts += [(f"{sid}.{s.id}.companion", t) for s in scenario.scenes.values() for t in s.companion_lines.values()]
    texts += [(f"{sid}.{e.id}", e.text) for e in scenario.endings.values()]
    for where, text in texts:
        if PERSONAL_INFO_PATTERNS.search(text):
            err(where, "text appears to ask for personal information")

    # --- reachability (ignores conditions; a structural check) -----------
    if scenario.start in scenario.scenes:
        reachable = _reachable(scenario, scenario.start)
        for nid in list(scenario.scenes) + list(scenario.endings):
            if nid not in reachable:
                err(f"{sid}.{nid}", "unreachable from start")
        for scene_id in scenario.scenes:
            if scene_id in reachable and not (_reachable(scenario, scene_id) & set(scenario.endings)):
                err(f"{sid}.{scene_id}", "no path from here to any ending (dead end / loop)")

    return issues


def _reachable(scenario: Scenario, start: str) -> set[str]:
    seen, queue = {start}, deque([start])
    while queue:
        node = scenario.scenes.get(queue.popleft())
        if not node:
            continue
        for ch in node.choices:
            if ch.next not in seen and scenario.node(ch.next) is not None:
                seen.add(ch.next)
                queue.append(ch.next)
    return seen


def has_errors(issues: list[Issue]) -> bool:
    return any(i.level == "error" for i in issues)
