import os

from .base import Interpretation, Reasoner
from .llm import LLMReasoner
from .metta_adapter import HYPERON_AVAILABLE, MettaReasoner
from .rules_baseline import RulesBaseline


def get_reasoner(name: str = "auto") -> Reasoner:
    """auto = AI voice if a key is set, otherwise the written lines."""
    if name == "auto":
        return LLMReasoner() if os.environ.get("TQFAI_LLM_API_KEY") else RulesBaseline()
    if name == "baseline":
        return RulesBaseline()
    if name == "llm":
        return LLMReasoner()
    if name == "metta":
        return MettaReasoner()
    raise ValueError(f"Unknown reasoner '{name}' (use auto, baseline, llm or metta)")


__all__ = ["HYPERON_AVAILABLE", "Interpretation", "LLMReasoner", "MettaReasoner", "Reasoner", "RulesBaseline", "get_reasoner"]
