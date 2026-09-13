"""
Cargo Lander -- a practice stand-in for the MATS "AI-Assisted Advanced Coding
Assessment".

Shape of the task deliberately mirrors the description in the assessment blurb:

  * a simple physics simulation that unfolds over time
  * you implement ONE function, called ONCE PER FRAME
  * it returns ONE decision (a discrete action)
  * scoring is continuous (0-100), not pass/fail
  * there are VISIBLE scenarios and HIDDEN scenarios

Physics (per frame, semi-implicit Euler):
    ay = -GRAVITY  (+ THRUST_UP   if action == "up"   and fuel > 0)
    ax = wind      (-THRUST_SIDE  if action == "left"  and fuel > 0)
                   (+THRUST_SIDE  if action == "right" and fuel > 0)
    vx, vy = (vx + ax) * DRAG, (vy + ay) * DRAG
    x, y   = x + vx, y + vy

Note the constraint that makes this interesting: ONE action per frame, so you
cannot thrust up and sideways on the same frame. Vertical and lateral control
compete for frames *and* for fuel.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field, replace

ACTIONS = ("none", "up", "left", "right")

# ---------------------------------------------------------------- true physics
GRAVITY = 0.18
THRUST_UP = 0.45
THRUST_SIDE = 0.12
DRAG = 0.995
FUEL_UP = 1.0
FUEL_SIDE = 0.3

PAD_HALF_WIDTH = 8.0
MAX_LANDING_VY = 1.2
MAX_LANDING_VX = 0.8
MAX_FRAMES = 1200
WORLD_HALF_WIDTH = 200.0


@dataclass
class Scenario:
    name: str
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    fuel: float = 100.0
    wind: float = 0.0
    gravity: float = GRAVITY


@dataclass
class State:
    """Exactly what the policy gets to see each frame."""
    x: float
    y: float
    vx: float
    vy: float
    fuel: float
    frame: int
    pad_half_width: float = PAD_HALF_WIDTH
    max_landing_vy: float = MAX_LANDING_VY
    max_landing_vx: float = MAX_LANDING_VX


@dataclass
class Result:
    scenario: str
    score: float
    landed: bool
    frames: int
    fuel_left: float
    touchdown_vy: float
    touchdown_vx: float
    touchdown_x: float
    reason: str
    trajectory: list = field(default_factory=list)


def score_outcome(landed_ok, x, vx, vy, fuel_left, fuel0, frames):
    """0-100. Landing is most of it, but fuel and gentleness are real money."""
    if landed_ok:
        base = 60.0
        fuel_score = 25.0 * max(0.0, fuel_left) / fuel0
        soft = 10.0 * (1.0 - min(1.0, abs(vy) / MAX_LANDING_VY))
        center = 5.0 * (1.0 - min(1.0, abs(x) / PAD_HALF_WIDTH))
        return base + fuel_score + soft + center
    # partial credit for "nearly": close to the pad, and not coming in hot
    prox = math.exp(-abs(x) / 30.0)
    gentle = math.exp(-max(0.0, abs(vy) - MAX_LANDING_VY) / 4.0)
    return 20.0 * prox * gentle


def run(policy, scenario: Scenario, record=False, seed=0) -> Result:
    """Run one episode. `policy` is called once per frame with a State."""
    rng = random.Random(seed)
    x, y, vx, vy, fuel = scenario.x, scenario.y, scenario.vx, scenario.vy, scenario.fuel
    fuel0 = scenario.fuel
    traj = []
    reason = "timeout"
    for frame in range(MAX_FRAMES):
        st = State(x=x, y=y, vx=vx, vy=vy, fuel=fuel, frame=frame)
        if record:
            traj.append((round(x, 2), round(y, 2), round(vx, 3), round(vy, 3), round(fuel, 2)))
        try:
            action = policy(st)
        except Exception as exc:                      # a crash scores ~zero
            return Result(scenario.name, 0.0, False, frame, fuel, vy, vx, x,
                          f"policy raised {type(exc).__name__}: {exc}", traj)
        if action not in ACTIONS:
            action = "none"

        ax = scenario.wind + rng.gauss(0.0, 0.002)    # mild turbulence
        ay = -scenario.gravity
        if fuel > 0:
            if action == "up":
                ay += THRUST_UP
                fuel -= FUEL_UP
            elif action == "left":
                ax -= THRUST_SIDE
                fuel -= FUEL_SIDE
            elif action == "right":
                ax += THRUST_SIDE
                fuel -= FUEL_SIDE
        fuel = max(0.0, fuel)

        vx = (vx + ax) * DRAG
        vy = (vy + ay) * DRAG
        x += vx
        y += vy

        if abs(x) > WORLD_HALF_WIDTH:
            reason = "flew out of bounds"
            break
        if y <= 0.0:
            y = 0.0
            landed_ok = (abs(x) <= PAD_HALF_WIDTH
                         and abs(vy) <= MAX_LANDING_VY
                         and abs(vx) <= MAX_LANDING_VX)
            reason = "landed" if landed_ok else "crashed"
            if record:
                traj.append((round(x, 2), round(y, 2), round(vx, 3), round(vy, 3), round(fuel, 2)))
            return Result(scenario.name,
                          score_outcome(landed_ok, x, vx, vy, fuel, fuel0, frame),
                          landed_ok, frame, fuel, vy, vx, x, reason, traj)
    return Result(scenario.name, score_outcome(False, x, vx, vy, fuel, fuel0, MAX_FRAMES),
                  False, MAX_FRAMES, fuel, vy, vx, x, reason, traj)


# ------------------------------------------------------------------ scenarios
def visible_scenarios():
    """What you can see while you work. Clean, no wind, generous fuel."""
    return [
        Scenario("V1 straight drop",  x=0.0,   y=120.0, fuel=100.0),
        Scenario("V2 offset right",   x=45.0,  y=130.0, fuel=100.0),
        Scenario("V3 offset left",    x=-38.0, y=110.0, fuel=100.0),
    ]


def hidden_scenarios(n=40, seed=7):
    """What you are actually graded on. Wind, drift, tighter fuel, new gravity."""
    rng = random.Random(seed)
    out = []
    for i in range(n):
        out.append(Scenario(
            name=f"H{i:02d}",
            x=rng.uniform(-90, 90),
            y=rng.uniform(80, 170),
            vx=rng.uniform(-1.5, 1.5),
            vy=rng.uniform(-2.0, 0.0),
            fuel=rng.uniform(70, 110),
            wind=rng.uniform(-0.035, 0.035),
            gravity=GRAVITY * rng.uniform(0.88, 1.12),   # physics is NOT exactly what you assumed
        ))
    return out


def validation_scenarios(n=60, seed=999):
    """THE MOST IMPORTANT FUNCTION YOU WILL WRITE.

    The visible scenarios are not what you are graded on. Write your own
    randomised generator, make it WIDER than you think the hidden set is, tune
    against it, and keep the hidden set as a genuinely held-out test.
    """
    rng = random.Random(seed)
    out = []
    for i in range(n):
        out.append(Scenario(
            name=f"T{i:02d}",
            x=rng.uniform(-110, 110),
            y=rng.uniform(60, 190),
            vx=rng.uniform(-2.2, 2.2),
            vy=rng.uniform(-3.0, 0.5),
            fuel=rng.uniform(62, 115),
            wind=rng.uniform(-0.05, 0.05),
            gravity=GRAVITY * rng.uniform(0.82, 1.18),
        ))
    return out


def evaluate(policy, scenarios, seed=0):
    return [run(policy, s, seed=seed + i) for i, s in enumerate(scenarios)]


def summarise(results):
    scores = [r.score for r in results]
    landed = sum(1 for r in results if r.landed)
    return {
        "mean": sum(scores) / len(scores),
        "min": min(scores),
        "landed": landed,
        "n": len(results),
        "land_rate": landed / len(results),
    }
