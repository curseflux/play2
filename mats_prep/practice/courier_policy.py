"""YOUR WORK GOES HERE.

Read simlab/courier.py first - the docstring at the top is the spec and the
step() method below it is the ground truth. Prose can be ambiguous; the code
cannot.

    python grade.py courier --visible-only      # fast loop while you build
    python watch.py courier C3_busy             # see what it is actually doing
    python grade.py courier                     # visible + hidden
    python tools/stress.py courier --n 200      # scenarios nobody has seen

Contract
--------
    policy(obs) -> one of "idle", "up", "down", "left", "right"
    Called once per frame. Anything else fails the episode immediately.

Stuck, or not sure where to start? practice/LADDER.md breaks this into four
rungs with measured scores, and says which of the obvious ideas is a trap.

Things worth knowing before you start
-------------------------------------
  * Many episodes run in the same process and nothing resets your globals.
    If you keep state between frames you must notice when a new episode has
    started and throw it away.  obs["t"] == 0 is one way. It is not the only
    one - think about what else changes.
  * You must be slow to trade: within pickup_radius AND speed <= grab_speed.
    Flying past at full tilt does nothing at all.
  * Terminal speed under continuous thrust is thrust/drag, and BOTH of those
    are in the observation. Do not hard-code either.
  * Hazards move on straight lines and bounce off the walls. Their velocities
    are in the observation, so where they will be is not a guess.
"""

import math

DEBUG: dict = {}      # see DEBUGGING.md - this is the fastest loop you have


def policy(obs: dict) -> str:
    agent = obs["agent"]
    x, y = agent["x"], agent["y"]
    vx, vy = agent["vx"], agent["vy"]

    # --- 1. choose a target ------------------------------------------------
    # carrying something? it has a dropoff. otherwise pick a parcel worth going
    # for. "nearest pickup" is the obvious answer and is not the best one.
    target = None

    # --- 2. decide the velocity you want at this instant -------------------
    # a direction is not enough - you need a SPEED too, or you will sail past
    # the target too fast to trade.

    # --- 3. stay away from the hazards -------------------------------------

    # --- 4. turn a desired velocity into one of five actions ---------------

    return "idle"


# def policy(obs: dict) -> str:
#     agent = obs["agent"]
#     x, y = agent["x"], agent["y"]
#     vx, vy = agent["vx"], agent["vy"]

#     thrust = obs["thrust"]
#     drag = obs["drag"]
#     v_term = thrust / drag
#     grab_speed = obs["grab_speed"]
#     pickup_radius = obs["pickup_radius"]
#     agent_radius = obs["agent_radius"]

#     DEBUG.clear()
#     DEBUG.update(t=obs["t"], stunned=agent["stunned"], carrying=obs["carrying"])

#     # ---------------------------------------------------------------- target
#     target_loc = None
#     if obs["carrying"] is not None:
#         carrying_id = obs["carrying"]
#         for parcel in obs["parcels"]:
#             if parcel["id"] == carrying_id:
#                 target_loc = parcel["dropoff"]
#                 break
#     else:
#         # Cost is BOTH legs: flying the delivery leg is time too.
#         min_cost = float("inf")
#         for parcel in obs["parcels"]:
#             if parcel["state"] != "waiting":
#                 continue
#             pickup_x, pickup_y = parcel["pickup"]
#             dropoff_x, dropoff_y = parcel["dropoff"]
#             cost = (math.hypot(pickup_x - x, pickup_y - y)
#                     + math.hypot(dropoff_x - pickup_x, dropoff_y - pickup_y))
#             if cost < min_cost:
#                 min_cost = cost
#                 target_loc = parcel["pickup"]

#     if target_loc is None:
#         # Nothing left to fetch (or carrying an id we cannot find). Coast.
#         return "idle"

#     target_x, target_y = target_loc
#     dx = target_x - x
#     dy = target_y - y
#     dist_to_target = math.hypot(dx, dy)

#     # ------------------------------------------------------- desired velocity
#     # Speed we would like to have right now: fast when far, grab-legal on arrival.
#     arrive_speed = ARRIVE_FRAC * grab_speed
#     margin = MARGIN_FRAC * pickup_radius
#     a_brake = BRAKE_FRAC * thrust
#     braking_room = max(0.0, dist_to_target - margin)
#     want_speed = min(v_term, math.sqrt(arrive_speed ** 2 + 2 * a_brake * braking_room))

#     if dist_to_target > 1e-9:
#         want_vx = dx / dist_to_target * want_speed
#         want_vy = dy / dist_to_target * want_speed
#     else:
#         want_vx = want_vy = 0.0

#     # ------------------------------------------------------ hazard avoidance
#     # Not a separate mode: a push blended into the velocity we already want,
#     # so there is nothing to oscillate between.
#     for hazard in obs.get("hazards", []):
#         rel_x = hazard["x"] - x
#         rel_y = hazard["y"] - y
#         rel_vx = hazard["vx"] - vx
#         rel_vy = hazard["vy"] - vy

#         # Time of closest approach, clamped into [0, horizon].
#         den = rel_vx * rel_vx + rel_vy * rel_vy
#         if den < 1e-9:
#             t_cpa = 0.0
#         else:
#             t_cpa = -(rel_x * rel_vx + rel_y * rel_vy) / den
#             t_cpa = max(0.0, min(HAZARD_HORIZON, t_cpa))

#         close_x = rel_x + rel_vx * t_cpa
#         close_y = rel_y + rel_vy * t_cpa
#         close_dist = math.hypot(close_x, close_y)
#         safe_dist = hazard["r"] + agent_radius + HAZARD_MARGIN_FRAC * agent_radius

#         if close_dist < safe_dist:
#             # Push away from where the gap will be tightest, hardest when tightest.
#             if close_dist > 1e-9:
#                 away_x = -close_x / close_dist
#                 away_y = -close_y / close_dist
#             elif math.hypot(rel_x, rel_y) > 1e-9:
#                 d = math.hypot(rel_x, rel_y)
#                 away_x, away_y = -rel_x / d, -rel_y / d
#             else:
#                 away_x, away_y = 1.0, 0.0
#             strength = v_term * (safe_dist - close_dist) / safe_dist
#             want_vx += away_x * strength
#             want_vy += away_y * strength

#     # Re-clamp: the blended vector can exceed anything we can actually hold.
#     want_speed_final = math.hypot(want_vx, want_vy)
#     if want_speed_final > v_term:
#         want_vx *= v_term / want_speed_final
#         want_vy *= v_term / want_speed_final

#     # ------------------------------------------------------------ act on error
#     # One axis per frame, so serve whichever velocity component is further off.
#     err_x = want_vx - vx
#     err_y = want_vy - vy
#     DEBUG.update(dist=dist_to_target, want_speed=want_speed,
#                  speed=math.hypot(vx, vy), err_x=err_x, err_y=err_y)

#     # Deadband: below one frame's worth of thrust, correcting only adds speed.
#     if max(abs(err_x), abs(err_y)) < 0.25 * thrust * obs["dt"]:
#         return "idle"

#     if abs(err_x) >= abs(err_y):
#         return "right" if err_x > 0 else "left"
#     return "up" if err_y > 0 else "down"