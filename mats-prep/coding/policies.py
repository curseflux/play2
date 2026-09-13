"""
Policies for Cargo Lander, in the order you should actually write them during a
60-minute assessment. Every one is a PURE FUNCTION of the current frame's state
-- no memory, nothing cached between frames (except dp_openloop, which is the
cautionary tale and needs memory by construction).

    v0_baseline     ~08 min in.  Gets the loop running, banks partial credit.
    v1_pd           ~18 min in.  Closed loop. Lands the easy case, wastes fuel.
    v2_braking      ~32 min in.  Kinematic braking curves. Aces VISIBLE, fails HIDDEN.
    v2b_gated       ~45 min in.  Adds the readiness floor. The actual answer.
    v3_mpc          ~55 min in.  Short-horizon re-planned search on top of v2b.

    dp_openloop     The trap: a plan that is optimal for the world you ASSUMED.
    dp_closedloop   The same DP table, re-queried every frame. Night and day.
"""
from __future__ import annotations

import math
from functools import lru_cache

from lander import (ACTIONS, DRAG, GRAVITY, MAX_LANDING_VX, MAX_LANDING_VY,
                    PAD_HALF_WIDTH, THRUST_SIDE, THRUST_UP, State,
                    score_outcome)

A_UP = THRUST_UP - GRAVITY          # net upward accel while thrusting: 0.27


# --------------------------------------------------------------- v0: baseline
def v0_baseline(s: State) -> str:
    """Dumbest thing that is not nothing: hover down, nudge toward the pad."""
    if s.vy < -0.8:
        return "up"
    if s.x > 2.0:
        return "left"
    if s.x < -2.0:
        return "right"
    return "none"


# --------------------------------------------------------------------- v1: PD
def v1_pd(s: State) -> str:
    """Proportional-derivative on both axes, vertical wins ties."""
    target_vy = -0.9 - 0.03 * s.y
    if s.vy < target_vy:
        return "up"
    lateral = s.x + 6.0 * s.vx
    if lateral > 1.5:
        return "left"
    if lateral < -1.5:
        return "right"
    return "none"


# --------------------------------------------- shared kinematics for v2 and up
def _brake_vy(distance: float, duty: float, floor_speed: float = 0.55) -> float:
    """Fastest descent from which we can still stop within `distance`.

    From v^2 = 2*a*d. `duty` < 1 reserves frames for lateral thrust AND pads
    against gravity being stronger than we assumed.
    """
    a = max(0.02, A_UP * duty)
    return -(math.sqrt(2.0 * a * max(0.0, distance)) + floor_speed)


def _brake_vx(x: float, duty: float, cap: float = 2.2) -> float:
    a = max(0.01, THRUST_SIDE * duty)
    mag = min(cap, math.sqrt(2.0 * a * abs(x)))
    return -math.copysign(mag, x)


def _lateral_action(s: State, duty: float, tol: float = 1.0) -> str:
    want_vx = _brake_vx(s.x, duty)
    if abs(s.x) > tol or abs(s.vx) > 0.15:
        if s.vx > want_vx + 0.08:
            return "left"
        if s.vx < want_vx - 0.08:
            return "right"
    return "none"


# -------------------------------------------- v2: braking curves, no coupling
def make_v2(vduty=0.55, hduty=0.45, handover=18.0):
    def v2_braking(s: State) -> str:
        if s.vy < _brake_vy(s.y - 1.5, vduty):
            return "up"
        if s.y < handover and abs(s.x) <= PAD_HALF_WIDTH * 0.6 \
                and abs(s.vx) <= MAX_LANDING_VX * 0.5:
            return "none"
        return _lateral_action(s, hduty)
    return v2_braking


v2_braking = make_v2()


# ------------------------- v2b: the same thing, plus a LATERAL READINESS FLOOR
# The bug in v2 is that altitude is a non-renewable resource and the lateral
# subproblem needs frames to finish. Once you are low, vertical control wins
# every tie, so leftover vx can never be paid off -- you land on the pad,
# sideways, and crash. Fix: refuse to descend below an altitude that scales with
# how much lateral work is still outstanding. Brake to a stop at that FLOOR
# rather than at the ground; the floor falls as the lateral error shrinks, so in
# practice you glide down continuously instead of hovering.
def make_v2b(vduty=0.55, hduty=0.50, k_x=0.42, k_vx=26.0, floor_base=7.0,
             commit_alt=11.0, margin=0.15):
    """`margin` biases the thrust switch to the SAFE side of the braking curve.

    Without it the controller rides exactly on the feasibility boundary; one
    coasted frame puts it outside, and because real gravity is up to 12% stronger
    than assumed it can never claw back. Observed symptom: touchdown at
    vy = -1.22 against a limit of -1.20, i.e. a 70-point loss to buy 1 unit of
    fuel worth 0.25 points. The constraint is a cliff; the score is a slope. Pay
    the slope to stay off the cliff.
    """
    def lateral_floor(s: State) -> float:
        slack_x = max(0.0, abs(s.x) - PAD_HALF_WIDTH * 0.35)
        slack_vx = max(0.0, abs(s.vx) - MAX_LANDING_VX * 0.35)
        if slack_x <= 0.0 and slack_vx <= 0.0:
            return 0.0
        return floor_base + k_x * slack_x + k_vx * slack_vx

    def v2b_gated(s: State) -> str:
        floor = lateral_floor(s)

        # Final commit: lateral is clean, so the only job is a soft touchdown.
        if s.y < commit_alt and floor == 0.0:
            want = _brake_vy(s.y - 1.0, vduty * 1.25, 0.45)
            return "up" if s.vy < want + margin else "none"

        if floor > 0.0 and s.y <= floor + 1.5:
            # Hold altitude; spend the spare frames fixing lateral.
            if s.vy < -0.06:
                return "up"
            return _lateral_action(s, hduty, tol=0.8)

        distance = s.y - 1.5 if floor == 0.0 else s.y - floor
        if s.vy < _brake_vy(distance, vduty) + margin:
            return "up"
        return _lateral_action(s, hduty, tol=0.8)

    return v2b_gated


v2b_gated = make_v2b()


# ------------------------------------------------ v3: short-horizon MPC on top
# A first attempt at this shaped the rollout cost by hand and included a term
# rewarding lost altitude. It PROCRASTINATED: every frame it reasoned "falling is
# progress, and the fallback controller will save me in a moment", then overrode
# the fallback's thrust on the next frame too, and rode a free fall into the
# ground. The cure is to stop shaping. Roll each candidate action out to
# TERMINATION under the fallback policy and score it with the REAL scoring
# function. No proxy, nothing to mis-weight.
def _simulate_to_end(x, y, vx, vy, fuel, fuel0, first_action, base,
                     commit, gravity, cap=400):
    for k in range(cap):
        a = first_action if k < commit else base(
            State(x=x, y=y, vx=vx, vy=vy, fuel=fuel, frame=k))
        ax, ay = 0.0, -gravity
        if fuel > 0:
            if a == "up":
                ay += THRUST_UP; fuel -= 1.0
            elif a == "left":
                ax -= THRUST_SIDE; fuel -= 0.3
            elif a == "right":
                ax += THRUST_SIDE; fuel -= 0.3
        fuel = max(0.0, fuel)
        vx = (vx + ax) * DRAG
        vy = (vy + ay) * DRAG
        x += vx
        y += vy
        if y <= 0.0:
            ok = (abs(x) <= PAD_HALF_WIDTH and abs(vy) <= MAX_LANDING_VY
                  and abs(vx) <= MAX_LANDING_VX)
            return score_outcome(ok, x, vx, vy, fuel, fuel0, k)
    return score_outcome(False, x, vx, vy, fuel, fuel0, cap)


def make_v3(commit=3, base=None, margin=0.35):
    """Re-plan every frame. Only deviate from `base` when clearly better, so a
    rollout-model error cannot talk us out of a thrust the fallback wanted."""
    base = base or make_v2b()

    def v3_mpc(s: State) -> str:
        fuel0 = max(s.fuel, 1.0)
        fallback = base(s)
        best, best_score = fallback, _simulate_to_end(
            s.x, s.y, s.vx, s.vy, s.fuel, fuel0, fallback, base, commit, GRAVITY)
        for a in ACTIONS:
            if a == fallback:
                continue
            sc = _simulate_to_end(s.x, s.y, s.vx, s.vy, s.fuel, fuel0,
                                  a, base, commit, GRAVITY)
            if sc > best_score + margin:
                best, best_score = a, sc
        return best

    return v3_mpc


v3_mpc = make_v3()


# --------------------------------------------------------------- the DP family
# Minimise up-thrust frames subject to touching down softly, over a grid of
# (altitude, vertical speed). Solved ONCE, against ASSUMED gravity. Lateral
# control is the SAME module v2b uses, so the only difference between the two DP
# policies below is open-loop replay vs. re-querying the table each frame.
#
# TWO GRID TRAPS THAT COST REAL TIME, both hit while writing this file:
#
#  1. SELF-TRANSITIONS. One frame at low speed moves the craft ~0.18 units. With
#     an altitude cell of 3.0 units, next_cell == current_cell, so a single
#     backward sweep ordered by altitude has no valid topological order. A sweep
#     that forbids same-cell transitions silently concludes "every state is
#     infeasible", which shows up as a policy that never fires the thruster.
#
#  2. AN UNREACHABLE GOAL. Soft touchdown requires |vy| <= 1.2, i.e. descending
#     at most ~1 unit per frame. If the bottom altitude cell is 2 units tall, you
#     physically cannot cross it in one frame while staying under the speed
#     limit, so the terminal state is unreachable from anywhere and the table is
#     again all-infeasible.
#
# Both are fixed below by (a) solving the shortest-path problem exactly with
# Dijkstra instead of a sweep, and (b) using cells small relative to one frame of
# motion. The moral is not "DP is wrong" -- it is that discretising a continuous
# system is where the difficulty actually lives.
DP_DY, DP_DVY = 0.5, 0.2
DP_Y = [i * DP_DY for i in range(0, 561)]            # 0 .. 280
DP_VY = [-16.0 + i * DP_DVY for i in range(0, 121)]  # -16 .. +8
ASSUMED_GRAVITY = GRAVITY                            # the "textbook" value
INF = float("inf")


def _snap(val, grid):
    val = min(grid[-1], max(grid[0], val))
    step = grid[1] - grid[0]
    return int(round((val - grid[0]) / step))


@lru_cache(maxsize=1)
def _dp_table():
    """(iy, ivy) -> best vertical action. Exact Dijkstra over the discretised grid."""
    import heapq

    nY, nVY = len(DP_Y), len(DP_VY)
    trans = {}          # state -> [(action, fuel, next_state_or_None, terminal_cost)]
    rev = {}            # next_state -> [(state, action, fuel)]
    for iy in range(nY):
        y = DP_Y[iy]
        for ivy in range(nVY):
            vy = DP_VY[ivy]
            row = []
            for a in ("none", "up"):
                ay = -ASSUMED_GRAVITY + (THRUST_UP if a == "up" else 0.0)
                nvy = (vy + ay) * DRAG
                nyv = y + nvy
                fuel = 1.0 if a == "up" else 0.0
                if nyv <= 0.0:
                    ok = abs(nvy) <= MAX_LANDING_VY * 0.85
                    row.append((a, fuel, None, 0.0 if ok else INF))
                else:
                    nxt = (_snap(nyv, DP_Y), _snap(nvy, DP_VY))
                    row.append((a, fuel, nxt, 0.0))
                    rev.setdefault(nxt, []).append(((iy, ivy), a, fuel))
            trans[(iy, ivy)] = row

    dist = {k: INF for k in trans}
    act = {k: "up" for k in trans}          # safe default for unreachable states
    heap = []
    for k, row in trans.items():            # seed: states that can land directly
        for a, fuel, nxt, term in row:
            if nxt is None and term == 0.0 and fuel < dist[k]:
                dist[k], act[k] = fuel, a
    for k, d in dist.items():
        if d < INF:
            heapq.heappush(heap, (d, k))

    seen = set()
    while heap:
        d, k = heapq.heappop(heap)
        if k in seen:
            continue
        seen.add(k)
        for pred, a, fuel in rev.get(k, ()):
            nd = d + fuel
            if nd < dist[pred]:
                dist[pred], act[pred] = nd, a
                heapq.heappush(heap, (nd, pred))
    return act


def _dp_vertical(y, vy):
    return _dp_table().get((_snap(y, DP_Y), _snap(vy, DP_VY)), "up")


_PLAN: dict = {}


def dp_openloop(s: State) -> str:
    """Compute the whole action sequence on frame 0, then just replay it.

    This is the shape of 'I applied dynamic programming and it should be
    correct'. It IS correct -- for the world it was planned against.
    """
    if s.frame == 0:
        y, vy, seq = s.y, s.vy, []
        for _ in range(900):
            a = _dp_vertical(y, vy)
            seq.append(a)
            vy = (vy + (-ASSUMED_GRAVITY + (THRUST_UP if a == "up" else 0.0))) * DRAG
            y += vy
            if y <= 0.0:
                break
        n = int(math.sqrt(abs(s.x) / THRUST_SIDE))
        toward = "left" if s.x > 0 else "right"
        away = "right" if s.x > 0 else "left"
        _PLAN["v"] = seq
        _PLAN["h"] = [toward] * n + [away] * n

    v, h = _PLAN.get("v", []), _PLAN.get("h", [])
    if s.frame < len(v) and v[s.frame] == "up":
        return "up"
    if s.frame < len(h):
        return h[s.frame]
    return "none"


def dp_closedloop(s: State) -> str:
    """The identical DP table, looked up fresh from the CURRENT state each frame,
    with v2b's readiness floor layered on top."""
    base = make_v2b()
    floor = 0.0
    slack_x = max(0.0, abs(s.x) - PAD_HALF_WIDTH * 0.35)
    slack_vx = max(0.0, abs(s.vx) - MAX_LANDING_VX * 0.35)
    if slack_x > 0.0 or slack_vx > 0.0:
        floor = 7.0 + 0.42 * slack_x + 26.0 * slack_vx

    if floor > 0.0:
        if s.y <= floor + 1.5:
            return "up" if s.vy < -0.06 else _lateral_action(s, 0.50, tol=0.8)
        # plan the vertical profile as if the FLOOR were the ground
        if _dp_vertical(s.y - floor, s.vy) == "up":
            return "up"
        return _lateral_action(s, 0.50, tol=0.8)

    if _dp_vertical(s.y, s.vy) == "up":
        return "up"
    return _lateral_action(s, 0.50, tol=0.8)


ALL = {
    "v0_baseline": v0_baseline,
    "v1_pd": v1_pd,
    "v2_braking": v2_braking,
    "v2b_gated": v2b_gated,
    "v3_mpc": v3_mpc,
    "dp_openloop": dp_openloop,
    "dp_closedloop": dp_closedloop,
}


# ------------------------------ v4: measure the physics instead of assuming it
# Every controller above hard-codes GRAVITY and ignores wind. The hidden set
# varies gravity by +-12% and adds a sideways wind worth up to 40% of the side
# thruster, so the braking curves are wrong by exactly the margin you cannot
# afford. But the velocity is handed to you every frame and you know what you
# commanded last frame, so ONE SUBTRACTION gives the acceleration you actually
# received -- hence gravity and wind. Do not assume the dynamics. Measure them.
#
# A DISCARDED IDEA, KEPT HERE AS A WARNING. I first tried replacing the hover
# gate with "spend altitude as time": estimate how many frames the lateral
# problem needs, then descend slowly enough that both axes finish together.
# Elegant, and worse -- 63.4 against v2b's 73.5 on the same validation set, all
# thirteen failures touching down softly but off-pad with empty tanks. The
# premise was false. Free fall is free; any CONSTANT descent rate below free fall
# needs continuous thrust at the same ~42% duty as hovering. There is no cheap
# time in the air. Total fuel is roughly (frames aloft) x 0.42 plus lateral
# thrust, so the right objective is to MINIMISE time aloft subject to finishing
# the lateral manoeuvre -- which is what v2b's gate already does. Kept the
# measurement, threw away the theory.
def make_v4(vduty=0.55, hduty=0.50, k_x=0.42, k_vx=26.0, floor_base=7.0,
            commit_alt=11.0, margin=0.15, alpha_fast=0.35, alpha_slow=0.10,
            fuel_safety=1.30, vx_cap=2.2):
    mem: dict = {}

    def observe(s: State):
        if not mem or s.frame != mem.get("frame", -99) + 1:
            mem.clear()
            mem.update(frame=s.frame, vx=s.vx, vy=s.vy, act="none",
                       g=GRAVITY, w=0.0, n=0, fuel_was=s.fuel)
            return
        thrust_ax = thrust_ay = 0.0
        if mem["fuel_was"] > 0.0:
            a = mem["act"]
            thrust_ax = -THRUST_SIDE if a == "left" else THRUST_SIDE if a == "right" else 0.0
            thrust_ay = THRUST_UP if a == "up" else 0.0
        ax = s.vx / DRAG - mem["vx"]
        ay = s.vy / DRAG - mem["vy"]
        alpha = alpha_fast if mem["n"] < 12 else alpha_slow
        mem["w"] += alpha * ((ax - thrust_ax) - mem["w"])
        mem["g"] += alpha * ((thrust_ay - ay) - mem["g"])
        mem["g"] = min(max(mem["g"], 0.05), 0.60)
        mem["w"] = min(max(mem["w"], -0.105), 0.105)
        mem["n"] += 1

    def v4_adaptive(s: State) -> str:
        observe(s)
        g, w = mem["g"], mem["w"]
        a_up = max(0.03, THRUST_UP - g)               # measured, not assumed
        a_lat = max(0.02, THRUST_SIDE - abs(w))       # wind eats side authority

        def brake_vy(d, duty, floor_speed=0.55):
            return -(math.sqrt(2.0 * max(0.0, d) * max(0.02, a_up * duty)) + floor_speed)

        slack_x = max(0.0, abs(s.x) - PAD_HALF_WIDTH * 0.35)
        slack_vx = max(0.0, abs(s.vx) - MAX_LANDING_VX * 0.35)
        floor = 0.0 if (slack_x <= 0.0 and slack_vx <= 0.0) \
            else floor_base + k_x * slack_x + k_vx * slack_vx

        # Bankruptcy alarm: a soft touchdown off-pad still scores ~12, a
        # high-speed crash scores ~0. If we cannot afford both, buy the landing.
        v_est = math.sqrt(max(0.0, 2.0 * g * s.y / (1.0 + g / a_up)))
        if s.fuel < fuel_safety * (v_est + max(0.0, -s.vy) * 0.3) / a_up:
            floor = 0.0

        def lateral() -> str:
            mag = min(vx_cap, math.sqrt(2.0 * a_lat * abs(s.x)))
            want = -math.copysign(mag, s.x) if abs(s.x) > 0.6 else 0.0
            if abs(s.x) > 0.8 or abs(s.vx) > 0.12:
                if s.vx > want + 0.06:
                    return "left"
                if s.vx < want - 0.06:
                    return "right"
            return "none"

        if s.y < commit_alt and floor == 0.0:
            action = "up" if s.vy < brake_vy(s.y - 1.0, vduty * 1.25, 0.42) + margin else "none"
        elif floor > 0.0 and s.y <= floor + 1.5:
            action = "up" if s.vy < -0.06 else lateral()
        else:
            d = s.y - 1.5 if floor == 0.0 else s.y - floor
            action = "up" if s.vy < brake_vy(d, vduty) + margin else lateral()

        mem["vx"], mem["vy"], mem["act"] = s.vx, s.vy, action
        mem["fuel_was"], mem["frame"] = s.fuel, s.frame
        return action

    return v4_adaptive


v4_adaptive = make_v4()

ALL["v2b_gated"] = make_v2b(margin=0.15, vduty=0.45)
ALL["v3_mpc"] = make_v3(base=make_v2b(margin=0.15, vduty=0.45))
ALL["v4_adaptive"] = v4_adaptive


# ----------------------------------------------------------------- final answer
# Tuned by random search on a self-made 120-scenario validation set (tune.py),
# taking the centroid of the top 25 configs rather than the single argmax.
#
# Notable negative result: v4's online estimation of gravity and wind scored
# slightly WORSE than this after both were tuned (72.6 vs 74.2). The measurement
# is correct and does raise the landing rate, but a tuned safety margin already
# absorbs a bounded +-12% gravity error far more cheaply than an estimator that
# needs a dozen frames to converge. Sophistication is not free. Measure before
# you keep it.
FINAL_KW = dict(vduty=0.462, hduty=0.406, k_x=0.415, k_vx=28.5,
                floor_base=6.68, commit_alt=10.6, margin=0.173)
final_policy = make_v2b(**FINAL_KW)

ALL["final_policy"] = final_policy
