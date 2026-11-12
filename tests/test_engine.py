import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tqfai import SCENARIO_DIR  # noqa: E402
from tqfai.engine import EngineError, NarrativeEngine  # noqa: E402
from tqfai.scenario import load_all  # noqa: E402
from tqfai.session import Session  # noqa: E402

SC = load_all(SCENARIO_DIR)["s01_the_lagging_teammate"]


def play(path, companion="Bookworm"):
    eng = NarrativeEngine(SC)
    s = eng.start(companion)
    view = eng.view(s)
    for cid in path:
        view = eng.choose(s, cid)
    return eng, s, view


class Engine(unittest.TestCase):
    def test_happy_path_reaches_warm_ending(self):
        path = ["c_ask_sam", "c_suggest_role", "c_give_mia", "c_explain_max", "c_warn_team", "c_thank_team", "c_revive_max", "c_final_plan", "c_friend_sam"]
        _, s, v = play(path)
        self.assertTrue(v["finished"])
        self.assertEqual(v["ending"]["id"], "e_mycelial")
        self.assertEqual(v["ending"]["path"], path)
        self.assertIn("curiosity", v["ending"]["perspectives_used"])

    def test_deterministic(self):
        path = ["c_pile_on", "c_call_break", "c_squad_rule", "c_grab", "c_keep_it", "c_chat_back",
                "c_block_now", "c_onward", "c_mock_max", "c_final_charge", "c_blame"]
        a, b = play(path)[2], play(path)[2]
        self.assertEqual(a["ending"]["id"], "e_cold_network")
        for k in ("state", "ending"):
            self.assertEqual(a[k], b[k])

    def test_condition_gates_vote_kick(self):
        _, _, v = play(["c_pile_on"])  # entropy 1+3 = 4
        self.assertIn("c_vote_kick", [c["id"] for c in v["scene"]["choices"]])
        _, _, v = play(["c_ask_sam", "c_keep_quiet"])  # entropy 2
        self.assertNotIn("c_vote_kick", [c["id"] for c in v["scene"]["choices"]])

    def test_unavailable_choice_is_gentle_error(self):
        eng, s, _ = play([])
        with self.assertRaises(EngineError):
            eng.choose(s, "c_vote_kick")

    def test_cannot_continue_after_ending(self):
        eng, s, _ = play(["c_step_into_shade", "c_log_off"])
        with self.assertRaises(EngineError):
            eng.choose(s, "anything")

    def test_unknown_companion(self):
        with self.assertRaises(KeyError):
            NarrativeEngine(SC).start("Dragon")

    def test_companion_specific_and_default_lines(self):
        _, _, v = play([], companion="Protector")
        self.assertEqual(v["scene"]["companion_line"], SC.scenes["intro"].companion_lines["Protector"])
        _, _, v = play(["c_ask_sam"], companion="Protector")  # no Protector line in s_sam_reply
        self.assertEqual(v["scene"]["companion_line"], SC.scenes["s_sam_reply"].companion_lines["default"])

    def test_state_is_clamped(self):
        _, s, _ = play(["c_step_into_shade", "c_squad_rule"])
        self.assertTrue(all(0 <= v <= 10 for v in s.state.values()))

    def test_session_roundtrip(self):
        eng, s, _ = play(["c_speak_up"])
        s2 = Session.from_dict(s.to_dict())
        self.assertEqual(eng.choose(s2, "c_hear_max")["scene"]["id"], "s_regroup")

    def test_every_ending_reachable_in_actual_play(self):
        """Search every real path (respects conditions). Remembers visited (scene, state) to avoid loops."""
        eng = NarrativeEngine(SC)
        found, seen = set(), set()

        def dfs(sess):
            key = (sess.current, tuple(sorted(sess.state.items())))
            if key in seen:
                return
            seen.add(key)
            v = eng.view(sess)
            if v["finished"]:
                found.add(v["ending"]["id"])
                return
            for c in v["scene"]["choices"]:
                s2 = Session.from_dict(sess.to_dict())
                eng.choose(s2, c["id"])
                dfs(s2)

        dfs(eng.start("Bookworm"))
        self.assertEqual(found, set(SC.endings))

    def test_game_is_long_enough(self):
        """A full game (not logging off early) takes at least 7 choices."""
        _, _, v = play(["c_ask_sam", "c_suggest_role", "c_roll", "c_cheer_max", "c_block_report",
                        "c_onward", "c_calm_max", "c_final_plan", "c_gg_all"])
        self.assertEqual(v["ending"]["id"], "e_mycelial")
        self.assertGreaterEqual(len(v["ending"]["path"]), 7)

if __name__ == "__main__":
    unittest.main()
