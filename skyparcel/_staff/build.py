"""Author-only course generation and feasibility witnesses."""
import base64
import json
import math
import pathlib
import random
import sys
import zlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from engine import Flight

STYLES = ("warmup", "handoff", "heavy", "temptation", "narrow", "longhaul")
PUBLIC = tuple((f"S{i + 1:02d}", 3601 + 29 * i, s) for i, s in enumerate(STYLES))
PRIVATE = tuple((f"X{i + 1:02d}", 4201 + 37 * i, STYLES[1 + i % 5]) for i in range(12))


def build(name, seed, style):
    if style not in STYLES:
        raise ValueError(style)
    for attempt in range(100):
        result = _attempt(name, seed + 9973 * attempt, style)
        if result is not None:
            return result
    raise RuntimeError(f"no feasible construction for {name}")


def _attempt(name, seed, style):
    rng = random.Random(seed)
    dt = rng.choice((0.08, 0.1, 0.12))
    scale = rng.uniform(0.9, 1.2)
    gravity = 24 * scale * (0.1 / dt) ** 2
    height = rng.uniform(75, 95) * scale
    p = dict(dt=dt, gravity_empty=gravity,
             gravity_loaded=gravity * rng.uniform(1.65, 1.9) if style == "heavy" else gravity * 1.3,
             flap_speed=19 * scale * (0.1 / dt), fall_limit=35 * scale * (0.1 / dt),
             speed=rng.uniform(20, 29), radius=rng.uniform(1.2, 1.8), height=height)
    count = 7 if style == "longhaul" else 4
    pickups = [27 + i * 50 + rng.randint(-3, 3) for i in range(count)]
    depots = [tick + rng.randint(21, 28) for tick in pickups]
    events = {tick: "pickup" for tick in pickups}
    events.update({tick: "depot" for tick in depots})
    end = depots[-1] + 20
    dx = p["speed"] * dt
    course = dict(name=name, title=style.title(), physics=p,
                  start=dict(y=height * rng.uniform(0.4, 0.6), vy=rng.uniform(-3, 3),
                             held=style == "heavy", carrying=False),
                  finish_x=(end - 0.25) * dx, limit=end + 5,
                  required=0 if style == "warmup" else count - 1,
                  gates=[], stations=[])
    env = Flight(course)
    phase = rng.uniform(-math.pi, math.pi)
    period = rng.uniform(90, 140)
    actions, frames = [], [env.snapshot()]
    for tick in range(end):
        target = height * (0.5 + 0.17 * math.sin(2 * math.pi * tick / period + phase))
        action = "press" if not env.held and env.y + 0.2 * env.vy > target else "release"
        actions.append(action)
        env.step(action)
        if env.done and env.x < course["finish_x"]:
            return None
        if env.tick in events:
            env.carrying = events[env.tick] == "pickup"
        frames.append(env.snapshot())

    for tick, kind in sorted(events.items()):
        f = frames[tick]
        half_height = p["radius"] + (3.5 if style == "narrow" else 5.5)
        course["stations"].append(dict(x=f["x"] - dx * 0.01, kind=kind,
                                       top=f["y"] - half_height, bottom=f["y"] + half_height))
    for i, pickup in enumerate(pickups):
        tick = pickup + (5 if style == "handoff" else 12)
        x, half_width = frames[tick]["x"], rng.uniform(3, 5)
        crossing = [f["y"] for f in frames if abs(f["x"] - x) <= half_width + p["radius"]]
        margin = 4 if style == "narrow" else 8 if style == "warmup" else 6
        top, bottom = min(crossing) - p["radius"] - margin, max(crossing) + p["radius"] + margin
        if top < 2 or bottom > height - 2:
            return None
        course["gates"].append(dict(x=x, half_width=half_width, top=top, bottom=bottom))
        if style == "temptation":
            # An optional pickup that cannot be reached through the shutter.
            course["stations"].append(dict(x=x, kind="pickup", top=bottom + 1,
                                           bottom=bottom + 1 + 2 * p["radius"] + 3))
    course["stations"].sort(key=lambda item: item["x"])
    if any(s["top"] < 0 or s["bottom"] > height for s in course["stations"]):
        return None
    proof = Flight(course)
    for action in actions:
        proof.step(action)
        if proof.done:
            break
    if not proof.won or proof.delivered < count:
        return None
    return course, actions[:proof.tick]


def encode(data):
    return base64.b64encode(zlib.compress(json.dumps(data).encode(), 9)).decode()


def main():
    visible, hidden, witnesses = [], [], {}
    for destination, recipes in ((visible, PUBLIC), (hidden, PRIVATE)):
        for name, seed, style in recipes:
            course, actions = build(name, seed, style)
            destination.append(course)
            witnesses[name] = actions
    (ROOT / "visible.json").write_text(json.dumps(visible, indent=2) + "\n", encoding="utf-8")
    (ROOT / "_staff" / "hidden.dat").write_text(encode(hidden), encoding="ascii")
    (ROOT / "_staff" / "witnesses.dat").write_text(encode(witnesses), encoding="ascii")
    print("Built 6 visible + 12 hidden courses with successful delivery witnesses.")


if __name__ == "__main__":
    main()
