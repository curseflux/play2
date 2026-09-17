"""YOUR WORK GOES HERE.

Read simlab/dog.py first. The docstring is the spec; the step() method below
it is the ground truth.

    python3 grade.py dog --visible-only        # fast loop while you build
    python3 watch.py dog D2_apex               # see what it is actually doing
    python3 grade.py dog                       # 9 visible + 16 hidden
    python3 tools/stress.py dog --n 200        # courses nobody curated

Contract
--------
    policy(obs) -> True (bounce) or False (glide)

    NOTE this is a bool, not a string. The other two environments in this repo
    use strings. Read the contract, do not assume it.

Four things in the spec that are easy to miss
---------------------------------------------
  * A bounce SETS vy to +bounce_impulse. It does not add. Bouncing while you
    are already rising throws away the speed you had and costs stamina anyway.
  * Stamina. A bounce costs 1, you regenerate 1 every regen_period frames, and
    at 0 stamina a bounce silently does nothing. Bouncing on every frame you
    feel nervous will leave you with nothing when it matters.
  * You only see the next `sight` pipes. In one scenario that is 1.
  * Every physical constant is in the observation, including gravity,
    bounce_impulse, max_fall_speed and forward_speed. None of them belong in
    your code as a literal.

You have the exact physics in front of you, and only two actions. That is
worth thinking about before you write a single if-statement.
"""

DEBUG: dict = {}      # see DEBUGGING.md


def policy(obs: dict) -> bool:
    y, vy = obs["y"], obs["vy"]

    DEBUG.clear()
    DEBUG.update(t=obs["t"], y=y, vy=vy, stamina=obs["stamina"])

    # --- 1. where do you need to be, and by when? --------------------------

    # --- 2. what happens if you bounce now? what if you do not? ------------

    # --- 3. pick the one that is still alive later -------------------------

    return False
