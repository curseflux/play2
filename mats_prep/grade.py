#!/usr/bin/env python3
"""Grader.

    python grade.py lander                       # run the reference lander policy
    python grade.py courier                      # run practice/courier_policy.py
    python grade.py courier --policy mine.py     # run a specific file
    python grade.py courier --visible-only       # skip the hidden set
    python grade.py courier --reveal             # show what the hidden cases were
    python grade.py courier --record C3_busy     # also dump a trace for watch.py

Visible cases print their full outcome. Hidden cases print pass/fail and
nothing else, which is roughly what CodeSignal gives you. Every case in a run
shares one Python process and the hidden cases run in a shuffled order, so a
policy that leaks state between episodes will look fine on the visible set and
fall over here.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import random
import sys
from typing import Callable, List, Tuple

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from simlab.core import EpisodeResult, run_episode          # noqa: E402
from simlab.courier import CourierEnv                        # noqa: E402
from simlab.hidden import courier_hidden, lander_hidden      # noqa: E402
from simlab.lander import LanderEnv                          # noqa: E402
from simlab.scenarios import courier_visible, lander_visible # noqa: E402

DEFAULT_POLICY = {
    "lander": "solutions/lander_reference.py",
    "courier": "practice/courier_policy.py",
}
ENV_CLASS = {"lander": LanderEnv, "courier": CourierEnv}


def load_policy(path: pathlib.Path):
    spec = importlib.util.spec_from_file_location("user_policy", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot import {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "policy"):
        raise SystemExit(f"{path} does not define policy(obs)")
    return mod


def banner(title: str) -> None:
    print("\n" + title)
    print("-" * len(title))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("env", choices=sorted(ENV_CLASS))
    ap.add_argument("--policy", default=None)
    ap.add_argument("--visible-only", action="store_true")
    ap.add_argument("--hidden-only", action="store_true")
    ap.add_argument("--reveal", action="store_true")
    ap.add_argument("--record", default=None,
                    help="scenario name to record a trace for (visible cases only)")
    args = ap.parse_args()

    path = pathlib.Path(args.policy or DEFAULT_POLICY[args.env])
    if not path.is_absolute():
        path = HERE / path
    mod = load_policy(path)
    env_cls = ENV_CLASS[args.env]

    visible = lander_visible() if args.env == "lander" else courier_visible()
    hidden = lander_hidden() if args.env == "lander" else courier_hidden()
    random.Random(20260914).shuffle(hidden)

    vis_results: List[EpisodeResult] = []
    if not args.hidden_only:
        banner(f"visible cases  ({path.name})")
        for sc in visible:
            env = env_cls(sc)
            record = (args.record == sc.name)
            r = run_episode(env, mod.policy, record=record, debug_source=mod)
            vis_results.append(r)
            print("  " + r.line())
            if record and r.trace is not None:
                out = HERE / "traces" / f"{args.env}_{sc.name}.json"
                out.parent.mkdir(exist_ok=True)
                out.write_text(json.dumps({"static": env.static(), "frames": r.trace}))
                print(f"        trace -> {out.relative_to(HERE)}")

    hid_results: List[Tuple[str, EpisodeResult]] = []
    if not args.visible_only:
        banner("hidden cases")
        for label, sc in hidden:
            env = env_cls(sc)
            r = run_episode(env, mod.policy, debug_source=mod)
            hid_results.append((label, r))
            if args.reveal:
                print(f"  {'PASS' if r.passed else 'FAIL'}  {label}  "
                      f"[{sc.name}]  {r.reason}")
            else:
                print(f"  {'PASS' if r.passed else 'FAIL'}  {label}")

    banner("summary")
    vp = sum(1 for r in vis_results if r.passed)
    hp = sum(1 for _, r in hid_results if r.passed)
    if vis_results:
        print(f"  visible : {vp}/{len(vis_results)}   "
              f"total score {sum(r.score for r in vis_results):.1f}")
    if hid_results:
        print(f"  hidden  : {hp}/{len(hid_results)}   "
              f"total score {sum(r.score for _, r in hid_results):.1f}")
    total = vp + hp
    denom = len(vis_results) + len(hid_results)
    if denom:
        print(f"  OVERALL : {total}/{denom}  ({100.0 * total / denom:.0f}%)")
    if hid_results and not args.reveal and hp < len(hid_results):
        print("\n  (no, you do not get to see which hidden cases failed or why.\n"
              "   re-read the environment docstring and ask what class of input\n"
              "   your policy has never been shown.)")
    return 0 if total == denom else 1


if __name__ == "__main__":
    raise SystemExit(main())
