"""Hard dog courses, constructed around feasible trajectories.

This is course-authoring code, not a policy. The construction witness never
enters an observation. Replay it with tools/validate_dog.py to independently
check the finished obstacles against DogEnv's actual collision rules.
"""
from __future__ import annotations

import random
from dataclasses import replace

from .dog import DogEnv, DogScenario, Pipe


KINDS = ("apex", "climb", "descent", "slalom", "tunnel", "endurance",
         "rising_start", "falling_start")


def build_challenge(name: str, seed: int, kind: str) -> tuple[DogScenario, frozenset[int]]:
    """Return a scenario and a known legal set of bounce decision frames.

    Place each gap around the entire swept crossing, including the dog's
    radius and the trailing edge. This permits openings smaller than a full
    bounce without accidentally generating an impossible course.
    """
    if kind not in KINDS:
        raise ValueError(f"unknown dog challenge: {kind}")
    rng = random.Random(seed)
    scale = rng.uniform(0.8, 1.35)
    dt = rng.choice((0.08, 0.10, 0.12))
    radius = rng.uniform(1.1, 1.8)
    delay = rng.randint(2, 5)
    y0 = rng.uniform(24, 32) * scale
    vy0 = 0.0
    stamina, regen = 3, 12
    width = 1.20                 # half crossing duration in frames
    margin = 0.16 * scale       # positive clearance, not an exact-boundary trick

    if kind == "climb":
        delay = 0
        intervals = [6, 6, 6, 6, 12, 12, 12, 12]
    elif kind == "descent":
        y0 += 45 * scale
        intervals = [12, 18, 18, 6, 6, 12, 12]
    elif kind == "slalom":
        y0 += 25 * scale
        intervals = [6, 6, 18, 6, 6, 18, 6, 6, 12]
        stamina, regen = 4, 10
    elif kind == "endurance":
        intervals = [12] * 27
        stamina, regen = 1, 12
    else:
        intervals = [rng.choice((11, 12, 13)) for _ in range(7)]
        if kind == "tunnel":
            width = 3.15
        elif kind == "rising_start":
            vy0 = 13 * scale * (0.1 / dt)
            delay = 10
        elif kind == "falling_start":
            vy0 = -18 * scale * (0.1 / dt)
            delay = 2

    burns = [delay]
    for interval in intervals:
        burns.append(burns[-1] + interval)
    witness = frozenset(burns)
    end = burns[-1] + 12
    sc = DogScenario(
        name=name, y0=y0, vy0=vy0, ceiling=10000,
        gravity=30 * scale * (0.1 / dt) ** 2,
        bounce_impulse=19 * scale * (0.1 / dt),
        max_fall_speed=40 * scale * (0.1 / dt),
        forward_speed=rng.uniform(22, 38), dt=dt, dog_radius=radius,
        stamina_max=stamina, regen_period=regen, sight=4,
        max_frames=end + 1,
        # A distant sentinel keeps the engine running while we author the path.
        pipes=[Pipe(1e6, 1, radius, 9999)],
    )
    env = DogEnv(sc)
    frames = [env.snapshot()]
    for t in range(end):
        if t in witness and env.stamina <= 0:
            raise ValueError(f"{kind}/{seed}: construction exhausted stamina at {t}")
        env.step(t in witness)
        if env.done:
            raise ValueError(f"{kind}/{seed}: construction hit a boundary")
        frames.append(env.snapshot())

    pipes = []
    dx = sc.forward_speed * sc.dt
    for i, burn in enumerate(burns):
        # During the climb, keep the next high gate visible from the low gate,
        # but leave the intermediate ascent unobstructed.
        if kind == "climb" and i in (1, 2, 3):
            continue
        centre = burn + 6 + rng.uniform(-0.12, 0.12)
        half_w = max(0.25, width * dx - radius)
        px = centre * dx
        crossing = [f["y"] for f in frames
                    if f["x"] + radius > px - half_w
                    and f["x"] - radius < px + half_w]
        if not crossing:
            raise ValueError("pipe skipped between frames")
        pipes.append(Pipe(px, half_w, min(crossing) - radius - margin,
                          max(crossing) + radius + margin))

    ceiling = max(f["y"] for f in frames) + radius + (
        0.35 * scale if kind == "tunnel" else 7 * scale)
    return replace(sc, pipes=pipes, ceiling=ceiling, target=len(pipes)), witness


def make_dog_challenge(name: str, seed: int, kind: str) -> DogScenario:
    return build_challenge(name, seed, kind)[0]


VISIBLE_CHALLENGES = (
    ("D2_apex", 301, "apex"),
    ("D3_stamina_climb", 307, "climb"),
    ("D4_early_descent", 311, "descent"),
    ("D5_slalom", 313, "slalom"),
    ("D6_long_tunnel", 317, "tunnel"),
    ("D7_endurance", 331, "endurance"),
    ("D8_rising_start", 337, "rising_start"),
    ("D9_falling_start", 347, "falling_start"),
)
