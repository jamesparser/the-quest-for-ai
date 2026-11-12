"""Transparent rules-based reasoner. The baseline every fancier reasoner must beat."""

from __future__ import annotations

from ..companions import Companion
from ..scenario import Choice, Scene
from .base import Interpretation

# One gentle, non-judgemental reflection per perspective. Companions never grade.
REFLECTIONS = {
    "empathy": "You thought about how they might be feeling.",
    "boundaries": "You protected a limit - yours or someone else's.",
    "fairness": "You were thinking about what's fair for the whole team.",
    "curiosity": "You asked before assuming. That's how roots find water.",
    "repair": "You tried to reconnect a broken link in the network.",
    "self_care": "You stepped into the Shade to cool down. That's allowed.",
    "escalation": "That turned the heat up a bit. Want to see where it goes?",
}

# Companion-flavoured openers.
OPENERS = {
    "Protector": "Steady.",
    "Bookworm": "Interesting data point!",
    "ScientificallyAttuned": "I felt the network shift.",
    "ClassClown": "Plot twist!",
}


class RulesBaseline:
    name = "baseline"

    def interpret(
        self, scene: Scene, choice: Choice, state: dict[str, int], companion: Companion
    ) -> Interpretation:
        perspectives = [p for p in choice.perspectives if p in REFLECTIONS]
        opener = OPENERS.get(companion.id, "Hmm.")
        if not perspectives:
            return Interpretation(
                companion_note=f"{opener} I'm not totally sure what you were going for - "
                "that's okay. What made you pick that?",
                perspectives=[],
                uncertain=True,
                source=self.name,
            )
        lines = " ".join(REFLECTIONS[p] for p in perspectives[:2])
        # Ambiguous when a choice carries both a calming and an escalating tag.
        uncertain = "escalation" in perspectives and len(perspectives) > 1
        tail = " I might be reading this wrong, though." if uncertain else ""
        return Interpretation(
            companion_note=f"{opener} {lines}{tail}",
            perspectives=perspectives,
            uncertain=uncertain,
            source=self.name,
        )
