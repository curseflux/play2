"""Stage 2 - the velocity reference. The first real idea.

Instead of a fixed speed threshold, compute the fastest speed from which we
could still stop by the time we reach the ground: v = sqrt(2*a*y).
Scores 10/17, 25% on random scenarios. Everything it fails, it fails
sideways - because steering never gets a frame during the brake.
"""
# stage 2: velocity-reference (profile) controller, vertical priority, no coupling
import math

SAFETY = 0.80
DEAD = 0.15

def policy(obs):
    g, T, S = obs["g"], obs["up_thrust"], obs["side_thrust"]
    y, vy, x, vx = obs["y"], obs["vy"], obs["x"], obs["vx"]
    net = T - g
    if net <= 0 or obs["fuel"] <= 0:
        return "off"

    touch = 0.45 * obs["max_touchdown_speed"]
    a_br = SAFETY * net
    v_allow = -math.sqrt(touch * touch + 2.0 * a_br * max(y, 0.0))
    need_up = vy < v_allow
    slack = vy - v_allow

    a_lat = SAFETY * S
    want_vx = -math.copysign(math.sqrt(2.0 * a_lat * abs(x)), x) if x != 0.0 else 0.0
    err = vx - want_vx
    lat = None
    if err > DEAD:
        lat = "left"
    elif err < -DEAD:
        lat = "right"

    if need_up:
        return "up"
    if lat is not None and slack > T * obs["dt"]:
        return lat
    return "off"
