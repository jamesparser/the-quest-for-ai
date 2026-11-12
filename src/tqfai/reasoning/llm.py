"""AI voice for the companion, using any OpenAI-style chat API (stdlib only).

Default: ASI Cloud, model asi1-mini (free). Settings come from environment
variables, never from the code or the browser:

    TQFAI_LLM_API_KEY   the secret key (required, otherwise AI is off)
    TQFAI_LLM_BASE_URL  default https://inference.asicloud.cudos.org/v1
    TQFAI_LLM_MODEL     default asi1-mini

How it stays safe and cheap:
* The browser never sees the key. Only the server calls the AI.
* The server builds every prompt from the story files. Players cannot type
  anything to the AI, so nobody can use our key as a free chatbot.
* Every AI line is checked. If it is too long, asks for personal info, or the
  AI is slow / down, the written baseline line is used instead.
"""

from __future__ import annotations

import json
import os
import re
import urllib.request

from ..companions import Companion
from ..scenario import Choice, Scene
from ..scenario.validator import PERSONAL_INFO_PATTERNS
from .base import Interpretation
from .rules_baseline import RulesBaseline

DEFAULT_BASE_URL = "https://inference.asicloud.cudos.org/v1"
DEFAULT_MODEL = "asi1-mini"
MAX_CHARS = 280
BLOCKED = re.compile(r"https?://|www\.|@|\b(stupid|idiot|loser|dumb|hate|kill|die)\b", re.IGNORECASE)

SYSTEM_PROMPT = """You are {name}, {title}, an AI helper in a video game for kids aged 9 to 12.
Your personality: {style}.
The player just made a choice. Reply in 1 or 2 short sentences, under 35 words, in very simple English.
Rules:
- Say what you noticed about the choice and how the other characters might feel.
- Be warm. Never grade, judge, lecture, or say the choice was right or wrong.
- You may end with one short, open question about the game.
- Never ask about the player's real life, name, age, school, or location.
- No links, no emojis, no bad words.
Reply with only your words, no quotes, no name."""


class LLMReasoner:
    name = "llm"

    def __init__(self, api_key: str | None = None, base_url: str | None = None,
                 model: str | None = None, timeout: float = 8.0):
        self.api_key = api_key if api_key is not None else os.environ.get("TQFAI_LLM_API_KEY", "")
        self.base_url = (base_url or os.environ.get("TQFAI_LLM_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self.model = model or os.environ.get("TQFAI_LLM_MODEL") or DEFAULT_MODEL
        self.timeout = timeout
        self.fallback = RulesBaseline()

    @property
    def active(self) -> bool:
        return bool(self.api_key)

    def interpret(self, scene: Scene, choice: Choice, state: dict[str, int], companion: Companion) -> Interpretation:
        base = self.fallback.interpret(scene, choice, state, companion)
        if not self.active:
            return base
        try:
            text = self._ask(scene, choice, state, companion)
        except Exception:  # network error, timeout, bad reply: keep the game going
            return base
        if not is_safe(text):
            return base
        base.companion_note = text
        base.source = self.model
        return base

    def _ask(self, scene: Scene, choice: Choice, state: dict[str, int], companion: Companion) -> str:
        mood = "tense" if state.get("entropy", 0) >= 4 else "calm" if state.get("entropy", 0) <= 1 else "a bit tense"
        user = (
            f"What was happening: {scene.text}\n"
            f"The player chose: {choice.text}\n"
            f"What happened next: {choice.reaction or 'nothing yet'}\n"
            f"Ideas this choice shows: {', '.join(choice.perspectives) or 'not clear'}\n"
            f"The team mood is now {mood}."
        )
        body = json.dumps({
            "model": self.model,
            "max_tokens": 90,
            "temperature": 0.7,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT.format(name=companion.name, title=companion.title, style=companion.style)},
                {"role": "user", "content": user},
            ],
        }).encode()
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions", data=body, method="POST",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"},
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            data = json.loads(r.read())
        return clean(data["choices"][0]["message"]["content"])


def clean(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text or "", flags=re.DOTALL).strip()
    return text.strip().strip('"').strip()


def is_safe(text: str) -> bool:
    return bool(text) and len(text) <= MAX_CHARS and not PERSONAL_INFO_PATTERNS.search(text) and not BLOCKED.search(text)
