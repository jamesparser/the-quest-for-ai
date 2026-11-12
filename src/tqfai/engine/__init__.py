"""Deterministic narrative engine.

Same scenario + same companion + same choices  ->  same outcome, every time.
Clients (CLI, web, VR) only ever see the dicts returned by ``view()`` / ``choose()``;
that dict shape is the client contract documented in docs/API.md.
"""

from __future__ import annotations

from ..companions import CompanionRegistry
from ..reasoning import Reasoner, RulesBaseline
from ..scenario import Ending, Scenario, Scene
from ..session import ReflectionEntry, Session

STATE_MIN, STATE_MAX = 0, 10


class EngineError(Exception):
    """A gentle, client-displayable error (e.g. a choice that isn't available)."""


class NarrativeEngine:
    def __init__(
        self,
        scenario: Scenario,
        companions: CompanionRegistry | None = None,
        reasoner: Reasoner | None = None,
    ):
        self.scenario = scenario
        self.companions = companions or CompanionRegistry.load()
        self.reasoner = reasoner or RulesBaseline()

    # -- lifecycle ---------------------------------------------------------
    def start(self, companion_id: str) -> Session:
        self.companions.get(companion_id)  # validates id
        return Session(
            scenario_id=self.scenario.id,
            scenario_version=self.scenario.version,
            companion_id=companion_id,
            current=self.scenario.start,
            state={"entropy": 0, "connection": 0, "shade": 0, **self.scenario.initial_state},
        )

    def choose(self, session: Session, choice_id: str) -> dict:
        if session.finished:
            raise EngineError("This story has already reached an ending. Start a new session to play again.")
        scene = self.scenario.scenes[session.current]
        choice = next((c for c in self._available(scene, session) if c.id == choice_id), None)
        if choice is None:
            raise EngineError(f"'{choice_id}' isn't one of the paths open right now. Try another one.")

        for k, delta in choice.effects.items():
            session.state[k] = max(STATE_MIN, min(STATE_MAX, session.state.get(k, 0) + delta))

        companion = self.companions.get(session.companion_id)
        interp = self.reasoner.interpret(scene, choice, session.state, companion)
        session.history.append(
            ReflectionEntry(
                scene_id=scene.id, choice_id=choice.id, choice_text=choice.text,
                perspectives=interp.perspectives, companion_note=interp.companion_note,
                uncertain=interp.uncertain,
            )
        )
        session.current = choice.next
        session.finished = self.scenario.is_ending(choice.next)

        out = self.view(session)
        out["last"] = {"choice_id": choice.id, "reaction": choice.reaction, **interp.to_dict()}
        return out

    # -- rendering ---------------------------------------------------------
    def view(self, session: Session) -> dict:
        node = self.scenario.node(session.current)
        companion = self.companions.get(session.companion_id)
        base = {
            "session_id": session.id,
            "scenario": {"id": self.scenario.id, "title": self.scenario.title, "version": self.scenario.version},
            "companion": companion.to_dict(),
            "state": dict(session.state),
            "finished": session.finished,
        }
        if isinstance(node, Ending):
            base["ending"] = {
                "id": node.id, "title": node.title, "text": node.text, "tone": node.tone,
                "reflection_questions": list(node.reflection_questions),
                "perspectives_used": session.perspective_summary(),
                "path": [h.choice_id for h in session.history],
            }
            return base
        assert isinstance(node, Scene)
        base["scene"] = {
            "id": node.id,
            "speaker": node.speaker,
            "text": node.text,
            "background": node.background,
            "companion_line": node.companion_lines.get(companion.id)
            or node.companion_lines.get("default", ""),
            "choices": [{"id": c.id, "text": c.text} for c in self._available(node, session)],
        }
        return base

    @staticmethod
    def _available(scene: Scene, session: Session):
        return [c for c in scene.choices if c.condition is None or c.condition.holds(session.state)]


__all__ = ["EngineError", "NarrativeEngine"]
