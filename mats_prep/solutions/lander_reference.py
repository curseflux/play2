"""Reference policy for the LANDER environment.

The whole design rests on one observation: the lander has TWO jobs (arrive
slowly, arrive on the pad) and ONE engine. Every frame spent steering is a
frame not spent braking. So the policy is organised as:

    1. work out how fast we are allowed to be falling at this altitude
       (a velocity reference, not a PID gain),
    2. work out how long the sideways job will take,
    3. if the sideways job needs more clock than the descent gives it,
       slow the descent down - but only as far as the fuel can pay for,
    4. spend the frame: vertical first (missing it is fatal and
       unrecoverable), steering gets every frame vertical does not need.

Everything tunable is a named constant with a reason next to it. There are no
numbers in the body of the function.
"""

from __future__ import annotations

import math

# --- tunables ---------------------------------------------------------------
# Plan the brake at 80% of the available deceleration. The 20% is what pays
# for the one-frame control lag and for frames stolen by the steering channel.
V_SAFETY = 0.80
# The steering channel only gets the frames the engine is not using to hover,
# and not all of those. Half of the leftover is what we plan against.
LAT_MARGIN = 0.50
# Aim to touch down at 45% of the limit, so a late frame is not a crash.
TOUCH_FRAC = 0.45
# Cruise fast enough to finish the sideways job in ~1/1.8 of the time we have.
CRUISE_K = 1.8
# Stop correcting sideways below 0.6 of one frame's worth of side thrust;
# tighter than this and the engine chatters left-right and wastes fuel.
DEAD_FRAC = 0.60
# Only stretch the descent once the sideways job needs more than 1.3x the
# clock a normal descent would give it. Stretching early wastes fuel.
CRIT = 1.30
STRETCH = 1.20
# Steady wind has to be held against forever, so reserve engine duty for it.
# Capped, because the wind we can see is an instantaneous gust, not the mean.
WD_CAP = 0.35
# Never plan a descent that needs more than this share of the remaining fuel.
FUEL_USE = 0.90

DEBUG: dict = {}


def _t_to_ground(y: float, vy: float, a_brake: float, touch: float, g: float) -> float:
    """Seconds to touchdown if we ride the reference profile down."""
    v = math.sqrt(touch * touch + 2.0 * a_brake * max(y, 0.0))
    # time spent on the profile, plus time free-falling until we meet it
    return (v - touch) / a_brake + max(0.0, (v + vy) / g)


def _t_sideways(x: float, vx: float, a_lat: float) -> float:
    """Seconds for a bang-bang move that ends at x = 0 with vx = 0."""
    if vx * x > 0.0:                       # currently moving away from the pad
        d = abs(x) + vx * vx / (2.0 * a_lat)
        return abs(vx) / a_lat + 2.0 * math.sqrt(d / a_lat)
    d = max(0.0, abs(x) - vx * vx / (2.0 * a_lat))
    return 2.0 * math.sqrt(d / a_lat) + abs(vx) / a_lat


def policy(obs: dict) -> str:
    g, up, side, dt = obs["g"], obs["up_thrust"], obs["side_thrust"], obs["dt"]
    y = max(obs["y"], 0.0)
    vy, x, vx, fuel = obs["vy"], obs["x"], obs["vx"], obs["fuel"]

    net = up - g
    if net <= 0.0 or fuel <= 0:
        return "off"                       # nothing the engine can do for us

    touch = TOUCH_FRAC * obs["max_touchdown_speed"]

    # How much of the engine is left over once hovering is paid for? That
    # leftover is all the steering channel will ever get, so size the sideways
    # plan against it rather than against the raw side thrust.
    share = max(0.05, 1.0 - g / up)
    a_lat = max(1e-6, LAT_MARGIN * share * side)

    # Reserve duty for holding against wind by planning a gentler brake.
    wd = min(WD_CAP, abs(obs.get("wind", 0.0)) / max(side, 1e-9))
    a_brake = V_SAFETY * max(0.08 * net, up * (1.0 - wd) - g)

    t_std = max(_t_to_ground(y, vy, a_brake, touch, g), dt)
    t_lat = _t_sideways(x, vx, a_lat)

    # If the sideways job is on the critical path, descend more slowly - but
    # a slow descent burns fuel just to hover, so cap it by what we can pay for.
    v_cap = float("inf")
    if t_lat > CRIT * t_std:
        frames = t_lat / dt
        need = frames * (g / up) + frames * share       # hover cost + steering cost
        afford = min(1.0, FUEL_USE * fuel / max(need, 1e-9))
        t_want = max(t_std, STRETCH * t_lat * afford)
        v_cap = max(0.05, y / max(t_want, dt))

    v_allow = -min(math.sqrt(touch * touch + 2.0 * a_brake * y), v_cap)

    # Sideways velocity setpoint. sqrt(2*a*d) is the minimum-TIME approach and
    # it is the most expensive one; cap it at the cruise speed that actually
    # finishes the job in the time we have.
    t_use = max(min(t_std, t_lat) if t_lat > 0.0 else t_std, dt)
    v_arrive = math.sqrt(2.0 * a_lat * abs(x))
    want_vx = -math.copysign(min(v_arrive, CRUISE_K * abs(x) / t_use), x) if x else 0.0
    err = vx - want_vx
    dead = DEAD_FRAC * side * dt
    steer = "left" if err > dead else "right" if err < -dead else None

    DEBUG.update(v_allow=v_allow, vy=vy, slack=vy - v_allow, want_vx=want_vx,
                 err=err, t_std=t_std, t_lat=t_lat, a_brake=a_brake,
                 capped=v_cap < 1e8)

    # Vertical is a hard constraint - a frame missed here cannot be bought back
    # later. Steering gets everything vertical does not need.
    if vy < v_allow:
        return "up"
    if steer is not None:
        return steer
    return "off"
