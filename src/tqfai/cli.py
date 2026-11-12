"""Command line entry point.

    python -m tqfai play [--scenario ID] [--companion ID]   play in the terminal
    (--reasoner auto uses the AI voice when TQFAI_LLM_API_KEY is set, else written lines)
    python -m tqfai validate                                 check all scenario files
    python -m tqfai serve [--port 8787]                      JSON API for web/VR clients
    python -m tqfai eval                                     baseline vs MeTTa on fixed cases
"""

from __future__ import annotations

import argparse
import json
import sys
import textwrap

from . import REPO_ROOT, SCENARIO_DIR
from .companions import CompanionRegistry
from .engine import EngineError, NarrativeEngine
from .reasoning import get_reasoner
from .scenario import has_errors, load_all, validate


def _wrap(text: str) -> str:
    return "\n".join(textwrap.fill(p, 78) for p in text.split("\n"))


def cmd_validate(_args) -> int:
    companions = CompanionRegistry.load()
    scenarios = load_all(SCENARIO_DIR)
    failed = False
    for sc in scenarios.values():
        issues = validate(sc, companions.ids())
        status = "FAIL" if has_errors(issues) else "ok"
        print(f"{status:4}  {sc.id} v{sc.version}  ({len(sc.scenes)} scenes, {len(sc.endings)} endings)")
        for i in issues:
            print(f"      {i}")
        failed |= has_errors(issues)
    if not scenarios:
        print("No scenarios found in content/scenarios/")
        return 1
    return 1 if failed else 0


def cmd_play(args) -> int:
    from .api.server import load_dotenv

    load_dotenv()
    companions = CompanionRegistry.load()
    scenarios = load_all(SCENARIO_DIR)
    sc = scenarios.get(args.scenario) or next(iter(scenarios.values()))
    comp_id = args.companion
    if not comp_id:
        print(f"\n== {sc.title} ==\n{_wrap(sc.summary)}\n\nChoose your AI partner:")
        all_c = companions.all()
        for i, c in enumerate(all_c, 1):
            print(f"  {i}. {c.name} - {c.title}: {c.style}")
        comp_id = all_c[_ask(len(all_c)) - 1].id
    engine = NarrativeEngine(sc, companions, get_reasoner(args.reasoner))
    session = engine.start(comp_id)
    comp = companions.get(comp_id)
    print(f"\n{comp.name}: \"{comp.greeting}\"")
    view = engine.view(session)
    while True:
        if "last" in view:
            if view["last"]["reaction"]:
                print(f"\n  > {_wrap(view['last']['reaction'])}")
            print(f"  {comp.name}: \"{view['last']['companion_note']}\"")
        if view["finished"]:
            e = view["ending"]
            print(f"\n*** {e['title']} ***\n{_wrap(e['text'])}\n\nThings to think about:")
            for q in e["reflection_questions"]:
                print(f"  - {q}")
            return 0
        s = view["scene"]
        print(f"\n{_wrap(s['text'])}")
        if s["companion_line"]:
            print(f"\n  {comp.name}: \"{s['companion_line']}\"")
        for i, c in enumerate(s["choices"], 1):
            print(f"  {i}. {c['text']}")
        pick = s["choices"][_ask(len(s["choices"])) - 1]["id"]
        try:
            view = engine.choose(session, pick)
        except EngineError as e:
            print(e)


def _ask(n: int) -> int:
    while True:
        raw = input(f"Choose 1-{n}: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= n:
            return int(raw)
        print("Hmm, try a number from the list.")


def cmd_serve(args) -> int:
    from .api import serve

    serve(args.host, args.port, args.reasoner)
    return 0


def cmd_eval(_args) -> int:
    """Decision-gate harness: run fixed cases through each reasoner and compare."""
    companions = CompanionRegistry.load()
    scenarios = load_all(SCENARIO_DIR)
    cases = json.loads((REPO_ROOT / "tests" / "eval_cases.json").read_text(encoding="utf-8"))["cases"]
    for rname in ("baseline", "metta"):
        r = get_reasoner(rname)
        hits = 0
        for case in cases:
            sc = scenarios[case["scenario_id"]]
            scene = sc.scenes[case["scene_id"]]
            choice = next(c for c in scene.choices if c.id == case["choice_id"])
            out = r.interpret(scene, choice, dict(sc.initial_state), companions.get(case["companion_id"]))
            ok = set(case["expect_perspectives"]) <= set(out.perspectives) and out.uncertain == case["expect_uncertain"]
            hits += ok
        print(f"{rname:9} {hits}/{len(cases)} cases match expectations")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="tqfai", description="The Quest for AI narrative engine")
    sub = p.add_subparsers(dest="cmd", required=True)
    pp = sub.add_parser("play")
    pp.add_argument("--scenario")
    pp.add_argument("--companion")
    pp.add_argument("--reasoner", default="auto", choices=["auto", "baseline", "llm", "metta"])
    sub.add_parser("validate")
    ps = sub.add_parser("serve")
    ps.add_argument("--host", default="127.0.0.1")
    ps.add_argument("--port", type=int, default=8787)
    ps.add_argument("--reasoner", default="auto", choices=["auto", "baseline", "llm", "metta"])
    sub.add_parser("eval")
    args = p.parse_args(argv)
    return {"play": cmd_play, "validate": cmd_validate, "serve": cmd_serve, "eval": cmd_eval}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
