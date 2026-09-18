"""Coinrun CLI: grade, replay, stress, list."""
from __future__ import annotations

import argparse
import base64
import copy
import importlib.util
import json
import pathlib
import random
import time
import zlib

from world import World
from viewer import write_replay

ROOT = pathlib.Path(__file__).resolve().parent


def load_cases(hidden=False):
    if hidden:
        data = (ROOT / "_private" / "hidden.dat").read_text(encoding="ascii")
        return json.loads(zlib.decompress(base64.b64decode(data)))
    return json.loads((ROOT / "visible.json").read_text(encoding="utf-8"))


def load_policy(filename):
    path = pathlib.Path(filename)
    if not path.is_absolute():
        path = ROOT / path
    spec = importlib.util.spec_from_file_location("submission", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not callable(getattr(module, "act", None)):
        raise ValueError("policy file must define act(obs)")
    return module


def run_case(case, policy, record=False):
    world, frames, durations = World(case), [], []
    error = None
    while not world.done:
        obs = copy.deepcopy(world.observe())
        start = time.perf_counter()
        try:
            action = policy.act(obs)
        except Exception as exc:
            error = f"policy raised {type(exc).__name__}: {exc}"
            durations.append((time.perf_counter() - start) * 1000)
            break
        durations.append((time.perf_counter() - start) * 1000)
        if type(action) is not bool:
            error = f"illegal action {action!r}; return True or False"
            break
        if record:
            snap = world.snapshot()
            debug = getattr(policy, "DEBUG", {})
            snap.update(action=action, debug=json.loads(json.dumps(debug, default=repr))
                        if isinstance(debug, dict) else {})
            frames.append(snap)
        world.step(action)
    result = world.result(error)
    result["max_ms"] = max(durations, default=0)
    if record:
        snap = world.snapshot()
        snap.update(action=None, debug={}, reason=result["reason"])
        frames.append(snap)
    return result, frames


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list")
    grade = commands.add_parser("grade", help="visible grading; --all adds hidden cases")
    grade.add_argument("--all", action="store_true")
    grade.add_argument("--case", help="one visible case, e.g. V03")
    replay = commands.add_parser("replay", help="write a standalone HTML replay")
    replay.add_argument("case")
    stress = commands.add_parser("stress", help="new feasible, seeded courses")
    stress.add_argument("--count", type=int, default=50)
    stress.add_argument("--seed", type=int, default=1)
    for command in (grade, replay, stress):
        command.add_argument("--policy", default="solution.py")
    args = parser.parse_args(argv)
    visible = load_cases()
    if args.command == "list":
        for case in visible:
            print(f"{case['name']}  {case['description']:<12} "
                  f"{len(case['pipes'])} pipes, need {case['coin_target']} coins")
        return 0
    if args.command == "grade" and args.case and args.all:
        parser.error("choose --case or --all")
    if args.command == "stress" and args.count <= 0:
        parser.error("--count must be positive")
    try:
        policy = load_policy(args.policy)
    except Exception as exc:
        print(f"Cannot load policy: {type(exc).__name__}: {exc}")
        return 2
    if args.command == "replay" or (args.command == "grade" and args.case):
        case = next((c for c in visible if c["name"] == args.case), None)
        if case is None:
            parser.error("unknown visible case; run 'list'")
        cases = [case]
    elif args.command == "stress":
        from _private.courses import STYLES, build
        rng = random.Random(args.seed)
        cases = [build(f"R{i + 1:03d}", rng.randrange(1 << 30), STYLES[1 + i % 6])[0]
                 for i in range(args.count)]
    else:
        cases = list(visible)
        if args.all:
            hidden = load_cases(hidden=True)
            random.Random(1809).shuffle(hidden)
            cases += hidden
    results = []
    for case in cases:
        result, frames = run_case(case, policy, record=args.command == "replay")
        results.append(result)
        mark = "PASS" if result["passed"] else "FAIL"
        if case["name"].startswith("H"):
            print(f"{mark} {case['name']}", flush=True)
        else:
            print(f"{mark} {case['name']}  distance {100 * result['progress']:5.1f}%  "
                  f"coins {result['coins']}/{result['target']}  score {result['score']:5.1f}  "
                  f"{result['reason']}", flush=True)
        if args.command == "replay":
            path = ROOT / "replays" / f"{case['name']}.html"
            write_replay(path, case, result, frames)
            print(f"Replay: {path}")
    passed = sum(r["passed"] for r in results)
    mean = sum(r["score"] for r in results) / len(results)
    peak = max(r["max_ms"] for r in results)
    print(f"\nPassed {passed}/{len(results)} | mean score {mean:.1f}/100 | "
          f"slowest decision {peak:.2f} ms")
    if peak > 40:
        print("Advisory: some decisions exceeded the 40 ms practice budget.")
    return 0 if args.command == "replay" or passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

