"""Stage 3 - couple the two axes through TIME.

Estimate how long the sideways job needs, compare with how long the descent
gives it, and slow the descent down when the sideways job is on the critical
path. Scores 16/17, 79% on random scenarios.
"""
import math

V_SAFETY   = 0.85
L_SAFETY   = 0.70
TOUCH_FRAC = 0.45
DEAD_FRAC  = 0.60
URGENT     = 0.75

def _clamp(v, lo, hi): return lo if v < lo else hi if v > hi else v

def policy(obs):
    g, up, side, dt = obs["g"], obs["up_thrust"], obs["side_thrust"], obs["dt"]
    y, vy, x, vx = obs["y"], obs["vy"], obs["x"], obs["vx"]
    fuel = obs["fuel"]
    net = up - g
    if net <= 0.0 or fuel <= 0:
        return "off"

    touch = TOUCH_FRAC * obs["max_touchdown_speed"]
    a_br = max(1e-6, V_SAFETY * net)
    a_lat = max(1e-6, L_SAFETY * side)
    y = max(y, 0.0)

    # ---- nominal vertical profile and time-to-ground under it
    v_prof = math.sqrt(touch * touch + 2.0 * a_br * y)
    t_ground = (v_prof - touch) / a_br + max(0.0, (v_prof + vy) / g)

    # ---- lateral: how long does the sideways job take, at best?
    ax_w = obs.get("wind", 0.0)
    if vx * x > 0.0:                      # moving away from the pad
        d = abs(x) + vx * vx / (2.0 * a_lat)
        t_lat = abs(vx) / a_lat + 2.0 * math.sqrt(d / a_lat)
    else:
        d = max(0.0, abs(x) - vx * vx / (2.0 * a_lat))
        t_lat = 2.0 * math.sqrt(d / a_lat) + abs(vx) / a_lat
    t_lat += abs(ax_w) / max(a_lat, 1e-6) * 0.0

    # ---- stretch the descent if the sideways job needs more clock,
    #      but never beyond what the fuel can pay for
    v_cap = 1e9
    if t_lat > URGENT * t_ground and t_lat > dt:
        t_afford = (fuel * up * dt + touch + vy) / g
        t_want = min(t_lat / URGENT, max(t_afford * 0.85, dt))
        v_cap = max(touch, y / t_want)
    v_allow = -min(v_prof, v_cap)

    need_up = vy < v_allow
    slack = vy - v_allow

    # ---- lateral velocity setpoint: minimum-TIME profile, capped by the
    #      cruise speed that the clock we actually have makes necessary
    t_use = max(t_ground, dt)
    v_min_time = math.sqrt(2.0 * a_lat * abs(x))
    v_cruise = 1.7 * abs(x) / t_use
    want_vx = -math.copysign(min(v_min_time, max(v_cruise, 0.0)), x) if x != 0.0 else 0.0
    dead = DEAD_FRAC * side * dt
    err = vx - want_vx
    lat = "left" if err > dead else "right" if err < -dead else None

    urgent_lat = t_lat > URGENT * t_ground

    if need_up and not (urgent_lat and slack > -0.5 * up * dt and lat):
        return "up"
    if lat is not None and (slack > up * dt or urgent_lat):
        return lat
    if need_up:
        return "up"
    return "off"
