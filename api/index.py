"""Vercel entry point. Vercel runs this file for every /api/... request.

The AI key is NOT here. It is set in the Vercel project settings as the
environment variable TQFAI_LLM_API_KEY, so only the server can read it.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from tqfai.api.server import GameService, make_handler  # noqa: E402

_GameHandler = make_handler(GameService(reasoner=os.environ.get("TQFAI_REASONER", "auto")))


class handler(_GameHandler):  # noqa: N801  (Vercel needs this exact name)
    pass
