import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tqfai import SCENARIO_DIR  # noqa: E402
from tqfai.companions import CompanionRegistry  # noqa: E402
from tqfai.scenario import ScenarioFormatError, has_errors, load_all, scenario_from_dict, validate  # noqa: E402

S01 = SCENARIO_DIR / "s01_the_lagging_teammate.json"


def raw():
    return json.loads(S01.read_text(encoding="utf-8"))


class ShippedContent(unittest.TestCase):
    def test_every_scenario_validates_clean(self):
        ids = CompanionRegistry.load().ids()
        scenarios = load_all(SCENARIO_DIR)
        self.assertTrue(scenarios, "no scenarios shipped")
        for sc in scenarios.values():
            errors = [str(i) for i in validate(sc, ids) if i.level == "error"]
            self.assertEqual(errors, [], sc.id)


class ValidatorCatchesProblems(unittest.TestCase):
    def check(self, mutate, needle):
        d = copy.deepcopy(raw())
        mutate(d)
        issues = validate(scenario_from_dict(d), CompanionRegistry.load().ids())
        self.assertTrue(has_errors(issues))
        self.assertTrue(any(needle in i.message for i in issues), [str(i) for i in issues])

    def test_broken_reference(self):
        self.check(lambda d: d["scenes"]["intro"]["choices"][0].update(next="nowhere"), "does not exist")

    def test_unreachable_scene(self):
        self.check(lambda d: d["scenes"].update(orphan={"text": "x", "choices": [{"id": "a", "text": "a", "next": "e_rest"}]}), "unreachable")

    def test_dead_end_loop(self):
        def m(d):
            d["scenes"]["loop"] = {"text": "x", "choices": [{"id": "a", "text": "a", "next": "loop"}]}
            d["scenes"]["intro"]["choices"][0]["next"] = "loop"
        self.check(m, "no path")

    def test_unknown_perspective(self):
        self.check(lambda d: d["scenes"]["intro"]["choices"][0].update(perspectives=["winning"]), "unknown perspective")

    def test_unknown_companion(self):
        self.check(lambda d: d["scenes"]["intro"]["companion_lines"].update(Dragon="hi"), "unknown companion")

    def test_personal_info_request(self):
        self.check(lambda d: d["scenes"]["intro"].update(text="What school do you go to?"), "personal information")

    def test_missing_required_field(self):
        d = raw()
        del d["scenes"]["intro"]["text"]
        with self.assertRaises(ScenarioFormatError):
            scenario_from_dict(d)


if __name__ == "__main__":
    unittest.main()
