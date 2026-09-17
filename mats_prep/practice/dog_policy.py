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


def advance(state, action, obs):
    new_stamina = state['stamina']
    new_vy = state['vy']
    new_y = state['y']

    if action and new_stamina > 0:
        new_stamina -= 1
        new_vy = obs['bounce_impulse']

    new_vy -= obs['gravity'] * obs['dt']

    if new_vy < -obs['max_fall_speed']:
        new_vy = -obs['max_fall_speed']
    
    new_y += new_vy * obs['dt']

    new_t = state['t'] + 1

    if new_t % obs['regen_period'] == 0 and new_stamina < obs['stamina_max']:
        new_stamina += 1

    new_state = {
        't':new_t,
        'x':state['x'] + obs['forward_speed'] * obs['dt'],
        'y':new_y,
        'vy':new_vy,
        'stamina':new_stamina,
    }

    return new_state

def check_crashed(state, obs):
    dog_r = state['x'] + obs['dog_radius']
    dog_l = state['x'] - obs['dog_radius']
    dog_t = state['y'] + obs['dog_radius']
    dog_b = state['y'] - obs['dog_radius']

    if dog_b <= 0 or dog_t >= obs['ceiling']:
        return True

    for pipe in obs['pipes']:
        pipe_r = pipe['x'] + pipe['half_w']
        pipe_l = pipe['x'] - pipe['half_w']
        pipe_t = pipe['gap_hi']
        pipe_b = pipe['gap_lo']
        
        if dog_t > pipe_t or dog_b < pipe_b:
            if dog_r > pipe_l and pipe_r > dog_l:
                return True

    return False


def survival(state, obs, remain):

    if remain == 0:
        return 0

    best = 0

    for action in (True, False):
        if action and state['stamina'] == 0:
            continue

        next_state = advance(state, action, obs)
        crashed = check_crashed(next_state, obs)

        if crashed:
            continue
        
        survived = 1 + survival(next_state, obs, remain-1)

        best = max(best, survived)

        if best == remain:
            break
    
    return best


def policy(obs: dict) -> bool:
    DEBUG.clear()

    n = 30

    state = {
        't':obs['t'],
        'x':obs['x'],
        'y':obs['y'],
        'vy':obs['vy'],
        'stamina':obs['stamina'],
    }

    best_t = 0
    best_f = 0

    next_state = advance(state, False, obs)
    crashed = check_crashed(next_state, obs)

    if not crashed:
        best_f = survival(next_state, obs, n)

    if state['stamina'] == 0:
        best_t = best_f
    else:
        next_state = advance(state, True, obs)
        crashed = check_crashed(next_state, obs)

        if not crashed:
            best_t = survival(next_state, obs, n)

    DEBUG.update(best_t=best_t, best_f=best_f)

    if best_t > best_f:
        return True

    return False

# def rollout(obs, n=10):
#     all_res = []

#     action = False

#     state = {
#         't':obs['t'],
#         'x':obs['x'],
#         'y':obs['y'],
#         'vy':obs['vy'],
#         'stamina':obs['stamina'],
#     }

#     next_state = advance(state, action, obs)
#     crashed = check_crashed(next_state, obs)

#     return crashed

# {'t': 0, 'frames_left': 424, 'dt': 0.1, 'x': 0.0, 'y': 23.77665989343242, 'vy': 0.0, 'stamina': 5, 'stamina_max': 5, 'regen_period': 6, 'gravity': 30.0, 'bounce_impulse': 19.0, 'max_fall_speed': 30.0, 'forward_speed': 22.0, 'ceiling': 60.0, 'dog_radius': 1.5, 'cleared': 0, 'pipes_total': 14, 'pipes': [{'x': 62.0, 'half_w': 3.0, 'gap_lo': 15.77665989343242, 'gap_hi': 31.77665989343242}, {'x': 112.0, 'half_w': 3.0, 'gap_lo': 12.688095098949304, 'gap_hi': 28.688095098949304}, {'x': 162.0, 'half_w': 3.0, 'gap_lo': 15.673952321515586, 'gap_hi': 31.673952321515586}]}

# ----------------------------------------------

# def policy(obs: dict) -> bool:
#     y, vy = obs["y"], obs["vy"]

#     DEBUG.clear()
#     DEBUG.update(t=obs["t"], y=y, vy=vy, stamina=obs["stamina"])

#     pipe0_y = (obs['pipes'][0]['gap_lo'] + obs['pipes'][0]['gap_hi']) / 2 

#     DEBUG.update(x=obs['x'], y=obs['y'], pipe0_x=obs['pipes'][0]['x'], pipe0_y=pipe0_y)

#     if obs['stamina'] == 0:
#       return False
#     else:
#       if obs['x'] < obs['pipes'][0]['x'] + obs['pipes'][0]['half_w']:
#         jump_here = pipe0_y - (obs['pipes'][0]['gap_hi'] - obs['pipes'][0]['gap_lo']) / 4.5
#         if obs['y'] < jump_here:
#           return True

#     return False

# --------------------------------------------------

# import math

# MAX_H, MIN_H, LEAD = 46, 8, 4
# DEBUG: dict = {}


# def _target(obs):
#     pipes = obs["pipes"]
#     if not pipes:
#         return obs["ceiling"] / 2
#     p = pipes[0]
#     lo, hi = p["gap_lo"] + obs["dog_radius"], p["gap_hi"] - obs["dog_radius"]
#     t = (lo + hi) / 2
#     if len(pipes) > 1:
#         q = pipes[1]
#         t += 0.35 * (((q["gap_lo"] + q["gap_hi"]) / 2) - t)
#     return min(max(t, lo), hi)


# def _horizon(obs):
#     if not obs["pipes"]:
#         return 20
#     p = obs["pipes"][0]
#     span = p["x"] + p["half_w"] - obs["x"] + obs["dog_radius"]
#     return max(MIN_H, min(MAX_H, int(span / (obs["forward_speed"] * obs["dt"])) + LEAD))


# def _roll(obs, first, target, horizon):
#     """Copy of the environment's update. Returns (survived, miss, bounces)."""
#     dt, g, r = obs["dt"], obs["gravity"], obs["dog_radius"]
#     imp, vmaxf, fwd = obs["bounce_impulse"], obs["max_fall_speed"], obs["forward_speed"]
#     ceil_, period, smax = obs["ceiling"], obs["regen_period"], obs["stamina_max"]
#     x, y, vy, st, t = obs["x"], obs["y"], obs["vy"], obs["stamina"], obs["t"]
#     pipes, bounces, miss = obs["pipes"], 0, abs(obs["y"] - target)

#     for k in range(horizon):
#         if k == 0:
#             act = first
#         else:
#             # continuation: climb only when below target and not already rising
#             act = y < target and vy <= 0.0
#         if act and st > 0:
#             st -= 1
#             vy = imp
#             bounces += 1
#         vy = max(vy - g * dt, -vmaxf)
#         y += vy * dt
#         x += fwd * dt
#         t += 1
#         if t % period == 0 and st < smax:
#             st += 1
#         if y - r <= 0.0 or y + r >= ceil_:
#             return k, 1e9, bounces
#         for p in pipes:
#             if x + r > p["x"] - p["half_w"] and x - r < p["x"] + p["half_w"]:
#                 if not (y - r >= p["gap_lo"] and y + r <= p["gap_hi"]):
#                     return k, 1e9, bounces
#                 miss = min(miss, abs(y - target))
#     return horizon, miss, bounces


# def policy(obs):
#     target = _target(obs)
#     h = _horizon(obs)
#     sb, mb, bb = _roll(obs, True, target, h)
#     sg, mg, bg = _roll(obs, False, target, h)
#     DEBUG.clear()
#     DEBUG.update(target=round(target, 2), y=round(obs["y"], 2), vy=round(obs["vy"], 2),
#                  stamina=obs["stamina"], horizon=h, surv_b=sb, surv_g=sg,
#                  miss_b=round(min(mb, 999), 2), miss_g=round(min(mg, 999), 2))
#     if sb != sg:
#         return sb > sg
#     if abs(mb - mg) > 1e-6:
#         return mb < mg
#     return bb < bg          # same outcome: take the cheaper option

  

