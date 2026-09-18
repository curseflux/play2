"""Author-only course construction and successful action witnesses.

The coins are fitted to a verified flight, not guaranteed by a distance-only
reachability estimate. Extra coins may be unsafe or impossible to collect.
"""
import base64
import json
import math
import pathlib
import random
import sys
import zlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from world import World

STYLES = ("warmup", "harvest", "temptation", "approach", "exit", "sparse", "finale")
PUBLIC = tuple((f"V{i + 1:02d}", 901 + i * 19, style) for i, style in enumerate(STYLES))
HIDDEN = tuple((f"H{i + 1:02d}", 1501 + i * 31, STYLES[1 + i % 6]) for i in range(14))


def build(name, seed, style):
    if style not in STYLES:
        raise ValueError(style)
    for attempt in range(100):
        result = _attempt(name, seed + 7919 * attempt, style)
        if result is not None:
            return result
    raise RuntimeError(f"failed to author {name}")


def _attempt(name, seed, style):
    rng = random.Random(seed)
    scale = rng.uniform(0.85, 1.2)
    dt = rng.choice((0.08, 0.10, 0.12))
    ceiling = rng.uniform(65, 90) * scale
    physics = {"dt": dt, "gravity": 30 * scale * (0.1 / dt) ** 2,
               "bounce_velocity": 19 * scale * (0.1 / dt),
               "max_fall_speed": 34 * scale * (0.1 / dt),
               "scroll_speed": rng.uniform(18, 28), "radius": rng.uniform(1.2, 1.8),
               "ceiling": ceiling}
    times = [rng.randint(26, 36)]
    count = 9 if style == "finale" else 6
    for _ in range(count - 1):
        times.append(times[-1] + rng.randint(28, 40))
    end = times[-1] + 26
    dx = physics["scroll_speed"] * dt
    case = {"name": name, "description": style.title(), "physics": physics,
            "y0": ceiling * rng.uniform(0.4, 0.6),
            "vy0": 0 if style == "warmup" else rng.uniform(-5, 5),
            "finish_x": (end - 0.25) * dx, "max_frames": end + 5,
            "pipe_sight": 2, "coin_lookahead": rng.uniform(45, 70),
            "coin_target": 0, "pipes": [], "coins": []}
    env = World(case)
    phase = rng.uniform(-math.pi, math.pi)
    period = rng.uniform(75, 120)
    actions, frames = [], [env.snapshot()]
    for tick in range(end):
        target = ceiling * (0.48 + 0.16 * math.sin(2 * math.pi * tick / period + phase))
        bounce = env.y + 0.2 * env.vy < target
        actions.append(bounce)
        env.step(bounce)
        frames.append(env.snapshot())
        if env.done and env.x < case["finish_x"]:
            return None

    for t in times:
        x, half = t * dx, rng.uniform(2.5, 5)
        crossing = [f["y"] for f in frames if abs(f["x"] - x) <= half + physics["radius"]]
        margin = 9 if style == "warmup" else 4 if style in ("approach", "exit", "finale") else 6
        lo, hi = min(crossing) - physics["radius"] - margin, max(crossing) + physics["radius"] + margin
        if lo < 2 or hi > ceiling - 2:
            return None
        case["pipes"].append({"x": x, "half_width": half, "gap_lo": lo, "gap_hi": hi})

    if style == "approach":
        coin_times = [t - 7 for t in times]
    elif style == "exit":
        coin_times = [t + 7 for t in times]
    elif style == "sparse":
        coin_times = [times[i] - 10 for i in (1, 3, 5)]
        case["coin_lookahead"] = 38
    else:
        coin_times = [t - 11 for t in times] + [times[-1] + 15]
    for t in coin_times:
        case["coins"].append({"x": frames[t]["x"], "y": frames[t]["y"] + rng.uniform(-0.3, 0.3),
                              "radius": 1.15 * scale})
    if style in ("temptation", "finale"):
        # Visible rewards in dangerous locations. The target never requires
        # these extras; some are inside a solid shutter and must be skipped.
        for i, pipe in enumerate(case["pipes"]):
            case["coins"].append({"x": pipe["x"],
                                  "y": pipe["gap_hi"] + 3 if i % 2 else pipe["gap_lo"] - 3,
                                  "radius": scale})
    case["coins"].sort(key=lambda coin: coin["x"])
    needed = math.ceil(len(coin_times) * (0.75 if style in ("harvest", "finale") else 0.6))
    case["coin_target"] = 0 if style == "warmup" else needed
    proof = World(case)
    for action in actions:
        proof.step(action)
        if proof.done:
            break
    if not proof.passed:
        return None
    return case, actions[:proof.frame]


def encode(value):
    return base64.b64encode(zlib.compress(json.dumps(value).encode(), 9)).decode()


def main():
    visible, hidden, witnesses = [], [], {}
    for group, recipes in ((visible, PUBLIC), (hidden, HIDDEN)):
        for name, seed, style in recipes:
            case, actions = build(name, seed, style)
            group.append(case)
            witnesses[name] = actions
    (ROOT / "visible.json").write_text(json.dumps(visible, indent=2) + "\n", encoding="utf-8")
    (ROOT / "_private" / "hidden.dat").write_text(encode(hidden), encoding="ascii")
    (ROOT / "_private" / "witnesses.dat").write_text(encode(witnesses), encoding="ascii")
    print("Built 7 visible + 14 hidden cases, each verified for survival AND its coin target.")


if __name__ == "__main__":
    main()
