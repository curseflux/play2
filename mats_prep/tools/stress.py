#!/usr/bin/env python3
"""Randomised scenarios nobody has curated. Run this BEFORE you think you are done.

    python tools/stress.py lander  --n 300
    python tools/stress.py courier --n 150 --policy practice/courier_policy.py

The visible cases tell you whether your policy works. This tells you whether
it works for a reason. A policy that scores well here is one that read the
observation instead of memorising the five examples in front of it.

A perfect score is not the goal - some random worlds are not survivable. Watch
the NUMBER MOVE as you change your policy, and read the failure breakdown.
"""

from __future__ import annotations

import argparse
import collections
import math
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from grade import DEFAULT_POLICY, load_policy                # noqa: E402
from simlab.core import run_episode                          # noqa: E402
from simlab.courier import CourierEnv                        # noqa: E402
from simlab.lander import LanderEnv, LanderScenario          # noqa: E402
from simlab.scenarios import make_courier                    # noqa: E402


def lander_cases(n: int, seed: int):
    r = random.Random(seed)
    for i in range(n):
        g = r.uniform(0.5, 3.0)
        up = g * r.uniform(1.7, 3.6)
        side = r.uniform(0.3, 0.85) * g
        y0, vy0 = r.uniform(20, 220), r.uniform(-13, 9)
        x0, vx0 = r.uniform(-50, 50), r.uniform(-6, 6)
        est = (abs(vy0) + math.sqrt(2 * g * y0)) / ((up - g) * 0.1) + abs(x0) / 2 + 60
        yield LanderScenario(
            name=f"rnd{i:03d}", y0=y0, vy0=vy0, x0=x0, vx0=vx0,
            fuel=int(est * 2.4), g=g, up_thrust=up, side_thrust=side,
            max_touchdown_speed=r.uniform(1.0, 3.0),
            max_lateral_speed=r.uniform(0.4, 1.5),
            pad_half_width=r.uniform(2.5, 9.0),
            wind_base=r.choice([0.0, 0.0, r.uniform(-0.45, 0.45) * side]),
            wind_amp=r.choice([0.0, 0.0, r.uniform(0.0, 0.7) * side]),
            wind_period=r.uniform(40, 300), wind_phase=r.uniform(0, 6.28))


def courier_cases(n: int, seed: int):
    r = random.Random(seed)
    for i in range(n):
        w, h = r.uniform(60, 190), r.uniform(45, 120)
        thrust = r.uniform(5.0, 28.0)
        yield make_courier(
            f"rnd{i:03d}", seed=r.randrange(1 << 30),
            n_parcels=r.randint(6, 18), n_hazards=r.randint(0, 8),
            w=w, h=h, max_frames=r.randint(600, 1600),
            haz_speed=r.uniform(4, 14), haz_r=r.uniform(3, 11),
            thrust=thrust, drag=thrust / r.uniform(6.0, 18.0),
            stun_frames=r.randint(10, 60), target=1,
            cluster=r.random() < 0.3)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("env", choices=["lander", "courier"])
    ap.add_argument("--policy", default=None)
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--show", type=int, default=6, help="print this many failures")
    args = ap.parse_args()

    path = pathlib.Path(args.policy or DEFAULT_POLICY[args.env])
    if not path.is_absolute():
        path = HERE / path
    mod = load_policy(path)

    kinds: collections.Counter = collections.Counter()
    shown = []
    ok = 0
    scores = []
    cases = (lander_cases if args.env == "lander" else courier_cases)(args.n, args.seed)
    env_cls = LanderEnv if args.env == "lander" else CourierEnv

    for sc in cases:
        env = env_cls(sc)
        res = run_episode(env, mod.policy, debug_source=mod)
        scores.append(res.score)
        good = res.passed if args.env == "lander" else res.score > 0
        if good:
            ok += 1
        else:
            r = res.reason
            k = ("policy error" if "raised" in r or "illegal" in r else
                 "timeout" if "timeout" in r else
                 "hit the ground too hard" if "impact" in r else
                 "sideways at touchdown" if "slide" in r else
                 "missed the pad" if "off pad" in r else
                 "left the arena" if "bounds" in r or "escaped" in r else
                 "delivered nothing" if args.env == "courier" else "other")
            kinds[k] += 1
            if len(shown) < args.show:
                shown.append(f"    {sc.name}: {r}")

    n = args.n
    print(f"\n{args.env}: {ok}/{n} ({100.0 * ok / n:.1f}%) survived "
          f"{n} scenarios you have never seen")
    if args.env == "courier":
        srt = sorted(scores)
        print(f"  deliveries  mean {sum(scores)/n:.2f}   median {srt[n//2]:.0f}   "
              f"worst {srt[0]:.0f}   best {srt[-1]:.0f}")
    if kinds:
        print("\n  how it went wrong")
        for k, v in kinds.most_common():
            print(f"    {v:4d}  {k}")
        print("\n  examples")
        print("\n".join(shown))
    if kinds.get("policy error"):
        print("\n  *** a policy that raises or returns a bad action scores zero on"
              "\n      that whole scenario. fix these before anything else. ***")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
