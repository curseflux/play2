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
