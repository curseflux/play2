#!/usr/bin/env python3
"""CLI: list, test, watch, or stress. Run without arguments for help."""
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

from arena.engine import ACTIONS, Arena
from arena.replay import write_replay


ROOT = pathlib.Path(__file__).resolve().parent


def visible_cases():
    return json.loads((ROOT / "cases" / "visible.json").read_text(encoding="utf-8"))


def hidden_cases():
    data = (ROOT / "_exam" / "hidden.dat").read_text(encoding="ascii")
    return json.loads(zlib.decompress(base64.b64decode(data)))


def load_agent(filename):
    path = pathlib.Path(filename)
    if not path.is_absolute():
        path = ROOT / path
    spec = importlib.util.spec_from_file_location("submitted_agent", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not callable(getattr(module, "decide", None)):
        raise ValueError("submission must define decide(telemetry)")
    return module


def run_case(case, agent, record=False):
    env = Arena(case)
    trace, timings, error = [], [], None
    wall_start = time.perf_counter()
    while not env.finished:
        obs = copy.deepcopy(env.observe())
        start = time.perf_counter()
        try:
            action = agent.decide(obs)
        except Exception as exc:
            timings.append((time.perf_counter() - start) * 1000)
            error = f"agent raised {type(exc).__name__}: {exc}"
            break
        timings.append((time.perf_counter() - start) * 1000)
        if type(action) is not str or action not in ACTIONS:
            error = f"illegal action {action!r}; expected {ACTIONS}"
            break
        if record:
            frame = env.snapshot()
            frame["action"] = action
            debug = getattr(agent, "DEBUG", {})
            # Freeze DEBUG now: nested objects must not change earlier frames.
            frame["debug"] = json.loads(json.dumps(debug, default=repr)) if isinstance(debug, dict) else {}
            trace.append(frame)
        env.step(action)
    result = env.result(error)
    result.update(wall_ms=(time.perf_counter() - wall_start) * 1000,
                  max_decision_ms=max(timings, default=0),
                  mean_decision_ms=sum(timings) / max(1, len(timings)))
    if record:
        final = env.snapshot()
        final.update(action=None, debug={}, reason=result["reason"])
        trace.append(final)
    return result, trace


def result_line(r):
    return (f"{'PASS' if r['passed'] else 'FAIL'} {r['name']:<8} "
            f"{r['cleared']:2}/{r['total']:<2} gates  {r['score']:5.1f}/100  "
            f"{r['frames']:4} frames  {r['reason']}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="show visible case names")
    test = commands.add_parser("test", help="grade visible cases; --all also grades hidden cases")
    test.add_argument("--all", action="store_true")
    test.add_argument("--case", help="run one visible case")
    watch = commands.add_parser("watch", help="write a self-contained HTML replay")
    watch.add_argument("case")
    stress = commands.add_parser("stress", help="new seeded, feasible courses")
    stress.add_argument("--count", type=int, default=50)
    stress.add_argument("--seed", type=int, default=1)
    for command in (test, watch, stress):
        command.add_argument("--agent", default="answer.py", help="policy file, relative to this folder")
    args = parser.parse_args(argv)
    visible = visible_cases()
    if args.command == "list":
        for case in visible:
            print(f"{case['name']}  {case['description']:<20} {len(case['gates'])} gates")
        return 0
    if args.command == "test" and args.case and args.all:
        parser.error("choose --case or --all, not both")
    if args.command == "stress" and args.count <= 0:
        parser.error("--count must be positive")
    try:
        agent = load_agent(args.agent)
    except Exception as exc:
        print(f"Cannot load submission: {type(exc).__name__}: {exc}")
        return 2

    if args.command == "watch" or (args.command == "test" and args.case):
        case = next((c for c in visible if c["name"] == args.case), None)
        if case is None:
            parser.error(f"unknown visible case {args.case!r}; run 'list'")
        cases = [case]
    elif args.command == "stress":
        from _exam.factory import FAMILIES, build
        rng = random.Random(args.seed)
        cases = [build(f"R{i + 1:03d}", rng.randrange(1 << 30), FAMILIES[i % len(FAMILIES)])[0]
                 for i in range(args.count)]
    else:
        cases = list(visible)
        if args.all:
            hidden = hidden_cases()
            random.Random(1709).shuffle(hidden)
            cases += hidden

    results = []
    for case in cases:
        result, trace = run_case(case, agent, record=args.command == "watch")
        results.append(result)
        if case["name"].startswith("H"):
            print(f"{'PASS' if result['passed'] else 'FAIL'} {case['name']}")
        else:
            print(result_line(result))
        if args.command == "watch":
            out = ROOT / "replays" / f"{case['name']}.html"
            write_replay(out, case, result, trace)
            print(f"Replay: {out}")

    passed = sum(r["passed"] for r in results)
    score = sum(r["score"] for r in results) / len(results)
    peak = max(r["max_decision_ms"] for r in results)
    print(f"\nPassed {passed}/{len(results)} | average score {score:.1f}/100 | "
          f"slowest decision {peak:.2f} ms")
    if peak > 40:
        print("Some decisions exceeded the suggested 40 ms practice budget. This is advisory, not a disqualification.")
    return 0 if args.command == "watch" or passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
