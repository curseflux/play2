"""Course authoring and feasibility witnesses. Spoilers: not learner material.

Construct a legal flight first, then fit oscillating shutters around its full
crossing. Replaying the witness through Arena checks the final geometry.
"""
import math
import random

from arena.engine import Arena


FAMILIES = ("wide", "momentum", "moving", "cooldown", "combined")


def build(name, seed, family):
    if family not in FAMILIES:
        raise ValueError(f"unknown family {family}")
    for attempt in range(100):
        result = _attempt(name, seed + 100003 * attempt, family)
        if result is not None:
            return result
    raise RuntimeError(f"could not construct a feasible course: {name}")


def _attempt(name, seed, family):
    rng = random.Random(seed)
    dt = rng.choice((1 / 30, 0.04, 0.05))
    height = rng.uniform(360, 460)
    gravity = rng.uniform(260, 420)
    recharge = rng.randint(3, 5) if family != "cooldown" else rng.randint(7, 9)
    impulse = gravity * dt * recharge * rng.uniform(1.65, 2.2)
    p = {"dt": dt, "gravity": gravity, "drag": rng.uniform(0.15, 0.85),
         "impulse": impulse, "recharge": recharge, "rise_cap": rng.uniform(160, 210),
         "fall_cap": rng.uniform(180, 240), "speed": rng.uniform(95, 150),
         "radius": rng.uniform(7, 10)}
    count = 6 if family == "wide" else 10 if family == "combined" else 8
    times = [rng.randint(45, 62)]
    for _ in range(count - 1):
        times.append(times[-1] + rng.randint(40, 66))
    end = times[-1] + 20
    start = {"y": height * rng.uniform(0.40, 0.60),
             "vy": 0.0 if family == "wide" else rng.uniform(-85, 100),
             "cooldown": 0 if family == "wide" else rng.randrange(recharge)}
    case = {"name": name, "height": height, "physics": p, "start": start,
            "sight": 3, "limit": end + 30,
            "gates": [{"x": 1e8, "half_width": 10, "centre": height / 2,
                       "gap": height - 10, "amplitude": 0, "period": 100, "phase": 0}]}
    env = Arena(case)
    phase = rng.uniform(-math.pi, math.pi)
    flight_period = rng.uniform(140, 240)
    actions, frames = [], [env.snapshot()]
    for tick in range(end):
        target = height * (0.5 + 0.19 * math.sin(2 * math.pi * tick / flight_period + phase)
                           + 0.035 * math.sin(tick / 19))
        action = "pulse" if env.cooldown == 0 and env.y + 0.23 * env.vy > target else "glide"
        actions.append(action)
        env.step(action)
        if env.finished:
            return None
        frames.append(env.snapshot())

    gates = []
    for centre_tick in times:
        x = centre_tick * p["speed"] * dt
        half_width = rng.uniform(10, 22)
        amplitude = 0 if family in ("wide", "momentum") else rng.uniform(12, 35)
        period = rng.uniform(95, 220)
        gate_phase = rng.uniform(-math.pi, math.pi)
        crossing = [f for f in frames if abs(f["x"] - x) <= half_width + p["radius"]]
        adjusted = [f["y"] - amplitude * math.sin(2 * math.pi * f["tick"] / period + gate_phase)
                    for f in crossing]
        margin = {"wide": 26, "momentum": 15, "moving": 12,
                  "cooldown": 14, "combined": 8}[family]
        gap = max(adjusted) - min(adjusted) + 2 * (p["radius"] + margin)
        centre = (max(adjusted) + min(adjusted)) / 2
        if centre - amplitude - gap / 2 < 8 or centre + amplitude + gap / 2 > height - 8:
            return None
        gates.append({"x": x, "half_width": half_width, "centre": centre,
                      "gap": gap, "amplitude": amplitude, "period": period,
                      "phase": gate_phase})
    case["gates"] = gates

    proof = Arena(case)
    for action in actions:
        if proof.finished:
            break
        proof.step(action)
    if not proof.won:
        return None
    return case, actions[:proof.tick]


PUBLIC = (
    ("A01", 1701, "wide", "Warmup"),
    ("A02", 1709, "momentum", "Momentum"),
    ("A03", 1721, "moving", "Moving shutters"),
    ("A04", 1723, "cooldown", "Long recharge"),
    ("A05", 1733, "combined", "Mixed course"),
)

PRIVATE = tuple((f"H{i + 1:02d}", 2003 + i * 37, FAMILIES[i % 5]) for i in range(10))
