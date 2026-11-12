"""Web server: the game page + a small JSON API. Stdlib only.

Local:   python -m tqfai serve      ->  open http://127.0.0.1:8787
Online:  the same code runs on Vercel through api/index.py

The server keeps NOTHING between requests. The browser holds the game "save"
(which scene you are on, the choices made) and sends it back with each move.
That is why it works on Vercel, and why no player data is ever stored.

Endpoints (see docs/API.md):
    GET  /api/health
    GET  /api/companions
    GET  /api/scenarios
    POST /api/start    {"scenario_id": "...", "companion_id": "..."}
    POST /api/choose   {"save": {...}, "choice_id": "..."}
"""

from __future__ import annotations

import json
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .. import REPO_ROOT, SCENARIO_DIR, __version__
from ..companions import CompanionRegistry
from ..engine import STATE_MAX, STATE_MIN, EngineError, NarrativeEngine
from ..reasoning import get_reasoner
from ..scenario import WORLD_STATE_KEYS, load_all
from ..session import Session

WEB_DIR = REPO_ROOT / "web"
WEB_PAGE = WEB_DIR / "index.html"
STATIC_FILE = re.compile(r"^/((?:fonts/)?[a-z0-9_-]+\.(?:js|woff2|svg|png|ico))$")
STATIC_TYPES = {".js": "text/javascript; charset=utf-8", ".woff2": "font/woff2", ".svg": "image/svg+xml",
                ".png": "image/png", ".ico": "image/x-icon"}
MAX_BODY = 64_000


def load_dotenv(path: Path = REPO_ROOT / ".env") -> None:
    """Read KEY=value lines from a local .env file (never committed)."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


class GameService:
    """All game logic for the web. The HTTP handler is a thin wrapper."""

    def __init__(self, scenario_dir: str | Path = SCENARIO_DIR, reasoner: str = "auto"):
        self.companions = CompanionRegistry.load()
        self.scenarios = load_all(scenario_dir)
        self.reasoner = get_reasoner(reasoner)

    def engine_for(self, scenario_id: str) -> NarrativeEngine:
        if scenario_id not in self.scenarios:
            raise EngineError(f"Unknown story '{scenario_id}'.")
        return NarrativeEngine(self.scenarios[scenario_id], self.companions, self.reasoner)

    def start(self, scenario_id: str, companion_id: str) -> dict:
        engine = self.engine_for(scenario_id)
        if companion_id not in self.companions.ids():
            raise EngineError("Please pick one of the helpers.")
        session = engine.start(companion_id)
        return {**engine.view(session), "save": session.to_dict()}

    def choose(self, save: dict, choice_id: str) -> dict:
        session = self._load_save(save)
        engine = self.engine_for(session.scenario_id)
        out = engine.choose(session, choice_id)
        return {**out, "save": session.to_dict()}

    def _load_save(self, save: dict) -> Session:
        try:
            s = Session.from_dict(save)
        except Exception:
            raise EngineError("This game save is broken. Please start a new game.") from None
        sc = self.scenarios.get(s.scenario_id)
        if sc is None or s.current not in sc.scenes or s.companion_id not in self.companions.ids():
            raise EngineError("This game save is out of date. Please start a new game.")
        try:
            s.state = {k: max(STATE_MIN, min(STATE_MAX, int(s.state.get(k, 0)))) for k in WORLD_STATE_KEYS}
        except (TypeError, ValueError):
            raise EngineError("This game save is broken. Please start a new game.") from None
        s.history = s.history[-50:]
        return s

    def info(self, what: str) -> dict:
        if what == "health":
            return {"ok": True, "version": __version__, "voice": self.reasoner.name}
        if what == "companions":
            return {"companions": [c.to_dict() for c in self.companions.all()], "guide": self.companions.guide}
        if what == "scenarios":
            return {"scenarios": [
                {"id": s.id, "title": s.title, "summary": s.summary, "version": s.version,
                 "audience": s.audience, "learning_goals": list(s.learning_goals)}
                for s in self.scenarios.values()]}
        raise KeyError(what)


def make_handler(service: GameService):
    class Handler(BaseHTTPRequestHandler):
        server_version = f"tqfai/{__version__}"

        def _send(self, code: int, payload: dict | bytes, ctype: str = "application/json; charset=utf-8") -> None:
            body = payload if isinstance(payload, bytes) else json.dumps(payload, ensure_ascii=False).encode()
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _route(self) -> str:
            path = self.path.split("?")[0].rstrip("/")
            return path[4:] if path.startswith("/api") else path  # "/api/start" -> "/start"

        def do_OPTIONS(self):  # noqa: N802
            self._send(204, b"")

        def do_GET(self):  # noqa: N802
            route = self._route()
            if route in ("", "/index.html") and WEB_PAGE.exists():
                return self._send(200, WEB_PAGE.read_bytes(), "text/html; charset=utf-8")
            m = STATIC_FILE.match(route)
            if m and (WEB_DIR / m.group(1)).is_file():
                f = WEB_DIR / m.group(1)
                return self._send(200, f.read_bytes(), STATIC_TYPES[f.suffix])
            try:
                return self._send(200, service.info(route.lstrip("/")))
            except KeyError:
                return self._send(404, {"error": "Not found."})

        def do_POST(self):  # noqa: N802
            route = self._route()
            try:
                n = int(self.headers.get("Content-Length") or 0)
                if n > MAX_BODY:
                    return self._send(413, {"error": "Request too big."})
                body = json.loads(self.rfile.read(n) or b"{}") if n else {}
                if route == "/start":
                    return self._send(200, service.start(body.get("scenario_id", ""), body.get("companion_id", "")))
                if route == "/choose":
                    return self._send(200, service.choose(body.get("save") or {}, body.get("choice_id", "")))
                return self._send(404, {"error": "Not found."})
            except (json.JSONDecodeError, ValueError):
                return self._send(400, {"error": "Body must be JSON."})
            except EngineError as e:
                return self._send(400, {"error": str(e)})

        def log_message(self, fmt, *args):  # never log bodies
            pass

    return Handler


def serve(host: str = "127.0.0.1", port: int = 8787, reasoner: str = "auto") -> None:
    load_dotenv()
    service = GameService(reasoner=reasoner)
    httpd = ThreadingHTTPServer((host, port), make_handler(service))
    print(f"Game running at http://{host}:{port}  (helper voice: {service.reasoner.name})")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
