"""EchoFlight runner. Commands: list, test, replay, stress."""
import argparse
import base64
import copy
import importlib.util
import json
import pathlib
import random
import time
import zlib

from simulator import World
from replay import write_replay

ROOT = pathlib.Path(__file__).resolve().parent


def courses(hidden=False):
    if hidden:
        return json.loads(zlib.decompress(base64.b64decode(
            (ROOT / "_staff" / "hidden.dat").read_text(encoding="ascii"))))
    return json.loads((ROOT / "visible.json").read_text(encoding="utf-8"))


def load(filename):
    path = pathlib.Path(filename)
    if not path.is_absolute():
        path = ROOT / path
    spec = importlib.util.spec_from_file_location("candidate", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not callable(getattr(module, "act", None)):
        raise ValueError("submission must define act(view)")
    return module


def run(course, module, record=False):
    world, frames, peak, error = World(course), [], 0.0, None
    while not world.done:
        view = copy.deepcopy(world.observe())
        start = time.perf_counter()
        try:
            action = module.act(view)
        except Exception as exc:
            error = f"policy raised {type(exc).__name__}: {exc}"
            peak = max(peak, (time.perf_counter() - start) * 1000)
            break
        peak = max(peak, (time.perf_counter() - start) * 1000)
        if type(action) is not bool:
            error = f"illegal action {action!r}"
            break
        if record:
            frame = world.snapshot()
            debug = getattr(module, "DEBUG", {})
            frame.update(action=action, debug=json.loads(json.dumps(debug, default=repr))
                         if isinstance(debug, dict) else {})
            frames.append(frame)
        world.step(action)
    result = world.result(error)
    result["max_ms"] = peak
    if record:
        frame = world.snapshot()
        frame.update(action=None, debug={}, reason=result["reason"])
        frames.append(frame)
    return result, frames


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list")
    test = commands.add_parser("test")
    test.add_argument("--all", action="store_true")
    test.add_argument("--case")
    replay = commands.add_parser("replay")
    replay.add_argument("case")
    stress = commands.add_parser("stress")
    stress.add_argument("--count", type=int, default=30)
    stress.add_argument("--seed", type=int, default=1)
    for command in (test, replay, stress):
        command.add_argument("--submission", default="policy.py")
    args = parser.parse_args(argv)
    visible = courses()
    if args.command == "list":
        for c in visible:
            print(f"{c['name']} {c['title']:<12} need {c['required']} stars")
        return 0
    if args.command == "test" and args.case and args.all:
        parser.error("choose --case or --all")
    if args.command == "stress" and args.count <= 0:
        parser.error("--count must be positive")
    try:
        module = load(args.submission)
    except Exception as exc:
        print(f"Cannot load submission: {type(exc).__name__}: {exc}")
        return 2
    if args.command == "replay" or (args.command == "test" and args.case):
        selected = [c for c in visible if c["name"] == args.case]
        if not selected:
            parser.error("unknown visible case; run 'list'")
    elif args.command == "stress":
        from _staff.build import STYLES, build
        rng = random.Random(args.seed)
        selected = [build(f"R{i + 1:03d}", rng.randrange(1 << 30), STYLES[1 + i % 5])[0]
                    for i in range(args.count)]
    else:
        selected = list(visible)
        if args.all:
            hidden = courses(True)
            random.Random(1809).shuffle(hidden)
            selected += hidden
    results = []
    for c in selected:
        r, frames = run(c, module, args.command == "replay")
        results.append(r)
        mark = "PASS" if r["passed"] else "FAIL"
        if c["name"].startswith("X"):
            print(f"{mark} {c['name']}", flush=True)
        else:
            print(f"{mark} {c['name']} collected {r['collected']}/{r['required']}  "
                  f"distance {100*r['progress']:.1f}%  score {r['score']:.1f}  {r['reason']}", flush=True)
        if args.command == "replay":
            path = ROOT / "replays" / f"{c['name']}.html"
            write_replay(path, c, r, frames)
            print(f"Replay: {path}")
    passed = sum(r["passed"] for r in results)
    peak = max(r["max_ms"] for r in results)
    print(f"\nPassed {passed}/{len(results)} | mean score "
          f"{sum(r['score'] for r in results)/len(results):.1f}/100 | slowest decision {peak:.2f} ms")
    if peak > 20:
        print("Advisory: some decisions exceeded the 20 ms practice budget.")
    return 0 if args.command == "replay" or passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

