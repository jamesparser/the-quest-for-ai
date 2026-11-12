import json
import sys
import threading
import unittest
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tqfai import SCENARIO_DIR  # noqa: E402
from tqfai.api import GameService, make_handler  # noqa: E402
from tqfai.cli import main as cli_main  # noqa: E402
from tqfai.companions import CompanionRegistry  # noqa: E402
from tqfai.reasoning import LLMReasoner, RulesBaseline  # noqa: E402
from tqfai.scenario import load_all  # noqa: E402

SC = load_all(SCENARIO_DIR)["s01_the_lagging_teammate"]
COMPS = CompanionRegistry.load()


def start_server(handler_cls):
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler_cls)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{httpd.server_address[1]}"


class Api(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd, cls.base = start_server(make_handler(GameService(reasoner="baseline")))

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()

    def call(self, method, path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.base + path, data=data, method=method,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req) as r:
                raw = r.read()
                return r.status, (json.loads(raw) if r.headers["Content-Type"].startswith("application/json") else raw)
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    def test_full_game_over_http(self):
        self.assertEqual(self.call("GET", "/api/health")[0], 200)
        self.assertEqual(len(self.call("GET", "/api/companions")[1]["companions"]), 4)
        code, v = self.call("POST", "/api/start", {"scenario_id": SC.id, "companion_id": "ClassClown"})
        self.assertEqual(code, 200)
        for cid in ["c_speak_up", "c_hear_max", "c_give_mia", "c_explain_max", "c_warn_team", "c_thank_team",
                    "c_revive_max", "c_final_plan", "c_gg_all"]:
            code, v = self.call("POST", "/api/choose", {"save": v["save"], "choice_id": cid})
            self.assertEqual(code, 200, v)
        self.assertEqual(v["ending"]["id"], "e_mycelial")

    def test_serves_game_page(self):
        code, body = self.call("GET", "/")
        self.assertEqual(code, 200)
        self.assertIn(b"The Quest for AI", body)

    def test_errors_are_400_with_message(self):
        self.assertEqual(self.call("POST", "/api/start", {"scenario_id": "nope", "companion_id": "Protector"})[0], 400)
        self.assertEqual(self.call("POST", "/api/start", {"scenario_id": SC.id, "companion_id": "Dragon"})[0], 400)
        code, v = self.call("POST", "/api/choose", {"save": {"junk": 1}, "choice_id": "c_ask_sam"})
        self.assertEqual(code, 400)
        self.assertIn("start a new game", v["error"])

    def test_tampered_save_is_clamped(self):
        _, v = self.call("POST", "/api/start", {"scenario_id": SC.id, "companion_id": "Protector"})
        save = v["save"]
        save["state"]["entropy"] = 999
        code, v = self.call("POST", "/api/choose", {"save": save, "choice_id": "c_pile_on"})
        self.assertEqual(code, 200)
        self.assertEqual(v["state"]["entropy"], 10)


class FakeAI(BaseHTTPRequestHandler):
    reply = "You checked on Sam first. How do you think Sam feels now?"
    seen = []

    def do_POST(self):  # noqa: N802
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        FakeAI.seen.append((self.headers.get("Authorization"), body))
        out = json.dumps({"choices": [{"message": {"content": FakeAI.reply}}]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def log_message(self, *a):
        pass


class AIVoice(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd, cls.base = start_server(FakeAI)

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()

    def interpret(self, reasoner):
        scene = SC.scenes["intro"]
        choice = next(c for c in scene.choices if c.id == "c_ask_sam")
        return reasoner.interpret(scene, choice, {"entropy": 1}, COMPS.get("Bookworm"))

    def test_uses_ai_line_and_sends_key_only_to_ai(self):
        FakeAI.reply = "You checked on Sam first. How do you think Sam feels now?"
        out = self.interpret(LLMReasoner(api_key="test-key", base_url=self.base + "/v1", model="asi1-mini"))
        self.assertEqual(out.companion_note, FakeAI.reply)
        self.assertEqual(out.source, "asi1-mini")
        self.assertEqual(out.perspectives, ["curiosity", "empathy"])
        auth, body = FakeAI.seen[-1]
        self.assertEqual(auth, "Bearer test-key")
        self.assertEqual(body["model"], "asi1-mini")

    def test_unsafe_ai_line_falls_back(self):
        FakeAI.reply = "Cool! What school do you go to?"
        out = self.interpret(LLMReasoner(api_key="k", base_url=self.base + "/v1"))
        self.assertEqual(out.source, "baseline")

    def test_ai_down_falls_back(self):
        out = self.interpret(LLMReasoner(api_key="k", base_url="http://127.0.0.1:9/v1", timeout=1))
        self.assertEqual(out.source, "baseline")

    def test_no_key_means_written_lines(self):
        self.assertEqual(self.interpret(LLMReasoner(api_key="")).source, "baseline")


class CliAndReasoning(unittest.TestCase):
    def test_validate_command_passes(self):
        self.assertEqual(cli_main(["validate"]), 0)

    def test_eval_command_runs(self):
        self.assertEqual(cli_main(["eval"]), 0)

    def test_baseline_matches_all_eval_cases(self):
        r = RulesBaseline()
        cases = json.loads((ROOT / "tests" / "eval_cases.json").read_text())["cases"]
        for c in cases:
            scene = SC.scenes[c["scene_id"]]
            ch = next(x for x in scene.choices if x.id == c["choice_id"])
            out = r.interpret(scene, ch, {}, COMPS.get(c["companion_id"]))
            self.assertTrue(set(c["expect_perspectives"]) <= set(out.perspectives), c)
            self.assertEqual(out.uncertain, c["expect_uncertain"], c)


if __name__ == "__main__":
    unittest.main()
